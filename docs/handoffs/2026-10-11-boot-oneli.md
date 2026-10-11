# Subsystem handoff: Boot / SM8475 / Motorola oneli

- Date and originating chat: 2026-10-11; Linux on Motorola razr 2022 project, dedicated Boot chat.
- Repository / branch / exact commit: `Drzet/linux`, `razr/boot`, **`cb9105ebeb9485e31d044d4fa69396b415523669`**.
- Upstream baseline SHA: **`a5ebb76233b79db01e82e061173cb73c6d2b5c6b`**.
- Required board-support and other subsystem SHAs: boot itself is based solely on the upstream SHA; **none** from GPU/USB/VPU/power. Future subsystem work should depend on the exact boot commit above or a later reviewed boot commit.
- Evidence stage: **researched: yes; implemented: yes; build-tested: no; hardware-tested: no**.

## Changes and provenance

Read `AGENTS.md`, `docs/STATUS.md`, `docs/WORKFLOW.md` and `docs/sm8475_baseline_comparison_2026-10-11.md` before implementation. Used the structured `docs/razr2022_native_linux_hardware_database_2026-10-11.json` and its newer focused audit as primary board evidence.

Provenance (source revisions fixed):
- Mainline baseline: `Drzet/linux` at `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- SM8475 community reference: `sm8450-mainline/linux` at `bf1d29fced6e156dd6090a9b6600a8c44259c114`; `arch/arm64/boot/dts/qcom/sm8475.dtsi`. Attribution retained.
- Motorola hardware/board DT: `MotorolaMobilityLLC/kernel-devicetree` at `90fa7be1db5bd47202673d4431408659149a7359`; `qcom/cape.dtsi`, `cape-moto-oneli-base.dts`, `cape-v2-moto-oneli-base.dts`, `cape-oneli-pvt-overlay.dts`, `cape-reserved-memory.dtsi`, `cape-moto-common-overlay-base.dtsi`.
- Motorola Cape TLMM driver: `MotorolaMobilityLLC/kernel-msm` at `9511d6b2dc469e5bd836992e3bdd6d19ace112e0`; `drivers/pinctrl/qcom/pinctrl-cape.{c,h}`.
- Baseline Linux `pinctrl-sm8450.c`, SM8450 DTS, current PHY and ARM/DT bindings compared at upstream SHA.

Sequential boot-branch commits:
1. `8c0ac0714073eaf78eda13483e5ec03b2c7cba34` — add reconciled `sm8475.dtsi` layered on upstream `sm8450.dtsi`; use current exact SM8475 clock-controller and USB3/DP PHY compatibles; replace SM8450 UFS PHY with SM8475 PHY at `0x01d80000` while **preserving required `UFS_PHY_GDSC` power-domain relationship**; adjust community UFS clock limits; provisionally add TLMM two-compatible fallback. The initial PHY/controller remain disabled absent board regulators.
2. `ea40f45c27df98fe28cb3236673acef614d4905b` — add minimal `sm8475-motorola-oneli.dts` and PMIC includes, board identification, diagnostic `uart7`, documented oneli ADSP `0x85700000` / `0x02800000` and video `0x9fd00000` / `0x00700000` reservations. Remove inherited SM8450 RMTFS node because its `0x9fd00000` address conflicts with Motorola oneli video reservation. Do **not** invent a replacement RMTFS address.
3. `2c156692d460bfa7c5ed6ce20cfebcc5683240f1` — register `sm8475-motorola-oneli.dtb` in ARM64 Qualcomm DTB Makefile.
4. `8820d412d149708f0b7fc58eb4b6a2a4b0dd8e71` — document `qcom,sm8475-tlmm`, `qcom,sm8450-tlmm` fallback in TLMM binding.
5. `cb9105ebeb9485e31d044d4fa69396b415523669` — document `motorola,oneli`, `qcom,sm8475` board compatible in ARM Qualcomm binding.

**TLMM compatibility assessment:** Motorola Cape and upstream SM8450 have the same 210 GPIOs plus special groups, identical PDC wake mapping, and an equivalent TLMM register base after Motorola's `0x100000` pin-register offset. Full mux-function lists differ, including Cape's GPIO98 `pll_clk` option, plus naming/index distinctions for other functions. **[INFERRED]** Mainline SM8450 TLMM data are provisionally appropriate for initial GPIO/UART boot diagnostics; this is **not** a verified complete SM8475 TLMM driver and must be revisited before other pinctrl clients are enabled. We deliberately did not misrepresent a stand-alone `qcom,sm8475-tlmm` as supported by mainline.

**Board identification:** Motorola PVT overlay identifies `moto,oneli` and a specific board-id `<0x45 0xC000>`, but the tested handset's hardware revision and actual bootloader-selected DTB are unknown. **[INFERRED]** Canonical upstream compatible is `motorola,oneli`. Do not select a PVT board-id or runtime memory layout based solely on this reference.

**Diagnostics:** Motorola Cape references serial address `0x0099c000`, matching mainline `uart7`. The DTS enables it and sets `stdout-path`. **[INFERRED]** The UART signal is physically usable on the target unit; wiring and output have not been tested.

## Shared files and integration

Boot owns the following shared kernel files on `razr/boot`:
- `arch/arm64/boot/dts/qcom/sm8475.dtsi`
- `arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dts`
- `arch/arm64/boot/dts/qcom/Makefile`
- `Documentation/devicetree/bindings/pinctrl/qcom,sm8450-tlmm.yaml`
- `Documentation/devicetree/bindings/arm/qcom.yaml`

No other subsystem branch was merged or modified; shared baseline SHA was not changed. GPU/USB/VPU/power chats should propose their requested board and SoC DT fragments to Boot, **not independently edit these shared DTS files**.

Integration order: take the exact Boot head above first (review the five commits), then apply reviewed individual subsystem driver/binding commits and incorporate their shared DT proposals in separate Boot commits before an integration build. Record any cherry-picked SHA changes.

Deliberately deferred:
- USB owner: SM8475 eUSB2 PHY and NXP repeater `0x4f`, required `vdd` and `vdda12` rails, USB role/orientation, PS5169 redriver and current DWC3 graph; inherited SM8450 high-speed PHY remains disabled. Community's old wrapper/child USB node must **not** be copied to current mainline.
- GPU owner: replace inherited SM8450 OPP table atomically with a validated SM8475 table and confirm firmware/voltage operating points; do **not** append community OPP entries. GPU stays disabled.
- VPU owner: request shared VIDEOCC/VPU DT changes through Boot after firmware/HFI and Iris support established.
- Power owner: supply/regulator and battery policy; supply phandles required to safely enable UFS/eUSB and other consumers.

## Validation

**Performed:** readback of boot head from GitHub confirmed `cb9105ebeb9485e31d044d4fa69396b415523669`; readback of committed source files and 10 static source-level assertions passed (UFS address and power domain, supported TLMM fallback and binding, exact USB3/DP compatible, ADSP/video reservations, conflicting RMTFS deletion, board identification, single DTB Makefile entry and UART7 choice). These are text checks only, **not** device-tree compilation, schema validation or device boot.

**Not performed:** ARM64 cross-build, `dtbs_check`, compiled DTB phandle and reserved-memory validation, images, flashing, actual UART log, boot, UFS or USB probe. Existing clean-baseline attempt `tests/results/2026-10-11-baseline-build.md` failed due to unavailable AArch64 cross-toolchain/flex/bison and package-install environment, not demonstrated source defects. See `docs/BUILD_CI.md` for baseline-only GitHub Actions; that workflow does not yet build this Boot branch.

Actual Motorola firmware build, board revision, live Android FDT/DTBO, boot image parameters and memory map: **not yet recorded**.

## Blockers and next test

1. On an ARM64-capable CI runner check out `Drzet/linux` at exactly `cb9105ebeb9485e31d044d4fa69396b415523669`, build `sm8475-motorola-oneli.dtb` and run applicable DT schema checks. Acceptance: DT preprocessing, compilation and schema validation succeed with captured versions/logs, or specific failures are recorded and corrected.
2. Read the target phone's actual hardware revision, firmware ID, selected DTB/DTBO, memory and reserve maps **without reflashing**. Acceptance: documented live evidence, including RMTFS address and UART availability. Reconcile bootloader-selected compatible and carveouts against the board DTS before any boot attempt.
3. Incorporate vetted power/UFS/USB proposals as individual commits; validate a reversible non-destructive initramfs boot with useful diagnostics. Acceptance: retained UART/pstore/kernel logs at exact build and firmware versions. No native-boot success is claimed here.
