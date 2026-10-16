# Build record: VPU framework cleanup correction

- Date: 2026-10-16. Coordinator `432f2f84f6350f0c1b7670b751bf41fd349048ce` requested two cleanup corrections to project `be103e0fc0dbedefbf647dfea46c51ad5301e501` / kernel `3086118adc521943bd533f98d53b136cf4694bc2`.
- Corrected kernel: `Drzet/linux:razr/vpu-provenance-v5@905d2403c451838a408f6bb44e80a7cf9aa6ed10`, direct child of 3086118; no history rewrite. Project parent remains be103e0; its delivery commit contains this record and the updated canonical handoff.
- Baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` and accepted integration `2b5acf108ae37040ac1e652e029bb37f5609e886` unchanged. No firmware or shared DTS input changed.
- Changes: only `iris_power.c`, `iris_vb2.c/.h`, `iris_vidc.c`. Reuse existing VB2/M2M, Iris STOP/CLOSE/completion and resource interfaces. No arithmetic/ICC/OPP/binding expansion.
- Environment: isolated `/tmp/razr-vpu-checked`, existing output `/tmp/vpu-checked-build` and `/tmp/vpu-consumer-link`, AArch64 GCC 15.2.0, W=1. Shared `/workspace/linux` unchanged.
- Configurations are byte-identical to the previous [object/link record](2026-10-16-vpu-consumer-build.md). Existing saved config gzip files are reused. Decompressed SHA256: object `8ed994a9873de36b7cf2d40e33740d18c35e3961bf580b5d18bb5a8197fac0f7`; link `d3b9555dd16a17d6f06d9caf7cea941745052ec923df16e15f18ac3d6727bffa`. Real OPP/genpd/ICC/UBWC/reset dependencies remain enabled in the link config.

## Commands and results

From the kernel checkout:

```sh
make -j4 O=/tmp/vpu-checked-build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- W=1 drivers/media/platform/qcom/iris/
make -j4 O=/tmp/vpu-consumer-link ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- W=1 vmlinux modules
scripts/checkpatch.pl --no-tree --strict -q - < <(git show --format= HEAD)
```

**PASS** focused ARM64 changed-object compilation and combined driver object; **PASS** incremental module build, `MODPOST Module.symvers` and `LD [M] qcom-iris.ko`; **PASS** strict checkpatch with quiet empty output. [Object log](2026-10-16-vpu-cleanup/object-build.log), [module log](2026-10-16-vpu-cleanup/module-build.log), [checkpatch](2026-10-16-vpu-cleanup/checkpatch.log), [ELF header](2026-10-16-vpu-cleanup/module-elf.txt), [hash/config manifest](2026-10-16-vpu-cleanup/build-manifest.json). Final committed-source check reuses objects compiled from the same bytes earlier in this correction; it is not a clean whole-kernel rebuild.

Actual linked qcom-iris.ko SHA256: `ac44718e031ca3d585cca9795113edf5f1d19bb440f39cf3d4a65a9f190d3b04`. Module.symvers SHA256: `9f4914a135355be3e776b6d917a615f62e3ac5b0191ce4501b054b486c8aa64e`. Module remains outside this repository. No compiler/modpost warning or error in the focused logs. No Image build, combined artifact, packaging or native test was performed. Push CI is skipped to avoid its duplicate Image job.

From the project root:

```sh
python3 tests/vpu/consumer-policy.py --framework --kernel-dir /tmp/razr-vpu-checked --json-out tests/results/2026-10-16-vpu-cleanup/framework-after.json
python3 tests/vpu/consumer-policy.py --kernel-dir /tmp/razr-vpu-checked --json-out tests/results/2026-10-16-vpu-cleanup/consumer-after.json
```

**PASS** six targeted framework cases / 645 assertions; **PASS** existing 52 consumer cases / 2325 assertions. Same updated runner at pinned rejected 3086118 reproduces the specific expected assertion failure for each of `failed-start`, `nonstreaming-cancel`, `successful-close`: [before files](2026-10-16-vpu-cleanup/). See [harness scope and reproduction](../vpu/cleanup-framework.md). Source/test/function hashes and compiler flags are recorded per run. Compiler/UBSan output is clean. Mock lock/reference checks contribute to counts; these are sequential host executions of actual control flow.

## Reused evidence and device boundary

Calculator C/header/math, resource arithmetic and binding bytes remain unchanged. Prior reference/differential vectors and schema results are reused; no firmware/source extraction or schema replay. Baseline/configuration selections and acceptance were not changed.

Hardware not tested. No full Linux VB2/IRQ concurrency, real DMA, firmware/PAS/HFI or provider recovery result is claimed. SM8475 remains gated and unintegrated. Failed OPP recovery, full quarantine reclamation, inherited IOVA reservation failure and general-purpose startup remain separate decisions. /3 remains [INFERRED, USER-ACCEPTED FOR DEVELOPMENT]; retained startup still rejects 1080p/4K under the reviewed policy.
