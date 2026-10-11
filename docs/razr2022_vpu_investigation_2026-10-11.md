# Razr 2022 (oneli) VPU / 4K browser playback investigation
Date: 2026-10-11

## Evidence status

This is a **source-backed feasibility audit, not a successful VPU bring-up**. No running Razr firmware/DTB, VPU firmware image, boot logs or decoder benchmarks were inspected. Sources mentioning **Cape / SM8475** are SoC-family evidence, not proof the same DT overlay or firmware revision is running on a particular Razr 2022.

## Confirmed source findings

1. **Motorola's video-specific device-tree repository supplies the missing controller description.** Its `waipio-vidc.dts` has `qcom,cape` in the platform compatible list and includes `waipio-vidc.dtsi`. The included node supplies:
   - Device `qcom,vidc@aa00000`, MMIO base `0x0aa00000`, length `0xF0000`.
   - Compatibles `qcom,msm-vidc`, `qcom,msm-vidc-waipio`, `qcom,msm-vidc-iris2`.
   - GIC SPI interrupt 174; `pas-id = <9>`; `memory-region = <&video_mem>`.
   - Firmware name `vpu20_4v`.
   - GCC/video CC clock, GDSC power, interconnect, reset and SMMU context-bank definitions (secure and non-secure).
   - Sources: [waipio-vidc.dts](https://github.com/MotorolaMobilityLLC/kernel-video-devicetree/blob/android-13-release-t1sh33.35-23-20/waipio-vidc.dts), [waipio-vidc.dtsi](https://github.com/MotorolaMobilityLLC/kernel-video-devicetree/blob/android-13-release-t1sh33.35-23-20/waipio-vidc.dtsi).
   - **Caution:** This is an Android 13 Motorola branch, not a verified effective DT overlay from the Razr 2022. `Kbuild` maps `CONFIG_ARCH_WAIPIO` to `waipio-vidc.dtbo` and `CONFIG_ARCH_CAPE` to `ukee-vidc.dtbo`. The `ukee` overlay includes the same `waipio-vidc.dtsi`, but selection on oneli must be checked from its actual boot artifacts. Sources: [Kbuild](https://github.com/MotorolaMobilityLLC/kernel-video-devicetree/blob/android-13-release-t1sh33.35-23-20/Kbuild), [ukee-vidc.dts](https://github.com/MotorolaMobilityLLC/kernel-video-devicetree/blob/android-13-release-t1sh33.35-23-20/ukee-vidc.dts).

2. **Upstream VPU architecture.** Linux video-maintainer discussion describes the SM8450 core as **VPU2.0 hardware with HFI Gen2 firmware**, unlike the assumption that HFI Gen2 necessarily implies VPU3 hardware. [March 2026 driver discussion](https://patchew.org/linux/20260320-iris-platform-data-v9-0-3939967f4752%40oss.qualcomm.com/20260320-iris-platform-data-v9-8-3939967f4752%40oss.qualcomm.com/). [INFERRED] SM8475/Cape likely follows the closely related SM8450 video architecture; the Motorola `iris2` DT compatible and `vpu20_4v` naming support this.
   
3. **Upstream clock support exists.** `CONFIG_SM_VIDEOCC_8450` includes the `qcom,sm8475-videocc` match, introduced in Linux 6.13. This is a clock-controller driver, **not** VPU decode support. [LKDDb](https://cateee.net/lkddb/web-lkddb/SM_VIDEOCC_8450.html).

4. **Upstream Iris still needs a platform addition.** At inspection on 2026-10-11, [Linux Iris probe matching table](https://github.com/torvalds/linux/blob/master/drivers/media/platform/qcom/iris/iris_probe.c) contains platforms including SM8250, SM8550 and Milos, but **no SM8450 or SM8475 entry**. Likewise [sm8450.dtsi](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/qcom/sm8450.dtsi) has `videocc` but no video-codec device node. Thus neither the Android downstream DT `compatible` nor just enabling the upstream clock driver can yield a decoder device.

5. **Close contemporary reference implementation:** [July 2026 Iris Milos VPU2.0 / Gen2 patchset](https://lists.openwall.net/linux-kernel/2026/07/05/252) adds an example Gen2 HFI implementation on VPU2 hardware and V4L2/VP9 tests. This is a development reference, not proven binary-compatible platform data for SM8475.

6. **Firmware availability is unresolved.** The Motorola Android overlay specifies `vpu20_4v`. The [February 2026 linux-firmware qcom/vpu directory](https://kernel.googlesource.com/pub/scm/linux/kernel/git/firmware/linux-firmware/+/refs/tags/20260221/qcom/vpu/) does not list `vpu20_4v.mbn` (it contains other VPU20 variants). Android device firmware manifests for other Qualcomm devices list `vendor/firmware/vpu20_4v.mbn`, e.g. [LineageOS device manifest](https://github.com/LineageOS/android_device_xiaomi_venus/blob/lineage-23.2/proprietary-files.txt). Those manifests do not prove firmware interchangeability: a mainline upstream developer explicitly warns VPU20 images for different SoCs can be incompatible. [Driver discussion](https://lists.openwall.net/linux-kernel/2026/02/05/520). Prefer identifying Motorola oneli's own signed firmware in its public firmware package or currently running Android first.

7. **Browser path is separate from device bring-up.** Iris exposes a stateful V4L2 memory-to-memory decoder. Chromium has V4L2 stateful decoder code ([Chromium source](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/media/gpu/v4l2/v4l2_stateful_video_decoder.h)), but a generic Debian/Chromium ARM64 build is **not guaranteed** to enable that accelerated pipeline, nor is zero-copy / DMA-BUF integration automatically proven. Confirm VP9 4K hardware decoding through standalone V4L2/GStreamer first; only then test the browser.

## Next steps, ordered

- **Remote/source only:** Identify the correct oneli Android vendor firmware release and its `vpu20_4v` file(s). Inspect matching kernel video-driver code / firmware protocol, review upstream Iris VPU2 Gen2 support and turn Motorola's downstream node into a draft upstream-style binding with supplies, clocks, power domains, IOMMU, reserved memory and OPPs.
- **After booted Android read-only artifacts are available:** Capture exact effective DT/DTBO, VPU firmware image/hash, and relevant logs from that hardware revision. No flashing is required for this stage.
- **Once Linux boots:** Verify regulator/clock/IOMMU and firmware load; register V4L2 decoder; run `v4l2-compliance`, a VP9 3840x2160 test with GStreamer, then verify Chromium hardware decode and output path.
- **Important separation:** Hardware capability is not proof of working Linux support. 4K30 via the selected USB-C dock further depends on the DisplayPort bridge / dock and DRM output modes.

## Source inventory update needed

The 2026-10-11 hardware database earlier omitted the separate [Motorola kernel-video-devicetree](https://github.com/MotorolaMobilityLLC/kernel-video-devicetree) repository. Merge the confirmed source index, DT, firmware and outstanding-driver entries after selecting the verified branch/commit for the actual Razr Android firmware.
