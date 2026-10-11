# Oneli compiled-FDT audit: 2026-10-11

- **Outcome:** PASS for checks implemented in the pinned Python auditor; **not** a full DT schema pass and not hardware validation.
- Kernel repository: `Drzet/linux`, `razr/boot` exact tested SHA `f13417376a9b8627ac0a459496b98f3040e01840`; upstream baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- Project source for checker: `Drzet/razr2022_nuc`, commit `908fd4a21416c555261856d0e4fdf80d0c34f794`, `tests/scripts/check-oneli-dtb.py`; pinned by the workflow checkout at kernel SHA above.
- [GitHub Actions run 38174737265](https://github.com/Drzet/linux/actions/runs/38174737265): **completed / success**, job 114574636696.
- [Evidence artifact 11715795518](https://github.com/Drzet/linux/actions/runs/38174737265/artifacts/11715795518), `oneli-fdt-38174737265-1`, 102227 bytes, GitHub-reported ZIP digest `sha256:55048b54ee63b473ebbad8862c3a0c245c5af540f8278433da137ebaf4d55340` (not independently recomputed); contains compiled DTB, `.config`, tool versions, build/apt logs and JSON/text audit.
- Host: hosted Ubuntu 24.04 runner with AArch64 GCC and dtc; versions and environment captured in artifact `versions.txt`, not independently copied or asserted here.
- No external patches, kernel modules, kernel Image, firmware binaries or boot images generated. No device firmware/board runtime measurements.

## Executed workflow commands

```sh
export ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-
make O=out defconfig
make O=out -j"$(nproc)" qcom/sm8475-motorola-oneli.dtb
python3 project-audit/tests/scripts/check-oneli-dtb.py \
  out/arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dtb \
  --output evidence/audit.json
```

## Actual compiled-tree outcome

```text
nodes=893 reserved=39 overlaps=0 phandle_refs=888 decode_errors=0 active_to_disabled=35 GPU_OPPs=13
```

- All **39** statically addressed `/reserved-memory` records were obtained from the compiled DTB, not source text; pairwise interval overlaps **zero**. Oneli ADSP `0x85700000 + 0x02800000` and video `0x9fd00000 + 0x00700000` sizes verified in compiled output. The invalid inherited RMTFS overlap is absent.
- GPU `qcom,adreno-730.2` is **disabled** and exactly **13** frequency/level OPP pairs match the pinned GPU-owner proposal, including corrected 220MHz RPMh corner. This is source transcription accuracy, not GPU compatibility or validation of the independent CX rail votes.
- UART7 at `/soc@0/geniqup@9c0000/serial@99c000` and all ancestors are enabled. Direct UART/QUP0 provider references to unavailable clock/power dependencies would have failed the gate.
- **888** decoded regulator supply/clock/reset/power-domain/interconnect/IOMMU/DMA/other supported phandle references; **zero** parser errors. Optional zero phandle cells in inherited clock arrays are handled as valid absent entries rather than fabricating unresolved providers.
- **35 enabled-consumer → disabled-provider references** remain *warnings recorded in JSON*. Examples include GCC parent clocks from intentionally disabled UFS/USB/PCIe PHYs, audio codec to disabled ADSP GPR clock, and display clock parent from disabled DSI PHYs. Such cross-references may be legal placeholders and are not proof of a probed clock. Any subsequent active consumer enablement must re-review its chain; the checker only treats UART7/QUP0 direct disabled dependencies as fatal. This separation prevents a false failure without hiding the references.
- The checker does not prove actual board DDR size, bootloader-selected DTBO, programmable regulator parent wiring, functional UART pins, GPU firmware, UFS storage, USB role or physically booted Linux.

## Failed first iteration, reason and correction

[Run 38174586784](https://github.com/Drzet/linux/actions/runs/38174586784), tested kernel `5e713100d9743b120cb059bfb4800cc7d8ab8fe5`, project checker `ceb102384214cbaa714e9ebf88765fe97f786ea4`, **failed its Python check** despite confirming 39 regions / zero overlaps / 13 GPU OPPs. The checker mistakenly treated an optional zero clock specifier as an unresolved provider and treated all 35 inherited disabled-provider references as fatal. Corrected logic in project `908fd4a...` now recognizes zero specifiers, emits all 35 cross references to JSON, and leaves hard failures for invalid nonzero references and UART7/QUP0's required dependencies. New completed run above is the first successful exact result. Do not attribute the first failure to an actual new DT incompatibility.

## Subsequent schema validation

At this result publication, the original `dt_binding_check` all-examples jobs were still active and are **not** part of this result. A separate Boot exact oneli DTB all-applicable schema workflow is being optimized to validate one target rather than building every Linux binding example; record its own conclusion and diagnostics in a separate result. Neither `dtc` compilation nor this Python script is equivalent to all-schema `dtbs_check`.

**Physical tests:** Not performed. Stock ADB has established actual model/firmware and PVT hwrev, but native-Linux boot remains untested and the phone is disconnected.
