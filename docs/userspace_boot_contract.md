# Debian ARM64 userspace / oneli Boot integration contract

Date: 2026-10-11. Owner: userspace, coordinator repository branch razr/userspace.
Kernel baseline remains a5ebb76233b79db01e82e061173cb73c6d2b5c6b in Drzet/linux.

## Interfaces and ownership

| Contract | Userspace artifact | Native Boot / subsystem obligation |
| --- | --- | --- |
| CPU and init | Debian trixie arm64, systemd PID 1, AArch64 glibc | ARM64 kernel capable of executing /sbin/init; record resolved ABI and runtime result |
| Root filesystem | rootfs.tar.zst with numeric owners, modes, symlinks and package manifest | Select real partition, format and mounting method from actual oneli boot/partition evidence; supply root= and rootwait or validated initramfs root discovery |
| Kernel | QEMU test uses Debian linux-image-arm64; never delivered as an oneli kernel | Exact reviewed Drzet/linux SHA, built Image, resolved .config, generated kernel release and System.map |
| Modules | Debian distribution module tree is QEMU-only | From the SAME native kernel build: make modules_install INSTALL_MOD_PATH=staging, depmod against same release; package under /lib/modules/$(uname -r) of target kernel |
| Early root drivers | Debian generic initramfs-tools for QEMU | Ensure storage controller, regulator, pinctrl, clock and filesystem dependency closure exists built-in or in native initramfs. UFS support currently unproven |
| Hardware description | None included in the rootfs | Boot owns sm8475-motorola-oneli.dts, shared sm8475.dtsi and all DT schema results; select correct board/DTBO |
| Diagnostics | systemd journal and test-specific ttyAMA0 QEMU marker | Prove actual console (UART and/or USB debugging) and persistent logs; do not reuse ttyAMA0 assumption |
| Firmware | No proprietary firmware binaries committed | Separate audited source/license, filenames and hashes; respective GPU/VPU/Power/USB owners report driver requirements |
| Services | OpenSSH installed, password SSH disabled, razr login without authorized keys in exported tar; systemd-networkd DHCP matches only virtio_net for QEMU | Provision authorized user keys explicitly for device; select oneli network interface/services only after native device support |
| QEMU smoke flag | razr.smoke=1 starts one-shot test and powers down | NEVER include in phone boot arguments; testing harness only |

## Native integration stages

1. Boot publishes exact reviewed kernel SHA, oneli DTB build/schema evidence and source-supported boot image/container layout. Unknown stock boot and vendor_boot parameters, A/B slot mapping, page size, offsets and DTBO selection remain unresolved. No guessed mkbootimg invocation is accepted.
2. Unpack rootfs.tar.zst preserving ownership and permissions. Remove or replace Debian QEMU-only /boot and /lib/modules entries, then install native kernel modules and a native initramfs from identical kernel commit/config. Pin artifact hashes and firmware inventory.
3. Validate offline: ELF architecture and dynamic loader for /sbin/init; native module release, depmod -b result, lsinitramfs contents, root driver dependency closure, initramfs firmware paths and DT/schema checks. Label this build/integration-tested only.
4. Once the phone is available, first inventory the existing installed firmware/boot partitions, board revision, chosen DTB/DTBO and escape/recovery procedure without flashing. Boot owns the reversible boot trial. Confirm root mount, serial or USB diagnostic logs, uname -r, arm64 architecture, PID 1, storage identification and service status. Record actual device hardware separately from emulated findings.

## QEMU evidence boundary

The independent workflow on razr/userspace bootstraps from a signed Debian snapshot (see userspace/inputs.env), creates a Linux ext4 test disk, and starts QEMU -machine virt with its virtual DT, its PL011 serial console and the Debian distribution ARM64 kernel and initrd. It requires a systemd serial marker, successful virtio-net DHCP, authenticated ephemeral-key host-to-guest SSH command, and clean guest poweroff. Test keys and NOPASSWD shutdown permission exist only in disposable QEMU ext4 disk; the exported rootfs tar has neither.

This does not use the project kernel, oneli device tree, actual Qualcomm UFS, GPU, VPU, USB, DisplayPort, charge controller or regulators. It demonstrates no oneli boot or physical component functionality. Actual phone hardware tests remain deferred.

## Native kernel artifact contract (schema v2)

The tracked `userspace/native-kernel-inputs.example.json` is **schema_version 2**. All absent device-specific fields are intentionally null. The offline validator `scripts/validate-native-kernel-inputs.py` refuses incomplete inputs and checks:

1. Exact 40-hex `Drzet/linux` kernel commit; kernel release and matching `lib/modules/<release>` directory with `modules.dep`.
2. SHA256 hashes for Image, resolved kernel config, oneli DTB, initramfs, firmware manifest, boot packaging manifest and `modules.dep`. `modules_sha256` must exhaustively cover every provided native `.ko` (including gzip/xz/zstd compressed forms).
3. Each module must be AArch64 ELF, and its actual `modinfo -F vermagic` kernel-release token must match `kernel_release`. This is a necessary ABI check, not proof of matching symbol CRCs, compiler configuration or runtime loading.
4. `initramfs_modules` must list specific native modules needed at early boot; `lsinitramfs` and `unmkinitramfs` verify the **actual extracted module bytes, vermagic and hashes**, not merely path presence.
5. The firmware manifest must explicitly declare `schema_version: 1`, `status: complete`, nonempty `required_files` with `path`, `sha256`, `consumer`, boolean `in_initramfs`, and an empty `unknown_requirements` list. Each licensed staged file hash is checked, as is actual embedded content when designated for initramfs. An empty JSON object, a zero-file inventory or an unresolved required firmware path fails closed.
6. Boot packaging manifest must explicitly declare `status: verified`. Its actual header/DTBO and phone-specific semantics remain Boot's responsibility.

Build host requirements: Python 3, kmod (`modinfo`), `unmkinitramfs`/`lsinitramfs`, and `zstd` for compressed modules. Example command once the Boot artifacts are genuinely available:

```sh
python3 scripts/validate-native-kernel-inputs.py native-inputs.json --artifact-root staging --output native-input-evidence.json
```

Six automated synthetic fixtures include a valid AArch64 ELF module and failures for mismatched vermagic, altered Image, altered initramfs module bytes, missing embedded firmware and an unresolved firmware manifest. CI records its exact PR merge SHA and logs. This is a static consistency gate, not successful boot, module relocation/CRC validation or firmware secure-world authentication.

### Project-kernel QEMU interface stage

After the generic Debian-distribution-kernel QEMU boot/network/SSH gate passes, the coordinator may supply an exact reviewed **mainline kernel Image and matching module build**. A separate QEMU `virt` test would use **QEMU's virtual DT** and new matching initramfs; it must explicitly preserve the kernel SHA/config/Module.symvers and its artifacts. **Never** supply the oneli DT to the virt machine or label it phone emulation. No exact combined integration kernel/modules image is accepted as available until the coordinator records the selected commit and passing build.

## Unresolved handover requests for Boot

- Exact native kernel/Image/DTB/modules artifact SHA, native kernel release, and any verified initramfs/root storage driver requirements.
- Proven boot image, bootloader and DTBO parameters from pinned Motorola/public firmware evidence; distinguish the public reference from installed firmware.
- Choice of root filesystem location and recoverable test path from physical phone.
- Usable console/diagnostics path and firmware-loading location, to be determined together with USB and Power owners.

[INFERRED] A native kernel plus this Debian ARM64 userland should be able to execute a normal Linux PID 1 once device-specific boot and root-storage requirements are solved. This is an integration hypothesis, not a proven hardware result.
