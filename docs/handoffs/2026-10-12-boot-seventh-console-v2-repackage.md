# BOOT handoff: seventh-round console-summary v2 one-time host refresh

- **Date / chat:** 2026-10-12, BOOT continuation of seventh coordinator review.
- **Source branch:** `Drzet/razr2022_nuc:razr/boot`.
- **Exact tested packaging source:** `0b2ee0709987831ede07a1494117c7abd3485075`.
- **Accepted kernel and DT unchanged:** `Drzet/linux:razr/integration@2b5acf108ae37040ac1e652e029bb37f5609e886`, `Image` SHA256 `3a8fa9620e0fc8de68ce8db45dacdfd811a2ba2c9718f9cddee3893ec9af0939`, mainline oneli DTB SHA256 `d3c9abcea9950200babbcf6c979073dc94c6af5cac68578540ad570db4a14a03`.
- **Upstream baseline:** `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- **Evidence levels:** v2 Userspace diagnostic output tested in QEMU; BOOT unsigned AOSP v4 image **host-tested**; Motorola phone hardware **not tested**.

## Changed input and source provenance

Userspace completed the independent seventh-review console-summary fix: actual diskless test [run 38317559417](https://github.com/Drzet/razr2022_nuc/actions/runs/38317559417) at exact Userspace commit `64b7a3358d3250dbe92518e548517ddfd038b149`. Its 15/15 artifact checksums pass. Downloaded Userspace v2 artifact **11777077254**: ZIP SHA256 `3625ebfdaf83edd4628791f8a818ecaea357aeabcb354b062e00911124f4ed76`. The raw cpio SHA256 `cf00eb88014e177a48164f5d70ee8ee277ebe5936a8808bf80885ae8818a408e`; gzip cpio SHA256 `ccd4c96b2cb05ff695175af8625dbbf8fe2f822d32fafaa5ae930e7796b7a93b`; embedded `/init` SHA256 `d23e8bd9662a91d9cd1b6edaa1db49ed5ec8ea6aec70f9763cddab4a6e8989e9`. Both positive and negative QEMU console logs include **one nonempty summary line between PROBE_ERRORS_BEGIN/END**. The marker `RAZR_NATIVE_PROBE_ERROR_FIXTURE_CI_ONLY` is supplied through QEMU's test command line and is **not evidence of an actual oneli probe failure**.

For this *single* changed-payload-only repackaging, BOOT added [input lock](../../configs/oneli-native-host-console-v2-input-lock.json), [bounded wrapper](../../scripts/repackage_oneli_native_console_v2.py) and [isolated CI](../../.github/workflows/boot-native-console-v2.yml). Original BOOT v1 packer blob `8221b23255489f7e94d3b267106c36db02c31df5` and accepted vendor_boot v1 remain pinned. This workflow **does not regenerate or publish vendor_boot**; the v1 file is consumed and independently SHA verified byte-for-byte against a recomputed identical vendor layout. The new generic v2 gzip only replaces the boot-v4 ramdisk section.

## Validation / exact artifact

First new run [38318193635](https://github.com/Drzet/razr2022_nuc/actions/runs/38318193635) **failed** after successful input downloads/checksums due to a wrapper bug passing a filesystem Path instead of bytes to SHA256. Corrected at BOOT commit `0b2ee0709987831ede07a1494117c7abd3485075`. Retain this failed test in history.

**Successful [BOOT run 38318260840](https://github.com/Drzet/razr2022_nuc/actions/runs/38318260840)**, job **115039980166**, checked source commit `0b2ee0709987831ede07a1494117c7abd3485075`. All CI jobs passed: pin accepted kernel+v2 payload+v1 vendor inputs; verify their hashes; check v2 `/init`, actual QEMU probe fixture and hold logs; pack only a changed boot image; inspect with BOOT parser; independently unpack/repack with pinned AOSP tools and compare section sizes/hashes, command line and signature policy. No kernel or Debian rebuild.

- Artifact **11777433748**, `oneli-native-boot-console-v2`, independently downloaded ZIP SHA256 **`c2f7353a652d60c4d3e0282dfa101ab421d1dfd605c571c509194f25b26cb00b`**, **5/5 internal SHA256SUMS passed**.
- `boot-console-v2.UNSIGNED.img`, 53,395,456 bytes, SHA256 **`1e00e4f998f5001bc08d9e0d4e4465664100194ce211cd9eb8b329612b5563bb`**. Embedded kernel identical; generic gzip changed to v2 sha `ccd4c96b2cb05ff695175af8625dbbf8fe2f822d32fafaa5ae930e7796b7a93b`. OS version field 0; no boot-v4 signature; empty cmdline; Android image structure only.
- Previous v1 `boot-candidate.UNSIGNED.img` remains accepted for its former payload and untouched: SHA256 `f47686e4cff28d9491ece814dd6c91c6f22eab32b3061a46f9bb935ae1fcda74`.
- **No new vendor_boot output.** The exact existing v1 vendor image SHA256 `1b4f6379b41e22735176bf63c725d3455d47c7b510f29d0de62b408da5f47572` remains the paired *structural* host reference. Neither v1 nor v2 is native-phone accepted or AVB signed.
- Machine output artifact includes `boot-console-v2-inspection.json`; durable [result record](../../tests/results/2026-10-12-oneli-native-console-v2-repackage.json) with all identities and distinct historical failure.

## Shared files, dependencies and next action

Only BOOT-owned project files are touched, no kernel/DT/schema/baseline edits, no `razr/integration` movement, no coordinator STATUS/NEXT_TASKS changes. Separate seventh BOOT decision report [native loader/output decision](../oneli_native_loader_output_decision_2026-10-12.md), machine [readiness record](../../configs/oneli-native-loader-readiness-v1.json) and [handoff](2026-10-12-boot-seventh-loader-output.md) establish the actual remaining oneli unknowns.

**Phone readiness remains BLOCKED:** actual Motorola bootloader Image base/relocation, bootloader-supplied RAM, DT/DTBO selection, generic/vendor ramdisk and cmdline priority, observed physical UART/early diagnostic route, AVB/rollback and independently verified reversible restoration. The *only* next physical acceptance path requires evidenced loader placement and a safe observable recovery-capable experiment; no flash command is supplied or approved. Do not repeat unchanged host image builds or generic ROM scans. Coordinator reviews these BOOT artifacts and is sole owner of any aggregate readiness change.


## Current BOOT assignment: 2026-10-15 schematic-to-board review

**Assignment:** current main `docs/NEXT_TASKS.md` at coordinator main revision `b525b6ab2bd399810d70365d048bc46cfda5f98e`. Independent source-only review while USB reviews PTN3222BUK. **No DTS, driver, kernel or artifact change**. Accepted kernel remains `Drzet/linux@2b5acf108ae37040ac1e652e029bb37f5609e886`. Reviewed exact Boot project head before this update: `3462c5e61c0defde33c49eee647064894dc5b24b`.

**Pinned, reviewable contract:** [configs/oneli-schematic-board-contract-v1.json](../../configs/oneli-schematic-board-contract-v1.json), creation commit `e7747622c90a2dce689bcb553bf258f10a7069df`. Derived input: [coordinator's schematic evidence](https://github.com/Drzet/razr2022_nuc/blob/d84b05099dd9f01e11b744503a3728ae71e70ee4/docs/oneli_schematic_evidence_2026-10-15.md), from user/auditor inspected `Schematics_256_MP_0616.pdf`, Motorola `maven.cpm` rev03. Drawing not redistributed. **Schematic-derived reference design only, exact installed PVT population and runtime unverified**. For Linux comparison: [pinned SoC DTS](https://github.com/Drzet/linux/blob/2b5acf108ae37040ac1e652e029bb37f5609e886/arch/arm64/boot/dts/qcom/sm8450.dtsi), [accepted oneli DTS](https://github.com/Drzet/linux/blob/2b5acf108ae37040ac1e652e029bb37f5609e886/arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dts), [RPMh binding](https://github.com/Drzet/linux/blob/2b5acf108ae37040ac1e652e029bb37f5609e886/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml), [driver per-rail supply names](https://github.com/Drzet/linux/blob/2b5acf108ae37040ac1e652e029bb37f5609e886/drivers/regulator/qcom-rpmh-regulator.c) and [HDK comparator](https://github.com/Drzet/linux/blob/2b5acf108ae37040ac1e652e029bb37f5609e886/arch/arm64/boot/dts/qcom/sm8450-hdk.dts).

### UART7 verdict: GPIO mux matches; source labels conflict with schematic directions

| Source | TX | RX | Functional evidence |
| --- | --- | --- | --- |
| User-transcribed reference schematic | AP **GPIO26**, ball **D24**, net `SDM_DBG_UART_TX` | AP **GPIO27**, ball **C24**, net `SDM_DBG_UART_RX` | Physical-net direction in reference drawing, not a confirmed solder-accessible pad |
| Inherited `sm8450.dtsi` pinctrl labels | `qup_uart7_tx` **gpio27** | `qup_uart7_rx` **gpio26** | **Names opposite** those signal directions |
| Accepted `uart7` / SoC TLMM | `qup7` alternate function, drive 2, bias disable **on both** pads | Same | Both GPIO26/27 are enabled for `qup7`; the group names don't program TX/RX direction, which is determined by silicon's mux role |
| Pinned Motorola `cape-pinctrl.dtsi` | `qupv3_se7_2uart`: **GPIO26/27 together**, `qup7` | No labelled pin direction | Confirms the same two-pad function, not which physical pad is a usable console receiver |

Mainline `drivers/pinctrl/qcom/pinctrl-sm8450.c` advertises `qup7` for GPIO24–27, including both reported pins. `uart7 = serial@99c000` is `qcom,geni-debug-uart`, parent QUP0 enabled, corrected QUP0 ICC links, `serial0` alias and `stdout-path=serial0:115200n8`, with built-in `CONFIG_SERIAL_QCOM_GENI=y` and `CONFIG_SERIAL_QCOM_GENI_CONSOLE=y`. **No currently demonstrated functional pinmux error.** Minimal *future* optional source clean-up: use a single oneli-local `qup7` two-pad default pinctrl state for GPIO26+27, or relabel inherited references without changing electrical configuration. Do **not** silently swap the actual pin group contents or claim UART operation. **Required device observation:** identify a real ground/pad, voltage domain and accessible UART TX receiver path; capture bytes from the controlled handoff. UART voltage/test pads remain UNKNOWN.

### RPMh regulator parent reconciliation: proposed, not applied

The driver and binding explicitly support the grouped property names below. `PM8350` means RPMh `qcom,pm8350-rpmh-regulators`, `qcom,pmic-id="b"` in accepted **disabled** `regulators-0`; `PM8350C` means `qcom,pm8350c-rpmh-regulators`, ID **c** in disabled `regulators-1`. Neither provider has parent `vdd-*-supply` inputs staged in accepted oneli DTS.

| Provider | Mainline binding property | Schematic input rail | HDK input | Decision |
| --- | --- | --- | --- | --- |
| PM8350 | `vdd-l1-l4-supply` | **S11B** | S11B | Same |
| PM8350 | `vdd-l3-l5-supply` | **S11B** | BOB | **Change source assumption** |
| PM8350 | `vdd-l2-l7-supply` | **BOB (PM8350C)** | BOB | Same |
| PM8350 | `vdd-l6-l9-l10-supply` | **S12B** | S12B | Same |
| PM8350 | `vdd-l8-supply` | **S2H** (PM8450; **not PM8350BH**) | S2H | Same |
| PM8350C | `vdd-l1-l12-supply` | **S1C** | BOB | **Change source assumption** |
| PM8350C | `vdd-l2-l8-supply` | **S1C** | BOB | **Change source assumption; L8C→S1C** |
| PM8350C | `vdd-l3-l4-l5-l7-l13-supply` | **BOB (PM8350C)** | BOB | Same |
| PM8350C | `vdd-l6-l9-l11-supply` | **BOB (PM8350C)** | BOB | Same |
| PM8350C | `vdd-l10-supply` | **S12B** | S12B | Same |
| PM8350C | `vdd-bob-supply` | **B_PLUS** | HDK `vph_pwr` (fixed 3.7V) | **Variable physical power-path; NO HDK fixed-supply copy** |

**Additional physical feeds:** PM8350 S1–S12 buck inputs and PM8350C S1–S10 buck inputs derive from `B_PLUS` in the reference drawing. Mapping requires actual regulator supply-provider ownership and cannot be replaced with `regulator-fixed` at an invented 3.7V. The BOB output `VREG_BOB` is generated by **PM8350C** and shares its variable `B_PLUS` input. The accepted oneli DTS lacks instantiated `S11B`, `S12B`, `S1C`, `S2H`, `BOB` and high-level `B_PLUS` provider phandles; **do not paste a table into DTS as if these phandles exist**.

**Consumer implications:** UFS PHY VDDA-PHY←PM8350 **L5B** now traces to **S11B** rather than HDK BOB; UFS host VCC←**L7B** traces to BOB; UFS VCCQ←**L9B** traces to S12B; PHY VDDA-PLL←PM8350C **L10C** traces to S12B. For USB and DP, the identified `PTN3222BUK` repeater gets S10B and L2B; PS5169 VCC=S10B and VIO=**L8C fed by S1C**; AUX `WAS7227Q-10/TR` VCC=L2B. Actual supply constraints and pin control belong to the separately queued USB/DP/Power agreements. **All current regulators and consumers remain disabled**.

**Battery provider/name boundary:** `PM8350BH` is the schematic main charge/bridge power-controller designation, distinct from the PM8350 (RPMh ID **b**) and PM8350C (**c**) regulator inputs, and not interchangeable with the upstream `qcom,pm8350b-rpmh-regulators` name without a part/provider audit. The user-corrected `CHG_EN` belongs to **PM8350C GPIO2 pin134**, `FLIP_BALANCE_EN_N` to **PM8350BH GPIO1 pin114**, and `FLIP_BATTPLUS_EN` to **PM8350BH GPIO3 pin139**, with R909 470kΩ pull-down and U900 WS4695C-12 bridge. **Power owner** has the queued polarity/provider/paired-pack policy task; BOOT makes no GPIO or charger DTS proposal in this round.

### Concrete next observations and stop

- **Offline source, owner Boot/Power (future assigned integration only):** decide how actual `B_PLUS` is represented without HDK's fixed `vph_pwr`, instantiate correct *disabled* PM8350/PM8350C/PM8450 RPMh producer phandles for S11B/S12B/S1C/S2H/BOB, and review cross-provider dependencies before any proposed `vdd-*-supply` patch. Check binding/schema and regulator parent/provider readiness then, not now.
- **On device, Boot/owner:** actual MBM-selected RAM map/Image load and relocation, DT/DTBO treatment (the accepted compiled DT memory remains size zero), ramdisk/command-line selection; separately physical GPIO26/27 UART output pad, voltage, accessible receiver and logs. Stock Android PVT `0xc000` plus reference schematic alone does not prove installed PCB variant or voltage/readout.
- **Test gate, Boot/device owner:** read-only bootloader capabilities and original per-slot data, credible restoration and observable diagnostic method before a separately reviewed native trial. Successful kernel entry and logs are *test outcomes*, **not pre-existing proof required to plan the trial**.

**Validation:** read-only comparison of the exact accepted SoC DTS, oneli board, pinctrl driver, RPMh binding/driver, SM8450 HDK and pinned Motorola pinmux source; grouped property names and differences checked. No changed kernel/DTS/schema source, no CI/build/QEMU replay, no physical test and no charging/power state change. Stop BOOT work here and post the exact document commit to issues #13 and #9 for coordinator review; USB's independent BUK/reset task remains active.
