#!/usr/bin/env python3
"""Android boot/vendor_boot v4 layout auditor and *unflashable* candidate builder.

Purpose: inspect user-supplied local reference images, structurally round-trip
their sections, or build UNSIGNED candidate files from explicitly supplied
mainline payloads. Never writes a block device, invokes fastboot/adb, or
copies Android ramdisks/bootconfig into a native candidate automatically.

Layout reference: AOSP system/tools/mkbootimg/include/bootimg/bootimg.h,
Android boot header v4 and vendor_boot header v4.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

BOOT_MAGIC, VENDOR_MAGIC, PAGE = b"ANDROID!", b"VNDRBOOT", 4096
BOOT_HDR, VENDOR_HDR, TABLE_ENTRY = 1584, 2128, 108


def align(n, page):
    return (n + page - 1) // page * page


def u32(blob, off):
    if off + 4 > len(blob):
        raise ValueError("truncated header at %s" % off)
    return struct.unpack_from("<I", blob, off)[0]


def safe_slice(data, off, length, where):
    if off < 0 or length < 0 or off + length > len(data):
        raise ValueError("%s extends beyond image (%d+%d > %d)" %
                         (where, off, length, len(data)))
    return data[off:off+length]


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def magic_type(blob):
    if blob.startswith(b"\x1f\x8b"): return "gzip"
    if blob.startswith(b"\x04\x22\x4d\x18"): return "lz4-frame"
    if blob.startswith(b"\x02\x21\x4c\x18"): return "lz4-legacy"
    if blob.startswith(b"\x28\xb5\x2f\xfd"): return "zstd"
    if blob.startswith(b"\xfd7zXZ\0"): return "xz"
    if blob.startswith((b"070701", b"070702")): return "cpio-newc"
    return "unknown (not identified by prefix)"


def cstring(blob):
    return blob.split(b"\0", 1)[0].decode("utf-8", "replace")


def inspect_boot(data):
    if len(data) < PAGE or data[:8] != BOOT_MAGIC:
        raise ValueError("not a boot.img (v4) magic/header")
    if u32(data, 40) != 4 or u32(data, 20) != BOOT_HDR:
        raise ValueError("unsupported boot header version or size")
    kern, ram, signature = u32(data, 8), u32(data, 12), u32(data, 1580)
    offsets = [PAGE, PAGE + align(kern, PAGE),
               PAGE + align(kern, PAGE) + align(ram, PAGE)]
    bodyend = offsets[2] + align(signature, PAGE)
    if bodyend > len(data):
        raise ValueError("truncated boot sections")
    parts = [("header", 0, PAGE), ("kernel", offsets[0], kern),
             ("ramdisk", offsets[1], ram), ("signature", offsets[2], signature)]
    return {"kind": "boot", "version": 4, "header_size": BOOT_HDR,
            "page_size": PAGE, "bytes": len(data), "sha256": sha(data),
            "os_version_raw": u32(data, 16), "cmdline": cstring(data[44:1580]),
            "sections": [{"name": name, "offset": off, "bytes": size,
                          "sha256": sha(safe_slice(data, off, size, name)),
                          "compression": magic_type(data[off:off+min(size, 8)])
                          if name in ("kernel", "ramdisk") else None}
                         for name, off, size in parts],
            "trailing_partition_padding": len(data) - bodyend}


def inspect_vendor(data):
    if len(data) < VENDOR_HDR or data[:8] != VENDOR_MAGIC:
        raise ValueError("not a vendor_boot.img magic/header")
    version, page = u32(data, 8), u32(data, 12)
    if version != 4 or u32(data, 2096) != VENDOR_HDR:
        raise ValueError("unsupported vendor_boot header version/size")
    if page < 2048 or page > 65536 or page & (page - 1):
        raise ValueError("invalid vendor_boot page size")
    ram, dtb = u32(data, 24), u32(data, 2100)
    ts, count, es, conf = [u32(data, off) for off in (2112, 2116, 2120, 2124)]
    if es != TABLE_ENTRY or count * es > ts or count > 1024:
        raise ValueError("invalid vendor ramdisk table layout")
    off = align(VENDOR_HDR, page)
    sections = []
    for name, size in (("vendor_ramdisk", ram), ("dtb_region", dtb),
                       ("ramdisk_table", ts), ("bootconfig", conf)):
        safe_slice(data, off, size, name)
        sections.append({"name": name, "offset": off, "bytes": size,
                         "sha256": sha(data[off:off+size]),
                         "compression": magic_type(data[off:off+8])
                         if name == "vendor_ramdisk" else None})
        off += align(size, page)
    if off > len(data):
        raise ValueError("truncated vendor_boot layout")
    table = next(x for x in sections if x["name"] == "ramdisk_table")
    rows = []
    for index in range(count):
        raw = safe_slice(data, table["offset"] + index * es, es, "ramdisk table entry")
        size, ram_off, kind = struct.unpack_from("<III", raw)
        if ram_off + size > ram:
            raise ValueError("vendor ramdisk fragment exceeds section")
        rows.append({"index": index, "bytes": size, "offset": ram_off,
                     "type": kind, "name": cstring(raw[12:44]),
                     "board_id": list(struct.unpack_from("<16I", raw, 44))})
    config = next(x for x in sections if x["name"] == "bootconfig")
    cfgdata = safe_slice(data, config["offset"], conf, "bootconfig")
    keys = []
    for line in cfgdata.decode("utf-8", "replace").splitlines():
        if "=" in line:
            keys.append(line.split("=", 1)[0].strip())
    # One vendor_boot DTB region can contain multiple FDTs. We only
    # identify aligned contiguous FDT boundaries; overlays are not applied.
    dreg = next(x for x in sections if x["name"] == "dtb_region")
    fdtdata = safe_slice(data, dreg["offset"], dtb, "dtb region")
    fdts, pos = [], 0
    while pos + 8 <= len(fdtdata) and fdtdata[pos:pos+4] == b"\xd0\x0d\xfe\xed":
        size = int.from_bytes(fdtdata[pos+4:pos+8], "big")
        if size < 40 or pos + size > len(fdtdata):
            raise ValueError("FDT header size beyond vendor_boot DTB region")
        fdts.append({"relative_offset": pos, "bytes": size,
                     "sha256": sha(fdtdata[pos:pos+size])})
        pos = align(pos + size, 4)
    return {"kind": "vendor_boot", "version": 4, "bytes": len(data),
            "sha256": sha(data), "page_size": page, "header_size": VENDOR_HDR,
            "kernel_addr_raw": u32(data, 16), "ramdisk_addr_raw": u32(data, 20),
            "tags_addr_raw": u32(data, 2076),
            "dtb_addr_raw": struct.unpack_from("<Q", data, 2104)[0],
            "name": cstring(data[2080:2096]),
            "cmdline": cstring(data[28:2076]),
            "sections": sections, "ramdisk_table": rows,
            "bootconfig_keys": keys, "dtb_fdt_chunks": fdts,
            "dtb_unparsed_bytes": len(fdtdata) - pos,
            "trailing_partition_padding": len(data) - off}


def repack_structural(data, report):
    page = report["page_size"]
    regions = report["sections"]
    # Explicitly recopy unmodified raw components and intervening pages,
    # then compare the entire image, including partition padding. This is
    # an *identity* repack only, not evidence that an edited image will boot.
    out, cursor = bytearray(), 0
    for section in regions:
        start = section["offset"]
        if start < cursor:
            raise ValueError("overlapping sections")
        out += safe_slice(data, cursor, start - cursor, "preceding padding")
        out += safe_slice(data, start, section["bytes"], section["name"])
        cursor = start + section["bytes"]
        next_aligned = align(cursor, page)
        out += safe_slice(data, cursor, min(next_aligned, len(data)) - cursor,
                          "section padding")
        cursor = next_aligned
    out += safe_slice(data, cursor, len(data) - cursor, "partition padding")
    if bytes(out) != data:
        raise ValueError("structural identity reconstruction mismatch")
    return sha(out)


def padded(data, page):
    return data + bytes(align(len(data), page) - len(data))


def sized_text(s, size):
    raw = s.encode("utf-8")
    if b"\0" in raw or len(raw) >= size:
        raise ValueError("text field too long or contains NUL")
    return raw + bytes(size - len(raw))


def prototype(args, boot, vendor):
    # Explicit new payloads only. Absolutely no copies of stock Android
    # vendor ramdisk or bootconfig. No bootloader signing/AVB is performed.
    k = Path(args.kernel).read_bytes()
    initrd = Path(args.initramfs).read_bytes()
    dtb = Path(args.dtb).read_bytes()
    vr = Path(args.vendor_ramdisk).read_bytes()
    cfg = Path(args.bootconfig).read_bytes()
    if not k or not initrd or not dtb or not vr:
        raise ValueError("all kernel/ramdisk/DTB/vendor-ramdisk inputs required")
    config = json.loads(Path(args.ramdisk_descriptor).read_text())
    if not isinstance(config, dict) or "name" not in config or "type" not in config:
        raise ValueError("explicit JSON name/type/board_id required")
    board_ids = config.get("board_id")
    if not isinstance(board_ids, list) or len(board_ids) != 16 or any(
            not isinstance(v, int) or v < 0 or v > 0xffffffff for v in board_ids):
        raise ValueError("board_id must have exactly 16 explicit unsigned words")
    kind = config["type"]
    if type(kind) is not int or kind not in (1, 2, 3):
        raise ValueError("vendor ramdisk type must be explicit 1/2/3")
    bh = bytearray(PAGE)
    bh[:BOOT_HDR] = boot[:BOOT_HDR]
    struct.pack_into("<II", bh, 8, len(k), len(initrd))
    bh[44:1580] = sized_text(args.cmdline, 1536)
    struct.pack_into("<I", bh, 1580, 0)  # unsigned, no boot signature
    boot_candidate = bytes(bh) + padded(k, PAGE) + padded(initrd, PAGE)
    page = u32(vendor, 12)
    vh = bytearray(page)
    vh[:VENDOR_HDR] = vendor[:VENDOR_HDR]
    vh[28:2076] = sized_text(args.vendor_cmdline, 2048)
    vh[2080:2096] = sized_text(args.vendor_name, 16)
    struct.pack_into("<I", vh, 24, len(vr))
    struct.pack_into("<I", vh, 2100, len(dtb))
    struct.pack_into("<IIII", vh, 2112, TABLE_ENTRY, 1, TABLE_ENTRY, len(cfg))
    entry = struct.pack("<III32s16I", len(vr), 0, kind,
                        sized_text(config["name"], 32), *board_ids)
    vendor_candidate = (bytes(vh) + padded(vr, page) + padded(dtb, page) +
                        padded(entry, page) + padded(cfg, page))
    # Re-parse both outputs before writing. No stock padding is copied.
    x, y = inspect_boot(boot_candidate), inspect_vendor(vendor_candidate)
    if y["ramdisk_table"][0]["bytes"] != len(vr):
        raise ValueError("vendor ramdisk descriptor failed")
    output = Path(args.out_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "boot-candidate.UNSIGNED.img").write_bytes(boot_candidate)
    (output / "vendor_boot-candidate.UNSIGNED.img").write_bytes(vendor_candidate)
    (output / "candidate-layout.json").write_text(json.dumps(
        {"boot": x, "vendor_boot": y, "runtime_validated": False,
         "avb_signed": False, "flash_tested": False,
         "note": "structural demonstration only; not a phone flashing recipe"},
        indent=2) + "\n")
    print("UNSIGNED candidate layout produced; NO flash/boot success claimed")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["inspect", "roundtrip", "prototype"])
    ap.add_argument("boot_img", type=Path)
    ap.add_argument("vendor_boot_img", type=Path)
    ap.add_argument("--out-dir", default="out-boot-layout")
    ap.add_argument("--kernel")
    ap.add_argument("--initramfs")
    ap.add_argument("--dtb")
    ap.add_argument("--vendor-ramdisk")
    ap.add_argument("--bootconfig")
    ap.add_argument("--ramdisk-descriptor")
    ap.add_argument("--cmdline")
    ap.add_argument("--vendor-cmdline")
    ap.add_argument("--vendor-name")
    args = ap.parse_args()
    boot, vendor = args.boot_img.read_bytes(), args.vendor_boot_img.read_bytes()
    b, v = inspect_boot(boot), inspect_vendor(vendor)
    if args.action in ("inspect", "roundtrip"):
        if args.action == "roundtrip":
            if repack_structural(boot, b) != sha(boot) or repack_structural(vendor, v) != sha(vendor):
                raise ValueError("roundtrip digest mismatch")
        print(json.dumps({"boot": b, "vendor_boot": v,
                          "identity_roundtrip": args.action == "roundtrip"}, indent=2))
    else:
        for opt in ("kernel", "initramfs", "dtb", "vendor_ramdisk",
                    "bootconfig", "ramdisk_descriptor", "cmdline",
                    "vendor_cmdline", "vendor_name"):
            if getattr(args, opt) is None:
                ap.error("--%s required for candidate" % opt.replace("_", "-"))
        prototype(args, boot, vendor)


if __name__ == "__main__":
    main()
