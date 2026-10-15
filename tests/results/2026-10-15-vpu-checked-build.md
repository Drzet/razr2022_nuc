# Build record: VPU checked helper ARM64 object

- Date: 2026-10-15.
- Project source parent: `3a6729caf68aea40cfb80a4f449f067b6208b682`; this evidence commit adds tests and the canonical handoff, without changing accepted reference inputs.
- Kernel repository / branch / exact source commit: `Drzet/linux:razr/vpu-provenance-v5@7ac8d3afedfde74286b52e11aaa1eca42a1329a5`, parent `a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac`.
- Upstream baseline: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- Board support / accepted integration: `2b5acf108ae37040ac1e652e029bb37f5609e886`, unchanged and not used as a new integration candidate.
- External patches: the local attributable checked-model adaptation in 7ac8d3af; origin is Qualcomm GPL-2.0-only decoder at comparator `39382bf760ccf05a8fb4dddee7138ecac02d4a59` as pinned in the canonical handoff/reference. No additional upstream patch or firmware imported.
- Environment: isolated `/tmp/razr-vpu-checked` checkout using existing local objects; the shared `/workspace/linux` checkout is read-only and was not modified. Build output `/tmp/vpu-checked-build`. This is a modified-helper object build, not a clean/full baseline build.
- Toolchain: `/usr/bin/aarch64-linux-gnu-gcc`, `gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0`, host-provided Ubuntu cross-compiler; `W=1`.
- Architecture / configuration base: ARM64, `arch/arm64/configs/defconfig` at the exact source above.
- Ordered config changes: `scripts/config --file /tmp/vpu-checked-build/.config -m VIDEO_QCOM_IRIS`, then `olddefconfig`; no external fragment. This follows the existing Iris workflow's configuration inputs without running its full-build target.
- Generated config: [kernel.config.gz](2026-10-15-vpu-checked-build/kernel.config.gz), compressed SHA256 `998d66bfe4dba7eaae2d2d03a8c83c846418ea9b6c7f7d381940074f46ae4d42`; decompressed `.config` SHA256 `8ed994a9873de36b7cf2d40e33740d18c35e3961bf580b5d18bb5a8197fac0f7`.
- Firmware: not included or used for this pure object build.

## Commands and results

From the isolated kernel checkout:

```sh
make O=/tmp/vpu-checked-build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
scripts/config --file /tmp/vpu-checked-build/.config -m VIDEO_QCOM_IRIS
make O=/tmp/vpu-checked-build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- olddefconfig
make -j4 O=/tmp/vpu-checked-build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- prepare
make -j4 O=/tmp/vpu-checked-build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- W=1 drivers/media/platform/qcom/iris/iris_vpu2_bw.o
scripts/checkpatch.pl --no-tree --strict --file drivers/media/platform/qcom/iris/iris_vpu2_bw.c drivers/media/platform/qcom/iris/iris_vpu2_bw.h drivers/media/platform/qcom/iris/iris_vpu2_bw_math.h
aarch64-linux-gnu-readelf -h /tmp/vpu-checked-build/drivers/media/platform/qcom/iris/iris_vpu2_bw.o
```

Final configuration/prepare/object commands exited 0. [Object build log](2026-10-15-vpu-checked-build/helper-build.log) records `CC [M] .../iris_vpu2_bw.o` with no warnings. [ELF header](2026-10-15-vpu-checked-build/object-elf.txt) identifies a relocatable ELF64 AArch64 object. [Strict checkpatch](2026-10-15-vpu-checked-build/checkpatch.log) reports zero errors/warnings/checks for all three new code/header files. Config and prepare logs are preserved in the same directory; text artifacts normalize trailing whitespace only. Initial style findings were corrected before these final results; an unavailable `file` executable was replaced by readelf for object identity.

The object's source bytes match 7ac8d3af and the kernel source hashes in [host differential evidence](2026-10-15-vpu-checked.json). Source was compiled before committing the same bytes; host tests then ran against the clean committed checkout. Object SHA256: `b5582d79e29ae42f99a2ed97d7d1b95bf56cc208aacc432b5c1dc55df70fd969`. The generated object stays outside this repository.

## Image preparation

Not applicable. No Image, modules link/modpost, boot image, DT, ramdisk, firmware, boot parameters or packaging operation. Object compilation does not establish module linkage or a bootable kernel. The kernel commit uses `[skip ci]` to avoid the pre-existing push workflow's unassigned full Image/modules rebuild; no workflow was changed.

## Artifacts

Durable artifacts are the compressed generated configuration and text logs under [2026-10-15-vpu-checked-build](2026-10-15-vpu-checked-build/). No kernel source or generated binary is duplicated in the project repository. The unchanged reference and new host results have separate evidence records.

## Device validation

Not tested. No phone or firmware execution. The helper has no runtime caller, VPU enablement or integration effect; OPP, IOVA/PAS/HFI, physical bandwidth and LLCC policy gates remain unchanged.
