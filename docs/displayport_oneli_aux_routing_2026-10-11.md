# Motorola oneli: DP AUX switch software truth table and Type-C handoff

**Date:** 2026-10-11. **Research state:** pinned-source audit complete for *vendor GPIO software behaviour*. **Runtime state:** not tested; phone unavailable. **Kernel baseline:** `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. **Kernel DisplayPort branch:** `razr/displayport` at baseline, **no kernel patch**.

## Source provenance and critical distinction

Earlier oneli evidence named GPIO2 and GPIO71, but could not prove their asserted/deasserted states. The matching **Motorola display driver is in a separate repository**, rather than the generic `kernel-msm/drivers/gpu/drm/msm/dp` tree:

- **Motorola display-driver revision:** `MotorolaMobilityLLC/kernel-msm-5.4-techpack-display`, release `android-12-release-s3sl32.16-72-46`, immutable commit **`701a48c1db80eda2ff17154a9017783230cc22aa`**.
  - [`msm/dp/dp_aux.c` lines 714–778](https://github.com/MotorolaMobilityLLC/kernel-msm-5.4-techpack-display/blob/701a48c1db80eda2ff17154a9017783230cc22aa/msm/dp/dp_aux.c#L714-L778), `dp_aux_configure_aux_switch`: logical enable / orientation and GPIO writes.
  - [`msm/dp/dp_display.c` lines 2057–2103](https://github.com/MotorolaMobilityLLC/kernel-msm-5.4-techpack-display/blob/701a48c1db80eda2ff17154a9017783230cc22aa/msm/dp/dp_display.c#L2057-L2103): obtains the two Motorola GPIOs, initializes enable GPIO high and flip GPIO low.
  - [`msm/dp/dp_display.c` lines 1449–1459](https://github.com/MotorolaMobilityLLC/kernel-msm-5.4-techpack-display/blob/701a48c1db80eda2ff17154a9017783230cc22aa/msm/dp/dp_display.c#L1449-L1459) and [lines 1690–1695](https://github.com/MotorolaMobilityLLC/kernel-msm-5.4-techpack-display/blob/701a48c1db80eda2ff17154a9017783230cc22aa/msm/dp/dp_display.c#L1690-L1695): AUX switch is set for DP attach/configure and disconnected on detach, outside simulator and separate GPIO-HPD paths.
  - [`msm/dp/dp_parser.c` lines 246–285](https://github.com/MotorolaMobilityLLC/kernel-msm-5.4-techpack-display/blob/701a48c1db80eda2ff17154a9017783230cc22aa/msm/dp/dp_parser.c#L246-L285): a **different** `qcom,dp-gpio-aux-switch` / `qcom,aux-en-gpio`, `qcom,aux-sel-gpio`, `qcom,usbplug-cc-gpio` vendor variant. Do not conflate this with oneli's `mmi,` GPIO path.
- **Motorola oneli display device tree:** `MotorolaMobilityLLC/kernel-display-devicetree`, commit **`80b207bf35be5da38375e755506f136558ad24b5`**:
  - [`display/cape-sde-display-oneli-common-base.dtsi` lines 778–804](https://github.com/MotorolaMobilityLLC/kernel-display-devicetree/blob/80b207bf35be5da38375e755506f136558ad24b5/display/cape-sde-display-oneli-common-base.dtsi#L778-L804): `&fsa4480` is disabled, `mmi,aux-switch-enable-gpio = <&tlmm 2 0x00>`, `mmi,aux-switch-flip-gpio = <&tlmm 71 0x00>`.
  - [`display/cape-sde.dtsi` lines 21–30](https://github.com/MotorolaMobilityLLC/kernel-display-devicetree/blob/80b207bf35be5da38375e755506f136558ad24b5/display/cape-sde.dtsi#L21-L30): `sde_dp` inherited `qcom,dp-aux-switch = <&fsa4480>`. The Motorola driver checks that phandle *even though the node is disabled*. The actual FSA4480 switch-event call and notifier registration are commented out in the inspected driver. **Do not carry the phantom FSA phandle into mainline**.
  - [`display/cape-sde-oneli.dts` lines 10–14](https://github.com/MotorolaMobilityLLC/kernel-display-devicetree/blob/80b207bf35be5da38375e755506f136558ad24b5/display/cape-sde-oneli.dts#L10-L14): vendor disables MST.
- **Mainline candidates:** `Drzet/linux` at `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`:
  - [`drivers/usb/typec/mux/gpio-sbu-mux.c`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/usb/typec/mux/gpio-sbu-mux.c): handles TYPEC orientation, DP modes C/D/E, safe and USB modes.
  - [`Documentation/devicetree/bindings/usb/gpio-sbu-mux.yaml`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/Documentation/devicetree/bindings/usb/gpio-sbu-mux.yaml): **requires a documented first compatible** (listed hardware IC) plus `"gpio-sbu-mux"`, `select-gpios`, `orientation-switch`, and Type-C graph `port`. Mode switching adds the `enable-gpios` requirement. Bare `"gpio-sbu-mux"` does not satisfy this schema. None of the enumerated IC identities is established for oneli.
  - [`drivers/soc/qcom/pmic_glink_altmode.c`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/soc/qcom/pmic_glink_altmode.c), [QMP USB3/DP PHY](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/phy/qualcomm/phy-qcom-qmp-combo.c), [MSM DP bridge](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/gpu/drm/msm/dp/dp_display.c): existing Mode/Orientation, hotplug, DP AUX, and DRM chain, no new DRM driver justified by current sources.
- **PS5169 distinction:** Motorola board has the Parade **PS5169** redriver at I²C `0x30`, GPIO91 orientation reference; PS5169 does **not** integrate an AUX switch (PS5170 does). USB owns redriver/GLINK/PHY, DisplayPort owns analysis of the separate SBU/AUX path. [Upstream PS5169 v3 cover/series](https://patchew.org/linux/20260810-ps5169-bup-v3-0-a2178b2834d7@proton.me/).

## Reconstructed Motorola GPIO logic: source-backed *software* truth table

For the **oneli-defined** GPIO assignments, the vendor driver's `gpio_set_value` uses 0 to assert AUX enable and 1 to release it. In that driver, `ORIENTATION_CC1` sets flip 0; `ORIENTATION_CC2` sets flip 1. The oneli DT flags for both GPIO specs are `0x00`, not an active-low descriptor remapping.

| Vendor event | `enable` | `orientation` | GPIO2 value written | GPIO71 value written | Explanation |
| --- | --- | --- | --- | --- | --- |
| Driver initialization | N/A | N/A | `1` | `0` | Explicit `gpio_direction_output` defaults |
| DP connection/configure CC1 | true | `ORIENTATION_CC1` | `0` | `0` | AUX enabled, unflipped |
| DP connection/configure CC2 | true | `ORIENTATION_CC2` | `0` | `1` | AUX enabled, flipped |
| DP disconnect | false | `ORIENTATION_NONE` | `1` | `0` | AUX disabled and flip reset |

**Proven:** the exact values written by this pinned vendor implementation, the GPIO indices in oneli source and the driver call sites. **[INFERRED]** those GPIO writes physically select the intended SBU paths on every production board, because the actual switch IC, route wiring, board revision and live FDT have not been independently inspected. The unknown electrical chip polarity cannot be replaced with a hardware identification claim.

**[INFERRED] Mainline descriptor translation if the hardware qualifies for the generic driver:** `enable-gpios = <&tlmm 2 GPIO_ACTIVE_LOW>` and `select-gpios = <&tlmm 71 GPIO_ACTIVE_HIGH>`. This maps the generic driver's logical `enabled=true` to vendor GPIO2 = 0, `swapped=true` to vendor GPIO71 = 1. The active-low descriptor encoding is a *software translation backed by the vendor writes*, **not** independent electrical validation. Do not land this node without identifying a compatible switch IC (or obtaining a reviewed binding extension). The existing generic driver is a candidate, not a proven oneli match.

### Vendor special case

The driver retains `qcom,dp-aux-switch = <&fsa4480>` from `cape-sde.dtsi` to satisfy its `aux_switch_node` guard in `dp_display_usbpd_configure_cb` and `dp_aux_configure_aux_switch`, while actually writing the `mmi,` GPIOs. Oneli's display overlay disables `fsa4480`. The real hardware is **not thereby proven to be FSA4480**. Mainline instead should link the independent switch into the Type-C graph; do not invent a legacy `qcom,dp-aux-switch` phandle or propagate the vendor `mmi,` properties into the mainline DP node.

## Cross-subsystem ownership matrix

| Path/function | Code/DT owner | Pinned evidence and handoff | Condition before enabling |
| --- | --- | --- | --- |
| DPU → DP0 | **Boot** owns shared DTS; DisplayPort reviews | `sm8450.dtsi` defines `dpu_intf0_out` ↔ `mdss_dp0_in` | Reviewed Boot DTB/schema and stable MDSS power/clock |
| DP0 → QMP DP input | **Boot** graph, **USB** PHY driver/binding enable, DisplayPort checks | `mdss_dp0_out` ↔ `usb_1_qmpphy_dp_in`; exact SM8475 QMP compatible on Boot branch | USB/Power supplies + graph + schema |
| QMP SuperSpeed output ↔ PS5169 ↔ Type-C connector `port@1` | **USB** | Motorola PS5169 `0x30`, QUP SE18, PS5169 patch v3 | Valid PS5169 driver/binding; actual reset/supplies; graph + device identity |
| Type-C `port@0` ↔ `usb_1_dwc3_hs` | **USB** | Current baseline's single DWC3 node and USB role switch | HS path, UCSI and repeater ready |
| Type-C `port@2` ↔ independent GPIO-SBU AUX switch | **DisplayPort** proposes, **Boot** integrates | oneli GPIO2/71 truth table above | Switch IC compatible established, or custom narrowly scoped binding accepted; correct polarity |
| Type-C orientation / DP pin assignment, mode C/D/E, HPD | **USB** owns PMIC GLINK + connector, DisplayPort confirms HPD bridge | Mainline `pmic_glink_altmode.c` produces mode/orientation and `drm_aux_hpd_bridge_notify` | Firmware message format/source supported; only one GPIO91 owner |
| PS5169 orientation / GPIO91 | **USB** in consultation with Power/DisplayPort | Motorola vendor `redriver,orientation-gpio`; mainline GLINK has optional orientation GPIO input | Do not request GPIO91 twice or assume it is an output |
| Regulators: QMP PHY, PS5169 `S10B/L8C`, MDSS, QUP | **Power** supplies; **Boot** incorporates; **USB** validates consumers | Motorola I²C and PMIC DT | Verified voltage constraints and parent supplies |

*Coordinate by exact commits and shared handoff, not by independently editing `sm8475.dtsi` or `sm8475-motorola-oneli.dts`.*

## Graph proposal to Boot and USB

This is an **ownership/endpoint graph**, not a compilable DT fragment. Square-bracket labels identify **unimplemented/unverified** nodes, not invented Linux bindings:

```text
DPU INTF0 ─── mdss_dp0:port@0
                  |
             mdss_dp0:port@1
                  |
             usb_1_qmpphy:port@2       existing reciprocal DP/PHY link
                  |
             QMP USB3/DP shared physical lanes
                  |
             usb_1_qmpphy:port@0 ─ [PS5169 @ qupv3_se18_i2c, 0x30] ─ connector@0:port@1
             usb_1:HS endpoint ─────────────────────────────────────── connector@0:port@0
                     [AUX/SBU GPIO mux, actual compatible UNKNOWN] ─ connector@0:port@2

PMIC GLINK firmware ─ DP Alt Mode/orientation/HPD → Type-C mux/switches and DRM HPD bridge
                                      ├─ QMP mode/orientation
                                      ├─ PS5169 orientation/mode (USB owner)
                                      └─ AUX/SBU GPIO2/71 state (DisplayPort owner)
```

For Boot, **request only after USB/Power prerequisites are assembled**:
```dts
&mdss {
    status = "okay";
};

&mdss_dp0 {
    status = "okay";
};
```

These two overlay fragments are *uncommitted proposals* and do **not** themselves make DP functional. The inherited `sm8450.dtsi` has reciprocal DP0/QMP ports; do not duplicate or renumber them. The **new independent AUX/SBU node stays absent/disabled** until its IC compatible and Type-C graph can satisfy a real binding. Do not invent `data-lanes`, PHY polarity, IC names, GPIO reset or a new MSM DRM driver. `qcom,mst-enable` is vendor-only and should not be copied.

## Offline validation and deferred boundary

- **Performed (2026-10-11):** retrieved all six cited pinned source files for oneli GPIOs, driver GPIO writes, mainline mux implementation and binding; 13 read-only static source assertions passed (vendor CC1/CC2 cases, enable-low, flip-high, startup defaults, configure gate, DT GPIO2/GPIO71, FSA phandle, FSA disabled, mainline DP mode handling, binding compatible requirements). Source text checks only, **not** driver compilation, binding/schema validation or native boot.
- **Performed, baseline graph text checks (2026-10-11):** 10/10 pinned-source assertions passed against `sm8450.dtsi`, `sm8450-hdk.dts`, `dp_display.c`, and `phy-qcom-qmp-combo.c`: DPU INTF0↔DP0 in; DP0 out↔QMP DP in; QMP SS in↔DWC3 SS; presence of QMP output port@0; upstream SM8450 HDK Type-C connector `port@2` precedent; PMIC GLINK compatible precedent; MSM DP bridge lookup at output port 1; QMP DRM AUX bridge registration. **These check source text only**, not a compiled oneli candidate graph, schema pass, firmware signal routing or DP operation. The HDK is a comparator, **not** evidence that oneli contains the same SBU mux.
- **Existing baseline CI:** [clean ARM64 Image/dtbs run 38144632260](https://github.com/Drzet/razr2022_nuc/actions/runs/38144632260) passed; it does not cover this unimplemented DP graph.
- **Not possible to honestly validate as a device-tree schema candidate today:** the physical SBU/AUX switch identity is unrecorded; the selected mainline GPIO-SBU binding explicitly requires a listed IC compatible and a connected Type-C port, while USB has not yet supplied the complete connector/PS5169 graph. There is **no fabricated schema-valid switch node** to test. Source-level mapping is demonstrated; full graph `dtbs_check` remains pending its real prerequisites.
- **Physical runtime all deferred:** no phone, no selected live firmware/revision; no EDID, HPD, actual pin voltage, monitor output or retimer behaviour. [Dock/display procedure](../tests/procedures/2026-10-11-displayport-dock.md) applies later.

## Next actionable gates

1. USB confirms Type-C/PMIC GLINK `connector@0` port ownership, PS5169 input/output ports and GPIO91 single-owner policy with exact commit(s). Shared board edits go to Boot.
2. Seek oneli bill of materials/schematic, supplier or stock-firmware evidence establishing the separate AUX switch IC, followed by a binding compatibility check. **Do not claim an exact IC based on this GPIO truth table alone**.
3. Boot adds reviewed DP enablement only once USB, Power, and SBU switch graph can be expressed with existing supported bindings; compile the exact oneli DTB and run `dtbs_check` with recorded toolchain/logs. On phone availability, test both orientations and DP/USB/PD dock combinations.

Current evidence stages: **researched yes; kernel implementation no; build-tested no; hardware-tested no**.
