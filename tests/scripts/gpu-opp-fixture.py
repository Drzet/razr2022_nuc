#!/usr/bin/env python3
"""Build-only SM8475 GPU OPP fixture check, not a board DTS implementation.

Inputs are a pinned Boot kernel tree, the already-reviewed GPU DTS proposal
fenced in docs/handoffs/gpu-2026-10-11.md, and a compiled oneli DTB.
No kernel source changes are committed by this test.
"""
import argparse
from pathlib import Path
import re
import subprocess

EXPECTED_MHZ_CORNERS = {
    900: 416, 862: 384, 815: 320, 765: 256, 710: 224,
    645: 192, 580: 144, 515: 128, 439: 96, 364: 80,
    324: 64, 285: 56, 220: 48,
}
STALE_MHZ = {818, 791, 734, 640, 599, 545, 492, 421, 350, 317}


def apply_proposal(kernel: Path, handoff: Path) -> None:
    source = handoff.read_text()
    matches = re.findall(r"(?ms)^\\x60\\x60\\x60dts\\s*\\n(.*?)^\\x60\\x60\\x60\\s*$", source)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one DTS proposal block; found {len(matches)}")
    patch = matches[0]
    if patch.count("/delete-node/ opp-") != len(STALE_MHZ):
        raise ValueError("proposal does not delete ten SM8450-only OPP children")
    dts = kernel / "arch/arm64/boot/dts/qcom/sm8475.dtsi"
    if not dts.is_file():
        raise FileNotFoundError(dts)
    if "oneli-gpu-opp-fixture" in dts.read_text():
        raise ValueError("fixture already applied")
    with dts.open("a") as out:
        out.write("\n/* oneli-gpu-opp-fixture: TEST ONLY, not Boot source */\n")
        out.write(patch)
        out.write("\n")
    print("APPLIED GPU OPP TEST FIXTURE ONLY", dts)


def fdtget(dtb: Path, *args: str) -> list[str]:
    run = subprocess.run(["fdtget", *args[:1], str(dtb), *args[1:]],
                         capture_output=True, text=True, check=True)
    return run.stdout.split()


def check(dtb: Path) -> None:
    gpu = "/soc@0/gpu@3d00000"
    table = gpu + "/opp-table"
    names = fdtget(dtb, "-l", table)
    opp_names = [n for n in names if n.startswith("opp-")]
    actual = {}
    for name in opp_names:
        path = table + "/" + name
        hz_parts = fdtget(dtb, "-t", "x", path, "opp-hz")
        if len(hz_parts) != 2:
            raise AssertionError(f"{name}: 64-bit opp-hz must use two cells: {hz_parts}")
        hz = (int(hz_parts[0], 16) << 32) | int(hz_parts[1], 16)
        if hz % 1000000:
            raise AssertionError(f"{name}: unexpected noninteger MHz {hz}")
        mhz = hz // 1000000
        levels = fdtget(dtb, "-t", "x", path, "opp-level")
        if len(levels) != 1:
            raise AssertionError(f"{name}: one corner expected, found {levels}")
        if mhz in actual:
            raise AssertionError(f"duplicate frequency: {mhz}")
        actual[mhz] = int(levels[0], 16)
        if name != f"opp-{hz}":
            raise AssertionError(f"{name} does not match frequency {hz}")

    assert len(opp_names) == 13, f"expected 13 entries, found {len(opp_names)}"
    assert not (actual.keys() & STALE_MHZ), "SM8450-only GPU OPPs survived"
    assert actual == EXPECTED_MHZ_CORNERS, (
        f"frequency/corner mismatch\nactual: {actual}\nexpected: {EXPECTED_MHZ_CORNERS}")
    compat = fdtget(dtb, "-t", "s", gpu, "compatible")
    assert compat == ["qcom,adreno-730.2", "qcom,adreno"], compat
    gpucc = fdtget(dtb, "-t", "s", "/soc@0/clock-controller@3d90000", "compatible")
    assert gpucc == ["qcom,sm8475-gpucc"], gpucc
    print("PASS: compiled DTB contains exactly 13 SM8475 GPU OPPs with expected RPMh corners")
    for mhz, corner in sorted(actual.items(), reverse=True):
        print(f"{mhz:3} MHz -> RPMh level {corner}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", nargs=2, metavar=("BOOT_KERNEL_TREE", "GPU_HANDOFF_MD"))
    mode.add_argument("--check", metavar="COMPILED_ONELI_DTB")
    args = parser.parse_args()
    if args.apply:
        apply_proposal(Path(args.apply[0]), Path(args.apply[1]))
    else:
        check(Path(args.check))
