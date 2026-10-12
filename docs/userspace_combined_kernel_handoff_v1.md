# Combined ARM64 build → Userspace QEMU virt handoff, wire contract v1

Proposed by Userspace 2026-10-12 for Boot owner review; linked to fifth coordinator assignments. **A proposal is not mutual acknowledgement until Boot explicitly accepts it.** This is separate from Boot's phone-specific `oneli-native-boot-packaging-contract-v2` and from Userspace's *post-initramfs* `native-kernel-inputs` schema v3.

## What Boot publishes

One immutable ZIP artifact named `oneli-combined-kernel-v1-<run_id>.zip` containing the following tree at archive root (paths case-sensitive):

```text
boot/Image
boot/kernel.config
boot/Module.symvers
boot/kernel.release
boot/oneli.dtb
lib/modules/<EXACT_KERNEL_RELEASE>/modules.dep
lib/modules/<EXACT_KERNEL_RELEASE>/**  # installed matching .ko[.gz|.xz|.zst] plus modules.* metadata
manifests/combined-kernel-build-v1.json
```

No absolute paths, `..`, unsafe tar links or symlinks pointing to build/source trees; packaged modules must include `modules.dep`, `modules.builtin`, `modules.order` when generated. A module tree cannot be replaced with `Module.symvers` alone. Kernel `Image` is uncompressed ARM64 `arch/arm64/boot/Image`; `kernel.config` is the **generated `.config` actually used** for this build, not defconfig or fragments. `Module.symvers` and every installed module are from that same kernel build and release. `boot/oneli.dtb` exists as Boot schema evidence, **never passed to QEMU**.

Boot records ZIP SHA256, artifact ID and run URL in its handoff. The in-ZIP manifest `manifests/combined-kernel-build-v1.json` has these exact required keys (unknown numeric/hash fields must be filled from build, not guessed):

```json
{
  "schema": "oneli-combined-kernel-build-v1",
  "repository": "https://github.com/Drzet/linux",
  "kernel_commit": "<full-40hex-combined-commit>",
  "kernel_release": "<exact-make-kernelrelease>",
  "build_id": "<stable-CI-run-and-attempt-ID>",
  "files": {
    "image": "boot/Image",
    "config": "boot/kernel.config",
    "module_symvers": "boot/Module.symvers",
    "kernel_release": "boot/kernel.release",
    "oneli_dtb": "boot/oneli.dtb",
    "modules_directory": "lib/modules/<exact-release>"
  },
  "sha256": {
    "image": "<sha256>",
    "config": "<sha256>",
    "module_symvers": "<sha256>",
    "kernel_release": "<sha256>",
    "oneli_dtb": "<sha256>",
    "modules_dep": "<sha256>"
  },
  "modules_sha256": {
    "kernel/drivers/net/dummy.ko": "<sha256>"
  },
  "qemu_runtime_module": {
    "name": "dummy",
    "relative_path": "kernel/drivers/net/dummy.ko"
  },
  "qemu_virt_config": {
    "machine": "virt",
    "console": "ttyAMA0",
    "virtio_transport": "mmio",
    "root_disk": "virtio-blk",
    "network": "virtio-net",
    "root_fs": "ext4",
    "required_builtin": [
      "CONFIG_ARM64",
      "CONFIG_SERIAL_AMBA_PL011",
      "CONFIG_SERIAL_AMBA_PL011_CONSOLE",
      "CONFIG_ARM_GIC",
      "CONFIG_VIRTIO_MMIO",
      "CONFIG_VIRTIO_BLK",
      "CONFIG_VIRTIO_NET",
      "CONFIG_EXT4_FS",
      "CONFIG_DEVTMPFS",
      "CONFIG_DEVTMPFS_MOUNT",
      "CONFIG_BLK_DEV_INITRD",
      "CONFIG_RD_GZIP",
      "CONFIG_INET",
      "CONFIG_UNIX",
      "CONFIG_PACKET",
      "CONFIG_TMPFS",
      "CONFIG_BINFMT_ELF"
    ],
    "required_loadable": ["CONFIG_DUMMY"],
    "required_enabled": ["CONFIG_MODULES"]
  },
  "toolchain": {
    "compiler": "<exact-compiler-version-and-target>",
    "linker": "<exact-linker-version>",
    "build_command": "<reproducible-command>"
  },
  "commits": [
    {"original": "<selected-original-sha>", "applied": "<candidate-result-sha>"}
  ],
  "evidence": {
    "modpost_completed": true,
    "oneli_dtb_compiled": true,
    "phone_tested": false
  }
}
```

The example module filename is a **recommended** deterministic config choice, not evidence a module already exists. If Boot chooses another harmless module, report its exact `name`, installed relative path, and config symbol instead. `modules_sha256` covers **every installed .ko and compressed .ko** with exact paths under the release directory; `modules.dep` itself has a separate hash. The manifest may include additional fields, but cannot omit the above.

## Configuration agreement (directly tied to existing smoke command)

Userspace's actual QEMU command is `qemu-system-aarch64 -machine virt -cpu cortex-a57 -m 2048 -smp 2 -nographic -serial stdio -kernel boot/Image -initrd <new-initrd> -append 'console=ttyAMA0,115200 root=/dev/vda rw rootwait systemd.unit=multi-user.target razr.smoke=1' -drive if=none,... -device virtio-blk-device -netdev user,... -device virtio-net-device`. QEMU generates its own virt DT. The built-in symbols named in `required_builtin` are explicit **`=y`** requirements; `required_enabled` must be `=y`; `CONFIG_DUMMY=m` ensures guest `modprobe dummy` and an entry in `/proc/modules`. Add any prerequisite to get those requested `=y` values; do not silently downgrade core early-boot drivers to modules. For actual accepted Images, Userspace validates values from the generated config and Boot reports any Kconfig-unavailable symbol/change before the build.

No oneli DTB, Qualcomm firmware, Android stock ramdisk/bootconfig, AVB/bootloader packaging or phone-specific load addresses are required for this QEMU `virt` run. Disable GPU/VPU/USB/DP/charging consumers in the oneli candidate as coordinator directed. The `oneli.dtb` is an independent build/schema deliverable.

## Userspace completion after Boot publishes

1. Download the **exact** ZIP by artifact ID; verify ZIP digest from the Boot handoff and extract safely. Check all manifest SHA256s and artifact paths and the real generated kernel config. Reject a mismatched release or `modinfo vermagic`, including a negative deliberately mislabeled module.
2. Unpack previously verified Debian ARM64 rootfs tar preserving numeric ownership. Remove distribution modules, copy *only* bundled matching modules, regenerate depmod and a fresh initramfs for the new kernel using Debian ARM64 initramfs-tools. Archive generated initramfs/rootfs/SSH credential-free provenance with hashes. The package is not phone-installable.
3. Complete the QEMU-specific schema-v3 manifest with actual *new* initramfs SHA256, a firmware-v2 record describing explicitly justified zero firmware requirements for selected virt config, and same-build hashes. `qemu_virt` profile forbids oneli DT and Boot phone-packaging manifest; no boot v2 file is required in QEMU staging.
4. Run the selected Image on QEMU virt and require exact `uname -r`, **real** `modprobe` + `/proc/modules` match, systemd PID1, configured IPv4, authenticated SSH and clean shutdown. Retain command, logs, run IDs and all hashes; no external-network claim unless independently tested.

**Separate Boot phone-packaging contract**: `configs/oneli-boot-packaging-v2.json`, project revision `cfdecbf41a329bcc0fa3074f8de708e95ef698b1`. It is only structural/reference stage, `native_ready=false`, `hardware_accepted=false`. Required explicit native header-input fields (`os_version_raw`, `kernel_addr`, `ramdisk_addr`, `tags_addr`, `dtb_addr`, `purpose`, `phone_boot_validated`) may not be null in a *composition attempt*; copied stock values are not approved phone placements. Userspace does not need native packaging in QEMU.

## Handshake

Boot: accept or propose **specific** changes to archive tree, manifest keys, Kconfig symbols and chosen loadable module on [Boot PR #12](https://github.com/Drzet/razr2022_nuc/pull/12). Once agreed, Boot can build while Userspace completes direct preflight/staging tests. Coordinator reviews/promotes the candidate independently. Do not claim agreement solely because this proposal was published.
