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
