#!/usr/bin/env python3
"""Bounded ZIP64 HTTP-range inspection of public oneli ROM; metadata only.

Downloads ONLY selected compressed ZIP members, not the 4.35GB ZIP. Rejects
servers that ignore Range and refuses oversized responses. Does not identify
the handset's installed firmware, trust a bootloader overlay, or persist blobs.
"""
import argparse
import hashlib
import json
import re
import struct
import subprocess
import tempfile
import urllib.request
import zlib
from pathlib import Path

STOCK_URL = ("https://mirrors-obs-1.lolinet.com/firmware/lenomola/2022/oneli/"
             "official/RETGB/XT2251-1_ONELI_RETEU_14_U2SLS34.1-42-14-11_"
             "subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.xml.zip")
EXPECTED_ZIP_BYTES = 4353164507
COMPRESSED_CAP = 26 * 1024 * 1024
EXPANDED_CAP = 128 * 1024 * 1024
META_CAP = 1024 * 1024
TARGETS = ("dtbo.img", "boot.img", "vendor_boot.img", "flashfile.xml", "servicefile.xml")


def http_range(url, start, length):
    if length <= 0 or length > COMPRESSED_CAP:
        raise ValueError("refusing oversized range request")
    req = urllib.request.Request(url, headers={
        "Range": f"bytes={start}-{start+length-1}",
        "Accept-Encoding": "identity",
        "User-Agent": "razr-oneli-stock-inspection/1.0",
    })
    with urllib.request.urlopen(req, timeout=35) as response:
        if response.status != 206:
            raise ValueError(f"server did not honor byte range (HTTP {response.status})")
        cr = response.headers.get("Content-Range", "")
        m = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", cr)
        if not m or (int(m[1]), int(m[2]), int(m[3])) != (
                start, start + length - 1, EXPECTED_ZIP_BYTES):
            raise ValueError(f"bad Content-Range {cr!r}")
        data = response.read(length + 1)
        if len(data) != length:
            raise ValueError("range response wrong size")
        return data


def metadata(url):
    tail = http_range(url, EXPECTED_ZIP_BYTES - 65536, 65536)
    p = tail.rfind(b"PK\x05\x06")
    if p == -1 or p + 22 > len(tail):
        raise ValueError("ZIP end-of-central-directory record not found")
    eocd = struct.unpack_from("<4s4H2IH", tail, p)
    total_entries, cd_size, cd_offset = eocd[4], eocd[5], eocd[6]
    if cd_size == 0xffffffff or cd_offset == 0xffffffff or total_entries == 0xffff:
        locator = tail.rfind(b"PK\x06\x07", 0, p)
        if locator == -1 or locator + 20 > p:
            raise ValueError("ZIP64 locator not in last 65536 bytes")
        marker, disk, eocd64_offset, disks = struct.unpack_from("<4sIQI", tail, locator)
        hdr = http_range(url, eocd64_offset, 56)
        if hdr[:4] != b"PK\x06\x06":
            raise ValueError("ZIP64 EOCD mismatch")
        cd_count, cd_size, cd_offset = struct.unpack_from("<QQQ", hdr, 32)
        total_entries = cd_count
    if cd_size > META_CAP or cd_offset + cd_size > EXPECTED_ZIP_BYTES:
        raise ValueError("central directory outside bounded region")
    cd = http_range(url, cd_offset, cd_size)
    entries, i = {}, 0
    while i < len(cd):
        if i + 46 > len(cd) or cd[i:i+4] != b"PK\x01\x02":
            raise ValueError(f"bad central directory entry at {i}")
        q = struct.unpack_from("<4s6H3I5H2I", cd, i)
        method, crc, comp, uncomp = q[4], q[7], q[8], q[9]
        name_len, extra_len, comment_len, local = q[10], q[11], q[12], q[16]
        name = cd[i+46:i+46+name_len].decode("utf-8", "replace")
        if name in TARGETS:
            if local == 0xffffffff:
                raise ValueError(f"ZIP64 extended local offset required for {name}")
            entries[name] = {"local_header": local, "compressed_size": comp,
                             "uncompressed_size": uncomp, "method": method,
                             "crc32": f"{crc:08x}"}
        i += 46 + name_len + extra_len + comment_len
    return entries, {"central_directory_offset": cd_offset, "central_directory_size": cd_size,
                     "central_directory_entries": total_entries}


def member(url, name, info):
    size = info["compressed_size"]
    if size > COMPRESSED_CAP or info["uncompressed_size"] > EXPANDED_CAP:
        raise ValueError(f"{name}: member exceeds bounded extraction caps")
    header = http_range(url, info["local_header"], 30)
    if header[:4] != b"PK\x03\x04":
        raise ValueError(f"{name}: bad local file header")
    local_name_len, local_extra_len = struct.unpack_from("<HH", header, 26)
    at = info["local_header"] + 30 + local_name_len + local_extra_len
    compressed = http_range(url, at, size)
    if info["method"] == 0:
        blob = compressed
    elif info["method"] == 8:
        blob = zlib.decompress(compressed, -15, EXPANDED_CAP)
    else:
        raise ValueError(f"{name}: unhandled compression method")
    if len(blob) != info["uncompressed_size"]:
        raise ValueError(f"{name}: wrong uncompressed size")
    if f"{zlib.crc32(blob):08x}" != info["crc32"]:
        raise ValueError(f"{name}: ZIP CRC32 verification failed")
    return blob


def boot_header(name, blob):
    r = {"sha256": hashlib.sha256(blob).hexdigest(), "size": len(blob),
         "magic": blob[:8].decode("ascii", "replace")}
    if name == "boot.img" and blob[:8] == b"ANDROID!":
        r["kernel_size"], r["ramdisk_size"], r["os_version"], r["header_size"] = (
            struct.unpack_from("<4I", blob, 8))
        r["header_version"] = struct.unpack_from("<I", blob, 40)[0]
    elif name == "vendor_boot.img" and blob[:8] == b"VNDRBOOT":
        r["header_version"], r["page_size"] = struct.unpack_from("<2I", blob, 8)
    return r


def dtbo_inspect(blob):
    if len(blob) < 32 or int.from_bytes(blob[:4], "big") != 0xd7b7ab1e:
        raise ValueError("missing Android DT table magic")
    hdr = struct.unpack_from(">8I", blob)
    _, total, header, entsize, count, offset, page, version = hdr
    if header < 32 or total > len(blob) or entsize < 32 or count > 128 or (
            offset + count * entsize > total):
        raise ValueError("malformed DT table bounds")
    entries = []
    for i in range(count):
        size, at, ident, rev = struct.unpack_from(">4I", blob, offset + i*entsize)
        if at + size > total or at < offset + count * entsize or size == 0:
            raise ValueError("bad FDT image bounds")
        data = blob[at:at+size]
        row = {"index": i, "id": ident, "rev": rev, "fdt_sha256": hashlib.sha256(data).hexdigest()}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate.dtb"
            path.write_bytes(data)
            for prop in ("compatible", "model"):
                cmd = subprocess.run(["fdtget", "-t", "s", str(path), "/", prop],
                                     capture_output=True, text=True, timeout=10)
                if cmd.returncode == 0:
                    row["root_" + prop] = cmd.stdout.strip()
            cmd = subprocess.run(["dtc", "-q", "-I", "dtb", "-O", "dts", str(path)],
                                 capture_output=True, text=True, timeout=10)
            row["dtc_exit"] = cmd.returncode
            if cmd.returncode == 0:
                lines = cmd.stdout.splitlines()
                row["selected_compatible_strings"] = sorted(set(
                    value for line in lines
                    if "compatible =" in line
                    for value in re.findall(r'"([^"]+)"', line)
                    if any(term in value.lower() for term in
                           ("oneli", "cape", "sm8475", "vidc", "iris", "gpu", "usb", "pmic"))
                ))[:90]
                row["has_video_firmware_reference"] = "vpu20_4v" in cmd.stdout
                row["has_oneli_reference"] = "oneli" in cmd.stdout.lower()
        entries.append(row)
    return {"dtbo_sha256": hashlib.sha256(blob).hexdigest(),
            "entry_count": len(entries), "entries": entries,
            "selection": "unknown; ZIP candidate metadata, not live device DT"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=STOCK_URL)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    entries, meta = metadata(args.url)
    report = {"source_url": args.url, "zip_size_assumed_from_verified_stock": EXPECTED_ZIP_BYTES,
              "byte_ranges_not_full_zip_rehash": True, "zip_index": meta, "members": {}}
    for name in TARGETS:
        if name not in entries:
            report["members"][name] = {"state": "not in ZIP central directory"}
            continue
        blob = member(args.url, name, entries[name])
        item = boot_header(name, blob)
        if name == "dtbo.img":
            item["dtbo"] = dtbo_inspect(blob)
        elif name.endswith(".xml"):
            # No OEM raw XML is persisted; expose only file count/length.
            item["text_scope"] = "content not published"
        report["members"][name] = item
        print(f"{name}: SHA256 {item['sha256']}, bytes {len(blob)}")
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("Metadata-only inspection succeeded; no signed firmware was acquired")


if __name__ == "__main__":
    main()
