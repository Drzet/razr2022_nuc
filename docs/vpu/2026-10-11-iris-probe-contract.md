# SM8475 Iris resource and UBWC provider audit (2026-10-11)

Kernel RFC source head: 7f1d729b6f458f1e76efe2894eb3c544bc9db856. Baseline: a5ebb76233b79db01e82e061173cb73c6d2b5c6b. Boot DTS reviewed at 3825dc6afb0f5e102845b32811ce0f518c0b4bbf. Source-only findings; no physical phone.

## Concrete missing UBWC probe prerequisite

The pinned drivers/media/platform/qcom/iris/iris_probe.c calls qcom_ubwc_config_get_data() before creating V4L2 nodes. The baseline drivers/soc/qcom/ubwc_config.c dispatches qcom_ubwc_configs using of_machine_get_match_data() and had **no qcom,sm8475** entry. Boot's oneli root declares compatible = "motorola,oneli", "qcom,sm8475", with no sm8450 fallback. That means Iris would fail probing with -EINVAL even if its board node and firmware were perfect.

At kernel commit 7f1d729b6f458f1e76efe2894eb3c544bc9db856 the VPU branch now adds [INFERRED] qcom,sm8475 to existing ubwc_4_0_hbb16. Independent Waipio/SM8475 vendor driver pins its default LPDDR5 config to UBWC_CONFIG(8,32,16,0,1,1,1), corresponding to upstream 8-channel, 32-byte MAL, HBB 16, swizzle levels 0/1/1 and bank spreading on the upstream UBWC 4.0 profile. Upstream qcom_ubwc_config_get_data() may override HBB using qcom_smem_dram_get_hbb(); oneli's actual SMEM value has not been measured.

Sources: upstream [ubwc_config.c](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/soc/qcom/ubwc_config.c), blob 23901a4c51f7305d95ac65e2a651fc557863a4ac; [ubwc.h](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/include/linux/soc/qcom/ubwc.h), blob f3a70360b177bbf5a9ff71b8730368cd3342e4e7; independent pinned [Waipio platform source](https://github.com/LowTension/android_kernel_xiaomi_sm8475/blob/39382bf760ccf05a8fb4dddee7138ecac02d4a59/techpack/video/driver/platform/waipio/src/msm_vidc_waipio.c) blob 362ff9402757fb247e96a26afa7fabd10e76b945. **[INFERRED] No Motorola runtime UBWC parameters were obtained.** GPU and Boot should review this shared SoC provider change.

## Probe resource contract reconciled

The candidate's iris_platform_vpu2.c has an unconditional two-stage power-domain request: venus/vcodec0 and mxc/mmcx (the latter with PD_FLAG_REQUIRED_OPP). iris_probe.c subsequently runs devm_pm_opp_set_config() and devm_pm_opp_of_add_table(). The earlier schema allowed only two power domains and omitted a mandatory OPP table. Commit 3d532ed35ab98ce45efe0be65f7ec165e27e2a4c **corrects the schema** to require exactly four power domains, their ordered names, and operating-points-v2.

The binding previously demanded exactly two IOMMU entries, inferred directly from the two downstream nonsecure bitstream/pixel context banks. No provider/consumer evidence establishes that translation. The same commit now accepts one or two IOMMU specifiers, with an explicit source-level uncertainty. This is not evidence that either option is correct. Boot must review upstream SMMU stream IDs and flags before a board node can be enabled.

Three clocks (iface, core, vcodec0_core), two resets (bus, core), two interconnects (cpu-cfg, video-mem), memory-region and a verified firmware-name remain part of the draft mainline driver/binding proposal. Firmware is signed and the correct Motorola filename/revision remains unknown.

## Isolation of remaining [INFERRED] platform data

| Candidate setting | What is justified | Remaining gate |
| --- | --- | --- |
| BW table | SM8250 benchmark table is *only* referenced by proposed sm8475_data; existing platforms unchanged | [INFERRED] bandwidth is not Waipio-validated; source-backed MBPS/DDR units missing |
| DMA mask | 0xe0000000 - 1 mirrors vendor pixel IOVA pool and existing VPU2 defaults | [INFERRED] effective SM8475 IOMMU domain/stream IDs, actual DMA aperture unverified |
| Four VPP pipes | Independent Waipio VPU_VERSION_IRIS2 profile specifies four | [INFERRED] actual Motorola HFI/capacity/thermal profile unverified |
| OPP corners | Names mxc/mmcx follow existing RPMh VIDEOCC dependencies and Iris resource pattern | [INFERRED] Motorola level mapping and required-opps frequencies not validated |
| UBWC payload | SM8475 Waipio default LPDDR5 source values match the chosen upstream UBWC v4 defaults | Runtime SMEM HBB and device-specific LPDDR tuning unknown |

**No shared board or SoC DTS was changed in VPU.** Boot owns disabled-node integration, and should not treat schema success as permission to enable video. Signed PAS 9 authentication, HFI init, actual V4L2 decode and Chromium playback remain untested until the handset becomes available.
