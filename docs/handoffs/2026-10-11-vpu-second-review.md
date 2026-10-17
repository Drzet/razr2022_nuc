# VPU second coordinator review: resource contract, public stock and strict kernel build

**Origin:** VPU subsystem chat 2026-10-11, executing coordinator `docs/NEXT_TASKS.md` blob `cf3d86160c6d9bc04efaf0b462babd5c7375618c` from main. Evidence is source, GitHub CI and public reference only; the phone remains unavailable.

## Exact revisions and ownership

- Selected baseline kernel: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`, **unchanged**.
- Kernel fork / branch / current VPU RFC head: `Drzet/linux`, `razr/vpu`, **`7f1d729b6f458f1e76efe2894eb3c544bc9db856`**, draft [PR #2](https://github.com/Drzet/linux/pull/2), 7 commits past baseline.
- Boot dependency reviewed but *not integrated*: `Drzet/linux` `razr/boot` commit `3825dc6afb0f5e102845b32811ce0f518c0b4bbf`. No shared board or SoC DTS edits by VPU.
- Coordinator branch `Drzet/razr2022_nuc` `razr/vpu`, draft [PR #1](https://github.com/Drzet/razr2022_nuc/pull/1), contains scripts, GitHub workflows, schema/firmware/boot metadata and this handoff. Aggregate coordinator `docs/STATUS.md` and `docs/NEXT_TASKS.md` intentionally untouched.
- Kernel source changes limited to `Documentation/devicetree/bindings/media/qcom,sm8475-iris.yaml`, four `drivers/media/platform/qcom/iris/` files and `drivers/soc/qcom/ubwc_config.c`.

## Completed code and provenance

1. Kernel binding commit **`3d532ed35ab98ce45efe0be65f7ec165e27e2a4c`**: four ordered VPU power domains now required because the actual Iris probe attaches `venus/vcodec0` and `mxc/mmcx` OPP domains; `operating-points-v2` made mandatory for the unconditional OPP table call; required IOMMU count relaxed from unsupported exactly two to 1–2, pending stream-ID/IOMMU policy proof. **Neither possible mapping is marked verified.**
2. Kernel UBWC provider commit **`7f1d729b6f458f1e76efe2894eb3c544bc9db856`**: supplies previously missing `qcom,sm8475` machine compatible in Qualcomm `qcom_ubwc_configs`, mapping to existing `ubwc_4_0_hbb16`. **[INFERRED]** match derives from pinned Xiaomi Waipio LPDDR5 default `UBWC_CONFIG(8,32,16,0,1,1,1)`, not Motorola SMEM measurement. Without the match, `qcom_ubwc_config_get_data()` would return `-EINVAL` before Iris resources register. The shared provider modification needs Boot/GPU review; other drivers may consume it.
3. Complete source contract and bounded assumptions: [Iris probe contract](../vpu/2026-10-11-iris-probe-contract.md). SM8250-derived ICC BW table, `0xe0000000-1` DMA mask, capacity and RPMh OPP corner guesses remain explicitly **[INFERRED]** and *isolated* to the proposed SM8475 profile; they are not validated for native decode. Signed firmware and video enablement still blocked.
4. Hardened offline firmware inventory `scripts/inventory-oneli-firmware.py`: enumerates ZIP members, parses bounded Android DTBO entries (rejects out-of-range/overlapping entries) and hashes extracted firmware when supplied. Synthetic regression tests added to `tests/vpu/test-inventory.py`.
5. New bounded public ZIP64 inspector `scripts/inspect-oneli-stock-ranges.py`, with ZIP64 extended offsets and decompression size caps; metadata-only [workflow](../../.github/workflows/vpu-stock-metadata.yml) verified exact boot/vboot and four FDT hashes. Corrected workflow uses `set -euo pipefail`; historical run 38169976751 had a **false-positive green job** because Python failed parsing ZIP64 and `tee` masked it. Later [run 38170215643](https://github.com/Drzet/razr2022_nuc/actions/runs/38170215643) actually passed all inspections.

## Public stock reference, shared across Boot/GPU/Power

- Hosted complete download [run 38169190369](https://github.com/Drzet/razr2022_nuc/actions/runs/38169190369) **passed**; HTTP 200, 4,353,164,507 bytes, verified package SHA256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`. Specific public URL/build in [stock manifest](../vpu/2026-10-11-public-stock-reference-manifest.md). No proprietary binary uploaded; temporary 4.35-GB ZIP deleted from runner.
- [ZIP64 range validation run 38170215643](https://github.com/Drzet/razr2022_nuc/actions/runs/38170215643) **passed**; project exact checkout PR test-merge **`b54c76ace9c997697b8732138ec855569ec1225f`**, `dtc 1.7.0`, evidence artifact SHA256 `9ec33e7bfa01dee313a7e8e22ee08ad62b7da0f58ad2be67cc52c76f96fb1531`. [Metadata-only artifact](https://github.com/Drzet/razr2022_nuc/actions/runs/38170215643/artifacts/11713258439); [exact hashes/report](../vpu/2026-10-11-public-stock-boot-dtbo.md).
- Stock `boot.img` and `vendor_boot.img` both have **header version 4**; four decompiled candidate DTBOs all root `oneli` / `qcom,cape-mtp`, `qcom,cape`, `qcom,mtp`, `moto,oneli`. They include `diodes,eusb2-repeater` and `nxp,eusb2-repeater` compatibles. Actual selected overlay remains unknown.
- Stock ZIP member list contains sixteen `super.img_sparsechunk.*` members; **VPU signed `vpu20_4v`, vendor ZAP and other GPU firmware still require super/vendor partition extraction**. No signed firmware hash or version marker yet. VPU HFI Gen2 matches tested **host code**, not the stock signed firmware.
- [Shared issue #10](https://github.com/Drzet/razr2022_nuc/issues/10) contains exact public firmware hashes and Boot/GPU/Power consumption contract. No second multi-GB download required merely to know the package fingerprint.

## Validation result and remaining gate

**Previously PASS with limited scope:** [run 38165380924](https://github.com/Drzet/razr2022_nuc/actions/runs/38165380924) source ABI fixtures, isolated ARM64 Iris `qcom-iris.ko` compile/link and SM8475 binding lint, but it tolerated unresolved symbols because `M=` build had no complete `Module.symvers`. This is historical and does **not** validate the current corrected kernel head.

**Strict in-tree build configured, completion must be checked:** workflow `.github/workflows/vpu-hfi-audit.yml` now pins kernel exactly to `7f1d729b6f458f1e76efe2894eb3c544bc9db856`, saves actual resolved `.config`, runs `make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j4 Image modules` without `KBUILD_MODPOST_WARN=1`, requires populated `Module.symvers` and linked `qcom-iris.ko`, records Image/Module.symvers/module SHA256, runs DT binding check, and enforces `set -euo pipefail`. [Push build run 38170604512](https://github.com/Drzet/razr2022_nuc/actions/runs/38170604512) was started; its **final conclusion is not recorded in this handoff yet**. Previous PR full builds with many redundant sync events were in-progress/cancelled; only a completed, successful result on the exact pinned kernel SHA with artifacts can close the gate. This is deliberately **not called PASS**.

Phone access remains deferred for PAS authentication, HFI exchange, V4L2 registration/decode, 4K playback and secure firmware variants. The kernel candidate is an unmerged RFC, not operational acceleration. Boot keeps all `sm8475.dtsi` and oneli board DTS edit ownership.

## Next actionable handoffs

- **To Boot:** review four-domain mandatory binding/OPP/pinctrl/IOMMU contract and actual four public stock FDT candidate compatibles; no oneli VPU node enabled until signed firmware path and RAM/IOVA/corner mapping are grounded.
- **To GPU:** review shared UBWC provider match; use *same* public archive reference SHA and metadata for SQE/GMU/ZAP inventory; do not assume signed zap interchangeability.
- **To Power:** use referenced vendor root compatible/DTBO evidence and keep rail parents deferred until verified on real hardware.
- **To coordinator:** record final conclusion and build artifact hashes from strict run 38170604512; if it fails, use its exact compiler/modpost diagnostics rather than interpreting partial module compile as success.
