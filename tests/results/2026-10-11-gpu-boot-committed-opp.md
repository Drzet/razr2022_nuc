# GPU committed Boot oneli DTB acceptance

- Date: 2026-10-11; outcome: **PASSED**.
- Test scope: compiled and inspected the **actual Boot committed DTS**, not the earlier disposable GPU OPP source fixture. GPU remains intentionally disabled.
- Run: [GPU committed Boot OPP DT validation #38174125440](https://github.com/Drzet/razr2022_nuc/actions/runs/38174125440), attempt 1.
- Tested project workflow commit: `4c59c36af62d1212be10bce9969b9d66354e275a` on `Drzet/razr2022_nuc` branch `razr/gpu`.
- Tested Boot kernel commit: `9b37ea4953eada0837b18421ce6b74beebfe0a2b` on `Drzet/linux` branch `razr/boot`; it is the **OPP adoption commit**, not a moving branch alias.
- Separate GPU catalog patch **not present** in this Boot-only DTB checkout: `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`.
- Baseline: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- Toolchain: hosted `ubuntu-24.04`, `gcc-aarch64-linux-gnu`, `dtc`, `fdtget`, full versions in run artifact `environment.txt` (not inferred here).
- Configuration: ARM64 `defconfig`; resolved `.config` included in run artifact, **not** a GPU-enabled oneli kernel configuration.
- Firmware and boot image: not prepared; no signed ZAP or GMU binary included.

## Commands and evidence

Executed by [committed workflow](../../.github/workflows/gpu-boot-opp.yml) (with out-of-tree `O=` output):

```sh
make -C kernel O="$out" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
make -C kernel O="$out" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j"$(nproc)" dtbs
python3 tests/scripts/gpu-opp-fixture.py --check "$out/arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dtb"
fdtget -t s "$out/arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dtb" /soc@0/gpu@3d00000 status
```

The last value was `disabled`. Full run logs showed:

```text
PASS: compiled DTB contains exactly 13 SM8475 GPU OPPs with expected RPMh corners
900 MHz -> RPMh level 416
862 MHz -> RPMh level 384
815 MHz -> RPMh level 320
765 MHz -> RPMh level 256
710 MHz -> RPMh level 224
645 MHz -> RPMh level 192
580 MHz -> RPMh level 144
515 MHz -> RPMh level 128
439 MHz -> RPMh level 96
364 MHz -> RPMh level 80
324 MHz -> RPMh level 64
285 MHz -> RPMh level 56
220 MHz -> RPMh level 48
PASS: GPU remains disabled in the committed oneli board DTB
```

The check rejects ten inherited SM8450-only GPU frequency nodes, duplicate frequencies, wrong numeric levels and wrong GPU/GPUCC compatible strings. All checks passed against compiled FDT.

- Artifacts: [`gpu-boot-opp-38174125440-1`](https://github.com/Drzet/razr2022_nuc/actions/runs/38174125440/artifacts/11714519663), artifact ID `11714519663`, 112429 bytes, containing `sm8475-motorola-oneli.dtb`, `kernel.config`, `SHA256SUMS`, environment, configure and build logs.
- GitHub uploaded ZIP SHA256: `1129fe28a5f13f243522c006235c50d1b5a4effeb901f4dd513805e4ff03411c`. Individual DTB/config hashes are recorded inside the artifact, not independently reproduced in this report.

## Boundaries

This is compiled DTB validation, **not** a full dt-schema acceptance report and **not** a GPU module build. The Boot source still has the GPU disabled. The existence and correctness of separate Motorola CX votes, ACD HFI, firmware signature, command-DB contents, user-space rendering, thermal states or usable GPU hardware remain untested. For source disposition see [GMU/RPMh audit](../../docs/gpu_cx_gmu_rpmh_disposition_2026-10-11.md).

Next consumers: Boot can cite this result for OPP transcription; coordinator must select exact Boot and GPU commits separately for an integration build. The full MSM module build remains a distinct acceptance gate.
