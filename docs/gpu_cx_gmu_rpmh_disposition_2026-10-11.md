# Oneli GPU A730v3: source-level GMU / CX / RPMh vote disposition

Date: 2026-10-11. Baseline `Drzet/linux` `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. GPU driver proposal `razr/gpu` `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`. Committed Boot OPP candidate `razr/boot` `9b37ea4953eada0837b18421ce6b74beebfe0a2b`. Evidence is **source inspection plus compiled DTB**, not Adreno runtime. No oneli firmware was loaded.

## Data inputs and actual driver consumption

The source-backed thirteen rates, GPU corners and vendor CX/ACD/bus fields are listed in [the first GPU followup](gpu_a730v3_second_pass_2026-10-11.md). Exact sources:

- [Motorola `cape-gpu.dtsi` at `90fa7be1db5bd47202673d4431408659149a7359`, levels 0–12](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-gpu.dtsi#L67-L245).
- [Upstream GPU/GMU OPP tables at baseline](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/arch/arm64/boot/dts/qcom/sm8450.dtsi#L2427-L2585): GPU OPPs overridden in Boot; GMU OPPs remain 200 MHz / LOW_SVS (64) and 500 MHz / SVS (128).
- [GMU ARC command-DB and OPP vote construction](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/gpu/drm/msm/adreno/a6xx_gmu.c#L1689-L1981); [Gen7 HFI table serialization](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/gpu/drm/msm/adreno/a6xx_hfi.c#L258-L356).

| Data / behaviour | Present in mainline baseline? | Consequence for the committed oneli OPP proposal |
|---|---|---|
| GPU frequency `opp-hz` | Yes, `gpu` OPP is read into `gmu->gpu_freqs` | Boot now includes exactly thirteen Cape frequencies, validated by compiled FDT |
| GPU RPMh corner `opp-level` | Yes, `a6xx_gmu_get_arc_level(&gpu->pdev->dev, gpu_freq)`; primary `gfx.lvl`, secondary `gmxc.lvl` when present or `mx.lvl` | Thirteen GPU corner values are correctly supplied in the Boot candidate; **physical RPMh command-DB level arrays remain unobserved** |
| Vendor per-GPU-frequency **CX corner** `qcom,cx-level` | **No direct equivalent** in the currently committed GPU OPP nodes or the Gen7 HFI performance-table layout. Separate `cx_arc_votes` are computed using the **GMU device's** 200/500 MHz OPP table and `cx.lvl`/`mx.lvl`. | The upstream layout has **three GMU frequency entries including zero**, not thirteen per-frequency CX votes. Vendor mappings cannot be claimed reproduced by the GPU OPP alone; review firmware and RPMh contract before GPU enablement |
| GPU extra MX dependency vote | Source has `dep_arc_votes`, but for A7xx non-A8xx HFI `a6xx_hfi_send_perf_table` writes GX and CX vote arrays and **does not serialize `dep_arc_votes`**; A8xx uses a separate table with a dependency field | Do not claim this independently mirrors the vendor `qcom,cx-level`; source proves a different packet layout |
| Vendor `qcom,acd-level` words | **Optional support already exists:** upstream `a6xx_gmu_acd_probe` reads `qcom,opp-acd-level` from OPP children; HFI enables ACD **only if the bitmask is nonzero**. No oneli `qcom,opp-acd-level` properties are committed | ACD is **not configured** by the current oneli proposal. Candidate source-derived mapping needs binding review and firmware agreement; do not silently copy proprietary KGSL ACD flags into unvalidated upstream HFI |
| Vendor IFPC capability | Upstream A730 profile at baseline **lacks `ADRENO_QUIRK_IFPC`**. `gmu->idle_level` is selected from this quirk, and A7xx power-config skips the legacy register setup | GMU stays on non-IFPC driver path. Vendor's IFPC capability is not automatically enabled. This is a bounded power/idle feature gap, not a proven boot/render blocker |
| Vendor DDR bus min/freq/max indexes | Upstream **has a hardcoded A730 HFI bandwidth table with 12 entries** (`a730_build_bw_table`), but the pinned A730 profile has no `.bcms` or `opp-peak-kBps` mappings. `a6xx_gmu_set_freq` initializes `bw_index = 0` and selects a nonzero index **only when** `info->bcms && gmu->nr_gpu_bws > 1`. | The fixed table **is sent** to GMU but DCVS requests from this profile carry **bandwidth index zero**; there is no per-frequency automatic mapping to vendor `qcom,bus-freq` indexes. Without translating source-verified OPP bandwidth votes and BCM resources, DDR scaling is a concrete performance/throughput gap. Do not assume vendor indexes correspond to the hardcoded mainline table without comparing encoded votes. |
| GMU and ZAP firmware | A730 entry expects `a730_sqe.fw`, `gmu_gen70000.bin`, board-specific signed `a730_zap`. Vendor Gen7-4-0 shares SQE/GMU/ZAP base names with Gen7-0-1 | Names match, but binary versions and Motorola signature acceptance remain untested. VPU owns one matching-build archive inventory |

### Concrete Adreno 730 DDR bandwidth path

[Upstream `a6xx_hfi.c` lines 672–741](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/gpu/drm/msm/adreno/a6xx_hfi.c#L672-L740) implement a **hardcoded twelve-level A730 HFI bandwidth table** using `SH0`, `MC0` and `ACV` command DB addresses. [Lines 788–834](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/gpu/drm/msm/adreno/a6xx_hfi.c#L787-L834) select this fallback when `.bcms` support is unavailable. In [`a6xx_gmu_set_freq` lines 153–242](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/gpu/drm/msm/adreno/a6xx_gmu.c#L153-L242), the bandwidth index defaults to **0** and is raised only by the optional `.bcms` path. Therefore the present oneli profile sends a usable-looking *fallback table* but never derives a nonzero frequency-based index from the Motorola `qcom,bus-freq` 2–11 annotations. That is a concrete driver/DT performance gap, not merely a generic concern. **[INFERRED]** Basic GPU command submission may still work while running at an unscaled/firmware-managed bandwidth state; throughput, underflow and power cannot be predicted without hardware.

We have **not** proven that vendor downstream bus-index 11 equals upstream hardcoded table index 11 or that the encoded downstream `SH0/MC0/ACV` votes have identical units. Reconcile those command-DB records and the vendor bus table before introducing a new driver mapping. In particular, using vendor indexes directly or inventing `opp-peak-kBps` values would be unsupported.

### Six real CX/GPU corner disagreements

All are **numeric RPMh levels**, not microvolts. Vendor's independent `qcom,cx-level` differs from its `qcom,level` at:

| GPU frequency MHz | GPU corner | Vendor CX corner |
|---:|---:|---:|
| 710 | SVS_L2 (224) | NOM (256) |
| 580 | SVS_L0 (144) | SVS_L1 (192) |
| 439 | LOW_SVS_L2 (96) | SVS (128) |
| 364 | LOW_SVS_L1 (80) | SVS (128) |
| 285 | LOW_SVS_D1 (56) | LOW_SVS (64) |
| 220 | MIN_SVS (48) | LOW_SVS (64) |

For the seven other rates the reported GPU and CX corner names match. Their equality **does not** imply that one upstream RPMh command also votes on both rails. [INFERRED] Applying GPU levels while the firmware independently applies higher CX minimums might be safe, but this cannot be established from source-only evidence. No unconditional CX/GPU equivalence is claimed.

### Additional specific upstream call-site concern

[GMU vote path lines 1690–1708, 1783–1831 and 1859–1869](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/gpu/drm/msm/adreno/a6xx_gmu.c#L1689-L1869) show:

```c
a6xx_gmu_rpmh_dep_votes_init(gmu->dev, gmu->dep_arc_votes,
                             gmu->gpu_freqs, gmu->nr_gpu_freqs);
```

Inside that function `a6xx_gmu_get_arc_level(dev, freqs[i])` searches **the passed device's** OPP table for an **exact** frequency, returns zero on failure, then chooses an MX corner index from `mx.lvl`. The inherited GMU 200/500 MHz OPPs do not intersect the Cape 220–900 MHz GPU OPPs. Therefore **with the currently documented tables this source path would look up every GPU frequency against the wrong-frequency GMU OPP table and use level 0 for each**. This is a reproducible source-level hazard, **not** a demonstrated oneli runtime regression. The resulting index also depends on the unknown command-DB `mx.lvl` contents. Crucially, the non-A8xx Gen7 HFI table does **not** transmit this dependent vote array; a code change to it is not justified solely by this finding. Keep this call-site marked for upstream review rather than introducing a speculative global-driver patch.

Separately, [`a6xx_gmu_probe` line 2459](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/gpu/drm/msm/adreno/a6xx_gmu.c#L2455-L2465) discards the return code from `a6xx_gmu_pwrlevels_probe(gmu)`. Since that helper returns errors on missing OPP / ARC resources, unsuccessful vote setup is not immediately propagated by this call site. This is a **source-identified error-handling risk** affecting generic A6xx/A7xx; review separately against upstream rather than silently modifying shared GPU initialization for the oneli chip-ID patch.

## Revision-specific quirks and actionable disposition

The pinned vendor [Gen7-0-1 vs Gen7-4-0 catalogs](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/9511d6b2dc469e5bd836992e3bdd6d19ace112e0/drivers/gpu/msm/adreno-gpulist.h#L1986-L2043) have identical supported feature bitsets and table names for hardware clock gating, GBIF, protected registers, GMEM and base firmware. The pinned upstream [A730 record](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/gpu/drm/msm/adreno/a6xx_catalog.c#L1480-L1503) has more conservative quirks and a different generic-clock/power programming implementation. **No vendor-specific Gen7-4-0 register programming override is evidenced by the two vendor catalog records themselves.** [INFERRED] A730 reuse for first render-node bring-up remains defensible, but it is not proof of full programming-table equivalence.

**One specific vendor Gen7-4-0 initialization operation is demonstrably absent from the upstream A730-specific code path.** In [pinned Motorola `adreno_gen7.c` lines 517–526](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/9511d6b2dc469e5bd836992e3bdd6d19ace112e0/drivers/gpu/msm/adreno_gen7.c#L517-L526), the same prefetch workaround is enabled for Gen7-0-0, Gen7-0-1 **and Gen7-4-0**: it writes `0x1` to `GEN7_CP_CHICKEN_DBG`, `GEN7_CP_BV_CHICKEN_DBG` and `GEN7_CP_LPAC_CHICKEN_DBG`, with a comment explaining that CP I-cache prefetch brings no benefit on these generations. [Pinned mainline `a6xx_gpu.c` lines 1385–1396](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/gpu/drm/msm/adreno/a6xx_gpu.c#L1385-L1396) writes the CP chicken register for **A660/A690** or **A702**, but not the A730 profile; the two BV/LPAC writes are not present in that mainline branch at those code paths. This is a **concrete source difference**, not proof of failure: [INFERRED] it might influence command-processor prefetch behaviour/performance. The same vendor operation applies to Gen7-0-1 and Gen7-4-0, so it is **not a unique silicon-v3 quirk**, and a possible upstream adaptation belongs in a separately reviewed patch with verified register definitions, rather than piggybacking on the chip-ID match change.

Concrete deferred operations, not generalized "unknown compatibility":

1. Confirm source/hosted archive contains Motorola oneli's **signed** ZAP and exact SQE/GMU binary versions with hashes, and which path is appropriate for the native board DT; then test SCM authorization later.
2. Confirm actual GMU firmware responds to current HFI performance, bandwidth, start and idle messages, RPMh `gfx.lvl`/`cx.lvl`/`mx.lvl`/`gmxc.lvl` auxiliary data and 200/500 MHz GMU levels. A compiled module cannot test this.
3. Source-review and, only if supported, express vendor CX floor, ACD level and DDR bandwidth semantics in upstream binding/driver. The current thirteen `opp-level` properties do **not** encode these.
4. Enable and test IFPC only through supported upstream quirks/firmware handshake after stable baseline rendering, rather than copying downstream vendor flags into upstream C code.
5. Confirm exact HWCG, GBIF, protected-register and preemption behaviour with a running Adreno 730v3. Vendor record identity alone does not validate those sequences.

**Integration decision:** accept the current GPU OPPs as a **disabled source-backed DT candidate** and the chip-ID patch as an isolated match fix. Do not enable the GPU or rework global GMU vote algorithms based on source-only inference. The next module CI run must pass with normal modpost, and stock firmware acceptance needs device testing later.

## Target device evidence update

The [2026-10-11 stock ADB capture](oneli_stock_android14_adb_hardware_capture_2026-10-11.md) establishes **XT2251-1 PVT, hwrev 0xC000, SKU dn**, Android 14 build `U2SLS34.1-42-14-11`. Stock's `renderD128` is registered under its display DRM device. **This does not establish Mesa / upstream Adreno acceleration**. The phone is disconnected, and no device-side GPU runtime test was performed. VPU owns the public stock image matching that version; no duplicate archive download was performed.
