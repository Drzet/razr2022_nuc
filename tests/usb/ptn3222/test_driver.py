#!/usr/bin/env python3
"""Execute the supplied production PTN3222 driver with scoped host mocks.

The shim covers provider failures, regulator vote accounting and I2C faults;
it does not emulate the generic PHY core, GPIO electricity or a real chip.
Only includes and the module registration trailer are omitted from C input.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

SHIM = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#define NUM_TEST_SUPPLIES 2
#define GFP_KERNEL 0
#define GPIOD_OUT_HIGH 1
#define THIS_MODULE NULL
#define EPROBE_DEFER 517
#define ERR_PTR(e) ((void *)(intptr_t)(e))
#define PTR_ERR(p) ((long)(intptr_t)(p))
#define IS_ERR(p) ((uintptr_t)(p) >= (uintptr_t)-4095)
#define PTR_ERR_OR_ZERO(p) (IS_ERR(p) ? PTR_ERR(p) : 0)
#define dev_err(...) ((void)0)
#define dev_dbg(...) ((void)0)
#define dev_err_probe(d, e, ...) (e)
enum phy_mode { PHY_MODE_INVALID, PHY_MODE_USB_HOST, PHY_MODE_USB_DEVICE,
                PHY_MODE_USB_OTG, PHY_MODE_PCIE };
struct device_node { const char *profile; bool present, malformed, supply[2]; };
struct device { struct device_node *of_node; };
struct i2c_client { struct device dev; };
struct phy { void *data; };
struct gpio_desc { int value; };
struct regulator { int index, votes, min_uv, max_uv; };
struct regulator_bulk_data {
    const char *supply; int init_load_uA; struct regulator *consumer;
};
struct regmap { unsigned int values[256]; };
struct regmap_config { int reg_bits, val_bits, max_register; };
struct phy_provider { int dummy; };
struct phy_ops {
    int (*init)(struct phy *); int (*exit)(struct phy *);
    int (*set_mode)(struct phy *, enum phy_mode, int); void *owner;
};
enum { F_NONE, F_ALLOC, F_GPIO, F_REGULATORS, F_REGMAP, F_ACTION,
       F_PHY, F_PROVIDER };
static int provider_fault, provider_errno, operation, fail_at, fail_also;
static int writes, reads, disable_fail, clear_fail, bulk_calls;
static bool no_gpio, startup_wait;
static struct gpio_desc gpio;
static struct regulator rails[2];
static struct regmap map;
static struct regulator_bulk_data supply_data[2];
static struct phy test_phy;
static struct phy_provider provider;
static void *allocated;
static void (*cleanup_action)(void *);
static void *cleanup_data;
static int events[128], nevents;
static int scenarios;
static void event(int code) { assert(nevents < 128); events[nevents++] = code; }
static int fault(void) {
    operation++;
    return operation == fail_at || operation == fail_also ? -EIO : 0;
}
static void *devm_kzalloc(struct device *d, size_t n, int flags) {
    if (provider_fault == F_ALLOC) return NULL;
    allocated = calloc(1, n); assert(allocated); return allocated;
}
static void *of_find_property(struct device_node *n, const char *name, void *len) {
    if (!strcmp(name, "nxp,usb2-tuning-profile")) return n->present ? n : NULL;
    if (!strcmp(name, "vdd3v3-supply")) return n->supply[0] ? n : NULL;
    if (!strcmp(name, "vdd1v8-supply")) return n->supply[1] ? n : NULL;
    return NULL;
}
static int of_property_read_string(struct device_node *n, const char *key,
                                   const char **value) {
    if (n->malformed) return -EILSEQ;
    *value = n->profile; return 0;
}
static struct gpio_desc *devm_gpiod_get_optional(struct device *d,
                                                const char *key, int flags) {
    if (provider_fault == F_GPIO) return ERR_PTR(provider_errno);
    if (no_gpio) return NULL;
    gpio.value = flags; return &gpio;
}
static void gpiod_set_value_cansleep(struct gpio_desc *g, int value) {
    if (!g) return;
    g->value = value; event(value ? 91 : 90);
    startup_wait = false;
}
static int devm_regulator_bulk_get_const(struct device *d, int n,
        const struct regulator_bulk_data *s, struct regulator_bulk_data **out) {
    if (provider_fault == F_REGULATORS) return provider_errno;
    assert(n == 2);
    memcpy(supply_data, s, sizeof(supply_data));
    for (int i = 0; i < 2; i++) supply_data[i].consumer = &rails[i];
    *out = supply_data; return 0;
}
static int regulator_set_voltage(struct regulator *r, int min, int max) {
    event((min ? 10 : 40) + r->index);
    if (min) { int e = fault(); if (e) return e; }
    else if (clear_fail) { clear_fail--; return -ERANGE; }
    r->min_uv = min; r->max_uv = max; return 0;
}
static int regulator_enable(struct regulator *r) {
    int e; event(20 + r->index); e = fault(); if (e) return e;
    r->votes++; assert(r->votes == 1); return 0;
}
static int regulator_disable(struct regulator *r) {
    event(30 + r->index);
    if (disable_fail) { disable_fail--; return -EAGAIN; }
    assert(r->votes == 1); r->votes--; return 0;
}
static int regulator_bulk_enable(int n, struct regulator_bulk_data *s) {
    bulk_calls++;
    for (int i = 0; i < n; i++) {
        int ret = regulator_enable(s[i].consumer);
        if (ret) { while (i--) regulator_disable(s[i].consumer); return ret; }
    }
    return 0;
}
static int regulator_bulk_disable(int n, struct regulator_bulk_data *s) {
    bulk_calls++;
    for (int i = n - 1; i >= 0; i--) {
        int ret = regulator_disable(s[i].consumer); if (ret) return ret;
    }
    return 0;
}
static struct regmap *devm_regmap_init_i2c(struct i2c_client *c,
                                        const struct regmap_config *config) {
    if (provider_fault == F_REGMAP) return ERR_PTR(provider_errno);
    assert(config->reg_bits == 8 && config->val_bits == 8); return &map;
}
static void usleep_range(int min, int max) {
    assert(min <= max); event(min == 1000 ? 80 : 81);
    if (min >= 1000) startup_wait = true;
}
static int regmap_read(struct regmap *m, unsigned int reg, unsigned int *value) {
    int e;
    assert(rails[0].votes == 1 && rails[1].votes == 1);
    assert(!gpio.value && startup_wait);
    reads++; event(100 + reg); e = fault(); if (e) return e;
    *value = m->values[reg]; return 0;
}
static int regmap_write(struct regmap *m, unsigned int reg, unsigned int value) {
    int e;
    assert(rails[0].votes == 1 && rails[1].votes == 1 && !gpio.value);
    assert(reads >= 4); writes++; event(200 + reg);
    e = fault(); if (e) return e;
    m->values[reg] = value; return 0;
}
static int devm_add_action_or_reset(struct device *d, void (*fn)(void *), void *p) {
    if (provider_fault == F_ACTION) { fn(p); return provider_errno; }
    cleanup_action = fn; cleanup_data = p; return 0;
}
static struct phy *devm_phy_create(struct device *d, struct device_node *n,
                                 const struct phy_ops *ops) {
    if (provider_fault == F_PHY) return ERR_PTR(provider_errno);
    return &test_phy;
}
static void *phy_get_drvdata(struct phy *p) { return p->data; }
static void phy_set_drvdata(struct phy *p, void *data) { p->data = data; }
static int of_phy_simple_xlate;
static struct phy_provider *devm_of_phy_provider_register(struct device *d,
                                                          int xlate) {
    if (provider_fault == F_PROVIDER) return ERR_PTR(provider_errno);
    return &provider;
}
'''

CASES = r'''
static struct device_node node;
static struct i2c_client client;
static void fresh(bool profile) {
    free(allocated); allocated = NULL; cleanup_action = NULL; cleanup_data = NULL;
    memset(&map, 0, sizeof(map)); memset(rails, 0, sizeof(rails));
    rails[0].index = 0; rails[1].index = 1;
    node = (struct device_node){ .profile = "motorola,oneli", .present = profile,
                                 .supply = {true, true} };
    client.dev.of_node = &node; test_phy.data = NULL;
    gpio.value = 1; startup_wait = false;
    provider_fault = F_NONE; provider_errno = -EPROBE_DEFER;
    fail_at = fail_also = operation = writes = reads = nevents = bulk_calls = 0;
    disable_fail = clear_fail = 0; no_gpio = false;
    map.values[0x13] = 0xa2; map.values[0x14] = 0x22;
    map.values[0x15] = 0x32; map.values[0x16] = 0x02;
    scenarios++;
}
static struct ptn3222 *probe(void) {
    assert(ptn3222_probe(&client) == 0);
    assert(!rails[0].votes && !rails[1].votes && !reads && !writes);
    return test_phy.data;
}
static void off(void) {
    assert(!rails[0].votes && !rails[1].votes);
    assert(!rails[0].min_uv && !rails[1].min_uv && gpio.value == 1);
}
static void profile(unsigned int tx) {
    assert(map.values[6] == 0x40 && map.values[7] == 0x22 && map.values[8] == tx);
}
static void successful_paths(void) {
    struct ptn3222 *p;
    fresh(true); p = probe();
    assert(supply_data[0].init_load_uA == 3500 && supply_data[1].init_load_uA == 32000);
    assert(ptn3222_init(&test_phy) == 0); profile(0x64);
    const int begin[] = {11, 21, 10, 20, 90, 80, 119, 120, 121, 122, 206, 207, 208, 81};
    assert(nevents == 14 && !memcmp(events, begin, sizeof(begin)));
    assert(rails[1].min_uv == 1800000 && rails[0].min_uv == 3075000);
    assert(ptn3222_set_mode(&test_phy, PHY_MODE_USB_HOST, 0) == 0); profile(0x24);
    assert(ptn3222_set_mode(&test_phy, PHY_MODE_USB_DEVICE, 0) == 0); profile(0x64);
    int old_writes = writes;
    assert(ptn3222_set_mode(&test_phy, PHY_MODE_PCIE, 0) == -EINVAL);
    assert(writes == old_writes && p->mode == PHY_MODE_USB_DEVICE);
    nevents = 0; assert(ptn3222_exit(&test_phy) == 0); off();
    const int end[] = {91, 30, 40, 31, 41};
    assert(nevents == 5 && !memcmp(events, end, sizeof(end)));
    assert(ptn3222_set_mode(&test_phy, PHY_MODE_USB_HOST, 0) == 0);
    assert(writes == old_writes);
    assert(ptn3222_init(&test_phy) == 0); profile(0x24);
    assert(ptn3222_exit(&test_phy) == 0); off();

    fresh(true); probe(); map.values[0x16] = 1; map.values[0x13] = 0xa4;
    assert(ptn3222_set_mode(&test_phy, PHY_MODE_USB_HOST, 0) == 0);
    assert(ptn3222_init(&test_phy) == 0); profile(0x24);
    assert(ptn3222_set_mode(&test_phy, PHY_MODE_USB_OTG, 0) == 0); profile(0x64);
    cleanup_action(cleanup_data); off();

    fresh(false); p = probe(); assert(!p->regmap);
    assert(ptn3222_init(&test_phy) == 0 && !reads && !writes && bulk_calls == 1);
    assert(ptn3222_set_mode(&test_phy, PHY_MODE_USB_HOST, 0) == 0 && !writes);
    assert(ptn3222_exit(&test_phy) == 0 && bulk_calls == 2); off();
    fresh(false); no_gpio = true; probe();
    assert(ptn3222_init(&test_phy) == 0 && ptn3222_exit(&test_phy) == 0);
}
static void init_faults(void) {
    for (int i = 1; i <= 11; i++) {
        fresh(true); struct ptn3222 *p = probe(); fail_at = i;
        assert(ptn3222_init(&test_phy) == -EIO); off();
        assert(!p->initialized && !p->faulted);
        if (i <= 8) assert(!writes);
        fail_at = 0; assert(ptn3222_init(&test_phy) == 0); profile(0x64);
        assert(ptn3222_exit(&test_phy) == 0); off();
    }
    for (int byte = 0; byte < 3; byte++) {
        fresh(true); probe(); map.values[0x14 + byte] ^= 0x80;
        assert(ptn3222_init(&test_phy) == -ENODEV && !writes); off();
    }
    fresh(true); struct ptn3222 *p = probe(); fail_at = 9; disable_fail = 1;
    assert(ptn3222_init(&test_phy) == -EIO && p->faulted && gpio.value == 1);
    assert(rails[0].votes == 1 && rails[1].votes == 1);
    assert(ptn3222_init(&test_phy) == -EBUSY);
    assert(ptn3222_exit(&test_phy) == 0); off();
    assert(ptn3222_init(&test_phy) == 0 && ptn3222_exit(&test_phy) == 0); off();
    fresh(true); p = probe(); fail_at = 4; clear_fail = 1;
    assert(ptn3222_init(&test_phy) == -EIO && p->faulted);
    assert(ptn3222_exit(&test_phy) == 0); off();
}
static void mode_faults(void) {
    for (int i = 1; i <= 3; i++) {
        fresh(true); struct ptn3222 *p = probe(); assert(ptn3222_init(&test_phy) == 0);
        fail_at = operation + i;
        assert(ptn3222_set_mode(&test_phy, PHY_MODE_USB_HOST, 0) == -EIO);
        assert(p->mode == PHY_MODE_USB_DEVICE && p->initialized && !p->faulted);
        profile(0x64); fail_at = 0;
        assert(ptn3222_set_mode(&test_phy, PHY_MODE_USB_HOST, 0) == 0); profile(0x24);
        assert(ptn3222_exit(&test_phy) == 0); off();
    }
    fresh(true); struct ptn3222 *p = probe(); assert(ptn3222_init(&test_phy) == 0);
    fail_at = operation + 3; fail_also = operation + 4;
    assert(ptn3222_set_mode(&test_phy, PHY_MODE_USB_HOST, 0) == -EIO); off();
    assert(p->faulted && !p->initialized && p->mode == PHY_MODE_USB_DEVICE);
    assert(ptn3222_set_mode(&test_phy, PHY_MODE_USB_HOST, 0) == -EIO);
    assert(ptn3222_exit(&test_phy) == 0);
    assert(ptn3222_set_mode(&test_phy, PHY_MODE_USB_HOST, 0) == 0);
    assert(ptn3222_init(&test_phy) == 0); profile(0x24);
    assert(ptn3222_exit(&test_phy) == 0); off();
    fresh(true); p = probe(); assert(ptn3222_init(&test_phy) == 0);
    disable_fail = 1; assert(ptn3222_exit(&test_phy) == -EAGAIN);
    assert(p->faulted && rails[0].votes == 1 && rails[1].votes == 1 && gpio.value == 1);
    assert(ptn3222_exit(&test_phy) == 0); off();
}
static void probe_faults(void) {
    for (int i = F_ALLOC; i <= F_PROVIDER; i++) {
        fresh(true); provider_fault = i;
        if (i == F_ALLOC) assert(ptn3222_probe(&client) == -ENOMEM);
        else assert(ptn3222_probe(&client) == -EPROBE_DEFER);
        off();
    }
    fresh(true); node.profile = "unknown";
    assert(ptn3222_probe(&client) == -EINVAL && !reads && !writes); off();
    fresh(true); node.malformed = true;
    assert(ptn3222_probe(&client) == -EILSEQ); off();
    for (int i = 0; i < 2; i++) {
        fresh(true); node.supply[i] = false;
        assert(ptn3222_probe(&client) == -EINVAL); off();
    }
    fresh(true); no_gpio = true;
    assert(ptn3222_probe(&client) == -EINVAL); off();
}
int main(void) {
    successful_paths(); init_faults(); mode_faults(); probe_faults();
    free(allocated); printf("PASS: %d production-driver scenarios\n", scenarios);
    return 0;
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kernel", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.kernel / "drivers/phy/phy-nxp-ptn3222.c"
    original = source.read_text()
    production = "\n".join(line for line in original.splitlines()
                           if not line.startswith("#include"))
    production = production.split("static const struct i2c_device_id", 1)[0]
    args.output.mkdir(parents=True, exist_ok=True)
    harness = args.output / "driver-harness.c"
    harness.write_text(SHIM + production + CASES)
    binary = args.output / "driver-harness"
    subprocess.run(["gcc", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                    "-Wno-unused-parameter", "-Wno-unused-const-variable",
                    "-fsanitize=address,undefined", "-g", "-o", str(binary),
                    str(harness)], check=True)
    result = subprocess.run([str(binary)], text=True, capture_output=True)
    if result.returncode:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        raise SystemExit(result.returncode)
    (args.output / "host-result.json").write_text(json.dumps({
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": "production C with host mocks; ASan/UBSan; not kernel/hardware",
        "result": result.stdout.strip(),
    }, indent=2) + "\n")
    print(result.stdout, end="")


if __name__ == "__main__":
    main()
