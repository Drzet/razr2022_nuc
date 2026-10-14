/* SPDX-License-Identifier: GPL-2.0-only */
/* Host fixtures and preconditions only; the decoder is extracted at run time. */
#include <assert.h>
#include <inttypes.h>
#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BIT(n) (1UL << (n))
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define max(a, b) ((a) > (b) ? (a) : (b))
/* The operand types and addition order deliberately match the kernel macro. */
#define DIV_ROUND_UP(n, d) (((n) + (d) - 1) / (d))
static uint64_t div_u64(uint64_t a, uint32_t b) { return a / b; }
#include "candidate-limits.h"
#include "reference.h"

_Static_assert(sizeof(size_t) == 8 && sizeof(unsigned long) == 8, "ARM64 word semantics required");
_Static_assert(sizeof(int) == 4 && INT_MAX == 2147483647, "32-bit source int required");
_Static_assert(FP_FRACTIONAL_BITS == 16, "source fixed-point fraction");

static unsigned checks, calls;
#define CHECK(expr) do { checks++; if (!(expr)) { \
    fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #expr); exit(1); } } while (0)

/* Debug observer: copy values from the unchanged production dump array. */
static struct { size_t width, height, opb, bitrate; } observed;
void __dump(struct dump dump[], int len)
{
    for (int i = 0; i < len; i++) {
        if (!strcmp(dump[i].key, "frame width")) observed.width = dump[i].val;
        if (!strcmp(dump[i].key, "frame height")) observed.height = dump[i].val;
        if (!strcmp(dump[i].key, "opb write")) observed.opb = dump[i].val;
        if (!strcmp(dump[i].key, "bitrate (Mbit/sec)")) observed.bitrate = dump[i].val;
    }
}

enum status { OK, FORMAT, DIMENSION, RATE, ADMISSION_MBPF, ADMISSION_MBPS,
              ARITH_BITRATE, ARITH_PIXELS, ARITH_COLLOCATED, ARITH_LINE, ARITH_FIXED };
static const char *const status_name[] = {
    "ok", "unsupported-format", "dimension-envelope", "rate-envelope",
    "candidate-mbpf", "candidate-mbps", "bitrate-arithmetic", "pixel-arithmetic",
    "collocated-arithmetic", "line-arithmetic", "fixedpoint-certificate"
};
struct input {
    uint64_t width, height, out_width, out_height;
    uint64_t frame_rate, operating_rate, queued_bytes;
    enum msm_vidc_codec_type codec;
    enum msm_vidc_colorformat_type capture;
};
struct pair { uint64_t d, l; };

static bool mul_within(uint64_t a, uint64_t b, uint64_t ceiling, uint64_t *out)
{
    if (b && a > ceiling / b) return false;
    *out = a * b;
    return true;
}
static uint64_t align_to(uint64_t v, uint64_t a) { return (v + a - 1) / a * a; }

/* No bandwidth formula is implemented here. This validates a bounded domain
 * for the original expression types; the interval certificate is in the README.
 * Admission is for ONE session against the candidate's stated source limits.
 */
static enum status prepare(const struct input *in, bool synthetic_cache,
                           struct vidc_bus_vote_data *vote)
{
    uint64_t mbpf, mbps, area, out_area, rate, bitrate, w, h, n, product;
    uint64_t lcu = in->codec == MSM_VIDC_H264 ? 16 : 32;
    uint64_t src_align = in->codec == MSM_VIDC_HEVC ? 32 : 16;
    if ((in->codec != MSM_VIDC_H264 && in->codec != MSM_VIDC_HEVC && in->codec != MSM_VIDC_VP9) ||
        (in->capture != MSM_VIDC_FMT_NV12 && in->capture != MSM_VIDC_FMT_P010) ||
        (in->codec == MSM_VIDC_H264 && in->capture != MSM_VIDC_FMT_NV12))
        return FORMAT; /* H264 10-bit deliberately outside this reference scope. */
    if (in->width < C_MIN_FRAME_WIDTH || in->width > C_MAX_FRAME_WIDTH ||
        in->height < C_MIN_FRAME_HEIGHT || in->height > C_MAX_FRAME_HEIGHT ||
        in->width % src_align || in->height % src_align ||
        in->out_width != align_to(in->width, 128) || in->out_height != align_to(in->height, 32))
        return DIMENSION;
    if (in->frame_rate < C_DEFAULT_FPS || in->frame_rate > C_MAXIMUM_FPS ||
        in->operating_rate > C_MAXIMUM_FPS)
        return RATE;
    rate = max(in->frame_rate, in->operating_rate);
    mbpf = ((in->width + 15) / 16) * ((in->height + 15) / 16);
    if (mbpf > C_MAX_MBPF || mbpf > C_MAX_CORE_MBPF) return ADMISSION_MBPF;
    if (!mul_within(mbpf, rate, C_MAX_CORE_MBPS, &mbps)) return ADMISSION_MBPS;

    /* Source d->bitrate is int; DIV_ROUND_UP evaluates n + 1000000 - 1.
     * Check the full bytes*rate*8 in u64 BEFORE assigning/narrowing.
     */
    if (!mul_within(in->queued_bytes, rate, INT_MAX - 1000000ULL, &bitrate) ||
        !mul_within(bitrate, 8, INT_MAX - 1000000ULL, &bitrate)) return ARITH_BITRATE;
    if (!mul_within(in->width, in->height, INT_MAX, &area) ||
        !mul_within(in->out_width, in->out_height, INT_MAX, &out_area)) return DIMENSION;
    w = max(in->width, 1280ULL);
    h = max(in->height, 720ULL);
    if (!mul_within(w, h, INT_MAX, &product) ||
        !mul_within(product, rate, INT_MAX, &product)) return ARITH_PIXELS;
    /* Mirror only integer expression bounds, not the output calculation. */
    n = ((w + lcu - 1) / lcu) * ((h + lcu - 1) / lcu);
    if (!mul_within(n, lcu == 16 ? 16 : 64, INT_MAX, &product) ||
        !mul_within(product, rate, INT_MAX, &product)) return ARITH_COLLOCATED;
    if (!mul_within(n, lcu == 16 ? 128 : 64, INT_MAX, &product) ||
        !mul_within(product, rate, INT_MAX, &product)) return ARITH_LINE;

    /* Preconditions of the unsigned interval certificate, checked explicitly.
     * Positive DPB/OPB ratio is [0.5,1]; original area shifts fit u64.
     * Every non-area fp_mult has operands <=2^33 and <=256*2^16.
     * Raw signed-product FP_INT numerators are <2^47 (shifted: <2^63).
     * Other non-area fp_div numerators are <2^36; total adds stay <2^33.
     */
    if (!area || !out_area || out_area < area || out_area > 2 * area ||
        area > (1ULL << 26) || out_area > (1ULL << 26) ||
        !mul_within(area, 1ULL << 32, UINT64_MAX, &product) ||
        !mul_within(INT_MAX, 1ULL << 32, UINT64_MAX, &product) ||
        !mul_within(1ULL << 33, 256ULL << 16, UINT64_MAX, &product) ||
        !mul_within(1ULL << 36, 1ULL << 16, UINT64_MAX, &product) ||
        !mul_within(131073, 1000, UINT32_MAX, &product)) return ARITH_FIXED;
    memset(vote, 0, sizeof(*vote));
    vote->domain = MSM_VIDC_DECODER;
    vote->codec = in->codec;
    vote->input_width = (int)in->width;
    vote->input_height = (int)in->height;
    vote->output_width = (int)in->out_width;
    vote->output_height = (int)in->out_height;
    vote->fps = (u32)rate;
    vote->bitrate = (int)bitrate;
    vote->lcu_size = (u32)lcu;
    vote->num_formats = 2;
    vote->color_formats[0] = in->capture == MSM_VIDC_FMT_P010 ? MSM_VIDC_FMT_TP10C : MSM_VIDC_FMT_NV12;
    vote->color_formats[1] = in->capture;
    vote->compression_ratio = MSM_VIDC_MIN_UBWC_COMPRESSION_RATIO;
    vote->complexity_factor = MSM_VIDC_MAX_UBWC_COMPLEXITY_FACTOR;
    vote->num_vpp_pipes = C_NUM_VPP_PIPE;
    vote->use_sys_cache = synthetic_cache;
    return OK;
}

static struct input fixture(uint64_t w, uint64_t h, uint64_t fps, uint64_t bytes,
                            enum msm_vidc_codec_type codec, enum msm_vidc_colorformat_type fmt)
{
    return (struct input){w, h, align_to(w, 128), align_to(h, 32), fps, 0, bytes, codec, fmt};
}

static struct pair execute(const char *name, struct input in, bool cache)
{
    struct vidc_bus_vote_data vote;
    CHECK(prepare(&in, cache, &vote) == OK);
    CHECK(vote.fps == max(in.frame_rate, in.operating_rate));
    CHECK(vote.num_formats == 2 && vote.num_vpp_pipes == 4);
    CHECK(vote.compression_ratio == 65536 && vote.complexity_factor == 262144);
    memset(&observed, 0, sizeof(observed));
    calls++;
    CHECK(__calculate_decoder(&vote) == 0);
    CHECK(observed.opb > 0); /* Split linear output writes are actually counted. */
    CHECK(observed.width == max(in.width, 1280ULL) && observed.height == max(in.height, 720ULL));
    CHECK(vote.calc_bw_ddr % 1000 == 0 && vote.calc_bw_llcc % 1000 == 0);
    CHECK(vote.calc_bw_ddr < 131073000 && vote.calc_bw_llcc < 131073000);
    CHECK(cache ? vote.calc_bw_llcc > vote.calc_bw_ddr : vote.calc_bw_ddr == vote.calc_bw_llcc);
    printf("{\"case\":\"%s\",\"kind\":\"%s\",\"fps\":%u,\"ddr_kBps\":%" PRIu64
           ",\"llcc_kBps\":%" PRIu64 ",\"bitrate_Mbps\":%zu,"
           "\"width\":%" PRIu64 ",\"height\":%" PRIu64 ",\"queued_bytes\":%" PRIu64 "}\n",
           name, cache ? "synthetic-cache-on" : "selected-model", vote.fps,
           vote.calc_bw_ddr, vote.calc_bw_llcc, observed.bitrate, in.width, in.height, in.queued_bytes);
    return (struct pair){vote.calc_bw_ddr, vote.calc_bw_llcc};
}

static void reject(const char *name, struct input in, enum status expected)
{
    struct vidc_bus_vote_data vote;
    unsigned before = calls;
    enum status result = prepare(&in, false, &vote);
    CHECK(result == expected);
    CHECK(calls == before); /* Rejected inputs never execute the original body. */
    printf("{\"case\":\"%s\",\"kind\":\"rejected-before-calculation\",\"reason\":\"%s\"}\n", name, status_name[result]);
}

/* HOST CONTRACT FIXTURE ONLY. No production ICC consumer or lifecycle is run. */
struct host_vote { struct pair average; uint64_t peak, cnoc; };
static bool contract(const struct pair *sessions, size_t n, bool unvote, bool turbo,
                     struct host_vote *vote)
{
    *vote = (struct host_vote){0};
    if (unvote) return true;
    struct pair sum = {0};
    for (size_t i = 0; i < n; i++) {
        if (sessions[i].d > UINT64_MAX - sum.d || sessions[i].l > UINT64_MAX - sum.l) return false;
        sum.d += sessions[i].d;
        sum.l += sessions[i].l;
    }
    if (turbo) sum = (struct pair){INT_MAX, INT_MAX};
    vote->average.d = sum.d < 1000 ? 1000 : sum.d > 15000000 ? 15000000 : sum.d;
    vote->average.l = sum.l < 1000 ? 1000 : sum.l > 15000000 ? 15000000 : sum.l;
    vote->cnoc = 1000;
    return true; /* Peak stays zero. No actual provider accepts these values. */
}

int main(void)
{
    CHECK(C_NUM_VPP_PIPE == 4 && C_MAXIMUM_FPS == 480 && C_DEFAULT_FPS == 30);
    struct input x = fixture(1920, 1088, 30, 100000, MSM_VIDC_H264, MSM_VIDC_FMT_NV12);
    struct pair h264 = execute("h264-nv12-1080p30", x, false);
    struct pair cached = execute("h264-cache-paired", x, true);
    CHECK(cached.d < h264.d);
    x.codec = MSM_VIDC_HEVC;
    execute("hevc-nv12-1080p30", x, false);
    x.capture = MSM_VIDC_FMT_P010;
    struct pair hevc10 = execute("hevc-p010-1080p30", x, false);
    cached = execute("hevc-cache-paired", x, true);
    CHECK(cached.d < hevc10.d);
    x.codec = MSM_VIDC_VP9;
    execute("vp9-p010-1080p30", x, false);
    x.capture = MSM_VIDC_FMT_NV12;
    struct pair vp9 = execute("vp9-nv12-1080p30", x, false);
    cached = execute("vp9-cache-paired", x, true);
    CHECK(cached.d < vp9.d);
    execute("vp9-p010-4k60", fixture(3840, 2160, 60, 200000, MSM_VIDC_VP9, MSM_VIDC_FMT_P010), false);
    struct pair low = execute("floor-640x352", fixture(640, 352, 30, 1000, MSM_VIDC_H264, MSM_VIDC_FMT_NV12), false);
    struct pair high = execute("floor-1280x704", fixture(1280, 704, 30, 1000, MSM_VIDC_H264, MSM_VIDC_FMT_NV12), false);
    CHECK(low.d == high.d); /* Same ratio=1; both effective dimensions 1280x720. */
    execute("minimum-96x96", fixture(96, 96, 30, 0, MSM_VIDC_HEVC, MSM_VIDC_FMT_NV12), false);
    execute("startup-480-retained", fixture(1920, 1088, 480, 65536, MSM_VIDC_H264, MSM_VIDC_FMT_NV12), false);
    x = fixture(1920, 1088, 30, 65536, MSM_VIDC_HEVC, MSM_VIDC_FMT_P010);
    x.operating_rate = 60;
    execute("operating-rate-wins", x, false);
    x.frame_rate = 120;
    execute("frame-rate-wins", x, false);
    execute("candidate-mbps-last-whole-fps", fixture(3840, 2160, 241, 1000, MSM_VIDC_VP9, MSM_VIDC_FMT_NV12), false);
    reject("candidate-mbps-next-fps", fixture(3840, 2160, 242, 1000, MSM_VIDC_VP9, MSM_VIDC_FMT_NV12), ADMISSION_MBPS);
    execute("signed-pixel-last-fps", fixture(96, 8192, 204, 1000, MSM_VIDC_H264, MSM_VIDC_FMT_NV12), false);
    reject("signed-pixel-next-fps", fixture(96, 8192, 205, 1000, MSM_VIDC_H264, MSM_VIDC_FMT_NV12), ARITH_PIXELS);
    x = fixture(1920, 1088, 30, (INT_MAX - 1000000ULL) / (30 * 8), MSM_VIDC_HEVC, MSM_VIDC_FMT_P010);
    execute("bitrate-last-queued-byte", x, false);
    x.queued_bytes++;
    reject("bitrate-next-byte", x, ARITH_BITRATE);
    x.queued_bytes = UINT64_MAX;
    reject("queued-u64-overflow", x, ARITH_BITRATE);
    x = fixture(1280, 704, 30, 4166, MSM_VIDC_H264, MSM_VIDC_FMT_NV12);
    struct pair ceil_low = execute("bitrate-ceil-below-1Mbit", x, false);
    CHECK(observed.bitrate == 1);
    x.queued_bytes++;
    struct pair ceil_high = execute("bitrate-ceil-above-1Mbit", x, false);
    CHECK(observed.bitrate == 2 && ceil_high.d > ceil_low.d);
    x.queued_bytes = 0;
    execute("zero-queued-bytes-is-not-unvote", x, false);
    x.capture = MSM_VIDC_FMT_NV12C; reject("compressed-output-out-of-scope", x, FORMAT);
    x.capture = MSM_VIDC_FMT_P010; reject("h264-10bit-out-of-scope", x, FORMAT);
    x.capture = MSM_VIDC_FMT_NV12; x.codec = MSM_VIDC_HEIC; reject("heic-out-of-scope", x, FORMAT);
    x.codec = MSM_VIDC_H264; x.out_width = 0; reject("zero-output", x, DIMENSION);
    x = fixture(96, 96, 30, 0, MSM_VIDC_H264, MSM_VIDC_FMT_NV12);
    x.width = 0; reject("zero-input", x, DIMENSION);
    x.width = 95; reject("below-candidate-dimensions", x, DIMENSION);
    x.width = 97; reject("unaligned-source", x, DIMENSION);
    x = fixture(8192, 8192, 30, 0, MSM_VIDC_H264, MSM_VIDC_FMT_NV12); reject("candidate-mbpf", x, ADMISSION_MBPF);
    x.width = 8208; reject("above-candidate-dimensions", x, DIMENSION);
    x = fixture(1280, 704, 0, 0, MSM_VIDC_H264, MSM_VIDC_FMT_NV12); reject("zero-frame-rate", x, RATE);
    x.frame_rate = 29; reject("below-reference-rate", x, RATE);
    x.frame_rate = 481; reject("above-reference-rate", x, RATE);
    x.frame_rate = 30; x.operating_rate = 481; reject("above-operating-rate", x, RATE);

    /* Source helper edges, with bounded explicit inputs (no model defaults changed). */
    CHECK(fp_round(FP_INT(1) + 32766) == 1);
    CHECK(fp_round(FP_INT(1) + 32767) == 2);
    CHECK(fp_round(FP_INT(1) + 32768) == 2);
    CHECK(kbps(fp_round(FP_INT(1))) == 1000);
    CHECK(fp_mult(FP_ONE + 1, FP_ONE + 1) == FP_ONE + 2);
    CHECK(fp_div(FP_INT(1), FP_INT(3)) == 21845);
    CHECK(Q16_FRAC(65536 + 65535) == 99 && Q16_INT(65536 + 65535) == 1);
    CHECK(Q16_FRAC(65536 + 655) == 0 && Q16_FRAC(65536 + 656) == 1);
    puts("{\"case\":\"source-helper-edges\",\"kind\":\"rounding-Q16-units\",\"result\":\"PASS\"}");

    struct host_vote v;
    struct pair sessions[] = {{800, 1200}, {800, 1200}};
    CHECK(contract(sessions, 2, false, false, &v));
    CHECK(v.average.d == 1600 && v.average.l == 2400 && v.peak == 0 && v.cnoc == 1000);
    sessions[0] = (struct pair){15000001, 42};
    CHECK(contract(sessions, 1, false, false, &v));
    CHECK(v.average.d == 15000000 && v.average.l == 1000);
    CHECK(contract(NULL, 0, false, true, &v));
    CHECK(v.average.d == 15000000 && v.average.l == 15000000);
    CHECK(contract(NULL, 0, false, false, &v));
    CHECK(v.average.d == 1000 && v.average.l == 1000 && v.cnoc == 1000);
    CHECK(contract(NULL, 0, true, false, &v));
    CHECK(v.average.d == 0 && v.average.l == 0 && v.peak == 0 && v.cnoc == 0);
    sessions[0] = (struct pair){UINT64_MAX, 0}; sessions[1] = (struct pair){1, 0};
    CHECK(!contract(sessions, 2, false, false, &v));
    sessions[0] = (struct pair){0, UINT64_MAX}; sessions[1] = (struct pair){0, 1};
    CHECK(!contract(sessions, 2, false, false, &v));
    puts("{\"case\":\"independent-vote-contract\",\"kind\":\"host-contract-only\",\"result\":\"PASS\"}");
    printf("{\"summary\":\"PASS\",\"checks\":%u,\"production_decoder_calls\":%u}\n", checks, calls);
    return 0;
}
