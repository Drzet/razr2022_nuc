# Subsystem handoff: GPU second pass after coordinator review

- Date and originating chat: 2026-10-11, GPU chat, in response to [coordinator NEXT_TASKS](../NEXT_TASKS.md).
- Kernel repository / branch / exact commit: `Drzet/linux` / `razr/gpu` / `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`.
- Coordination repository / branch: `Drzet/razr2022_nuc` / `razr/gpu`; deliverables in [draft PR #6](https://github.com/Drzet/razr2022_nuc/pull/6). Branch's exact head should be read from the PR before any cherry-pick/merge.
- Upstream baseline SHA: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- Required board-support and other subsystem SHAs: Boot `cbde49d927478decd6d608a309a7d7482992f776` **only as an exact test-fixture input**, not an integrated dependency. The eventual integration must select a Boot commit that **actually** adopts the GPU OPP and compatible proposal. GPU kernel patch still has the upstream baseline as its parent.
- Evidence stage: researched **yes**; implemented **yes (ID match only)**; build-tested **yes for ephemeral OPP DTB fixture only**, full MSM module **pending CI conclusion**; hardware-tested **no, physical phone unavailable**.

## Changes and provenance

1. No new kernel source changes in this followup. The existing [A730v3 chip-ID patch](https://github.com/Drzet/linux/commit/4955f07a94ea3c51e423e34d819ac3f76f1c9d37) adds `0x07030002` to upstream A730's catalog; no new GMU profile has been fabricated.
2. [Pinned downstream profile audit](../gpu_a730v3_second_pass_2026-10-11.md): Motorola KGSL `adreno-gpulist.h` at `9511d6b2dc469e5bd836992e3bdd6d19ace112e0` uses matching firmware filenames, HWCG, GBIF and protected register table references for Gen7-0-1 and Gen7-4-0. Vendor flags include IFPC/ACD/L3/BCL which are not all implemented/enabled by the upstream A730 profile. [INFERRED] The reuse candidate is reasonable for initial bring-up but no claims about firmware protocol, power efficiency or stability follow.
3. [Boot-facing OPP proposal, issue #4](https://github.com/Drzet/razr2022_nuc/issues/4) prevents 23 accidentally merged OPP nodes. Thirteen Cape rates/levels are transcribed directly from pinned Motorola `cape-gpu.dtsi` at `90fa7be1db5bd47202673d4431408659149a7359`. The vendor's CX corners differ from GPU corners for six steps; mainline's GMU/RPMh vote translation and optional ACD/DDR knobs are not established as identical.
4. [Shared public-stock firmware inventory request, issue #5](https://github.com/Drzet/razr2022_nuc/issues/5): SQE, GMU and signed Motorola ZAP requirements supplied to VPU/Boot. Public oneli RETEU package listing identified but archive/member checksums and installed phone build remain unknown. No blobs committed.

## Shared files and integration

- Kernel GPU branch touched only `drivers/gpu/drm/msm/adreno/a6xx_catalog.c`; no shared board/SoC files were touched.
- **Proposed, not committed:** GPU `compatible` and thirteen-corner table update in `arch/arm64/boot/dts/qcom/sm8475.dtsi`. Boot must apply on a reviewable Boot commit and check new resolved DT. The oneli board's GPU remains disabled until its power, memory and signed firmware conditions are established.
- The compiled check used a **disposable checkout**, not a tracked edit of Boot. Any subsequent integration must reference exact GPU and Boot SHAs and rerun DTB/schema checks.

## Validation

- [GPU OPP DTB fixture run 38164310160](https://github.com/Drzet/razr2022_nuc/actions/runs/38164310160): **PASSED** against exact Boot `cbde49d927478decd6d608a309a7d7482992f776`, docs project commit `7e606e2f6c8e2fa54ba94386fd2776c6208c2f97`; verified `sm8475-motorola-oneli.dtb` has exactly thirteen frequencies/levels, with no SM8450-only nodes, expected GPU and GPUCC compatibles. See [full record](../../tests/results/2026-10-11-gpu-opp-fixture.md) and retained run artifact.
- [MSM ARM64 module CI run 38164004265](https://github.com/Drzet/razr2022_nuc/actions/runs/38164004265): launched against kernel `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`; **in progress at initial publication**. The run compiles ARM64 Image plus out-of-tree Kbuild `M=drivers/gpu/drm/msm modules`, preserving config, logs and `msm.ko` if successful. Until a completed successful run is inspected, no module build success is claimed.
- No oneli hardware, firmware, GPU submission, rendering, thermal or runtime performance tests have occurred.

## Blockers and next test

1. Complete/inspect GPU module CI, record exact output, resolved `.config`, toolchain and logs. If modpost reports missing module dependencies, treat this as a build setup issue and rerun a proper in-tree module build before claiming a compiled module.
2. Boot adopts the correct GPU OPP replacement and compatible, then builds/checks its actual committed DTB (not the fixture). Shared regulator/CX/ACD and GPU reserved-memory obligations still need audit.
3. VPU/Boot/GPU jointly hash exact public reference firmware members; secure ZAP acceptance and full GPU acceleration remain hardware-deferred.
