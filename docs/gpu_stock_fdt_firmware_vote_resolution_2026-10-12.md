# GPU canonical evidence resolution: compiled stock levels, HFI DDR table, ZAP loader

**Date:** 2026-10-12. **Status:** this report **supersedes** [2026-10-12 GPU partial-export audit](gpu_firmware_fdt_vote_audit_2026-10-12.md) and earlier [CX/bandwidth proposal](gpu_cx_bandwidth_mapping_contract_2026-10-11.md) where they called the compiled-FDT values unexported or the HFI index correspondence unverified. This is a bounded *new-evidence* analysis, not another generic review. CPU/GMU firmware authentication, bootloader-effective FDT and actual phone electrical levels remain untested.

## Accepted new inputs: VPU owns and has published these exact artifacts

- [VPU focused compiled-property JSON](vpu/evidence/focused-stock-properties.json): source Git blob `664268b7bb6a8587b24eeb69909b1574db6ffb9e`; 803,197 bytes, SHA256 `f1bb6f41036aeb2e04ac289cfa803aab686cf92097a77444c9ed50c96397fe48` per successful [CI 38291543595](https://github.com/Drzet/razr2022_nuc/actions/runs/38291543595). Exact upstream inputs: public stock ZIP SHA256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`; `vendor_boot.img` SHA256 `1c27e22565f6f50919812bfcb5254cea2f3b629d98f5c26a7b54f5ece452036e`, two standalone base FDTs, MSM ID `530/65536` and `540/65536`, original FDT SHA256 `8e269672cd9d77da8575bf201c646c966219064cc0f9001bf512e7bf47455652` and `b8a243a0ae0569e64dfc85bc5ee15e2eeddf65aa2f4df406c24a8467e739c843`. Export contains exact per-property bytes, u32 arrays and hashes, **not a reconstructed effective handset FDT**. 156 focused nodes in each base have byte-identical properties, although their entire original binary FDTs differ.
- [VPU qualified MDT/ZAP bounds JSON](vpu/evidence/qualified-mdt-loader-bounds.json), Git blob `28c4d1971f3c1830320cf0f8e8f20637ba34df27`; [CI 38292192600 PASS](https://github.com/Drzet/razr2022_nuc/actions/runs/38292192600). This replays pinned Qualcomm `qcom_mdt_get_size`, split-segment and TYPE_HASH behavior against exact reference radio hashes, **without publishing firmware bytes**. Use the VPU metadata as canonical, not a parallel extraction.
- GPU driver under test is **unchanged** [`Drzet/linux` GPU kernel `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`](https://github.com/Drzet/linux/commit/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3), prior full ARM64 [Image/modules + normal modpost PASS run 38178986611](https://github.com/Drzet/razr2022_nuc/actions/runs/38178986611); no rebuild needed.

## Every missing GPU field now recovered and checked, both base FDTs agree

All cells below were read from **both actual compiled base FDT property exports** at `/soc/qcom,kgsl-3d0@3d00000/qcom,gpu-pwrlevels/qcom,gpu-pwrlevel@N`, not copied from a source DTS. Both contain all seven requested named u32 fields for each of 13 levels and **all 13 complete rows agree**. `GX` is `qcom,level`, `CX` is `qcom,cx-level`; `DDR` is `qcom,bus-freq` index, with `min/max` bounds, not an encoded HFI command. `ACD` is opaque and **not** an RPMh corner.

| Level | GPU MHz | GX | CX | DDR index | Min | Max | ACD u32 |
|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | 900 | 416 | 416 | 11 | 11 | 11 | `0x882b5ffd` |
| 1 | 862 | 384 | 384 | 11 | 11 | 11 | `0x882b5ffd` |
| 2 | 815 | 320 | 320 | 11 | 10 | 11 | `0x882b5ffd` |
| 3 | 765 | 256 | 256 | 10 | 9 | 11 | `0x882c5ffd` |
| 4 | 710 | 224 | **256** | 10 | 6 | 11 | `0x882c5ffd` |
| 5 | 645 | 192 | 192 | 8 | 6 | 9 | `0x882d5ffd` |
| 6 | 580 | 144 | **192** | 8 | 6 | 9 | `0x882e5ffd` |
| 7 | 515 | 128 | 128 | 6 | 6 | 8 | `0x882e5ffd` |
| 8 | 439 | 96 | **128** | 6 | 3 | 8 | `0xc0285ffd` |
| 9 | 364 | 80 | **128** | 3 | 1 | 6 | `0xc0285ffd` |
| 10 | 324 | 64 | 64 | 2 | 1 | 6 | `0xc02a5ffd` |
| 11 | 285 | 56 | **64** | 2 | 1 | 5 | `0xc02c5ffd` |
| 12 | 220 | 48 | **64** | 2 | 1 | 5 | `0xc8285ffd` |

At the GPU parent, both base FDTs have `qcom,chipid=0x07030002`, `qcom,initial-pwrlevel=11`, `qcom,ubwc-mode=4`, `qcom,min-access-length=32`, `qcom,bus-table-cnoc=[0,100]`, and `qcom,bus-table-ddr` **raw u32 values** `[0,781250,1761718,2136718,2660156,3000000,6074218,6671875,8171875,10687500,12484375,13085937]`. These match the pinned [Motorola `cape-gpu.dtsi`](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-gpu.dtsi) source (integer-truncated `MHZ_TO_KBPS(mhz,4)`) and Boot's previous 13 GX OPP values, but **the published stock binaries now independently confirm both tables**.

The GMU node retains `iommus=<546 5 0x400>`, `qcom,iommu-dma="disabled"`, `vdd-supply=<556>` (GPU GX GDSC) and `vddcx-supply=<545>` (GPU CX GDSC); these are stock consumer/provider references **not** per-frequency RPMh level commands. Hardware board matching is still unknown.

## New decisive DDR table equivalence: 12 / 12 HFI entries mathematically match stock

I independently compared **each u32** of the two new compiled-FDT DDR tables against the unchanged pinned kernel's [`a6xx_hfi.c::a730_build_bw_table`](https://github.com/Drzet/linux/blob/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3/drivers/gpu/drm/msm/adreno/a6xx_hfi.c#L680-L734), rather than merely noticing that the two tables happen to have 12 entries.

For every **nonzero** stock DDR bandwidth integer `B` at vendor index `i` from 1 through 11, the HFI command words match **exactly**:

```text
A730_HFI_SH0[i] = 0x60000000 | floor(B / 1050)
A730_HFI_MC0[i] = 0x60000000 | floor(B /  800)
A730_HFI_ACV[i] = 0x60000008
```

Index 0 instead has `SH0=MC0=ACV=0x40000000` (off). These factors are **algebraic relationships between two source datasets**, not independently measured command-DB bus widths or proof of hardware transfer rate. All twelve command triples, including the off entry, match the above integer computation exactly:

| Index | Compiled stock DDR B | Upstream HFI SH0 low vote | Upstream HFI MC0 low vote | Result |
|---:|---:|---:|---:|---|
| 0 | 0 | off | off | MATCH |
| 1 | 781250 | 744 | 976 | MATCH |
| 2 | 1761718 | 1677 | 2202 | MATCH |
| 3 | 2136718 | 2034 | 2670 | MATCH |
| 4 | 2660156 | 2533 | 3325 | MATCH |
| 5 | 3000000 | 2857 | 3750 | MATCH |
| 6 | 6074218 | 5784 | 7592 | MATCH |
| 7 | 6671875 | 6354 | 8339 | MATCH |
| 8 | 8171875 | 7782 | 10214 | MATCH |
| 9 | 10687500 | 10178 | 13359 | MATCH |
| 10 | 12484375 | 11889 | 15605 | MATCH |
| 11 | 13085937 | 12462 | 16357 | MATCH |

**Updated decision:** unlike the older report, the fixed A730 HFI *table row numbers* now have **strong, exact cross-source correspondence** with Motorola's compiled stock `qcom,bus-table-ddr` row numbers. This is enough to propose an index mapping for a narrowly scoped **SM8475 A730v3** frequency profile, without recreating/guessing BCM numeric words. It does **not** prove that a stock runtime GMU uses those HFI commands or that dynamic bus scaling is already enabled.

**Critical missing actual selection code:** [`a6xx_gmu.c::a6xx_gmu_set_freq`](https://github.com/Drzet/linux/blob/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3/drivers/gpu/drm/msm/adreno/a6xx_gmu.c#L155-L225) initializes `bw_index=0` and only selects a nonzero index inside `if (info->bcms && gmu->nr_gpu_bws > 1)`. Current shared A730 catalog has **no `.bcms`**, so a normal Gen7 `HFI_H2F_MSG_GX_BW_PERF_VOTE` goes out with BW index zero; the 12 hardcoded HFI rows are sent at startup but **not selected from the vendor per-GPU pwrlevels** by this path. With zero, it also calls `dev_pm_opp_set_opp`; Boot's disabled candidate currently has GX OPPs only, not source-approved bandwidth entries.

**Minimal *separate future* implementation proposal** (after Boot/Power design review, not applied now):
1. Restrict to exact `0x07030002` A730v3 or a verified board-specific capability; never apply vendor levels indiscriminately to shared SM8450 A730 `0x07030001`.
2. Represent per-frequency source-backed **peak KB/s** using supported OPP/interconnect properties *if* the binding/consumer semantics are verified; associate each OPP bandwidth with **one of the exact 12 fixed A730 HFI rows** by equality to the compiled stock table. Alternatively add an explicitly described platform HFI index table, after binding review. Avoid abusing `.bcms` merely to enter generic `a6xx_gmu_rpmh_bw_votes_init`, which generates a *different* votes path and requires runtime command-DB parameters.
3. Ensure index zero/off, validation for missing/unsorted/duplicate levels, normal HFI acknowledgement, suspended path, idle updates and `dev_pm_opp_set_opp` transition behavior are reviewed. Source `bus-min/max` are dynamic governor clamps, *not* automatically peak throughput. Reject any DTS values outside 0–11.
4. Hold actual driver patch/enablement until the selected per-OPP ABI and interaction with existing OPP/interconnect consumer are agreed. A **12/12 exact proof narrows the blocker to index selection and firmware acceptance**, not table numerical equivalence.

## CX floor: compiled source confirms six divergences, but host vote ABI still missing

`qcom,cx-level` exceeds `qcom,level` for **710,580,439,364,285,220 MHz**. The [mainline GMU ARC vote builder](https://github.com/Drzet/linux/blob/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3/drivers/gpu/drm/msm/adreno/a6xx_gmu.c#L1689-L1857) builds GX votes from the GPU OPP `opp-level` using `gfx.lvl` and `gmxc.lvl` or `mx.lvl`, while separate CX votes are derived from **GMU-frequency OPPs** using `cx.lvl`, not from the stock per-GPU `qcom,cx-level`. The inherited GMU OPP profile at 200/500 MHz levels 64/128 cannot on its own express per-GPU CX floors 192–416.

**CX decision stays HOLD:** nothing in the new signed ZAP/SQE/GMU location/hash manifests discloses per-state firmware-enforced CX floors, `cx.lvl` physical mapping, or correct HFI table packing. Do not replace GPU GX levels with CX levels, guess `required-opps` cross-rail requirements, or program host RPMh/ACD values from unverified assumptions. Obtain actual dynamic rail vote ownership/command-DB data or hardware traces before enacting. This does **not** delay combined Image/modules with disabled GPU.

## Signed A730 ZAP loader: previous “all three Bxx mandatory” assertion corrected

VPU [qualified loader replay](vpu/evidence/qualified-mdt-loader-bounds.json) verified source `image/a730_zap.mdt`: 4,044 bytes SHA256 `f5d8a41c1380ba2b42cd742538083306d245471ac5d51139e3bc8a6168ce84d2`, **3 ELF32 program headers**, Qualcomm relocatable flag, host `qcom_mdt_get_size=0x1000` (4 KiB), fitting stock `gpu_microcode_region@8b91a000` **0x2000** (8 KiB). Host split load requires **one** indexed PT_LOAD companion `a730_zap.b01` exactly 2,236 bytes SHA256 `1fc98f97cf354b9704b20d0848f7b2739638539a57d88ecf5cc71ca1c5c4e6b9`. Hash-program-header index 2 metadata is already **packed in the MDT** (3,896 bytes), so `.b02` is not another `qcom_mdt_load` file request; `.b00` exists in stock but is not a required loadable program-header segment. Recovered file provenance remains VPU-owned `radio.img/SINGLE_N_LONELY/NON-HLOS.bin/Android sparse/ext4/image/`, archive SHA256 `620117...`.

**Exact minimal future Linux firmware install set for the pinned kernel:** `/lib/firmware/qcom/oneli/a730_zap.mdt` and sibling `/lib/firmware/qcom/oneli/a730_zap.b01`, with Boot-owned `zap-shader { firmware-name = "qcom/oneli/a730_zap.mdt"; memory-region = <&gpu_microcode_mem>; }` when **board GPU is permitted**. The original `.b00` and `.b02` can be preserved for full vendor archive completeness but are not mandatory kernel loader requests. This is **not** evidence of SCM PAS authorization; do not enable GPU or claim binary signing acceptance.

Generic SQE + GMU request-name/format/hash paths remain as previously recorded in [firmware consumer report](gpu_shared_firmware_consumer_2026-10-11.md): reference `a730_sqe.fw` 74,676 B SHA256 `e67d1829f57fc8326d806234b932dc3b78e28a9940df34c70752f17d5f38b7aa`; reference `gmu_gen70000.bin` 57,272 B SHA256 `b2d3f0e2a98fd6259ab9ffef16df63265542e6cc9a970d53d476e823d432042a`. Name compatibility is established; bytes/GMU handshake on target not verified. No re-download or duplicate stock manifest introduced.

## Reproducible independent evidence-only CI

New [`scripts/check-gpu-stock-hfi-crosswalk.py`](../scripts/check-gpu-stock-hfi-crosswalk.py) uses SHA-pinned VPU focused-property JSON, qualified ZAP loader metadata and the pinned current GPU kernel `a6xx_hfi.c`. It fails on missing fields, MSM530/MSM540 disagreement, nonzero indexes outside vendor bounds, non-exact HFI SH0/MC0/ACV encoded values, or changed ZAP MDT segment/load constraints. **No kernel compilation or full ROM download.**

[Run 38297688741](https://github.com/Drzet/razr2022_nuc/actions/runs/38297688741) **COMPLETED SUCCESS**, exact tested project SHA `3b6a6d0f174aa0c576f93a8aeca2822442909723`. Job `114972644855` logged all three passes: 13×7 FDT fields for both bases; exact 12/12 encoded HFI DDR values; ZAP requires `.b01` and fits 4 KiB into 8 KiB. [Artifact `gpu-stock-hfi-crosswalk-38297688741` (ID 11768914259)](https://github.com/Drzet/razr2022_nuc/actions/runs/38297688741/artifacts/11768914259) contains machine-readable matched rows, SHA256 of fetched sources, pinned commits and stdout; uploaded ZIP SHA256 **`75dbdce400071437ce838fd610700e5aa062edc841bd4bc1291cead9f25b9a72`**. This is a **source metadata validation**, neither kernel module/hardware vote validation nor SCM acceptance.

## Acceptance, integration and stop

**PASS (source evidence):** all 13x7 power-level raw fields match between both compiled bases; stock 12-u32 DDR table matches; A730 HFI SHA/MC/ACV fixed table matches **all 12** stock indices exactly via the displayed integer formulas; qualified host ZAP split relocation/size accepted by VPU. **No new kernel code/DT change**; original GMU return fix `3baaec...` already strict full module build PASS. **NO phone test**. Prior [GPU fourth-round handoff](handoffs/gpu-2026-10-11-fourth-pass.md) has historical evidence; future consumers should use *this* canonical report first. Boot owns board GPU disabled pending power/CX contract; coordinator's minimal combined build can proceed without this optional feature.
