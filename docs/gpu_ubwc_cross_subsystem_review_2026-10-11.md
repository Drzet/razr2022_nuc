# GPU/display review of VPU's SM8475 shared UBWC SoC mapping

Date: 2026-10-11. VPU kernel commit under review: `7f1d729b6f458f1e76efe2894eb3c544bc9db856` (`drivers/soc/qcom/ubwc_config.c` only for this commit). GPU kernel remains on its own branch. Sources pinned to exact revisions; **all conclusions are source-level, not phone-tested**.

## Verdict: acceptable as a shared, provisional SoC match

The VPU patch adds:

```c
{ .compatible = "qcom,sm8475", .data = &ubwc_4_0_hbb16, },
```

to [`qcom_ubwc_configs[]`](https://github.com/Drzet/linux/blob/7f1d729b6f458f1e76efe2894eb3c544bc9db856/drivers/soc/qcom/ubwc_config.c). Boot's source-backed oneli root uses `"motorola,oneli", "qcom,sm8475"`, without `qcom,sm8450` fallback. Before this patch, [`of_machine_get_match_data(qcom_ubwc_configs)`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/soc/qcom/ubwc_config.c) would have no SM8475 match and return `-EINVAL` whenever SMEM is available and a consumer requested the provider. This **also affects GPU and display**, not only Iris.

The [independent pinned Waipio SM8475 vendor source](https://github.com/LowTension/android_kernel_xiaomi_sm8475/blob/39382bf760ccf05a8fb4dddee7138ecac02d4a59/techpack/video/driver/platform/waipio/src/msm_vidc_waipio.c#L3287-L3290) explicitly says default `UBWC_CONFIG(8, 32, 16, 0, 1, 1, 1)` for LPDDR5. Motorola's pinned [Cape GPU description](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-gpu.dtsi#L31-L35) independently specifies UBWC mode 4 and minimum access length 32. The existing upstream [`ubwc_4_0_hbb16` profile](https://github.com/Drzet/linux/blob/7f1d729b6f458f1e76efe2894eb3c544bc9db856/drivers/soc/qcom/ubwc_config.c) has version `UBWC_4_0`, HBB 16, no disable-swizzle flags.

## Consumer-by-consumer field check

With default HBB 16 and no SMEM override, the shared helpers in pinned [`include/linux/soc/qcom/ubwc.h`](https://github.com/Drzet/linux/blob/7f1d729b6f458f1e76efe2894eb3c544bc9db856/include/linux/soc/qcom/ubwc.h) produce:

| Property | Shared provider computation | GPU (Adreno DRM) | Display (MDSS/DPU) | Iris VPU (HFI Gen2) |
|---|---|---|---|---|
| Encoding | `UBWC_4_0` (`0x40000000`) | [`a6xx_set_ubwc_config`](https://github.com/Drzet/linux/blob/7f1d729b6f458f1e76efe2894eb3c544bc9db856/drivers/gpu/drm/msm/adreno/a6xx_gpu.c#L748-L809) enables v4-family RBG565 predictor and AMSBC | [`msm_mdss_6x_setup_ubwc`](https://github.com/Drzet/linux/blob/7f1d729b6f458f1e76efe2894eb3c544bc9db856/drivers/gpu/drm/msm/msm_mdss.c#L199-L224) reports version tag 2 and prediction mode 1 | HFI packets are assembled from common helper values; codec firmware must accept v4 geometry |
| Channel count | UBWC version >= 3.1 -> macrotile mode true -> **8** | Uses macrotile bit in GPU noncompressed mode config | MDSS macrotiling enabled | `HFI_PROP_UBWC_MAX_CHANNELS = 8` |
| Minimum access length | Only UBWC 1.0 uses 64; v4 -> **32 bytes** | 32-byte selection | 32-byte bit selection | `HFI_PROP_UBWC_MAL_LENGTH = 32` |
| Highest bank bit | **16** default | GPU encodes HBB offset `16 - 13 = 3` into registers | MDSS encodes the same offset 3 | `HFI_PROP_UBWC_HBB = 16` |
| Swizzle level 1/2/3 | No disable flags, v4 -> **0/1/1** | Level 2 remains enabled | UBWC static register consumes common swizzle bits | Gen2 HFI gets `0,1,1` |
| Bank spreading | Common helper returns **1** | GPU programmed relevant v4 mode bits | MDSS enables bank-spread bit | `HFI_PROP_UBWC_BANK_SPREADING = 1` |

Consumer provenance: [Adreno GPU init provider call](https://github.com/Drzet/linux/blob/7f1d729b6f458f1e76efe2894eb3c544bc9db856/drivers/gpu/drm/msm/adreno/a6xx_gpu.c#L2778-L2788), [MDSS provider call](https://github.com/Drzet/linux/blob/7f1d729b6f458f1e76efe2894eb3c544bc9db856/drivers/gpu/drm/msm/msm_mdss.c#L374-L386), [DPU KMS provider call](https://github.com/Drzet/linux/blob/7f1d729b6f458f1e76efe2894eb3c544bc9db856/drivers/gpu/drm/msm/disp/dpu1/dpu_kms.c#L1183-L1194), and [Iris HFI Gen2 packet assignments](https://github.com/Drzet/linux/blob/7f1d729b6f458f1e76efe2894eb3c544bc9db856/drivers/media/platform/qcom/iris/iris_hfi_gen2_packet.c#L124-L212).

### SMEM boundary and build ownership

The provider first checks `qcom_smem_is_available()`; without SMEM it returns `-EPROBE_DEFER`. If `qcom_smem_dram_get_hbb()` returns a valid value, **it overrides the static HBB 16** in a cached copy. If SMEM reports `-ENODATA`, it uses the static default 16. Other negative errors propagate. Thus cross-subsystem agreement holds because all three consumers use the **same actual HBB result**; this does **not** prove it is the correct physical setting for the actual oneli RAM controller.

**[INFERRED]** LPDDR5 and the independent Waipio default might not cover a Motorola-specific DRAM configuration, bin or memory SKU. The stock ADB session did not measure HBB, resolved root UBWC parameters, GPU compressed-buffer import, or VPU firmware ACKs. GPU's [UBWC initialization](https://github.com/Drzet/linux/blob/7f1d729b6f458f1e76efe2894eb3c544bc9db856/drivers/gpu/drm/msm/adreno/a6xx_gpu.c#L748-L810) asserts HBB >= 13, so an invalid SMEM value would be an independent safety/probe concern for actual hardware.

### Integration recommendation

- **Accept the `qcom,sm8475` -> `ubwc_4_0_hbb16` match as a separately reviewable SoC prerequisite** for GPU, MDSS/DPU and Iris. Existing SM8450 uses the exact same payload, so the change is conceptually minimal.
- **Do not cherry-pick unready VPU/Iris RFC commits solely to obtain UBWC**. VPU's change is the standalone tip commit `7f1d729b...`, but cherry-picking that one isolated commit onto coordinator integration (subject to normal conflict/build checks) is distinct from endorsing the earlier VPU driver series. The coordinator should retain its original attribution and `[INFERRED]` status.
- Maintain GPU and VPU disabled while firmware and CX/GMU resources are unproven; enabling an MDSS node also needs Boot's independent KMS/DP/DSI contracts.
- When a usable reference DT and phone become available, compare SMEM HBB, memory profile and DRM/V4L2 UBWC buffers across GPU/display/VPU. Before then, no alternate invented HBB/swizzle patch is warranted.

**Conclusion:** VPU's UBWC change is a useful shared minimum; its helper-derived fields are internally consistent with source-pinned Waipio and Motorola GPU UBWC v4 defaults. The confidence limit is hardware LPDDR5/SMEM configuration and firmware HFI acceptance, not a source mismatch among the three Linux consumers.
