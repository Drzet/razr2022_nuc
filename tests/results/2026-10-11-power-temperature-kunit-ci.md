# Power signed battery temperature: ARM64 compile + real UML KUnit

**Date:** 2026-10-11 | **Kernel patch under test:** [Drzet/linux@`3b02b11bc5abdc5c453fa4af16b71bd8e44c2056`](https://github.com/Drzet/linux/commit/3b02b11bc5abdc5c453fa4af16b71bd8e44c2056) on `razr/power`, forked from Boot commit `cb9105ebeb9485e31d044d4fa69396b415523669`. **Baseline:** `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. **Code reviewer:** [kernel draft PR #3](https://github.com/Drzet/linux/pull/3) against current Boot head `3825dc6afb0f5e102845b32811ce0f518c0b4bbf`. Board DTS was not edited.

## Defect and source justification

Mainline `drivers/power/supply/qcom_battmgr.c` `qcom_battmgr_sm8350_callback()` previously decoded `BATT_TEMP` into `unsigned int val` before `DIV_ROUND_CLOSEST(val,10)`, and stored the result in `unsigned int status.temperature`. This produces an invalid enormous reading for a valid two's-complement *negative* temperature. The pinned Motorola reference `qti_battery_charger.c` casts the raw value to signed `int` before dividing by ten; standard Linux `power_supply` temperature is signed `int` in deci-degrees Celsius. This is a **standalone C arithmetic defect** independent of any unobserved oneli firmware variant.

Kernel fix is a single semantic conversion at the real callback, using `qcom_battmgr_decode_temperature(__le32)` in `drivers/power/supply/qcom_battmgr_internal.h`, and a signed `status.temperature` field. `qcom_battmgr_test.c` contains **three** KUnit test cases calling that exact production helper; negative inputs `-201`, `-5`, `-4`, positive `253`, `5`, `4`, and zero/250 exercise signed scaling and rounding.

The **header-only ACK difference** is retained as a bounded [INFERRED] protocol hypothesis: `qcom_battmgr_sm8350_callback()` rejects messages with payload under 4 bytes before recognizing opcode `0x04`; vendor `handle_message()` accepts `0x04` without enforcing response size. **No oneli firmware response length is observed**; we intentionally did **not** change ACK acceptance or charging controls. Actual driver-callback injection tests have not been run. KUnit validates the real shared conversion helper, not the entire RPMSG/GLINK transport or dispatcher.

## ARM64 object compile: PASS

- **Run:** [38169526109](https://github.com/Drzet/razr2022_nuc/actions/runs/38169526109); job `114559010192`; conclusion **success**; both driver and KUnit object files present/nonempty.
- Actual workflow project pull-request test-merge SHA **`74a4ec97a4b70f325c423c8e80c316e218fdab4e`**, with branch source `18508891b14431796704490afcdedf913b7409d6`; independent pinned kernel checkout SHA **`3b02b11bc5abdc5c453fa4af16b71bd8e44c2056`**.
- Host: `ubuntu-24.04`, `aarch64-linux-gnu-gcc`. Commands in checked-in [`power-battmgr-compile.yml`](../../.github/workflows/power-battmgr-compile.yml): `make -C kernel O=$GITHUB_WORKSPACE/out ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig`, configure requested symbols, `olddefconfig`, `prepare`, then `make ... drivers/power/supply/qcom_battmgr.o drivers/power/supply/qcom_battmgr_test.o`.
- Resolved config from job log: `CONFIG_QCOM_PMIC_GLINK=m`, `CONFIG_BATTERY_QCOM_BATTMGR=m`, `CONFIG_BATTERY_QCOM_BATTMGR_KUNIT_TEST=m`, `CONFIG_KUNIT=y`.
- Job log SHA-256:
  ```text
  57034fba4748c4ba788b4c2e957028af6b578f480e4e80e4d7dfd1e0dbea8e36  out/drivers/power/supply/qcom_battmgr.o
  012e90003d99dea9e5195563e2550747bc59d86bc9c02bdf591057d347e01aa1  out/drivers/power/supply/qcom_battmgr_test.o
  ```
- Scope: **two objects compiled**, not complete `modules`/final `modpost`. The workflow archives full `.config`, configure/compile logs and hashes. This result does **not** establish dependency-complete module linkage or device runtime.

## Host UML KUnit **execution**: PASS

- **Run:** [38169484188](https://github.com/Drzet/razr2022_nuc/actions/runs/38169484188); job `114558880490`; conclusion **success**. Actual project PR test-merge SHA **`d437db8262d11caafc4c19aa086ca39092155f52`** (branch source `4cd914d8423da8f09af6e1ff357271f9f761c63f`), pinned kernel source checkout exact same `3b02b11...`.
- Host: Ubuntu 24.04 x86_64, GCC 13.3.0, Python 3.12.3. Source and exact command in [`power-battmgr-kunit.yml`](../../.github/workflows/power-battmgr-kunit.yml):
  ```sh
  python3 kernel/tools/testing/kunit/kunit.py run \
    --arch=um --jobs=4 --timeout=180 \
    --build_dir="$GITHUB_WORKSPACE/kunit-build" \
    --kunitconfig="$GITHUB_WORKSPACE/power.kunitconfig" \
    'qcom-battmgr-temperature*'
  ```
- Fragment `CONFIG_KUNIT=y`, `CONFIG_KUNIT_ALL_TESTS=n`, `CONFIG_POWER_SUPPLY=y`, `CONFIG_BATTERY_QCOM_BATTMGR_KUNIT_TEST=y`; resolved config included `CONFIG_KUNIT=y`, `CONFIG_BATTERY_QCOM_BATTMGR_KUNIT_TEST=y`.
- **Actual UML kernel booted and executed the kernel KUnit suite**, reporting:
  ```text
  [PASSED] qcom_battmgr_temp_positive_test
  [PASSED] qcom_battmgr_temp_negative_test
  [PASSED] qcom_battmgr_temp_zero_test
  [PASSED] qcom-battmgr-temperature
  Testing complete. Ran 3 tests: passed: 3
  ```
- Job log SHA-256: UML test binary `kunit-build/linux` `ae611a9bacc34201884079c1e2bf14feb836eb9268d9cb66fe00252df182076d`; generated `evidence/uml.config` `0c9e7203c05e45f4cebebb907259c5b090666f2819b695a7983b03395c259efb`. Saved KUnit run log, config, binary/config hashes.
- Historical initial attempt [38169365696](https://github.com/Drzet/razr2022_nuc/actions/runs/38169365696) **failed**, because the KUnit config omitted `CONFIG_POWER_SUPPLY=y` and hence the test symbol could not resolve on UML. Workflow correction at `4cd914d8423da8f09af6e1ff357271f9f761c63f` fixed it; confirmed run above passed. No change to production conversion was required.

## Scope and acceptance

**Researched:** vendor/mainline packet comparison. **Implemented:** narrow signed-temperature correction and shared helper/KUnit suite. **Build-tested:** driver/test ARM64 objects and hosted UML KUnit kernel. **Emulated:** pure decoder tests executed on Linux UML, not Qualcomm hardware. **Hardware-tested:** none, owner has no phone. **Not validated:** actual physical battery temperature, GLINK firmware ACK format, charger status/charge-control policy, driver module dependency linking, suspend and thermal mitigation. Don't infer oneli hardware behavior from UML.

**Consumers:** Coordinator integrates reviewed kernel PR, Boot considers [rail proposal / issue #9](https://github.com/Drzet/razr2022_nuc/issues/9) while UFS/USB remain disabled, USB integrates PHY/repeater paths independently. No kernel baseline change and no shared DTS change.
