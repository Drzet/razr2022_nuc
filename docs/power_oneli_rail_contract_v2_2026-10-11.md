# Power → Boot review contract v2: staged oneli UFS and USB rails

**Date:** 2026-10-11. **Source-evidence owner:** Power. **Shared DTS owner:** Boot. **Review baseline:** `Drzet/linux@3825dc6afb0f5e102845b32811ce0f518c0b4bbf`. **Status:** disabled-source proposal; **not** an electrical enablement authorization. Phone unavailable.

This updates the earlier [full regulator proposal](power_oneli_regulators_2026-10-11.md), explicitly separates vendor *supported ranges* from vendor *initial set points*, and audits what Boot already committed. All parent-supply wiring reconstructed from the upstream SM8450 HDK is **[INFERRED] for oneli**, even when the resource label and regulator driver are matched.

## Reviewed Boot staging, exact source

At `3825dc6afb0f5e102845b32811ce0f518c0b4bbf`, `arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dts`:

- Disabled `&apps_rsc` PM8350 `regulators-0` (`qcom,pmic-id="b"`) and PM8350C `regulators-1` (`qcom,pmic-id="c"`). Both use mainline-compatible strings and children named `ldo5`, `ldo7`, `ldo9`, `ldo10`.
- The UFS host/PHY are still disabled, and their source-backed supplies point to `oneli_l7b` VCC, `oneli_l9b` VCCQ, `oneli_l5b` VDDA-PHY and `oneli_l10c` VDDA-PLL. These correspond to downstream Cape `ufshc_mem`/`ufsphy_mem` assignments.
- Each child currently declares `regulator-min-microvolt == regulator-max-microvolt ==` the *vendor initial set-point*. That is acceptable only as a clearly inactive **review placeholder**; it does **not** represent the Motorola regulator's declared permissible range and must be reconsidered before actual rail control. `status="disabled"` on each parent provider prevents the present tree from controlling these RPMh resources.
- No parent `vdd-*-supply` phandles were staged, and there is no oneli input-supply model. This remains an **explicit unresolved prerequisite** for enabling providers. The initial DTB compilation [Boot run 38164785277](https://github.com/Drzet/linux/actions/runs/38164785277) checked only the selected ARM/TLMM schemas, not a regulator/UFS schema acceptance.

## Motorola source: ranges and current budgets

Use pinned [Cape regulator definitions](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-regulators.dtsi), [Cape common UFS / repeater consumers](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-common-overlay-base.dtsi), and [oneli-specific overlay](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-oneli-common-overlay.dtsi). All microvolt ranges below are *source values*, not a phone measurement.

| Resource / node | Motorola allowed µV | Motorola init µV | Vendor downstream direct consumers and limits | Staged upstream role |
| --- | ---: | ---: | --- | --- |
| PM8350 L5B `ldo5` | 720000–958000 | 880000 | UFS PHY VDDA-PHY; 197000 µA max | `&ufs_mem_phy.vdda-phy-supply` |
| PM8350 L7B `ldo7` | 2400000–3544000 | 2504000 | UFS VCC; 1100000 µA max | `&ufs_mem_hc.vcc-supply` |
| PM8350 L9B `ldo9` | 1200000–1304000 | 1200000 | UFS VCCQ; 1200000 µA max; vendor UFS reference clock, 100 µA max | `&ufs_mem_hc.vccq-supply`; evaluate separate ref-clock handling |
| PM8350C L10C `ldo10` | 1200000–1304000 | 1200000 | UFS PHY VDDA-PLL; 23700 µA max | `&ufs_mem_phy.vdda-pll-supply` |
| PM8350 S10B `smps10` | 1800000–1800000 | 1800000 | NXP eUSB `vdd18`; flip BQ27426 gauge and SGM41516D `vdd-i2c`; also oneli NFC 1.8V | Separate disabled USB2/battery stage |
| PM8350 L2B `ldo2` | 2700000–3300000 | 3072000 | NXP eUSB `vdd3` at vendor address `0x4f` | Separate disabled USB2 stage |
| PM8350C L8C `ldo8` | 1800000–2000000 | 1800000 | Parade PS5169 VIO; oneli references `regulator-boot-on` | USB3/DP stage only, not USB2 prerequisite |
| PM8350C L11C `ldo11` | 3000000–3000000 | 3000000 | Defined in oneli overlay, not the generic Cape regulator file; review exact panel consumer source separately | Display stage |

The source's `vdda-*-max-microamp`, `vcc*-max-microamp` are *consumer maximum-current votes*, **not measured draw or supply regulator current-limit constraints**. Use consumer binding semantics rather than blindly transferring downstream vendor-only properties.

## [INFERRED] upstream grouped parent supply relationships

The mainline `qcom,rpmh-regulator.yaml` PM8350/PM8350C schemas expect **grouped** input properties; vendors' `qcom,rpmh-vrm-regulator` resource DT nodes do not encode these mainline parent phandles. On SM8450 HDK *only*, reference upstream topology includes:

- PM8350 `vdd-l3-l5-supply` → PM8350C BOB (L5B)
- PM8350 `vdd-l2-l7-supply` → PM8350C BOB (L2B, L7B)
- PM8350 `vdd-l6-l9-l10-supply` → PM8350 S12B (L9B)
- PM8350C `vdd-l10-supply` → PM8350 S12B (L10C)
- PM8350C `vdd-l2-l8-supply` → PM8350C BOB (L8C)
- PM8350C `vdd-l6-l9-l11-supply` → PM8350C BOB (L11C)
- PM8350C `vdd-bob-supply`, PM8350 `vdd-s10-supply`, PM8350 `vdd-s12-supply` → *HDK's own* `vph_pwr`.

Motorola **does independently establish that its Cape RPMh resources include** `smpb12` (S12B source range 1224000–2040000 µV, init 1256000) and PM8350C `bobc1` (BOB source range 3008000–3960000 µV, init 3296000). **It does not establish oneli's physical supply routing into those resources.** The HDL/HDK comparator's fixed 3700000 µV `vph_pwr` is **not** a defensible model of a variable cellphone pack. Do not introduce it as an always-on fixed oneli regulator.

## Exact missing inputs before active rail enabling

1. **PMIC input topology:** physical PM8350/PM8350C LDO and SMPS inputs, including the L5B/L7B BOB, L9B/L10C S12B, and S10B source assignments. Need oneli/stock board schematic, credible populated-board DT/supply references or later physical evidence. Mainline HDK parent grouping is **[INFERRED]** only.
2. **Battery-side source and nominal voltage:** do not assert fixed `vph_pwr`. PMIC resource names and RPMh capability do not reveal charger/power-path wiring. Oneli's main + flip battery partition and current sense policy remain unported.
3. **UFS operating set-point and load:** vendor init entries are not full range. Validate what UFS PHY/host binding and silicon operating constraints permit at boot, reconcile UFS ref-clock treatment, and preserve `&ufs_mem_hc` `UFS_PHY_GDSC` power domain.
4. **USB repeater identity and sequencing:** vendor source establishes NXP `0x4f`, 1.8V S10B, 3.07V L2B, PM8350C GPIO7 reset and vendor override bytes `0x40=0x06`, `0x22=0x07`, `0x64=0x08`; it does **not** independently prove PTN3222 model compatibility. USB owner to supply driver contract. No active repeater node now.
5. **PS5169 and Type-C:** L8C is attributable to PS5169 VIO, but VCC, reset/enable, orientation and connector graph require USB/DP resolution. Do not tie external DP availability to USB2 readiness.
6. **Populated PCB revision, installed firmware and RPMh owner:** unknown without hardware. Public stock is a reference, never the live phone's identity.

## Boot acceptance and proposed action

- **Immediately:** keep staged UFS, RPMh providers and USB consumers disabled. Include this contract in Boot handoff and use the broader RPMh regulator/UFS schema test on the **current Boot head**. The rail review does not require Power to rebase over Boot's UART fixes.
- **Next independent Boot source patch:** optionally revise the disabled regulator child constraint ranges to explicit Motorola min/max values, annotating set-point separately in prose. That is review-only and not an enablement signal; compare binding rules and compiled FDT output first. The source voltage permissions alone are **insufficient** to authorize power-on.
- **Next USB2-first patch:** stage disabled S10B/L2B providers and eUSB consumer phandles only if the binding, reset ownership and exact driver compatible are independently supported. Ask Power before connecting charger-controlled consumers.
- **Later hardware validation:** measured rail status/voltage under read-only UFS boot, battery and external power source state, current/thermal sensor quality, suspend behavior and fault handling.

**Validation for this document:** cross-checked the exact Boot DTS via GitHub at `3825dc6...` and pinned Motorola Cape sources. No modification to Boot shared DTS; no compile/schema/electrical result is claimed by this contract. Consuming owner: Boot, with USB informed of S10B/L2B ownership.
