# Motorola Razr 2022 (oneli) native Linux: Wi-Fi/Bluetooth source-only handoff

**Owner:** Wireless research, dedicated project/kernel branches `razr/wireless`.
**Date:** 2026-10-16. **State:** research prepared; not an integration or handset-support claim.
**Policy gate:** The current `docs/NEXT_TASKS.md` (2026-10-16 evening) has no wireless implementation assignment. No kernel/DTS/config change is authorized. Shared DTS is Boot-owned, integration Astra-owned. This report is the only wireless handoff; do not reactivate without a new coordinator assignment.

## 1. Immutable inputs and evidence priority

- Project source `Drzet/razr2022_nuc` main `4135c6de120a83a5d5ad5579d003ae0cd3858408` (`AGENTS.md`, `docs/STATUS.md`, `docs/NEXT_TASKS.md`, `docs/WORKFLOW.md`, hardware database and stock ADB report). Project wireless branch was created from that main.
- Kernel accepted integration `Drzet/linux` `2b5acf108ae37040ac1e652e029bb37f5609e886`. Kernel wireless branch was created from this exact commit and has no delta.
- Motorola stock source `MotorolaMobilityLLC/kernel-devicetree` `90fa7be1db5bd47202673d4431408659149a7359`: `qcom/cape.dtsi`, `cape-pcie.dtsi`, `cape-pinctrl.dtsi`, `cape-regulators.dtsi`, `waipio-qupv3.dtsi`, and oneli PVT/common/base overlays. This is inherited Cape Android 12-era evidence, **not** a byte-verified loaded Android 14 DTB on the handset.
- Real handset read-only ADB capture on 2026-10-11: oneli XT2251-1, PVT/`0xC000`, SM8475, stock Android 14 `U2SLS34.1-42-14-11`, kernel 5.10.233. No readable live PCI ID, BT controller version, WLAN QMI board-ID, loaded DTB, or factory calibration was captured.
- Xiaomi **product** `yzddmr6/xiaomipad-6pro-mainline` `kernel/source.json` pins `yzddmr6/linux-sm8450-liuqin` `fe81794b5e1b8a3f11a165f3acbfdb8fa671dbb3`, ancestor `a19585977c11fa662435b607cb9ff4ac7133092e`. Product reports its own client Wi-Fi and BT functioning, not an oneli test.

## 2. Radio identification and pin evidence

| Item | Strongest available evidence | Disposition |
| --- | --- | --- |
| WLAN silicon | Inherited Motorola `cape.dtsi` node `qcom,cnss-qca6490` | Source-supported family name; [INFERRED] populated oneli part; silicon revision and actual PCI IDs unknown |
| Bluetooth silicon | Motorola *separate* `bt_qca6490` node, `compatible = "qcom,qca6490"` (around line 549) | Stronger than a BT GPIO alone but still inherited vendor-DT declaration, **not** independently read HCI identity |
| WLAN transport | Vendor WLAN `qcom,wlan-rc-num=<0>` + PCIe0 interconnect; vendor PCIe RC0 at `0x01c00000` | [INFERRED] PCIe0 WLAN function; stock physical enumeration not captured |
| BT transport | `hsuart0 = &qupv3_se20_4uart`; vendor enables serial engine 20, `qcom,qup_uart@894000` in `waipio-qupv3.dtsi` | [INFERRED] BT uses the UART20 four-wire route; UART20 is enabled in inherited Cape, oneli retail connection untested |
| BT UART pins | `cape-pinctrl.dtsi` `qupv3_se20_4uart_pins`: CTS TLMM76, RTS 77, TX 78, RX 79; RX wake interrupt TLMM79 | Vendor source-confirmed pinmux; direction is SoC-side |
| Radio controls | WLAN-enable TLMM80, BT-enable TLMM81, switch-control TLMM82, XO-clock TLMM204 in **both** Motorola WLAN and BT nodes | Source-confirmed GPIO numbers; active-high operation [INFERRED] from vendor pinctrl active/sleep and upstream comparator; electrical population untested |
| PCIe host controls | Motorola `cape-pcie.dtsi` RC0 PERST TLMM94, WAKE TLMM96 | Vendor root-complex declaration; do not transplant proprietary Qualcomm controller property format |

Motorola `cape-pinctrl.dtsi` sets WLAN active GPIO80 output-high, sleep output-low; Bluetooth sleep GPIO81 output-low. All four shared control GPIOs must be owned by **one** PMU sequencer, never independently driven by BT and WLAN consumers. Xiaomi and upstream SM8450 HDK independently use the same four control GPIO numbers, but common reference design does not establish installed oneli hardware.

## 3. Reuse decision: upstream already supplies the drivers

- **Wi-Fi:** kernel `drivers/net/wireless/ath/ath11k/pci.c` already matches Qualcomm vendor `17cb`, WCN6855 device `1103`. **[INFERRED]** This could bind a QCA6490 marketed module if the physical oneli endpoint enumerates with that ID. Do not assert the oneli ID is `17cb:1103` without `lspci -nn`/sysfs or stock PCI evidence. Use `ath11k_pci` with MHI/QRTR and normal firmware loader; no new chip ID or private CNSS driver.
- **Pre-enumeration power:** kernel `drivers/power/sequencing/pwrseq-qcom-wcn.c` understands `qcom,wcn6855-pmu`, ten parent supply inputs, internal LDO0–9, shared `wlan` and `bluetooth` targets and staged GPIO/XO sequencing. Kernel `drivers/pci/pwrctrl/pci-pwrctrl-pwrseq.c` matches `pci17cb,1103`, requires an endpoint `vddaon-supply`, requests the `wlan` target and powers it **before** host enumeration. Plain PCIe activation without this pre-power consumer may expose no radio at all.
- **Bluetooth:** `drivers/bluetooth/hci_qca.c` already matches `qcom,wcn6855-bt` via serdev on Qualcomm GENI UART; `drivers/bluetooth/btqca.c` loads firmware based on controller version, firmware fallback and board ID. BlueZ then handles pairing/services; no Motorola-specific HCI rewrite is justified.
- **Binding sources:** `Documentation/devicetree/bindings/regulator/qcom,qca6390-pmu.yaml` for the PMU; `.../net/wireless/qcom,ath11k-pci.yaml` for the enumerated PCI endpoint; `.../net/bluetooth/qcom,wcn6855-bt.yaml` for the UART child. The AHB-only `qcom,ath11k.yaml` is not the PCIe endpoint binding.
- **Important pinned driver limitation:** `hci_qca.c` may fall back to legacy direct-regulator behavior if a WCN6855 power-sequencer lookup fails; this must not be taken as proof of correct shared power ownership. The pinned PMU driver also retains its existing WLAN-GPIO-state preservation workaround for PCIe link-down. Do not rewrite these generic drivers under this assignment.
- **Kernel config dependency proposal (not a committed fragment):** Qualcomm GENI serial and PMIC/RPMh/regulator providers, `CONFIG_PCIE_QCOM`, `CONFIG_PHY_QCOM_QMP_PCIE`, `CONFIG_POWER_SEQUENCING`, `CONFIG_POWER_SEQUENCING_QCOM_WCN`, `CONFIG_PCI_PWRCTRL`, `CONFIG_PCI_PWRCTRL_PWRSEQ`, `CONFIG_ATH11K`, `CONFIG_ATH11K_PCI`, `CONFIG_MHI_BUS`, `CONFIG_QRTR`, `CONFIG_QRTR_MHI`, `CONFIG_BT`, `CONFIG_BT_HCIUART`, `CONFIG_BT_HCIUART_QCA`, `CONFIG_BT_QCA`, firmware loader and cfg80211/mac80211. Confirm actual Kconfig resolution with final kernel config. Built-in vs modules depends on agreed boot/rootfs availability.

## 4. Motorola supply inventory and mapping constraint

Vendor WLAN node parent rails: WLAN AON `S2E` (PMR735A S2, 1.012–1.040 V in stock node), digital `S11B` (PM8350 S11, 0.966–1.170 V), IO `S10B` (PM8350 S10, 1.800 V), RFA1 `S1C` (PM8350C S1, 1.900–2.024 V), RFA2 `S12B` (PM8350 S12, 1.350–2.040 V), and antenna-switch `L7E` (PMR735A L7, 2.800 V). BT node separately names IO `S10B`, AON/digital/RFA-CMN/RFA-0p8 `S11B`, RFA1 `S1C`, RFA2 `S12B`, ASD `L7E`. These ranges are **vendor node source values**, not confirmed oneli runtime votes.

Upstream `sm8450-hdk.dts` provides the closest **source-supported template** for exactly the same GPIO/PMU combination. Its PMU inputs map `vddio=S10B`, `vddaon=S11B`, `vddpmu=S12B`, `vddpmumx=S2E`, `vddpmucx=S11B`, `vddrfa0p95=S11B`, `vddrfa1p3=S12B`, `vddrfa1p9=S1C`, `vddpcie1p3=S12B`, `vddpcie1p9=S1C`. **[INFERRED]** Apply this **only as a wiring review candidate**, not an accepted oneli rail map: notably Motorola WLAN calls S2E its AON supply while its BT node uses S11B for AON. Power/Boot must reconcile the distinct downstream names against actual PMU inputs and ensure real RPMh providers/parents are available before enablement. Preserve vendor antenna-switch L7E requirement for separate later ownership analysis; the upstream PMU's ten-input binding has no equivalent L7E input, so do not silently discard its potential function or invent an always-on regulator.

Upstream PMU **requires** all ten input supplies; PCI WCN6855 endpoint requires `vddrfacmn`, `vddaon`, `vddwlcx`, `vddwlmx`, `vddrfa0p8`, `vddrfa1p2`, `vddrfa1p8`, `vddpcie0p9`, `vddpcie1p8` LDO-output phandles. Upstream BT child requires `vddrfacmn`, `vddaon`, `vddwlcx`, `vddwlmx`, `vddbtcmx`, `vddrfa0p8`, `vddrfa1p2`, `vddrfa1p7` (the last remains a required, deprecated name in **this pinned binding**). Do not replace these with vendor `qcom,bt-vdd-*` properties.

## 5. Xiaomi Pad 6 Pro comparison, exact product kernel revision

| Subsystem | Xiaomi pinned implementation | Reuse for oneli |
| --- | --- | --- |
| Power | `sm8475-xiaomi-liuqin.dts`: upstream `qcom,wcn6855-pmu` and ten input regulators, GPIO80/81/82/204, internal LDO0–9 | Structure, driver and GPIO numbering reusable as an evidence-backed proposal; **PMIC parent phandles differ by board** |
| WLAN | `&pcie0`/`&pcieport0/wifi@0`, `compatible="pci17cb,1103"`, slot `reg=<0x10000 0 0 0 0>` and nine LDO supplies, `&pcie0_phy` | Topology/binding reusable **only after oneli PCI identity and PHY/supply confirmation** |
| BT | `&uart20/bluetooth`, `qcom,wcn6855-bt`, eight supplies, `max-speed=<3200000>` | UART20/pins independently corroborated by Motorola source. [INFERRED] BT compatible and 3.2-Mbaud setting until actual oneli HCI exchange/baud policy verified |
| WLAN firmware | `tools/build-liuqin-wlan.py`: combines its own `amss20.bin`, `m3.bin`, `regdb.bin`, `bd_m81gf.elf` with upstream `board-2.bin.zst`, replacing Xiaomi key `bus=pci,vendor=17cb,device=1103,subsystem-vendor=17cb,subsystem-device=0108,qmi-chip-id=18,qmi-board-id=255` | **Do not reuse Xiaomi board entry, ELF, MAC, ROM-derived runtime blobs or IDs.** Reuse only generic ath11k board-data preparation method if Motorola needs a matching key |
| BT firmware | Xiaomi stages `qca/hpbtfw20.tlv`, `hpbtfw21.tlv`, various `hpnv20*/hpnv21*` from its `BTFM.bin` | Driver filename patterns and staging design reusable; the Xiaomi bytes and chosen revisions are **not** Motorola evidence |
| Userspace identity | Xiaomi provisions per-device WLAN MAC and Bluetooth address from its persist partition before NetworkManager/BlueZ | Maintain per-device identity/provenance, but no evidence Motorola has the same persist paths, layout or byte order. Do not copy services/scripts blindly |

Xiaomi's product README claims working client Wi-Fi/Bluetooth on its tablet. That experience is useful **only as reuse feasibility evidence**, not oneli device verification or proof that any of its private patched drivers are necessary. Upstream implementation is already present in our accepted kernel. No private Xiaomi driver change has been identified as necessary for oneli.

## 6. Firmware requirements/provenance (no blobs committed)

**ath11k** requests the WCN6855 hardware-revision directory, typically `ath11k/WCN6855/hw2.0/` or `hw2.1/` with `amss.bin`, `m3.bin`, `board-2.bin`, `regdb.bin`; board calibration matching depends on enumerated PCI subsystem IDs and QMI chip/board IDs, with optional `qcom,calibration-variant`. Neither the relevant oneli hardware revision nor board key is yet identified. If only a vendor board ELF/board file exists, inspect encoding and entry keys before constructing a Motorola-only `board-2.bin`; never overwrite the Xiaomi tuple or fabricate an identifier.

**Bluetooth** pinned `btqca.c` first asks for `qca/wcnhpbtfw%02x.tlv` (WCN6855) and falls back to `qca/hpbtfw%02x.tlv`; for NVM it first tries `qca/wcnhpnv...`, then `qca/hpnv...`, with version and possibly board ID in the filename. The commonly cited `20`/`21` variants are **examples observed in Xiaomi files**, not confirmed oneli ROM values. Record HCI-reported ROM and board revisions before choosing files.

**Motorola stock provenance already located:** historical project manifest `docs/vpu/2026-10-11-radio-non-hlos-firmware-manifest.json` at project SHA `c25ff584bde73515d036de424c57e48b985ca01b` identifies the matching public `XT2251-1_ONELI_RETEU_14_U2SLS34.1-42-14-11` archive (sha256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`) and embedded `NON-HLOS.bin` (sha256 `03d37634aa39ff9af06d3b583267e6d166996c22e7b4f06b0bcb7d7b4031a1d9`). It was a limited radio/GPU/VPU inventory, **not** a comprehensive QCA6490 WLAN inventory. Historical `docs/vpu/2026-10-11-stock-filesystem-firmware-manifest.json` explicitly leaves `BTFM.bin` sparse container unpacked. Never interpret absent wireless filenames in those scoped manifests as missing firmware. Reuse cached extracted objects/CI artifacts if a coordinator later authorizes exact wireless inventory. No new ROM download, extraction, hashes of unseen blobs, or cross-device firmware redistribution was performed.

## 7. Boot-owned shared DTS integration request to Astra (NOT APPLIED)

After Astra schedules wireless work and Power confirms PMU inputs, request Boot to stage **only** the following in `arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dts` with current SoC labels, leaving default disabled until corresponding gate resolves:

1. A single root `wcn6855-pmu { compatible = "qcom,wcn6855-pmu"; }` with `<&tlmm 80 GPIO_ACTIVE_HIGH>` WLAN, `<&tlmm 81 GPIO_ACTIVE_HIGH>` BT, `<&tlmm 82 GPIO_ACTIVE_HIGH>` SWCTRL and `<&tlmm 204 GPIO_ACTIVE_HIGH>` XO; source-based pinctrl defaults; ten named RPMh input phandles as in section 4 only **after** supply reconciliation; standard PMU `regulators { ldo0..ldo9 }` with LDO labels usable by both radios. [INFERRED] Active-high GPIO polarity until electrical verification.
2. `&pcie0` and `&pcie0_phy` controller/PHY supplies, resets/clocks/pinctrl from the upstream SoC tree, with enablement only after rail review; `&pcieport0 { wifi@0 { compatible = "pci17cb,1103"; reg = <0x10000 0 0 0 0>; <nine required WCN6855 LDO-output supply properties>; }; };` **conditionally** on the physical PCI ID being verified. Oneli's vendor RC0 PERST GPIO94 / WAKE GPIO96 are source evidence, not license to override upstream controller defaults speculatively. Do not import vendor CNSS node or DMA carveout.
3. `&qupv3_id_2 { status = "okay"; };` for the upstream UART20 parent; `&uart20 { status = "okay"; bluetooth { compatible = "qcom,wcn6855-bt"; <eight required LDO-output supply properties>; max-speed = <3200000>; }; };` after confirmation of Bluetooth family/baud and pinmux. The accepted oneli DTS currently enables only QUP wrapper 0 for UART7; wrapper 2 is otherwise disabled. [INFERRED] UART20 is connected to the physical BT controller.
4. Run schema checks for all three relevant bindings (including invalid supply/compatible fixtures), compiled DT label/pin ownership checks, focused ARM64 build with resolved Kconfig and module linkage; preserve stable UART7 diagnostic boot and any existing Boot PCIe root properties. Boot owns applying these changes and recording exact tested SHA.

No patch is being suggested for generic ath11k, hci_qca, WCN PMU or PCI power-control drivers. No changes to `sm8475.dtsi` or shared `sm8475-motorola-oneli.dts` have been made.

## 8. Verification ledger and stop condition

| Check | Result |
| --- | --- |
| Project and kernel baseline documents read | PASS, pinned source inspection |
| Motorola Cape radio, PCIe, UART, pinctrl and regulator source cross-check | PASS, source-only; oneli-specific loaded FDT unverified |
| Xiaomi product pin and firmware provenance comparison at fixed SHA | PASS, source-only; Xiaomi project reports tablet functionality |
| Accepted kernel `ath11k`, PCI power-control, WCN sequencer, `hci_qca`, `btqca` and bindings inspected | PASS, source-only; no driver patch warranted |
| Kernel branch compared to integration SHA | PASS: `razr/wireless` identical to `2b5acf108ae37040ac1e652e029bb37f5609e886` (zero commits/files) |
| Firmware files/hash validation | NOT RUN: no Motorola wireless binary inputs supplied or fetched; historical container manifests scoped as above |
| dt_binding_check / dtbs_check / changed-object build / module modpost | NOT RUN: no kernel or DT edits authorized; would test unchanged files only |
| oneli PCI enumeration, Wi-Fi association, BT pairing, suspend/resume, antenna, regulatory, coexistence | NOT TESTED: no native Linux boot / hardware |

**Future hardware-only gates**, when handset/native console available: (a) capture actual PCI `vendor:device`, subsystem IDs, link/MSI/MHI, WCN HW revision and ath11k QMI chip/board key; (b) inspect loaded stock DT selection and *oneli* factory calibration/MAC provenance; (c) capture Bluetooth HCI controller identity/ROM/board IDs and UART log on GPIO76–79 path; (d) validate shared enables XO and supply load sequencing, cold boot, Wi-Fi client scan/association throughput, BT discovery/pairing, both radios simultaneously, rfkill/suspend/wake, regulatory DB and cold/reboot stability. Do not flash while in this research task.

**Astra decision requested:** accept this as a source-only research handoff; keep wireless unscheduled until native boot and current DP priorities. When scheduled, first ask Boot/Power for the ten-input PMU supply mapping, then record actual PCI/HCI identifiers and firmware key before permitting any oneli wireless node to become active. This research does not authorize further wireless implementation rounds.

**Delivery:** project branch `razr/wireless` (this file only); kernel branch `razr/wireless` remains at exact accepted integration `2b5acf108ae37040ac1e652e029bb37f5609e886`, no kernel commits. No images, proprietary firmware, DTS, main or other agent branches changed.