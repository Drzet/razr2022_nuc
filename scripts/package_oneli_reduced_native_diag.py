#!/usr/bin/env python3
"""Offline Motorola oneli Android boot-v4 diagnostic assembler.

Never executes adb/fastboot, writes partitions, or builds a kernel.
Inputs are immutable accepted CI outputs. No device launch is authorized.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_oneli_native_host_candidate as base
import oneli_boot_v4_layout as layout

KERNEL = "7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce"
RELEASE = "7.3.0-rc6-oneli-reduced1-g7f3865ee17c3"
SOURCE_RUN = 39170486506
SOURCE_ARTIFACT = 12153785196
EARLY_RUN = 39237882830
EARLY_ARTIFACT = 12180445735
IMAGE_SHA = "279431f997fc2334d92760d47c01aec2b8e12cf47e6d149d6a078f2347c330e8"
CONFIG_SHA = "97ee634780847771163608e353e0086eceee6347ccd42a4d9d87d04f967981be"
DTB_SHA = "70d5c7b08ddda1c0974ac85e95bb1328528bb533c344a0681b5e95b88cd17435"
MODULES_SHA = "53223f163ebf1939192d85002939b4f201cff9abf7feb5160acf63c7eebbe908"
EARLY_GZIP_SHA = "875eb0a1b0f63dbecaefb5160775da01bd8a3bc445ca1eb016effe3717875b7c"
EARLY_CPIO_SHA = "e4d22424839f26a2013ecf88638e81523c1cb203a86836f4ca94a7bb7230fe2b"
EARLY_INIT_SHA = "4c179db5152439988d957cf542676dc98f2f766ada3a880b9977dad6ae76f323"
EMPTY_VENDOR_SHA = "af39e1c19af478aef7a03be98efa9d9baa228fb9f93e3842d6d7b14a1465a459"
PAGE = 4096
CMDLINE = "console=ttyMSM0,115200n8 loglevel=8 printk.time=1 rdinit=/init"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path, expected):
    data = path.read_bytes()
    require(sha(data) == expected, "SHA256 mismatch: " + str(path))
    return data


def check_release_manifest(directory):
    rows = (directory / "SHA256SUMS").read_text().splitlines()
    require(len(rows) == 10, "producer release manifest does not have 10 entries")
    seen = set()
    for row in rows:
        match = re.fullmatch(r"([a-f0-9]{64})  \./([A-Za-z0-9_.-]+)", row)
        require(match is not None, "invalid producer manifest line")
        name = match.group(2)
        require(name not in seen, "duplicate producer manifest name")
        seen.add(name)
        read(directory / name, match.group(1))
    require({"Image", "kernel.config", "kernel.release",
             "sm8475-motorola-oneli.dtb", "radio-modules.tar.zst",
             "source-identity.txt"} <= seen, "producer missing required members")
    return len(seen)


def verify_early(early):
    raw = read(early / "radio-early.cpio", EARLY_CPIO_SHA)
    gz = read(early / "radio-early.cpio.gz", EARLY_GZIP_SHA)
    require(gz[:3] == b"\x1f\x8b\x08" and gz[3] == 0 and gz[4:8] == bytes(4),
            "early ramdisk is not deterministic gzip")
    require(gzip.decompress(gz) == raw, "compressed early initramfs not byte-identical")
    members = base.newc_parse(raw)
    require("init" in members and members["init"]["mode"] & 0o111,
            "early /init missing or not executable")
    init = members["init"]["bytes"]
    require(sha(init) == EARLY_INIT_SHA, "early /init digest mismatch")
    need = (b"RADIO_EARLY_READY_V1", b"RADIO_EARLY_HOLD",
            b"RADIO_EARLY_INSMOD_OK", b"RADIO_EARLY_RELEASE",
            b"pci-pwrctrl-pwrseq.ko", RELEASE.encode(),
            b"razr.radio_qemu_shutdown=1", b"linux,dummy-virt")
    for token in need:
        require(token in init, "missing tested early init behavior: " + repr(token))
    require(init.endswith(b'while :; do "$BB" sleep 60; done\n'),
            "resident hold behavior differs from tested payload")
    require(not any(b"razr.radio_qemu_shutdown=1" in path.encode()
                    for path in members), "unexpected initramfs member")
    mod = "lib/modules/" + RELEASE + "/kernel/drivers/pci/pwrctrl/pci-pwrctrl-pwrseq.ko"
    require(mod in members and len(members[mod]["bytes"]) > 1000,
            "matching early PCI pwrctrl module missing")
    inputs = json.loads((early / "radio-inputs.json").read_text())
    for key, value in (("kernel_release", RELEASE), ("kernel_commit", KERNEL),
                       ("image_sha256", IMAGE_SHA), ("dtb_sha256", DTB_SHA),
                       ("modules_archive_sha256", MODULES_SHA),
                       ("early_gzip_sha256", EARLY_GZIP_SHA),
                       ("early_cpio_sha256", EARLY_CPIO_SHA),
                       ("init_sha256", EARLY_INIT_SHA)):
        require(inputs.get(key) == value, "Userspace early source mismatch: " + key)
    require(inputs.get("source_artifact") == SOURCE_ARTIFACT,
            "Userspace early source artifact mismatch")
    return gz, len(members), sha(members[mod]["bytes"])


def inspect_image(kernel):
    require(len(kernel) == 36436480 and kernel[56:60] == b"ARM\x64",
            "invalid ARM64 Image magic or file length")
    text_offset, image_size, flags = struct.unpack_from("<QQQ", kernel, 8)
    require(text_offset == 0 and image_size == 37158912 and flags == 0xa,
            "unexpected reduced ARM64 Image header")
    require(image_size >= len(kernel), "Image advertised size smaller than file")
    return {"file_bytes": len(kernel), "image_size_bytes": image_size,
            "text_offset_bytes": text_offset, "flags_hex": hex(flags),
            "magic_hex": kernel[56:60].hex(), "required_alignment_bytes": 2097152,
            "actual_load_address_known": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--producer", type=Path, required=True,
                        help="unzipped accepted run 39170486506 artifact")
    parser.add_argument("--early", type=Path, required=True,
                        help="unzipped accepted run 39237882830 early artifact")
    parser.add_argument("--header-inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "refuse to overwrite prior output")
    release = args.producer / "release"
    count = check_release_manifest(release)
    kernel = read(release / "Image", IMAGE_SHA)
    config = read(release / "kernel.config", CONFIG_SHA)
    dtb = read(release / "sm8475-motorola-oneli.dtb", DTB_SHA)
    read(release / "radio-modules.tar.zst", MODULES_SHA)
    require((release / "kernel.release").read_text().strip() == RELEASE,
            "reduced release differs")
    identity = (release / "source-identity.txt").read_text()
    require("kernel_source=" + KERNEL in identity and
            "kernel_release=" + RELEASE in identity, "producer identity mismatch")
    config_lines = set(config.decode().splitlines())
    for symbol in ("CONFIG_ARM64=y", "CONFIG_BLK_DEV_INITRD=y", "CONFIG_RD_GZIP=y",
                   "CONFIG_SERIAL_QCOM_GENI=y", "CONFIG_SERIAL_QCOM_GENI_CONSOLE=y",
                   "CONFIG_MODULES=y", "CONFIG_FW_LOADER=y", "CONFIG_PRINTK=y",
                   "CONFIG_PCI_PWRCTRL_PWRSEQ=m"):
        require(symbol in config_lines, "required builtin/module not retained: " + symbol)
    img_head = inspect_image(kernel)
    require(dtb[:4] == bytes.fromhex("d00dfeed") and
            int.from_bytes(dtb[4:8], "big") == len(dtb) and len(dtb) < 2*1024*1024,
            "single mainline oneli FDT malformed/too large")
    early_gz, members, early_module_sha = verify_early(args.early / "reduced-early")

    header = base.header_inputs(args.header_inputs)
    require(header["purpose"] == "structural-only" and
            header["phone_boot_validated"] is False and
            header["os_version_raw"] == 0, "non-structural header policy")
    vendor = subprocess.run(["gzip", "-n", "-9", "-c"],
                            input=base.newc_empty(), check=True,
                            stdout=subprocess.PIPE).stdout
    require(sha(vendor) == EMPTY_VENDOR_SHA and
            gzip.decompress(vendor) == base.newc_empty(),
            "v1 accepted empty vendor platform fragment changed")

    boot_blank, vendor_boot = base.build(kernel, early_gz, dtb, vendor, header)
    base.validate_structures(boot_blank, vendor_boot, kernel, early_gz, dtb,
                             vendor, header)
    boot = bytearray(boot_blank)
    command = CMDLINE.encode("ascii")
    require(len(command) < 1536 and b"razr.radio_qemu_shutdown=1" not in command,
            "forbidden handset shutdown parameter")
    boot[44:1580] = command.ljust(1536, b"\0")
    boot = bytes(boot)

    parsed_boot, parsed_vendor = layout.inspect_boot(boot), layout.inspect_vendor(vendor_boot)
    require(parsed_boot["version"] == parsed_vendor["version"] == 4,
            "expected v4 boot and vendor_boot")
    require(parsed_boot["cmdline"] == CMDLINE and parsed_vendor["cmdline"] == "",
            "unexpected bootloader command-line composition")
    require(parsed_boot["sections"][0]["name"] == "kernel" and
            parsed_boot["sections"][0]["sha256"] == IMAGE_SHA,
            "kernel round-trip offset/content mismatch")
    require(any(s["name"] == "ramdisk" and s["sha256"] == EARLY_GZIP_SHA
                for s in parsed_boot["sections"]), "generic ramdisk not from accepted Userspace")
    require(len(parsed_vendor["dtb_fdt_chunks"]) == 1 and
            parsed_vendor["dtb_fdt_chunks"][0]["sha256"] == DTB_SHA,
            "vendor_boot must embed ONE unmodified mainline oneli DTB")
    require(parsed_vendor["ramdisk_table"][0]["type"] == 1 and
            parsed_vendor["ramdisk_table"][0]["name"] == "native-diag",
            "vendor platform fragment descriptor changed")
    require(parsed_vendor["sections"][-1]["name"] == "bootconfig" and
            parsed_vendor["sections"][-1]["bytes"] == 0, "bootconfig should be empty")
    require(layout.repack_structural(boot, parsed_boot) == sha(boot) and
            layout.repack_structural(vendor_boot, parsed_vendor) == sha(vendor_boot),
            "v4 binary section round trip mismatch")
    reserve = (img_head["image_size_bytes"] +
               ((len(early_gz) + len(vendor) + PAGE-1)//PAGE)*PAGE +
               2*1024*1024 + 2*PAGE)
    require(reserve < 100 * 1024 * 1024, "nominal reserve exceeds fallback 100MiB")
    img_head["minimum_kernel_to_reserve_end_bytes"] = reserve
    img_head["runtime_uefi_KernelBaseAddr_KernelSize_unknown"] = True
    img_head["fallback_alignment_unproven"] = True
    img_head["dtb_memory_size_fixup_unproven"] = True

    args.output.mkdir(parents=True)
    bn = "oneli-reduced-radio-diag-boot-v4.UNSIGNED.img"
    vn = "oneli-reduced-radio-diag-vendor_boot-v4.UNSIGNED.img"
    (args.output / bn).write_bytes(boot)
    (args.output / vn).write_bytes(vendor_boot)
    report = {
        "schema":"oneli-reduced-radio-native-diagnostic-offline-v1",
        "status":"OFFLINE_PACKAGED_HARDWARE_UNTESTED",
        "kernel_source_commit":KERNEL, "release": RELEASE,
        "producer_run": SOURCE_RUN, "producer_artifact": SOURCE_ARTIFACT,
        "userspace_run": EARLY_RUN, "userspace_artifact": EARLY_ARTIFACT,
        "image_sha256":IMAGE_SHA,"dtb_sha256":DTB_SHA,
        "early_initramfs_sha256":EARLY_GZIP_SHA,
        "matching_modules_archive_sha256":MODULES_SHA,
        "kernel_config_sha256":CONFIG_SHA,
        "boot_image":{"name":bn, "bytes":len(boot), "sha256":sha(boot)},
        "vendor_boot_image":{"name":vn,"bytes":len(vendor_boot),"sha256":sha(vendor_boot)},
        "vendor_fragment_sha256":sha(vendor),
        "early_module_sha256":early_module_sha,
        "early_newc_members_verified":members,
        "producer_sha256sums_verified":count,
        "image_header":img_head,"boot_header_version":4,"vendor_boot_header_version":4,
        "boot_cmdline":CMDLINE,"vendor_cmdline":"",
        "bootconfig_bytes":0,"vendor_ramdisk_type":"platform",
        "vendor_ramdisk_name":"native-diag","vendor_dtb_count":1,
        "os_version_raw":0,"boot_signature_bytes":0,
        "reference_vendor_header_fields_structural_only":{
            key:header[key] for key in ("kernel_addr","ramdisk_addr","tags_addr","dtb_addr")},
        "v4_self_roundtrip":"PASS",
        "aosp_independent_unpack":"PENDING_CI",
        "avb_signed":False,"flash_approved":False,"hardware_tested":False,
        "fastboot_boot_uses_candidate_vendor_boot":"UNPROVEN",
        "temporary_boot_loads_candidate_dtb":"UNPROVEN",
        "runtime_ram_placement":"UNPROVEN",
        "root_device":None,
        "accepted_prior_releases_unchanged":True}
    (args.output / "offline-validation.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("ONELI_NATIVE_DIAG_OFFLINE_PACKAGING_PASS " +
          json.dumps({"boot_sha256":sha(boot),
                      "vendor_boot_sha256":sha(vendor_boot),
                      "required_reserve_bytes":reserve},sort_keys=True))


if __name__ == "__main__":
    main()
