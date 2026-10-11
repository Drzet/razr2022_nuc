# USB2-first Boot contract v1: oneli source-only DT staging

**Date:** 2026-10-11. **Owner:** USB / Type-C; **consumer/sole shared-DT owner:** Boot. **Status:** review-ready *disabled-node proposal*, not functional USB2. No oneli device is available.

Exact dependencies: upstream kernel `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`; USB eUSB2 binding `0119d73b40bed1041278cf9307bdec9c17880618`; Boot's second-review staged board `3825dc6afb0f5e102845b32811ce0f518c0b4bbf` (later Boot changes must be pinned afresh); Power [rail contract v2](https://github.com/Drzet/razr2022_nuc/blob/razr/power/docs/power_oneli_rail_contract_v2_2026-10-11.md). This contract explicitly does **not** depend on the PS5169 candidate or DisplayPort/AUX hardware.

## Hardware evidence versus acceptable offline change

Motorola `kernel-devicetree@90fa7be1db5bd47202673d4431408659149a7359`: [`cape-usb.dtsi`](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-usb.dtsi) puts eUSB2 at **0x088e3000**, DWC3 at **0x0a600000** and QMP USB3/DP at **0x088e8000**. [`cape-moto-common-overlay-base.dtsi`](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-common-overlay-base.dtsi) puts the active NXP repeater at **I2C 0x4f**, reset on **PM8350C GPIO7**, powered from PM8350 **S10B** (1.8 V) and **L2B** (vendor 2.7–3.3 V, initial 3.072 V); its three tuning bytes are **register `0x06←0x40`, `0x07←0x22`, `0x08←0x64`**. External NXP SKU and reset polarity are *not identified*. `nxp,ptn3222` is **[INFERRED]** and MUST NOT be used as oneli fact. The mainline PTN3222 driver neither reads ID nor applies those tunings.

Source labels correctly translated against `sm8450.dtsi`:
- Motorola `&qupv3_se5_i2c` → **`&i2c5`**, `i2c@994000`; parent **`&qupv3_id_0`**. Boot enabled this parent for UART7; child remains disabled.
- Vendor `&usb0` nested DWC3 → **`&usb_1` single integrated `usb@a600000`**; existing `&usb_1_dwc3_hs` Type-C role endpoint, no separate `&usb_1_dwc3`.
- Inherited `&usb_1_hsphy` is incompatible **SM8450 USB HS 7nm** with a different mainline PHY binding; do not change its compatible in place while retaining all legacy resources.
- Existing eUSB2 mainline driver `drivers/phy/phy-snps-eusb2.c` matches fallback `qcom,sm8550-snps-eusb2-phy`. It calls `devm_of_phy_optional_get` for a generic PHY repeater; **the phandle is optional for the driver but not for functioning oneli high-speed lines**.
- [Power's v2 contract](https://github.com/Drzet/razr2022_nuc/blob/razr/power/docs/power_oneli_rail_contract_v2_2026-10-11.md) separately establishes eUSB PHY `L5B` (0.88V) and `L10C` (~1.2V) source labels from Motorola plus NXP `S10B/L2B`. Actual parent supply topology and electrical RPMh ownership remain [INFERRED]. The current Boot `&apps_rsc` providers are intentionally disabled.

## Boot edit A: schema-stage SM8475 eUSB2 SoC node, not enabled

Request a **separate** Boot-owned `arch/arm64/boot/dts/qcom/sm8475.dtsi` commit replacing the old HS PHY node (as Boot already did for the UFS PHY). This is a candidate structure, NOT committed here:

```dts
/* SM8475 override, leave disabled; board provides required supplies. */
/delete-node/ &usb_1_hsphy;

&soc {
    usb_1_hsphy: phy@88e3000 {
        compatible = "qcom,sm8475-snps-eusb2-phy",
                     "qcom,sm8550-snps-eusb2-phy";
        reg = <0 0x088e3000 0 0x154>;
        #phy-cells = <0>;
        clocks = <&rpmhcc RPMH_CXO_CLK>;
        clock-names = "ref";
        resets = <&gcc GCC_QUSB2PHY_PRIM_BCR>;
        status = "disabled";
    };
};
```

**[INFERRED]** Register extent `0x154` and using the retained 19.2 MHz `RPMH_CXO_CLK` as the single mainline `ref` come from the current Qualcomm generic eUSB2 binding/example and inherited Qualcomm clock reference. Vendor Cape lists both `RPMH_CXO_CLK` and `GCC_EUSB3_0_CLKREF_EN`; verify correct SM8475 `ref` clock source and ownership rather than silently dropping the extra vendor gate. Binding requires `vdd-supply` and `vdda12-supply`, supplied in board DTS below; check compiled DT for duplicate MMIO nodes after `/delete-node/`.

## Boot edit B: disabled board supply consumers and diagnostic controller

Request a **separate** board-only `sm8475-motorola-oneli.dts` patch with supply phandles referring only to Boot's own **disabled** staged regulators; the existing Boot `oneli_l5b` and `oneli_l10c` labels are verified on that branch. This is a review/schematic validation stage, not approval to enable hardware.

```dts
&usb_1_hsphy {
    vdd-supply = <&oneli_l5b>;
    vdda12-supply = <&oneli_l10c>;
    status = "disabled";
};

/* Existing Qualcomm DWC3, unchanged MMIO/IRQ/clocks. */
&usb_1 {
    dr_mode = "otg";
    usb-role-switch;
    maximum-speed = "high-speed";
    qcom,select-utmi-as-pipe-clk;
    phys = <&usb_1_hsphy>;
    phy-names = "usb2-phy";
    status = "disabled";
};

/* QUP0 ancestor is already enabled for UART7. */
&i2c5 {
    status = "disabled";
};

/* QMP USB3/DP stays disabled; PS5169 SE18 stays disabled/absent. */
```

**[INFERRED]** The DWC3 HS-only arrangement is a *temporary diagnostic candidate*, justified by baseline DWC3 binding `qcom,select-utmi-as-pipe-clk` and driver selecting UTMI over PIPE without SSPHY; no HS-only oneli hardware operation has been demonstrated. Do not remove the inherited reciprocal SS/DP graph without a separate exact schema audit; those links can remain source declarations while disabled.

**Do not create a fake repeater provider node.** No `compatible = "nxp,ptn3222"` or unknown placeholder phandle is valid today. The repeater I2C at `&i2c5` may be inspected from a vendor/live board only after its power/reset contract is established. Even a schema-valid disabled eUSB2 PHY alone will not drive physical USB2 data lines through an uninitialized external repeater. **USB2 debugging is a priority, not currently viable device connectivity.**

## Boot edit C: independently stage the role graph (not USB3)

USB2 is electrically separate from PS5169 (SuperSpeed lanes), so Boot can propose the Qualcomm GLINK `connector@0` **port@0** now. Mainline comparator [`sm8450-hdk.dts`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/arch/arm64/boot/dts/qcom/sm8450-hdk.dts) uses `qcom,sm8450-pmic-glink`, `qcom,pmic-glink` and GPIO91 as `orientation-gpios`, plus an HS port to `&usb_1_dwc3_hs`. Oneli Motorola redriver also reads TLMM91 **low=CC1 / high=CC2**, providing source evidence for that *software polarity*. [INFERRED] actual oneli GLINK service and physical input semantics remain to be checked. One GPIO91 owner: GLINK only, never also PS5169.

```dts
/* Boot-owned board candidate; keep disabled until PMIC GLINK verified. */
/ {
    pmic-glink {
        compatible = "qcom,sm8450-pmic-glink", "qcom,pmic-glink";
        #address-cells = <1>;
        #size-cells = <0>;
        orientation-gpios = <&tlmm 91 GPIO_ACTIVE_HIGH>;
        status = "disabled";

        connector@0 {
            compatible = "usb-c-connector";
            reg = <0>;
            power-role = "dual";
            data-role = "dual";
            ports {
                #address-cells = <1>;
                #size-cells = <0>;
                port@0 {
                    reg = <0>;
                    usb_hs_connector: endpoint {
                        remote-endpoint = <&usb_1_dwc3_hs>;
                    };
                };
            };
        };
    };
};

&usb_1_dwc3_hs {
    remote-endpoint = <&usb_hs_connector>;
};
```

The PMIC GLINK parent compatible is inherited from a **comparator**, not a demonstrated oneli firmware protocol; remain [INFERRED] pending Power/GLINK compatibility audit. No QMP/PS5169 or DP/AUX `port@1`/`port@2` required for this stage. Host/gadget role-switch firmware behaviour must later be tested separately.

## Before any active USB2 enablement

Boot + Power + USB must establish *all* of the following, not merely pass YAML schema:

1. **Regulator contract:** actual enabled RPMh providers and parent inputs for L5B, L10C, S10B, L2B; declared Motorola acceptable ranges rather than copied initial set points. Power contract v2 still marks grouped oneli parent inputs [INFERRED].
2. **External repeater identity:** supported I2C generic-PHY driver/compatible, PM8350C GPIO7 reset polarity and full initialization/tune sequence with error handling. Read-only later: I2C `0x4f` revision `0x13` and chip IDs `0x14..0x16`. Stock DT register map is not a silicon identity.
3. **Clock/reset:** correct eUSB2 `ref` clock rate (driver supports 19.2/38.4 MHz) and GCC/QUP resets. Confirm `&qupv3_id_0` enabled (already Boot UART) and only then `&i2c5`.
4. **Type-C:** GLINK firmware signalling, USB role mux, GPIO91 single-source orientation. `connector@0` port@0 and `&usb_1_dwc3_hs` reciprocal, avoiding duplicate labels.
5. **Validation:** Boot records exact SoC/board SHA; `make ARCH=arm64 ... qcom/sm8475-motorola-oneli.dtb`, all-applicable filtered `dtbs_check`; inspect actual flattened DT for enabled ancestors, rail phandles, controller and link graph; log introduced-versus-baseline warnings. Do not call a disabled-node DTB an enumerating USB subsystem.

Next *physical* acceptance (unavailable today): repeatable USB gadget network/serial enumeration on external Linux host, dmesg and USB descriptors with timestamps/exact DTB/kernel/firmware; follow with host mode, both plug orientations, then independent USB3/DP. **No USB board patch, regulator enable, enumeration or hardware validation was performed by this USB chat.**
