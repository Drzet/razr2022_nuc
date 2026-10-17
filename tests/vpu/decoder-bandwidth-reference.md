# Extracted Iris2 decoder host reference

Assignment: coordinator `fcc6f13b8fbece67eba1c9c333621f97879b394f`.
This is an offline reference, not an Iris kernel port, an ICC consumer test,
bandwidth calibration, or evidence of phone operation. The selected policy sets
`use_sys_cache=false`, CR=1 and CF=4. It neither disables physical cache nor proves
that D=L safely covers production LLCC traffic. Three cache-on pairs are synthetic
source-branch characterizations only.

Run from the project root with Python 3 and a 64-bit C compiler supporting UBSan:

```sh
python3 tests/vpu/decoder-bandwidth-reference.py --cc gcc --json-out tests/results/2026-10-14-vpu-decoder-reference.json
```

The runner downloads seven hash-pinned files over HTTPS, including the unchanged
Qualcomm decoder and helpers and the candidate platform limits. Every URL, SHA256,
byte count, extraction line span/hash, generated reference hash, fixture hash,
compiler version, compile flags and result is included in the JSON. Generated
sources/binary are temporary and removed on exit. No downloaded vendor source is
stored in this repository. Offline reruns use `--source-dir /tmp/vpu-decoder-sources`
with filenames `calculator.c`, `power.h`, `fixedpoint.h`, `internal.h`, `power.c`,
`platform.h`, `platform.c`; those files must match the runner's pinned hashes.
The cache must reside outside the repository. No downloads/build are required for
the read-only kernel candidate.

The generated header retains original SPDX/copyright notices, contiguous unchanged
decoder/helper slices, real enums/struct, constants and macros. `fixedpoint.h` is
included whole and unchanged. Extraction excludes unrelated functions/includes and
the encoder/LUT. There are **no calculation-body edits**, including to its debug
block. Host shims supply u32/u64, BIT/GENMASK, max, DIV_ROUND_UP, div_u64 and array
size. GENMASK is used for source bits [15:0]; the original integer operand types
and `n + d - 1` order are retained. A debug observer reads the existing dump array
to assert dimension floors, bitrate ceiling and nonzero split OPB writes; it does
not compute bandwidth. Unsupported `__bpp` errors abort. Static assertions require
64-bit size_t/unsigned long, 32-bit int and 16 fractional bits.

## Admission and reference envelope

Candidate admission is evaluated for **one session**, from the pinned source
limits: each dimension 96..8192, max_mbpf=138240, max_core_mbpf=276480,
max_core_mbps=7833600. This does not exercise kernel admission or concurrent
sessions. The reference is narrower: H264/NV12, HEVC/NV12 or P010, VP9/NV12 or P010;
source dimensions must be aligned to 32 for HEVC and 16 otherwise; capture width
and height are the source aligned to 128 and 32. Compressed capture, downscaling,
H264/P010, HEIC, encoder, unknown formats, and frame rates outside 30..480 are
explicitly outside this reference, not claims of unsupported silicon. Operating
rate may be 0..480. The adapter uses max(frame_rate, operating_rate), including
480 startup, and the same rate in queued_bytes × rate × 8 bitrate estimation.

After admission and before invoking the unchanged function, the adapter checks:

- Source/output area products and all effective floored width × height × fps,
  LCU count × collocated bytes × fps and line-neighbor bytes × LCU count × fps
  products fit signed int. LCU size is 16 for H264, 32 for HEVC/VP9; core pipes=4.
- Queued bytes × rate × 8 is at most `INT_MAX-1000000` before narrowing. This
  preserves the left-associative signed `bitrate + 1000000 - 1` rounding addition.
  Multiplication uses checked division bounds first, including UINT64_MAX inputs.
- Positive aligned output area is between input area and twice input area, with
  both at most 2^26. The original fixed-point DPB/OPB ratio is therefore at least
  0.5 (32768 encoded), and CR and all other divisors are nonzero.

## Unsigned interval certificate

GCC UBSan detects signed overflow/invalid shifts/division, **not unsigned wrap**.
The explicit preconditions above and these conservative integer bounds cover the
unchanged unsigned expressions; they are part of the harness contract, rather
than a claim based only on sanitizer silence. This certificate applies to the
selected constants/formats and the bounded synthetic cache-on pairs, not arbitrary
CR/CF values or a general production port.

| Expression group | Bound before executing production code |
| --- | --- |
| FP_INT of raw integer products, then fp_div's left shift | Product ≤INT_MAX; encoded value <2^47; second shift gives <2^63. The adapter explicitly checks INT_MAX × 2^32 against UINT64_MAX. |
| Original area-ratio fp_div | Area ≤2^26; numerator encoded ≤2^42 and shifted ≤2^58; denominator positive. |
| Luma/10-bit/P010 intermediates | Integer-product cap gives luma <2148 MB/s, 10-bit <2864, P010 <4296. The 256/192 step's temporary numerator is <549888 MB/s encoded (<2^36). |
| DPB and split OPB | With CF=4, CR=1, read <17184 MB/s, write <4511, OPB <12888 because ratio ≥0.5; cached read cannot exceed uncached read. |
| Bitstream/collocated/line terms | Bitstream sum <2685 MB/s; each collocated/line term <2148 by its checked signed product. |
| Totals/additions/subtractions | Pre-overhead DDR <45860 MB/s; after 1.03 <47236; LLCC with cache terms <68716, hence all totals <131072 MB/s encoded (<2^33). Cache subtraction is original read minus a smaller/equal read (factor ≥1); no unsigned underflow. |
| fp_mult | At each multiplication, one operand is <2^33 and the other ≤256×2^16, so product <2^57. The source constants' fractional shifts also fit int. |
| Other fp_div shifts | Non-area, post-conversion numerators <2^36; shifted <2^52. Raw-product numerators are covered separately by the <2^63 bound above. |
| Final round/decimal conversion | After rounding, ≤131072 MB/s; checked conservative limit 131073×1000 fits u32 and u64. No final saturation is used to mask earlier overflow. |

The fps≥960 branch is never executed under this 480-limited envelope. The reference
checks the source's unusual `fp_round` threshold (32767/65536), Q16 hundredths
truncation, fixed-point multiply/divide truncation, and decimal kB/s conversion
using explicit bounded helper inputs. It does not substitute exact real arithmetic.

## Test interpretation

Assertions exercise codec/depth cases, dimension floor (two different inputs with
equal source floor and DPB/OPB ratio), real split OPB contribution, rates/startup,
bitrate ceiling, D=L, synthetic cache-on D<L and lower DDR, and the last safe/first
rejected pixel/bitrate boundaries. For example 96×8192 at 204 fps is accepted;
205 fps passes candidate admission but fails the floored signed pixel product.
3840×2160 at 241 fps passes one-session admission; 242 fails its macroblocks/s limit.
Source-policy bandwidth can exceed the 15,000,000 kB/s route cap; these are raw
calculator outputs, not proof that clamped production voting would be adequate.

The small C `contract()` fixture checks independent D/L sum-before-clamp, maxima,
turbo sentinel, average minimum, peak zero, explicit zero/unvote, and u64 sum
overflow. Its requests are synthetic host vectors. It does not call ICC, inspect
a route, implement kernel lifecycle, test partial failure cleanup, or demonstrate
hardware votes. There is no separate rewritten decoder formula or independent
numeric calibration oracle: recorded values are outputs of the pinned source;
relational/component/boundary assertions establish the stated host properties.

A later checked port is needed for admitted inputs outside this reference domain,
as well as any agreed production rate/cache policy. Such a port must widen/check
intermediate arithmetic explicitly and be validated separately; this harness
deliberately rejects those inputs and leaves the kernel unchanged.
