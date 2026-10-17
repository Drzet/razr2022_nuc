# Unwired checked VPU2 calculator validation

Assignment: coordinator `bcb38efbc2ec8799fa25645b95b5f76e752f62de`.
Kernel helper: `Drzet/linux:razr/vpu-provenance-v5@7ac8d3afedfde74286b52e11aaa1eca42a1329a5`.
The checked calculator and its local arithmetic primitives live only in that
kernel repository. This project contains host fixtures, independent expectations
and evidence. The accepted reference files/results remain unchanged.

```sh
python3 tests/vpu/decoder-bandwidth-checked.py --kernel-dir /tmp/razr-vpu-checked --source-dir /tmp/vpu-decoder-sources --json-out tests/results/2026-10-15-vpu-checked.json
```

`--kernel-dir` must be a checkout of the exact helper commit above. To retrieve
the seven pinned reference files instead of reusing the external cache, omit
`--source-dir`. Its cache format/hashes are documented in
[the accepted reference instructions](decoder-bandwidth-reference.md).
Python 3 and a 64-bit GCC with UBSan are required. No kernel build or image is
performed by this command; [the separate ARM64 object record](../results/2026-10-15-vpu-checked-build.md)
documents compilation in the intended kernel context.

The runner imports the **unchanged** accepted reference runner and temporarily
retains its generated directory for this enclosing test. It executes all original
fixtures and checks their source/extraction/generated/fixture/runner hashes,
candidate limits and every result against the accepted JSON. The C bridge includes
the original fixture/oracle plus the actual kernel `.c`/headers. It calls the
overflowing original **only after its original preconditions pass**. Kernel errno,
math64 and overflow includes have small host shims: errno 22/34, unsigned u64
division and compiler overflow builtins. Actual kernel headers are exercised by
the ARM64 object build. Host shims are not kernel execution.

The deterministic grid has 1344 vectors: five codec/depth pairs; dimensions
96×96, 640×352, 1280×704, 1920×1088, 3840×2160, 96×8192; frame rates
30/60/204/205/241/480; operating rates 0/480; queued bytes 0/1000/100000/8943682.
HEVC dimensions not aligned to 32 are omitted. Eighteen named wider/failure cases
bring the total to 1362. Input/result streams have reproducible hashes; the compact
JSON retains named vectors and independent wide-integer intermediates rather than
all grid rows.

Within the accepted safe reference domain, actual unchanged production outputs
are the differential oracle (810 matches). Every successful result outside that
domain (398 vectors) is also compared against independently expressed Python
unlimited-integer component equations. These preserve each Q16 truncation and the
32767 rounding threshold, rather than using floating-point or the checked helper
as its own oracle. Those expectation equations are test code, not a second kernel
implementation. Named newly representable cases retain all expected component
values in the JSON. For this bounded grid, an independent pixel-product criterion
also checks all 1344 expected success/range-error classifications. Other wide or
unsupported inputs do not inherit that grid-specific criterion.

Twenty direct C assertions cover checked add/multiply/shift last-safe and overflow
values, Q16 multiply/divide, zero denominator, rounding, decimal output-conversion
overflow, NULL public arguments, and cleared outputs after invalid/arithmetic
failures. The full run has 3157 C assertions, including grid checks. GCC UBSan
supplies signed/shift/division checks; explicit kernel overflow builtins and shift
bounds cover unsigned arithmetic. No claim relies on sanitizer silence alone.

The helper enforces **model** constraints (dimensions, alignment, linear formats,
rates), while the accepted `prepare()` independently reports candidate admission
and the old arithmetic envelope. Thus a raw checked result may exist even when
candidate admission fails: it is not permission to queue that workload. The helper
returns `-EINVAL` for unsupported/invalid model inputs and `-ERANGE` for a u64 Q16
operation that cannot be represented; both output fields clear on failure. The
public rate is max(frame_rate, operating_rate), including startup=480, with no
fallback to 30. CR=1, CF=4, four pipes and no cache discount are fixed model choices.

The supported arithmetic domain widens but is still finite. For example 96×8192
H264 at 205 and 409 fps now returns raw D=L=23693000 and 47271000 kB/s, respectively;
410 fps returns `-ERANGE` because the unchanged Q16 division order requires a
left-shifted numerator beyond u64. No 128-bit cancellation or silent saturation is
inserted. All three pass the candidate admission check. At 30 fps the old rejected
8943682-byte estimate is now representable (3626000 kB/s); a 10000000-byte VP9/P010
estimate at 3840×2160/60 gives 13035000 kB/s. The original is not run for these cases.

This test validates arithmetic, not the empirical bandwidth coefficients, phone
operation or adequacy of a 15000000 kB/s route cap. There are 382 successful vectors
above that cap; outputs stay raw. D=L reflects the no-cache-discount model, not
physical cache disablement or universal LLCC safety. There is no runtime caller,
ICC operation, cache lifecycle, firmware, DTS or integration change. A later
consumer must separately agree admission/error handling, runtime rate/cache
policy and cap adequacy before using the raw pair.
