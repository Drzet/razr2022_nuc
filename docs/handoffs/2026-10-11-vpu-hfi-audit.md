# Subsystem handoff: VPU / Motorola Razr 2022 (oneli)

- Date and originating chat: 2026-10-11, dedicated VPU subsystem chat.
- Repository / branch / exact commit: kernel `Drzet/linux`, `razr/vpu`, HEAD `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` (branch created; **no VPU kernel commits**). Evidence: `Drzet/razr2022_nuc`, `razr/vpu`, branched from `98a8c35f492ed8f1eedcd2a6b472ea587c894026` (this handoff's documentation commit is the branch head after publication).
- Upstream baseline SHA: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` (selected project baseline; never changed).
- Required board-support and other subsystem SHAs: **not yet available**. Boot's `razr/boot` begins at the same baseline, but no reconciled SM8475/oneli board-support commit was supplied; require an exact future `razr/boot` SHA before integrated tests.
- Evidence stage: **researched: yes (source audit and static subset comparison); implemented: no; build-tested: no; hardware-tested: no**. No oneli firmware bytes, live DTB, boot logs or V4L2 tests were obtained.

## Changes and provenance

### 1. Motorola's controller and memory evidence

The Motorola video DT source `MotorolaMobilityLLC/kernel-video-devicetree`, pinned commit [`56e3632e15ab870f76920f80f19929addf48088b`](https://github.com/MotorolaMobilityLLC/kernel-video-devicetree/tree/56e3632e15ab870f76920f80f19929addf48088b), includes [`waipio-vidc.dtsi`](https://github.com/MotorolaMobilityLLC/kernel-video-devicetree/blob/56e3632e15ab870f76920f80f19929addf48088b/waipio-vidc.dtsi) (blob `7efca994185a058c061480ded659efb6cacec605`):

- Compatible sequence `qcom,msm-vidc`, `qcom,msm-vidc-waipio`, `qcom,msm-vidc-iris2`. It is a **downstream** compatible sequence, not an upstream Iris match.
- `reg = <0x0aa00000 0xf0000>`; interrupt `GIC_SPI 174`; `pas-id = <9>`; `memory-region = <&video_mem>`.
- Firmware designation `vidc,firmware-name = "vpu20_4v"`. This downstream property does **not** equal upstream `firmware-name`, and the bare name does not identify the exact firmware revision or HFI protocol.
- Video CC / GCC clocks (AXI0, MVS0C, MVS0, MVS0 source), GCC/Video CC resets, MVS0C/MVS0 GDSCs, three downstream interconnect paths, non-secure SMMU entries `0x2180/0x0400` and `0x2187/0x0400`, plus separate secure context banks. Downstream allowed rates `239999999, 338000000, 366000000, 444000000` Hz.
- The [`Kbuild`](https://github.com/MotorolaMobilityLLC/kernel-video-devicetree/blob/56e3632e15ab870f76920f80f19929addf48088b/Kbuild) associates `CONFIG_ARCH_CAPE` with `ukee-vidc.dtbo`. The [ukee DTS](https://github.com/MotorolaMobilityLLC/kernel-video-devicetree/blob/56e3632e15ab870f76920f80f19929addf48088b/ukee-vidc.dts) includes the waipio controller description but has a different root compatible. **Which overlays the retail oneli actually loads remains unverified.**

The separate Motorola board DT at [`MotorolaMobilityLLC/kernel-devicetree` revision `90fa7be1db5bd47202673d4431408659149a7359`, `qcom/cape-moto-oneli-base.dts`](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-oneli-base.dts) replaces `video_mem` with a `no-map` region at `0x9fd00000` of size `0x700000`. This is an oneli-source description, **not confirmation** of the phone's currently running memory layout.

### 2. VPU2 hardware and HFI Gen2 host ABI: concrete static match

A separate SM8475 reference tree `LowTension/android_kernel_xiaomi_sm8475`, pinned commit [`39382bf760ccf05a8fb4dddee7138ecac02d4a59`](https://github.com/LowTension/android_kernel_xiaomi_sm8475/tree/39382bf760ccf05a8fb4dddee7138ecac02d4a59), provides a *newer-generation* Waipio video driver (not oneli-specific):

- [`techpack/video/driver/platform/waipio/src/msm_vidc_waipio.c`](https://github.com/LowTension/android_kernel_xiaomi_sm8475/blob/39382bf760ccf05a8fb4dddee7138ecac02d4a59/techpack/video/driver/platform/waipio/src/msm_vidc_waipio.c) (blob `362ff9402757fb247e96a26afa7fabd10e76b945`) sets `VPU_VERSION_IRIS2`, reports **four** VPP pipes, and describes H.264/HEVC/VP9 decode. These are driver configuration/capability tables, not verified oneli measurements.
- [`techpack/video/driver/vidc/src/hfi_packet.c`](https://github.com/LowTension/android_kernel_xiaomi_sm8475/blob/39382bf760ccf05a8fb4dddee7138ecac02d4a59/techpack/video/driver/vidc/src/hfi_packet.c) uses the Gen2-style `hfi_header` / `hfi_packet` envelopes and sends `HFI_CMD_INIT` with `HFI_VIDEO_ARCH_LX`.
- The downstream [`hfi_command.h`](https://github.com/LowTension/android_kernel_xiaomi_sm8475/blob/39382bf760ccf05a8fb4dddee7138ecac02d4a59/techpack/video/driver/vidc/inc/hfi_command.h) (blob `e7128f3ab9428569a7ec7f37493ec86ca9e0111f`) defines identical `hfi_header` and `hfi_packet` field sequences to baseline upstream [`iris_hfi_gen2_packet.h`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/media/platform/qcom/iris/iris_hfi_gen2_packet.h).
- **Reproducible static constant audit:** collect numeric `#define HFI_* <decimal or hex literal>` values from vendor `hfi_command.h` + [`hfi_property.h`](https://github.com/LowTension/android_kernel_xiaomi_sm8475/blob/39382bf760ccf05a8fb4dddee7138ecac02d4a59/techpack/video/driver/vidc/inc/hfi_property.h) (blob `23de0e57667a8e7d412f08f831a7e424f01c75d5`) and compare by macro name with baseline [`iris_hfi_gen2_defines.h`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/media/platform/qcom/iris/iris_hfi_gen2_defines.h) (blob `f43aea10090d8f1d6ae5c20547e5f6321b2ca203`). **203** vendor literals, **110** upstream literals, **97** shared identifiers: **97 equal, 0 mismatches**. This includes `HFI_CMD_INIT = 0x01000001`, `HFI_PROP_IMAGE_VERSION = 0x03000001`, other packet commands and properties. The audit covers only directly numeric macros and does not compare every structure, state transition, feature or firmware revision.
- [INFERRED] The Cape/SM8475 VPU is a strong candidate for the **upstream Iris VPU2 register operations + HFI Gen2 packet generation**; the evidence is much stronger than the `iris2` and firmware filenames alone. **It does not establish compatibility of Motorola's actual `vpu20_4v` binary**.

**Discarded misleading reference:** `MotorolaMobilityLLC/kernel-msm-techpack-video` commit [`9a34a0963efdf57582927ca6fc3a05ee5f9e8dab`](https://github.com/MotorolaMobilityLLC/kernel-msm-techpack-video/tree/9a34a0963efdf57582927ca6fc3a05ee5f9e8dab) exposes *older* `msm/vidc/hfi_packetization.c` with `HFI_CMD_SYS_INIT` and an `msm_vidc_platform.c` match table without `qcom,msm-vidc-waipio`. Do **not** infer Cape's protocol from that unrelated driver-generation snapshot.

### 3. Exact upstream Iris gap

At baseline [`a5ebb76233b79db01e82e061173cb73c6d2b5c6b`](https://github.com/Drzet/linux/tree/a5ebb76233b79db01e82e061173cb73c6d2b5c6b):

- [`drivers/media/platform/qcom/iris/iris_probe.c`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/media/platform/qcom/iris/iris_probe.c) lacks `qcom,sm8450-iris` and `qcom,sm8475-iris` match entries. Adding the clock controller alone cannot register a decoder.
- [`iris_platform_vpu2.c`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/media/platform/qcom/iris/iris_platform_vpu2.c) defines SM8250 with VPU2 ops, four pipes **but Gen1 firmware descriptor** (`qcom/vpu/vpu20_p4.mbn`). SC7280 provides optional Gen1/Gen2 descriptors but **one** VPP pipe. Milos uses VPU2 hardware with a dedicated Gen2 HFI descriptor but **two** pipes. No existing platform definition is safely interchangeable with the four-pipe Waipio tables merely by changing its compatible.
- [`iris_platform_common.h`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/media/platform/qcom/iris/iris_platform_common.h) requires platform-specific firmware descriptors, `vpu_ops`, pipe count, clock mapping, reset table, power-domain names, OPP linkage, ICC data, DMA mask, caps and secure memory/TZ configuration. These must be justified individually.
- [`iris_firmware.c`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/media/platform/qcom/iris/iris_firmware.c) uses PAS 9 (consistent with Motorola's DT numeric `pas-id`), accepts the upstream DT `firmware-name` override, loads segmented MDT firmware via `qcom_mdt_load`, and authenticates using `qcom_pas_auth_and_reset`. It has optional Gen1-vs-Gen2 string sniffing **only when a platform advertises both descriptors**, based on firmware `QC_IMAGE_VERSION_STRING` such as `vfw` or `video-firmware.2.*`; it is not a proof that any firmware named `vpu20_4v` uses Gen2.
- [`qcom,sm8250-venus.yaml`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/Documentation/devicetree/bindings/media/qcom%2Csm8250-venus.yaml) and [`qcom,sm8550-iris.yaml`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/Documentation/devicetree/bindings/media/qcom%2Csm8550-iris.yaml) constrain the possible mainline DT representations. A reviewed SM8475 compatible/binding extension is required; no downstream `qcom,msm-vidc` compatible should be copied as an upstream Iris match.

### 4. Firmware status

- **Unknown:** currently installed oneli Android build/variant, selected video overlay, binary `vpu20_4v` revision, version marker, firmware SHA-256, split MDT segment set, authenticating signature, expected Gen1/Gen2 handshakes.
- **Known source only:** downstream Motorola overlay says `vpu20_4v`, while multiple unrelated Snapdragon device manifests distribute same-named files. This name does not establish substitutability or even the exact binary to load. Do not commit proprietary firmware here.
- **Next acquisition:** read-only extract firmware from the exact oneli stock `vendor` image or handset; capture SHA-256 of each `vpu20_4v.mbn`, `.mdt`, `.bNN` segment present, version marker, source build identifier and file provenance. Choose `firmware-name` under `qcom/vpu/` only after the actual blob and packaging convention are known.

## Shared files and integration

**Ownership: Boot chat exclusively edits and integrates the shared `sm8475.dtsi` and `oneli` board DTS. No shared DT file changed in this VPU work.** The VPU owner may later supply a dedicated Iris driver platform-data commit and binding commit on `razr/vpu`; Boot incorporates reviewed DTS changes into `razr/boot`. Integration records exact cherry-picked SHAs and any conflicts.

**Draft Boot-owned DT requirements (NOT implementation):**

1. Introduce a `video-codec@aa00000` node for **proposed** `qcom,sm8475-iris` (binding and platform match pending review), initially disabled until driver and firmware validation. `reg 0x0aa00000/0xf0000` and SPI 174 follow Motorola sources.
2. Add an oneli-specific reserved `video_mem` reference, proposed `0x9fd00000 + 0x700000`, conditional on the verified actual effective DTB/memory handoff. Retain proper `no-map` reservation; avoid overlapping ADSP memory.
3. Adapt Motorola's GDSC/GCC/video clocks, resets, nonsecure SMMU IDs and bus paths to *baseline upstream binding conventions*, not downstream supply/clock naming. [INFERRED] Two SMMU endpoints `0x2180` and `0x2187` may be needed for distinct bitstream/pixel paths; check IOMMU mapping and flags before finalizing. Secure context banks require separate policy, not a blind port of vendor child nodes.
4. Resolve the requested OPP frequencies (Motorola source `239999999`, `338000000`, `366000000`, `444000000` Hz) against SM8475 VIDEOCC driver and appropriate RPMh required-opps; **do not copy SM8250 or Milos OPP power domains blindly**. The four downstream frequencies are not a verified final mainline table.
5. Map downstream interconnects (three paths) to upstream Iris `cpu-cfg`, `video-mem` (two consumers) with correct SM8475 master/slave endpoints. Confirm reset `bus` and `core` and upstream clock names `iface`, `core`, `vcodec0_core`. Set `firmware-name` only after packaging the identified oneli blob. Use the binding-required `dma-coherent` only if corroborated.
6. Reconcile `CONFIG_ARCH_CAPE` → `ukee-vidc.dtbo` ambiguity with extracted oneli DTBO. Avoid interpreting an Android overlay selection rule as proof of effective retail hardware config.

**Potential dedicated VPU kernel files** (none currently changed): `drivers/media/platform/qcom/iris/iris_probe.c`, `iris_platform_vpu2.c`, `iris_platform_common.h` plus any dedicated platform header, reviewed `Documentation/devicetree/bindings/media/*.yaml`. **Shared with Boot, proposal only:** `arch/arm64/boot/dts/qcom/sm8475.dtsi` and oneli board DTS. The kernel fork's `master` and the shared upstream baseline remain unchanged.

**Integration order:** confirm firmware + protocol, finalize VPU binding/platform data, Boot integrates reviewed disabled DT node into its actual board support, run `dt_binding_check` and `dtbs_check` on the recorded combined commit, then attempt firmware load/decoder tests. Boot and VPU must each name their exact commit, rather than relying on mutable branch names.

## Validation

- **PASS (source checks):** fetched pinned Motorola video overlay, Motorola oneli reserved-memory source, VPU2/Gen2 upstream Iris code, SM8475 Waipio driver, and compared directly numeric HFI defines: **97/97 common constants match, zero mismatches**.
- **NOT DONE:** full structural ABI review, actual signed Motorola firmware inspection, protocol negotiation, qcom PAS auth, kernel/module compilation, device-tree schema validation, boot, decode or GPU/browser tests.
- Build toolchain/configuration, test artifact names and hashes: **not available**. No claim of implementation or successful hardware operation.

## Blockers and next test

1. **Firmware HFI identity gate:** acquire matched oneli firmware, hashes and `QC_IMAGE_VERSION_STRING`; compare protocol expectations with the Gen2 host ABI. Accept only when header/protocol and version information agree; if ambiguous, record ambiguity and use a controlled on-device firmware-init test instead of guessing.
2. **Platform-data gate:** derive four-pipe resource/capability tables, clock/power reset mapping, IOMMU DMA range, firmware descriptor and secure memory setup from specific sources. Produce separately reviewable Iris binding and platform-data commits on `razr/vpu`; no unsupported copy of SM8250 or Milos.
3. **Boot dependency:** obtain exact Boot SoC/board commit and effective retail DT memory/IOMMU evidence. Boot incorporates shared DT proposal; validate schema and DTS with recorded compiler configuration.
4. **Firmware bring-up test:** signed firmware loads through PAS 9, returns expected Gen2 HFI init response and image version, survives first state transitions without SCM/IOMMU/clock failures. Record image/firmware/hash/kernel commit and logs.
5. **Decoder then browser:** `v4l2-compliance`; H.264/HEVC/VP9 test streams including VP9 3840×2160 decode to verified frames in GStreamer or a direct V4L2 harness; separately establish Chromium V4L2/DRM zero-copy and 4K output. A `/dev/video*` node alone is not acceptance.

**Current disposition:** source-level Gen2 ABI match substantially narrows the investigation, but a verified oneli firmware image and proper SM8475 Iris resource tables are required before claiming Motorola firmware compatibility or implementing an enabled decoder node.
