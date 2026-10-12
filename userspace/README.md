# Reproducible Debian ARM64 rootfs

This userspace is independent of the Motorola stock Android boot image. Inputs live in inputs.env: Debian trixie arm64, snapshot.debian.org/archive/debian and debian-security as of 2026-10-11T00:00:00Z, 3072 MiB QEMU test disk. Debian 13 archive signing keys are downloaded from Debian FTP-master and their exact published SHA256 sums are checked (main 6f1d277429dd7ffedcc6f8688a7ad9a458859b1139ffa026d1eeaadcbffb0da7; security 844c07d242db37f283afab9d5531270a0550841e90f9f1a9c3bd599722b808b7). Signature verification remains enabled; this says nothing about the separate secure hardware boot chain.

The build script is scripts/build-userspace.sh. It performs a cross-architecture qemu-debootstrap of the signed Debian minbase, installs systemd-sysv, systemd-networkd, udev, iproute2, kmod, ca-certificates, e2fsprogs, initramfs-tools, openssh-server, sudo and linux-image-arm64, then writes a rootfs tarball and disposable ext4 disk. It records exact package versions, project SHA, host tool versions, apt and debootstrap logs, commands, kernel release and artifact SHA256 values. The Debian kernel and modules are present only to support this *generic emulator* milestone; Boot must replace them with the native project build before any physical test.

Run on Ubuntu 24.04 with sudo/root, a working binfmt_misc interpreter and network access to snapshot.debian.org:

~~~bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends debootstrap qemu-user-static binfmt-support qemu-system-arm debian-archive-keyring e2fsprogs zstd xz-utils ca-certificates gnupg wget ipxe-qemu openssh-client openssl
mkdir -p evidence
sudo env GITHUB_SHA="$(git rev-parse HEAD)" bash scripts/build-userspace.sh /tmp/razr-userspace-build "$PWD/evidence"
bash scripts/smoke-qemu.sh /tmp/razr-userspace-build "$PWD/evidence"
~~~

The requested work path must not already exist. To rerun, create a fresh path and evidence directory. The GitHub Actions job uses its own temporary path and uploads evidence including rootfs.tar.zst, the QEMU test kernel/initrd and QEMU serial log. The rootfs.ext4 image remains a local intermediate to avoid uploading a large, sparse disk. A bit-identical rebuild is **not asserted**, because upstream bootstrap tools, initramfs content, filesystem timestamps and UUIDs are not fully controlled. Signed snapshot repositories and recorded package versions make the software input set auditable.

The smoke service is gated on `razr.smoke=1`. It emits `RAZR_USERSPACE_SMOKE_PASS` **without powering off**, allowing the host to validate authenticated SSH and a DHCP route over an explicitly configured QEMU virtio NIC forwarded from 127.0.0.1:2222 to guest port 22. The host then requests systemd poweroff. A pass requires the boot marker, `RAZR_NETWORK_SSH_PASS` from a guest ARM64/systemd/networkd command, and QEMU exit 0. Independent boot and SSH stage statuses are retained.

The exported tarball preserves numeric owners and is checked by a real extraction roundtrip for `home/razr` and a non-root UID 1234/GID 1235 fixture. The generic rootfs has an SSH-capable `razr` account with password login disabled and no authorized key. CI creates a different ephemeral SSH key for every disposable ext4 test disk and injects its public key and a restricted shutdown sudoers rule **after** archiving. The private key is kept only in the Actions temporary working directory and never uploaded as an artifact. SSH host keys regenerate uniquely at boot rather than being shared in images. To use SSH on a real device, explicitly provision an authorized key and native network interface configuration after hardware confirmation. Root password remains locked. The smoke flag and CI key must never be used on the phone.

Validation boundary: QEMU -machine virt exposes a synthetic PL011 serial device, virtio storage and an emulated device tree. It does not emulate SM8475/oneli. The selected Drzet/linux baseline a5ebb76233b79db01e82e061173cb73c6d2b5c6b is **not** run by this userspace test. Firmware, real UFS boot, Qualcomm peripherals, GPU, VPU, USB, display, charging and thermal results remain untested on actual hardware.

Kernel and Boot-specific obligations are in docs/userspace_boot_contract.md.

The native Boot input JSON template is `userspace/native-kernel-inputs.example.json`. `scripts/validate-native-kernel-inputs.py` rejects absent kernel release/module/initramfs/firmware inputs. It cannot run a meaningful native integration test until Boot delivers pinned artifacts. See `docs/userspace_boot_contract.md`.

## Verified emulation and native-kernel boundary

[QEMU replay run 38180287160](https://github.com/Drzet/razr2022_nuc/actions/runs/38180287160) **passed** Debian ARM64 systemd boot, guest virtio IPv4 address, authenticated host-to-guest SSH and an orderly poweroff (QEMU exit 0). It consumed the already hashed rootfs archive from run 38177877133 rather than rebuilding it; see `tests/results/2026-10-11-userspace-qemu-replay.md`. That source run independently verified tar numeric ownership preservation. The guest's captured `eth0` was `10.0.2.15/24`, with a connected route but **no default IPv4 route**, so internet egress is not an acceptance claim.

`scripts/smoke-qemu.sh` deliberately checks network interface configuration and an authenticated remote command without relying on `systemctl is-active` in a minimal image lacking a normal system bus for unprivileged SSH sessions. It still requires the boot sentinel and guest-initiated systemd shutdown / QEMU exit 0. The replay CI downloads a pinned prior build artifact, checks `SHA256SUMS`, and injects a fresh disposable SSH public key only after extracting the deployable rootfs tar.

The expensive full rootfs workflow `.github/workflows/userspace-qemu.yml` is intentionally scoped to deliberate edits of that workflow file on `razr/userspace`, plus manual dispatch. Ordinary PR documentation updates do not cancel or restart a multi-minute build. The fast native-contract fixture workflow and artifact replay workflow run only on their own relevant branch changes or manual dispatch.

The native kernel contract is now **schema version 2**. `userspace/native-kernel-inputs.example.json` retains unresolved SHA/config/module/firmware fields as null until Boot supplies a validated build. `scripts/validate-native-kernel-inputs.py` verifies file/module hashes, real AArch64 ELF vermagic, initramfs extracted module bytes and explicitly inventoried firmware. Six synthetic positive/negative fixtures passed in [run 38179683577](https://github.com/Drzet/razr2022_nuc/actions/runs/38179683577). This does not make any Drzet/linux kernel ABI or Qualcomm firmware hardware-tested.

A later **project-kernel QEMU virt** test will use only the coordinator-selected exact mainline Image/config + matching modules and a QEMU virtual DT, never the oneli DT. The image/module set is not yet supplied by the coordinator; do not silently substitute Debian's kernel or one independent subsystem branch.

## 2026-10-12 Boot/header contract and combined-kernel preparation

Current [coordinator fourth review](https://github.com/Drzet/razr2022_nuc/blob/main/docs/NEXT_TASKS.md) accepted fresh full generic QEMU build [38180519542](https://github.com/Drzet/razr2022_nuc/actions/runs/38180519542). These tests are **Debian distribution kernel only**.

The pinned Boot v2/vendor_boot v4 header, vendor ramdisk fragment and unpadded dual-FDT metadata are summarized in `userspace/boot-reference-metadata-v2.json`, cross-checked by `scripts/audit-boot-reference-consumer.py` using immutable Boot/VPU JSON. Reference addresses `0x8000`, `0x1000000`, `0x100`, `0x1f00000` are **not** accepted mainline native load addresses. Ramdisk is legacy-LZ4, one 108-byte platform fragment with 16 zero board IDs, two 479481-byte embedded FDTs (second unaligned), and unknown fragment name/stock boot OS version. There is no active-DTBO or native-boot acceptance claim.

The **schema-v3** validator (`scripts/validate-native-kernel-inputs.py`) separates QEMU `virt` from oneli native packaging. `userspace/native-kernel-inputs.example.json` models `qemu_virt`: no oneli DTB or Boot image inputs, but exact same-build Image/config/Module.symvers, kernel release, installed modules, initramfs contents and SHA256s. `userspace/oneli-native-inputs.example.json` adds the Boot-owned manifest and native DTB. Boot's current v2 manifest is recognized only as a structural reference. Empty module/firmware requirements are permissible only for an explicit reviewed configuration with a specific written reason; unknown requirements still fail. Separate VPU firmware install convention `qcom/vpu/vpu20_4v.mbn` is [INFERRED] pending loader/user agreement and **not** a QEMU/minimal-boot dependency.

The proposed [Boot/Userspace combined-kernel handoff](../docs/userspace_combined_kernel_handoff_v1.md) defines the exact producer ZIP directory tree and immutable `manifests/combined-kernel-build-v1.json` with Image, **generated** config, Module.symvers, release, installed modules and a genuine loadable virt module. **Boot must explicitly acknowledge it**; userspace's proposal alone is not agreement. The executable `scripts/preflight-project-qemu.py --bundle-root EXTRACTED-ZIP-ROOT` checks actual build configuration, file hashes, AArch64 .ko/vermagic, release, toolchain, and no dangling module symlinks without root. Direct negative fixtures include wrong-release modules with updated hashes and missing/misconfigured components.

The prepared but **not project-kernel executed** `scripts/prepare-project-qemu.sh` takes four arguments: extracted and preflighted Boot bundle directory, a previously verified Debian ARM64 rootfs tar, that tar's SHA256, and a **nonexistent** new work directory. It reuses the same direct preflight, extracts the verified tar, installs only matching modules, creates a fresh ARM64 initramfs inside a temporary chroot, and constructs a disposable ext4 QEMU disk. Cleanup is installed **before the first mount**. It also invokes `scripts/finalize-project-qemu-manifest.py` to produce a separate post-initramfs Userspace schema v3, then validates its actual extracted module/initramfs bytes. Requires root, `qemu-user-static`/binfmt, kmod, initramfs-tools, zstd, e2fsprogs and the selected exact Boot bundle. No generic kernel is substituted for the selected project Image.

Once Boot publishes and coordinator accepts the **same-build** Image, `.config`, Module.symvers, installed modules, hashes and a selected loadable virt test module, set `RAZR_PROJECT_KERNEL_RELEASE` and `RAZR_PROJECT_QEMU_MODULE` and invoke the existing `scripts/smoke-qemu.sh` on the new work directory/evidence. In addition to systemd/SSH/IPv4/shutdown, it must authenticate a `modprobe` and prove the module appears in `/proc/modules`. A mismatched module release fails preflight or runtime. This is QEMU `virt` with its **own generated DT**, not phone emulation. Do not execute this stage against an unselected subsystem Image.

`userspace/native-early-diagnostics.example.json` and [Boot contract](../docs/userspace_boot_contract.md) describe a separate prospective native diagnostic initramfs. It keeps console, early storage/root, driver closure, firmware and bootloader parameters unresolved; no stock partitions are modified and no flash command exists.

### Fifth-review verification boundary

- Boot's new \`configs/oneli-boot-packaging-v2.json\` is pinned at \`cfdecbf41a329bcc0fa3074f8de708e95ef698b1\`; reference header values do **not** imply usable native placement. Native-only schema v3 requires \`native_header_inputs_path\` with explicit unsigned values including \`os_version_raw\`; QEMU \`virt\` prohibits this field and all oneli DT/package fields.
- Latest static checks: Boot v2 metadata audit and both the 14 native validator and 13 executable bundle/shell preflight fixtures. Read current CI outcome before treating the new fixtures as accepted. The older Debian-kernel QEMU boot remains separate and passed.
- An actual combined-project-kernel QEMU guest run is still blocked on Boot's immutable exact ZIP and accepted module selection, not on stock firmware or phone access.

