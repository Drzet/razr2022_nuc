#!/usr/bin/env python3
"""Check Userspace's metadata-only bridge against immutable Boot and VPU JSON."""
import argparse
import hashlib
import json
from pathlib import Path

def require(ok, detail):
    if not ok:
        raise ValueError(detail)

def blob_sha(path):
    content = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()

def inspect(boot_path, stock_path, consumer_path):
    b, v, c = [json.loads(p.read_text()) for p in (boot_path, stock_path, consumer_path)]
    require(c.get("schema") == "oneli-userspace-reference-metadata-v2", "wrong consumer schema")
    require(b.get("schema") == "oneli-native-boot-packaging-contract-v2", "not Boot v2")
    require(v.get("schema") == "oneli-stock-fdt-reference-properties-v1", "not pinned FDT export")
    src = c["source"]
    require(blob_sha(boot_path) == src["boot_contract"]["git_blob_sha1"],
            "Boot source blob has changed")
    require(blob_sha(stock_path) == src["vpu_export"]["git_blob_sha1"],
            "VPU source blob has changed")
    require(src["public_stock_zip_sha256"] == v["project_evidence"]["source_full_zip_sha256"] ==
            b["stock_public_archive"]["sha256"], "public source archive differs")
    require(src["vpu_export"]["full_raw_json_sha256"] == v["project_evidence"]["full_json_sha256"],
            "full raw FDT export hash differs")
    cb, cv = c["stock_header"]["boot"], c["stock_header"]["vendor_boot"]
    bb = b["reference_images"]["boot"]
    bv = b["reference_images"]["vendor_boot"]
    vb = v["vendor_boot"]
    require(cb["version"] == bb["header_version"] == 4 and
            cb["header_bytes"] == bb["header_bytes"] == 1584 and
            cb["layout_page_bytes"] == bb["layout_page_bytes"] == 4096 and
            cb["os_version_raw"] is None and bb["os_version_raw"] is None,
            "boot v4 fields or unresolved OS version changed")
    require(cv["version"] == vb["version"] == bv["header_version"] == 4 and
            cv["page_bytes"] == bv["page_bytes"] == vb["page_size"] == 4096 and
            cv["header_bytes"] == bv["header_bytes"] == vb["header_size"] == 2128,
            "vendor boot header disagreement")
    for field, source in (("kernel", "kernel_addr"), ("ramdisk", "ramdisk_addr"),
                          ("tags", "tags_addr"), ("dtb", "dtb_addr")):
        require(cv["reference_addresses"][field] == vb[source],
                "missing or mismatched reference address " + field)
        require(bv[source] == vb[source], "Boot v2 published reference address differs from stock")
    for field, source in (("offset", "offset"), ("bytes", "bytes"),
                          ("compression", "compression"), ("sha256", "sha256")):
        require(cv["vendor_ramdisk"][field] == vb["vendor_ramdisk"][source],
                "ramdisk compression/offset/hash disagreement " + field)
    region = cv["base_dtb_region"]
    f = vb["embedded_dtb"]
    require(region["offset"] == f["offset"] == bv["dtb_region_offset"] and
            region["bytes"] == f["bytes"] == bv["dtb_region_bytes"] and
            region["sha256"] == f["sha256"] == bv["dtb_region_sha256"],
            "embedded DTB region mismatch")
    pieces = region["fdt_components"]
    require(len(pieces) == 2 and len(f["two_unpadded_images"]) == 2, "base DTB count changed")
    for expected, actual in zip(pieces, f["two_unpadded_images"]):
        require(expected == {k: actual[src] for k, src in
                              (("offset", "offset"), ("bytes", "size"),
                               ("sha256", "sha256"), ("msm_id", "msm_id"))},
                "base FDT component differs")
    require(pieces[0]["offset"] == 0 and
            pieces[1]["offset"] == pieces[0]["bytes"] == 479481 and
            pieces[0]["bytes"] + pieces[1]["bytes"] == region["bytes"],
            "unpadded dual-FDT offset lost")
    frag = cv["fragment"]
    vt = vb["fragment_table"]
    require(frag["fragment_offset"] == bv["fragment_offset"] == 0 and
            frag["fragment_bytes"] == bv["fragment_bytes"] == cv["vendor_ramdisk"]["bytes"],
            "Boot v2 native fragment offset/length drifted")
    require(bv["embedded_dtb_count"] == 2 and
            [x["relative_offset"] for x in bv["embedded_dtb_roots"]] == [0, 479481],
            "Boot v2 unpadded base DTB inventory drifted")
    require(frag["count"] == vt["count"] == bv["ramdisk_table_entries"] == 1 and
            frag["entry_bytes"] == vt["entry_size"] == bv["ramdisk_table_entry_bytes"] == 108 and
            frag["type"] == vt["type"] == bv["ramdisk_fragment_type"] == 1 and
            frag["board_ids"] == vt["board_ids"] == bv["ramdisk_fragment_board_id_words"] == [0] * 16 and
            frag["name"] is None and bv["table_entry_name"] is None,
            "platform ramdisk fragment descriptor differs")
    require(cv["bootconfig"]["offset"] == vb["bootconfig"]["offset"] == bv["bootconfig_offset"] and
            cv["bootconfig"]["bytes"] == vb["bootconfig"]["bytes"] == bv["bootconfig_bytes"] and
            cv["bootconfig"]["keys"] == vb["bootconfig"]["keys"] and
            cv["bootconfig"]["values_verified"] is False, "bootconfig unverified value became accepted")
    pvt = next(row for row in v["dtbo_overlays"] if row["index"] == 3)
    require(c["reference_overlay"]["board_id"] == pvt["board_id"] == [69, 49152] and
            c["reference_overlay"]["sha256"] == pvt["sha256"] and
            c["reference_overlay"]["applied"] is False, "PVT source candidate confused with active DT")
    proto = b.get("prototype", {})
    nc = c.get("native_composition", {})
    required = ["os_version_raw", "kernel_addr", "ramdisk_addr", "tags_addr",
                "dtb_addr", "purpose", "phone_boot_validated"]
    require(proto.get("header_inputs_require_explicit_os_version") is True and
            proto.get("implicit_reference_placement_inheritance") is False and
            proto.get("native_ready") is False and proto.get("hardware_accepted") is False and
            proto.get("candidate_signed") is False and proto.get("boot_tested") is False,
            "Boot v2 must explicitly reject inherited placement and physical acceptance")
    require(proto.get("header_inputs_fields") == required and
            proto.get("header_inputs_file") == "--header-inputs explicit-header-fields.json" and
            "header-inputs" in proto.get("requires_explicit_payload_paths", []),
            "Boot v2 explicit header fields not recognized")
    require(nc.get("required_header_fields") == required and
            nc.get("boot_contract_schema") == b["schema"] and
            nc.get("header_inputs") is None and
            nc.get("boot_requires_explicit_header_inputs") is True and
            nc.get("source_reference_addresses_are_not_approved_native_placement") is True and
            nc.get("native_ready") is False and nc.get("hardware_accepted") is False,
            "reference bridge mistakenly accepts missing native header inputs")
    fw = c["vpu_firmware_install"]
    require(fw["status"] == "proposed-disabled-profile" and
            fw["sha256"] == "9582ea4c5565408bd3e5ba6f8fffc7881f226cae001b6fcd7a0c868de9add9af" and
            fw["required_for_qemu_virt"] is False and
            fw["required_for_minimal_oneli_early_initramfs"] is False and
            fw["authentication_verified"] is False, "VPU reference mistakenly promoted into base requirement")
    require(c["reference_only"] is True and c["structural_format_observed"] is True and
            c["native_composition_ready"] is False and c["hardware_accepted"] is False and
            c["active_bootloader_overlay_verified"] is False, "reference evidence promoted into native readiness")
    return {"boot_git_blob": blob_sha(boot_path),
            "vpu_git_blob": blob_sha(stock_path),
            "dual_base_offsets": [row["offset"] for row in pieces],
            "reference_stage": "structural-reference-only",
            "native_ready": False, "phone_accepted": False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boot-v2", required=True, type=Path)
    parser.add_argument("--vpu-fdt", required=True, type=Path)
    parser.add_argument("--userspace", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    a = parser.parse_args()
    try:
        result = inspect(a.boot_v2, a.vpu_fdt, a.userspace)
    except (ValueError, OSError, KeyError, IndexError, StopIteration) as e:
        parser.exit(1, f"BOOT_REFERENCE_AUDIT_FAILED: {e}\n")
    if a.output:
        a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("BOOT_REFERENCE_METADATA_PASS: structural source fields and unresolved gates preserved")

if __name__ == "__main__":
    main()
