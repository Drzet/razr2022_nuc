#!/usr/bin/env python3
"""Offline oneli unsigned legacy boot-header-v2 RAM-trial candidate.

Pins an accepted reduced Image, mainline DTB, and resident native early gzip
initramfs. Calls pinned AOSP mkbootimg; independently parses/checks the v2
header, payloads, padding, and legacy SHA-1 image ID. Never runs fastboot,
changes partitions, builds Linux, or asserts Motorola loader acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import package_oneli_reduced_native_diag as accepted

PAGE = 4096
CMDLINE = accepted.CMDLINE
NAME = "oneli-reduced-radio-diag-boot-v2.RAM-TRIAL.UNSIGNED.img"
LEGACY_HEADER_SIZE = 1660
# Structural address-template fields reused from reviewed Motorola v4 inputs.
# Never interpret these as final Motorola ABL physical placements.
ADDS = ("kernel_addr", "ramdisk_addr", "tags_addr", "dtb_addr")
HEADER_INPUTS = "configs/oneli-native-host-header-inputs-v1.json"


def check(condition, why):
    if not condition:
        raise ValueError(why)


def sha(content):
    return hashlib.sha256(content).hexdigest()


def align(n, p=PAGE):
    return (n + p-1)//p*p


def parse_v2(blob, image, early, dtb, expected_addresses):
    """Independent strict Android legacy-v2 byte parser, no AOSP imports."""
    check(len(blob) >= PAGE and blob[:8] == b"ANDROID!", "not boot image")
    vals = struct.unpack_from("<10I", blob, 8)
    (ksize, kaddr, rsize, raddr, second_size, second_addr,
     tags_addr, page_size, version, os_raw) = vals
    check(version == 2 and page_size == PAGE and os_raw == 0, "bad v2 version/page/os")
    check((ksize, rsize, second_size) == (len(image), len(early), 0),
          "boot kernel/ramdisk/second sizes changed")
    check(second_addr == 0, "unused second-stage load address must be zero")
    check((kaddr, raddr, tags_addr) ==
          tuple(expected_addresses[x] for x in ("kernel_addr","ramdisk_addr","tags_addr")),
          "unexpected structural header load addresses")
    board_bytes = blob[48:64]
    check(board_bytes == b"oneli" + bytes(11), "board name changed")
    cmd1 = blob[64:576]
    cmd2 = blob[608:1632]
    expected_cmd = CMDLINE.encode("ascii")
    check(cmd1 == expected_cmd.ljust(512,b"\0"), "cmdline differs from UART-first intent")
    check(not any(cmd2), "v2 extra cmdline must be empty")
    check(b"razr.radio_qemu_shutdown=1" not in cmd1, "QEMU shutdown parameter present")
    recover_size = struct.unpack_from("<I", blob, 1632)[0]
    recover_off = struct.unpack_from("<Q", blob, 1636)[0]
    hdr_size = struct.unpack_from("<I", blob, 1644)[0]
    dtb_size = struct.unpack_from("<I", blob, 1648)[0]
    dtb_load = struct.unpack_from("<Q", blob, 1652)[0]
    check((recover_size,recover_off,hdr_size,dtb_size,dtb_load) ==
          (0,0,LEGACY_HEADER_SIZE,len(dtb),expected_addresses["dtb_addr"]),
          "incorrect v2 DTB or recovery metadata")
    kernel_off=PAGE
    ramdisk_off=PAGE+align(ksize)
    dtb_off=ramdisk_off+align(rsize)
    end=dtb_off+align(dtb_size)
    check(len(blob)==end, "unexpected image length/trailing bytes")
    check(kernel_off%PAGE==ramdisk_off%PAGE==dtb_off%PAGE==0, "page alignment")
    check(blob[kernel_off:kernel_off+ksize]==image, "embedded Image differs")
    check(blob[ramdisk_off:ramdisk_off+rsize]==early, "embedded early gzip differs")
    check(blob[dtb_off:dtb_off+dtb_size]==dtb, "embedded oneli DTB differs")
    for start,stop in ((LEGACY_HEADER_SIZE,PAGE),
                       (kernel_off+ksize,ramdisk_off),
                       (ramdisk_off+rsize,dtb_off),
                       (dtb_off+dtb_size,end)):
        check(not any(blob[start:stop]), "nonzero image padding/hidden optional data")
    legacy_sha=hashlib.sha1()
    for payload in (image,early,b"",b"",dtb):
        legacy_sha.update(payload)
        legacy_sha.update(struct.pack("<I",len(payload)))
    expected_id=legacy_sha.digest()+bytes(12)
    check(blob[576:608]==expected_id, "v2 AOSP SHA1 legacy image ID mismatch")
    check(dtb[:4] == bytes.fromhex("d00dfeed"), "DTB missing FDT magic")
    check(int.from_bytes(dtb[4:8],"big")==len(dtb), "DTB FDT total size mismatch")
    return {
        "magic":"ANDROID!","header_version":2,"header_size_bytes":hdr_size,
        "os_version_raw":os_raw,"board":"oneli",
        "page_size_bytes":page_size,
        "kernel_file_bytes":ksize,
        "kernel_file_offset_bytes":kernel_off,
        "kernel_header_load_address_hex":hex(kaddr),
        "ramdisk_bytes":rsize,"ramdisk_file_offset_bytes":ramdisk_off,
        "ramdisk_header_load_address_hex":hex(raddr),
        "second_bytes":second_size,"second_load_address":second_addr,
        "tags_header_address_hex":hex(tags_addr),
        "recovery_dtbo_bytes":recover_size,"recovery_dtbo_offset_bytes":recover_off,
        "dtb_bytes":dtb_size,"dtb_file_offset_bytes":dtb_off,
        "dtb_header_load_address_hex":hex(dtb_load),
        "legacy_image_id_sha1":expected_id[:20].hex(),
        "command_line":CMDLINE,
        "extra_command_line_empty":True,
        "image_total_bytes":len(blob),
        "all_optional_regions_empty":True,
        "zero_padding_all_sections":True,
        "all_offsets_page_aligned":True,
        "header_addresses_structural_not_runtime":True
    }


def check_recipe(header):
    check(PAGE==4096 and LEGACY_HEADER_SIZE==1660, "unexpected pinned AOSP constants")
    check(len(CMDLINE.encode("ascii")) < 512 and
          "razr.radio_qemu_shutdown=1" not in CMDLINE, "bad native command")
    check(header["purpose"]=="structural-only" and
          header["phone_boot_validated"] is False and
          header["os_version_raw"]==0, "template wrongly claims phone support")
    for key in ADDS:
        check(isinstance(header[key],int) and 0<=header[key]<2**32,
              "unsafe legacy structural field "+key)
    # Deliberately retain accepted placeholder values; do NOT claim load addresses.
    check(tuple(header[k] for k in ADDS) ==
          (32768,16777216,256,32505856), "reviewed field policy differs")


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--producer",type=Path)
    ap.add_argument("--early",type=Path)
    ap.add_argument("--aosp-mkbootimg",type=Path)
    ap.add_argument("--header-inputs",type=Path,
                    default=Path(HEADER_INPUTS))
    ap.add_argument("--output",type=Path)
    ap.add_argument("--check-recipe",action="store_true")
    args=ap.parse_args()
    header=json.loads(args.header_inputs.read_text())
    check_recipe(header)
    if args.check_recipe:
        print("ONELI_V2_RECIPE_CHEAP_CHECK_PASS")
        return
    check(args.producer and args.early and args.aosp_mkbootimg and args.output,
          "production requires pinned inputs, AOSP tool, and output")
    check(not args.output.exists(),"refuse to overwrite an output directory")
    producer=args.producer/"release"
    accepted.check_release_manifest(producer)
    image=accepted.read(producer/"Image",accepted.IMAGE_SHA)
    cfg=accepted.read(producer/"kernel.config",accepted.CONFIG_SHA)
    dtb=accepted.read(producer/"sm8475-motorola-oneli.dtb",accepted.DTB_SHA)
    accepted.read(producer/"radio-modules.tar.zst",accepted.MODULES_SHA)
    check((producer/"kernel.release").read_text().strip()==accepted.RELEASE,
          "accepted reduced kernel release changed")
    identity=(producer/"source-identity.txt").read_text()
    check("kernel_source="+accepted.KERNEL in identity and
          "kernel_release="+accepted.RELEASE in identity,
          "kernel producer/source provenance changed")
    required=("CONFIG_ARM64=y","CONFIG_BLK_DEV_INITRD=y","CONFIG_RD_GZIP=y",
              "CONFIG_SERIAL_QCOM_GENI=y","CONFIG_SERIAL_QCOM_GENI_CONSOLE=y",
              "CONFIG_MODULES=y","CONFIG_PCI_PWRCTRL_PWRSEQ=m")
    config_lines=set(cfg.decode().splitlines())
    for symbol in required:
        check(symbol in config_lines,"required kernel symbol missing "+symbol)
    runtime=accepted.inspect_image(image)
    check(len(dtb)<2*1024*1024 and dtb[:4]==bytes.fromhex("d00dfeed"),
          "unaccepted FDT geometry")
    early, members, module_sha=accepted.verify_early(args.early/"reduced-early")

    args.output.mkdir(parents=True)
    out=args.output/NAME
    cmd=[
        sys.executable,str(args.aosp_mkbootimg),
        "--header_version","2","--pagesize",str(PAGE),
        "--base","0",
        "--kernel_offset",hex(header["kernel_addr"]),
        "--ramdisk_offset",hex(header["ramdisk_addr"]),
        "--tags_offset",hex(header["tags_addr"]),
        "--dtb_offset",hex(header["dtb_addr"]),
        "--board","oneli",
        "--kernel",str(producer/"Image"),
        "--ramdisk",str(args.early/"reduced-early/radio-early.cpio.gz"),
        "--dtb",str(producer/"sm8475-motorola-oneli.dtb"),
        "--cmdline",CMDLINE,
        "--output",str(out)
    ]
    subprocess.run(cmd,check=True,capture_output=True,text=True)
    blob=out.read_bytes()
    parsed=parse_v2(blob,image,early,dtb,header)
    # Separate runtime/physical Image requirements from structural file layout.
    runtime["nominal_unplaced_ramdisk_plus_dtb_bytes"] = align(len(early))+align(len(dtb))
    runtime["actual_motorola_uefi_kernel_base_unknown"]=True
    runtime["actual_abl_dtb_board_match_and_memory_fixup_unknown"]=True
    runtime["image_start_2mib_alignment_required"]=True

    report={
        "schema":"oneli-reduced-radio-v2-ram-trial-offline-v1",
        "status":"HOST_PACKAGED_NOT_DEVICE_TESTED_NOT_FLASH_APPROVED",
        "source_kernel_commit":accepted.KERNEL,
        "kernel_release":accepted.RELEASE,
        "producer_run_id":accepted.SOURCE_RUN,
        "producer_artifact_id":accepted.SOURCE_ARTIFACT,
        "early_run_id":accepted.EARLY_RUN,
        "early_artifact_id":accepted.EARLY_ARTIFACT,
        "aosp_mkbootimg_commit":"7209a7164f1772db43f92928012c86a00f6202ff",
        "aosp_tool_used":True,
        "candidate_filename":NAME,
        "candidate_sha256":sha(blob),
        "image_sha256":accepted.IMAGE_SHA,
        "kernel_config_sha256":accepted.CONFIG_SHA,
        "dtb_sha256":accepted.DTB_SHA,
        "early_gzip_sha256":accepted.EARLY_GZIP_SHA,
        "early_embedded_module_sha256":module_sha,
        "early_newc_member_count_checked":members,
        "native_init_behavior_present":True,
        "image_runtime_header":runtime,
        "v2_header":parsed,
        "v2_format_independent_parser":"PASS",
        "v2_aosp_independent_unpack":"PENDING_CI",
        "v2_aosp_repack":"PENDING_CI",
        "avb_signature_present":False,
        "native_ram_only_fastboot_supported":"UNPROVEN",
        "motorola_downloaded_buffer_selected":"UNPROVEN",
        "motorola_dtb_selected":"UNPROVEN",
        "vendor_boot_modified":False,
        "other_partitions_modified":False,
        "existing_v4_artifact_id":12338654148,
        "device_commands_executed":False,
        "hardware_boot_tested":False,
        "flash_approved":False,
    }
    (args.output/"offline-v2-validation.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ONELI_V2_RAM_TRIAL_PACKAGE_PASS "+
          json.dumps({"sha256":sha(blob),"bytes":len(blob),
                      "dtb_offset":parsed["dtb_file_offset_bytes"],
                      "runtime_image_size":runtime["image_size_bytes"]},sort_keys=True))


if __name__=="__main__":
    main()
