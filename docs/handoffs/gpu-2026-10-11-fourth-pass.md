> **2026-10-12 supplement:** the strict full ARM64 `Image modules` job [38178986611](https://github.com/Drzet/razr2022_nuc/actions/runs/38178986611) is now **completed SUCCESS** for GPU kernel `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`, tested project `649aafdf4b00766c2c22cae34f2212b7c71c94d5`, artifact [11717571590](https://github.com/Drzet/razr2022_nuc/actions/runs/38178986611/artifacts/11717571590). Also, VPU has since **located SQE, GMU and ZAP**. See [the fifth-round current evidence report](../gpu_stock_fdt_firmware_vote_review_2026-10-12.md); this handoff's pending/unlocated wording is retained only as historical test status.

# Subsystem handoff: GPU fourth round, GMU probe error handling and shared UBWC

- Date / originating chat: 2026-10-11, GPU owner responding to coordinator third-review `docs/NEXT_TASKS.md` (on main).
- Kernel repository / branch / **exact head**: `Drzet/linux` / `razr/gpu` / **`3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`**.
- Kernel commit series (separate, attributable changes):
  1. `4955f07a94ea3c51e423e34d819ac3f76f1c9d37` [Adreno A730v3 `0x07030002` chip-ID match](https://github.com/Drzet/linux/commit/4955f07a94ea3c51e423e34d819ac3f76f1c9d37).
  2. `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3` [GMU power-level error propagation and runtime-PM unwind](https://github.com/Drzet/linux/commit/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3).
- Upstream baseline: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` (unchanged).
- Boot dependency: source-backed disabled 13-rate OPP integration `9b37ea4953eada0837b18421ce6b74beebfe0a2b`; later Boot builds may advance. [Committed-DTB check 38174125440](https://github.com/Drzet/razr2022_nuc/actions/runs/38174125440) **PASS**. Coordinator selects exact merged/cherry-picked revisions.
- VPU dependency: independently reviewed shared SoC UBWC commit `7f1d729b6f458f1e76efe2894eb3c544bc9db856` (`drivers/soc/qcom/ubwc_config.c` only), provisional `qcom,sm8475` machine match. This is **not** an endorsement of the earlier unready Iris RFC.
- Coordinator project / branch: `Drzet/razr2022_nuc` / `razr/gpu` ([draft PR #6](https://github.com/Drzet/razr2022_nuc/pull/6)); exact SHA for each test below and the PR head determine which content was tested.
- Evidence stages: **researched** yes; **implemented** two isolated kernel commits and project tests; **build-tested** baseline chip ID full module **PASS**, modified GMU source ARM64 object **PASS**, modified GMU return-path static guard **PASS**, new full kernel/modpost job initially pending; **hardware-tested** no.

## Changes and provenance

The previous `a6xx_gmu_init()` discarded `a6xx_gmu_pwrlevels_probe(gmu)` errors; the next stage might consume unpopulated HFI/RPMh frequency and corner tables. The new kernel commit checks `ret`, returns it through the already established `detach_gxpd` chain, and adds `pm_runtime_disable(gmu->dev)` in the common error label to balance earlier `pm_runtime_enable`. A6xx caller already propagates initialization errors; no power votes/clock rates/HFI structures were changed. [Validation record](../../tests/results/2026-10-11-gpu-gmu-error-path.md) includes exact source paths, cleanup-order inspection and compile outputs.

**CX-floor / DDR contract:** [actionable per-field mapping](../gpu_cx_bandwidth_mapping_contract_2026-10-11.md) distinguishes Motorola `qcom,level` (GX RPMh corner, represented by current GPU OPPs), independent `qcom,cx-level` (unrepresented per-GPU CX floor), and downstream DDR index-based `qcom,bus-table-ddr` values (source-defined numeric bandwidth, **not** direct HFI indexes). Six rates have CX floor different from GX; 900 MHz vendor CX floor reaches TURBO_L1/416, whereas mainline inherited 200/500 MHz GMU CX OPP levels are only 64/128. Gen7 HFI `cx_votes` are derived from GMU states, not thirteen per-GPU states. The A730 hardcoded `SH0/MC0/ACV` HFI bandwidth table has twelve entries but default `bw_index=0` for current no-`.bcms` profile. **Explicit HOLD** on changing CX floor, ACD and bus indexes until HFI/command-DB/ICC mapping can be justified; no guessed numeric votes added. `MHZ_TO_KBPS(mhz,4)` produces reference-only bandwidth values in the contract, not an approved DTS patch.

**Shared UBWC:** [cross-subsystem review](../gpu_ubwc_cross_subsystem_review_2026-10-11.md) independently checked VPU's `qcom,sm8475` -> `ubwc_4_0_hbb16` against `a6xx_set_ubwc_config` (Adreno), `msm_mdss_6x_setup_ubwc` / DPU (display) and Iris `iris_hfi_gen2_packet_sys_init`. All use shared `qcom_ubwc_config_get_data`. Default HFI values correspond to independent Waipio `UBWC_CONFIG(8,32,16,0,1,1,1)` and Motorola's mode 4/MAL32. **[INFERRED]** actual oneli SMEM HBB, DRAM configuration and compressed buffer interoperability are untested. Recommend only isolated UBWC commit for the integration prerequisite, not enabling VPU/GPU.

**Firmware:** [consumed shared VPU public-stock manifest](../gpu_shared_firmware_consumer_2026-10-11.md), not a GPU-managed download. ZIP `U2SLS34.1-42-14-11`, 4,353,164,507 bytes, SHA256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`, matches observed handset build label but not verified installed image identity. Generic linux-firmware SQE v1.81, GMU v4.00.07 are not verified as stock. Actual board-signed ZAP member/path/segments and all stock GPU firmware hashes remain **unresolved**; VPU owns the single extraction job. GPU review posted to [VPU kernel PR #2](https://github.com/Drzet/linux/pull/2), firmware request to shared [issue #10](https://github.com/Drzet/razr2022_nuc/issues/10).

## Shared files and integration

- GPU changed **no** shared SoC/board DTS or common UBWC driver. Boot alone owns `arch/arm64/boot/dts/qcom/sm8475.dtsi`.
- GPU kernel touched `drivers/gpu/drm/msm/adreno/a6xx_catalog.c` in the older ID commit and `drivers/gpu/drm/msm/adreno/a6xx_gmu.c` in the new independent error-handling commit.
- VPU's UBWC commit is a single shared SoC provider match that affects GPU, display/MDSS and Iris. If selected, cherry-pick/rebase it explicitly with the original commit hash and record the resulting integration SHA, without importing the full experimental VPU driver series.
- **Do not enable** oneli GPU on the Boot branch until CX floor and firmware/power requirements are supported; the current offline OPP-compatible transcription pass is not an enablement decision.

## Validation and exact input SHAs

| Run / exact source | Completed conclusion | What was actually tested |
|---|---|---|
| [38174090675](https://github.com/Drzet/razr2022_nuc/actions/runs/38174090675), project `d0fc7d7bba683719e852311f5f2d0e3fd95a1fbe`, kernel `4955f07...` | **PASS** | Full ARM64 `Image modules` with normal modpost, complete `Module.symvers`, `msm.ko`, config, logs and hashes in [artifact 11716182125](https://github.com/Drzet/razr2022_nuc/actions/runs/38174090675/artifacts/11716182125); this predates the new GMU fix |
| [38179317499](https://github.com/Drzet/razr2022_nuc/actions/runs/38179317499), project `68f17e289b8f3d4e21d8700a8662ec1e51d31e64`, kernel `3baaec...` | **PASS** | Static GMU resource-unwind and runtime-PM balance check, plus **four negative mutations** rejected; [artifact 11716729054](https://github.com/Drzet/razr2022_nuc/actions/runs/38179317499/artifacts/11716729054) |
| [38179435399](https://github.com/Drzet/razr2022_nuc/actions/runs/38179435399), project `aea7f092d7f6e3eb01401062fbca86b622497da4`, kernel `3baaec...` | **PASS** | ARM64 Kbuild compiles changed `a6xx_gmu.o` (`CC [M]`), verifies AArch64 ELF, retains config/toolchain/compile log and hashes in [artifact 11717267945](https://github.com/Drzet/razr2022_nuc/actions/runs/38179435399/artifacts/11717267945). Object compile alone is **not** strict module modpost |
| [38178986611](https://github.com/Drzet/razr2022_nuc/actions/runs/38178986611), project `649aafdf4b00766c2c22cae34f2212b7c71c94d5`, kernel `3baaec...` | **In progress at first handoff publication** | Complete ARM64 Image/modules and strict modpost of new code; **do not mark PASS** until final conclusion and artifact are inspected |
| [38174125440](https://github.com/Drzet/razr2022_nuc/actions/runs/38174125440), Boot `9b37ea...` | **PASS** | Compiled actual disabled oneli DTB with 13 SM8475 GPU OPP frequencies and RPMh corner values, not a temporary fixture |

A failed first static-guard run [38179175912](https://github.com/Drzet/razr2022_nuc/actions/runs/38179175912) was the test's mutation-scoping bug, fixed before the successful run; it did not establish a kernel error. No phone boot, GPU/GMU firmware load, UBWC interop or rendering test occurred.

## Blockers, next consumer and acceptance

1. **GPU/coordinator:** inspect full changed-code strict module CI run's final conclusion; if successful, record tested kernel SHA, `Module.symvers`, config, `msm.ko` and artifact/hash. If unsuccessful, repair actual failure and re-test. Object compile already passed.
2. **Boot/Power:** review the source-backed CX-floor contract and current GMU 200/500 MHz OPP mismatch, *not* a guessed voltage patch. Keep device node disabled and consider explicit required provider vote ownership before enabling.
3. **VPU:** publish actual SQE/GMU/ZAP binary manifest (or bounded negative filesystem inventory) via one controlled archive job; GPU compares expected vs observed firmware and ZAP path without acquiring another 4.35-GB source.
4. **Coordinator:** select the exact independent GPU chip-ID, GMU cleanup and VPU UBWC provider commits for a combined build; ensure firmware/resource assumptions remain labelled. No integrated or hardware-tested kernel is claimed.

## Fifth-round update, 2026-10-12 (coordinator latest fourth-review amendment)

Coordinator [fourth review](https://github.com/Drzet/razr2022_nuc/blob/main/docs/FOURTH_REVIEW.md) confirmed **full ARM64 Image/modules run 38178986611 PASSED** at kernel `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3` with normal modpost; the above first-publication pending status is superseded. No unchanged rebuild or kernel change followed.

[GPU firmware/FDT/CX/DDR fifth-pass audit](../gpu_firmware_fdt_vote_audit_2026-10-12.md) independently downloaded and SHA256-checked VPU's accepted **six-FDT metadata-only artifact**, verified the extracted raw-property JSON digest, consumed actual radio SQE / vendor GMU / split signed ZAP hashes, and reviewed their exact mainline request and ZAP split-loader call paths. The **published filtered FDT JSON does not contain the per-pwrlevel `qcom,gpu-freq`, `qcom,level`, `qcom,cx-level`, `qcom,bus-freq/min/max`, `qcom,acd-level` or parent `qcom,bus-table-ddr` values**, even though it proves all 13 source-tree child paths and exact GPU/GMU/ZAP/ICC topology. The existing Motorola pinned source supplies those numeric candidates, not an observed stock binary field. The source-vs-binary numeric reconciliation is a **bounded metadata property-filter gap**, not a full-ROM download gate. GPU CX-floor and HFI bandwidth-index patch **remain held** pending non-guessed vote/firmware semantics; stock ZAP signature acceptance still hardware-only. Board GPU disabled.
