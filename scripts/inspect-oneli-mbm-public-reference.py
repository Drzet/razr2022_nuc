#!/usr/bin/env python3
"""Read-only, bounded oneli MBM bootloader inventory. Proprietary bytes remain ephemeral."""
import binascii
import hashlib
import json
import re
import struct
import subprocess
import tempfile
import urllib.request
import zlib
from pathlib import Path

SOURCE = ("https://mirrors-obs-1.lolinet.com/firmware/lenomola/2022/oneli/"
          "official/RETGB/XT2251-1_ONELI_RETEU_14_U2SLS34.1-42-14-11_"
          "subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.xml.zip")
ZIP_SIZE = 4353164507
CD_OFFSET = 4353161182
CD_SIZE = 3227
EXPECTED = {"name": "bootloader.img", "compressed": 6756902,
            "uncompressed": 29116160, "crc32": 0xbf11c10f}
MAX_RANGE = 8 * 1024 * 1024
KEYWORDS = [b"MBM", b"Motorola", b"oneli", b"Fastboot", b"fastboot",
            b"BootLinux", b"LoadImageAndAuth", b"KernelBaseAddr",
            b"KernelSize", b"bootconfig", b"BootConfig", b"vendor_boot",
            b"VendorBoot", b"ramdisk", b"Ramdisk", b"DTBO", b"dtbo",
            b"AVB", b"Avb", b"DeviceTree", b"Fdt", b"boot image",
            b"BootImage", b"Console", b"UART", b"serial",
            b"memmap", b"memory map", b"KernelLoad",
            b"GetDtb", b"GetDtb", b"Uncompress", b"VerifiedBoot"]

def fetch_range(start, length):
    if length <= 0 or length > MAX_RANGE or start < 0 or start + length > ZIP_SIZE:
        raise ValueError("out-of-bounds byte range")
    last = start + length - 1
    req = urllib.request.Request(SOURCE, headers={
        "Range": f"bytes={start}-{last}", "Accept-Encoding": "identity",
        "User-Agent": "oneli-mbm-readonly-static-inventory/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        code = response.status
        cr = response.headers.get("Content-Range", "")
        if code != 206 or cr != f"bytes {start}-{last}/{ZIP_SIZE}":
            raise ValueError(f"HTTP byte range not honored: HTTP={code}, Content-Range={cr}")
        raw = response.read(length+1)
    if len(raw) != length:
        raise ValueError(f"short/long download {len(raw)} != {length}")
    return raw

def get_zip_entry(cd, target):
    pos = 0
    while pos < len(cd):
        if cd[pos:pos+4] != b"PK\x01\x02":
            raise ValueError(f"bad central-directory record offset {pos}")
        (_, made, ver, flags, method, tm, dt, crc, comp, uncomp, name_len,
         extra_len, comment_len, disk, intern, extern, local) = struct.unpack_from(
             "<IHHHHHHIIIHHHHHII", cd, pos)
        pos += 46
        name = cd[pos:pos+name_len].decode("utf-8")
        extra = cd[pos+name_len:pos+name_len+extra_len]
        pos += name_len + extra_len + comment_len
        needs = (uncomp == 0xffffffff, comp == 0xffffffff, local == 0xffffffff)
        if any(needs):
            cursor = 0
            while cursor+4 <= len(extra):
                typ, sz = struct.unpack_from("<HH", extra, cursor)
                cursor += 4
                if typ == 1:
                    values = []
                    at = cursor
                    for required in needs:
                        if required:
                            values.append(struct.unpack_from("<Q", extra, at)[0])
                            at += 8
                    it = iter(values)
                    if needs[0]: uncomp = next(it)
                    if needs[1]: comp = next(it)
                    if needs[2]: local = next(it)
                    break
                cursor += sz
            else:
                raise ValueError("missing ZIP64 extra")
        if name == target:
            return dict(name=name, compressed=comp, uncompressed=uncomp,
                        crc32=crc, local=local, method=method, flags=flags)
    raise ValueError("bootloader.img absent from indexed stock ZIP")

def member_download():
    entry = get_zip_entry(fetch_range(CD_OFFSET, CD_SIZE), EXPECTED["name"])
    for k in ("compressed", "uncompressed", "crc32"):
        if entry[k] != EXPECTED[k]:
            raise ValueError(f"indexed {k} differs from previous inventory: {entry[k]}")
    if entry["flags"] & 1 or entry["method"] not in (0, 8):
        raise ValueError("unsupported/encrypted ZIP member")
    local = fetch_range(entry["local"], 30)
    if local[:4] != b"PK\x03\x04":
        raise ValueError("invalid local header")
    (_, _, flags, method, _, _, _, _, _, nlen, xlen) = struct.unpack("<IHHHHHIIIHH", local)
    if flags != entry["flags"] or method != entry["method"]:
        raise ValueError("inconsistent ZIP headers")
    x = fetch_range(entry["local"]+30, nlen+xlen)
    if x[:nlen] != b"bootloader.img":
        raise ValueError("incorrect ZIP local entry")
    data_at = entry["local"]+30+nlen+xlen
    compressed = fetch_range(data_at, entry["compressed"])
    if method == 8:
        z = zlib.decompressobj(-15)
        decoded = z.decompress(compressed, entry["uncompressed"]+1)
        decoded += z.flush()
        if not z.eof or z.unused_data or z.unconsumed_tail:
            raise ValueError("incomplete deflate or unexpected trailing bytes")
    else:
        decoded = compressed
    if len(decoded) != entry["uncompressed"]:
        raise ValueError("decoded member size mismatch")
    if (binascii.crc32(decoded) & 0xffffffff) != entry["crc32"]:
        raise ValueError("decoded member CRC mismatch")
    return decoded, dict(entry, data_offset_in_source_zip=data_at,
                         sha256=hashlib.sha256(decoded).hexdigest())

def submembers(blob):
    if blob[:256].rstrip(b"\0") != b"SINGLE_N_LONELY":
        return [("bootloader.img", 0, blob)], "unrecognized-flat"
    offset = 256
    items = []
    for i in range(100):
        if offset+256 > len(blob):
            raise ValueError("truncated Motorola member header")
        name = blob[offset:offset+248].split(b"\0",1)[0].decode("ascii","replace")
        size = struct.unpack_from("<Q", blob, offset+248)[0]
        offset += 256
        if name == "LONELY_N_SINGLE":
            break
        if not name or size > len(blob)-offset:
            raise ValueError(f"invalid Motorola member {name!r} at {offset} size {size}")
        items.append((name, offset, blob[offset:offset+size]))
        offset += (size+4095)//4096*4096
    return items, "SINGLE_N_LONELY"

def markers(blob):
    output = {}
    for keyword in KEYWORDS:
        offsets = [m.start() for m in re.finditer(re.escape(keyword), blob, re.IGNORECASE)]
        if offsets:
            output[keyword.decode("ascii")] = dict(count=len(offsets), offsets=offsets[:16])
    return output

def file_ident(blob):
    if blob.startswith(b"\x7fELF"):
        klass, endian = blob[4], blob[5]
        if klass == 2:
            fields = struct.unpack_from("<HHIQQQIHHHHHH", blob, 16)
            machine = fields[1]
            entry = fields[3]
            phoff, shoff = fields[4], fields[5]
        else:
            fields = struct.unpack_from("<HHIIIIIHHHHHH", blob, 16)
            machine = fields[1]
            entry = fields[3]
            phoff, shoff = fields[4], fields[5]
        return dict(type="ELF", elf_class=klass, endian=endian,
                    machine=machine, entry=hex(entry), phoff=phoff, shoff=shoff)
    if blob.startswith(b"MZ"):
        return dict(type="PE-MZ", pe_pointer=hex(struct.unpack_from("<I",blob,0x3c)[0]))
    return dict(type="unknown", header32=blob[:32].hex())

def static_inspect(blob, name, absolute_offset, temp):
    safe = re.sub("[^0-9A-Za-z_.-]", "_", name)[:90]
    row = dict(name=name, offset_in_bootloader_img=absolute_offset,
               size=len(blob), sha256=hashlib.sha256(blob).hexdigest(),
               binary=file_ident(blob), string_markers=markers(blob))
    if blob[:4] == b"\x7fELF":
        p = temp / safe
        p.write_bytes(blob)
        for cmd, key in [(["readelf", "-h", "-l", "-S", str(p)], "elf_headers"),
                         (["readelf", "-s", str(p)], "symbols")]:
            cp = subprocess.run(cmd, capture_output=True, text=True,
                                errors="replace", timeout=30)
            if cp.returncode == 0:
                row[key] = cp.stdout[:10000]
            else:
                row[key+"_error"] = cp.stderr[:2000]
        p.unlink()
    return row

def main():
    outdir = Path("evidence")
    outdir.mkdir(exist_ok=True)
    image, entry = member_download()
    components, container = submembers(image)
    with tempfile.TemporaryDirectory(prefix="oneli-mbm-") as folder:
        temp = Path(folder)
        parts = [static_inspect(data, name, offset, temp)
                 for name,offset,data in components]
    result = dict(
        evidence_type="public-reference-ROM, NOT installed-phone dump",
        archive_url=SOURCE, archived_zip_sha256_preverified=
        "620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c",
        full_zip_sha256_not_recomputed=True,
        zip_member=entry, container=container, components=parts,
        flashed=False, handset_tested=False, raw_binaries_preserved=False,
        no_loader_semantics_claimed=True)
    (outdir/"oneli-mbm-inventory.json").write_text(json.dumps(result,indent=2))
    summary = [
        "Reference only; no installed-partition identity. ZIP member CRC verified.",
        f"bootloader.img SHA-256: {entry['sha256']}",
        f"Container: {container}; components: {len(parts)}"]
    summary += [f"{v['name']} offset={v['offset_in_bootloader_img']} bytes={v['size']} "
                f"sha256={v['sha256']} type={v['binary'].get('type')}"
                for v in parts]
    (outdir/"oneli-mbm-summary.txt").write_text("\n".join(summary)+"\n")
    print("\n".join(summary))
    print("Only metadata and short structural reports are published, never raw firmware")

if __name__ == "__main__":
    main()
