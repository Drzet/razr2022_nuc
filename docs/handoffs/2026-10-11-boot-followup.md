# Subsystem handoff: Boot follow-up, UART/DT validation/memory

- Date and originating chat: 2026-10-11, Boot chat following coordinator `docs/NEXT_TASKS.md` at `8dbf44ee4ca5fc096dbf740b0ce8c210723a3736` and `AGENTS.md` at `06f6c1e282b5fca83a144dc414c313b0be79cbc4`.
- Repository / branch / exact commit: `Drzet/linux`, `razr/boot`, **`3825dc6afb0f5e102845b32811ce0f518c0b4bbf`** (after disabled UFS power proposal).
- Upstream baseline: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- Required board-support SHA: previous Boot head `cb9105ebeb9485e31d044d4fa69396b415523669`. Other subsystem dependency SHAs: **none integrated**; GPU `4955f07a94ea3c51e423e34d819ac3f76f1c9d37` and USB `0119d73b40bed1041278cf9307bdec9c17880618` remain on their branches.
- Evidence: **researched yes; implemented yes; DTB-compiled yes (run below); binding schema compilation yes; hardware-tested no**. The complete DTB schema stage for run 38164378662 remained in progress at this handoff update; no unobserved results are claimed.

## Changes and provenance

1. Kernel [`cbde49d927478decd6d608a309a7d7482992f776`](https://github.com/Drzet/linux/commit/cbde49d927478decd6d608a309a7d7482992f776): in `sm8475-motorola-oneli.dts` enable `&qupv3_id_0`, disabled by inherited `sm8450.dtsi`, so ordinary device-model enumeration can reach enabled `&uart7`. Override UART7 interconnect references to QUP0, correcting inherited QUP2 votes. Existing `GCC_QUPV3_WRAP0_S7_CLK` and `qup_uart7_tx`/rx on GPIO27/26 agree with mainline QUP0 topology and Motorola Cape pinmux. Motorola source for selected UART: `kernel-devicetree` `90fa7be1db5bd47202673d4431408659149a7359` `qcom/cape.dtsi` `stdout-path = /soc/qcom,qup_uart@99c000`. [INFERRED] Physical retail-board UART signal is accessible.
2. Kernel [`4c35d719bdcdae1dd47daeed8252e60212a7ae47`](https://github.com/Drzet/linux/commit/4c35d719bdcdae1dd47daeed8252e60212a7ae47): add branch-specific `.github/workflows/razr-oneli-dt.yml`. Kernel changes remain only in `razr/boot`; master/baseline unchanged.
3. Kernel [`e664c44e48f1011b0705f42fdd63b61e69f90b9d`](https://github.com/Drzet/linux/commit/e664c44e48f1011b0705f42fdd63b61e69f90b9d): fix Ubuntu dependency name `device-tree-compiler`.
4. Kernel [`a04bd3d934de88c7024c35991681d5b09e9ff6bd`](https://github.com/Drzet/linux/commit/a04bd3d934de88c7024c35991681d5b09e9ff6bd): fix kernel ARM64 Makefile relative DTB target, `qcom/sm8475-motorola-oneli.dtb`.
5. Project [reserved memory report](../oneli_reserved_memory_audit_2026-10-11.md) at coordinator commit `7db0661b90f23d25814bf2e4d9c9415ccf67c1ff`. Compared **all 40** inherited static reserved regions with **32** active Motorola Cape entries plus oneli remaps; effective projected **39** entries have **zero** interval overlaps in textual source analysis. Full inventory and discrepancies documented. No actual stock DTB/DTBO extracted or host/device boot attempted.

6. Kernel [`3825dc6afb0f5e102845b32811ce0f518c0b4bbf`](https://github.com/Drzet/linux/commit/3825dc6afb0f5e102845b32811ce0f518c0b4bbf): integrate **only electrically disabled UFS rail provider candidates** from the newly delivered [Power proposal](../power_oneli_regulators_2026-10-11.md). Two RPMh provider devices under `&apps_rsc` use documented compatible/PMIC-ID pairs `pm8350` b and `pm8350c` c, both with `status = "disabled"`; UFS regulator labels L5B/L7B/L9B/L10C are phandled to the **disabled** UFS PHY/host nodes. They have no live parent-supply definitions, by design. The exact voltage constraints are Motorola's vendor *initial* values, **[INFERRED]** as fixed candidate constraints and not electrical settings proven on oneli. No enablement of UFS or charging. No USB or GPU shared-DT proposal accepted yet, since eUSB repeater identity/driver/binding and GPU OPP review remain unresolved. Kernel CI for this commit: [run 38164785277](https://github.com/Drzet/linux/actions/runs/38164785277) (status must be checked before claiming results).

## Shared files and integration

- Boot-owned board file modified (UART and separate disabled RPMh UFS rail proposal): `arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dts`.
- Branch-specific CI: `.github/workflows/razr-oneli-dt.yml`.
- No upstream baseline, GPU, USB, power, VPU, DisplayPort or integration branch changes. No kernel subtree imported.
- Existing boot-handled shared `sm8475.dtsi`, ARM and TLMM bindings are unchanged in this round.
- Separate review-only rail commit is applied **after** UART correction and workflow fixes, without cherry-picking the Power branch or enabling any powered consumer.
- USB/power/GPU proposals remain contingent on complete rail IDs/voltage constraints, NXP repeater silicon/reset identity, exact SM8475 GPU OPP corner validation and reviewable proposed node fragments. Existing USB PHY binding commit is separate and **not merged**; avoid copying obsolete DWC3 wrapper or inventing a repeater compatible. Incomplete consumers remain disabled.
- `razr/integration` remains untouched; cherry-pick mapping: not applicable.

## Validation

- [Run 38164147773](https://github.com/Drzet/linux/actions/runs/38164147773) at `4c35d7`: failed before config, apt could not find package `dtc`. Fixed by `e664c44`.
- [Run 38164252342](https://github.com/Drzet/linux/actions/runs/38164252342) at `e664c44`: dependency install and ARM64 defconfig passed, attempted `make O=out ... arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dtb`; failed in Makefile because path was duplicated. This was a CI target invocation error, **not** a source compilation error. Fixed by `a04bd3`.
- [Run 38164378662](https://github.com/Drzet/linux/actions/runs/38164378662) at exact `a04bd3d934de88c7024c35991681d5b09e9ff6bd`: checkout, dependency install, `make O=out defconfig`, `make O=out -j$(nproc) qcom/sm8475-motorola-oneli.dtb` **passed**. Targeted `make O=out DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/qcom.yaml dt_binding_check` and corresponding TLMM schema command **passed**. The separate DTB schema validation stage was still in progress at handoff creation; its final status, warnings, artifact IDs and tool versions must be read from the completed run rather than assumed.
- All CI runs are Linux Ubuntu 24.04 with AArch64 GCC and Python dtschema installed during the workflow. Exact resolved versions/config/commands are in the run evidence; no pinned container digest.
- No kernel `Image` or modules built in these runs. No on-device test, UART output or physical evidence.

## Blockers and next test

1. Review completed `38164378662` job conclusion, logs and uploaded evidence. Correct any DTB binding warnings introduced by oneli; differentiate pre-existing SM8450/baseline warnings.
2. Re-run a targeted compiled-DTB check of **all applicable** bindings and extract the flattened `reserved-memory` to audit overlaps, labels and phandle references. Static interval review alone does not establish a completely resolved FDT.
3. Public oneli stock archive catalogued in the memory report, but its contents/header version/DTBO remain unread and un-hashed. Select/extract a specific public reference, record source and hash, and inspect boot/vender_boot/dtbo offline before candidate packaging. Do not treat public image as the installed version.
4. With hardware unavailable, refrain from claiming UART signal access, UFS, USB enumeration or device boot. Incorporate peer subsystem node proposals on Boot only after supply/driver/binding review.
