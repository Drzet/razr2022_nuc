# SM8475/oneli A730v3: actionable CX-floor and bandwidth contract

Date 2026-10-11. Inputs: Motorola `kernel-devicetree` `90fa7be1db5bd47202673d4431408659149a7359`, `qcom/cape-gpu.dtsi`; Drzet/linux pinned baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` plus disabled Boot OPP integration `9b37ea4953eada0837b18421ce6b74beebfe0a2b` and GPU chip-ID patch `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`. Source interpretation only; firmware RAM command DB, HFI handshake, runtime clocks and rail voltages are **not** measured.

## Exact field-by-field disposition

| Field from Motorola Cape DT | Evidence / numeric meaning | Existing upstream consumer | Change readiness / owner |
|---|---|---|---|
| `qcom,gpu-freq` | Thirteen observed vendor values, 220–900 MHz; source [pwrlevels](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-gpu.dtsi#L66-L247) | `gpu_opp_table/opp-hz`; `a6xx_gmu_build_freq_table`; HFI `gx_votes[].freq` | **DONE (disabled candidate)** in Boot `9b37ea49`; compiled DTB run 38174125440 passed |
| `qcom,level` | GX RPMh *corner enum*, not a voltage in microvolts. [RPMHPD header](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/include/dt-bindings/power/qcom,rpmhpd.h) | GPU `opp-level` -> `a6xx_gmu_get_arc_level(GPUdev, frequency)` -> `gfx.lvl` primary GX ARC | **DONE (source transcription)**, but live `gfx.lvl` buckets and firmware vote interpretation are unknown; GPU stays disabled |
| `qcom,cx-level` | Vendor **separate per-GPU-frequency** CX floor, six stages differ from GX and high-rate states reach corner 416 | Mainline `cx_arc_votes` derive from **GMU** OPP table, inherited 200/500 MHz levels 64/128 via `cx.lvl`; GX secondary votes come from `gmxc.lvl` or `mx.lvl` level mapping against **GPU `qcom,level`**, not `qcom,cx-level` | **HOLD.** No proved per-GPU CX-floor mapping. An isolated upstream HFI/DT design must state whether host owns each vote or the installed GMU firmware does. Do **not** copy CX floors into the GX `opp-level` values, since that would corrupt verified `gfx.lvl` votes. Owner GPU + Power + Boot |
| `qcom,bus-freq` | Index into vendor 0–11 `qcom,bus-table-ddr`, *not* raw kBps and *not* HFI index contract | Baseline A730 `a730_build_bw_table` sends a fixed twelve-entry `SH0/MC0/ACV` HFI table; `a6xx_gmu_set_freq` keeps `bw_index=0` because the catalog has no `.bcms` | **HOLD index translation.** Do not copy index `11` as a host BW level or silently bind vendor 12 entries to the hardcoded HFI 12 entries. Decode/compare actual SH0/MC0/ACV BCM vote encodings and firmware expectations first |
| `qcom,bus-min`, `qcom,bus-max` | Vendor governor bounds for the indexed DDR table; not simple per-state bandwidth requirements | No one-to-one upstream OPP properties implementing this clamp in A730 | **HOLD** until governor behavior and BCM path are established; do not discard evidence or assume these are compulsory minima for mainline |
| `qcom,bus-table-ddr` + `MHZ_TO_KBPS(mhz,w)` | Source literal `((mhz * 1000000 * w) / 1024)`, with `w=4`; units labelled *KB/s* (base 1024, integer truncation). This converts the **vendor requested aggregate DDR rate** to a numeric value for comparison | `opp-peak-kBps` + BCM path is a **potential** binding mechanism, but the current A730 profile has no `.bcms` and no OPP bandwidth values. HFI fallback table is a different representation | **SOURCE-DERIVABLE candidate numeric values only**. They are not approved `opp-peak-kBps` entries until the ICC width, bandwidth aggregation, SCM/GMU command DB mapping and bus-vote equivalence are verified |
| `qcom,acd-level` | Thirteen opaque vendor words, different across stages; firmware/GMU semantics not known | Existing upstream `a6xx_gmu_acd_probe` can read `qcom,opp-acd-level` and send HFI ACD table and AOSS QMP, but only when properties exist | **HOLD** OPP ACD translation until level encoding/HFI acceptance and power impact are source-verified; the current DT intentionally omits them |
| `qcom,initial-pwrlevel` = 11 | Vendor initial *indexed pwrlevel* (index 11 = 285 MHz) | Upstream GMU has its own performance-index initialization policy | **DO NOT copy** numeric 11 without checking downstream index reversal vs upstream sorted OPP table and firmware boot requirements |
| `qcom,ubwc-mode` = 4; `qcom,min-access-length` = 32 | Vendor GPU UBWC v4, 32-byte MAL | Shared `qcom_ubwc_config_get_data` from VPU SM8475 mapping gives UBWC 4.0 / 32-byte MAL; Adreno `a6xx_set_ubwc_config` consumes it | **Reviewed separately** in [UBWC consumer review](gpu_ubwc_cross_subsystem_review_2026-10-11.md); phone's SMEM HBB not measured |

## Concrete reference matrix (not a DTS patch)

Derived only from Motorola's `cape-gpu.dtsi`. The `nominal KB/s` column is evaluated from the **vendor table** formula and nominal bus-freq index, not from upstream HFI commands. CX/GX entries are numeric RPMh corner enums.

| GPU MHz | GX corner | vendor CX floor | vendor freq/min/max indices | indexed DDR MHz | nominal KB/s |
|---:|---:|---:|---|---:|---:|
| 900 | 416 | 416 | 11 / 11 / 11 | 3350 | 13085937 |
| 862 | 384 | 384 | 11 / 11 / 11 | 3350 | 13085937 |
| 815 | 320 | 320 | 11 / 10 / 11 | 3350 | 13085937 |
| 765 | 256 | 256 | 10 / 9 / 11 | 3196 | 12484375 |
| 710 | 224 | 256 | 10 / 6 / 11 | 3196 | 12484375 |
| 645 | 192 | 192 | 8 / 6 / 9 | 2092 | 8171875 |
| 580 | 144 | 192 | 8 / 6 / 9 | 2092 | 8171875 |
| 515 | 128 | 128 | 6 / 6 / 8 | 1555 | 6074218 |
| 439 | 96 | 128 | 6 / 3 / 8 | 1555 | 6074218 |
| 364 | 80 | 128 | 3 / 1 / 6 | 547 | 2136718 |
| 324 | 64 | 64 | 2 / 1 / 6 | 451 | 1761718 |
| 285 | 56 | 64 | 2 / 1 / 5 | 451 | 1761718 |
| 220 | 48 | 64 | 2 / 1 / 5 | 451 | 1761718 |

Original twelve vendor DDR index values (MHz) are `0, 200, 451, 547, 681, 768, 1555, 1708, 2092, 2736, 3196, 3350`. Their conversion is deterministic, but matching counts (**12 vendor indexes** and **12 upstream fixed HFI levels**) do not establish matching encoded commands or memory paths. The upstream hardcoded entries [`a730_build_bw_table`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/gpu/drm/msm/adreno/a6xx_hfi.c#L672-L739) are BCM vote words, not throughput units. Vendor nominal interconnect table numbers have not been observed on the actual phone.

## Proposed implementation stages and explicit holds

1. **Stage 0, already approved:** keep 13 committed frequencies and **GX** RPMh levels in Boot's disabled GPU node. Pin [compiled Boot DTB result](../tests/results/2026-10-11-gpu-boot-committed-opp.md).
2. **CX-floor design gate:** reconstruct GMU Gen7 HFI performance table layout, command-db `gfx.lvl`, `gmxc.lvl`/`mx.lvl`, `cx.lvl` and Motorola governor's per-frequency CX vote ownership from authoritative source or exact matching reference firmware. Current `gx_arc_votes` packs primary `gfx.lvl` and a secondary index chosen using the GPU corner; the separate `cx_arc_votes` has only GMU 0/200/500 MHz states. Choose **one supported** voltage-floor approach only after establishing whether the GMU firmware itself enforces the vendor `cx-level` table. No guessed direct RPMh vote, no inflated GX corner, no blind `required-opps` on GPU nodes.
3. **Bandwidth design gate:** for every Motorola DDR index, resolve source/stock command-db `SH0/MC0/ACV` parameters and compare encoded HFI `ddr_cmds_data` vote values, plus actual `MASTER_GFX3D -> SLAVE_EBI1` ICC route/bus width. If equivalent, introduce a **separately reviewed** A730-specific `.bcms` description and `opp-peak-kBps` values calculated from backed bandwidth requirements, with normal `a6xx_gmu_set_freq` index selection and build/schema tests. If not equivalent, document a separate A730 HFI index policy or hold dynamic bus switching until hardware; direct `qcom,bus-freq` index copying is explicitly disallowed.
4. **ACD/IFPC power feature gate:** preserve current conservative A730 quirks and no ACD OPP properties. Revise only with matched Motorola firmware metadata and packet ABI evidence; first rendering has priority over optional power features.
5. **Hardware acceptance gate:** after unlock and justified firmware, inspect real RPMh bucket levels, log GPU/GMU init and HFI acknowledgements, exercise 220/285/515/710/900 MHz transitions with independent CX/GX observations and DDR throughput/thermal tracing, then stress GPU↔display↔VPU compressed-buffer interoperability.

### Immediate consequence

**The board GPU stays disabled.** The source-backed OPP and chip-ID fixes are acceptable offline patches; the **CX floor** and **DDR-bandwidth index semantics** are not yet an enablement contract. Remaining missing evidence is precisely the per-state GMU HFI/firmware ownership of CX floor and an equivalence proof between vendor DDR values and upstream `SH0/MC0/ACV` table entries, not simply absent code.
