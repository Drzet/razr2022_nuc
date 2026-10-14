#!/usr/bin/env python3
"""Hash-pin/extract the vendor decoder unchanged, then run the bounded host test.

Generated vendor sources live only in a temporary directory, never in this repo.
See decoder-bandwidth-reference.md for preconditions and evidence limitations.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENDOR = "LowTension/android_kernel_xiaomi_sm8475"
VREF = "39382bf760ccf05a8fb4dddee7138ecac02d4a59"
KREF = "a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac"
SOURCES = {
    "calculator.c": (VENDOR, VREF, "techpack/video/driver/variant/iris2/src/msm_vidc_power_iris2.c", "a1a76266d723a855ec0f9f404ec4f5d04b88c7f6194a97945fb67782e1e4b0d0"),
    "power.h": (VENDOR, VREF, "techpack/video/driver/vidc/inc/msm_vidc_power.h", "36fa8f6a79a87af5b40f087865bcd986ad79074b52ade298073cf86b8d7f517d"),
    "fixedpoint.h": (VENDOR, VREF, "techpack/video/driver/vidc/inc/fixedpoint.h", "0f3b78b435c3f3a54ff1511bcaacbd5762af85fd24099a9456d3ce13ce39217a"),
    "internal.h": (VENDOR, VREF, "techpack/video/driver/vidc/inc/msm_vidc_internal.h", "93d21670685bb82f405592d83a3aa173a04b53f30d9dbd9da9244585718f7a98"),
    "power.c": (VENDOR, VREF, "techpack/video/driver/vidc/src/msm_vidc_power.c", "be2d9fa49d3058b6ccb1d8a355ee3d3f72b80e705f2ae51e5ee8fb2efb6e7f68"),
    "platform.h": ("Drzet/linux", KREF, "drivers/media/platform/qcom/iris/iris_platform_common.h", "988f60d3a7f7b9d0d1412c6184ff23153f1a5d162d02ab07bc9a6344a08ba757"),
    "platform.c": ("Drzet/linux", KREF, "drivers/media/platform/qcom/iris/iris_platform_vpu2.c", "584f116f71a157ef652a98b884e103de9a9268deca92911a3c5992307f72e408"),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def outside_repo(path):
    if path.resolve().is_relative_to(ROOT):
        raise ValueError("Vendor source cache must be outside the project repository")


def extract(source, pattern):
    """Return an exact contiguous source slice; fail on ambiguous matches."""
    matches = list(re.finditer(pattern, source, re.M | re.S))
    if len(matches) != 1:
        raise ValueError(f"Expected one extraction for {pattern!r}, got {len(matches)}")
    return matches[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, help="Offline cache with SOURCES filenames; outside repo")
    ap.add_argument("--cc", default="gcc")
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()
    if args.source_dir:
        outside_repo(args.source_dir)
    src, provenance, slices = {}, {}, []
    for name, (repo, ref, path, expected) in SOURCES.items():
        url = f"https://raw.githubusercontent.com/{repo}/{ref}/{path}"
        if args.source_dir:
            data = (args.source_dir / name).read_bytes()
        else:
            with urllib.request.urlopen(url, timeout=40) as response:
                data = response.read()
        if sha(data) != expected:
            raise ValueError(f"{name}: SHA256 {sha(data)} != {expected}")
        src[name] = data.decode("utf-8")
        provenance[name] = {"url": url, "sha256": sha(data), "bytes": len(data)}

    def take(name, pattern):
        m = extract(src[name], pattern)
        value = m.group(0)
        slices.append({"source": name, "first_line": src[name][:m.start()].count("\n") + 1,
                       "last_line": src[name][:m.end()].count("\n") + 1,
                       "sha256": sha(value.encode()), "unchanged": True})
        return value

    # Keep notices from each file that contributes extracted source.
    notices = [take(n, r"\A(?:/\* SPDX[^\n]*\*/|// SPDX[^\n]*)\n/\*.*?\*/")
               for n in ("calculator.c", "power.h", "internal.h", "power.c")]
    pieces = [*notices, '#include "fixedpoint.h"']
    for enum in ("msm_vidc_domain_type", "msm_vidc_codec_type",
                 "msm_vidc_colorformat_type", "msm_vidc_power_mode"):
        pieces.append(take("internal.h", rf"^enum {enum} \{{.*?^\}};"))
    pieces.append(take("internal.h", r"^struct vidc_bus_vote_data \{.*?^\};"))
    pieces.append(take("power.h", r"^static const struct \{.*?^\} BASELINE_DIMENSIONS = \{.*?^\};"))
    for name, macros in (("power.h", ("kbps", "bps", "DUMP_HEADER_MAGIC", "DUMP_FP_FMT")),
                         ("internal.h", ("Q16_INT", "Q16_FRAC")),
                         ("power.c", ("MSM_VIDC_MIN_UBWC_COMPRESSION_RATIO", "MSM_VIDC_MAX_UBWC_COMPLEXITY_FACTOR"))):
        for macro in macros:
            pieces.append(take(name, rf"^#define {macro}(?:\([^\n]*?\))?[ \t]+[^\n]+"))
    pieces.append(take("power.h", r"^struct dump \{.*?^\};"))
    for fn in ("__ubwc", "__bpp"):
        pieces.append(take("power.h", rf"^static inline [^\n]+ {fn}\([^\n]+\)\n\{{.*?^\}}"))
    pieces += ["static unsigned msm_vidc_debug = 1;\n#define VIDC_BUS 1\n"
               "void __dump(struct dump dump[], int len);",
               # d_vpr_e is needed while parsing the preceding __bpp, too.
               take("calculator.c", r"^static u64 __calculate_decoder\([^\n]+\)\n\{.*?^\}")]
    # Put the error stub before extracted __bpp, without modifying that helper.
    generated = "\n\n".join([*notices, "#define d_vpr_e(...) abort()",
                               *pieces[len(notices):]]) + "\n"

    limits = {}
    cap = extract(src["platform.c"], r"^static struct platform_inst_caps platform_inst_cap_sm8475 = \{.*?^\};").group(0)
    platform = extract(src["platform.c"], r"^const struct iris_platform_data sm8475_data = \{.*?^\};").group(0)
    for key in ("min_frame_width", "max_frame_width", "min_frame_height", "max_frame_height", "max_mbpf"):
        limits[key] = int(extract(cap, rf"\.{key} = (\d+),").group(1))
    for key in ("num_vpp_pipe", "max_core_mbpf", "max_core_mbps"):
        limits[key] = int(extract(platform, rf"\.{key} = (\d+),").group(1))
    for key in ("DEFAULT_FPS", "MAXIMUM_FPS"):
        limits[key] = int(extract(src["platform.h"], rf"^#define {key}\s+(\d+)").group(1))
    limit_header = "\n".join(f"#define C_{key.upper()} {value}ULL" for key, value in limits.items()) + "\n"
    commands = [[args.cc, "-std=c11", "-O1", "-g", "-Wall", "-Wextra", "-Werror",
                 "-fsanitize=undefined", "-fno-sanitize-recover=all", "-fno-omit-frame-pointer",
                 "-I", "$BUILD", str(Path(__file__).with_suffix(".c")), "-o", "$BUILD/reference"],
                ["$BUILD/reference"]]
    with tempfile.TemporaryDirectory(prefix="vpu-decoder-reference-") as tmp:
        build = Path(tmp)
        (build / "linux").mkdir()
        (build / "linux/types.h").write_text("#include <stdint.h>\n#include <stdbool.h>\n#include <stddef.h>\ntypedef uint32_t u32;\ntypedef uint64_t u64;\n")
        (build / "linux/bits.h").write_text("#define GENMASK(h,l) ((~0UL << (l)) & (~0UL >> (63 - (h))))\n")
        (build / "fixedpoint.h").write_text(src["fixedpoint.h"])
        (build / "reference.h").write_text(generated)
        (build / "candidate-limits.h").write_text(limit_header)
        rows = []
        for cmd in commands:
            actual = [arg.replace("$BUILD", tmp) for arg in cmd]
            run = subprocess.run(actual, capture_output=True, text=True)
            if run.returncode:
                raise RuntimeError(f"Command failed: {actual}\n{run.stdout}\n{run.stderr}")
            if run.stderr:
                raise RuntimeError(f"Unexpected diagnostics: {run.stderr}")
            if cmd == commands[-1]:
                rows = [json.loads(line) for line in run.stdout.splitlines()]
                print(run.stdout, end="")
    report = {"assignment": "fcc6f13b8fbece67eba1c9c333621f97879b394f",
              "project_parent": "3b085bb0ae3493d4ff630027b035ccbadd0fc43e",
              "evidence": "host extracted-source reference; not kernel, ICC or hardware execution",
              "model": {"use_sys_cache": False, "compression_ratio_q16": 65536,
                        "complexity_factor_q16": 262144, "rate": "max(frame_rate, operating_rate)"},
              "sources": provenance, "extractions": slices,
              "fixedpoint_header_unchanged": True, "generated_reference_sha256": sha(generated.encode()),
              "fixture_sha256": sha(Path(__file__).with_suffix(".c").read_bytes()),
              "runner_sha256": sha(Path(__file__).read_bytes()),
              "retrieval_mode": "offline-cache" if args.source_dir else "HTTPS",
              "python_version": sys.version.split()[0],
              "candidate_limits": limits, "compiler": subprocess.check_output([args.cc, "--version"], text=True).splitlines()[0],
              "commands": commands, "results": rows,
              "unsigned_checks": "explicit preflight bounds and documented interval proof; GCC UBSan does not detect unsigned wrap"}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
