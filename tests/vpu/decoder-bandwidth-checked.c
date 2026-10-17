/* SPDX-License-Identifier: GPL-2.0-only */
/* Bridge only: include the accepted fixture/oracle and actual kernel helper. */
#define main accepted_reference_main
#include "decoder-bandwidth-reference.c"
#undef main
#include "iris_vpu2_bw.c"

static void primitive_checks(void)
{
    u64 v = 123;
    CHECK(iris_bw_add(UINT64_MAX, 1, &v) == -ERANGE && v == 0);
    CHECK(iris_bw_add(UINT64_MAX - 1, 1, &v) == 0 && v == UINT64_MAX);
    CHECK(iris_bw_mul(UINT64_MAX, 2, &v) == -ERANGE && v == 0);
    CHECK(iris_bw_mul(UINT64_MAX, 1, &v) == 0 && v == UINT64_MAX);
    CHECK(iris_bw_q16(UINT64_MAX >> 16, &v) == 0 && v == (UINT64_MAX & ~65535ULL));
    CHECK(iris_bw_q16((UINT64_MAX >> 16) + 1, &v) == -ERANGE && v == 0);
    CHECK(iris_bw_qmul(UINT64_MAX, 2, &v) == -ERANGE && v == 0);
    CHECK(iris_bw_qdiv(1, 0, &v) == -EINVAL && v == 0);
    CHECK(iris_bw_qdiv((UINT64_MAX >> 16) + 1, 65536, &v) == -ERANGE && v == 0);
    CHECK(iris_bw_qdiv(65536, 65536, &v) == 0 && v == 65536);
    CHECK(iris_bw_round(65536 + 32766, &v) == 0 && v == 1);
    CHECK(iris_bw_round(65536 + 32767, &v) == 0 && v == 2);
    CHECK(iris_bw_round(65536 + 32768, &v) == 0 && v == 2);
    CHECK(iris_bw_kbps(UINT64_MAX / 1000 + 1, &v) == -ERANGE && v == 0);
    CHECK(iris_bw_kbps(UINT64_MAX / 1000, &v) == 0 && v == UINT64_MAX / 1000 * 1000);
    struct iris_vpu2_bw_output out = {123, 456};
    CHECK(iris_vpu2_calc_bw(NULL, &out) == -EINVAL && out.ddr_kbps == 0 && out.llcc_kbps == 0);
    CHECK(iris_vpu2_calc_bw(NULL, NULL) == -EINVAL);
    struct iris_vpu2_bw_input in = {IRIS_VPU2_BW_H264, IRIS_VPU2_BW_NV12,
                                   1280, 704, 1280, 704, 30, 0, 1000};
    CHECK(iris_vpu2_calc_bw(&in, &out) == 0 && out.ddr_kbps == 292000);
    in.output_height = 0;
    CHECK(iris_vpu2_calc_bw(&in, &out) == -EINVAL && out.ddr_kbps == 0 && out.llcc_kbps == 0);
    in.output_height = 704; in.queued_bytes = UINT64_MAX;
    CHECK(iris_vpu2_calc_bw(&in, &out) == -ERANGE && out.ddr_kbps == 0 && out.llcc_kbps == 0);
    printf("{\"primitive_checks\":%u,\"result\":\"PASS\"}\n", checks);
}

int main(void)
{
    primitive_checks();
    unsigned codec, fmt;
    struct input in;
    while (scanf("%u %u %" SCNu64 " %" SCNu64 " %" SCNu64 " %" SCNu64
                 " %" SCNu64 " %" SCNu64 " %" SCNu64,
                 &codec, &fmt, &in.width, &in.height, &in.out_width, &in.out_height,
                 &in.frame_rate, &in.operating_rate, &in.queued_bytes) == 9) {
        CHECK(in.width <= UINT32_MAX && in.height <= UINT32_MAX &&
              in.out_width <= UINT32_MAX && in.out_height <= UINT32_MAX &&
              in.frame_rate <= UINT32_MAX && in.operating_rate <= UINT32_MAX);
        struct iris_vpu2_bw_input input = {(enum iris_vpu2_bw_codec)codec,
            (enum iris_vpu2_bw_format)fmt, (u32)in.width, (u32)in.height,
            (u32)in.out_width, (u32)in.out_height, (u32)in.frame_rate,
            (u32)in.operating_rate, in.queued_bytes};
        struct iris_vpu2_bw_output output = {123, 456};
        int ret = iris_vpu2_calc_bw(&input, &output);
        if (ret) CHECK(output.ddr_kbps == 0 && output.llcc_kbps == 0);
        in.codec = codec == 0 ? MSM_VIDC_H264 : codec == 1 ? MSM_VIDC_HEVC :
                   codec == 2 ? MSM_VIDC_VP9 : MSM_VIDC_HEIC;
        in.capture = fmt == 0 ? MSM_VIDC_FMT_NV12 : fmt == 1 ? MSM_VIDC_FMT_P010 : MSM_VIDC_FMT_NONE;
        struct vidc_bus_vote_data reference;
        enum status original = prepare(&in, false, &reference);
        bool equal = false;
        if (original == OK) {
            calls++;
            CHECK(__calculate_decoder(&reference) == 0);
            equal = ret == 0 && output.ddr_kbps == reference.calc_bw_ddr &&
                    output.llcc_kbps == reference.calc_bw_llcc;
            CHECK(equal);
        }
        printf("{\"ret\":%d,\"ddr_kBps\":%" PRIu64 ",\"llcc_kBps\":%" PRIu64
               ",\"reference_status\":\"%s\",\"differential_equal\":%s}\n",
               ret, output.ddr_kbps, output.llcc_kbps, status_name[original], equal ? "true" : "false");
    }
    CHECK(feof(stdin));
    printf("{\"summary\":\"PASS\",\"c_checks\":%u,\"safe_reference_calls\":%u}\n", checks, calls);
    return 0;
}
