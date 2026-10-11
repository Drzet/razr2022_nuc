#!/usr/bin/env python3
"""Read-only offline inventory of a PUBLIC oneli stock ZIP and extracted partition trees.

Does not flash, modify, distribute, or attest firmware. Use the exact ZIP version
in --source-url; a reference package is not the phone's installed firmware.

Usage:
  python3 scripts/inventory-oneli-firmware.py \
    --stock-zip /path/to/XT2251-1_ONELI_...zip \
    --source-url https://.../same.zip \
    --extracted-root /path/to/unpacked_vendor_and_odm \
    --json-out /path/to/vpu-gpu-firmware-manifest.json
"""
import argparse
import hashlib
import json
import re
import struct
import sys
import zipfile
from pathlib import Path

MARKERS = (
    "vpu20_4v", "a730_sqe", "gmu_gen70000", "a730_zap",
    "zap.mbn", "zap.mdt", "dtbo.img", "vendor.img", "odm.img",
    "super.img", "payload.bin", "boot.img", "vendor_boot.img",
)
DTBO_MAGIC = 0xD7B7AB1E


def digest_stream(stream):
    h, size = hashlib.sha256(), 0
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        h.update(block)
        size += len(block)
    return {"sha256": h.hexdigest(), "bytes": size}


def digest_file(path):
    with path.open("rb") as stream:
        return digest_stream(stream)


def dtbo_header(data):
    """Android DT table header is big-endian. Report selection candidates, not selected DTB."""
    if len(data) < 32 or struct.unpack_from(">I", data)[0] != DTBO_MAGIC:
        return {"state": "unrecognized_dtbo_header"}
    magic, total, header, ent_size, ent_count, offset, page, version = struct.unpack_from(">8I", data)
    if header < 32 or ent_size < 32 or ent_count > 10000 or offset > total:
        return {"state": "invalid_dtbo_header", "entry_count": ent_count}
    entries = []
    for i in range(ent_count):
        pos = offset + i * ent_size
        if pos + 32 > len(data):
            return {"state": "truncated_dtbo_entries", "entries": entries}
        vals = struct.unpack_from(">8I", data, pos)
        entries.append({"index": i, "dt_size": vals[0], "dt_offset": vals[1],
                        "id": vals[2], "rev": vals[3], "custom": list(vals[4:])})
    return {"state": "parsed_candidate_table", "total_size": total,
            "entry_size": ent_size, "entry_count": ent_count,
            "page_size": page, "version": version, "entries": entries,
            "note": "This lists candidate overlays; effective bootloader selection is unknown"}


def inventory_zip(path):
    output = {"archive": digest_file(path), "entries": [], "dtbo_candidates": []}
    with zipfile.ZipFile(path) as zf:
        for entry in zf.infolist():
            name = entry.filename
            if not any(marker in name.lower() for marker in MARKERS):
                continue
            item = {"name": name, "uncompressed_bytes": entry.file_size,
                    "crc32": f"{entry.CRC:08x}", "compressed_bytes": entry.compress_size}
            # Hash relevant direct ZIP entries, but do NOT stream multi-GB super/vendor images
            # here for a second time unless explicitly needed. Their contents must be unpacked
            # separately to inspect individual firmware blobs.
            if "dtbo.img" in name.lower() and entry.file_size <= 256 * 1024 * 1024:
                with zf.open(entry) as stream:
                    data = stream.read()
                item["sha256"] = hashlib.sha256(data).hexdigest()
                output["dtbo_candidates"].append({"zip_entry": name, **dtbo_header(data)})
            elif re.search(r"(?i)(vpu20_4v|a730_sqe|gmu_gen70000|a730_zap)", name) and entry.file_size <= 64 * 1024 * 1024:
                with zf.open(entry) as stream:
                    item.update(digest_stream(stream))
            output["entries"].append(item)
    return output


def firmware_version_marker(path):
    # Only scan signed firmware candidates of practical size. Do not log raw firmware bytes.
    if path.stat().st_size > 64 * 1024 * 1024:
        return None
    with path.open("rb") as stream:
        data = stream.read()
    match = re.search(rb"QC_IMAGE_VERSION_STRING=([^\x00\r\n]{1,128})", data)
    return match.group(1).decode("ascii", errors="replace") if match else None


def inventory_extracted(root):
    if not root.is_dir():
        raise ValueError(f"Not an extracted partition directory: {root}")
    records = []
    for file in sorted(root.rglob("*")):
        if not file.is_file() or not any(tag in file.name.lower() for tag in MARKERS):
            continue
        row = {"relative_path": file.relative_to(root).as_posix(),
               **digest_file(file)}
        if "vpu20_4v" in file.name.lower():
            row["qc_image_version_string"] = firmware_version_marker(file)
        records.append(row)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-zip", type=Path)
    parser.add_argument("--source-url")
    parser.add_argument("--extracted-root", type=Path,
                        help="Already extracted vendor/odm tree, not a proprietary ZIP")
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    if not args.stock_zip and not args.extracted_root:
        parser.error("Provide --stock-zip, --extracted-root, or both")
    doc = {"device": "Motorola razr 2022 (oneli)", "stock_image_role": "public reference only",
           "installed_on_handset": "unknown", "source_url": args.source_url,
           "verified_vpu_hfi_compatibility": False, "tested_on_hardware": False}
    try:
        if args.stock_zip:
            doc["stock_zip"] = inventory_zip(args.stock_zip)
        if args.extracted_root:
            doc["firmware_files"] = inventory_extracted(args.extracted_root)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"INVENTORY FAILED: {exc}", file=sys.stderr)
        return 2
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"Inventory written: {args.json_out}; phone-installed firmware and runtime remain UNKNOWN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
