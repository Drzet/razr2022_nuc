# SM8475 baseline comparison

Date: 2026-10-11. Stage: researched; kernel build blocked before configuration completed; no hardware tests.

## Selected inputs

- Baseline: [Drzet/linux at a5ebb76233b79db01e82e061173cb73c6d2b5c6b](https://github.com/Drzet/linux/tree/a5ebb76233b79db01e82e061173cb73c6d2b5c6b), 7.3-rc6 plus subsequent commits. `razr/boot` created at this SHA; master unchanged. No patches applied.
- Community reference: [sm8450-mainline/linux at bf1d29fced6e156dd6090a9b6600a8c44259c114](https://github.com/sm8450-mainline/linux/tree/bf1d29fced6e156dd6090a9b6600a8c44259c114), 6.13-rc3-based.
- Compared both `arch/arm64/boot/dts/qcom/sm8450.dtsi` files, community `sm8475.dtsi` and Nothing Phone 2 board references, plus baseline driver matches and bindings. This is not a review of every commit in the community fork.

## Findings and disposition

| Area | Verified source finding | Required action |
| --- | --- | --- |
| SoC include | Baseline has sm8450.dtsi but no sm8475.dtsi | Construct a reconciled SM8475 include; retain community attribution for reused material |
| Clock controllers | GCC, GPUCC, DISPCC, CAMCC and VIDEOCC already have exact SM8475 matches and bindings | Reuse baseline drivers; do not backport these drivers wholesale |
| UFS PHY | Exact SM8475 driver and binding exist. Community replaces the SM8450 PHY with a different register range; baseline SM8450 node also has a power-domain property absent in that replacement | Validate the SM8475 node against current binding/driver and Motorola evidence, preserving required power relationships |
| USB3 / DP PHY | Baseline has qcom,sm8475-qmp-usb3-dp-phy; community sm8475.dtsi does not override the inherited combo compatible | Use current SM8475 support after validating its node resources; copying the old include alone misses this distinction |
| eUSB2 | Community uses qcom,sm8475-snps-eusb2-phy with sm8550 fallback. Baseline has the fallback driver, but its schema does not list the SM8475-specific compatible | Establish justified compatibility and add binding support as needed; fallback matching is not proof of working Razr USB |
| TLMM | Community sets qcom,sm8475-tlmm alone. No exact match exists in baseline drivers or bindings | Resolve pinctrl compatibility before enabling board peripherals; this is not a usable unchanged override |
| GPU OPP table | Community adds SM8475 OPP children to the inherited opp-table without deleting the old table. Baseline has ten SM8450 OPP child names not replaced by those additions | Explicitly reconcile/replace the table against verified SM8475 operating points; do not accept accidental merged OPP sets |
| USB controller layout | Baseline uses a single usb_1 node with qcom,snps-dwc3. Community has an older wrapper and usb_1_dwc3 child; its Pong board refers to that child label | Translate board USB properties and graph references into current bindings; do not import the old hierarchy |
| VPU | Community include changes VIDEOCC compatible; baseline already supports that clock controller. No SM8475 match found in baseline Iris sources | Decoder enablement remains separate VPU work; clock changes alone do not provide decode |

The GPU OPP merge concern is a source-level finding, not a measured runtime failure. The old and new node names were compared; no compiled DTB or device test was produced.

## Source paths

Paths below are relative to the pinned kernel repositories above:

- `arch/arm64/boot/dts/qcom/sm8450.dtsi` (both revisions).
- `arch/arm64/boot/dts/qcom/sm8475.dtsi` and `sm8475-nothing-pong.dts` (community).
- `drivers/clk/qcom/{gcc,gpucc,dispcc,camcc,videocc}-sm8450.c` and their clock schemas (baseline).
- `drivers/pinctrl/qcom/pinctrl-sm8450.c`, `Documentation/devicetree/bindings/pinctrl/qcom,sm8450-tlmm.yaml`.
- `drivers/phy/phy-snps-eusb2.c`, `Documentation/devicetree/bindings/phy/qcom,snps-eusb2-phy.yaml`.
- `drivers/phy/qualcomm/phy-qcom-qmp-ufs.c`, `Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-ufs-phy.yaml`.
- `drivers/phy/qualcomm/phy-qcom-qmp-combo.c`, `Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-usb43dp-phy.yaml`.
- `drivers/media/platform/qcom/iris/`.

## Implementation order

1. Resolve the [build environment blocker](../tests/results/2026-10-11-baseline-build.md) and establish the clean ARM64 kernel/DT build.
2. Resolve TLMM/eUSB2 compatibility and current binding requirements using Motorola and community driver evidence.
3. Add a reconciled SM8475 include, with GPU operating points separately reviewed and USB/UFS resources verified.
4. Add the oneli board tree using its own wiring, supplies, reserved memory and boot artifacts. Pong is a reference, not a replacement for oneli evidence.
5. Validate bindings and DTBs before packaging with the reviewed postmarketOS tooling.

The baseline and branch are now concrete. Board support remains unimplemented; no DT source was imported merely to create an apparent milestone.
