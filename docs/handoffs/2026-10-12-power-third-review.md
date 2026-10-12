# Power third coordinator handoff: charger/policy source audit and stock firmware reconciliation

- **Date/chat:** 2026-10-12, Power owner continuation from the third coordinator review. Connection stalled during a bulk GitHub source inspection; resumed using bounded pinned-source reads.
- **Kernel repo:** `Drzet/linux`. Assigned `razr/power@3b02b11bc5abdc5c453fa4af16b71bd8e44c2056` unchanged in this round. Coordinator already supplied standalone fix branch `razr/power-temp-standalone@564f2c7df60316db86e36d7267ddadf07bc32b7e` and [draft PR #4](https://github.com/Drzet/linux/pull/4).
- **Kernel upstream baseline:** `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`; source-reviewed current Boot head `razr/boot@6eec6ddd7842622668c937a466a8db47d20517b1`.
- **Project repo:** `Drzet/razr2022_nuc` assigned branch `razr/power`; third-round new source matrix [`docs/power_oneli_sgm41516d_policy_stock_review_2026-10-12.md`](../power_oneli_sgm41516d_policy_stock_review_2026-10-12.md), first commit `f2af97efb3100537708cc3693cc94d359567e561`. This handoff is a separate project commit; no aggregate main STATUS/NEXT_TASKS edited.
- **Stage:** source-researched; existing temperature fix implementation **previously ARM64-object-built and UML KUnit 3/3 passed**, new charger policy code **not implemented**, stock Android hardware readings **observed**, native phone **not tested**.

## Changes and provenance

**Standalone integration patch verified:** The coordinator's `razr/power-temp-standalone@564f2c7df60316db86e36d7267ddadf07bc32b7e` has **five commits** relative to upstream baseline and modifies exactly:

- `drivers/power/supply/qcom_battmgr.c`
- `drivers/power/supply/qcom_battmgr_internal.h`
- `drivers/power/supply/qcom_battmgr_test.c`
- `drivers/power/supply/Kconfig`
- `drivers/power/supply/Makefile`

For **all five files**, exact Git blob IDs were independently compared with previously tested `razr/power@3b02b11bc5abdc5c453fa4af16b71bd8e44c2056`: **identical 5/5**. This is a clean baseline-based change set with **no inherited Boot commits**. Previously accepted tests on the original source: [ARM64 object pass 38169526109](https://github.com/Drzet/razr2022_nuc/actions/runs/38169526109), [real UML KUnit 3/3 pass 38169484188](https://github.com/Drzet/razr2022_nuc/actions/runs/38169484188), original pinned Motorola/mainline opcode/property CLI [pass 38168888153](https://github.com/Drzet/razr2022_nuc/actions/runs/38168888153). **New standalone branch itself not recompiled or dependency-linked**. Coordinator's proposed combined Image/modules normal modpost is the appropriate next meaningful gate. No independently new build claims.

**SGM41516D:** source audit against pinned oneli Motorola overlay `MotorolaMobilityLLC/kernel-devicetree@90fa7be1db5bd47202673d4431408659149a7359` and separate Motorola-family source comparator `LineageOS/android_kernel_motorola_sm8250@d0c1bd7e2578bba26e5e178702fae09596b11920` (`drivers/power/sgm4154x_charger_lite`, `drivers/power/mmi_charger`, `drivers/power/bq27426_fg_mmi`). The latter is not established to be the exact stock **oneli** build's driver. Mainline reference `Drzet/linux@a5ebb...` `sgm41542_charger.c` only matches `sgmicro,sgm41542`.

Confirmed Motorola-family source:
- Chip ID reads register `0x0B` and masks bits 6:3; SGM41542 and SGM41516D are assigned the **same** masked PN ID. Thus a 41542 alias is not validated by this read. Vendor-family probe may return a raw positive byte on mismatch and its OTG registration error handling dereferences before checking `IS_ERR()`; don't wholesale import driver.
- Register/common-unit overlap includes REG02 charging-current 60mA step, REG00 input current 100mA offset/step and REG04 voltage 3.856V+32mV/step with REG0F fine tuning. Oneli charger uses distinct CE PM8350C GPIO2 and paired PM8350B GPIO1+3 switches.
- Vendor-family `SGM4154x_MANUFACTURER` is literally `Texas Instruments`, matching the weird stock `uevent` manufacturer even though SGMicro's actual SGM41516D product page lists an SGMicro single-cell NVDC charger. **This is a source-consistent explanation, not proof of identical installed driver bytes**.
- Family BQ27426 `mmi,temp-source=1` maps to enum `TEMP_SOURCE_EXTERNAL`, a source-level improvement over previous unknown. The physical external thermistor/channel remains unknown.
- Paired Motorola manager dynamically tracks both current and OCV (corrects ESR), sets load switches/paired charge current, protects overvoltage/overcurrent and applies temperature-zone/charging constraints. Composite SOC is charge-full-capacity-weighted, currents and counters summed, reported pack voltages averaged, hottest pack temperature used; absent from mainline general battery manager.
- Oneli DT defines exact `mmi,paired-ichg-table=<60 1200 90 900 120 600 150 300>`, `mmi,paired-load-thres=<800 400>`, split paired IDs, thermal zoning, charger thresholds and `mmi,upper-limit-capacity=80`. Motorola-family manager's 80% limit is conditionally gated by `enable_charging_limit && factory_version`, so **not proven active during normal Android operation**.
- **Implementation disposition:** no new charge-driving patch or binding alias before verifying 41516D silicon/datasheet and one coherent pair/thermal fail-safe owner. Plan staged read-only driver identification → variant-specific charger register support with unit tests/PM cleanup → separate paired charging manager → physical characterization before enablement. Direct policy copy or SGM41542 compatible alias is not approved.

## Shared stock metadata and DT integration

- VPU's extraction **is completed** for stock firmware: [source-hashed radio/NON-HLOS manifest](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/vpu/2026-10-11-radio-non-hlos-firmware-manifest.json) documents `vpu20_4v.mbn`, `vpu20_4v.mdt`, split `.bXX` plus `a730_sqe.fw` and `a730_zap` in `radio.img` → `SINGLE_N_LONELY` → sparse ext4. Firmware is **not** in the previously assumed super/vendor path. VPU CI [38180934057](https://github.com/Drzet/razr2022_nuc/actions/runs/38180934057) has host evidence of extraction, **not** PAS auth or native codec runtime. None of these firmware ELF physical load ranges validates PMIC parent supply lines, VPU domain votes, battery topology, or stock selected DTBO.
- Four actual source-hashed public stock Android 14 DTBOs are known, but metadata available at review exports no *per-variant* actual regulator parent properties or numeric root board/MSM IDs. PVT hwrev 0xC000 from real device and matching public build label are insufficient to select overlay or infer physical parent inputs. Boot head `6eec6ddd...` still keeps PM8350 and PM8350C RPMh UFS provider candidates and USB2 PHY graph disabled, with no guessed `vph_pwr`. This remains the correct hold. Earlier [rail-contract v2](../power_oneli_rail_contract_v2_2026-10-11.md) voltage/consumer matrix remains valid as **Motorola source values**, not a live FDT-derived parent mapping.
- Published precise metadata-only additional extraction request to shared [issue #10, comment 6119543640](https://github.com/Drzet/razr2022_nuc/issues/10#issuecomment-6119543640), for per-index 0–3 RPMh supplies/consumers, numeric board/MSM IDs and vendor_boot base, or a bounded negative result. **No separate 4.35GB download requested**.
- Posted updated Boot Power boundary to [issue #9, comment 6119544140](https://github.com/Drzet/razr2022_nuc/issues/9#issuecomment-6119544140).
- **Shared files changed:** none in kernel DTS/DT binding or coordinator main. No branch merge, no direct hardware writes. Boot retains sole shared DTS ownership.

## Validation (exact and limited)

| Result | Evidence | Interpretation |
| --- | --- | --- |
| Current round SGM/aggregator source reading | Direct GitHub `fetch_file` at immutable source SHAs above, exact oneli overlay; SGM header, driver, BQ and policy formulas checked | Research/protocol mapping only; no specific SGM41516D firmware/operating driver binary verified |
| Standalone patch isolation | GitHub `compare_commits` from baseline `a5ebb762...` to `564f2c7...`: five commits / five `drivers/power/supply/*` files; exact source blob IDs identical 5/5 to tested `3b02b11...` | Integration-ready review series **without inherited Boot**; this branch itself **not build-tested** |
| Original ARM64 object compilation | [38169526109](https://github.com/Drzet/razr2022_nuc/actions/runs/38169526109) **PASS** | `qcom_battmgr.o` and `qcom_battmgr_test.o`; **no dependency-complete normal modpost** |
| Original UML KUnit execution | [38169484188](https://github.com/Drzet/razr2022_nuc/actions/runs/38169484188) **3/3 PASS** | Real shared signed-temperature helper, not actual PMIC GLINK dispatch or Motorola charger |
| Physical stock Android source/topology | [2026-10-11 ADB capture](../oneli_stock_android14_adb_hardware_capture_2026-10-11.md), `1-0055` and `1-006b`, main+flip+combo supplies | Stock hardware observed; **no mainline oneli boot, charging or rail measurements** |
| VPU stock firmware inventory | [38180934057](https://github.com/Drzet/razr2022_nuc/actions/runs/38180934057) **PASS**, source-hashed manifest | Files actually located, but no signature/HFI acceptance, no PMIC info |

## Blockers and acceptance criteria

1. **Integrator:** review [standalone Power PR #4](https://github.com/Drzet/linux/pull/4) as a five-file baseline-derived series, cherry-pick/replay only once, record resulting SHA, and include it in the next combined Image/modules + oneli DT/schema build with dependency-complete modpost.
2. **VPU/Boot:** return per-variant source-hashed DT regulator and consumer property matrix, distinguishing fragment absence from effective FDT resolution; **no oneli parent supply patch without evidence**.
3. **Power:** obtain exact SGM41516D driver/variant (or defensible datasheet proof of register-specific behavior) and paired-load failsafe semantics before code; keep generic per-chip support separate from Motorola manager. Mainline support may report batteries *read-only* before charger writes are permitted.
4. **Hardware phase:** runtime register and voltage/current polarity readings, thermal sensor/external NTC provenance, charger CE/load switch sequence, battery isolation, suspend/off mode and negative-temperature behavior. Device currently unavailable. Stock Android manufacturer/model string cannot substitute for part-read and PN revision validation.
