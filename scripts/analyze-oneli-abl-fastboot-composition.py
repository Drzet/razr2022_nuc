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
    print("No executable firmware bytes exported.")

if __name__ == "__main__":
    main()
