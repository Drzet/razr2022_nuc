# Oneli all-applicable DT schema validation: 2026-10-11

**Result: PASS for a specific compiled oneli DTB checked against the complete processed Linux binding-schema inventory.** Critical binding definitions passed independent `dt-doc-validate`. This does **not** mean all Linux schema example DTS files were built, and does **not** constitute a phone boot test.

## Exact immutable inputs and provenance

- Kernel: `Drzet/linux`, `razr/boot`, **`6eec6ddd7842622668c937a466a8db47d20517b1`** (board sources, GPU OPP replacement, disabled regulator voltage ranges, CI).
- Upstream baseline: **`a5ebb76233b79db01e82e061173cb73c6d2b5c6b`** (unchanged); no subsystem driver commits merged onto Boot.
- Project checker `Drzet/razr2022_nuc` exactly **`908fd4a21416c555261856d0e4fdf80d0c34f794`**, file `tests/scripts/check-oneli-dtb.py`.
- [Successful GitHub Actions run 38175014232](https://github.com/Drzet/linux/actions/runs/38175014232), job `114575455379`; Ubuntu 24.04; ARM64 defconfig; AArch64 cross compiler and `dtc`; dtschema installed in venv. Tool and resolved configuration recorded in evidence artifact.
- [Evidence artifact 11715203203](https://github.com/Drzet/linux/actions/runs/38175014232/artifacts/11715203203), `oneli-dt-38175014232-1`, 118331 bytes, GitHub-reported ZIP digest `sha256:4223572658ab1c6247f528fb001047ef748b280572b8db9ba00ef37b6ae5a040` (GitHub metadata; not independently recomputed). Contains compiled DTB, `kernel.config`, source-version and tool-version records, critical-binding log, oneli schema validation logs, resolved DTS and FDT JSON, compile log and SHA256SUMS.

## Executed commands and results

```sh
export ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-
make O=out defconfig
make O=out -j"$(nproc)" qcom/sm8475-motorola-oneli.dtb

export PATH="/tmp/razr-dt-venv/bin:$PATH"
dt-doc-validate -u Documentation/devicetree/bindings \
  Documentation/devicetree/bindings/arm/qcom.yaml \
  Documentation/devicetree/bindings/pinctrl/qcom,sm8450-tlmm.yaml \
  Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml \
  Documentation/devicetree/bindings/ufs/qcom,ufs.yaml \
  Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-ufs-phy.yaml \
  Documentation/devicetree/bindings/display/msm/gpu.yaml \
  Documentation/devicetree/bindings/display/msm/gmu.yaml

rm -f out/arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dtb
make O=out -j"$(nproc)" CHECK_DTBS=y qcom/sm8475-motorola-oneli.dtb

dt-validate -m -u Documentation/devicetree/bindings \
  -p out/Documentation/devicetree/bindings/processed-schema.json \
  out/arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dtb

python3 project-audit/tests/scripts/check-oneli-dtb.py \
  out/arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dtb \
  --output evidence/oneli-fdt-audit.json

dtc -I dtb -O dts -s \
  -o evidence/sm8475-motorola-oneli.resolved.dts \
  out/arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dtb
```

- `make defconfig`: success.
- Direct one-board DTB build: success.
- Seven critical source schema definition checks: success.
- Kernel Kbuild produced `SCHEMA Documentation/devicetree/bindings/processed-schema.json` from **all source binding YAMLs**, followed by `DTC [C] arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dtb`. No `DT_SCHEMA_FILES` filter was used. Success.
- Separate direct `dt-validate -m`: success, **no schema diagnostics were emitted in the job log**. This directly observes the checker rather than relying only on kernel Kbuild's `|| true`-guarded `dt-validate` invocation.
- Separate compiled-FDT audit: success, exact line:
  `nodes=893 reserved=39 overlaps=0 phandle_refs=888 decode_errors=0 active_to_disabled=35 GPU_OPPs=13`.
- Decompiled DTB successfully. No device-test evidence.
- Action log emitted two **Node.js deprecation warnings from GitHub artifact tooling**, not Linux device-tree schema warnings.

## Classified remaining dependencies

There were **zero unresolved nonzero phandle references** in the scanner's covered categories, and no static reserved-memory interval collisions. The **35 enabled-to-disabled provider references** in `oneli-fdt-audit.json` are retained as nonfatal dependency warnings, mainly common SoC GCC→disabled PHY, DSP audio codec→disabled ADSP GPR clock and display clocks→disabled DSI PHY patterns. Several occur in the inherited upstream SM8450 tree; this source attribution is not a separate automated baseline-vs-branch warning diff, and it does not establish that the named peripherals are ready. None involve the enabled UART7/QUP0's directly required providers. Activating USB/UFS/audio/display later requires their own full dependency review.

The GPU OPP table exactly matches the 13 pinned SM8475 frequencies and numerical GPU RPMh levels; GPU/GMU remain disabled and the A730v3 kernel **driver** chip-ID patch remains in another branch. CPU/DDR memory bank size, upstream PMIC parent topology, signed firmware, actual stock DTBO selection, video decode, DP/USB enumeration and UART electrical path are not validated by this test.

## Coverage boundary

The earlier all-YAML **`dt_binding_check` example-build** workflows were too broad/slow and are not used to claim this result. The chosen check compiles all schema YAMLs and uses that complete inventory on **one exact oneli DTB**, plus seven targeted schema-definition checks. It does not run examples for unrelated platforms, full kernel Image build, kernel modules or a real oneli boot.

Physical evidence available independently: a PVT XT2251-1 stock Android 14 handset was inspected through restricted ADB, not native Linux. Actual Linux boot remains **untested**.
