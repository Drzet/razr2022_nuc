# Motorola Razr 2022 (oneli): native Linux hardware audit

**Research snapshot:** 11 October 2026. **Device firmware and hardware revision:** not yet read. **Native kernel boot:** not attempted/verified.

This is a **source-linked investigation**, not a claim that every subsystem already functions on mainline Linux. Exact Git commit hashes and per-component evidence appear in the XLSX and JSON.

## Most significant confirmed findings

- The [Motorola oneli overlay](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-oneli-common-overlay.dtsi) and [Cape SoC base](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape.dtsi) give exact board hardware configuration.
- **USB and DisplayPort:** DWC3, Qualcomm USB/DP PHY, Parade PS5169 redriver (I²C **0x30**; orientation **GPIO91**), and DP AUX switch GPIOs **2** and **71**. The [SM8475 upstream QMP USB/DP PHY](https://github.com/torvalds/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/phy/qualcomm/phy-qcom-qmp-combo.c) was merged in August 2026. The [PS5169 driver](https://lists.openwall.net/linux-kernel/2026/08/11/241) was submitted but **not present** in the inspected upstream Linux master.
- **Wi-Fi:** Qualcomm **QCA6490** appears in the inherited Cape device tree. Its exact PCI ID, revision and firmware on this Razr remain unknown. Upstream `ath11k` includes WCN6855-family support, **not proof of this Razr working**.
- **UFS:** Qualcomm UFS controller plus an upstream PHY containing an **exact SM8475 compatible**; board wiring and regulators found in Moto files.
- **Battery:** Qualcomm PMIC GLINK, **SGM41516D** flip charger, **TI BQ27426** fuel gauge with a **712 mAh source profile**. **Cellwise CW2217** is **disabled** in the inspected overlay. Mainline has an exact BQ27426 driver match, but not a demonstrated complete Moto dual-battery policy.
- **Display:** Oneli-specific `sde_dp` config and DP AUX routing present; output under upstream DRM/KMS remains unverified.

## Source trees and pinned commits

- [kernel-msm](https://github.com/MotorolaMobilityLLC/kernel-msm/tree/9511d6b2dc469e5bd836992e3bdd6d19ace112e0): `android-12-release-s3sl32.16-72-46`, commit `9511d6b2dc469e5bd836992e3bdd6d19ace112e0`
- [kernel-devicetree](https://github.com/MotorolaMobilityLLC/kernel-devicetree/tree/90fa7be1db5bd47202673d4431408659149a7359): `android-12-release-ssl`, commit `90fa7be1db5bd47202673d4431408659149a7359`
- [kernel-display-devicetree](https://github.com/MotorolaMobilityLLC/kernel-display-devicetree/tree/80b207bf35be5da38375e755506f136558ad24b5): `android-12-release-ssl`, commit `80b207bf35be5da38375e755506f136558ad24b5`
- [Mainline Linux snapshot](https://github.com/torvalds/linux/tree/a5ebb76233b79db01e82e061173cb73c6d2b5c6b): commit `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`

## Relevant DT source layering

```text
oneli base: cape-moto-oneli-base.dts / cape-v2-moto-oneli-base.dts
  -> cape-moto-common-base.dtsi / cape-v2-moto-common-base.dtsi
    -> cape.dtsi / cape-v2.dtsi (SoC; subsystems and UFS/WLAN)
oneli board overlays (EVT1/DVT1b/DVT2a/PVT)
  -> cape-oneli-common-overlay.dtsi
    -> cape-moto-common-overlay-base.dtsi (UFS, USB role, eUSB2 repeater)
    -> cape-moto-common-overlay.dtsi
    -> waipio-moto-common-charger.dtsi, waipio-li-charger-overlay.dtsi
    -> oneli thermal / touch / sensor / fingerprint / haptic overlays
    -> cape-moto-common-redriver.dtsi (PS5169, via I2C bus node)
display tree: cape-sde-oneli.dts + cape-sde-display-oneli-common-base.dtsi
  -> separate oneli EVT/DVT display overlays
```

This is a **logical source include map**. The actual in-memory DT depends on firmware DTB/DTBO selection and installed hardware revision.

## Next evidence collection

1. Read running Android firmware/build ID and selected oneli board revision.
2. Dump the **live** DTB/DTBO and PCI identification without reflashing.
3. Inspect QCA6490 WLAN firmware and validate PCIe enablement; align with ath11k board data.
4. Recheck PS5169 upstream patch status and integrate the mainline-compatible USB/DP DT.
5. Bring up a reversible initramfs, UFS read-only first; measure charging and thermal status before sustained NUC operation.

**File roles:** `.xlsx` human-filterable tables; `.json` machine-readable identical rows; this `.md` a quick project primer.