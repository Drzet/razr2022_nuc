# Userspace Boot reference bridge and artifact-schema v3 audit

Date: 2026-10-12. Owner: Userspace, project branch `razr/userspace`. Source-only validation, no phone or combined project kernel available.

## Exact coordinator decisions consumed

Coordinator main at `5261a8cb15e93d406bc58d711c224d53104c129c`; `docs/STATUS.md` blob `ba9a17056ea24cc437a9c9496540a992f6e52d97`, `docs/NEXT_TASKS.md` blob `9a9b9b1f9a06c4f1998677871b9d25bee496d5e5`, updated fourth-review VPU export `docs/FOURTH_REVIEW_VPU_UPDATE.md` blob `97e765f09931337a2a232a7d7d0036a572c099bb`. No coordinator-owned files modified.

Pinned consumer source files, separate from uploaded binary images:

- Boot `configs/oneli-boot-packaging-v1.json` at project `12fd47873ed587ab7518c3ac747c747757e8005f`, **blob SHA1** `dae3b4898f236e0ff8c86e5f01b84326c6cf40d2`.
- VPU `docs/vpu/2026-10-12-oneli-stock-fdt-properties.json` at project `1a59d79fda42a977956de8e06c3a60d44b2971f4`, **blob SHA1** `51a3ea64119a4f39de7be2197f1d706a97f5f939`. Full raw derived property archive JSON SHA256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465` from completed extraction [38220276125](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125). Public ROM source ZIP SHA256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`.

## Metadata agreement and unresolved fields

`userspace/boot-reference-metadata-v1.json` records **observed** v4 structure: 1584-byte boot header, 2128-byte vendor_boot header, page 4096; legacy-LZ4 vendor ramdisk; platform fragment type 1 / 108 bytes / sixteen zero board-ID words; base FDTs of 479481 bytes each at offsets 0 and 479481; PVT reference overlay index 3 board-ID (69,49152). VPU-extracted reference addresses: 0x8000/0x1000000/0x100/0x1f00000. They are **not approved native loading addresses**. Boot OS-version raw value, fragment name and bootconfig values are unverified. Reference PVT overlay is not the running bootloader's proven choice.

The normalized metadata is checked by `scripts/audit-boot-reference-consumer.py` against both **immutable git blob digests**, header/offset equations and fragment fields. This verifies source fidelity of the bridge and rejects accidental promotion of structural source information into native-ready/physical status. It does **not** prove an independent byte-level stock unpack/repack or applied libfdt overlay.

Boot's current v1 `schema=oneli-native-boot-packaging-contract-v1` is intentionally structural. Userspace schema v3 recognizes it and emits `structural_reference_audited=true`, `native_composition_ready=false`, `hardware_accepted=false`; it does **not** require an invented `status=verified`.

A scoped `qemu_virt` manifest has no oneli DTB or Boot packaging. An `oneli_native` manifest may reference the Boot v1 prototype for structural checking without making the image native-ready. Firmware requirements for disabled Iris/VPU are excluded from both minimal and QEMU scopes. The optional **proposed**, not validated Linux VPU install convention remains `qcom/vpu/vpu20_4v.mbn` at exact stock SHA256 `9582ea4c5565408bd3e5ba6f8fffc7881f226cae001b6fcd7a0c868de9add9af`. An explicitly reviewed zero-required-firmware configuration is representable; unknown enabled-consumer requirements still fail the validator.

## Independently inspected CI, corrected false-positive

- Earlier [run 38244458164](https://github.com/Drzet/razr2022_nuc/actions/runs/38244458164) appeared green **incorrectly**. The new negative empty-manifest fixture failed because it still expected an old error string, and a missing shell `pipefail` allowed `tee` to mask the failure. This is a recorded validation defect, not a pass. Fixed by `fde6eb0fbc2fd06ab2ec9d1ffbdd12c7bc5fe4be` and `6d3f41b7281905ff4c27ca85a61799b32e78a7b6`.
- **Accepted new [run 38244943279](https://github.com/Drzet/razr2022_nuc/actions/runs/38244943279)**, actual branch checkout `dcf72a622481e77c45809d877cfdadd55feeabd3`, job `114796372357`, conclusion **success**. Eleven of eleven Python fixtures passed with failure-propagating pipe; anchored Boot and VPU raw JSON metadata cross-audit printed `BOOT_REFERENCE_METADATA_PASS`; `bash -n` passed for the project-QEMU preparation and shared smoke scripts. Artifact ID `11744775728`, artifact ZIP digest reported `sha256:3b01171695f1f01846ceb76f6d782fdb92078b76a756ef765115d6ba7a84cd02`. The test source includes intentionally synthesized AArch64 module and firmware fixtures, not project binary output.
- Fresh full [run 38180519542](https://github.com/Drzet/razr2022_nuc/actions/runs/38180519542) (source `e14f618fc1c55b3581e3bf082c1d12bbb0b05e03`) already passed signed-snapshot Debian arm64 rootfs, numeric archive UID/GID, generic QEMU systemd, configured IPv4, authenticated SSH and orderly poweroff. No re-run is needed because these new edits affect future artifact contracts rather than that tested Debian kernel.

## Held project-kernel and native early diagnostic stages

`scripts/prepare-project-qemu.sh` stages a selected **combined** Image/config/Module.symvers/installed modules into a verified Debian rootfs, checks AArch64 ELF/vermagic and exact hashes, generates a matching new initramfs and disposable QEMU disk, and adds test-only SSH/modprobe credentials. `scripts/smoke-qemu.sh` now has an optional **required** project-kernel mode that checks `uname -r` and actual in-guest modprobe/`/proc/modules` in addition to systemd, configured IPv4, authenticated SSH and QEMU poweroff. Neither script has yet executed its **project-kernel path**: only syntax checked. No combined kernel artifacts were published/accepted at this review.

Exact required coordinator inputs: source commit, generated kernel release/config, Image, `Module.symvers`, fully installed matching module tree and `modules.dep`, module hashes/ABI build provenance, a known QEMU-loadable module and explicit virt-capable kernel configuration, artifact IDs and SHA256. QEMU will use its own generated DT, not oneli DT. Source-stage prep and actual modprobe remain deferred until those artifacts exist; a deliberately wrong-release module is rejected in source preflight/validator fixtures, but no real combined guest module load has occurred.

`userspace/native-early-diagnostics.example.json` separately describes native early initramfs design inputs with unresolved console, storage, clock/regulator dependencies, static AArch64 recovery binary and bootloader/AVB acceptance. No oneli `root=`, `console=`, UART path, bootconfig or flash recipe was invented.

**Validation categories:** stock metadata researched + pinned; userspace source implemented; synthetic validator/metadata CI tested; Debian-distro QEMU tested; **combined-project-kernel-QEMU not tested**; **physical Motorola hardware not tested**.
