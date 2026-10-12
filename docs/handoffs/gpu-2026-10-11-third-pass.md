# Subsystem handoff: GPU third round (coordinator second review)

- Date and originating chat: 2026-10-11, GPU agent after reading `docs/NEXT_TASKS.md` main content SHA `96d377b19ed0528c8568d9b2d2f180b6dc7b7373`.
- GPU kernel: `Drzet/linux`, `razr/gpu`, exact driver patch `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`.
- Boot kernel: `Drzet/linux`, OPP-commit `9b37ea4953eada0837b18421ce6b74beebfe0a2b`, **tested** by compiled-DTB job. Boot may advance afterwards; integration must select exact commits.
- Documentation/test branch: `Drzet/razr2022_nuc` `razr/gpu`; see [draft PR #6](https://github.com/Drzet/razr2022_nuc/pull/6) for current head. Tested project SHA is recorded per run; do not substitute a moving branch or PR test merge SHA.
- Baseline kernel: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` (unchanged).
- Evidence stage: **researched** yes (source comparison); **implemented** A730v3 catalog chip ID; **build-tested** Boot's exact OPP DTB **yes**; GPU module complete-build run **not yet accepted pending completed conclusion** at initial drafting; **hardware-tested** no (stock ADB capture is not native Linux).

## Changes and provenance

1. Replaced the failed isolated MSM `M=` module CI with [strict complete in-tree Image/modules CI](../../.github/workflows/gpu-arm64.yml): normal modpost, retain resolved ARM64 `.config`, populated `Module.symvers`, resulting `msm.ko`, `modinfo`, ELF metadata, tool versions, commands, SHA256 artifacts or error logs. Kernel checkout stays pinned to GPU patch `4955f07...`. No `KBUILD_MODPOST_WARN=1` workaround.
2. Added [Boot committed OPP CI](../../.github/workflows/gpu-boot-opp.yml). It does not copy or append the temporary fixture. It compiles exact Boot commit `9b37ea49...` and runs the existing [fdtget frequency/corner checker](../../tests/scripts/gpu-opp-fixture.py), also asserting GPU `status = "disabled"`.
3. Closed the [source-level GMU/CX/RPMh/ACD/IFPC/DDR disposition](../gpu_cx_gmu_rpmh_disposition_2026-10-11.md). Concrete gaps: six independent vendor CX corner differences; GMU 200/500 MHz CX levels 64/128 vs vendor high-rate CX floor up to 416; fixed A730 HFI DDR table with no per-GPU bandwidth index selection; optional upstream ACD parser unused by DT; IFPC deliberately inactive; pinned vendor Gen7-4-0 CP I-cache-prefetch chicken-register writes absent from the conservative baseline A730 path. GMU MX dependency vote call-site frequency table mismatch and dropped return code are source-audit risks, not proven oneli runtime failures. [INFERRED] None of these justifies enabling GPU before firmware and power-rail validation.
4. Stock ADB observed XT2251-1 PVT, hwrev 0xC000, SKU dn, Android 14 build `U2SLS34.1-42-14-11`; stock `renderD128` is not proof of Mesa acceleration. VPU remains sole owner of public matching-version firmware archive and hash inventory; GPU awaits signed Motorola ZAP path.

## Shared files and integration

- **No shared SoC or oneli board DTS edited by GPU agent**. Boot owns `sm8475.dtsi`; it committed the reviewed disabled GPU OPP table in `9b37ea49...`.
- GPU kernel branch touches only `drivers/gpu/drm/msm/adreno/a6xx_catalog.c` (chip ID).
- Coordinator integration selects exact Boot and GPU patch commits; separate code/module build and DTB check precede integration. No auto-merge/branch rewrite.

## Validation

- [Past isolated MSM build run 38164004265](https://github.com/Drzet/razr2022_nuc/actions/runs/38164004265): **FAILED**, missing `Module.symvers` produced hundreds of unresolved kernel/DRM symbols under standalone `M=` modpost. Not a validated patch defect.
- [Complete in-tree MSM build run 38174090675](https://github.com/Drzet/razr2022_nuc/actions/runs/38174090675): launched against project `d0fc7d7bba683719e852311f5f2d0e3fd95a1fbe` and kernel `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`. **Status pending at handoff drafting**; it must be inspected after completion before acceptance. Do not equate workflow commit, config success or in-progress job with passed module test.
- [Boot committed OPP run 38174125440](https://github.com/Drzet/razr2022_nuc/actions/runs/38174125440): **COMPLETED SUCCESS** on project `4c59c36af62d1212be10bce9969b9d66354e275a`, Boot kernel `9b37ea4953eada0837b18421ce6b74beebfe0a2b`. [Detailed build record](../../tests/results/2026-10-11-gpu-boot-committed-opp.md), [artifact with DTB + configuration + hashes](https://github.com/Drzet/razr2022_nuc/actions/runs/38174125440/artifacts/11714519663). Verified exactly thirteen 220–900 MHz Cape frequencies, numeric corner values, no stale SM8450-only GPU OPPs, correct GPU/GPUCC compatible strings, GPU `status = "disabled"`.
- Physical GPU/GMU/ZAP and rendering tests: **not run**.

## Remaining bounded blockers, next consumer and test

1. **GPU agent:** inspect completed full in-tree module run, preserve/commit result and resolved config + Module.symvers artifact hashes; repair any real build failures. Do not use warning-tolerant modpost.
2. **Boot/coordinator:** consume committed OPP PASS record and the source-level CX/GMU vote audit. Keep GPU disabled pending supported CX floor, firmware and regulator semantics. Actual all-applicable board DT schema coverage belongs to Boot.
3. **VPU → GPU/Boot:** one matching Android14 `U2SLS34.1-42-14-11` public archive inventory with exact SQE/GMU/signed ZAP filenames and SHA256. GPU does not download duplicate multi-GB archive.
4. **Eventually hardware:** native kernel power-up, firmware request/SCM, render node identification and readback rendering, DVFS transitions, power and thermals after bootloader prerequisite is satisfied.
