# Subsystem handoff: VPU / coordinator NEXT_TASKS follow-up

- Date and originating chat: 2026-10-11, dedicated VPU subsystem chat, second assignment from coordinator main `docs/NEXT_TASKS.md` (sha `8dbf44ee4ca5fc096dbf740b0ce8c210723a3736`).
- Kernel repository / branch / exact commit: `Drzet/linux` `razr/vpu` at **`9bc913217b9051f515970c4b65770efb3374e33a`**, after five VPU-only commits. [Draft kernel PR #2](https://github.com/Drzet/linux/pull/2), **not merged**.
- Coordination evidence: `Drzet/razr2022_nuc` `razr/vpu`; see draft [PR #1](https://github.com/Drzet/razr2022_nuc/pull/1). Exact committed [source matrix](../vpu/2026-10-11-resource-firmware-matrix.md), [HFI comparison utility](../../scripts/audit-vpu-hfi.py), [stock-inventory utility](../../scripts/inventory-oneli-firmware.py) and [CI record](../../tests/results/2026-10-11-vpu-candidate-ci.md). Branch SHA after handoff publication to be read from PR #1, not guessed.
- Upstream baseline SHA: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`, unchanged.
- Required board-support and other subsystem SHAs: referenced Boot head `cb9105ebeb9485e31d044d4fa69396b415523669` (**not integrated**). No GPU/USB/Power/DP SHA required to compile candidate in isolation. Actual board/SoC integration requires an exact Boot successor SHA, reviewed firmware and resources.
- Evidence stage: **researched yes; implemented candidate yes; ARM64 compiler and changed-schema tested yes (bounded); full kernel module dependency build no; hardware-tested no**.

## Changes and provenance

The first [VPU HFI handoff](2026-10-11-vpu-hfi-audit.md) remains historical evidence. This update implements its source-comparison next steps and keeps the signed-firmware gap explicit.

1. Reproducible HFI audit `scripts/audit-vpu-hfi.py`: six inputs pinned by exact repository commit **and Git blob SHA**, audited against the Waipio/SM8475 host driver and baseline Iris Gen2. The reproducible static count remains 97 overlapping directly numeric `HFI_*` constants, 97 equal, 0 unequal. The vendor/upstream fixed layouts agree (header 32 bytes/alignment 4; packet 32/4; buffer 64/8); matching field names/offsets, system-init command/flags and seven UBWC property IDs. The source audit now also reports explicit semantic deviations: vendor conditional UBWC configuration and packet-capacity checks versus upstream firmware/UBWC configuration behavior and formulas. [INFERRED] Identical host format makes Iris VPU2+Gen2 plausible, **not verified Motorola firmware compatibility**.
2. Synthetic host C layout assertions in `tests/vpu/hfi-host-layout.c` and Python source/parser self-test. Fake stock DTBO/firmware fixtures in `tests/vpu/test-inventory.py`; fixtures contain no real proprietary bits.
3. Public firmware reference: mirror lists `XT2251-1_ONELI_RETEU_14_U2SLS34.1-42-14-11_subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.xml.zip` at `RETGB`, ~4,353,164 KB. URL and explicit DNS/unsupported binary-download blockers are documented in the source matrix. No bytes, ZIP checksum, `vpu20_4v` hash, oneli ZAP hash or DTBO table were acquired. Script `inventory-oneli-firmware.py` produces SHA-256 inventory when package is supplied. Do not claim the public ROM is installed on the absent handset.
4. A vendor-to-upstream MMIO/IRQ/PAS/clock/reset/GDSC/RPMh/IOMMU/memory/ICC/capability matrix in `docs/vpu/2026-10-11-resource-firmware-matrix.md`, separating Motorola controller/board source and Xiaomi comparison.
5. **RFC kernel candidate**, five commits after baseline:
   - `f5b6ae7c2a69a70f85f474648df79a3f8c411959`: new `Documentation/devicetree/bindings/media/qcom,sm8475-iris.yaml` requiring source-supported two resets, two IOMMU context endpoints and explicit `firmware-name` (the last prevents guessing Motorola's firmware filesystem path).
   - `c01332709b34a8c5b57745495022b687dd996a05`: `drivers/media/platform/qcom/iris/iris_platform_vpu2.c` candidate profile, VPU2 and Gen2 host descriptor, four pipes from pinned Waipio reference.
   - `381f4833410f3945cdb70a8e8806d2462a31dd8a`: declare `sm8475_data` in `iris_platform_common.h`.
   - `b296bc972ef91871a2f29afda6c62ec7e49b158a`: bind `qcom,sm8475-iris` in `iris_probe.c`.
   - `9bc913217b9051f515970c4b65770efb3374e33a`: `iris_firmware.c` returns `-ENOENT` for missing DT firmware-name when a platform descriptor intentionally has no default, instead of requesting an unspecified blob.
   
   **[INFERRED] assumptions remain**: VPU2 ops reuse, HFI Gen2 binary acceptance, SM8250-derived DDR bandwidth estimates, `mxc/mmcx` OPP power-domain mapping, capacity policy, and buffer-size algorithm. These are review-only; do not enable an oneli node from this candidate alone.

## Shared files and integration

Kernel `razr/vpu` modifies **only** the new Iris binding and four Iris driver paths enumerated above. No `arch/arm64/boot/dts/qcom/sm8475.dtsi`, `sm8475-motorola-oneli.dts`, shared defconfig, GPU/USB/Power/DP branches, or kernel `master` were touched.

**Boot retains sole ownership of shared DT.** It may separately integrate a *disabled* `video-codec@aa00000` node at MMIO `0x0aa00000`, GIC SPI 174, PAS 9 (driver), with reviewed clocks, GDSCs, two nonsecure IOMMUs, two reset lines, ICC consumers, OPPs and the oneli video reserved memory `0x9fd00000 + 0x700000`, all subject to exact binding/source reviews. No inferred firmware filename or electrical assertions may be put into the shared DTS. Do not cherry-pick to integration until Boot supplies its exact applicable commit and checks.

## Validation

- **PASS**: GitHub Actions [run 38165075988](https://github.com/Drzet/razr2022_nuc/actions/runs/38165075988), project commit `7b9a21ba30c83a38b71ba36d2bc7c6df3d749485`, kernel candidate `9bc913217b9051f515970c4b65770efb3374e33a`. HFI host audit, synthetic parser/layout C build, ARM64 `CONFIG_VIDEO_QCOM_IRIS=m` source compile plus linked `qcom-iris.ko`, and `qcom,sm8475-iris.yaml` `dt_binding_check` all completed exit 0. `dtschema 2026.9`. See [full build record](../../tests/results/2026-10-11-vpu-candidate-ci.md), logs and artifact digests.
- **Explicit limitation:** isolated `M=` compile lacks full `Module.symvers`; `KBUILD_MODPOST_WARN=1` turns many unresolved external symbols into warnings. This is *not* a demonstrated fully loadable kernel module. Board `dtbs_check` and combined Boot/VPU compilation also not performed. Generated `.config` SHA recorded; full resolved `.config` not retained.
- **FAIL historical (fixed test harness):** [run 38164857539](https://github.com/Drzet/razr2022_nuc/actions/runs/38164857539) tested the wrong expected module filename `iris.ko`; actual Kbuild output is `qcom-iris.ko`. Later run corrected artifact check and passed.
- **NOT PERFORMED:** download/extraction/hash of stock oneli ZIP, actual Motorola signed firmware compatibility, PAS authorization, HFI negotiation, V4L2 registration, 4K VP9 decoding, hardware acceleration/browser playback. Handset is unavailable.

## Blockers and next test

1. **Firmware**: run the new inventory utility against the specific public oneli ZIP from a host able to download it; capture SHA-256 for package, exact `vpu20_4v*` files, `QC_IMAGE_VERSION_STRING`, candidate DTBO entries and any A730 ZAP firmware. Preserve provenance and compare later to actual device build/board.
2. **Profile review**: replace [INFERRED] SM8250 bandwidth table and RPMh corner mappings with justified SM8475 information. Check two nonsecure SMMU context-bank flags and clock source OPP correspondence. Address vendor/upstream UBWC init semantic differences with actual Qualcomm UBWC provider evidence.
3. **Build**: rerun full in-tree ARM64 modules with populated `Module.symvers` and a retained resolved configuration; retain successful `dt_binding_check` and validate a compiled *Boot-owned* disabled node via `dtbs_check`.
4. **Hardware deferred**: once actual Razr becomes available, verify selected firmware/DTB, PAS 9 signed firmware load, Gen2 HFI response/state transitions, V4L2 registration and standalone VP9 3840×2160 decode before Chromium tests.

**Do not merge the RFC profile into integration as operational VPU support on the strength of a compiling candidate.**
