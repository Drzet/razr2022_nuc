#!/usr/bin/env python3
"""Bounded public Moto radio.img member-only fetch and packed-image inspection.

Recognize format by its actual magic. All output is JSON metadata/sha256 only;
no Motorola stock binaries, signatures, or raw payloads are ever published.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import struct
import sys
import tempfile
from pathlib import Path

FW = re.compile(r"(vpu|venus|vidc|a7\d\d|c500|gmu|sqe|zap)", re.I)
EXPECTED_RADIO_SHA256 = None  # verified member via ZIP CRC32, hash emitted from fetched bytes
RADIO_SIZE = 203319040


def read_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_single_lonely(blob):
    if blob[:256].replace(b"\0", b"") != b"SINGLE_N_LONELY":
        return None
    entries, ptr = [], 256
    for i in range(256):
        if ptr + 256 > len(blob):
            raise ValueError("truncated SINGLE_N_LONELY record")
        header = blob[ptr:ptr+256]
        name = header[:248].split(b"\0", 1)[0].decode("ascii", "replace")
        size = struct.unpack_from("<Q", header, 248)[0]
        start = ptr + 256
        if name == "LONELY_N_SINGLE":
            break
        if not name or not re.fullmatch(r"[\x20-\x7e]{1,247}", name):
            raise ValueError(f"invalid packed member name at record {i}")
        if size > len(blob) - start:
            raise ValueError(f"packed member {name}: size outside radio image")
        entries.append((name, start, size))
        ptr = start + ((size + 4095) // 4096) * 4096
    else:
        raise ValueError("packed header terminator missing")
    return "Motorola SINGLE_N_LONELY", entries


def parse_mbootv1(blob):
    magic = b"MBOOTV1\0"
    if blob[4+20*32:4+20*32+8] != magic:
        return None
    count = struct.unpack_from("<I", blob)[0]
    if count > 20:
        raise ValueError("MBOOTV1 count exceeds table")
    entries = []
    for i in range(count):
        name_raw, begin, end = struct.unpack_from("<24sII", blob, 4+i*32)
        name = name_raw.split(b"\0", 1)[0].decode("ascii", "replace")
        at = 1024 + begin*512
        size = (end+1-begin)*512
        if not name or size < 0 or at+size > len(blob):
            raise ValueError("invalid MBOOTV1 extent")
        entries.append((name, at, size))
    return "Motorola MBOOTV1", entries



def decode_android_sparse(source, target):
    """Interpret Android sparse v1 typed chunks, not concatenated bytes."""
    if len(source) < 28:
        raise ValueError("too small for Android sparse")
    import os
    magic, major, minor, hdr, chdr, block, total, chunks, checksum = struct.unpack_from(
        "<I4H4I", source, 0)
    if (magic != 0xed26ff3a or major != 1 or hdr < 28 or chdr < 12
            or block < 512 or block % 512 or total * block > 1024**3
            or chunks > 100000):
        raise ValueError("not a bounded supported Android sparse v1 image")
    ptr, logical = hdr, 0
    with target.open("w+b") as out:
        for i in range(chunks):
            if ptr + chdr > len(source):
                raise ValueError("truncated sparse chunk header")
            kind, reserved, nblocks, size = struct.unpack_from("<2H2I", source, ptr)
            ptr += chdr
            span = nblocks * block
            if logical + nblocks > total:
                raise ValueError("chunk exceeds Android sparse declared blocks")
            if kind == 0xcac1:
                if size != chdr + span or ptr + span > len(source):
                    raise ValueError("invalid sparse RAW extent")
                out.write(memoryview(source)[ptr:ptr+span])
                ptr += span
            elif kind == 0xcac2:
                if size != chdr + 4 or ptr + 4 > len(source):
                    raise ValueError("invalid sparse FILL extent")
                word = source[ptr:ptr+4]
                ptr += 4
                tile = word * (1024*1024 // 4)
                todo = span
                while todo:
                    n = min(todo, len(tile))
                    out.write(tile[:n])
                    todo -= n
            elif kind == 0xcac3:
                if size != chdr:
                    raise ValueError("invalid DONT_CARE extent")
                out.seek(span, os.SEEK_CUR)
            elif kind == 0xcac4:
                if size != chdr + 4 or nblocks or ptr + 4 > len(source):
                    raise ValueError("invalid CRC32 chunk")
                ptr += 4
            else:
                raise ValueError(f"unsupported sparse chunk {kind:#x}")
            logical += nblocks
        if logical != total or ptr != len(source):
            raise ValueError("sparse bytes/count mismatch")
        out.truncate(total * block)
    return {"type": "Android sparse v1", "block_bytes": block, "total_blocks": total,
            "typed_chunks": chunks, "decoded_bytes": total * block,
            "decoded_sha256": hashlib.sha256(target.read_bytes()).hexdigest()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json-out", required=True, type=Path)
    args = p.parse_args()
    base = Path(__file__).parent
    ranges = read_module(base / "inspect-oneli-stock-ranges.py", "stock_ranges")
    ranges.TARGETS = ("radio.img",)
    ranges.COMPRESSED_CAP = 145 * 1024 * 1024
    ranges.EXPANDED_CAP = 230 * 1024 * 1024
    meta, idx = ranges.metadata(ranges.STOCK_URL)
    if "radio.img" not in meta:
        raise RuntimeError("radio.img absent from ZIP central directory")
    radio = ranges.member(ranges.STOCK_URL, "radio.img", meta["radio.img"])
    if len(radio) != RADIO_SIZE:
        raise RuntimeError("unexpected radio.img bytes from pinned ZIP")
    radio_hash = hashlib.sha256(radio).hexdigest()
    parsed = parse_single_lonely(radio)
    if parsed is None:
        parsed = parse_mbootv1(radio)
    report = {
        "archive": ranges.STOCK_URL,
        "reference_archive_full_sha256_from_prior_hosted_run": "620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c",
        "radio_img_bytes": len(radio), "radio_img_sha256": radio_hash,
        "zip_member_crc32_verified_by_python_zip_decompression": True,
        "stock_installed_firmware_proven": False, "pas_authentication_tested": False,
        "container_magic": "recognized" if parsed else "unknown",
        "file_format": parsed[0] if parsed else "unknown",
        "entries": [],
    }
    if parsed:
        _, members = parsed
        helper = read_module(base / "inspect-oneli-lp-firmware.py", "firmware_metadata")
        report["file_count"] = len(members)
        report["nested_filesystem_search"] = []
        report["located_firmware"] = []
        for name, start, size in members:
            entry = {"name": name, "offset": start, "bytes": size,
                     "sha256": hashlib.sha256(memoryview(radio)[start:start+size]).hexdigest()}
            if FW.search(name):
                with tempfile.TemporaryDirectory() as tmp:
                    f = Path(tmp) / "candidate.bin"
                    f.write_bytes(memoryview(radio)[start:start+size])
                    entry["firmware_metadata"] = helper.binary_metadata(f)
            if name in ("NON-HLOS.bin", "fsg.mbn"):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    original = root / "member.img"
                    original.write_bytes(memoryview(radio)[start:start+size])
                    candidate = original
                    if bytes(memoryview(radio)[start:start+4]) == b"\x3a\xff\x26\xed":
                        candidate = root / "decoded-non-hlos.img"
                        entry["inner_sparse_image"] = decode_android_sparse(
                            memoryview(radio)[start:start+size], candidate)
                    mountpoint = root / "mount"
                    mountpoint.mkdir()
                    (root / "erofs").mkdir()
                    info = helper.inspect_partition(candidate, f"radio:{name}",
                        mountpoint, root / "erofs")
                    entry["nested_filesystem"] = {
                        "state": info["state"], "image_sha256": info["image_sha256"],
                        "image_bytes": info["image_bytes"],
                        "detected_type": info.get("file_type"),
                        "blkid_type": info.get("blkid_type"),
                        "searched_paths": info.get("searched_paths"),
                        "hit_count": len(info.get("hits", [])),
                        "error": info.get("mount_error")}
                    report["nested_filesystem_search"].append(entry["nested_filesystem"])
                    for hit in info.get("hits", []):
                        report["located_firmware"].append({
                            "nested_container": f"radio:{name}", **hit})
                    print(f"nested {name}: {info['state']} ({len(info.get('hits', []))} matching files)", flush=True)
            report["entries"].append(entry)
    else:
        report["reason"] = "neither pinned MBOOTV1 nor SINGLE_N_LONELY magic recognized"
        report["unparsed_blob_firmware_search"] = "NOT a negative search"
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"radio.img: {len(radio)} bytes, SHA256 {radio_hash}; format {report['file_format']}; entries {len(report['entries'])}")
    for x in report["entries"]:
        if FW.search(x["name"]):
            print(f"candidate: {x['name']}, {x['bytes']} bytes, sha256 {x['sha256']}")


if __name__ == "__main__":
    main()
