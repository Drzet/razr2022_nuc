#!/usr/bin/env python3
"""Bounded Motorola oneli wireless inventory. Metadata only, never export blobs.

Reuses VPU's pinned ZIP64 range, Motorola container and sparse decoders.
Runs on ephemeral CI host; original extracted binaries were not retained.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

RADIO_HASH = "bcaac550d908ea72f08e9a1782714a46f52d26f20ec11c7e32f97140677769ca"
NON_HLOS_HASH = "03d37634aa39ff9af06d3b583267e6d166996c22e7b4f06b0bcb7d7b4031a1d9"
NON_HLOS_DECODED_HASH = "2ea61a0b5d31b626358f0b72c102131535f08ae3fb279b1857e646b0675416c6"
PACKAGE_HASH = "620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c"

# Broad targeted search, including board-data names but not generic .mbn files.
WIRELESS = re.compile(
    r"(?i)(wlan|wi[-_]?fi|wcn|qca|qcw|cnss|btfm|bluetooth|btfw|bt[-_]?nv|"
    r"hpbt|hpnv|bdwlan|board[-_.]?2|regdb|amss|m3[.]bin|wlfw|"
    r"qcacld|bdf|bd[-_]?data|qwlan|wcss|q6wcn|macaddr|bt[-_]?addr)"
)
VERSION = re.compile(rb"QC_IMAGE_VERSION_STRING=([^\x00\r\n]{1,128})")

def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def sha(data):
    return hashlib.sha256(data).hexdigest()

def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=180)

def scan(image, label, temp):
    """Read-only mount of recognized filesystems, complete filename enumeration."""
    meta = {"source": label, "image_bytes": image.stat().st_size,
            "image_sha256": sha_file(image)}
    b = run(["blkid", "-p", "-o", "value", "-s", "TYPE", str(image)])
    f = run(["file", "-b", str(image)])
    typ = b.stdout.strip() if b.returncode == 0 else None
    meta["blkid"] = typ
    meta["file_type"] = f.stdout.strip()[:160]
    if typ not in ("ext2", "ext3", "ext4", "vfat", "erofs"):
        meta["state"] = "unrecognized filesystem, no claim that firmware absent"
        return meta
    mnt = temp / ("mount-" + str(len(list(temp.glob("mount-*")))))
    mnt.mkdir()
    opts = "loop,ro,noload" if typ == "ext4" else "loop,ro"
    mounted = run(["sudo", "mount", "-t", typ, "-o", opts, str(image), str(mnt)])
    if mounted.returncode:
        meta.update(state="read-only mount failed; no negative search",
                    mount_error=mounted.stderr[:240])
        return meta
    files, hits, symlinks = 0, [], []
    try:
        for folder, dirs, names in os.walk(mnt, followlinks=False):
            dirs.sort()
            for name in sorted(names):
                p = Path(folder) / name
                rel = p.relative_to(mnt).as_posix()
                files += 1
                if not WIRELESS.search(rel):
                    continue
                if p.is_symlink():
                    symlinks.append({"path": rel, "target": os.readlink(p)})
                elif p.is_file():
                    candidate = {"path": rel, "bytes": p.stat().st_size,
                                 "sha256": sha_file(p)}
                    if p.stat().st_size <= 64 * 1024 * 1024:
                        with p.open("rb") as s:
                            head = s.read(min(p.stat().st_size, 1024 * 1024))
                        v = VERSION.search(head)
                        if v:
                            candidate["qc_version"] = v.group(1).decode("ascii", "replace")
                    hits.append(candidate)
        meta.update(state="complete read-only filename scan",
                    files_examined=files, matching_files=hits,
                    matching_symlinks=symlinks,
                    filename_pattern=WIRELESS.pattern)
    finally:
        umount = run(["sudo", "umount", str(mnt)])
        if umount.returncode:
            raise RuntimeError("read-only unmount failed: " + umount.stderr[:180])
    return meta

def sparse_or_raw(blob, filename, temp, radio_helpers):
    p = temp / filename
    if blob[:4] == b"\x3a\xff\x26\xed":
        sparse = radio_helpers.decode_android_sparse(memoryview(blob), p)
        return p, sparse
    p.write_bytes(blob)
    return p, {"type": "raw/unknown", "sha256": sha(blob)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vpu-reference", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    refs = args.vpu_reference / "scripts"
    ranges = load_module(refs / "inspect-oneli-stock-ranges.py", "stock_ranges")
    radio_helpers = load_module(refs / "inspect-oneli-moto-radio.py", "moto_radio")
    ranges.TARGETS = ("radio.img", "BTFM.bin")
    ranges.COMPRESSED_CAP = 145 * 1024 * 1024
    ranges.EXPANDED_CAP = 230 * 1024 * 1024
    index, central_dir = ranges.metadata(ranges.STOCK_URL)
    report = {
        "provenance": {"motorola_build": "U2SLS34.1-42-14-11",
                       "archive_sha256_verified_prior_run": PACKAGE_HASH,
                       "archive_full_rehash_performed": False,
                       "source_script_revision": "pinned from the checked-out razr/vpu ref",
                       "extraction": "only ZIP64 selected members, never complete archive"},
        "zip_central_directory": central_dir,
        "target_members": {},
        "testing": {"motorola_stock_reference": True,
                    "oneli_loaded_firmware_tested": False,
                    "native_linux_radio_tested": False},
    }
    with tempfile.TemporaryDirectory(prefix="oneli-wireless-") as td:
        temp = Path(td)
        # BTFM first, low-cost. Metadata and filenames only.
        for member_name in ("BTFM.bin", "radio.img"):
            if member_name not in index:
                report["target_members"][member_name] = {
                    "state": "not present by this exact case in ZIP index",
                    "other_case_names_not_searched": True}
                continue
            blob = ranges.member(ranges.STOCK_URL, member_name, index[member_name])
            m = {"archive_member_sha256": sha(blob), "bytes": len(blob),
                 "compressed_bytes": index[member_name]["compressed_size"],
                 "crc32": index[member_name]["crc32"]}
            report["target_members"][member_name] = m
            if member_name == "BTFM.bin":
                image, format_info = sparse_or_raw(blob, "btfm-decoded.img", temp, radio_helpers)
                m["reconstruction"] = format_info
                m["filesystem"] = scan(image, "BTFM.bin", temp)
                print("BTFM.bin inspected:", m["filesystem"]["state"], flush=True)
            else:
                if m["archive_member_sha256"] != RADIO_HASH:
                    raise RuntimeError("radio.img differs from pinned Motorola reference")
                parsed = radio_helpers.parse_single_lonely(blob)
                if parsed is None:
                    raise RuntimeError("radio.img no longer matches known SINGLE_N_LONELY")
                kind, entries = parsed
                m["container"] = kind
                m["direct_members"] = [
                    {"name": name, "bytes": size} for name, offset, size in entries
                ]
                for name, offset, size in entries:
                    if name not in ("NON-HLOS.bin", "fsg.mbn"):
                        continue
                    inner = memoryview(blob)[offset:offset+size]
                    if name == "NON-HLOS.bin" and sha(inner) != NON_HLOS_HASH:
                        raise RuntimeError("NON-HLOS.bin does not match pinned hash")
                    image, format_info = sparse_or_raw(inner, 
                        "non-hlos-decoded.img" if name == "NON-HLOS.bin" else "fsg-image.img",
                        temp, radio_helpers)
                    if name == "NON-HLOS.bin" and sha_file(image) != NON_HLOS_DECODED_HASH:
                        raise RuntimeError("NON-HLOS decoded image does not match pinned hash")
                    record = {"source_hash": sha(inner), "reconstruction": format_info,
                              "filesystem": scan(image, name, temp)}
                    m[name] = record
                    print(name, "inspected:", record["filesystem"]["state"],
                          len(record["filesystem"].get("matching_files", [])),
                          "wireless filename candidates", flush=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("=== BEGIN VERIFIED WIRELESS INVENTORY JSON ===", flush=True)
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)
    print("=== END VERIFIED WIRELESS INVENTORY JSON ===", flush=True)

if __name__ == "__main__":
    main()
