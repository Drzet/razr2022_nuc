# VPU third-round handoff: complete ARM64 build and hosted Motorola stock evidence

**Date:** 2026-10-11. Owner: VPU, branch `razr/vpu`. This supersedes only the pending validation/archive results in the previous [VPU handoff](2026-10-11-vpu-next-tasks.md); historical records are preserved.

**Baseline:** `Drzet/linux` `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`, unchanged. **Tested VPU kernel head:** `7f1d729b6f458f1e76efe2894eb3c544bc9db856` ([draft PR #2](https://github.com/Drzet/linux/pull/2)). Boot-shared DT is **not** modified, merged or integrated. **Coordinator workflow successful PR run:** [38170604512](https://github.com/Drzet/razr2022_nuc/actions/runs/38170604512), head branch SHA `caf55be52c43da0ffea14b0009087c6c1bdf4a9b` (actual tested kernel SHA separately verified by `kernel-sha.txt` and `tested-kernel-sha.txt`).

## Result 1: dependency-complete ARM64 Image/modules build PASSED

Workflow `.github/workflows/vpu-hfi-audit.yml`, run 38170604512: both `hfi-source-audit` and `iris-candidate-arm64` jobs **success**. ARM64 GCC cross-compiled an in-tree `Image modules` build using regular modpost. No `KBUILD_MODPOST_WARN=1`; populated `Module.symvers` and full `.config` preserved. This replaces the prior warning-tolerant external `M=` module check. A new `qcom,sm8475-iris.yaml` `dt_binding_check` also passed. No combined oneli Boot DTS/`dtbs_check` performed.

**Command contract:**

```sh
make -C kernel O="$PWD/out" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
make -C kernel O="$PWD/out" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j2 Image modules
make -C kernel O="$PWD/out" ARCH=arm64 DT_SCHEMA_FILES=Documentation/devicetree/bindings/media/qcom,sm8475-iris.yaml dt_binding_check
```

**Artifact and hashes:** [ARM64 build evidence](https://github.com/Drzet/razr2022_nuc/actions/runs/38170604512/artifacts/11714598972), GitHub archive SHA256 `eea18b050cfe683389fa51937cdcaedd0676ac820cd15d1aeefca8494667d430`.

| Generated file | SHA-256 |
| --- | --- |
| `out/arch/arm64/boot/Image` | `1ab59d37f0d823acccc4671d7ab5559cdcbfd998711d912a9b7dd39597e187f8` |
| `out/Module.symvers` | `5802d8bb9cb077c61dcf0d7b2bdc8d32793329389156b3b312e7339f9a3d3151` |
| `out/drivers/media/platform/qcom/iris/qcom-iris.ko` | `d0f9f8e9c49c699382c021a1371572cb6e6c632e78441d8eeaf67d0b70710dc2` |

The artifact contains `resolved-arm64-defconfig` (full generated `.config`), `Module.symvers`, binary `qcom-iris.ko`, cross-compiler/tool versions, module build log and schema log. Compiles/links are **not** VPU probe or runtime tests. [Host HFI artifact](https://github.com/Drzet/razr2022_nuc/actions/runs/38170604512/artifacts/11713412405) also succeeded (97/97 shared direct-number macros, 32/32/64 byte layouts, synthetic tests), artifact SHA256 `522f3a853dd77b753d20425bbef198ca2bb357c9a5902e11f7427694cace4a8b`.

## Result 2: public Motorola stock package acquired, headers and DTBOs parsed

- **Full public ROM:** [CI run 38169190369](https://github.com/Drzet/razr2022_nuc/actions/runs/38169190369), HTTP 200 download, exactly **4,353,164,507** bytes, ZIP SHA256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`. This is a public `U2SLS34.1-42-14-11` reference; it matches the device's previously captured build label, **not** proof of identical binaries or active overlay. No proprietary bytes retained in Git.
- **ZIP64 selective verification:** [CI run 38170377311](https://github.com/Drzet/razr2022_nuc/actions/runs/38170377311), both the bounded HTTP ZIP member parsing and `dtc` examination succeeded. Source head `c1711e0de97f657d604ae5d593af9cee8698ae91`; tested checkout/revision is recorded inside [metadata artifact](https://github.com/Drzet/razr2022_nuc/actions/runs/38170377311/artifacts/11713227502), archive digest `6fd35148471e32cc88f3fc11e10f371f1e47bca752f7ff0e07768caa169a1621`. The earlier `38169976751` green result was a **false positive** caused by an unhandled ZIP64 extended offset hidden by a logging pipe; the parser now handles ZIP64 and the workflow uses `set -euo pipefail`.
- **Boot headers:** `boot.img` version **4**, header size **1584**, kernel size **46,854,172**, ramdisk size **1,380,093**; `vendor_boot.img` version **4**, page size **4096**. Exact individual SHA-256 values in [verified boot/DTBO report](../vpu/2026-10-11-public-stock-boot-dtbo.md).
- **DTBO:** `dtbo.img` SHA256 `daf02eb24af55cf4c20569db51b5bca70f0550d035846672ef3054f0c0484bd0`, four valid extracted DTB candidates. All four are `model=oneli` with root compatible `qcom,cape-mtp`, `qcom,cape`, `qcom,mtp`, `moto,oneli`. No effective board overlay selected: Android DT table IDs/revisions are all zero.
- **Container shape:** `super.img_sparsechunk.0` through `.15` contain the undissected vendor/system/etc. partitions. The signed VPU `vpu20_4v` image and GPU ZAP are **not yet extracted**. Boot/GPU should reuse this single reference hash rather than downloading competing packages.

Provenance is centralized in [shared issue #10](https://github.com/Drzet/razr2022_nuc/issues/10). Boot consumes boot/vendor_boot/DTBO identities, GPU consumes stock GPU firmware candidates when vendor extraction becomes available, Power consumes relevant overlay metadata; VPU owns the shared acquisition manifest. No full images or firmware blobs were published.

## Result 3: source-level driver/schema consistency reconciled

At kernel `3d532ed35ab98ce45efe0be65f7ec165e27e2a4c` the SM8475 binding now **requires four named power domains** (venus/vcodec0/mxc/mmcx) and `operating-points-v2` because Iris probe unconditionally attaches both GDSC and OPP domains and calls `devm_pm_opp_of_add_table`. The schema's old mandatory two-IOMMU mapping was relaxed to one or two because two downstream context banks are insufficient evidence to require two upstream device specifiers. It remains an **unresolved mapping**.

At kernel `7f1d729b6f458f1e76efe2894eb3c544bc9db856`, Qualcomm UBWC config gains `qcom,sm8475` using the [INFERRED] Waipio LPDDR5 v4 HBB16 defaults. Without this, the pinned `qcom_ubwc_config_get_data` provider lacked a root-compatible match and Iris probe would return `-EINVAL`. The independent Waipio source uses `UBWC_CONFIG(8,32,16,0,1,1,1)`, matching the default payload formulas. Actual device memory/SMEM HBB remains unknown. See [resource/probe contract](../vpu/2026-10-11-iris-probe-contract.md). GPU and Boot need to review the shared SoC UBWC provider change.

## Remaining gates

- **No signed Motorola VPU firmware version/hash**: extract `vendor` and `odm` from the pinned public super sparse chunks; record exact `vpu20_4v*`, ZAP and vendor firmware hashes plus QC version marker. Existing direct ZIP member inspection is **not** equivalent.
- **[INFERRED] resource profile:** mainline/Iris platform data still includes provisional SM8250 bandwidth/OPP policies, VPU2 buffer sizing, DMA aperture, and SMMU stream mapping. No board node should be enabled until reviewed.
- **Boot ownership:** no combined disabled `video-codec@aa00000` DT validation yet. Boot alone owns shared `sm8475.dtsi` and `sm8475-motorola-oneli.dts`.
- **Phone unavailable:** no PAS 9 authentication, HFI handshake, V4L2 decode registration, video throughput, or Chromium playback tests. The reported old ADB capture was on **stock Android**, not native Linux.

**Status:** this assignment's dependency-complete ARM64 compile/schema gate and hosted public-package acquisition gate have both passed. Firmware extraction and source-to-board mapping remain independent tasks; no claim of hardware completion.
