#!/usr/bin/env python3
"""Bounded, source-hashed FDT property export for oneli Android14 stock images.

Reads only verified dtbo.img, vendor_boot.img, optionally boot.img via existing
ZIP64 HTTP Range reader. No proprietary DTB or ramdisk bytes written or uploaded.
Whole-tree indexes and selected raw property bytes are derived from immutable FDT
structures, NOT a composed/selected bootloader device tree.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import struct
from pathlib import Path

EXPECTED = {
    "dtbo.img": "daf02eb24af55cf4c20569db51b5bca70f0550d035846672ef3054f0c0484bd0",
    "vendor_boot.img": "1c27e22565f6f50919812bfcb5254cea2f3b629d98f5c26a7b54f5ece452036e",
    "boot.img": "287b3b5e3c61dec6a40f2b9203942b57533df206b0ed2ef16ecdb6bbe01e305d",
}
FDT_MAGIC = 0xd00dfeed
TOKEN_BEGIN, TOKEN_END_NODE, TOKEN_PROP, TOKEN_NOP, TOKEN_END = 1, 2, 3, 4, 9
RELEVANT = re.compile(
    r"oneli|cape|board.id|msm.id|pvt|sku|revision|vidc|video|venus|iris|codec|"
    r"vpu|a7\d\d|gpu|gmu|smmu|iommu|interconnect|noc|rpmh|opp|power.domain|"
    r"reserved.memory|memory.region|regulator|pinctrl|gpio|tlmm|pmic|glink|"
    r"usb|eusb|dwc3|type.c|typec|ucsi|ps5169|parade|redriver|retimer|repeater|"
    r"orientation|aux|displayport|display.port|dp.phy|qmp|fsa4480|sbu|"
    r"connector|clock|reset|qup|se5|se18|serial@|i2c@", re.I)
PROPERTY_HINT = re.compile(
    r"reg$|status$|compatible$|model$|(?:board|msm|pmic).id|"
    r"^phandle$|linux,phandle$|^clocks$|^clock.names$|"
    r"^resets$|^reset.names$|^iommus$|^iommu.names$|"
    r"^power.domains$|^power.domain.names$|^operating.points.v2$|"
    r"^required.opps$|^interconnects$|^interconnect.names$|"
    r"^memory.region$|^memory.region.names$|^interrupts.*$|"
    r"^.*(?:supply|gpio|gpios|pinctrl|enable|flip|config.seq|switch)$|"
    r"^(?:target|target.path|ranges|dma.ranges|reg.names)$", re.I)
SENSITIVE = re.compile(r"(serial.?number|imei|meid|mac.?address|bluetooth.?address|"
                       r"wifi.?mac|ssid|pairing.?key|private.?key|device.?id|fingerprint)", re.I)
REFERENCE = re.compile(r"^(?:clocks|resets|iommus|interconnects|power-domains|"
                       r"operating-points-v2|required-opps|memory-region|interrupts-extended|"
                       r"pinctrl-\d+|.*-supply|.*-gpios?|.*gpio.*)$", re.I)
MAX_DTB = 16 * 1024 * 1024
MAX_NODES = 40000
MAX_PROPERTIES = 500000
MAX_PROP_LEN = 1024 * 1024
MAX_RAW_PUBLISHED = 4096


def sha(buf):
    return hashlib.sha256(buf).hexdigest()


def align(n, a):
    return (n + a - 1) // a * a


def u32(data, offset):
    return struct.unpack_from(">I", data, offset)[0]


def nul_string(data, i, end):
    j = data.find(b"\0", i, end)
    if j < 0:
        raise ValueError("unterminated FDT string")
    return data[i:j].decode("utf-8", "replace"), j + 1


def render_prop(name, value):
    row = {"name": name, "bytes": len(value), "sha256": sha(value)}
    if SENSITIVE.search(name):
        row.update({"state": "omitted_sensitive_identifier", "raw": None})
        return row
    row["state"] = "published" if len(value) <= MAX_RAW_PUBLISHED else "omitted_oversized_raw"
    if len(value) <= MAX_RAW_PUBLISHED:
        row["raw_hex"] = value.hex()
    if value and value.endswith(b"\0"):
        chunks = value.rstrip(b"\0").split(b"\0")
        if chunks and all(chunk and all(32 <= b < 127 for b in chunk) for chunk in chunks):
            row["strings"] = [x.decode("ascii") for x in chunks]
    if value and len(value) % 4 == 0:
        row["cells_be_u32"] = [u32(value, i) for i in range(0, min(len(value), 512), 4)]
        if len(value) > 512:
            row["cells_truncated_after_bytes"] = 512
    return row


def parse_fdt(blob, position):
    if position < 0 or position + 40 > len(blob) or u32(blob, position) != FDT_MAGIC:
        raise ValueError("missing FDT header magic")
    total, struct_at, strings_at, reserve_at, version, last, bootcpu, strings_sz, struct_sz = struct.unpack_from(
        ">9I", blob, position + 4)
    if (total < 40 or total > MAX_DTB or position + total > len(blob) or
            version < 16 or struct_at + struct_sz > total or
            strings_at + strings_sz > total or reserve_at + 16 > total):
        raise ValueError("invalid FDT range/version")
    image = bytes(memoryview(blob)[position:position+total])
    strings = bytes(image[strings_at:strings_at+strings_sz])
    offset = struct_at
    end = struct_at + struct_sz
    stack, nodes, seen_props = [], [], 0
    terminated = False
    while offset + 4 <= end:
        tag = u32(image, offset)
        offset += 4
        if tag == TOKEN_BEGIN:
            name, offset = nul_string(image, offset, end)
            offset = align(offset, 4)
            path = "/" + "/".join(n["name"] for n in stack if n["name"])
            path = path.rstrip("/") + ("/" + name if name else "") or "/"
            node = {"name": name, "path": path, "properties": {}}
            nodes.append(node)
            stack.append(node)
            if len(nodes) > MAX_NODES:
                raise ValueError("FDT node cap reached")
        elif tag == TOKEN_END_NODE:
            if not stack:
                raise ValueError("FDT unmatched END_NODE")
            stack.pop()
        elif tag == TOKEN_PROP:
            if not stack or offset + 8 > end:
                raise ValueError("invalid PROP placement")
            length, nameoff = struct.unpack_from(">2I", image, offset)
            offset += 8
            if length > MAX_PROP_LEN or offset + length > end or nameoff >= len(strings):
                raise ValueError("FDT property beyond bounds")
            prop_name, _ = nul_string(strings, nameoff, len(strings))
            stack[-1]["properties"][prop_name] = bytes(image[offset:offset+length])
            offset = align(offset + length, 4)
            seen_props += 1
            if seen_props > MAX_PROPERTIES:
                raise ValueError("FDT property cap reached")
        elif tag == TOKEN_NOP:
            pass
        elif tag == TOKEN_END:
            if stack:
                raise ValueError("FDT END with unclosed nodes")
            terminated = True
            break
        else:
            raise ValueError(f"unrecognized FDT structure token {tag:#x}")
    if not terminated or not nodes or nodes[0]["path"] != "/":
        raise ValueError("incomplete FDT token stream")
    reserves = []
    pos = reserve_at
    while pos + 16 <= total:
        addr, size = struct.unpack_from(">QQ", image, pos)
        pos += 16
        if not addr and not size:
            break
        reserves.append({"address": addr, "size": size})
        if len(reserves) > 1024:
            raise ValueError("too many FDT memreserve entries")
    out = {"byte_offset_in_member_or_region": position, "total_size": total,
           "sha256": sha(image), "fdt_version": version, "last_comp_version": last,
           "boot_cpu_id": bootcpu, "memreserve": reserves,
           "node_count": len(nodes), "property_count": seen_props}
    return nodes, out


def inspect_fdt(blob, at, provenance):
    nodes, result = parse_fdt(blob, at)
    result["provenance"] = provenance
    by_path = {n["path"]: n for n in nodes}
    handles = {}
    for node in nodes:
        for key in ("phandle", "linux,phandle"):
            value = node["properties"].get(key)
            if value and len(value) == 4:
                handles[u32(value, 0)] = node["path"]
    root = nodes[0]["properties"]
    result["root_ids"] = {
        k: render_prop(k, v) for k, v in root.items()
        if k in ("model", "compatible", "qcom,board-id", "qcom,msm-id",
                 "qcom,pmic-id", "moto,board-id", "moto,hw-rev") or
        ("board-id" in k or "msm-id" in k or "hwrev" in k)
    }
    selected = set()
    for n in nodes:
        props = n["properties"]
        compatible = props.get("compatible", b"").decode("ascii", "replace")
        if RELEVANT.search(n["path"]) or RELEVANT.search(compatible) or any(
                RELEVANT.search(key) and PROPERTY_HINT.search(key) for key in props):
            selected.add(n["path"])
    # Include all parents, then candidate referenced-provider nodes. No cell
    # decoding is pretended: phandle matches may be accidental raw integers.
    for path in tuple(selected):
        cur = path
        while cur != "/":
            cur = cur.rsplit("/", 1)[0] or "/"
            selected.add(cur)
    edges = []
    for n in nodes:
        if n["path"] not in selected:
            continue
        for key, value in n["properties"].items():
            if REFERENCE.match(key) and len(value) and len(value) % 4 == 0:
                for pos in range(0, len(value), 4):
                    number = u32(value, pos)
                    if number in handles:
                        edges.append({"from": n["path"], "property": key,
                                      "cell_index": pos // 4, "raw_phandle": number,
                                      "possible_target": handles[number],
                                      "resolution": "within_standalone_FDT_candidate_only"})
                        selected.add(handles[number])
    for path in tuple(selected):
        cur = path
        while cur != "/":
            cur = cur.rsplit("/", 1)[0] or "/"
            selected.add(cur)
    out_nodes, index = [], []
    for n in nodes:
        props = n["properties"]
        status = props.get("status")
        state = "absent" if status is None else status.split(b"\0", 1)[0].decode("ascii", "replace")
        compatible = render_prop("compatible", props["compatible"]).get("strings", []) if "compatible" in props else []
        indexed = {"path": n["path"], "status": state, "compatible": compatible}
        if "phandle" in props and len(props["phandle"]) == 4:
            indexed["phandle"] = u32(props["phandle"], 0)
        if "reg" in props and len(props["reg"]) <= 256:
            indexed["reg_cells"] = render_prop("reg", props["reg"]).get("cells_be_u32", [])
        index.append(indexed)
        if n["path"] not in selected:
            continue
        ancestors = []
        parent = n["path"].rsplit("/", 1)[0] or "/"
        while parent != "/":
            other = by_path.get(parent, {})
            v = other.get("properties", {}).get("status")
            ancestors.append({"path": parent, "status": "absent" if v is None else v.split(b"\0", 1)[0].decode("ascii", "replace")})
            parent = parent.rsplit("/", 1)[0] or "/"
        chosen = {k: render_prop(k, v) for k, v in props.items()
                  if PROPERTY_HINT.search(k) or k in ("#address-cells", "#size-cells", "phandle", "linux,phandle",
                       "qcom,board-id", "qcom,msm-id", "qcom,pmic-id") or
                  n["path"].startswith(("/__fixups__", "/__local_fixups__", "/__symbols__"))}
        out_nodes.append({"path": n["path"], "status": state, "ancestor_status": ancestors,
                          "matching_scope": "standalone_uncomposed_FDT", "properties": chosen})
    result["node_index"] = index
    result["nodes_with_requested_properties"] = out_nodes
    result["candidate_phandle_edges"] = edges
    result["selection"] = "uncomposed public reference, no active on-phone choice"
    return result


def dtbo_parts(buf):
    if len(buf) < 32 or u32(buf, 0) != 0xd7b7ab1e:
        raise ValueError("not Android DTBO table")
    magic, total, header, entry_size, count, entry_off, page, version = struct.unpack_from(">8I", buf, 0)
    if total > len(buf) or count > 64 or entry_size < 32 or entry_off + count * entry_size > total:
        raise ValueError("DTBO table bounds invalid")
    reports = []
    for i in range(count):
        size, offset, boardid, rev, *custom = struct.unpack_from(">8I", buf, entry_off+i*entry_size)
        if offset < entry_off+count*entry_size or offset+size > total:
            raise ValueError("DTBO entry bounds invalid")
        body = buf[offset:offset+size]
        report = inspect_fdt(body, 0, {"member": "dtbo.img", "table_entry": i,
                         "member_entry_offset": offset, "member_entry_bytes": size})
        if report["total_size"] != size:
            raise ValueError("DTBO FDT size differs from entry size")
        report["table_id"] = boardid
        report["table_rev"] = rev
        report["table_custom"] = custom
        reports.append(report)
    return reports


def region_fdts(data):
    found, invalid = [], []
    p = 0
    while p <= len(data) - 40:
        pos = data.find(b"\xd0\x0d\xfe\xed", p)
        if pos < 0:
            break
        if pos % 4:
            invalid.append({"offset": pos, "reason": "unaligned_fdt_magic"})
            p = pos + 4
            continue
        try:
            result = inspect_fdt(data, pos, {"member": "vendor_boot.img", "region": "dtb",
                         "offset_in_dtb_region": pos})
        except ValueError as e:
            invalid.append({"offset": pos, "reason": str(e)})
            p = pos + 4
            continue
        found.append(result)
        p = pos + result["total_size"]
    return found, invalid


def vendor_boot(buf):
    if buf[:8] != b"VNDRBOOT":
        raise ValueError("vendor_boot magic absent")
    ver, page = struct.unpack_from("<2I", buf, 8)
    hsz, dtbsz = struct.unpack_from("<2I", buf, 2096)
    table_sz, table_n, entry_sz, config_sz = struct.unpack_from("<4I", buf, 2112)
    ramdisk_sz = struct.unpack_from("<I", buf, 24)[0]
    fields = {"header_version": ver, "page_size": page, "header_size": hsz,
              "kernel_addr": struct.unpack_from("<I", buf, 16)[0],
              "ramdisk_addr": struct.unpack_from("<I", buf, 20)[0],
              "tags_addr": struct.unpack_from("<I", buf, 2076)[0],
              "dtb_addr": struct.unpack_from("<Q", buf, 2104)[0],
              "vendor_ramdisk_size": ramdisk_sz, "dtb_size": dtbsz,
              "ramdisk_table_size": table_sz, "fragment_count": table_n,
              "fragment_entry_size": entry_sz, "bootconfig_size": config_sz}
    if ver != 4 or hsz < 2112 or page not in (2048, 4096, 8192, 16384):
        raise ValueError("unexpected vendor_boot v4 format")
    rd = align(hsz, page)
    dt = rd + align(ramdisk_sz)
    tbl = dt + align(dtbsz)
    cfg = tbl + align(table_sz)
    if cfg + config_sz > len(buf) or table_n > 2048 or table_n * entry_sz > table_sz:
        raise ValueError("vendor_boot section bounds invalid")
    fields["offsets"] = {"vendor_ramdisk": rd, "embedded_dtb": dt,
                          "fragment_table": tbl, "bootconfig": cfg}
    sections = {"vendor_ramdisk": buf[rd:rd+ramdisk_sz],
                "dtb": buf[dt:dt+dtbsz],
                "table": buf[tbl:tbl+table_sz],
                "bootconfig": buf[cfg:cfg+config_sz]}
    fields["section_sha256"] = {k: sha(v) for k, v in sections.items()}
    fields["sections_first_bytes_hex"] = {k: v[:16].hex() for k, v in sections.items() if k != "bootconfig"}
    fields["bootconfig_keys"] = sorted({
        line.split(b"=", 1)[0].decode("ascii", "replace").strip()
        for line in sections["bootconfig"].splitlines() if b"=" in line})
    fragments = []
    for i in range(table_n):
        record = sections["table"][i*entry_sz:(i+1)*entry_sz]
        if len(record) < 108:
            raise ValueError("vendor_boot v4 fragment descriptor truncated")
        size, offset, typ = struct.unpack_from("<3I", record)
        name = record[12:44].split(b"\0", 1)[0].decode("ascii", "replace")
        board_ids = list(struct.unpack_from("<16I", record, 44))
        frag = sections["vendor_ramdisk"][offset:offset+size]
        if offset+size > ramdisk_sz:
            raise ValueError("vendor ramdisk fragment outside region")
        if frag[:2] == b"\x1f\x8b":
            compression = "gzip"
        elif frag[:4] == b"\x04\x22\x4d\x18":
            compression = "LZ4 frame"
        elif frag[:4] == b"\x02\x21\x4c\x18":
            compression = "legacy LZ4"
        elif frag[:6] in (b"070701", b"070702"):
            compression = "cpio newc"
        else:
            compression = "unknown"
        fragments.append({"index": i, "name": name, "type": typ, "board_id": board_ids,
                          "bytes": size, "offset": offset, "sha256": sha(frag),
                          "compression_from_magic": compression, "magic_hex": frag[:12].hex()})
    fields["fragments"] = fragments
    fdts, invalid = region_fdts(sections["dtb"])
    fields["embedded_fdt_list"] = fdts
    fields["invalid_fdt_magic_candidates"] = invalid
    fields["embedded_fdt_bytes_unparsed"] = not bool(fdts)
    return fields


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", required=True, type=Path)
    ap.add_argument("--include-boot", action="store_true")
    args = ap.parse_args()
    script = Path(__file__).with_name("inspect-oneli-stock-ranges.py")
    spec = importlib.util.spec_from_file_location("zipranges", script)
    ranges = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ranges)
    names = ("dtbo.img", "vendor_boot.img") + (("boot.img",) if args.include_boot else ())
    ranges.TARGETS = names
    ranges.COMPRESSED_CAP = 110 * 1024 * 1024
    ranges.EXPANDED_CAP = 125 * 1024 * 1024
    directory, zipmeta = ranges.metadata(ranges.STOCK_URL)
    result = {"scope": "reference_FDTs_only_not_phone_active",
              "source_archive_sha256_verified_previous_full_run": "620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c",
              "zip_reader": "pinned project scripts/inspect-oneli-stock-ranges.py",
              "members": {}, "per_fdt": []}
    for name in names:
        if name not in directory:
            raise ValueError(f"expected ZIP member missing: {name}")
        data = ranges.member(ranges.STOCK_URL, name, directory[name])
        digest = sha(data)
        if digest != EXPECTED[name]:
            raise ValueError(f"{name}: member SHA mismatch {digest}, expected {EXPECTED[name]}")
        result["members"][name] = {"source": name, "zip_crc32": directory[name]["crc32"],
                                   "bytes": len(data), "sha256": digest}
        if name == "dtbo.img":
            result["per_fdt"].extend(dtbo_parts(data))
        elif name == "vendor_boot.img":
            result["vendor_boot"] = vendor_boot(data)
            result["per_fdt"].extend(result["vendor_boot"].pop("embedded_fdt_list"))
        elif name == "boot.img":
            result["boot_image"] = {"magic": data[:8].decode("ascii", "replace"),
                "header_version": struct.unpack_from("<I", data, 40)[0],
                "kernel_addr_not_encoded_in_boot_v4": True,
                "os_version_packed_u32": struct.unpack_from("<I", data, 16)[0]}
        print(f"{name}: {len(data)} bytes, SHA256 {digest}", flush=True)
    result["per_fdt"].sort(key=lambda x: (x["provenance"]["member"], x["provenance"].get("table_entry", -1),
                                          x["provenance"].get("offset_in_dtb_region", 0)))
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("FDTs", len(result["per_fdt"]), "total exported JSON bytes", args.json_out.stat().st_size, flush=True)


if __name__ == "__main__":
    main()
