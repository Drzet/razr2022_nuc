#!/usr/bin/env python3
"""Focused, read-only Motorola ABL fastboot/load trace. No firmware bytes exported.

The pinned research helper uses HTTP 206 to retrieve only the verified
bootloader.img member of the already inventoried public firmware archive.
RVA windows are selected from the existing 2026-10-15 Motorola evidence.
"""
import argparse
import hashlib
import importlib.util
import json
import struct
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
import pefile

EXPECTED_MEMBER = "bcb596054b276aa3e314412e32b274be8c33b4d93dde9550f55f9a7376496ab3"
EXPECTED_LOADER = "5e6db9577a35ec5a5e9c848e271e13048b9ba71a47311d64f0a29b78500eb3ca"
GUID = "file-9ab20751-6179-47f8-af85-796468678f92"

# ABL code RVAs, NOT device physical addresses. Extra regions are bounded
# context for source/branch selection and Motorola's real BootLinux route.
WINDOWS = {
    "FASTBOOT_BOOT_DISPATCH": (0x8ca8, 0x8e9c),
    "LOAD_AND_AUTH_DOWNLOADED_IMAGE": (0x53b00, 0x56100),
    "LOADER_INIT_PARTITION_SOURCE": (0x60000, 0x62300),
    "UPDATE_BOOT_PARAMS_VENDOR_RAMDISK": (0x64b00, 0x673d0),
    "DTB_IMAGE_AND_RAMDISK_SOURCE": (0x68c00, 0x6b100),
    "BOOTLINUX_DTBO_SOURCE": (0x86c00, 0x88fc0),
}
TARGETS = (0x53b50, 0x65708, 0x882c8, 0x6b320, 0x6b310, 0x55b00,
           0x55b28, 0x55b30, 0x55b40, 0x88294, 0x88f50,
           0x66c00, 0x673d0, 0x68c78)


# The following focused follow-up walks actual branch edges from the component
# provider and mode source. It does not mistake a static parser for an observed
# hardware execution, and it never exports PE sections or executable bytes.
COMPONENT_SEEDS = (0x4f0d8, 0x5bfe8, 0x55ad0)
MAX_TOTAL_INSTRUCTIONS = 60000
MAX_FUNCTIONS = 75
MAX_ONE_FUNCTION_INSTRUCTIONS = 11000

def _literal_target(inst):
    import re
    if inst.mnemonic in ("b", "bl") or inst.mnemonic.startswith("b.") or inst.mnemonic in ("cbz", "cbnz", "tbz", "tbnz"):
        last = inst.op_str.rsplit(",", 1)[-1].strip()
        if re.fullmatch(r"#(?:0x[0-9a-f]+|\d+)", last):
            return int(last[1:], 0)
    return None

def _discover_cfg(seed, instruction_map, hard_limit=MAX_ONE_FUNCTION_INSTRUCTIONS):
    """One function's forward reachable instructions, stopping at returns.

    Calls are recorded but not followed within the current function. A tail
    branch leaving the local 64 KiB envelope is separately exposed so a
    displaced compiler thunk cannot silently disappear.
    """
    todo = [seed]
    seen = set()
    calls, tail_external, indirect = set(), set(), set()
    while todo:
        at = todo.pop()
        if at in seen:
            continue
        if len(seen) >= hard_limit:
            raise RuntimeError(f"CFG budget exceeded for entry {seed:#x}; inspect before publication")
        i = instruction_map.get(at)
        if i is None:
            tail_external.add((at, "missing-executable-instruction"))
            continue
        if abs(at-seed) >= 0x10000:
            tail_external.add((at, "outside-64KiB-seed-envelope"))
            continue
        seen.add(at)
        name = i.mnemonic
        target = _literal_target(i)
        if name == "bl":
            if target is not None:
                calls.add(target)
            todo.append(at+4)
        elif name == "blr":
            indirect.add(at)
            todo.append(at+4)
        elif name in ("ret", "eret", "br", "drps"):
            if name == "br":
                indirect.add(at)
            continue
        elif name == "b":
            if target is None:
                indirect.add(at)
            else:
                todo.append(target)
        elif name.startswith("b.") or name in ("cbz", "cbnz", "tbz", "tbnz"):
            if target is not None:
                todo.append(target)
            todo.append(at+4)
        else:
            todo.append(at+4)
    return {"addresses": sorted(seen), "calls": sorted(calls),
            "indirect": sorted(indirect), "external": sorted(tail_external)}

def record_component_source_trace(instructions, loader, output):
    by_pc={i.address:i for i in instructions}
    for seed in COMPONENT_SEEDS:
        assert seed in by_pc, f"Missing focused entry RVA {seed:#x}"
    # Recurse into every direct callee of 0x4f0d8 and 0x5bfe8. A second
    # generation is included for acquisition-related ABL routines; exclude
    # generic low-address UEFI/stub helpers to control scope and expense.
    work=[(s,0,s) for s in COMPONENT_SEEDS]
    visited={}
    overflow=False
    while work:
        entry,depth,root=work.pop(0)
        if entry in visited:
            continue
        if len(visited)>=MAX_FUNCTIONS:
            overflow=True
            break
        if entry not in by_pc:
            visited[entry]={"missing": True, "depth":depth, "root":hex(root)}
            continue
        cfg=_discover_cfg(entry,by_pc)
        visited[entry]=dict(cfg,depth=depth,root=hex(root))
        if sum(len(q.get("addresses",())) for q in visited.values())>MAX_TOTAL_INSTRUCTIONS:
            overflow=True
            break
        if depth<1:
            follow=cfg["calls"]
        elif depth==1:
            follow=[t for t in cfg["calls"] if 0x45000<=t<0x8c000]
        else:
            follow=[]
        for target in follow:
            if target in by_pc and target not in visited:
                work.append((target,depth+1,root))
    if overflow:
        raise RuntimeError(f"COMPONENT_TRACE_BUDGET_EXCEEDED functions={len(visited)}; adjust bounded call graph explicitly, do not claim success")
    total=sum(len(q.get("addresses",())) for q in visited.values())
    if total<80:
        raise RuntimeError("Component-source trace underpopulated: no reliable instruction coverage")
    output=Path(output)
    lines=["# Motorola oneli exact component-source static AArch64 trace",
           "All addresses are PE RVAs, not RAM addresses; no firmware bytes retained",
           f"Pinned LinuxLoader SHA256 {hashlib.sha256(loader).hexdigest()}",
           f"Roots {', '.join(hex(x) for x in COMPONENT_SEEDS)}",
           f"Functions/roots walked {len(visited)}; total instruction instances {total}",
           "Conditional branches followed both ways; BL recorded separately; indirect BLR/BR marked",
           ""]
    report={}
    for entry,r in sorted(visited.items()):
        label=f"0x{entry:x}"
        if r.get("missing"):
            report[label]=r
            lines.append(f"## {label} missing target\n")
            continue
        addrs=r["addresses"]
        report[label]={
            "entry_rva":label,"seed_root":r["root"],"depth":r["depth"],
            "covered_instructions":len(addrs),
            "covered_start_rva":hex(addrs[0]),
            "covered_end_exclusive_rva":hex(addrs[-1]+4),
            "direct_callees":[hex(t) for t in r["calls"]],
            "indirect_branch_or_call_sites":[hex(t) for t in r["indirect"]],
            "external_unresolved_edges":[{"rva":hex(t),"reason":reason} for t,reason in r["external"]]
        }
        lines+= [f"## FUNCTION {label} root={r['root']} depth={r['depth']}"
                 f" covered={len(addrs)} start={hex(addrs[0])} end={hex(addrs[-1]+4)}",
                 f"CALLS {', '.join(hex(x) for x in r['calls'])}",
                 f"INDIRECT {', '.join(hex(x) for x in r['indirect'])}",
                 f"EXTERNAL {', '.join(hex(x[0])+':'+x[1] for x in r['external'])}", ""]
        lines += [f"{pc:08x}  {by_pc[pc].mnemonic:<10} {by_pc[pc].op_str}"
                  for pc in addrs]
        lines.append("")
    (output/"abl-component-source-reachable-disassembly.txt").write_text("\n".join(lines)+"\n")
    (output/"abl-component-source-callgraph.json").write_text(json.dumps({
        "firmware_pe_sha256":hashlib.sha256(loader).hexdigest(),
        "seeds":[hex(x) for x in COMPONENT_SEEDS],
        "bounded_branch_follow":True,
        "reported_function_instances":len(visited),
        "reported_instruction_instances":total,
        "functions":report,
        "source_bytes_retained":False,
        "hardware_execution":False,
        "static_semantics_not_runtime_validation":True
    },indent=2)+"\n")
    for seed in COMPONENT_SEEDS:
        item=report[f"0x{seed:x}"]
        assert item["covered_instructions"]>10, f"Incomplete seed {seed:x}"
    print(f"COMPONENT_SOURCE_TRACE_PASS functions={len(visited)} instructions={total} "
          f"roots={','.join(hex(s) for s in COMPONENT_SEEDS)}")
    for seed in COMPONENT_SEEDS:
        x=report[f"0x{seed:x}"]
        print(f"COVERAGE root={seed:#x} {x['covered_start_rva']}..{x['covered_end_exclusive_rva']} "
              f"count={x['covered_instructions']} calls={len(x['direct_callees'])} "
              f"indirect={len(x['indirect_branch_or_call_sites'])}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspector", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("evidence"))
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("pinned_motorola_member", args.inspector)
    src = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(src)
    blob, source_meta = src.member_download()
    assert source_meta["sha256"] == EXPECTED_MEMBER, "Unexpected public bootloader.img!"
    pieces, _ = src.submembers(blob)
    original_abl = next(data for name, _, data in pieces if name == "abl.elf")
    with tempfile.TemporaryDirectory(prefix="oneli-pinned-abl-") as folder:
        root = Path(folder)
        at = original_abl.find(b"_FVH") - 40
        assert at >= 0, "Expected public Motorola EFI firmware volume missing"
        fv_size = struct.unpack_from("<Q", original_abl, at + 32)[0]
        fv_file = root / "abl.fv"
        fv_file.write_bytes(original_abl[at:at + fv_size])
        dest = root / "extracted"
        dest.mkdir()
        run = subprocess.run(
            ["uefi-firmware-parser", "-b", "-e", "-o", str(dest), str(fv_file)],
            capture_output=True, text=True, timeout=140)
        assert run.returncode == 0, run.stderr[-1500:]
        found = [f for f in dest.rglob("section1.pe") if GUID in str(f)]
        assert len(found) == 1, f"Expected one pinned LinuxLoader PE: {len(found)}"
        loader = found[0].read_bytes()
    assert hashlib.sha256(loader).hexdigest() == EXPECTED_LOADER, "Unpinned ABL PE"
    pe = pefile.PE(data=loader, fast_load=True)
    assert pe.FILE_HEADER.Machine == 0xaa64
    md = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    md.detail = False
    instructions = []
    for section in pe.sections:
        if not section.Characteristics & 0x20000000:
            continue
        instructions += list(md.disasm(section.get_data(), section.VirtualAddress))
    calls = defaultdict(list)
    for inst in instructions:
        if inst.mnemonic == "bl" and inst.op_str.startswith("#"):
            try:
                calls[int(inst.op_str[1:], 16)].append(inst.address)
            except ValueError:
                pass
    args.output.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Focused Motorola ABL source-backed fastboot and vendor composition trace",
        "Source firmware component: publicly distributed oneli bootloader.img",
        "Scope: static PE disassembly; branches/callers listed, not runtime outcomes",
        "All instruction addresses below are ABL PE RVAs, NOT RAM addresses.",
        "NO proprietary executable/blob is uploaded.",
        f"bootloader.img sha256: {source_meta['sha256']}",
        f"LinuxLoader PE sha256: {hashlib.sha256(loader).hexdigest()}",
        ""
    ]
    for label, (lo, hi) in WINDOWS.items():
        selected = [i for i in instructions if lo <= i.address < hi]
        lines.extend([
            f"## {label} [0x{lo:x},0x{hi:x})",
            f"Instructions: {len(selected)}",
            "",
        ])
        lines.extend(f"{i.address:08x}  {i.mnemonic:<10} {i.op_str}" for i in selected)
        lines.append("")
    (args.output / "abl-focused-fastboot-load-disassembly.txt").write_text(
        "\n".join(lines) + "\n")
    caller_map = {}
    for target in TARGETS:
        sites = calls.get(target, [])
        caller_map[f"0x{target:x}"] = {
            "bl_call_sites": [f"0x{x:x}" for x in sites],
            "caller_count": len(sites),
            "near_target": [
                f"{i.address:08x} {i.mnemonic} {i.op_str}"
                for i in instructions if target - 40 <= i.address < target + 100
            ]
        }
    report = {
        "stock_bootloader_img_sha256": source_meta["sha256"],
        "abl_linuxloader_pe_sha256": hashlib.sha256(loader).hexdigest(),
        "analysis": "static AArch64 instruction trace; zero binary output",
        "windows": {name: {"start_rva": hex(a), "end_rva": hex(b)}
                    for name, (a, b) in WINDOWS.items()},
        "callers": caller_map,
        "imported_research_inspector": str(args.inspector),
        "no_full_archive_download": True,
        "no_proprietary_executable_export": True,
        "no_kernel_or_image_build": True,
        "no_hardware_execution": True,
    }
    (args.output / "abl-focused-fastboot-call-index.json").write_text(
        json.dumps(report, indent=2) + "\n")
    print("FOCUSED_ABL_STATIC_TRACE_PASS")
    print(f"bootloader.img={source_meta['sha256']} LinuxLoader={report['abl_linuxloader_pe_sha256']}")
    for name, (lo, hi) in WINDOWS.items():
        print(f"{name}: 0x{lo:x}..0x{hi:x}")
    record_component_source_trace(instructions, loader, args.output)
    print("No executable firmware bytes exported.")

if __name__ == "__main__":
    main()
