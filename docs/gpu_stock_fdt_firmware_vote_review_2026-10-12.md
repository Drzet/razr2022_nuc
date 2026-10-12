# GPU: six-FDT power/ICC evidence reconciled with recovered oneli firmware

**Date:** 2026-10-12. **Owner:** GPU, `razr/gpu`. This closes the source-only fourth-round GPU assignment; it does **not** enable the GPU or establish firmware acceptance. Upstream baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`, GPU branch head `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`, Boot DTS integration reference `525b504b82dbca593a9a697af9be63f53915e0a3`. Physical stock observation: oneli PVT hwrev 0xc000, Android14 build `U2SLS34.1-42-14-11`; public package matching that build label is **not** a verified phone flash dump.

## Verified inputs and scope

- VPU completed [six-FDT export run 38220276125](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125), [raw-property artifact 11734430639](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125/artifacts/11734430639). Original `stock-per-fdt-property-export.json`: **15,862,099 bytes**, SHA256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`; artifact ZIP SHA256 `485ff37b87cff2e6432928cfd4c0d4168bb3c10af163f6e68b6adfba35a528ae`. **Independently downloaded, extracted and recomputed both hashes in this GPU round** (no repeat ROM download). Also checked [compact metadata](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-12-oneli-stock-fdt-properties.json).
- VPU recovered [radio/NON-HLOS firmware](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-11-radio-non-hlos-firmware-manifest.json) and [vendor_a firmware](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-11-stock-filesystem-firmware-manifest.json). Parent public ZIP SHA256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c` (4,353,164,507 bytes). This review consumes committed file-hash metadata, **not** firmware bytes.
- For numeric pwrlevel comparison, pinned Motorola [`qcom/cape-gpu.dtsi`](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-gpu.dtsi), `90fa7be1db5bd47202673d4431408659149a7359`. For host interpretation: [`a6xx_gmu.c`](https://github.com/Drzet/linux/blob/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3/drivers/gpu/drm/msm/adreno/a6xx_gmu.c), [`a6xx_hfi.c`](https://github.com/Drzet/linux/blob/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3/drivers/gpu/drm/msm/adreno/a6xx_hfi.c), [`adreno_gpu.c`](https://github.com/Drzet/linux/blob/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3/drivers/gpu/drm/msm/adreno/adreno_gpu.c).

## The exported GPU/GMU structures: what is truly present

Independent inspection of the **full** 15.86 MB artifact, not just its compact report, finds:

| Item | vendor_boot base FDT MSM ID 530 | vendor_boot base FDT MSM ID 540 | Consequence |
| --- | --- | --- | --- |
| FDT SHA256 | `8e269672cd9d77da8575bf201c646c966219064cc0f9001bf512e7bf47455652` | `b8a243a0ae0569e64dfc85bc5ee15e2eeddf65aa2f4df406c24a8467e739c843` | **Two separately extracted, uncomposed** base candidates. |
| `/soc/qcom,kgsl-3d0@3d00000` | `status="ok"`, compatible `qcom,adreno-gpu-gen7-4-0`, model `Adreno730v3` | Same selected values | Mainline's `0x07030002` catalog addition has Motorola source support; no live rendering claim. |
| `/qcom,gpu-pwrlevels/qcom,gpu-pwrlevel@0..12` | **13 numeric-indexed child nodes** with exported `reg=0..12` | Same | Confirms table cardinality/indexing, **not** numerical OPP values. |
| GMU `/soc/qcom,gmu@3d69000` | `qcom,gen7-gmu`; two IRQs, IOMMU cells `<546 5 0x400>`, `vddcx-supply=<545>`, `vdd-supply=<556>` | Same | Real stock GMU separate CX and GX-linked power supplies. Inherited mainline GMU source uses a different driver binding/layout. |
| GPU `interconnects` | `<75 21 72 512>`, with `interconnect-names="gpu_icc_path"` | Same | Provider phandles 75 `gem_noc`, 72 `mc_virt`, translation to mainline `MASTER_GFX3D -> SLAVE_EBI1`; `21` and `512` are **specifier IDs**, not generic phandle references. |
| `zap-shader/memory-region` | phandle **555** | Same | Resolves to `/reserved-memory/gpu_microcode_region@8b91a000`, base **0x8b91a000**, size **0x2000** (8192). Inherited mainline `gpu_micro_code_mem` has **identical address and size**; signed payload/load span still needs checked. |
| Overlay FDTs 0–3 | No matching KGSL/GMU nodes in the **exported** overlay node indexes | same observation | Does **not** prove absence of changes outside the requested projection or which base/overlay bootloader selects; PVT board-id `0x45/c000` points to **overlay 3 as candidate**, not confirmed runtime choice. |

**Important export limitation:** the exporter retained only selected requested properties. For each of the 13 GPU pwrlevel children, its `properties` dictionary contains **only `reg`**. The GPU parent record omits `qcom,chipid`, `qcom,initial-pwrlevel`, `qcom,bus-table-ddr`, `qcom,bus-table-cnoc`, `qcom,ubwc-mode` and `qcom,min-access-length`; each child record omits `qcom,gpu-freq`, `qcom,level`, `qcom,cx-level`, `qcom,bus-freq`, `qcom,bus-min`, `qcom,bus-max`, `qcom,acd-level`. The full file is **not** a lossless DTB and these omissions **must not** be reported as properties absent in stock. There is no raw-property SHA for those omitted fields. A **focused export extension** from VPU's existing parser/member workflow is the only way to confirm compiled binary values. Do not repeat the 4.35 GB download or assume the Motorola source was exactly the stock deployed configuration.

## Newly resolved CX/GX regulator chains

The exported base numeric phandles can be joined against its own `node_index`, without treating all integer cells as phandles:

```text
GMU vddcx-supply = 545
  -> /soc/qcom,gdsc@3d99108 (parent-supply=30)
  -> /soc/rsc@17a00000/rpmh-regulator-cxlvl/regulator-pm8350c-s6-level
     -> parent resource qcom,resource-name = "cx.lvl"
     -> qcom,init-voltage-level=384, qcom,proxy-consumer-voltage=<384 65535>

GMU vdd-supply = 556
  -> /soc/qcom,gdsc@3d9905c (parent-supply=53)
  -> /soc/rsc@17a00000/rpmh-regulator-mxclvl/regulator-pm8350c-s2-gfx-voter-level
     -> parent resource = "mxc.lvl"
     -> named gfx voter has *additional* parent-supply=69
     -> /soc/rsc@17a00000/rpmh-regulator-gfxlvl/regulator-pm8350-s5-level
        -> resource "gfx.lvl"
```

The stock **CX** RPMh regulator's `qcom,init-voltage-level=384` and proxy-consumer range `<384 65535>` are verified source bytes; the **GFX** regulator's init level is 16 and MXC gfx voter's init level is 48. These are **initial/proxy votes**, not a per-frequency policy and not microvolts despite some downstream regulator property names. `0x400` on stock SMMU specifiers is not translated into presumed identical upstream semantics here.

**Interpretation:** the physical reference topology has distinct CX and graphics-voter/MXC/GFX supply chains. It does **not** answer whether stock GMU firmware maintains a high CX floor across GPU DVFS changes after proxy initialization. Mainline [`a6xx_gmu_rpmh_votes_init`](https://github.com/Drzet/linux/blob/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3/drivers/gpu/drm/msm/adreno/a6xx_gmu.c#L1834-L1875) queries `gfx.lvl`, `cx.lvl`, `mx.lvl` and optionally `gmxc.lvl`; the stock regulator path names **do not** supply live command-DB index/value arrays or an equivalence between `mxc.lvl` and `gmxc.lvl`.

## Source-defined GPU/CX/DDR values pending binary property confirmation

Numerical data below are from **pinned Motorola DTS source**, **not from the filtered FDT export**. Values are RPMh corner IDs, not voltage units. The DDR column is a downstream index and not a mainline HFI vote number.

| GPU MHz | GX `qcom,level` | CX `qcom,cx-level` | DDR freq/min/max indexes |
| ---: | ---: | ---: | :--- |
| 900 | 416 | 416 | 11 / 11 / 11 |
| 862 | 384 | 384 | 11 / 11 / 11 |
| 815 | 320 | 320 | 11 / 10 / 11 |
| 765 | 256 | 256 | 10 / 9 / 11 |
| 710 | 224 | 256 | 10 / 6 / 11 |
| 645 | 192 | 192 | 8 / 6 / 9 |
| 580 | 144 | 192 | 8 / 6 / 9 |
| 515 | 128 | 128 | 6 / 6 / 8 |
| 439 | 96 | 128 | 6 / 3 / 8 |
| 364 | 80 | 128 | 3 / 1 / 6 |
| 324 | 64 | 64 | 2 / 1 / 6 |
| 285 | 56 | 64 | 2 / 1 / 5 |
| 220 | 48 | 64 | 2 / 1 / 5 |

The pinned vendor `qcom,bus-table-ddr` entries indexed 0–11 use MHz-like values `0,200,451,547,681,768,1555,1708,2092,2736,3196,3350` via `MHZ_TO_KBPS(mhz,4)`. A **numerically calculable** value is not a **verified equivalent** to upstream encoded `SH0/MC0/ACV` HFI votes, even though upstream A730's fixed HFI BW table also happens to have 12 entries.

### Vote gap disposition, separated by owner

1. **GX frequency and corner: implemented, disabled**. Mainline Boot has 13 compiled Cape rates and proper `opp-level` values. GPU host constructs GX votes from GPU OPP and `gfx.lvl`; accept these as a candidate, not actual firmware behavior.
2. **Per-GPU CX floor: HOLD**. Six vendor CX floors exceed GX corner. The existing upstream HFI `cx_arc_votes` correspond to *GMU's own* 200/500 MHz OPPs at 64/128, not thirteen GPU perf states; GX secondary index uses `gmxc.lvl`/fallback `mx.lvl`, not the vendor per-frequency `cx-level`. New confirmed stock CX `qcom,init-voltage-level=384` is **not** sufficient to prove persistent floors, and the recovered **GMU blob** supplies no host-side power contract solely from its filename/version. First obtain actual CX/command-DB vote ownership (downstream KGSL/GMU HFI logic or hardware trace) before proposing a new `required-opps` mapping, RPMh voter, or altered HFI schema. No guessed patch.
3. **DDR/bandwidth index: HOLD**. Mainline [`a730_build_bw_table`](https://github.com/Drzet/linux/blob/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3/drivers/gpu/drm/msm/adreno/a6xx_hfi.c#L680-L755) transmits 12 fixed `SH0/MC0/ACV` command words but, with no `.bcms` mapping, [`a6xx_gmu_set_freq`](https://github.com/Drzet/linux/blob/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3/drivers/gpu/drm/msm/adreno/a6xx_gmu.c#L150-L246) selects default bandwidth index 0. The verified stock GPU ICC tuple establishes *provider path* (`gem_noc` to `mc_virt`) **not** numeric bandwidth/HFI index equivalence. Require per-BCM command-DB `SH0/MC0/ACV` encodings or a pinned downstream GMU driver mapping; do **not** transplant vendor `qcom,bus-freq` into the mainline HFI index.
4. **ACD, IFPC, thermal/DVFS: HOLD**. Exact source ACD words exist but weren't in export; current upstream A730 no oneli `qcom,opp-acd-level` props. Firmware semantics and safety are not proven.

## Firmware is located: exact source hashes and Linux request/load contract

Two physical **containers** are important: `radio.img / SINGLE_N_LONELY / NON-HLOS.bin / Android-sparse ext4 / image/`, plus `super:vendor_a / firmware/`. The sizes and hashes below are from VPU's controlled stock scan; none are SHA-verified against the actual phone.

| Image (purpose) | Public reference format/path, bytes, SHA256 | Expected upstream loader request | Verdict |
| --- | --- | --- | --- |
| SQE | `image/a730_sqe.fw`; **74,676 bytes**, `e67d1829f57fc8326d806234b932dc3b78e28a9940df34c70752f17d5f38b7aa` | A730 catalog name `a730_sqe.fw`, `adreno_request_fw` prefers `qcom/a730_sqe.fw` | **Install-name plan supported; binary interoperability not proven.** Upstream [linux-firmware tag `20260221`](https://kernel.googlesource.com/pub/scm/linux/kernel/git/firmware/linux-firmware/+/refs/tags/20260221/qcom/a730_sqe.fw) independently has **75,924 bytes** and Git blob SHA1 `30cca6af3baf9b162d8f75642a630ee37510f608`; the **different size proves public stock and that upstream reference are NOT byte-identical**. `WHENCE` calls upstream v1.81, not a verified Motorola stock version. |
| GMU | `super:vendor_a/firmware/gmu_gen70000.bin`; **57,272 bytes**, `b2d3f0e2a98fd6259ab9ffef16df63265542e6cc9a970d53d476e823d432042a` | Catalog `gmu_gen70000.bin`, `adreno_request_fw` prefers `qcom/gmu_gen70000.bin` | **Name/size are compatible, content equivalence UNPROVEN.** [Upstream linux-firmware tag `20260221`](https://kernel.googlesource.com/pub/scm/linux/kernel/git/firmware/linux-firmware/+/refs/tags/20260221/qcom/gmu_gen70000.bin) independently has **57,272 bytes**, Git blob SHA1 `0c04d164fd20e3fa426c317c21eebfc8addfd77b`, WHENCE v4.00.07. SHA256 must be computed on exact upstream bytes or matching stock git-blob SHA1 before calling equal. VPU's `vendor_a` format is still `unclassified from prefix`, not proven ELF/MBN. |
| oneli ZAP | `image/a730_zap.mdt`: **4,044 bytes**, `f5d8a41c1380ba2b42cd742538083306d245471ac5d51139e3bc8a6168ce84d2` plus `.b00`: 148 bytes, `9cd65a08fa2ce72c05a52aad95951f749f52fc310613a2857e270b463a641a7f`; `.b01`: 2,236 bytes, `1fc98f97cf354b9704b20d0848f7b2739638539a57d88ecf5cc71ca1c5c4e6b9`; `.b02`: 3,896 bytes, `14228d0a3787ba77fc1859121d097d46e677d9e8773c39eeba625524d59f6336` | Catalog fallback `a730_zap.mdt`; mainline `zap_shader_load_mdt` can accept explicit board `zap-shader/firmware-name`, and `qcom_mdt_load` fetches **separate indexed Bxx** files | **Correct split-MDT structure is source-backed; not equivalent to generic `qcom/sm8450/a730_zap.mbn`** (linux-firmware WHENCE v0.14). Proposed install `/lib/firmware/qcom/oneli/a730_zap.mdt` and three `.bXX` companions; future Boot-only explicit `firmware-name = "qcom/oneli/a730_zap.mdt"` when enablement justified. Loader header/segments and cryptographic PAS accept still unverified. |

Mainline [`adreno_gpu.c` lines 31–184](https://github.com/Drzet/linux/blob/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3/drivers/gpu/drm/msm/adreno/adreno_gpu.c#L31-L184) calls `qcom_mdt_get_size`, checks 8 KiB reserved-region fit, uses `qcom_mdt_load` and secure `qcom_pas_auth_and_reset`. The inherited Boot [SM8450 shared carveout](https://github.com/Drzet/linux/blob/525b504b82dbca593a9a697af9be63f53915e0a3/arch/arm64/boot/dts/qcom/sm8450.dtsi#L691-L694) matches stock at `0x8b91a000/0x2000` **exactly**; this closes **address and size transcription**, not actual ZAP segment span or signed acceptance. Installing **only** the MDT or renaming the three Bxx files is insufficient. New [SQE security-check helper](https://github.com/Drzet/linux/blob/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3/drivers/gpu/drm/msm/adreno/a6xx_gpu.c#L985-L1049) accepts A7xx family by model without imposing A630's v1.90 firmware threshold; this is a host-code check, not SQE execution.

### Acceptance and next evidence, ordered by cost

1. **Already accepted**: full ARM64 `Image modules` including GMU fix [run 38178986611](https://github.com/Drzet/razr2022_nuc/actions/runs/38178986611) **PASS**, no unchanged recompile. Boot's 13-rate compiled FDT [run 38174125440](https://github.com/Drzet/razr2022_nuc/actions/runs/38174125440) **PASS**.
2. **Cheap, targeted VPU exporter amendment**: include `qcom,chipid`, GPU-parent `qcom,bus-table-ddr`, `qcom,initial-pwrlevel`, `zap-shader/firmware-name` (if present) and each `qcom,gpu-pwrlevel@N` child's `qcom,gpu-freq`, `qcom,level`, `qcom,cx-level`, `qcom,bus-freq/min/max`, `qcom,acd-level`, with raw byte hex, sizes and per-property hashes for **both already identified base FDTs**. This extension does not require the full ROM; use existing member/CI source or a bounded single-member fetch under VPU ownership. Until then, the 13-row table above is *Motorola source candidate* rather than compiled stock equality.
3. **Cheap, targeted firmware metadata**: parse the **recovered** `a730_zap.mdt` ELF program headers (PT_LOAD memory span, `p_offset/p_filesz`, relocation/secure bits and exact phdr index -> `bXX` naming). Compare with **0x2000** stock carveout and validate safe loader input bounds; publish metadata only. Confirm generic GMU SHA256 (or compare SHA1 Git object for byte-identical content) from the **exact pinned upstream revision**. New proprietary download is not needed for currently reported filenames/hashes; request genuinely missing member bytes centrally if unavoidable.
4. **Host firmware-ownership analysis**: VPU's stock GMU hash + CPU source cannot prove how authenticated GMU HFI enforces CX floors or maps vendor 12 DDR indices to 12 hardcoded mainline commands. Obtain stock GMU/driver semantics from pinned downstream Gen7 host source and RPMh command DB before coding HFI votes. Mark this a **hard HOLD**, not a license to guess.
5. **Physical-only**: PAS/SCM ZAP authorization, real SQE/GMU HFI handshake, live `gfx.lvl/cx.lvl/mx.lvl/gmxc.lvl` tables, compressed-buffer interoperability, rendering and DVFS tracing. **Board GPU must remain disabled** until host/power/firmware contract is supportable.

**Review outcome:** No new source-backed GPU driver voltage/BW patch follows from these records; retaining the reviewed chip-ID plus GMU error fix is the correct bounded implementation. UBWC source review already completed and remains [INFERRED] until SMEM memory-profile observation; no repeat audit required.
