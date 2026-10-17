# PS5169 durable kernel candidate, ARM64 Image/modules and binding validation

**Final result: PASS.** Verified on 2026-10-12 from the completed 2026-10-11 hosted run.

- Kernel candidate branch: `Drzet/linux:razr/usb-ps5169`.
- **Actual tested kernel source commit:** `4cbfc0145d9c837d2ba3fd9050f529a786135403`. The workflow trigger's SHA `068af1339724278235fa0880f565c47c344b3f7b` was the *pre-import* commit; the workflow successfully applied the v3 attribution-preserving source and published separate repairs, then built the final head.
- **CI:** [run 38181747728](https://github.com/Drzet/linux/actions/runs/38181747728), job `114595592411`, completed **success**. [Metadata/build/config artifact 11719113329](https://github.com/Drzet/linux/actions/runs/38181747728/artifacts/11719113329), archive digest `sha256:24ace3b16a551968f89f32e1f353c25f3e0a51ec8547eaa0a09720bd639b930a`.
- **PR:** [kernel draft #5](https://github.com/Drzet/linux/pull/5), intended to remain experimental and not enable oneli GPIO19 or port@1.

## Inputs

Original external [Esteban Urrutia v3 PS5169 series](https://patchew.org/linux/20260810-ps5169-bup-v3-0-a2178b2834d7@proton.me/), preserved commits `3212e1d8a836f3dbbd0a258410b18683a38207ad` (binding) and `551c094e0ce5e7f492fe21d7e6ab2de815343b6a` (driver). Local direct-header commit `cbed833e9d5131fbed49774f385bba38bcd7944f`; local dual VCC/VIO regulator support `4cbfc0145d9c837d2ba3fd9050f529a786135403`. CI checked original driver SHA256 `b76465571bc5a7f80a177660e9290115fedcfbccda1fb43c801e25a6f3a521ed`, original binding SHA256 `3c9f01f921398edf34e7d3b13439306bd26e8f48a75151294ec529c83b852cc3`, before local modifications. The mbox envelope SHA is *not* pinned because Patchew regenerates timestamps; this is source-content pinning.

## Exact build and results

Runner Ubuntu 24.04 x86_64, cross-toolchain `gcc-aarch64-linux-gnu`, `binutils-aarch64-linux-gnu`, kernel build dependencies, Python `dtschema` venv. Workflow source: [razr-ps5169-durable.yml](https://github.com/Drzet/linux/blob/068af1339724278235fa0880f565c47c344b3f7b/.github/workflows/razr-ps5169-durable.yml). Commands after original git-am and separate local commits:

```sh
PATH="$PWD/.ps5169-schema-venv/bin:$PATH" make DT_SCHEMA_FILES=Documentation/devicetree/bindings/usb/parade,ps5169.yaml dt_binding_check
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
scripts/config --enable I2C --enable REGMAP_I2C --enable DRM --enable DRM_BRIDGE --enable TYPEC --module TYPEC_MUX_PS5169
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- olddefconfig
grep -qx 'CONFIG_TYPEC_MUX_PS5169=m' .config
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j2 Image modules
test -s arch/arm64/boot/Image
test -s Module.symvers
test -s drivers/usb/typec/mux/ps5169.ko
aarch64-linux-gnu-readelf -h drivers/usb/typec/mux/ps5169.ko
```

The shell used `set -euo pipefail`. **All steps succeeded**, including `SCHEMA`, `LINT`, `STYLE`, `DTEX`, `DTC [C]`, normal kernel `MODPOST Module.symvers`, `LD [M] drivers/usb/typec/mux/ps5169.ko`, and a verified **ELF64 / AArch64** PS5169 kernel module.

| Exact tested output | SHA-256 from successful job |
| --- | --- |
| `arch/arm64/boot/Image` | `7faf96a0d51be28c57a323c6ccd32aebfa5eccd60064b51dd88253a87178df0e` |
| `Module.symvers` | `ad4f64708b64e132fea71feb4602c437831a2ba1c4f267708f2f8cfcf63725d9` |
| `drivers/usb/typec/mux/ps5169.ko` | `fd9b63ca50dd45d50e3a69b281ba1148673c39a33e359a03228a49846d05dea5` |

Artifact records original source hashes, exact tested-source SHA, full resolved ARM64 `.config`, toolchain info, schema logs, full Image/modules build log, ELF headers/symbols, hashes and commit authorship.

## Acceptance boundary and remaining work

This **closes the third coordinator's PS5169 source durability and full ARM64 linkage build gates**. It does **not** verify GPIO19 reset pulse/polarity (vendor only shows high-enable/low-disable), VCC-before-VIO sequencing on oneli, runtime I2C identity/register transactions, suspend/resume, powered Type-C connector operation, SuperSpeed link, or DP. The original imported code ignores return values from `regmap_write` / `regmap_update_bits` in PS5169 configuration and EQ setup; error propagation still needs a separate narrow review/patch. The external NXP eUSB2 repeater SKU and GPIO7 reset remain unproven. Boot owns all shared board DTS edits; leave electrical consumers disabled.

The requested **four-DTBO USB node/property matrix** is still missing from the currently exported VPU metadata (despite all four DTBO root models/hashes being known); USB request is [issue #10 comment](https://github.com/Drzet/razr2022_nuc/issues/10#issuecomment-6114753777). Do not start a duplicate multi-GB stock download. Phone unavailable, no hardware testing claimed.
