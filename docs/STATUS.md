# Project status

Updated: 2026-10-11, first subsystem review. **The phone is unavailable; work proceeds in GitHub with suitable generic emulation planned.**

The clean baseline build passed. No submitted subsystem patch has recorded build validation in this review, and no hardware result is claimed. Read [review and next assignments](NEXT_TASKS.md) for findings, acceptance criteria and deferred physical tests.

| Workstream | Research / implementation | Build evidence | Next action |
| --- | --- | --- | --- |
| Baseline CI | Upstream `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` | [ARM64 Image/dtbs passed](../tests/results/2026-10-11-baseline-ci.md); no modules/schema checks | Add exact subsystem SHA, module and schema validation |
| Boot | [UART/CI/Power follow-up](handoffs/2026-10-11-boot-followup.md), [full static reserved-memory audit](oneli_reserved_memory_audit_2026-10-11.md). Branch `razr/boot` at [`3825dc6`](https://github.com/Drzet/linux/commit/3825dc6afb0f5e102845b32811ce0f518c0b4bbf); UART parent and QUP0 votes fixed; four disabled UFS RPMh rails staged | [Run 38164378662](https://github.com/Drzet/linux/actions/runs/38164378662): oneli DTB compile and changed ARM/TLMM `dt_binding_check` stages passed; broader `dtbs_check` still to verify. [New rail commit run 38164785277](https://github.com/Drzet/linux/actions/runs/38164785277): final result pending | Inspect CI logs and resolved FDT, review rail parents and stock boot/DTBO; USB/GPU proposals pending |
| GPU | [Handoff](handoffs/gpu-2026-10-11.md); chip-ID patch `4955f07a94ea3c51e423e34d819ac3f76f1c9d37` | Not recorded | Compile MSM module; audit reused profile and OPP replacement |
| USB / Type-C | [Handoff](handoffs/usb_2026-10-11.md), [investigation](usb_oneli_investigation_2026-10-11.md); PHY binding patch `0119d73b40bed1041278cf9307bdec9c17880618` | Not recorded | Check schema; audit repeater and PS5169 prerequisites |
| VPU | [HFI audit](handoffs/2026-10-11-vpu-hfi-audit.md); branch remains baseline | No implementation to build | Reproducible protocol audit, public firmware inventory, platform resource matrix |
| Power / charging / thermal | [Updated handoff](handoffs/2026-10-11-power-oneli.md), [rail/Boot proposal](power_oneli_regulators_2026-10-11.md), [GLINK/dual-battery/thermal audit](power_oneli_charging_protocol_2026-10-11.md); no power-specific kernel patch | Source match: 8 common opcodes, 41 property IDs; six synthetic fixture tests reproduced; no kernel/DT/schema build | Boot review of disabled rail providers, source-backed parents and UFS wiring; keep charger writes and thermal enablement deferred |
| DisplayPort | [Pinned vendor AUX trace + software truth table](displayport_oneli_aux_routing_2026-10-11.md), [updated handoff](handoffs/2026-10-11-displayport-oneli.md), [deferred dock procedure](../tests/procedures/2026-10-11-displayport-dock.md), [USB/Boot coordination #3](https://github.com/Drzet/razr2022_nuc/issues/3); kernel branch remains baseline | 13/13 GPIO/mux plus 10/10 baseline graph pinned-source assertions passed; no kernel implementation/DT schema/phone tests | Identify GPIO-SBU switch IC/binding and obtain USB connector/PS5169/Power prerequisite commits; Boot to integrate shared DP DTS once supportable |

## Evidence rules and open decisions

Researched, implemented, build-tested and hardware-tested are separate evidence fields. Source compatibility and compilation do not establish operation on this phone. All six subsystem hardware statuses are **deferred: device unavailable**.

Actual installed firmware and board revision are unknown. A publicly obtainable stock image may supply a reference for offline work, but must not be described as the phone's installed image. Firmware loading, electrical behavior and real performance remain physical-test blockers.

No integration commit or validated phone boot-image recipe exists. Boot owns shared DT changes. VPU platform strategy and the unidentified/uncertain USB/AUX components require further source evidence. See NEXT_TASKS.md for bounded deliverables.

Handoffs remain historical snapshots. Statements about missing Boot commits or unavailable build infrastructure in earlier handoffs are superseded by this review. Documentation imports do not integrate kernel changes.
