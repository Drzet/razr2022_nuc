# Build record: disabled VPU consumer ARM64 compilation and module linkage

- Date: 2026-10-16. Assignment: coordinator `dfbac4c08358d1cc73ff262b39fe05657ecabd49`; project parent `29c59a2cb58559e0c00c2b5baead5bb5f8c95d32`.
- Kernel source: `Drzet/linux:razr/vpu-provenance-v5@3086118adc521943bd533f98d53b136cf4694bc2`, after implementation `18f326a67deb0df2ff873cb62ebae9d81c60a3b0` and binding/fixture `afd1712af59341447876df649ae670c046d84658`. Assigned parent `7ac8d3afedfde74286b52e11aaa1eca42a1329a5`.
- Upstream baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. Accepted integration/Boot hierarchy `2b5acf108ae37040ac1e652e029bb37f5609e886` remains unchanged; no new combined candidate.
- Environment: writable isolated checkout `/tmp/razr-vpu-checked`; shared `/workspace/linux` unchanged. Output directories `/tmp/vpu-checked-build` (objects) and `/tmp/vpu-consumer-link` (focused dependencies/module). AArch64 GCC 15.2.0; `W=1`.
- Reuse: accepted calculator C/header/math and prior vectors unchanged. Existing Linux ICC, OPP, CCF and genpd APIs reused; no external patch, firmware or new provider implementation imported.

## Configuration and commands

The object build reuses the earlier ARM64 defconfig plus `VIDEO_QCOM_IRIS=m`, preserved as [object.config.gz](2026-10-16-vpu-consumer-build/object.config.gz). Its decompressed SHA256 is `8ed994a9873de36b7cf2d40e33740d18c35e3961bf580b5d18bb5a8197fac0f7`.

The link build starts from ARM64 `allnoconfig`, then enables MODULES, COMPILE_TEST, OF, PM, INTERCONNECT, QCOM_SCM, media/V4L2 platform support and `VIDEO_QCOM_IRIS=m`. Focused configuration corrections enable PM_DEVFREQ/PM_OPP, ARCH_QCOM, ARM_SCPI_POWER_DOMAIN=m (a compile-test selector for actual generic-domain code), HWSPINLOCK, RESET_CONTROLLER, QCOM_SOC and QCOM_SMEM=m. Iris selects QCOM_UBWC_CONFIG=m. ARM_SCPI_POWER_DOMAIN is not a phone hardware assertion or deployment choice. No baseline manifest changed.

The exact generated [link.config.gz](2026-10-16-vpu-consumer-build/link.config.gz) is authoritative; decompressed SHA256 `d3b9555dd16a17d6f06d9caf7cea941745052ec923df16e15f18ac3d6727bffa`. [Configuration log](2026-10-16-vpu-consumer-build/config.log) preserves configuration stages. Earlier minimal configurations compiled some provider stubs and are not the qualified final linkage result. Final configuration enables real OPP, generic domains, ICC, UBWC and reset dependencies. The [module imports](2026-10-16-vpu-consumer-build/module-framework-imports.txt) confirm real `devm_pm_domain_attach_list`, `devm_of_icc_bulk_get`, `icc_set_tag`, `qcom_ubwc_config_get_data`, and OPP/clock APIs.

From the isolated kernel checkout, final checks were:

```sh
make -j4 O=/tmp/vpu-checked-build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- W=1 drivers/media/platform/qcom/iris/
make -j4 O=/tmp/vpu-consumer-link ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- W=1 vmlinux modules
PATH=/tmp/vpu-consumer-schema/bin:$PATH python3 tools/testing/iris-upstream/schema-test.py /tmp/vpu-consumer-schema-evidence
scripts/checkpatch.pl --no-tree --strict -q - < <(git show --format= 18f326a67deb0df2ff873cb62ebae9d81c60a3b0)
scripts/checkpatch.pl --no-tree --strict -q - < <(git show --format= 3086118adc521943bd533f98d53b136cf4694bc2)
aarch64-linux-gnu-readelf -h /tmp/vpu-consumer-link/drivers/media/platform/qcom/iris/qcom-iris.ko
```

Reproduce the link configuration by decompressing the saved config into a new output directory's `.config`, running `olddefconfig`, then the same `vmlinux modules` target with that directory. The final incremental check at the committed source and all prior dependency compilation are recorded separately.

## Results and artifacts

**PASS** ARM64 Iris object compilation and combined `qcom-iris.o`: [object log](2026-10-16-vpu-consumer-build/object-build.log). **PASS** dependency/module build, `MODPOST Module.symvers`, and `LD [M] .../qcom-iris.ko`: [dependency build](2026-10-16-vpu-consumer-build/link-build.log), [final committed-source check](2026-10-16-vpu-consumer-build/link-final.log). The final run recompiles the response guard and reruns modpost/link. No Iris compiler/modpost diagnostic. Earlier minimal COMPILE_TEST configurations produced unrelated `arch/arm64/kernel/sys.c` override-initializer warnings; they are not reported as Iris failures or hidden as a warning-free full-kernel result.

- Actual linked module SHA256: `f47b98e3252efb622d08748657ebaea14d84f5a53e8134a7c8299f8c799e02c8`.
- Actual Module.symvers SHA256: `9f4914a135355be3e776b6d917a615f62e3ac5b0191ce4501b054b486c8aa64e`.
- [ELF header](2026-10-16-vpu-consumer-build/module-elf.txt): relocatable ELF64 AArch64. Module/generated binary remains outside this repository.
- Strict checkpatch passes both production commits: [implementation](2026-10-16-vpu-consumer-build/implementation-checkpatch.log), [quarantine guard](2026-10-16-vpu-consumer-build/quarantine-checkpatch.log); quiet successful output is empty.
- Focused schemas use dt-schema `840a01d414daf3e8ac0b8a386c36edb68f397189`, installed version `2026.10.dev2+g840a01d41`. **PASS** binding documentation/schema compilation, one positive and 11 expected-invalid enabled-instance copies, plus unchanged hierarchy/range checks: [schema log](2026-10-16-vpu-consumer-build/schema.log). The committed fixture remains disabled.
- [Artifact/config/log manifest](2026-10-16-vpu-consumer-build/manifest.json) preserves hashes; [host evidence](2026-10-16-vpu-consumer.json) records the separate 52 scenarios / 2321 assertions against clean committed source.

## Image preparation and device validation

No Image, boot image, ramdisk, DT integration, firmware operation or handset trial. `vmlinux modules` supplies the required focused link/export evidence; it is not a combined deployable artifact or acceptance of this minimal configuration for the phone. Both publication branches retain tested history. Kernel commits skip the existing push workflow's unassigned Image rebuild.

Not hardware-tested. SM8475 probe remains disabled with `-EOPNOTSUPP`. OPP division by three remains [INFERRED, USER-ACCEPTED FOR DEVELOPMENT]; readback is a provider report. Physical bandwidth/cache/clock adequacy, firmware/PAS/HFI and active DMA are unverified; inherited IOVA reservation failures remain a separate source gate. Failed OPP transitions stay uncertain; quarantined contexts require reviewed provider recovery/reclamation.
