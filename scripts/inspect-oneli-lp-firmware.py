#!/usr/bin/env python3
"""Read-only host examination of source-pinned Android LP partitions and firmware.

Produces ONLY hashes, filenames, metadata, and bounded ELF/MBN layout facts.
Partition bytes, private signatures and raw config payloads are not exported.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

FW_NAME = re.compile(r"(vpu|a7\d\d|c500|gmu|sqe|zap|venus|vidc)", re.I)
VERSION = re.compile(rb"QC_IMAGE_VERSION_STRING=([^\x00\r\n]{1,128})")
MAX_FIRMWARE_SIZE = 128 * 1024**2


def call(command, timeout=180):
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for buf in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(buf)
    return sha.hexdigest()


def binary_metadata(path):
    r = {"size_bytes": path.stat().st_size, "sha256": digest(path)}
    with path.open("rb") as stream:
        head = stream.read(min(path.stat().st_size, MAX_FIRMWARE_SIZE))
    m = VERSION.search(head)
    if m:
        r["qc_image_version_string"] = m.group(1).decode("ascii", "replace")
    if head[:4] == b"\x7fELF" and head[5] == 1:
        bits = head[4]
        r["file_format"] = f"ELF{32 if bits == 1 else 64}"
        if bits == 1 and len(head) >= 52:
            off, entsize, count = struct.unpack_from("<I", head, 28)[0], struct.unpack_from("<H", head, 42)[0], struct.unpack_from("<H", head, 44)[0]
            r["segments"] = []
            for i in range(min(count, 128)):
                p = off + entsize * i
                if entsize < 32 or p + 32 > len(head):
                    break
                typ, poff, vaddr, paddr, fsz, msz, flags = struct.unpack_from("<7I", head, p)
                if typ == 1:
                    r["segments"].append({"file_offset": poff, "vaddr": vaddr, "paddr": paddr,
                                          "file_bytes": fsz, "mem_bytes": msz, "flags": flags})
        elif bits == 2 and len(head) >= 64:
            off = struct.unpack_from("<Q", head, 32)[0]
            entsize, count = struct.unpack_from("<HH", head, 54)
            r["segments"] = []
            for i in range(min(count, 128)):
                p = off + entsize * i
                if entsize < 56 or p + 56 > len(head):
                    break
                typ, flags, poff, vaddr, paddr, fsz, msz, align = struct.unpack_from("<2I6Q", head, p)
                if typ == 1:
                    r["segments"].append({"file_offset": poff, "vaddr": vaddr, "paddr": paddr,
                                          "file_bytes": fsz, "mem_bytes": msz, "align": align,
                                          "flags": flags})
    elif len(head) >= 40:
        words = struct.unpack_from("<10I", head, 0)
        if words[1] in (3, 5, 6) and words[4] <= path.stat().st_size + 65536:
            r["file_format"] = "candidate Qualcomm MBN40 header (not signature validated)"
            r["mbn_header"] = dict(zip(("image_id", "header_version", "image_src",
                  "image_dest_ptr", "image_size", "code_size", "signature_ptr",
                  "signature_size", "cert_chain_ptr", "cert_chain_size"), words))
    return r


def scan_tree(root):
    hits, links, filenames = [], [], []
    for folder, dirs, files in os.walk(root, followlinks=False):
        dirs.sort()
        for name in sorted(files):
            path = Path(folder) / name
            rel = path.relative_to(root).as_posix()
            filenames.append(rel)
            if path.is_symlink():
                if FW_NAME.search(name):
                    links.append({"path": rel, "symlink_target": os.readlink(path)})
            elif path.is_file() and FW_NAME.search(name):
                item = {"path": rel}
                item.update(binary_metadata(path))
                hits.append(item)
    for item in hits:
        stem = re.sub(r"\.(mdt|mbn|b\d\d)$", "", item["path"], flags=re.I)
        siblings = sorted(x for x in filenames if re.match(re.escape(stem) + r"\.(?:mdt|mbn|b\d\d)$", x, re.I))
        if len(siblings) >= 2:
            item["split_firmware_members"] = siblings
    return {"searched_paths": len(filenames), "hits": hits, "named_symlinks": links,
            "search_pattern": FW_NAME.pattern}


def opaque_image_markers(image):
    """Bounded magic/name offsets only; no image bytes or payload extraction."""
    patterns = {
        "ELF": b"\x7fELF", "Android_sparse": b"\x3a\xff\x26\xed",
        "FAT": b"FAT", "Qualcomm_VPU_name": b"vpu20_4v",
        "GMU_name": b"gmu", "SQE_name": b"sqe", "ZAP_name": b"zap",
        "Venus_name": b"venus",
    }
    matches = {name: [] for name in patterns}
    with image.open("rb") as stream:
        location = 0
        overlap = b""
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            data = overlap + block
            lower = data.lower()
            base = location - len(overlap)
            for name, magic in patterns.items():
                cursor = 0
                while len(matches[name]) < 40:
                    i = lower.find(magic.lower(), cursor)
                    if i < 0:
                        break
                    absolute = base + i
                    if absolute >= location - len(overlap) and absolute not in matches[name]:
                        matches[name].append(absolute)
                    cursor = i + 1
            location += len(block)
            overlap = data[-31:]
    return {"bytes_inspected": location,
            "marker_offsets_not_validated_firmware_or_filesystem": {
                name: offsets for name, offsets in matches.items() if offsets}}

def inspect_partition(image, name, mountpoint, extract_dir):
    out = {"container": name, "image_bytes": image.stat().st_size, "image_sha256": digest(image)}
    f = call(["file", "-b", str(image)])
    out["file_type"] = f.stdout.strip()
    b = call(["blkid", "-p", "-o", "value", "-s", "TYPE", str(image)])
    out["blkid_type"] = b.stdout.strip() if b.returncode == 0 else None
    typ = out["blkid_type"]
    if typ == "ext4":
        cmd = ["sudo", "mount", "-t", "ext4", "-o", "loop,ro,noload", str(image), str(mountpoint)]
    elif typ in ("erofs", "vfat", "squashfs", "f2fs"):
        cmd = ["sudo", "mount", "-t", typ, "-o", "loop,ro", str(image), str(mountpoint)]
    else:
        out["state"] = "not_a_recognized_mountable_filesystem"
        if name in ("radio.img", "BTFM.bin"):
            out["opaque_signature_probe"] = opaque_image_markers(image)
        return out
    mounted = call(cmd)
    if mounted.returncode == 0:
        try:
            out["state"] = "filesystem_scanned_via_readonly_mount"
            out.update(scan_tree(mountpoint))
        finally:
            dis = call(["sudo", "umount", str(mountpoint)])
            if dis.returncode:
                raise RuntimeError(f"failed unmounting {name}: {dis.stderr[:300]}")
    elif typ == "erofs":
        dest = extract_dir / re.sub(r"[^a-zA-Z0-9_-]", "_", name)
        dest.mkdir(parents=True, exist_ok=True)
        tool = call(["fsck.erofs", f"--extract={dest}", str(image)], timeout=300)
        if tool.returncode == 0:
            out["state"] = "filesystem_scanned_via_erofs_extract"
            out.update(scan_tree(dest))
        else:
            out["state"] = "filesystem_not_scanned"
            out["mount_error"] = mounted.stderr.strip()[:350]
            out["erofs_extraction_error"] = tool.stderr.strip()[:350]
        shutil.rmtree(dest)
    else:
        out["state"] = "filesystem_not_scanned"
        out["mount_error"] = mounted.stderr.strip()[:350]
    return out


def inspect_vendor_boot(blob):
    with blob.open("rb") as f:
        head = f.read(4096)
    if head[:8] != b"VNDRBOOT" or len(head) < 2128:
        return {"recognized_header": False}
    version, page = struct.unpack_from("<2I", head, 8)
    kernel_addr, ramdisk_addr, ramdisk_size = struct.unpack_from("<3I", head, 16)
    tags_addr = struct.unpack_from("<I", head, 2076)[0]
    name = head[2080:2096].split(b"\0", 1)[0].decode("ascii", "replace")
    header_size, dtb_size = struct.unpack_from("<2I", head, 2096)
    dtb_addr = struct.unpack_from("<Q", head, 2104)[0]
    table_size, table_count, entry_size, bootconfig_size = struct.unpack_from("<4I", head, 2112)
    if version != 4 or page not in (2048, 4096, 8192, 16384) or header_size > page:
        raise ValueError("unexpected vendor_boot v4 structural header")
    align = lambda n: (n + page - 1) // page * page
    ramdisk_offset = align(header_size)
    dtb_offset = ramdisk_offset + align(ramdisk_size)
    table_offset = dtb_offset + align(dtb_size)
    config_offset = table_offset + align(table_size)
    result = {
        "magic": "VNDRBOOT", "version": version, "page_size": page,
        "board_name": name, "kernel_addr": kernel_addr, "ramdisk_addr": ramdisk_addr,
        "tags_addr": tags_addr, "header_size": header_size,
        "vendor_ramdisk_bytes": ramdisk_size, "vendor_ramdisk_offset": ramdisk_offset,
        "dtb_bytes": dtb_size, "dtb_address": dtb_addr, "dtb_offset": dtb_offset,
        "ramdisk_table_bytes": table_size, "ramdisk_table_count": table_count,
        "ramdisk_table_entry_bytes": entry_size, "ramdisk_table_offset": table_offset,
        "bootconfig_bytes": bootconfig_size, "bootconfig_offset": config_offset,
        "validation": "public reference header/layout only, not bootloader selection",
        "ramdisk_table_entries": []
    }
    if config_offset + bootconfig_size > blob.stat().st_size or table_count > 4096:
        raise ValueError("vendor_boot v4 sections exceed image bounds")
    with blob.open("rb") as f:
        for name, start, size in (("vendor_ramdisk_sha256", ramdisk_offset, ramdisk_size),
                                  ("dtb_region_sha256", dtb_offset, dtb_size),
                                  ("ramdisk_table_sha256", table_offset, table_size),
                                  ("bootconfig_sha256", config_offset, bootconfig_size)):
            f.seek(start)
            data = f.read(size)
            result[name] = hashlib.sha256(data).hexdigest()
            if name == "bootconfig_sha256":
                result["bootconfig_keys"] = sorted(set(
                    row.split(b"=", 1)[0].strip().decode("ascii", "replace")
                    for row in data.splitlines() if b"=" in row))[:160]
        if entry_size >= 108 and table_count * entry_size <= table_size:
            f.seek(table_offset)
            for i in range(table_count):
                entry = f.read(entry_size)
                size, offset, typ = struct.unpack_from("<3I", entry)
                fragment_name = entry[12:44].split(b"\0", 1)[0].decode("ascii", "replace")
                board_ids = list(struct.unpack_from("<16I", entry, 44))
                result["ramdisk_table_entries"].append({
                    "index": i, "name": fragment_name, "type": typ,
                    "offset": offset, "size": size,
                    "board_id": board_ids})
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stock-zip", type=Path, required=True)
    p.add_argument("--raw-super", type=Path, required=True)
    p.add_argument("--lp-tool", type=Path, required=True)
    p.add_argument("--work-dir", type=Path, required=True)
    p.add_argument("--json-out", type=Path, required=True)
    a = p.parse_args()
    a.work_dir.mkdir(parents=True, exist_ok=True)
    (a.work_dir / "partition").mkdir(exist_ok=True)
    (a.work_dir / "mount").mkdir(exist_ok=True)
    (a.work_dir / "unpacked-erofs").mkdir(exist_ok=True)
    result = {"reference_zip_sha256": "620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c",
              "stock_build": "U2SLS34.1-42-14-11", "installed_firmware": "unverified",
              "runtime_authentication_or_hfi_test": False,
              "partition_containers": [], "outer_image_candidates": [], "firmware_summary": []}
    cmd = [sys.executable, str(a.lp_tool), "--info", "-f", "json", str(a.raw_super)]
    meta = call(cmd, timeout=90)
    if meta.returncode:
        raise RuntimeError(f"lpunpack info failed: {meta.stderr[:1000]} / {meta.stdout[:800]}")
    try:
        metadata = json.loads(meta.stdout[meta.stdout.index("{"):])
    except (ValueError, json.JSONDecodeError) as e:
        raise RuntimeError(f"unreadable lpunpack metadata: {meta.stdout[:900]}") from e
    # Metadata contains only structural partition addresses/names.
    result["logical_partition_metadata"] = metadata
    partitions = metadata.get("partitions", metadata.get("partition_table", []))
    if not partitions:
        raise RuntimeError("no logical partitions found; cannot claim negative search")
    print("logical partitions:", [row.get("name") for row in partitions], flush=True)
    for part in partitions:
        name = part["name"]
        # One partition at a time avoids accumulating multiple multi-GB images.
        cmd = [sys.executable, str(a.lp_tool), "-p", name,
               str(a.raw_super), str(a.work_dir / "partition")]
        ex = call(cmd, timeout=500)
        image = a.work_dir / "partition" / (name + ".img")
        if ex.returncode or not image.is_file():
            result["partition_containers"].append({
                "container": name, "state": "lp_extraction_failed",
                "error": (ex.stderr + ex.stdout)[-450:]})
            continue
        try:
            row = inspect_partition(image, f"super:{name}",
                                    a.work_dir / "mount", a.work_dir / "unpacked-erofs")
            result["partition_containers"].append(row)
            for hit in row.get("hits", []):
                result["firmware_summary"].append({
                    "container": name, **hit})
            print(f"searched {name}: {row['state']}, {len(row.get('hits', []))} matching names", flush=True)
        finally:
            image.unlink(missing_ok=True)
    with zipfile.ZipFile(a.stock_zip) as zf:
        for name in ("radio.img", "dspso.bin", "BTFM.bin", "vendor_boot.img", "boot.img", "recovery.img", "dtbo.img"):
            if name not in zf.namelist():
                result["outer_image_candidates"].append({"container": name, "state": "not_in_archive"})
                continue
            target = a.work_dir / name
            with zf.open(name) as src, target.open("wb") as dest:
                shutil.copyfileobj(src, dest, 1024*1024)
            try:
                if name == "dtbo.img":
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "stock_ranges", Path(__file__).with_name("inspect-oneli-stock-ranges.py"))
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    info = {"container": name, "state": "four_DTB_candidates_inspected",
                            **binary_metadata(target), "dtbo": mod.dtbo_inspect(target.read_bytes())}
                elif name == "vendor_boot.img":
                    info = {"container": name, **binary_metadata(target),
                            "vendor_boot": inspect_vendor_boot(target),
                            "state": "structural_header_inspected_not_filesystem"}
                else:
                    info = inspect_partition(target, name, a.work_dir / "mount",
                                             a.work_dir / "unpacked-erofs")
                result["outer_image_candidates"].append(info)
                for hit in info.get("hits", []):
                    result["firmware_summary"].append({"container": name, **hit})
            finally:
                target.unlink(missing_ok=True)
    result["searched_filesystems"] = [x["container"] for x in
        result["partition_containers"] + result["outer_image_candidates"]
        if x.get("state", "").startswith("filesystem_scanned")]
    result["unsearched_containers"] = [{"name": x["container"], "state": x["state"]} for x in
        result["partition_containers"] + result["outer_image_candidates"]
        if not x.get("state", "").startswith("filesystem_scanned")]
    result["target_name_search_conclusion"] = (
        "positive_match_in_scanned_filesystems" if result["firmware_summary"]
        else "no_matching_filename_in_scanned_filesystems_ONLY")
    a.json_out.parent.mkdir(parents=True, exist_ok=True)
    a.json_out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("Firmware inventory complete. Names and hashes are NOT secure boot validation.", flush=True)


if __name__ == "__main__":
    main()
