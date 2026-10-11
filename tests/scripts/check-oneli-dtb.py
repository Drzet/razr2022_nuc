#!/usr/bin/env python3
"""Audit *compiled* oneli DTB: reserved ranges, consumers and GPU OPPs.

The source DT is not parsed here.  The input is the actual built FDT blob.
No dependencies beyond Python stdlib; no stock firmware or device access.
"""
import argparse
import json
import struct
from pathlib import Path

BEGIN, END_NODE, PROP, NOP, END = 1, 2, 3, 4, 9
EXPECTED_GPU = {
    900000000: 416, 862000000: 384, 815000000: 320,
    765000000: 256, 710000000: 224, 645000000: 192,
    580000000: 144, 515000000: 128, 439000000: 96,
    364000000: 80, 324000000: 64, 285000000: 56,
    220000000: 48,
}
ARGS = {
    "clocks": "#clock-cells", "assigned-clocks": "#clock-cells",
    "power-domains": "#power-domain-cells", "resets": "#reset-cells",
    "interconnects": "#interconnect-cells", "phys": "#phy-cells",
    "iommus": "#iommu-cells", "dmas": "#dma-cells",
    "mboxes": "#mbox-cells",
}
NO_ARGS = ("memory-region", "operating-points-v2", "pinctrl-0", "pinctrl-1", "pinctrl-2")


def u32(blob):
    if len(blob) % 4:
        raise ValueError("unaligned u32 property")
    return list(struct.unpack(">%dI" % (len(blob)//4), blob))


def u64(blob):
    if len(blob) != 8:
        raise ValueError("opp-hz must be 64-bit")
    return struct.unpack(">Q", blob)[0]


def strlist(blob):
    return [p.decode("utf-8") for p in blob.rstrip(b"\0").split(b"\0") if p]


class Node:
    def __init__(self, name, parent=None):
        self.name, self.parent, self.props, self.children = name, parent, {}, []
        self.path = (parent.path.rstrip("/") + "/" + name) if parent else "/"
        self.effective = True

    def status(self):
        return strlist(self.props.get("status", b"okay\0"))[0]


def parse_fdt(raw):
    if len(raw) < 40:
        raise ValueError("short FDT header")
    magic, total, structoff, stroff, reserveoff, ver, last, boot, szstr, szstruct = struct.unpack_from(">10I", raw, 0)
    if magic != 0xd00dfeed or total > len(raw) or last > ver or stroff + szstr > total or structoff + szstruct > total:
        raise ValueError("invalid FDT header")
    strings = raw[stroff:stroff+szstr]
    data = raw[structoff:structoff+szstruct]
    p, stack, nodes, root = 0, [], {}, None
    while p + 4 <= len(data):
        op = struct.unpack_from(">I", data, p)[0]
        p += 4
        if op == BEGIN:
            end = data.find(b"\0", p)
            if end < 0: raise ValueError("unterminated node name")
            name = data[p:end].decode("utf-8")
            p = (end + 4) & ~3
            node = Node(name, stack[-1] if stack else None)
            if stack: stack[-1].children.append(node)
            else: root = node
            nodes[node.path] = node
            stack.append(node)
        elif op == PROP:
            if not stack or p + 8 > len(data): raise ValueError("property outside node")
            n, off = struct.unpack_from(">II", data, p); p += 8
            if off >= len(strings) or p+n > len(data): raise ValueError("property bounds")
            lastpos = strings.find(b"\0", off)
            if lastpos < 0: raise ValueError("unterminated property name")
            key = strings[off:lastpos].decode("utf-8")
            stack[-1].props[key] = data[p:p+n]
            p = (p+n+3) & ~3
        elif op == END_NODE:
            if not stack: raise ValueError("stray end node")
            stack.pop()
        elif op == NOP:
            continue
        elif op == END:
            if stack or root is None: raise ValueError("unterminated FDT")
            break
        else:
            raise ValueError("invalid FDT token %d" % op)
    else:
        raise ValueError("missing FDT_END")
    for node in nodes.values():
        node.effective = (node.status() != "disabled" and
                          (node.parent.effective if node.parent else True))
    return nodes


def onecell(node, prop, default=None):
    raw = node.props.get(prop)
    if raw is None: return default
    nums = u32(raw)
    if len(nums) != 1: raise ValueError("%s %s: not one cell" % (node.path, prop))
    return nums[0]


def phandle_report(nodes):
    providers = {}
    for n in nodes.values():
        pid = onecell(n, "phandle", None)
        if pid is not None:
            if pid in providers: raise ValueError("duplicate phandle %d" % pid)
            providers[pid] = n
    refs, errs = [], []
    for n in nodes.values():
        for prop, blob in n.props.items():
            typ = "supply" if prop.endswith("-supply") else ("noargs" if prop in NO_ARGS or prop.startswith("pinctrl-") and prop[8:].isdigit() else ARGS.get(prop))
            if typ is None: continue
            try: cells = u32(blob)
            except ValueError as e:
                errs.append("%s %s: %s" % (n.path, prop, e)); continue
            index = 0
            while index < len(cells):
                ph = cells[index]
                # Zero is a legitimate empty/optional clock specifier in
                # some inherited Qualcomm clock arrays, not a missing phandle.
                if ph == 0:
                    index += 1
                    continue
                provider = providers.get(ph)
                if provider is None:
                    errs.append("%s %s: unresolved phandle %d at cell %d" % (n.path, prop, ph, index))
                    break
                if typ in ("supply", "noargs"):
                    width = 0
                else:
                    try: width = onecell(provider, typ, None)
                    except ValueError: width = None
                    if width is None:
                        errs.append("%s %s -> %s lacks %s" % (n.path, prop, provider.path, typ))
                        break
                if index + 1 + width > len(cells):
                    errs.append("%s %s truncated arguments" % (n.path, prop))
                    break
                refs.append({"consumer": n.path, "consumer_active": n.effective,
                             "property": prop, "provider": provider.path,
                             "provider_active": provider.effective,
                             "args": cells[index+1:index+1+width]})
                index += 1 + width
    return refs, errs


def memory_report(nodes):
    parent = nodes.get("/reserved-memory")
    if parent is None: raise ValueError("no /reserved-memory")
    ac = onecell(parent, "#address-cells")
    sc = onecell(parent, "#size-cells")
    if ac not in (1, 2) or sc not in (1, 2): raise ValueError("unsupported address/size cells")
    regions = []
    for n in parent.children:
        raw = n.props.get("reg")
        if raw is None: continue
        vals = u32(raw)
        stride = ac + sc
        if len(vals) % stride: raise ValueError("invalid reserved-memory reg " + n.path)
        for i in range(0, len(vals), stride):
            start, size = 0, 0
            for x in vals[i:i+ac]: start = (start << 32) | x
            for x in vals[i+ac:i+stride]: size = (size << 32) | x
            if size:
                regions.append({"node": n.path, "start": start, "size": size, "end": start+size,
                                "active": n.effective, "no_map": "no-map" in n.props})
    regions.sort(key=lambda x: x["start"])
    overlaps = []
    for i, a in enumerate(regions):
        for b in regions[i+1:]:
            if b["start"] >= a["end"]: break
            if a["start"] < b["end"]:
                overlaps.append({"a": a["node"], "b": b["node"],
                                 "at": max(a["start"], b["start"])})
    return regions, overlaps


def gpu_report(nodes):
    gpus = [n for n in nodes.values() if "qcom,adreno-730.2" in strlist(n.props.get("compatible", b""))]
    if len(gpus) != 1: raise ValueError("expected exactly one SM8475 A730v3 GPU")
    gpu = gpus[0]
    if gpu.effective: raise ValueError("GPU must remain disabled")
    found = {}
    tables = [child for child in gpu.children if child.name == "opp-table"]
    if len(tables) != 1: raise ValueError("GPU OPP table missing")
    for opp in tables[0].children:
        if "opp-hz" not in opp.props: continue
        hz = u64(opp.props["opp-hz"]); lv = onecell(opp, "opp-level")
        if hz in found: raise ValueError("duplicate GPU OPP %d" % hz)
        found[hz] = lv
    if found != EXPECTED_GPU:
        raise ValueError("GPU OPP map mismatch expected=%s found=%s" % (EXPECTED_GPU, found))
    return {"gpu": gpu.path, "active": gpu.effective, "opps": [{"hz": hz, "level": level}
            for hz, level in sorted(found.items(), reverse=True)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dtb", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    nodes = parse_fdt(args.dtb.read_bytes())
    regions, overlaps = memory_report(nodes)
    refs, errors = phandle_report(nodes)
    gpu = gpu_report(nodes)
    known = {r["start"]: r["size"] for r in regions}
    if known.get(0x85700000) != 0x2800000 or known.get(0x9fd00000) != 0x700000:
        errors.append("oneli ADSP/video reservation not present at expected size/address")
    if overlaps: errors.append("%d overlapping reserved-memory intervals" % len(overlaps))
    uart = next((n for n in nodes.values() if n.name == "serial@99c000"), None)
    if uart is None or not uart.effective:
        errors.append("UART7 missing or disabled behind ancestor")
    suspicious = [r for r in refs if r["consumer_active"] and not r["provider_active"]]

    # First-boot contract: all optional peripheral families below remain
    # off until their own providers/rails/driver handoffs are reviewed.
    deferred = {
        "/soc@0/codec@31e0000": "WSA2 LPASS macro",
        "/soc@0/codec@3200000": "RX LPASS macro",
        "/soc@0/codec@3220000": "TX LPASS macro",
        "/soc@0/codec@3240000": "WSA LPASS macro",
        "/soc@0/pinctrl@3440000": "LPASS LPI pinctrl",
        "/soc@0/clock-controller@af00000": "DISPCC",
        "/soc@0/usb@a600000": "DWC3 USB2",
        "/soc@0/phy@88e3000": "eUSB2 PHY",
        "/pmic-glink": "PMIC GLINK Type-C service",
    }
    for path, purpose in deferred.items():
        n = nodes.get(path)
        if n is None or n.effective:
            errors.append("minimal boot must hold %s (%s)" % (purpose, path))
    phy = nodes.get("/soc@0/phy@88e3000")
    if phy is not None and "qcom,sm8475-snps-eusb2-phy" not in strlist(phy.props.get("compatible", b"")):
        errors.append("incorrect eUSB2 PHY compatible (SM8450 inherited?)")

    classifications = []
    critical = []
    for ref in suspicious:
        path = ref["consumer"]
        if path == "/soc@0/clock-controller@100000" and ref["property"] == "clocks":
            # GCC must probe for CPU/console. Disabled parent PHY clock
            # references are not considered harmless: hardware probe gate.
            group = "BOOT_REQUIRED_GCC_WITH_DEFERRED_PHY_PARENT"
        elif path == "/soc@0/clock-controller@af00000" and ref["property"] == "clocks":
            group = "DEFERRED_DISPLAY_CLOCK_PARENT"
        elif path.startswith("/soc@0/codec@") or path == "/soc@0/pinctrl@3440000":
            group = "UNSAFE_ACTIVE_AUDIO_DEPENDENCY"
        else:
            group = "UNCLASSIFIED_ACTIVE_TO_DISABLED_DEPENDENCY"
        classifications.append({"consumer": path, "provider": ref["provider"],
                                "property": ref["property"], "classification": group})
        if (group == "UNCLASSIFIED_ACTIVE_TO_DISABLED_DEPENDENCY"
                or group == "UNSAFE_ACTIVE_AUDIO_DEPENDENCY"
                or path in ({uart.path, uart.parent.path} if uart else set())):
            critical.append(ref)
    if critical:
        errors.append("%d unsafe/unclassified or UART7 references to disabled providers" % len(critical))
    report = {"input": str(args.dtb), "node_count": len(nodes),
              "reservation_count": len(regions), "reservations": regions,
              "overlaps": overlaps, "gpu": gpu,
              "uart7": {"path": uart.path, "effective": uart.effective} if uart else None,
              "phandle_references": refs, "reference_parse_errors": errors,
              "enabled_consumer_disabled_provider": suspicious,
              "provider_dependency_classification": classifications,
              "critical_disabled_provider_references": critical,
              "pass": not errors}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print("nodes=%d reserved=%d overlaps=%d phandle_refs=%d decode_errors=%d active_to_disabled=%d GPU_OPPs=%d" %
          (len(nodes), len(regions), len(overlaps), len(refs), len(errors), len(suspicious), len(gpu["opps"])))
    for e in errors: print("ERROR:", e)
    for e in suspicious[:15]:
        print("WARN: enabled consumer references disabled provider:", e)
    if len(suspicious) > 15:
        print("WARN: %d more active-to-disabled references in JSON" % (len(suspicious)-15))
    if errors: raise SystemExit(1)


if __name__ == "__main__":
    main()
