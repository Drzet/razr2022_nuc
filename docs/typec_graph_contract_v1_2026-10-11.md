# Type-C / PS5169 / DisplayPort connector graph contract v1

**Date:** 2026-10-11. **USB-owned graph/retimer proposal; Boot sole shared-DT editor.** Explicit coordination with [DisplayPort issue #3](https://github.com/Drzet/razr2022_nuc/issues/3) and [Power rail contract v2](https://github.com/Drzet/razr2022_nuc/blob/razr/power/docs/power_oneli_rail_contract_v2_2026-10-11.md). This is an unenabled source-level contract, not actual hardware operation. Independent earlier USB2 contract: [USB2-first v1](usb2_first_boot_contract_v1_2026-10-11.md).

**Source pins:** Motorola device tree `90fa7be1db5bd47202673d4431408659149a7359`, Motorola USB/PS5169 kernel `9511d6b2dc469e5bd836992e3bdd6d19ace112e0`, DisplayPort driver's oneli GPIO routing `701a48c1db80eda2ff17154a9017783230cc22aa`, Linux baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`, and external PS5169 [Esteban Urrutia v3](https://patchew.org/linux/20260810-ps5169-bup-v3-0-a2178b2834d7@proton.me/) originally based on `3d08ff75a47a3e7e2ab45a3bcab6723b4d906422`. USB GitHub Actions candidate compiles the v3 driver with direct-header repair; build result is **not** evidence of oneli reset wiring or Alt Mode.

## Version 1 endpoint ownership and wiring model

| Exact connector/graph port | Input/output association | Owner and stage |
| --- | --- | --- |
| `pmic-glink/connector@0/ports/port@0` | USB2 DWC3 role: bidirectional endpoint `&usb_1_dwc3_hs` on **single integrated** `&usb_1` controller | USB proposal → Boot DT. Can be schema-staged **disabled before PS5169**, see USB2-first v1. |
| `connector@0/port@1` | USB3/DP physical lane output of Parade PS5169 **`port@0`**; PS5169 `port@1` is its input from existing QMP `&usb_1_qmpphy_out` | USB Type-C + Boot. **Not enabled** until driver, power, reset and graph schema resolve. |
| `usb_1_qmpphy/port@1` | Existing `&usb_1_qmpphy_usb_ss_in` ↔ DWC3 `&usb_1_dwc3_ss` | Baseline internal pair; USB must preserve it. |
| `usb_1_qmpphy/port@2` | Existing `&usb_1_qmpphy_dp_in` ↔ `&mdss_dp0_out` | Baseline internal pair; DisplayPort reviews, Boot integrates only when ready. |
| `connector@0/port@2` | Independent SBU/AUX sideband GPIO switch. **Not PS5169 port@2**. No node or phandle until exact switch-compatible is source-backed | DisplayPort proposes and Boot integrates. Explicit hold. |

The generic connector's ports 0/1/2 are semantically different. The QMP's own ports 0/1/2 are also separate numbering spaces. The PS5169 v3 binding allows ports 0 (connector facing) and 1 (QMP facing) for PS5169; **only PS5170** supports a third integrated AUX switch port. A PS5169 `port@2` would assert nonexistent hardware.

```text
UCSI/PMIC GLINK firmware ⇒ Type-C connector@0 / DP Alt Mode + HPD
                               ├─ port@0 ⇄ usb_1_dwc3_hs (USB2 role)
                               ├─ port@1 ⇄ PS5169:port@0 ⇄ PS5169:port@1
                               │                        ⇄ usb_1_qmpphy_out
                               │                            ├─ QMP port@1 ⇄ DWC3 USB3
                               │                            └─ QMP port@2 ⇄ DRM DP0
                               └─ port@2 ⇄ [INDEPENDENT AUX/SBU SWITCH: UNKNOWN IC]
                                               ↑
                                    TLMM GPIO2 enable, GPIO71 flip
```

## GPIO input/enable assignment: exactly one owner each

1. **TLMM91 orientation:** Motorola `redriver,orientation-gpio` is an **input**, with vendor `0 = CC1`, `1 = CC2`. The mainline [PMIC GLINK binding](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/Documentation/devicetree/bindings/soc/qcom/qcom,pmic-glink.yaml) defines `orientation-gpios` active level as CC2. Therefore [INFERRED] **GLINK alone owns `orientation-gpios = <&tlmm 91 GPIO_ACTIVE_HIGH>`**, then forwards orientation through Type-C mux/retimer callbacks to QMP and PS5169; the latter **must not independently acquire GPIO91**. The SM8450 HDK comparator also uses GPIO91 but is not proof of physical oneli wiring.
2. **TLMM19 PS5169 control:** Motorola [oneli DT](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-oneli-common-overlay.dtsi) pinctrl **GPIO19 high = redriver enabled**, **low = disabled**. Vendor [PS5169 driver](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/9511d6b2dc469e5bd836992e3bdd6d19ace112e0/drivers/usb/misc/ssusb-redriver-ps5169.c) waits **10 ms after enabling**. [INFERRED] It *may* correspond to the v3 driver `reset-gpios` represented with `GPIO_ACTIVE_LOW`, making logical reset=1 physically low; however there is **no independent part-pin or reset pulse/power sequence evidence**. **Do not bind GPIO19 as an asserted reset or invent another GPIO until confirmed.** The v3 driver's 1 ms asserted/10 ms deasserted pulse is not a hardware-proven replacement for vendor pinctrl enable semantics.
3. **PM8350C GPIO7 eUSB2 repeater:** assigned only to external NXP repeater, not PS5169; physical reset polarity and chip SKU unknown.
4. **TLMM GPIO2/71 AUX switch:** the DisplayPort team proved vendor *software writes*: disconnected `GPIO2=1 GPIO71=0`, CC1 `GPIO2=0 GPIO71=0`, CC2 `GPIO2=0 GPIO71=1`, from [Motorola DP driver](https://github.com/MotorolaMobilityLLC/kernel-msm-5.4-techpack-display/blob/701a48c1db80eda2ff17154a9017783230cc22aa/msm/dp/dp_aux.c#L714-L778). [INFERRED] A mainline GPIO-SBU mux would need `enable-gpios` ACTIVE_LOW and `select-gpios` ACTIVE_HIGH to reproduce *software* state. The binding requires a proven part-compatible and none is known; **no port@2 board node can be legitimately enabled now**.

## Power and patch gates

- **PS5169 I2C:** vendor SE18 `0x30` corresponds to upstream `&i2c18`, `i2c@88c000` under `&qupv3_id_2`, both disabled on Boot's staged board. VCC source **PM8350 S10B** (1.8 V), VIO source **PM8350C L8C** (vendor 1.8–2.0 V, init 1.8 V). Neither are currently active upstream regulator contracts. The v3 upstream driver requests only `vcc`; USB proposes a separate **VIO bulk-regulator** adaptation with `vio-supply`, validated offline but not an active board-compatible claim. Retimer EQ differs from Motorola's pin-specific `config-seq`; comparison and signal integrity deferred.
- **PS5169 upstream v3:** Linux mainline baseline does not include it. It was reviewed for missing direct headers; USB has a source-pinned, attributable build with header fixes. No driver added to `Drzet/linux` shared mainline or board: candidate build script stages original patches in CI. [Source/validation](handoffs/2026-10-11-usb-priority1.md).
- **PMIC GLINK/UCSI and HPD:** `qcom,sm8450-pmic-glink` comparator plus driver exists, but oneli firmware's compatible message flow untested. Power owns charger/PD protocol evidence, USB owns Type-C role/orientation graph, DP checks DP Alt Mode/HPD and AUX. Existing `pmic_glink_altmode.c` and QMP combo PHY handle switch/HPD events if compatible; do not add a vendor DRM workaround without driver failure evidence.
- **Phase A:** Boot disabled USB2/eUSB2 + `connector@0 port@0` graph with reciprocal `usb_1_dwc3_hs`. No PS5169 or AUX prerequisite for *staging*.
- **Phase B (held):** verified repeater, accurate regulator parents and firmware role required for *active* USB2.
- **Phase C (held):** PS5169 confirmed reset/power, candidate kernel driver and binding compiled/schema-checked; Boot adds `connector@0 port@1` PS5169 QMP graph and enables QMP.
- **Phase D (held):** DP validates real AUX-SBU compatible and switch driver, adds `connector@0 port@2`, Boot integrates DP0 enable and checks DT, then hardware dock/HPD/AUX/EDID.

## Ownership acceptance

USB: connector ports 0/1, GPIO91 GLINK single-owner policy, PS5169/Type-C drivers/bindings and QMP proposal. DisplayPort: AUX software truth table and switch part-compatible, connector port@2, DRM validation. Power: S10B/L2B/L8C and eUSB PHY L5B/L10C parent/voltage gating; GLINK charger firmware. Boot: only repository branch that edits oneli board and SM8475 shared DTS. **No one integrates unresolved node compatibles into an active DT.**

Validation: sourced graph and GPIO logic checked against pinned code; **no integrated DTB/DT schema validation** of this graph yet; no physical tests. CI PS5169 source object is an independent build, not evidence of actual USB3, DP or GLINK firmware functionality.
