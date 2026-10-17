#!/usr/bin/env python3
"""Differential-test the unwired kernel calculator, preserving the old oracle.

The accepted runner generates the unchanged reference; kernel files are included
from --kernel-dir, never copied into this project. Widened cases use independent
Python unlimited-integer expectations; unsafe original code is never invoked.
"""
import argparse
import collections
import contextlib
import hashlib
import importlib.util
import io
import itertools
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
Q = 65536


def wide_expect(v):
    """Independent algebraic integer oracle; no u64 intermediate wrap allowed.

    Deliberately expressed as component equations, not a translation of the
    checked C helpers. Used only for specifically named widened vectors.
    """
    c, f, iw, ih, ow, oh, fr, op, size = v
    w, h, rate = max(iw, 1280), max(ih, 720), max(fr, op)
    lcu = 16 if c == 0 else 32
    n = ((w + lcu - 1) // lcu) * ((h + lcu - 1) // lcu)
    ratio = iw * ih * Q // (ow * oh)
    mbits = (size * rate * 8 + 999999) // 1000000
    y = w * h * rate * Q // 1000000
    dpb_y = y * 256 // 192 if f else y
    vsp = mbits * 6 * Q // 8 + mbits * 4 * Q // 8
    col = n * (16 if c == 0 else 64) * rate * Q // 1000000
    line = n * (128 if c == 0 else 64) * rate * Q // 1000000
    dpb_read = 6 * dpb_y
    write_factor = (3 * Q // 2) * (105 * Q // 100) // Q
    dpb_write = dpb_y * write_factor // Q
    opb = ((3 * (2 * y if f else y)) // 2) * Q // ratio
    before = vsp + 2 * col + dpb_read + dpb_write + opb + 2 * line
    after = before * (103 * Q // 100) // Q
    kbps = ((after // Q) + (after % Q >= 32767)) * 1000
    return {"sample_product": w * h * rate, "bitrate_bps": size * rate * 8,
            "ratio_q16": ratio, "luma_q16": y, "bitrate_Mbps": mbits,
            "vsp_q16": vsp, "collocated_q16": col, "line_q16": line,
            "dpb_read_q16": dpb_read, "dpb_write_q16": dpb_write,
            "opb_q16": opb, "pre_overhead_q16": before, "post_overhead_q16": after,
            "ddr_kBps": kbps, "llcc_kBps": kbps}


def vector(codec, fmt, w, h, fr, op=0, size=1000):
    return [codec, fmt, w, h, (w + 127) // 128 * 128, (h + 31) // 32 * 32, fr, op, size]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kernel-dir", type=Path, required=True)
    ap.add_argument("--source-dir", type=Path, help="Accepted runner's external offline source cache")
    ap.add_argument("--cc", default="gcc")
    ap.add_argument("--json-out", type=Path, required=True)
    args = ap.parse_args()
    kernel = args.kernel_dir.resolve()
    iris = kernel / "drivers/media/platform/qcom/iris"
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("accepted_reference", HERE / "decoder-bandwidth-reference.py")
    ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)
    sha = lambda data: hashlib.sha256(data).hexdigest()
    cases, names = [], []
    # Deterministic bounded product: five codec/depth pairs, asymmetric sizes,
    # source-alignment filtering, zero/typical/old-boundary byte estimates.
    for (c, f), (w, h), fr, op, size in itertools.product(
            [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1)],
            [(96, 96), (640, 352), (1280, 704), (1920, 1088), (3840, 2160), (96, 8192)],
            [30, 60, 204, 205, 241, 480], [0, 480], [0, 1000, 100000, 8943682]):
        if c == 1 and (w % 32 or h % 32):
            continue
        cases.append(vector(c, f, w, h, fr, op, size)); names.append("grid")
    wide = [
        ("old-pixel-first-overflow", vector(0, 0, 96, 8192, 205)),
        ("old-pixel-u64-last-fps", vector(0, 0, 96, 8192, 409)),
        ("old-bitrate-first-byte", vector(1, 1, 1920, 1088, 30, size=8943682)),
        ("old-bitrate-larger", vector(2, 1, 3840, 2160, 60, size=10000000)),
    ]
    expected = {}
    for name, v in wide:
        expected[len(cases)] = wide_expect(v)
        cases.append(v); names.append(name)
    negative = [
        ("pixel-u64-next-fps", vector(0, 0, 96, 8192, 410), -34),
        ("queued-u64-overflow", vector(0, 0, 1280, 704, 30, size=(1 << 64) - 1), -34),
        ("bitrate-round-add-overflow", vector(0, 0, 1280, 704, 30, size=((1 << 64) - 1) // 240), -34),
        ("q16-bitstream-product-overflow", vector(0, 0, 1280, 704, 30, size=1 << 50), -34),
        ("unsupported-codec", vector(3, 0, 1280, 704, 30), -22),
        ("unsupported-format", vector(0, 2, 1280, 704, 30), -22),
        ("h264-p010-out-of-model", vector(0, 1, 1280, 704, 30), -22),
        ("zero-source", vector(0, 0, 0, 704, 30), -22),
        ("zero-frame-rate", vector(0, 0, 1280, 704, 0), -22),
        ("rate-too-high", vector(0, 0, 1280, 704, 481), -22),
        ("operating-rate-too-high", vector(0, 0, 1280, 704, 30, 481), -22),
        ("unaligned-source", vector(0, 0, 97, 704, 30), -22),
        ("outside-dimensions", vector(0, 0, 8208, 704, 30), -22),
    ]
    zero_out = vector(0, 0, 1280, 704, 30); zero_out[5] = 0
    negative.append(("zero-output-denominator", zero_out, -22))
    errors = {}
    for name, v, code in negative:
        errors[len(cases)] = code; cases.append(v); names.append(name)

    with tempfile.TemporaryDirectory(prefix="vpu-checked-") as tmp:
        build = Path(tmp)
        # Reuse the unchanged runner, retaining its generated directory only for
        # this enclosing test. Restore its globals immediately after extraction.
        factory, argv = ref.tempfile.TemporaryDirectory, sys.argv
        try:
            ref.tempfile.TemporaryDirectory = lambda **kw: contextlib.nullcontext(tmp)
            sys.argv = [str(HERE / "decoder-bandwidth-reference.py"), "--cc", args.cc,
                        "--json-out", str(build / "baseline.json")]
            if args.source_dir: sys.argv += ["--source-dir", str(args.source_dir)]
            with contextlib.redirect_stdout(io.StringIO()): ref.main()
        finally:
            ref.tempfile.TemporaryDirectory = factory
            sys.argv = argv
        baseline = json.loads((build / "baseline.json").read_text())
        accepted = json.loads((ROOT / "tests/results/2026-10-14-vpu-decoder-reference.json").read_text())
        for field in ["sources", "extractions", "generated_reference_sha256", "fixture_sha256", "runner_sha256", "candidate_limits", "results"]:
            assert baseline[field] == accepted[field], field
        (build / "linux/errno.h").write_text("#define EINVAL 22\n#define ERANGE 34\n")
        (build / "linux/limits.h").write_text("#define U64_MAX UINT64_MAX\n")
        (build / "linux/math64.h").write_text("static inline uint64_t div64_u64(uint64_t a, uint64_t b) { return a / b; }\n")
        (build / "linux/overflow.h").write_text("#define check_add_overflow(a,b,p) __builtin_add_overflow(a,b,p)\n#define check_mul_overflow(a,b,p) __builtin_mul_overflow(a,b,p)\n")
        command = [args.cc, "-std=c11", "-O1", "-g", "-Wall", "-Wextra", "-Werror",
                   "-fsanitize=undefined", "-fno-sanitize-recover=all", "-fno-omit-frame-pointer",
                   "-I", str(build), "-I", str(iris), str(HERE / "decoder-bandwidth-checked.c"),
                   "-o", str(build / "checked")]
        compile_run = subprocess.run(command, text=True, capture_output=True)
        if compile_run.returncode or compile_run.stderr:
            raise RuntimeError(compile_run.stdout + compile_run.stderr)
        payload = "".join(" ".join(map(str, v)) + "\n" for v in cases)
        run = subprocess.run([str(build / "checked")], input=payload, text=True, capture_output=True)
        if run.returncode or run.stderr: raise RuntimeError(run.stdout + run.stderr)
        output = [json.loads(line) for line in run.stdout.splitlines()]
        primitive, rows, summary = output[0], output[1:-1], output[-1]
        assert len(rows) == len(cases)
        wide_checks = 0
        for i, r in enumerate(rows):
            if names[i] == 'grid':
                # In this fixed product, the sole u64 limit is the raw floored
                # pixel product's two Q16 shifts. Check it independently.
                _, _, w, h, _, _, fr, op, _ = cases[i]
                fits = max(w, 1280) * max(h, 720) * max(fr, op) <= ((1 << 64) - 1) >> 32
                assert r['ret'] == (0 if fits else -34), (cases[i], r)
            if r['ret'] == 0 and r['reference_status'] != 'ok':
                ex = wide_expect(cases[i])
                assert (r['ddr_kBps'], r['llcc_kBps']) == (ex['ddr_kBps'], ex['llcc_kBps']), (cases[i], r, ex)
                wide_checks += 1
            if i in expected:
                assert r['ret'] == 0 and r['ddr_kBps'] == expected[i]['ddr_kBps'] and r['llcc_kBps'] == expected[i]['llcc_kBps'], (names[i], r, expected[i])
                assert r['reference_status'] != 'ok'  # Never invoke overflowing original.
            if i in errors: assert r['ret'] == errors[i] and r['ddr_kBps'] == r['llcc_kBps'] == 0, (names[i], r)
            if r['ret'] == 0: assert r['ddr_kBps'] == r['llcc_kBps']
        records = [dict(name=names[i], input=cases[i], result=r,
                        **({'independent_wide_expectation': expected[i]} if i in expected else {}))
                   for i, r in enumerate(rows)]
        report = {'assignment': 'bcb38efbc2ec8799fa25645b95b5f76e752f62de',
                  'kernel_parent': ref.KREF,
                  'kernel_revision': subprocess.check_output(['git', '-C', str(kernel), 'rev-parse', 'HEAD'], text=True).strip(),
                  'kernel_dirty': bool(subprocess.check_output(['git', '-C', str(kernel), 'status', '--porcelain'], text=True)),
                  'kernel_files': {n: sha((iris / n).read_bytes()) for n in ['iris_vpu2_bw.c', 'iris_vpu2_bw.h', 'iris_vpu2_bw_math.h']},
                  'test_files': {n: sha((HERE / n).read_bytes()) for n in ['decoder-bandwidth-checked.py', 'decoder-bandwidth-checked.c']},
                  'baseline_reference_matches_accepted': True, 'reference_source_hashes': baseline['sources'],
                  'compiler': baseline['compiler'], 'compile_command': [x.replace(tmp, '$BUILD') for x in command],
                  'primitive_checks': primitive, 'summary': summary, 'vectors': len(cases),
                  'independent_wide_checks': wide_checks,
                  'grid_representability_checks': names.count('grid'),
                  'status_counts': dict(collections.Counter(str(r['ret']) for r in rows)),
                  'reference_status_counts': dict(collections.Counter(r['reference_status'] for r in rows)),
                  'result_stream_sha256': sha(run.stdout.encode()), 'vector_stream_sha256': sha(payload.encode()),
                  'named_results': [r for r in records if r['name'] != 'grid'],
                  'above_route_cap': sum(r['ret'] == 0 and r['ddr_kBps'] > 15000000 for r in rows),
                  'limits': 'Host shims + actual pure helper; kernel object build recorded separately. No runtime caller/ICC/hardware calibration.'}
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['vectors','summary','primitive_checks','independent_wide_checks','grid_representability_checks','status_counts','reference_status_counts','above_route_cap']}, indent=2))


if __name__ == '__main__': main()
