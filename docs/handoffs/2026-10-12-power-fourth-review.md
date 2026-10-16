# Power fourth coordinator handoff: PVT stock USB rails and minimal reporting holds

- **Date/originating chat:** 2026-10-12, Power fourth-review assignment. This handoff records the already-committed [PVT USB supply audit](../power_oneli_pvt_usb_supply_audit_2026-10-12.md) and remaining read-only/battery gating decisions.
- **Project:** `Drzet/razr2022_nuc`, assigned `razr/power`; audited branch head prior to this handoff: `0fd276513f4cb500ead5aded541efad9ed8b3e61`. The audit file is present at that head (blob `1b20a999d5dfef0431753c71a886f5cf7ba63544`). This handoff commit will advance that branch. No coordinator aggregate files edited.
- **Kernel upstream baseline:** `Drzet/linux@a5ebb76233b79db01e82e061173cb73c6d2b5c6b` unchanged.
- **Power temp series:** standalone `Drzet/linux@564f2c7df60316db86e36d7267ddadf07bc32b7e` (kernel PR #4), source-identical 5/5 changed file blobs to the original ARM64-object/UML-tested Power patch `3b02b11bc5abdc5c453fa4af16b71bd8e44c2056`. This round did not change kernel sources.
- **Required Boot staging:** `Drzet/linux@525b504b82dbca593a9a697af9be63f53915e0a3`. Boot alone owns shared oneli DT. Dependencies: Boot effective FDT/variant comparison before any device enablement; USB owns NXP/PS5169 driver reset/enable, error/retry and PM logic; coordinator owns the combined kernel Image/modules+ordinary modpost.
- **Stages:** stock raw-property and binding **researched + SHA-validated**; prior temperature patch **implemented + earlier tested objects/UML**; full combined link **not tested**; native oneli power, charging or USB operation **not tested**.

## Stock six-FDT evidence and exact consumer references

Accepted shared VPU [workflow run 38220276125](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125) produced artifact `11734430639`, artifact ZIP SHA-256 `485ff37b87cff2e6432928cfd4c0d4168bb3c10af163f6e68b6adfba35a528ae`. Independently read and SHA-256-checked its 15,862,099-byte `stock-per-fdt-property-export.json`: `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`. It inventories four independent DTBOs and two vendor_boot base FDTs; reference index 3 board ID `<0x45 0xc000>` matches observed PVT hwrev **but active runtime overlay selection is unproven**. Base candidates MSM530 and MSM540 independently agree on regulator values. No stock ROM rescanning needed.

Using *PVT overlay* named `__fixups__` plus base `__symbols__`, not numeric `0xffffffff` placeholders or heuristic edges:

| PVT consumer | Original stock supply property | Symbolically resolved base provider | Base voltage limits; stock initial vote |
| --- | --- | --- | --- |
| NXP eUSB2 0x4f | `vdd18-supply` | PM8350 S10B, `rpmh-regulator-smpb10/regulator-pm8350-s10` | 1,800,000..1,800,000 µV; 1,800,000 µV |
| NXP eUSB2 0x4f | `vdd3-supply` | PM8350 L2B, `rpmh-regulator-ldob2/regulator-pm8350-l2` | 2,700,000..3,300,000 µV; 3,072,000 µV |
| PS5169 0x30 | `vcc-supply` | PM8350 S10B | 1,800,000..1,800,000 µV; 1,800,000 µV |
| PS5169 0x30 | `vio-supply` | PM8350C L8C, `rpmh-regulator-ldoc8/regulator-pm8350c-l8` | 1,800,000..2,000,000 µV; 1,800,000 µV |

All provider node paths are under `/soc/rsc@17a00000/`. Four overlays favor NXP at 0x4f, explicitly disable Diodes at 0x6c; PS5169 at 0x30 is source `ok`. Local status/source defaults do **not** prove electrical power, physical chip population or actual variant selection. PVT does not justify importing variant A100's extra PM8010 i/j regulators.

## Input-parent supply audit: no speculative wiring patch

**Consumer provider identity is now resolved, but each regulator's own upstream electrical input remains unverified.** Mainline `qcom,rpmh-regulator.yaml` identifies valid *PMIC input-group property names*: S10B `vdd-s10-supply`; L2B `vdd-l2-l7-supply`; L8C `vdd-l2-l8-supply`; PM8350C BOB `vdd-bob-supply`. The SM8450 HDK ties S10B to artificial fixed `vph_pwr=3.7V` and L2B/L8C to PM8350C BOB. Those are **[INFERRED] oneli possibilities only**, *not* stock-proven input phandles or smartphone battery-bus voltage.

The two stock base FDTs independently show a PM8350C BOB output (3,008,000..3,960,000 µV, init 3,296,000 µV) and PM8350 S12B (1,224,000..2,040,000 µV, init 1,256,000 µV). Their existence does not prove an input connection to L2B/L8C; no export-backed oneli `vdd-l2-l7-supply`, `vdd-l2-l8-supply` or `vdd-s10-supply` parent-edge claim is accepted. Keep Boot's RPMh providers disabled and do not copy HDK `vph_pwr` or add guessed input phandles.

**Proposed Boot contract, disabled until reviewed:** if staging the consumer supply graph, add disabled-provider child labels for PM8350 smps10/S10B fixed 1.8V, PM8350 ldo2/L2B allowed 2.7..3.3V and PM8350C ldo8/L8C allowed 1.8..2.0V. The downstream `qcom,init-voltage` vote is **not** a standard mainline `regulator-min/max-microvolt` requirement by itself. USB and Boot should use the four resolved symbolic provider references without inventing PMIC input parents or enabling consumers. S10B also supplies flip charger/fuel gauge I²C; it does not imply active charging-manager enablement.

## Standalone temperature patch, CI and read-only charging/thermal scope

- Earlier proven UML KUnit temperature arithmetic 3/3 and ARM64 objects at original Power source are accepted. Clean five-file standalone series `564f2c7d...` is integration-ready, **not yet dependency-complete combined linked**. The current Power project workflows already limit `push` to changed workflow files (and GLINK audit script for source-only audit); documentation-only commits do not trigger redundant full kernel builds. No CI edit or unchanged rerun is justified this round.
- **Minimal read-only reporting path:** review the already documented mainline `qcom_battmgr` GLINK/BATT_STATUS messages for aggregate/main battery properties; expose decoded temperature with the independently tested signed-fix helper when and only when the coordinator's integrated kernel has the required PMIC GLINK service. The stock `mmi_battery` aggregation and `flip_battery` gauge are Motorola-specific: use an exact oneli BQ27426 driver/compatible and data-format comparison before exposing a second gauge, **read-only only**, avoiding GPIO or charger register writes. No invented Linux dual-battery aggregator.
- **Explicitly disabled:** oneli SGM41516D charger (0x6b) automatic charging, Motorola paired battery policy/load switches PM8350B GPIO1/GPIO3, PM8350C charger-enable GPIO2, thermal-dependent charging, switch sequencing, USB/DP active consumers. The published separate SM8250-family `sgm4154x` driver is a comparator, **not a verified oneli source**. Masked PN similarity to SGM41542 does not establish safe variant support. An authoritative oneli chip source/datasheet, ownership/fail-safe plan and physical evidence are required before write-capable enablement. Passive reporting is not evidence that all active protocol paths are safe.

## Shared files, validation, blockers

- **Files changed in this project round:** `docs/power_oneli_pvt_usb_supply_audit_2026-10-12.md` (existing project commit); this handoff file. **Kernel source, shared DT, config, workflow or coordinator main STATUS/NEXT_TASKS:** unchanged.
- **PASS:** reusable artifact SHA-256 (both ZIP and JSON); typed FDT #3 fixups against both base `__symbols__` and provider property checks; binding group-name/source comparator; Boot board staging source inspection. These are *host/source* checks. **NOT RUN:** native overlay application via libfdt, combined kernel compile, regulator measurement, live phone test. Coordinator integration must independently record chosen commit order and new combined SHAs, not silently attribute a future build to this Power handoff.
- **Remaining external inputs:** Boot-confirmed effective stock PVT overlay/base pairing and any source-backed supply-parent edges; physical PMIC input and load-switch topology if not recoverable from bounded references; USB reset-vs-enable semantics; actual oneli SGM41516D silicon/driver. Later electrical measurements and GLINK/thermal readings on unlocked hardware are the only runtime confirmation. **Minimal UART/initramfs does not depend on enabling PS5169**; USB2 eUSB rail staging may be useful later, but its providers remain disabled pending proper board integration.
