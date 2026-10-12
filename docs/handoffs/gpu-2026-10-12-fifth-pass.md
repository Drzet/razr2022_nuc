# Subsystem handoff: GPU fifth pass, recovered stock GPU/CX/firmware evidence

- **Date / chat:** 2026-10-12; GPU owner, coordinator fourth-review queue `docs/NEXT_TASKS.md` (main blob `9a9b9b1f9a06c4f1998677871b9d25bee496d5e5`), amendment `docs/FOURTH_REVIEW_VPU_UPDATE.md`.
- **Kernel repository / branch / exact commit:** `Drzet/linux` `razr/gpu` `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3` (unchanged this round). Commit 1: `4955f07a94ea3c51e423e34d819ac3f76f1c9d37` A730v3 catalog ID. Commit 2: `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3` GMU pwrlevel return-code + runtime-PM unwind. No undocumented further kernel patch.
- **Baseline:** `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` (unchanged).
- **Boot dependency:** `525b504b82dbca593a9a697af9be63f53915e0a3` (disabled GPU, 13 rate/corner table; mainline `gpu_micro_code_mem` same 0x8b91a000 / 8KiB stock reference).
- **VPU independent shared SoC UBWC candidate:** `7f1d729b6f458f1e76efe2894eb3c544bc9db856`, reviewed separately; *do not* merge Iris RFC ancestors on account of UBWC. VPU public stock metadata [run 38220276125](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125), project `1a59d79fda42a977956de8e06c3a60d44b2971f4`; original metadata SHA256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`.
- **Evidence class:** source research **yes**; six-FDT exported raw-property inspection **yes**; recovered proprietary firmware **metadata/hash inspection only**; new code implemented **none** this round; inherited kernel ARM64 Image/modules build **PASS**; physical firmware/GMU/GPU operation **not tested**. All unmeasured hardware/firmware claims marked [INFERRED].

## Changes and provenance

The [complete source/stock/driver comparison](../gpu_stock_fdt_firmware_vote_review_2026-10-12.md) is the authoritative fifth-round GPU report. Independently retrieved VPU's entire six-FDT metadata artifact, verified ZIP and JSON SHA256. Found both vendor_boot base FDTs contain the same exported GPU/GMU nodes and **thirteen** `reg=0..12` GPU powerlevel child nodes. The published **filtered** property export *does not contain* each child's `qcom,gpu-freq`, `qcom,cx-level`, `qcom,bus-freq` etc.; the prior 13-rate/GX/CX/DDR mapping is sourced from Motorola's pinned `cape-gpu.dtsi`, **not** verified bytewise against the compiled stock base. It is an exact, focused missing-data request, not evidence the properties are missing from stock. Stock PVT `0x45/c000` overlay index 3 is only a selection candidate.

Actual stock GX/CX provider facts improve previous generic audit:

- `vddcx-supply` 545 -> GDSC 0x3d99108 -> parent 30, `cx.lvl` S6; `qcom,init-voltage-level=384`, `qcom,proxy-consumer-voltage=<384 65535>`.
- `vdd-supply` 556 -> GDSC 0x3d9905c -> parent 53, `mxc.lvl` graphics voter (init 48); its parent phandle 69 is the `gfx.lvl` RPMh regulator (init 16).
- GPU ICC `<75 21 72 512>` identifies `gem_noc` and `mc_virt` providers and GPU3D/EBI1 endpoint specifiers. They are not an encoded HFI 0–11 bandwidth-index equivalence.
- Stock `zap-shader` phandle 555 resolves to memory reserved at `0x8b91a000/0x2000`, **identical** to inherited upstream `gpu_micro_code_mem`. Actual PT_LOAD bounds and secure PAS are not yet established.

Source-defined six GPU rates have per-frequency CX floor higher than GX; GMU CX proxy init 384 does not prove sustained dynamic floors. Upstream constructs GX votes against GPU OPPs/`gfx.lvl`, but CX votes against only GMU's own two OPPs/`cx.lvl`; its 12-level hardcoded A730 `SH0/MC0/ACV` HFI table has no per-frequency index mapping in the profile. **No CX/DDR/ACD code changes justified by this evidence.** All remain explicit HOLD; the oneli GPU node stays disabled.

Firmware is no longer unlocated: radio NON-HLOS ext4 `a730_sqe.fw` (74676, SHA256 `e67d1829f57fc8326d806234b932dc3b78e28a9940df34c70752f17d5f38b7aa`), `a730_zap.mdt` (4044, SHA256 `f5d8a41c1380ba2b42cd742538083306d245471ac5d51139e3bc8a6168ce84d2`) + b00/b01/b02 companions, vendor_a `gmu_gen70000.bin` (57272, SHA256 `b2d3f0e2a98fd6259ab9ffef16df63265542e6cc9a970d53d476e823d432042a`). Generic linux-firmware 20260221 SQE is **75924 bytes** (therefore definitely not same bytes as stock), GMU **57272 bytes** (same length but equality not proven), generic signed ZAP is a different SM8450 `.mbn` package. Proposed native layout `/lib/firmware/qcom/{a730_sqe.fw,gmu_gen70000.bin}` and board-specific `qcom/oneli/a730_zap.mdt` with three split companions; final `firmware-name` belongs to Boot/Userspace and is **not** an enablement or PAS acceptance result.

## Shared files and integration

- **No kernel source or shared DTS touched** in fifth pass. Existing GPU chip ID and GMU cleanup are candidates for coordinator integration. Boot owns shared DTS and active-node decisions.
- Shared VPU UBWC profile source review is already accepted as **provisional**; physical DRAM/SMEM HBB remains [INFERRED]. No new VPU duplicate download, GPU object rebuild, or ROM scan was performed.
- Historical [fourth-round GPU handoff](gpu-2026-10-11-fourth-pass.md) and [stale firmware-only note](../gpu_shared_firmware_consumer_2026-10-11.md) were marked superseded on this branch; earlier CI inputs/results remain immutable.

## Validation

1. [Full ARM64 Image/modules including GMU fix 38178986611](https://github.com/Drzet/razr2022_nuc/actions/runs/38178986611): **SUCCESS**, source input project `649aafdf4b00766c2c22cae34f2212b7c71c94d5`, kernel `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`, all steps passed, normal modpost; [artifact 11717571590](https://github.com/Drzet/razr2022_nuc/actions/runs/38178986611/artifacts/11717571590). No re-run needed.
2. [Boot compiled oneli OPP 38174125440](https://github.com/Drzet/razr2022_nuc/actions/runs/38174125440): **PASS** for source 13 GX frequency/corners with disabled board GPU. This does not validate vendor CX floors.
3. [VPU completed six-FDT export 38220276125](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125): **PASS**, independent GPU-local download and recomputation confirmed artifact ZIP SHA256 `485ff37b87cff2e6432928cfd4c0d4168bb3c10af163f6e68b6adfba35a528ae` and 15,862,099-byte `stock-per-fdt-property-export.json` SHA256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`.
4. **Physical/oneli tests:** none. Downloaded public reference container not a byte-verified device flash dump. No signed ZAP SCM acceptance, GPU HFI or display interop was tested.

## Blockers and next tests

- **VPU bounded metadata extension:** add the exact missed raw GPU-parent and 13 child OPP/bus/CX/ACD properties for *both existing base FDTs*; report each file/path, raw bytes and hashes, absent versus unselected. Do not download full ROM. Separately parse recovered ZAP MDT PT_LOAD phdr/segment-index bounds for the **0x2000** reserved region.
- **GPU firmware consistency:** generic linux-firmware SQE size differs from stock; GMU same size needs byte hash comparison using exact pinned upstream binary; do not infer stock GMU version from WHENCE. Interpret GX/CX firmware ownership only with HFI/command DB source, not blob basename.
- **Coordinator/Boot/Userspace:** compose enabled *only when* GPU CX/bandwidth, secure firmware and power contracts are demonstrated; until then preserve the disabled node and use these hash-backed metadata as integration documentation. No driver vote patch from current data.
