# Boot ↔ Userspace combined QEMU artifact contract v1

Agreed interface proposal by Boot for fifth-round execution, 2026-10-12. Canonical Userspace consumer: `razr/userspace` scripts `preflight-project-qemu.py`, `finalize-project-qemu-manifest.py`, `prepare-project-qemu.sh`, `validate-native-kernel-inputs.py`; manifest schema **3**. Userspace must explicitly acknowledge any change before Boot changes output format. This document defines the Boot producer's commitment, not an assertion that the bundle exists.

## Build target and configuration

One ARM64 kernel `Image` from isolated `Drzet/linux:razr/integration-candidate`, reviewed source sequence Boot `525b504b82dbca593a9a697af9be63f53915e0a3` + GPU `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`, `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3` + exact isolated Power series ending `564f2c7df60316db86e36d7267ddadf07bc32b7e`. Exact replay SHAs and any conflicts recorded by build. Optional UBWC omitted for first candidate. Keep USB/DP/GPU/VPU/charging board consumers disabled. The **same** Image must have a virt-capable configuration for `qemu-system-aarch64 -machine virt` using **QEMU-generated DT**, and separately compile `qcom/sm8475-motorola-oneli.dtb` for offline oneli checks.

Configuration must include ARM64, modules and modversions as appropriate, devtmpfs, tmpfs, proc/sysfs, ELF binfmt, PCI host + virtio PCI, virtio block/network/console and corresponding transports, ext4, initrd/initramfs support, serial PL011 for QEMU, interrupt controller GIC, PSCI, networking IPv4, Unix sockets, tun? only if QEMU command requires it. For deterministic boot, built-in drivers needed before root mount (GIC/PSCI/virtio transport, block/ext4, devtmpfs, serial) must be `=y`; `=m` is acceptable for a driver only if Userspace can prove the matching initramfs includes and loads it. Include one harmless `=m` test module that `modprobe` loads without hardware and appears in `/proc/modules` (candidate `CONFIG_CRYPTO_USER_API_HASH=m`/module `algif_hash`, final exact module to be confirmed from generated config and `modules.dep`). Boot must not assume a module name without verifying actual .ko. No Motorola `root=`/`console=` is injected into QEMU.

## Producer bundle (one immutable build ID and SHA)

Boot publishes a portable directory/archive, not just logs:

- `Image`, `sm8475-motorola-oneli.dtb`, `config` (generated `.config` explicitly copied as visible `config`), `kernel.release`, `Module.symvers`, `modules/` containing the **entire installed matching** `lib/modules/<release>` tree with `modules.dep`, plus complete per-file SHA256 inventory. Strip dangling `build` and `source` symlinks from portable modules.
- `build-manifest.json` with source repo, immutable integration SHA, exact ordered original/resulting replay SHAs, generated kernel release, build ID, config/Image/DTB/Module.symvers SHA256, installed module tree and module SHA256s, selected runtime test module name and relative path, toolchain and exact build/install/depmod commands, source workflow/job/artifact IDs and zip SHA256.
- `firmware-manifest.json` scoped `target_environment=qemu_virt`, schema v2, `assessment=complete`, `required_files=[]`, `unknown_requirements=[]`, and a substantive reason why no Qualcomm firmware is required for this **QEMU virt** guest.
- `native-inputs-v3.json` pre-initramfs producer stub for `qemu_virt`, schema v3, absolute prohibition of oneli DTB/phone packaging in that profile (`dtb_path=null`, `boot_packaging_manifest_path=null`, `native_header_inputs_path=null`). `initramfs_path` and its hash are unresolved until Userspace constructs the new matching initramfs. The Userspace finalizer produces the complete schema-v3 validated manifest and preserves the same build identity.

All paths inside manifests are relative to an explicit bundle root. Every file hash is SHA256; build ID and kernel release must agree across Image, config, Module.symvers and installed modules. Kernel module ELF architecture AArch64 and vermagic must match. Never claim that `Module.symvers` equality alone proves symbol CRC compatibility.

## Consumers and gates

Userspace first runs its executable nonroot `preflight-project-qemu.py --bundle-root BUNDLE`, rejects incomplete/missing hashes, missing module or release mismatch and stale build identity. It then stages the already verified Debian ARM64 rootfs and matching initramfs with `prepare-project-qemu.sh`; mount cleanup must be registered before first mount. Only after final schema-v3 validation does it run QEMU and assert actual `uname -r`, `modprobe` and `/proc/modules`, systemd, IPv4, SSH and clean shutdown. The distro-kernel QEMU pass does not count.

The Boot v2 `configs/oneli-boot-packaging-v2.json` is **separate native/reference structural evidence**, not a QEMU dependency. Userspace may pin it in a separate `oneli_native` metadata bridge with explicit OS version and vendor load addresses, retaining `native_ready=false` and `hardware_accepted=false`. QEMU virt must never consume the oneli DTB, Android boot header values, proprietary firmware or board-specific device enablements.

## Producer acceptance

Boot reports success only after one real full ARM64 Image + ordinary MODPOST modules build, installed modules tree, oneli DTB + applicable schema/FDT check and actual downloadable artifact set with SHA256 and exact commit. CI workflow creation or passing syntax checks alone is not completion. Coordinator accepts/promotes the candidate separately.
