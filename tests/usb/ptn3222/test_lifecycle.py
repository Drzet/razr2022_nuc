#!/usr/bin/env python3
"""Execute production PHY core dispatch and SNPS/PTN3222 lifecycle with host mocks."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess


def definition(source, signature):
    """Extract one unchanged C function/struct definition by balanced braces."""
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    if source[end:end + 1] == ";":
        end += 1
    return source[start:end] + "\n"


BOUNDARY_SHIM = r'''
#define ARRAY_SIZE(x) (sizeof(x) / sizeof((x)[0]))
#define __iomem
#define dev_warn(...) ((void)0)
static int pm_gets, pm_puts;
static void mutex_lock(int *m) { assert(!*m); *m = 1; }
static void mutex_unlock(int *m) { assert(*m); *m = 0; }
static int phy_pm_runtime_get_sync(struct phy *p) { pm_gets++; return -ENOTSUPP; }
static void phy_pm_runtime_put(struct phy *p) { pm_puts++; }
struct clk { int dummy; };
struct clk_bulk_data { int dummy; };
struct reset_control { int dummy; };
static int clocks, clock_fail, reset_assert_fail, reset_deassert_fail, soc_fail;
static int clk_bulk_prepare_enable(int n, struct clk_bulk_data *c) {
    if (clock_fail) return clock_fail;
    assert(!clocks); clocks = 1; return 0;
}
static void clk_bulk_disable_unprepare(int n, struct clk_bulk_data *c) {
    assert(clocks); clocks = 0;
}
static int reset_control_assert(struct reset_control *r) { return reset_assert_fail; }
static int reset_control_deassert(struct reset_control *r) { return reset_deassert_fail; }
'''

BOUNDARY_CASES = r'''
static struct regulator own_rails[2];
static struct phy consumer;
static struct snps_eusb2_hsphy snps;
static int soc_init(struct phy *p) { return soc_fail; }
static const struct snps_eusb2_phy_drvdata soc_data = { .phy_init = soc_init, .num_clks = 1 };
static const struct phy_ops snps_ops = {
    .init = snps_eusb2_hsphy_init, .exit = snps_eusb2_hsphy_exit,
    .set_mode = snps_eusb2_hsphy_set_mode,
};
static void setup(bool profile_enabled) {
    fresh(profile_enabled); probe();
    test_phy.init_count = test_phy.power_count = test_phy.mutex = 0;
    memset(&consumer, 0, sizeof(consumer)); memset(&snps, 0, sizeof(snps));
    memset(own_rails, 0, sizeof(own_rails));
    own_rails[0].index = 2; own_rails[1].index = 3;
    snps.vregs[0].consumer = &own_rails[0]; snps.vregs[1].consumer = &own_rails[1];
    snps.repeater = &test_phy; snps.data = &soc_data;
    consumer.data = &snps; consumer.ops = &snps_ops;
    snps.phy = &consumer;
    clocks = clock_fail = reset_assert_fail = reset_deassert_fail = soc_fail = 0;
    pm_gets = pm_puts = 0;
}
static bool check(bool condition, const char *what) {
    if (!condition) fprintf(stderr, "FAIL: %s\n", what);
    return condition;
}
static bool state(int outer, int inner, int rail_votes, int asserted) {
    struct ptn3222 *p = test_phy.data;
    fprintf(stderr, "STATE: outer=%d inner=%d reset=%d votes=%d/%d own=%d/%d faulted=%d initialized=%d\n",
        consumer.init_count, test_phy.init_count, gpio.value, rails[0].votes,
        rails[1].votes, own_rails[0].votes, own_rails[1].votes, p->faulted, p->initialized);
    return check(consumer.init_count == outer && test_phy.init_count == inner &&
        rails[0].votes == rail_votes && rails[1].votes == rail_votes &&
        gpio.value == asserted, "PHY counts / repeater votes / reset");
}
static bool own_off(void) {
    return check(!own_rails[0].votes && !own_rails[1].votes && !clocks,
                 "consumer regulator/clock cleanup");
}
static bool normal_exit(void) {
    int ret = phy_exit(&consumer);
    return check(ret == 0, "normal consumer exit") && state(0, 0, 0, 1) && own_off();
}
static bool failed_init_retry(bool persistent) {
    setup(true); struct ptn3222 *p = test_phy.data;
    fail_at = 11; /* two consumer votes, four provider power ops, four reads */
    disable_fail = 1;
    int ret = phy_init(&consumer); fprintf(stderr, "first init: %d\n", ret);
    if (!check(ret == -EIO && p->faulted, "preserved initiating write error") ||
        !state(0, 0, 1, 1) || !own_off()) return false;
    int before_writes = writes;
    fail_at = 0; disable_fail = persistent ? 1 : 0;
    ret = phy_init(&consumer); fprintf(stderr, "core init retry: %d\n", ret);
    if (persistent) {
        if (!check(ret == -EAGAIN && p->faulted && writes == before_writes,
                   "persistent cleanup returns provider error without new writes") ||
            !state(0, 0, 1, 1) || !own_off()) return false;
        ret = phy_init(&consumer);
    }
    if (!state(1, 1, 1, 0) ||
        !check(ret == 0 && !p->faulted && p->initialized, "normal core init retry recovers")) return false;
    profile(0x64); return normal_exit();
}
static bool reconnect(bool persistent) {
    setup(true); struct ptn3222 *p = test_phy.data;
    if (!check(phy_init(&consumer) == 0, "successful initial consumer init")) return false;
    disable_fail = 1;
    int ret = phy_exit(&consumer); fprintf(stderr, "consumer exit with pending repeater cleanup: %d\n", ret);
    if (!check(ret == 0 && p->faulted, "consumer releases own reference and defers repeater cleanup") ||
        !state(0, 1, 1, 1) || !own_off()) return false;
    disable_fail = persistent ? 1 : 0;
    ret = phy_init(&consumer); fprintf(stderr, "consumer reconnect: %d\n", ret);
    if (persistent) {
        if (!check(ret == -EAGAIN && p->faulted, "persistent pending exit prevents successful reconnect") ||
            !state(0, 1, 1, 1) || !own_off()) return false;
        ret = phy_init(&consumer);
    }
    if (!state(1, 1, 1, 0) ||
        !check(ret == 0 && !p->faulted && p->initialized, "reconnect actually reinitializes repeater")) return false;
    return normal_exit();
}
static bool late_failure(int stage) {
    setup(true); struct ptn3222 *p = test_phy.data;
    if (stage == 0) clock_fail = -ETIMEDOUT;
    if (stage == 1) reset_assert_fail = -ETIMEDOUT;
    if (stage == 2) reset_deassert_fail = -ETIMEDOUT;
    if (stage == 3) soc_fail = -ETIMEDOUT;
    disable_fail = 1;
    int ret = phy_init(&consumer);
    if (!check(ret == -ETIMEDOUT && p->faulted, "later consumer failure preserves initiating error") ||
        !state(0, 1, 1, 1) || !own_off()) return false;
    clock_fail = reset_assert_fail = reset_deassert_fail = soc_fail = 0;
    if (!check(phy_init(&consumer) == 0 && !p->faulted && p->initialized,
               "later unwind cleanup recovered before reconnect") || !state(1, 1, 1, 0)) return false;
    return normal_exit();
}
static bool voltage_retry(void) {
    setup(true); fail_at = 11; clear_fail = 1;
    if (!check(phy_init(&consumer) == -EIO, "write error preserved across voltage cleanup failure") ||
        !check(consumer.init_count == 0 && test_phy.init_count == 0 &&
               !rails[0].votes && rails[1].votes == 1 && gpio.value == 1,
               "remaining 1.8 V vote retained after 3 V voltage cleanup failure") || !own_off()) return false;
    fail_at = 0;
    if (!check(phy_init(&consumer) == 0, "voltage cleanup retried during normal init") ||
        !state(1, 1, 1, 0)) return false;
    return normal_exit();
}
static bool legacy_and_references(void) {
    setup(false);
    if (!check(phy_init(&consumer) == 0 && phy_init(&consumer) == 0, "shared outer init reference")) return false;
    if (!state(2, 1, 1, 0) || !check(!reads && !writes, "legacy no register accesses")) return false;
    if (!check(phy_exit(&consumer) == 0, "first outer reference release") || !state(1, 1, 1, 0)) return false;
    return normal_exit();
}
static bool optional_repeater(void) {
    setup(false); snps.repeater = NULL;
    if (!check(phy_init(&consumer) == 0 && phy_exit(&consumer) == 0,
               "optional absent repeater consumer lifecycle") || !own_off()) return false;
    return state(0, 0, 0, 1);
}
static bool role_replay(void) {
    setup(true);
    if (!check(phy_set_mode_ext(&consumer, PHY_MODE_USB_HOST, 0) == 0 && !writes,
               "consumer/core mode cached before init") ||
        !check(phy_init(&consumer) == 0, "host profile init")) return false;
    profile(0x24);
    disable_fail = 1;
    if (!check(phy_exit(&consumer) == 0, "host disconnect with deferred cleanup") ||
        !check(phy_init(&consumer) == 0, "host reconnect")) return false;
    profile(0x24);
    if (!check(phy_set_mode_ext(&consumer, PHY_MODE_USB_DEVICE, 0) == 0,
               "powered role change through consumer/core")) return false;
    profile(0x64); return normal_exit();
}
int main(int argc, char **argv) {
    bool result = false;
    if (argc != 2) return 2;
    if (!strcmp(argv[1], "init-retry")) result = failed_init_retry(false);
    if (!strcmp(argv[1], "init-persistent")) result = failed_init_retry(true);
    if (!strcmp(argv[1], "reconnect")) result = reconnect(false);
    if (!strcmp(argv[1], "reconnect-persistent")) result = reconnect(true);
    if (!strcmp(argv[1], "late-clock")) result = late_failure(0);
    if (!strcmp(argv[1], "late-reset-assert")) result = late_failure(1);
    if (!strcmp(argv[1], "late-reset-deassert")) result = late_failure(2);
    if (!strcmp(argv[1], "late-soc")) result = late_failure(3);
    if (!strcmp(argv[1], "voltage-retry")) result = voltage_retry();
    if (!strcmp(argv[1], "legacy-counts")) result = legacy_and_references();
    if (!strcmp(argv[1], "optional-repeater")) result = optional_repeater();
    if (!strcmp(argv[1], "role-replay")) result = role_replay();
    result = check(pm_gets == pm_puts, "balanced mocked PM dispatch") && result;
    free(allocated); allocated = NULL;
    fprintf(stderr, "%s: %s\n", result ? "PASS" : "FAIL", argv[1]);
    return result ? 0 : 1;
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kernel", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expect-failure", action="store_true")
    parser.add_argument("--revision", help="Read exact source from existing Git objects instead of the worktree")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    unit = runpy.run_path(str(Path(__file__).with_name("test_driver.py")))
    shim = unit["SHIM"].replace("struct phy { void *data; };", """
struct phy_ops;
struct phy { void *data; int init_count, power_count, mutex;
             struct device dev; const struct phy_ops *ops;
             struct { enum phy_mode mode; } attrs; };
""").replace("return &test_phy;", "test_phy.ops = ops; return &test_phy;")
    shim = shim.replace("if (disable_fail)", "if (disable_fail && r->index < 2)")
    shim = shim.replace("if (clear_fail)", "if (clear_fail && r->index < 2)")
    shim = shim.replace("#define EPROBE_DEFER 517", "#define EPROBE_DEFER 517\n#define ENOTSUPP 524")
    # Fresh fixtures use independent core counts; production structs/functions below are unchanged.
    helpers = unit["CASES"].split("static void successful_paths", 1)[0]
    helpers = helpers.replace("test_phy.data = NULL;", "memset(&test_phy, 0, sizeof(test_phy));")
    paths = ["drivers/phy/phy-nxp-ptn3222.c", "drivers/phy/phy-core.c",
             "drivers/phy/phy-snps-eusb2.c"]
    sources = [subprocess.check_output(["git", "-C", str(args.kernel), "show",
               args.revision + ":" + p], text=True) if args.revision
               else (args.kernel / p).read_text() for p in paths]
    provider = "\n".join(l for l in sources[0].splitlines() if not l.startswith("#include"))
    provider = provider.split("static const struct i2c_device_id", 1)[0]
    core = "".join(definition(sources[1], "int " + n + "(")
                   for n in ["phy_init", "phy_exit", "phy_set_mode_ext"])
    structs = "#define EUSB2_NUM_VREGS 2\n" + "".join(
        definition(sources[2], "struct " + n + " {")
        for n in ["snps_eusb2_phy_drvdata", "snps_eusb2_hsphy"])
    extra = ""
    if "static int snps_eusb2_repeater_exit(" in sources[2]:
        extra = definition(sources[2], "static int snps_eusb2_repeater_exit(")
    consumer = extra + "".join(definition(sources[2], "static int " + n + "(")
                              for n in ["snps_eusb2_hsphy_set_mode", "snps_eusb2_hsphy_init",
                                        "snps_eusb2_hsphy_exit"])
    harness = args.output / "lifecycle-harness.c"
    harness.write_text(shim + BOUNDARY_SHIM + provider + core + structs + consumer
                       + helpers + BOUNDARY_CASES)
    binary = args.output / "lifecycle-harness"
    subprocess.run(["gcc", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                    "-Wno-unused-parameter", "-Wno-unused-const-variable", "-Wno-unused-function",
                    "-fsanitize=address,undefined", "-g", "-o", str(binary), str(harness)], check=True)
    names = ["init-retry", "reconnect"] if args.expect_failure else [
        "init-retry", "init-persistent", "reconnect", "reconnect-persistent",
        "late-clock", "late-reset-assert", "late-reset-deassert", "late-soc",
        "voltage-retry", "legacy-counts", "optional-repeater", "role-replay"]
    results = []
    for name in names:
        r = subprocess.run([str(binary), name], text=True, capture_output=True)
        log = r.stdout + r.stderr
        (args.output / f"{name}.log").write_text(log)
        expected = r.returncode == 1 and "FAIL:" in log if args.expect_failure else r.returncode == 0
        results.append({"case": name, "returncode": r.returncode, "expected_outcome": expected})
        print(log, end="")
        assert expected, (name, r.returncode, log)
    (args.output / "lifecycle-result.json").write_text(json.dumps({
        "sources": {p: hashlib.sha256(s.encode()).hexdigest() for p, s in zip(paths, sources)},
        "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "unit_shim_sha256": hashlib.sha256(Path(__file__).with_name("test_driver.py").read_bytes()).hexdigest(),
        "source_revision": args.revision,
        "expected_failure": args.expect_failure,
        "scope": "unchanged production core dispatch/count and SNPS/provider bodies with host mocks",
        "cases": results,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
