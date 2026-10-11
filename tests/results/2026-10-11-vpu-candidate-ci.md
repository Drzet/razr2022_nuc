# Build record: VPU provisional Iris ARM64 / binding source checks

- Date: 2026-10-11.
- Project repository commit used for **successful** check: `Drzet/razr2022_nuc` `razr/vpu` at `7b9a21ba30c83a38b71ba36d2bc7c6df3d749485`.
- Kernel repository / branch / exact commit: `Drzet/linux` `razr/vpu` at `9bc913217b9051f515970c4b65770efb3374e33a`.
- Upstream baseline commit: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- Board-support and subsystem commits: standalone VPU candidate only; Boot reference `cb9105ebeb9485e31d044d4fa69396b415523669` **not integrated**.
- External patches: none.
- Host/build environment: GitHub-hosted `ubuntu-24.04` runner, workflow `.github/workflows/vpu-hfi-audit.yml`.
- Toolchain: `gcc-aarch64-linux-gnu`, `binutils-aarch64-linux-gnu`, Ubuntu runner packages recorded in `apt-install.log` and `cross-gcc.txt`; Python3 and C host compiler recorded in artifacts. `dtschema 2026.9`; full Python dependency versions in `pip-freeze.txt`.
- Architecture and configuration base: `ARCH=arm64`, `arch/arm64/configs/defconfig`; resolved `CONFIG_ARCH_QCOM=y`, `CONFIG_VIDEO_QCOM_IRIS=m`, `CONFIG_MEDIA_SUPPORT=m`. Full generated config was not uploaded, **only configuration SHA-256 and selected lines** were recorded; reproducibility gap to correct in next run.
- Configuration fragments in application order: none.
- Generated configuration SHA-256: recorded in `config-sha256.txt` inside artifact, not copied into this note. Exact resolved file not preserved.
- Firmware manifest/hashes: **no oneli stock images or proprietary firmware included**. Firmware file SHA-256 remains unknown; public mirror URL and download blocker recorded in [resource/firmware matrix](../../docs/vpu/2026-10-11-resource-firmware-matrix.md).

## Commands and results

[CI run 38165075988](https://github.com/Drzet/razr2022_nuc/actions/runs/38165075988), conclusion **success**. The HFI source audit and synthetic host layout check both completed successfully. The separate ARM64 candidate job passed:

```sh
make -C kernel O="$PWD/out" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
make -C kernel O="$PWD/out" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j2 modules_prepare
make -C kernel O="$PWD/out" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- KBUILD_MODPOST_WARN=1 -j2 M=drivers/media/platform/qcom/iris modules
make -C kernel ARCH=arm64 O="$PWD/out" DT_SCHEMA_FILES=Documentation/devicetree/bindings/media/qcom,sm8475-iris.yaml dt_binding_check
```

- PASS: changed Iris sources (including `iris_platform_vpu2.c`, `iris_probe.c`, `iris_firmware.c`) compiled using ARM64 GCC; kernel emitted linked `kernel/drivers/media/platform/qcom/iris/qcom-iris.ko`.
- **LIMITATION:** isolated `M=` module build had no full `Module.symvers` and used `KBUILD_MODPOST_WARN=1`. `modpost` reported undefined symbols including `v4l2_m2m_init` and `qcom_pas_shutdown`; these warnings do **not** demonstrate an actual module link problem in a complete in-tree kernel build, nor do they prove a loadable working module. Full in-tree `modules` build with `Module.symvers` remains pending.
- PASS: `dt_binding_check` for new `qcom,sm8475-iris.yaml` completed with exit 0 (SCHEMA, CHKDT, LINT, STYLE steps). This validates only the schema source. No combined board DTB/`dtbs_check` was run.
- PASS: pinned source HFI audit 97/97 matching direct numeric IDs, fixed packet layouts; source init token checks and host-compiled synthetic `hfi-host-layout.c` passed.
- UNKNOWN: exact Motorola oneli `vpu20_4v` binary protocol and PAS authentication.

Preceding [run 38164857539](https://github.com/Drzet/razr2022_nuc/actions/runs/38164857539) **failed for a CI filename error**, not a C compiler error: it looked for `iris.ko` despite Kbuild producing `qcom-iris.ko`. The failure prevented its schema step, so the later successful run above is the correct validation reference. Earlier intermediate runs during the VPU script edits are superseded; retain their failures in Actions history.

## Image preparation

Not applicable. No oneli boot image, DTB merge, firmware image or initramfs was created.

## Artifacts

- [Candidate ARM64 build/schema artifact](https://github.com/Drzet/razr2022_nuc/actions/runs/38165075988/artifacts/11712235364): `vpu-arm64-candidate-38165075988-1`, GitHub reported archive digest `sha256:f1b1176efc037a0783ff889f25126edf31a992419b10ab6d67c0ac0c5d47952a`. Logs include `iris-module-build.log`, `sm8475-iris-binding.log`, `kernel-sha.txt`, `config-sha256.txt` and version manifests.
- [HFI pinned source/host-ABI audit artifact](https://github.com/Drzet/razr2022_nuc/actions/runs/38165075988/artifacts/11712230196): `vpu-hfi-source-38165075988-1`, digest `sha256:f5a70bf62aee583bd1f6077a290bce3b55a54b2052332dfa8e8aa34aa5518553`. Contains source audit JSON and host synthetic test logs.
- Artifacts expire under the workflow's 30-day retention policy; keep this durable manifest and source scripts.

## Device validation

**Deferred: handset unavailable.** No driver probe, signed firmware load, HFI handshake, decoder node, VP9 decode or browser acceleration verified. This test is a source/compile/schema stage only.
