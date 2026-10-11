# Power subsystem handoff: second coordinator review, signed GLINK fix and staged rail contract

- **Date and originating chat:** 2026-10-11, Power agent follow-up to coordinator `docs/NEXT_TASKS.md` second review. The phone is unavailable; no physical tests were possible.
- **Kernel repository / branch / exact commit:** `Drzet/linux` / `razr/power` / **`3b02b11bc5abdc5c453fa4af16b71bd8e44c2056`**. Review branch through [kernel draft PR #3](https://github.com/Drzet/linux/pull/3) against Boot.
- **Coordinator repository / branch:** `Drzet/razr2022_nuc` / `razr/power`; this handoff and its CI workflows/results are committed only to the assigned branch; project-wide `STATUS.md` and `NEXT_TASKS.md` belong to coordinator and were **not modified**.
- **Upstream Linux baseline:** `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- **Required Boot dependency:** branch began at kernel `cb9105ebeb9485e31d044d4fa69396b415523669`. **Current Boot reviewed head** `3825dc6afb0f5e102845b32811ce0f518c0b4bbf` contains newer UART fixes and disabled RPMh/UFS candidates. Power commits touch no shared Boot-owned DTS and do not rebase or merge Boot work.
- **Research / implementation / validation state:** source-audited GLINK protocol and regulator assignments; **implemented** one signed-temperature driver fix + test helper + KUnit; **ARM64 object build passed** and **UML KUnit 3/3 executed/passed**; **kernel modules/modpost not tested**; **hardware tests deferred**.

## Changes and provenance

### Exact kernel patches on `razr/power`

1. `bb28bf42b6af5b9cbdb6b6b9e12c949d17547d78` modifies `drivers/power/supply/qcom_battmgr.c` to preserve negative two's-complement `BATT_TEMP` values and store temperature as signed `int`. This is a general arithmetic defect, not a Motorola-specific protocol assertion.
2. `9780ab22be444b840a5a3bb8ec1cb3497719dc1c` adds `drivers/power/supply/qcom_battmgr_internal.h`, production `qcom_battmgr_decode_temperature()` helper using `DIV_ROUND_CLOSEST((s32)le32_to_cpu(raw),10)`.
3. `d4aa07e37bb93158ed33c3c3ecb51c451e289417` adds three KUnit cases exercising that same helper with signed/unsigned boundary and rounding samples.
4. `b2b15e8bfd166062dcde6004addb58f267db939d` and `26d2fae5dd63d7c046b9b1f0f45a95e001d08f95` integrate test Kconfig and Makefile.
5. `3b02b11bc5abdc5c453fa4af16b71bd8e44c2056` allows isolated KUnit decoder validation on User-Mode Linux without the physical Qualcomm driver/firmware.
- **Files changed only:** `drivers/power/supply/{qcom_battmgr.c,qcom_battmgr_internal.h,qcom_battmgr_test.c,Kconfig,Makefile}`.
- **Source provenance:** pinned `MotorolaMobilityLLC/kernel-msm@9511d6b2dc469e5bd836992e3bdd6d19ace112e0` `drivers/power/supply/qti_battery_charger.c` casts temperature before dividing; upstream baseline `Drzet/linux@a5ebb76233b79db01e82e061173cb73c6d2b5c6b` uses unsigned storage and arithmetic. See [original protocol evidence](../power_oneli_charging_protocol_2026-10-11.md).

### Coordinator-owned tool/docs on subsystem branch

- [source-comparison CI](../../.github/workflows/power-glink-audit.yml) runs pinned Motorola/upstream source comparison and six synthetic fixtures.
- [source CI evidence](../../tests/results/2026-10-11-power-glink-ci.md) preserves source input hashes, exact PR merge SHA and passing results.
- [ARM64 compile CI](../../.github/workflows/power-battmgr-compile.yml) pins the **final** `3b02...` kernel SHA, records config and object hashes, and compiles both real production driver and KUnit suite objects.
- [UML KUnit runtime CI](../../.github/workflows/power-battmgr-kunit.yml) pins `3b02...` and launches UML kernel with three genuine signed-temperature KUnit subtests.
- [kernel build and KUnit runtime evidence](../../tests/results/2026-10-11-power-temperature-kunit-ci.md) records exact source SHA, test-merge SHAs, resolved config, object/binary hashes and earlier fixed Kconfig failure.
- [Power/Boot revised rail contract](../power_oneli_rail_contract_v2_2026-10-11.md) independently reviews Boot's already-disabled providers and distinguishes real vendor range versus vendor initial voltage; [issue #9](https://github.com/Drzet/razr2022_nuc/issues/9) directly assigns Boot the integration review.
- [cross-subsystem AUX/USB issue #3](https://github.com/Drzet/razr2022_nuc/issues/3) has Power's confirmation of S10B/L2B repeater supplies, L8C PS5169 VIO, and [INFERRED] input topology boundary (comment ID 6113030907).
- Coordinator review branch [draft PR #8](https://github.com/Drzet/razr2022_nuc/pull/8).

## Shared files and integration

No kernel board/SoC DT or firmware files are changed. No cherry-pick or merge was performed. Boot remains sole owner of `sm8475.dtsi` and `sm8475-motorola-oneli.dts`. Kernel draft PR #3 proposes **standalone driver change only**; coordinator may integrate after review. The current branch already inherits older Boot work, and latest Boot has four additional commits; coordinator must record the final merge/cherry-pick SHAs rather than assuming moving branches are equivalent.

- On Boot head `3825dc6...`, parent provider candidates PM8350 and PM8350C stay disabled and UFS host/PHY stay disabled. Consumer phandles match source.
- Vendor **allowed** UFS ranges µV: L5B 720000–958000 (init 880000), L7B 2400000–3544000 (init 2504000), L9B 1200000–1304000 (init 1200000), L10C 1200000–1304000 (init 1200000). Current disabled Boot DTS has min=max at these init values: should not be read as verified active constraints.
- PM8350 S10B (1.8V) and L2B (2.7–3.3V, init 3.072V) are the vendor-evidenced eUSB repeater supply paths. PM8350C L8C VIO is the later PS5169/USB3/DP supply (1.8–2.0V, init 1.8V).
- **[INFERRED]** PM8350C BOB and PM8350 S12B *input* relationships from SM8450 HDK comparator are not proven physical oneli connections; mainline's fixed 3.7V HDK `vph_pwr` must not be copied into a cell-phone power path.
- **GLINK/charger protocol:** source comparison has 8 matching opcodes and 41 property IDs. `BC_SET_NOTIFY_REQ` 0x04 header-only ACK handling differs in source, but whether actual Motorola firmware sends such packets is **unobserved [INFERRED]**. No code patch was made. No SGM41516D→SGM41542 false alias or Motorola dual-battery charging writes.

## Validation

| Stage | Exact result and SHA | What it establishes |
| --- | --- | --- |
| Source CLI | **PASS** [run 38168888153](https://github.com/Drzet/razr2022_nuc/actions/runs/38168888153), job 114557114053; PR test-merge `58514dd3e4d81ed8fcca2ae9cc30c31016ebe9ca`, source hashes documented in [CI record](../../tests/results/2026-10-11-power-glink-ci.md) | Two pinned C sources actually downloaded and tested: 8/8 common opcode mappings, 41/41 common property mappings; 6/6 independent synthetic fixtures; separate from kernel parser |
| ARM64 production + KUnit object compilation | **PASS** [run 38169526109](https://github.com/Drzet/razr2022_nuc/actions/runs/38169526109), job 114559010192; PR test-merge `74a4ec97a4b70f325c423c8e80c316e218fdab4e`, kernel exact `3b02b11bc5abdc5c453fa4af16b71bd8e44c2056` | `CONFIG_BATTERY_QCOM_BATTMGR=m`, `CONFIG_BATTERY_QCOM_BATTMGR_KUNIT_TEST=m`, `CONFIG_KUNIT=y`; produced both nonempty `.o` files, SHA-256 hashes in result doc. Not dependency-resolved module linking |
| Actual KUnit execution on host Linux UML | **PASS** [run 38169484188](https://github.com/Drzet/razr2022_nuc/actions/runs/38169484188), job 114558880490; PR test-merge `d437db8262d11caafc4c19aa086ca39092155f52`, kernel exact `3b02b11bc5abdc5c453fa4af16b71bd8e44c2056` | Test kernel built+booted under UML, `qcom-battmgr-temperature`: **3 passed, 0 failed**. Validates real shared conversion helper called by production driver; **not** entire GLINK response dispatch or transport |
| Earlier initial UML CI run | **FAILED** [run 38169365696](https://github.com/Drzet/razr2022_nuc/actions/runs/38169365696) | Kconfig did not select Power Supply menu; fixed by explicitly enabling `CONFIG_POWER_SUPPLY=y` at coordinator commit `4cd914d8423da8f09af6e1ff357271f9f761c63f`; later kernel-runtime suite passed |
| Oneli physical kernel/hardware | **DEFERRED** | Device unavailable, no battery/charger readings, no rail/USB/DP electrical validation, no temperature/charging response |

## Blockers and next test

1. **Boot:** consume [source-backed rail contract](../power_oneli_rail_contract_v2_2026-10-11.md), review current disabled provider min/max versus initial settings, all-applicable RPMh/UFS schema validation and exact parent-supply/board-revision gaps in [issue #9](https://github.com/Drzet/razr2022_nuc/issues/9). Never enable UFS/charging on guesses. USB may stage independently disabled S10B/L2B.
2. **Kernel coordinator/reviewer:** consider signed decoder patch [kernel PR #3](https://github.com/Drzet/linux/pull/3). Optional further gate: dependency-complete module build with normal `modpost`, or targeted in-kernel callback test harness. UML test only exercised the shared actual conversion helper; no GLINK wire test.
3. **Power next source investigation:** obtain pinned exact SGM41516D driver/register compatibility and Motorola combined-battery policy; distinguish `BATT_TEMP` wire unit and type from actual oneli firmware response; passive captures later if phone becomes available.
4. **Hardware:** only physical handset can validate actual PMIC voltages, charge state, thermal limits, suspend drain and battery switching. No current branch claims hardware acceptance.
