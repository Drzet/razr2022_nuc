# Motorola oneli: regulator and power dependency proposal for Boot

2026-10-11 | Owner: Power | Stage: **source-audited proposal only**. No device, DTB build, or electrical measurements. Shared DT files remain owned by Boot.

**Kernel baseline:** `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. **Required Boot source dependency reviewed:** `cb9105ebeb9485e31d044d4fa69396b415523669`. Power research branch `razr/power` inherits that Boot commit, and makes no changes to Boot-owned DTS. Phone revision and installed firmware are unknown. [INFERRED] denotes upstream reconstruction rather than independently observed oneli wiring.

## Sources (fixed revisions)

- [Motorola Cape regulator resources](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-regulators.dtsi) (particularly lines 19–55, 77–93, 115–130, 172–188, 208–223, 487–502, 525–541 and 601–618).
- [Motorola common UFS and eUSB2 supply relationships](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-common-overlay-base.dtsi) (lines 71–95 and 121–159).
- [Motorola oneli overlay](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-oneli-common-overlay.dtsi) (lines 83–160, 194–288).
- [Mainline regulator support](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/regulator/qcom-rpmh-regulator.c) (`pm8350_vreg_data`/`pm8350c_vreg_data` and compatible table), [RPMh regulator binding](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml).
- [SM8450 HDK regulator example](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/arch/arm64/boot/dts/qcom/sm8450-hdk.dts) (lines 316–530), **comparator only, not Motorola oneli**.
- [Boot's shared SoC and board DT](https://github.com/Drzet/linux/tree/cb9105ebeb9485e31d044d4fa69396b415523669/arch/arm64/boot/dts/qcom).

## A. Evidence and mappings, separate categories

### Actual Motorola resource constraints and consumers

Values are in **microvolts**. The ranges and init targets are literal **Motorola source values**; none is a measured voltage. `S` and `L` labels identify PM8350-family RPMh resources, not SPMI bus addresses.

| Rail | Vendor min..max; init (µV) | Board source consumer / role | Recommended staged role |
| --- | --- | --- | --- |
| PM8350 S10B (smps10) | 1800000..1800000; 1800000 | BQ27426 + SGM41516D I²C supply, NXP eUSB2 repeater 1.8V supply | USB and flip-battery later |
| PM8350 S12B (smps12) | 1224000..2040000; 1256000 | Upstream comparator: parent to PM8350 L9B and PM8350C L10C; **[INFERRED] oneli parent relationship** | Candidate dependency for UFS |
| PM8350 L2B (ldo2) | 2700000..3300000; 3072000 | NXP eUSB2 repeater `vdd3-supply` | USB later |
| PM8350 L5B (ldo5) | 720000..958000; 880000 | UFS PHY `vdda-phy-supply` | UFS first |
| PM8350 L7B (ldo7) | 2400000..3544000; 2504000 | UFS host `vcc-supply` | UFS first |
| PM8350 L9B (ldo9) | 1200000..1304000; 1200000 | UFS host `vccq-supply`, vendor UFS ref-clock rail | UFS first |
| PM8350C BOB (bob) | 3008000..3960000; 3296000 | Upstream comparator: parent to PM8350 L2B, L5B, L7B and PM8350C L8C/L11C; **[INFERRED] oneli parent relationship** | Candidate dependency |
| PM8350C L8C (ldo8) | 1800000..2000000; 1800000 | Parade PS5169 `vio-supply`; Motorola overlay marks `regulator-boot-on` | USB/DP after Boot regulator review |
| PM8350C L10C (ldo10) | 1200000..1304000; 1200000 | UFS PHY `vdda-pll-supply` | UFS first |
| PM8350C L11C (ldo11) | 3000000..3000000; 3000000 | Oneli panel/touch panel rail declared directly in overlay | Display later |

The **PM8350B** I²C-related pair/load GPIO controls and PM8350C GPIO2 charger enable in the oneli source are pinctrl/GPIO consumers, **not RPMh regulators**. Do not synthesize GPIO-controlled `regulator-fixed` devices from these vendor pins without a reviewed driver/ownership contract.

### Candidate upstream parent input-supply topology

This is taken from **SM8450 HDK**, using the baseline PM8350/PM8350C RPMh binding's *actual* `vdd-*-supply` property names. The source is explicitly **not oneli-specific**. Consequently every row here is **[INFERRED] for oneli**.

| Candidate upstream input property | Proposed upstream parent | Relevant outputs | Reason / blocker |
| --- | --- | --- | --- |
| PM8350 `vdd-s10-supply` | `vph_pwr` | S10B | HDK model; **oneli `vph_pwr` source and voltage unknown** |
| PM8350 `vdd-s12-supply` | `vph_pwr` | S12B | HDK model; do not invent a 3.7V fixed supply on oneli |
| PM8350 `vdd-l2-l7-supply` | PM8350C BOB | L2B, L7B | HDK arrangement; upstream group property from binding |
| PM8350 `vdd-l3-l5-supply` | PM8350C BOB | L5B | HDK arrangement; review actual phone power path |
| PM8350 `vdd-l6-l9-l10-supply` | PM8350 S12B | L9B | HDK arrangement; regulator dependency ordering |
| PM8350C `vdd-bob-supply` | `vph_pwr` | BOB | HDK arrangement; physical input and `vph_pwr` unknown |
| PM8350C `vdd-l2-l8-supply` | PM8350C BOB | L8C | HDK arrangement; redriver must not be enabled prematurely |
| PM8350C `vdd-l10-supply` | PM8350 S12B | L10C | HDK arrangement |
| PM8350C `vdd-l6-l9-l11-supply` | PM8350C BOB | L11C | HDK arrangement |

RPMh resource suffix IDs `b` for PM8350 and `c` for PM8350C agree between the observed downstream names `smpb`/`ldoc` and baseline SM8450 HDK. Their use in an oneli upstream tree is **[INFERRED]** pending the populated board/firmware. A 3.7 V `vph_pwr` `regulator-fixed` in the HDK is a **comparator board model**; copying it would claim a fixed voltage for the handset's variable supply. Do not do so.

### Prerequisite and enable-order matrix

1. Existing bootloader/firmware initialization → RPMh RSC `&apps_rsc` and power domains → regulator providers at corresponding resource IDs → parent supplies → consumers.
2. UFS: L5B, L10C → `&ufs_mem_phy` analog supplies; L7B, L9B → `&ufs_mem_hc` VCC/VCCQ. Mainline DTS defines `ufs_mem_hc: ufshc@1d84000` and `ufs_mem_phy: phy@1d87000`; the SM8475 Boot include relocates PHY to `0x1d80000`. Keep `UFS_PHY_GDSC` in power-domains. Vendor `vdd-hba-supply=<&gcc_ufs_phy_gdsc>` is *not* a regulator reference to copy.
3. USB debug: S10B (1.8 V), L2B (3.07 V) → NXP eUSB repeater `0x4f`, via PM8350C GPIO7 reset and translated I²C bus; L8C → PS5169 redriver `0x30`; Type-C/PMIC GLINK and USB owner supply the connector graph. Do not enable an unidentified repeater driver.
4. Flip charging: S10B → I²C gauge `0x55` and SGM charger `0x6b`; TLMM43/51 and PM8350C GPIO2 / PM8350B GPIO1/3 require explicit ownership only once their drivers and dual-battery policy are available. The vendor explicitly has `init-charger-disabled`.
5. Display: L11C is a vendor-established 3.0 V rail, enabled only after display owner accepts the actual consumer mapping. `regulator-boot-on` on L8C does **not** prove the rail should be permanently always-on.

**Minimal Boot proposal to Boot Sol:** add the two RPMh PMIC provider nodes beneath `&apps_rsc` using supported compatibles, actual PMIC-ID suffixes and only the needed UFS child regulators. Review them initially with `status = "disabled"` and vendor init voltages as **candidate constraints**, then resolve parent supply providers before enabling. Do not enable UFS until the final topology has passed binding/DT checks. Boot owns node labels and shared `sm8475-motorola-oneli.dts`; this report does not alter those files.

Illustrative **review-only, electrically disabled** provider skeleton (not a build-tested patch, and parent-supply phandles intentionally withheld):

```dts
&apps_rsc {
    regulators-0 {
        compatible = "qcom,pm8350-rpmh-regulators";
        qcom,pmic-id = "b"; /* [INFERRED] upstream oneli resource mapping */
        status = "disabled";

        oneli_l5b: ldo5 {
            regulator-name = "oneli-l5b-ufs-phy";
            regulator-min-microvolt = <880000>;
            regulator-max-microvolt = <880000>;
        };
        oneli_l7b: ldo7 {
            regulator-name = "oneli-l7b-ufs-vcc";
            regulator-min-microvolt = <2504000>;
            regulator-max-microvolt = <2504000>;
        };
        oneli_l9b: ldo9 {
            regulator-name = "oneli-l9b-ufs-vccq";
            regulator-min-microvolt = <1200000>;
            regulator-max-microvolt = <1200000>;
        };
    };
    regulators-1 {
        compatible = "qcom,pm8350c-rpmh-regulators";
        qcom,pmic-id = "c"; /* [INFERRED] upstream oneli resource mapping */
        status = "disabled";

        oneli_l10c: ldo10 {
            regulator-name = "oneli-l10c-ufs-pll";
            regulator-min-microvolt = <1200000>;
            regulator-max-microvolt = <1200000>;
        };
    };
};
```

All voltage numbers above are sourced vendor **initial settings**, proposed as [INFERRED] provisional *fixed* candidate constraints for a **disabled** DT, not approved operating ranges. The actual Motorola min/max ranges are in the first table. **The skeleton does not include parent supply properties, and deliberately cannot be used to turn the UFS rails on.** Boot should incorporate this only in a review-only step if useful, validate against the exact binding, and subsequently replace constraints/parents with justified live evidence.

## Revision and validation boundary

- Motorola oneli has EVT1, DVT1B, DVT2A and PVT overlay identities; the checked `cape-oneli-common-overlay.dtsi` is a shared source, not proof of any live revision.
- Hardware evidence is unavailable, so actual voltage state, boot-on persistence, charger enable, thermal sensors and the physical power path are **untested**.
- Offline acceptance: Boot creates separate DTS commits with source citations, runs `sm8475-motorola-oneli.dtb`, `dtbs_check` for selected bindings, checks resolved regulators and unresolved/duplicate phandles, and reports warnings distinct from base.
- Later phone acceptance: regulator `debugfs` state and hardware voltage verification, read-only UFS discovery, eUSB role stability, no brownouts and charging/thermal transitions under load.
- No off-branch merge or baseline change is requested.
