# Userspace ↔ Boot interface: QEMU virt versus native oneli

Owner: Userspace (`razr/userspace`). Revised 2026-10-12 following coordinator fourth review. The native upstream baseline remains `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` in `Drzet/linux`. Boot alone owns shared device trees, native boot composition and board selection.

## Evidence and readiness are separate

| Gate | What a PASS establishes | What it does **not** establish |
| --- | --- | --- |
| File consistency | Expected SHA256s, actual AArch64 ELF/vermagic, same-build manifest and installed module inventory, firmware and actual extracted initramfs file hashes | Symbol CRC compatibility, module runtime load, correct DT/bootloader |
| Reference structural format | Source-hashed Motorola boot v4/vendor_boot v4 header fields, offsets, ramdisk descriptor and FDT container evidence | An independently checked native repack, native load addresses or active DTBO selection |
| Native composition readiness | **Only when Boot independently establishes** selected DTB/overlay, explicit header OS/version and placement inputs, accepted ramdisk/bootconfig composition, independent roundtrip and bootloader/AVB strategy | That the handset has accepted it |
| Hardware acceptance | Actual reversible device boot and logs against a specific artifact | Transferability of a public stock reference to other variants |

The existing [Boot-owned v1 manifest](https://github.com/Drzet/razr2022_nuc/blob/12fd47873ed587ab7518c3ac747c747757e8005f/configs/oneli-boot-packaging-v1.json) has schema `oneli-native-boot-packaging-contract-v1`, **not** a generic `status: verified` field. It is a structural prototype with `flash_recipe=false`, `candidate_signed=false`, `boot_tested=false`. Our validator accepts this as a **reference-format audit only**, returning `native_composition_ready=false` and `hardware_accepted=false`. It does not change Boot's manifest or claim an image can be flashed. A future Boot v2 native-readiness interface must be separately agreed before any acceptance beyond that state.

## Consumed stock metadata: precisely bounded

Immutable sources: Boot v1 project SHA `12fd47873ed587ab7518c3ac747c747757e8005f`, VPU six-FDT summary project SHA `1a59d79fda42a977956de8e06c3a60d44b2971f4`, full extracted property JSON SHA256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`; reference Motorola Android 14 ZIP SHA256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`.

The consolidated, machine-readable, nonbinary consumer is [`userspace/boot-reference-metadata-v1.json`](../userspace/boot-reference-metadata-v1.json). The [audit script](../scripts/audit-boot-reference-consumer.py) checks its fields against both immutable original JSON sources using their Git blob IDs and cross-source values. This is independent *metadata comparison*, not independent binary `vendor_boot` parsing or libfdt overlay application.

| Source reference | Extracted value | Native disposition |
| --- | --- | --- |
| `boot.img` | v4, 1584-byte header, 4096-byte section alignment | Boot OS-version raw field remains **null**, kernel/cmdline/AVB not automatically inherited |
| `vendor_boot.img` | v4, 2128-byte header, 4096-byte page | Verified reference *format* only |
| Loading addresses | kernel `0x8000`, ramdisk `0x1000000`, tags `0x100`, DTB `0x1f00000` | **Reference addresses only**. Explicit Boot native placement approval required |
| Vendor ramdisk | offset 4096, size 13,335,589, legacy LZ4 magic `02214c18` | Do not copy Android vendor ramdisk into Linux unexamined |
| Fragment table | one entry of 108 bytes, type 1 platform, 16 board-ID words all zero | Fragment name not yet extracted; zero board IDs do not identify selected overlay |
| Embedded base FDT region | offset 13,340,672, total 958,962 bytes | Two separate FDTs, each 479,481 bytes, at offsets **0 and 479481** (not four-byte aligned) for MSM 530/540 |
| Bootconfig | offset 14,307,328, size 85 | Three *keys* observed; their actual values are not accepted native arguments |
| DTBO | four reference overlays; index 3 has `0x45/0xc000` | PVT **candidate** agrees with observed hwrev, but bootloader-selected overlay remains unproven |

The source-hashed extraction establishes image-container structure, not real oneli filesystem/root partition/console placement. No native bootloader parameters are generated from the values above. Boot must resolve v4 copy-through header fields explicitly, AOSP independent packer/roundtrip and effective DT selection. QEMU never consumes these stock DTs or addresses.

## Firmware profiles

For selected `qemu_virt`, no Qualcomm VPU/GPU firmware or oneli boot packaging is required. For `oneli_native` minimal early console, unresolved VPU and GPU consumers remain disabled; do not add their proprietary firmware to the boot-critical requirement list. A schema v3 **scoped zero-requirement** firmware manifest must explicitly identify the selected target and a substantive reason with `unknown_requirements=[]`. This means no firmware is needed by that *reviewed configuration*, not that all future firmware questions are answered. An unknown enabled consumer must fail closed.

The public stock radio filesystem has `image/vpu20_4v.mbn`, SHA256 `9582ea4c5565408bd3e5ba6f8fffc7881f226cae001b6fcd7a0c868de9add9af`; VPU proposes `qcom/vpu/vpu20_4v.mbn` as a possible Linux install path. **This is a future, disabled VPU-enabled profile**, pending accepted loader convention, dependencies, provenance and runtime PAS/HFI testing. See `vpu_firmware_install` in the userspace metadata bridge. It is not a QEMU or minimal-initramfs dependency, and no firmware bytes are committed.

## Native artifact schema v3 and exact build provenance

`scripts/validate-native-kernel-inputs.py` consumes `schema_version:3`. There are two disjoint targets:

- `qemu_virt`: **must** have `dtb_path=null`, `boot_packaging_manifest_path=null`. QEMU generates its own virtual DT. It consumes an actual coordinator-selected Image, generated config, `Module.symvers`, matching installed modules and fresh initramfs, all source SHA-pinned.
- `oneli_native`: additionally requires a source-hashed Boot manifest and oneli DTB. Boot v1 can pass **structural-reference** checks but cannot be promoted to native-readiness/hardware acceptance. No inferred partition, UART, AVB or root arguments are accepted.

Fields common to both: immutable 40-hex `kernel_commit`, exact `kernel_release`, a nontrivial `same_build.build_id` tying Image/config/Module.symvers digests, `sha256` for all staged files and `modules.dep`, an exhaustive `modules_sha256` list, verifiable AArch64 ELF `modinfo vermagic`, and `initramfs_modules` with actual extracted module/hash equality. Zero required initramfs modules are allowed only with an explicit reviewed reason; a truly empty module tree requires `CONFIG_MODULES=n`. Firmware manifest v2 requires an exact matching target, `assessment=complete`, declared `required_files`, and `unknown_requirements=[]`; a zero-length list requires a specific justification. Config/build provenance is checked for consistency, but neither that nor vermagic substitutes for a real module load or symbol CRC test.

Templates: [QEMU](../userspace/native-kernel-inputs.example.json), [oneli](../userspace/oneli-native-inputs.example.json). Their unresolved inputs remain `null` until the coordinator/Boot supplies exact binaries and source-backed metadata. Never fill fields with plausible guesses merely to get a green validator.

## Two deliberately separate execution stages

**Generic Debian distribution kernel**: complete. [Run 38180519542](https://github.com/Drzet/razr2022_nuc/actions/runs/38180519542) built Debian ARM64, checked tar UID/GID roundtrip, booted a Debian distribution ARM64 kernel in QEMU virt, authenticated SSH over configured IPv4, and shut down with QEMU exit zero. This neither exercises Drzet/linux nor establishes external internet connectivity or any physical Motorola feature.

**Selected combined project kernel**: **held until immutable coordinator artifacts**. `scripts/prepare-project-qemu.sh` is a source-stage consumer, not a tested build or run. It checks the selected Image/config/Module.symvers, module tree, exact module hashes and kernel provenance; extracts the verified Debian tar, replaces distribution modules, generates a fresh initramfs for the selected release and injects a **temporary** CI-only SSH key and authorized module-load command into the disposable disk. The existing smoke script can require `RAZR_PROJECT_KERNEL_RELEASE` and `RAZR_PROJECT_QEMU_MODULE`, prove the actual `uname -r`, run in-guest `modprobe`, verify `/proc/modules`, then SSH/IPv4/systemd/shutdown. A deliberate wrong-release module must fail. Artifact generation, complete symbol compatibility and runtime module loading are **not claimed as done** without that selected build and a completed run. The QEMU device tree is always QEMU's own.

The coordinator must provide a **single** selected exact combined kernel SHA, Image, generated config, Module.symvers, installed module inventory with hashes, release, build commands/toolchain, a suitable loadable QEMU module and an explicit virt-capable config. Independent Boot/GPU/Power branch builds cannot be mixed.

## Separate native early-initramfs diagnostic design

[`userspace/native-early-diagnostics.example.json`](../userspace/native-early-diagnostics.example.json) lists **unresolved** inputs for a future minimal native initramfs: Boot-approved Image/DT, kernel release, proven console selection, early storage/clock/regulator/pinctrl closure, matching modules, explicit firmware requirements and a pinned static AArch64 BusyBox or equivalent recovery binary. The prospective `/init` would mount proc/sys/devtmpfs, report the current kernel/DT/probe logs to a **verified** console and stop without mounting or modifying Android partitions. An optional root-mount trial must be a separate, evidence-supported explicit stage. Do not invent `root=/dev/...`, `console=...`, `earlycon`, bootconfig, flash command or a firmware requirement before Boot supplies it. The phone remains locked in the last observed session; there is no authorized flash/boot test in this contract.

## Ownership and next gate

Boot owns native composition and v4 image parameters. VPU owns provenance and candidate firmware convention; GPU/USB/Power own their respective driver/firmware/rail requirements. Userspace owns Debian rootfs, firmware-dependency declaration, new matching initramfs and both QEMU consumers. Coordinator owns combined integration and immutable artifact publishing. Native device tests require separate physical access/bootloader authorization and must be recorded independently.

The next Userspace execution gate is **one exact combined-artifact QEMU virt** build and test once the coordinator publishes it. Until then, maintain source/fixture validation only and leave project-kernel runtime, oneli boot and phone peripheral testing explicitly deferred.
