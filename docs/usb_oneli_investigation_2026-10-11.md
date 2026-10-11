# Motorola Razr 2022 (oneli): USB/Type-C integration investigation

Date: 2026-10-11. Stage: source researched; one binding patch implemented; no kernel build or on-device validation.

## Scope, pinned evidence and precedence

The primary hardware inventory is [the project hardware database](razr2022_native_linux_hardware_database_2026-10-11.json) and [audit](razr2022_linux_audit_readme_2026-10-11.md). The [SM8475 baseline comparison](sm8475_baseline_comparison_2026-10-11.md) determines which older node conventions must be translated. This report examines the specific USB dependencies in the kernel fork and Motorola sources.

- Target kernel baseline: [Drzet/linux a5ebb76233b79db01e82e061173cb73c6d2b5c6b](https://github.com/Drzet/linux/tree/a5ebb76233b79db01e82e061173cb73c6d2b5c6b).
- Motorola device tree: [MotorolaMobilityLLC/kernel-devicetree 90fa7be1db5bd47202673d4431408659149a7359](https://github.com/MotorolaMobilityLLC/kernel-devicetree/tree/90fa7be1db5bd47202673d4431408659149a7359).
- Motorola kernel: [MotorolaMobilityLLC/kernel-msm 9511d6b2dc469e5bd836992e3bdd6d19ace112e0](https://github.com/MotorolaMobilityLLC/kernel-msm/tree/9511d6b2dc469e5bd836992e3bdd6d19ace112e0).
- Community SM8475 reference: [sm8450-mainline/linux bf1d29fced6e156dd6090a9b6600a8c44259c114](https://github.com/sm8450-mainline/linux/tree/bf1d29fced6e156dd6090a9b6600a8c44259c114); useful for SoC PHY fallback, not a drop-in oneli board tree.
- PS5169 proposed mainline driver/binding: [August 2026 v3 posting](https://patchew.org/linux/20260810-ps5169-bup-v3-0-a2178b2834d7@proton.me/). It is external, unmerged in the selected baseline, and has not been tested on oneli.

Actual installed chip revisions, the running Android firmware, the selected board overlay, and USB cable/host tests remain unrecorded.

## Verified controller and wiring evidence

| Function | Motorola source at pinned revision | Kernel baseline capability / remaining work |
| --- | --- | --- |
| DWC3 host/gadget | [cape-usb.dtsi](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-usb.dtsi), core at `0x0a600000`; a legacy nested `dwc3@a600000` node | `drivers/usb/dwc3/dwc3-qcom.c` supports single integrated `qcom,snps-dwc3` controller in `sm8450.dtsi`. Board must use `&usb_1` directly. |
| HS eUSB2 PHY | [cape-usb.dtsi](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-usb.dtsi), `0x088e3000`; `L5B` (vdd), `L10C` (vdda12) | Baseline inherited `usb_1_hsphy` is an **SM8450 legacy HS PHY**, which must be replaced for SM8475. `drivers/phy/phy-snps-eusb2.c` implements the Synopsys eUSB2 PHY using the `qcom,sm8550-snps-eusb2-phy` fallback. |
| NXP eUSB2-to-USB2 repeater | [cape-moto-common-overlay-base.dtsi](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-common-overlay-base.dtsi), I²C 0x4f on `qupv3_se5_i2c`, PM8350C GPIO7 reset, `S10B` and `L2B` supplies | Baseline `drivers/phy/phy-nxp-ptn3222.c` and `Documentation/devicetree/bindings/phy/nxp,ptn3222.yaml` support the **specific PTN3222**, not generic `nxp,eusb2-repeater`. Exact oneli repeater SKU remains unknown. |
| USB3/DP PHY | [cape-usb.dtsi](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-usb.dtsi), combo PHY at `0x088e8000` | Baseline `drivers/phy/qualcomm/phy-qcom-qmp-combo.c` already matches `qcom,sm8475-qmp-usb3-dp-phy`. Board needs relevant supplies, compatible, orientation/mode graph. |
| Type-C and role | [cape-moto-common-overlay-base.dtsi](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-common-overlay-base.dtsi) links UCSI connector to USB role graph | Baseline `drivers/usb/typec/ucsi/ucsi_glink.c` and PMIC GLINK binding provide Type-C + USB role switching. Firmware protocol on oneli untested. |
| PS5169 redriver | [cape-oneli-common-overlay.dtsi](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-oneli-common-overlay.dtsi) enables [cape-moto-common-redriver.dtsi](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-common-redriver.dtsi), I²C 0x30 on `qupv3_se18_i2c` | No PS5169 driver in pinned Linux baseline. Review/rebase the v3 generic Type-C retimer/mux patch series before use. |

Motorola's NXP repeater supplies are `vdd18-supply = <&S10B>` and `vdd3-supply = <&L2B>`. The mainline PTN3222 binding instead names these `vdd1v8-supply` and `vdd3v3-supply`. The vendor's `qcom,param-override-seq = <0x40 0x06 0x22 0x07 0x64 0x08>` writes **0x40 to register 0x06, 0x22 to 0x07, and 0x64 to 0x08** (value/register ordering established by [repeater-i2c-eusb2.c](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/9511d6b2dc469e5bd836992e3bdd6d19ace112e0/drivers/usb/repeater/repeater-i2c-eusb2.c)). The generic upstream PTN3222 driver only implements regulators and reset, **not these tune writes**. Whether tune writes are essential, or whether it is a PTN3222 at all, requires on-device identification. Do not bind unknown silicon to `nxp,ptn3222` as fact. [INFERRED] PTN3222 is a candidate given the platform, function and address, but these details do not prove the part number. Qualcomm's PMIC eUSB2 repeater driver (`drivers/phy/qualcomm/phy-qcom-eusb2-repeater.c`) is unrelated to this I²C device.

## Required translation to current baseline DT layout (Boot-owned)

These are changes **requested of Boot**; none are yet committed to the shared kernel SoC/board DT:

| Legacy Motorola concept | New DT location/representation |
| --- | --- |
| `&usb0`, wrapper + child `dwc3@a600000` | **`&usb_1` only**, at `usb@a600000`; no child `dwc3`, no `&usb_1_dwc3` reference |
| `&eusb2_phy0`, `qcom,usb-snps-eusb2-phy` | Replace inherited `usb_1_hsphy: phy@88e3000` node with `qcom,sm8475-snps-eusb2-phy`, `qcom,sm8550-snps-eusb2-phy`; `#phy-cells = <0>`, mainline `ref` clock, reset, vdd/vdda12 supplies, and `phys = <&repeater>` |
| `dummy-supply`, `usb-repeater` vendor phandle | Drop both; mainline eUSB2 PHY uses generic `phys` phandle to a **generic PHY** repeater |
| `nxp,eusb2-repeater` with vendor `reset-gpio`, tune sequence | Keep I²C location and demonstrated power/reset wiring as evidence; identify chip, then use a compatible supported by mainline or contribute a new one. For PTN3222 specifically, new properties include `#phy-cells`, `vdd1v8-supply`, `vdd3v3-supply`, `reset-gpios`. GPIO polarity must be checked before encoding. |
| `&usb_qmp_dp_phy` | `&usb_1_qmpphy`, exact `qcom,sm8475-qmp-usb3-dp-phy`; existing USB and DP graphs `usb_1_qmpphy_usb_ss_in`, `usb_1_qmpphy_dp_in` |
| `&ucsi { connector { port ... } }` | PMIC GLINK compatible parent and a numbered `connector@0`, `compatible = "usb-c-connector"`, whose `port@0` endpoint pairs with **`&usb_1_dwc3_hs`**. Verify the parent and connector's mainline binding. |
| Motorola redriver `parade,ps5169-redriver`, `ssusb_redriver`, `redriver,orientation-gpio` | Remove legacy wrapper property. V3 retimer driver expects `parade,ps5169`, mode/orientation switch and a **graph**; consider PMIC GLINK's `orientation-gpios` from Motorola TLMM91. Establish VIO, VCC and reset pin sequencing and graph before enabling. |

Board dependency: `&qupv3_se5_i2c` (repeater), PM8350C GPIO7 pinctrl and supplies `S10B`/`L2B` must be functional for high-speed data; `&qupv3_se18_i2c`, VIO `L8C`, VCC `S10B` and reset pin assignment are separately required for PS5169. These Motorola regulator names are **vendor labels**, not assumed upstream label names. Boot must reconcile against the actual oneli PMIC definitions. Keep all Boot edits on its ownership branch, not USB.

## Driver/binding gaps, commits and integration order

1. **Implemented, binding only:** [kernel USB branch commit `0119d73b40bed1041278cf9307bdec9c17880618`](https://github.com/Drzet/linux/commit/0119d73b40bed1041278cf9307bdec9c17880618) extends `Documentation/devicetree/bindings/phy/qcom,snps-eusb2-phy.yaml` with the SM8475-specific compatible plus the existing SM8550 fallback. This follows the [community SM8475 include](https://github.com/sm8450-mainline/linux/blob/bf1d29fced6e156dd6090a9b6600a8c44259c114/arch/arm64/boot/dts/qcom/sm8475.dtsi). No driver change needed for fallback matching.
2. **P0 unresolved:** exact NXP repeater chip ID and reset polarity. Identify from live Android DT / I²C identification or other attributable board evidence. If actually PTN3222, adapt binding properties; evaluate whether vendor tuning is necessary. If not, design a new upstream I²C generic PHY driver + vendor-specific binding without copying Android's obsolete USB repeater framework.
3. **P0 proposed Boot DT:** reconciled SM8475 eUSB2 PHY, repeater I²C node, regulators and single DWC3 node. For an intentionally high-speed-only diagnostic candidate, [INFERRED] request `maximum-speed = "high-speed"` and `qcom,select-utmi-as-pipe-clk` on `&usb_1`, with only HS PHY in `phys`/ `phy-names`; later restore USB3. This is a **test variant** contingent on confirming the mainline binding, not a permanent constraint.
4. **P0 Type-C:** PMIC GLINK UCSI graph and USB-role switch; verify actual UCSI service and orientation on both cable rotations. `&usb_1_dwc3_hs` endpoint is already in selected baseline; do not add non-existent `&usb_1_dwc3` child.
5. **P1 PS5169/USB3:** inspect [2026 v3 series](https://patchew.org/linux/20260810-ps5169-bup-v3-0-a2178b2834d7@proton.me/) and mainline review, port under original attribution in **separate driver and binding commits** if necessary. Mainline representation requires reset, supplies and Type-C graph; vendor's register config sequence has no direct mechanical 1:1 binding. The PS5169 has no integrated DP AUX switch: keep Motorola's separate DP AUX GPIO2/GPIO71 with DisplayPort ownership.
6. **P1 SuperSpeed:** enable `usb_1_qmpphy` with exact SM8475 compatible, USB3 DWC3 PHY and PS5169 oriented retimer. Verify each cable orientation and DP altmode independently.

The v3 PS5169 work must not be counted as a delivered kernel patch until a reviewed version has actually been committed to `razr/usb`. The Motorola [vendor PS5169 driver](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/9511d6b2dc469e5bd836992e3bdd6d19ace112e0/drivers/usb/misc/ssusb-redriver-ps5169.c) uses proprietary framework-era notifier interfaces and legacy DT properties; wholesale copying is inappropriate.

## Validation and handoff to Boot

**Performed:** direct source-level comparison of pinned vendor/common/oneli DT, baseline `sm8450.dtsi`, mainline eUSB2 PHY and PTN3222 drivers/bindings, UCSI/DWC3 code, and upstream PS5169 submission. Kernel branch contains one binding edit.

**Not performed:** `dt_binding_check`, `dtbs_check`, compiled kernel, CI result, USB enumeration, gadget test, physical host mode, PD/role switching, SuperSpeed, DisplayPort. No oneli kernel board tree or complete build inputs yet.

Next test sequence, once Boot has provided an explicit dependency commit:

1. Confirm running oneli overlay, I²C repeater identity and reset polarity without modifying firmware; capture identity and source revision.
2. Boot a test kernel with the selected eUSB2/PMIC dependencies and board DT; validate binding schemas and `dtbs` against a recorded toolchain.
3. With a host connected to the Razr, demonstrate gadget enumeration and a usable USB network or serial debugging channel; save `dmesg`, USB descriptors, UCSI state and exact kernel/DTB revisions. This is the first **USB-debug usable** acceptance criterion.
4. Verify OTG/host mode with low/full/high-speed peripheral enumeration and USB power behavior, then both Type-C orientations.
5. Integrate PS5169/USB3/DP only after high-speed diagnostic connectivity is reliable; test SuperSpeed and external display separately.

Coordination: Boot owns `sm8475.dtsi`, oneli `.dts`, shared PMIC and UCSI nodes; USB supplies reviewed binding/driver patches and specific board-change requests. Board revision and firmware identification remain blocking evidence. See [subsystem handoff](handoffs/usb_2026-10-11.md).
