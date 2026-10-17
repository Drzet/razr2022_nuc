#!/usr/bin/env bash
# Debian ARM64 signed snapshot rootfs. Never treats QEMU as oneli hardware.
set -Eeuo pipefail
if [[ $EUID -ne 0 ]]; then echo "Run as root" >&2; exit 2; fi
project=$(pwd -P)
source "$project/userspace/inputs.env"
[[ "$DEBIAN_SUITE" == trixie && "$DEBIAN_ARCH" == arm64 ]]
[[ "$DEBIAN_SNAPSHOT" =~ ^[0-9]{8}T[0-9]{6}Z$ ]]
work=$(realpath -m "$1")
evidence=$(realpath -m "$2")
[[ ! -e "$work" ]] || { echo "Refusing existing work directory" >&2; exit 2; }
[[ "$work" != "$project" && "$work" != "$evidence" ]]
mkdir -p "$work" "$evidence"
root="$work/rootfs"
mkdir -p "$root"
finish() {
  rc=$?
  trap - EXIT
  umount "$root/dev" 2>/dev/null || true
  umount "$root/sys" 2>/dev/null || true
  umount "$root/proc" 2>/dev/null || true
  echo "$rc" > "$evidence/build-exit-code.txt"
  exit "$rc"
}
trap finish EXIT
mirror="https://snapshot.debian.org/archive/debian/$DEBIAN_SNAPSHOT/"
security="https://snapshot.debian.org/archive/debian-security/$DEBIAN_SNAPSHOT/"
cp userspace/inputs.env "$evidence/inputs.env"
cp scripts/build-userspace.sh "$evidence/build-userspace.sh"
cp scripts/smoke-qemu.sh "$evidence/smoke-qemu.sh"
cp scripts/verify-rootfs-ownership.sh "$evidence/verify-rootfs-ownership.sh"
# Ubuntu 24.04 keyring predates Debian 13 keys. Verify pinned Debian FTP-master keys.
wget -q -O "$work/archive-key-13.asc" https://ftp-master.debian.org/keys/archive-key-13.asc
wget -q -O "$work/archive-key-13-security.asc" https://ftp-master.debian.org/keys/archive-key-13-security.asc
printf '6f1d277429dd7ffedcc6f8688a7ad9a458859b1139ffa026d1eeaadcbffb0da7  %s\n' "$work/archive-key-13.asc" | sha256sum -c - | tee "$evidence/key-verification.txt"
printf '844c07d242db37f283afab9d5531270a0550841e90f9f1a9c3bd599722b808b7  %s\n' "$work/archive-key-13-security.asc" | sha256sum -c - | tee -a "$evidence/key-verification.txt"
gpg --batch --yes --dearmor -o "$work/debian-main.gpg" "$work/archive-key-13.asc"
gpg --batch --yes --dearmor -o "$work/debian-security.gpg" "$work/archive-key-13-security.asc"
cat "$work/debian-main.gpg" "$work/debian-security.gpg" > "$work/debian-trixie-archive.gpg"
sha256sum "$work/archive-key-13.asc" "$work/archive-key-13-security.asc" "$work/debian-trixie-archive.gpg" > "$evidence/key-sha256.txt"
{
 echo "project_commit=$GITHUB_SHA"
 echo "suite=$DEBIAN_SUITE architecture=$DEBIAN_ARCH snapshot=$DEBIAN_SNAPSHOT"
 echo "main_mirror=$mirror security_mirror=$security"
 date -u +%FT%TZ
 uname -a
 cat /etc/os-release
 debootstrap --version
 qemu-aarch64-static --version
 qemu-system-aarch64 --version
 dpkg-query -W -f='host_package=${Package}\t${Version}\n' debootstrap qemu-user-static qemu-system-arm debian-archive-keyring e2fsprogs zstd
} > "$evidence/environment.txt" 2>&1
echo "qemu-debootstrap --arch=arm64 --variant=minbase --keyring="$work/debian-trixie-archive.gpg" trixie ROOTFS $mirror" > "$evidence/commands.txt"
qemu-debootstrap --arch=arm64 --variant=minbase --keyring="$work/debian-trixie-archive.gpg" trixie "$root" "$mirror" 2>&1 | tee "$evidence/debootstrap.log"
mkdir -p "$root/etc/apt/keyrings"
cp "$work/debian-trixie-archive.gpg" "$root/etc/apt/keyrings/razr-debian-trixie.gpg"
cat > "$root/etc/apt/sources.list" <<APT
deb [check-valid-until=no signed-by=/etc/apt/keyrings/razr-debian-trixie.gpg] $mirror trixie main
deb [check-valid-until=no signed-by=/etc/apt/keyrings/razr-debian-trixie.gpg] $security trixie-security main
APT
printf 'Acquire::Check-Valid-Until "false";\n' > "$root/etc/apt/apt.conf.d/90-razr-snapshot"
echo razr-debian > "$root/etc/hostname"
printf '127.0.0.1 localhost\n127.0.1.1 razr-debian\n::1 localhost ip6-localhost ip6-loopback\n' > "$root/etc/hosts"
: > "$root/etc/machine-id"
printf '# Root device supplied by bootargs/initramfs; not an oneli partition guess.\n' > "$root/etc/fstab"
mkdir -p "$root/usr/sbin" "$root/proc" "$root/sys" "$root/dev"
printf '#!/bin/sh\nexit 101\n' > "$root/usr/sbin/policy-rc.d"
chmod 0755 "$root/usr/sbin/policy-rc.d"
mount -t proc proc "$root/proc"
mount -t sysfs sysfs "$root/sys"
mount --bind /dev "$root/dev"
echo "chroot ROOTFS apt-get update; apt-get install systemd-sysv udev iproute2 kmod ca-certificates e2fsprogs initramfs-tools linux-image-arm64 openssh-server sudo" >> "$evidence/commands.txt"
chroot "$root" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get update 2>&1 | tee "$evidence/apt-update.log"
chroot "$root" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends systemd-sysv udev iproute2 kmod ca-certificates e2fsprogs initramfs-tools linux-image-arm64 openssh-server sudo 2>&1 | tee "$evidence/apt-install.log"
chroot "$root" /usr/bin/dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n' > "$evidence/packages.tsv"
[[ "$(chroot "$root" dpkg --print-architecture)" == arm64 ]]
chroot "$root" passwd -l root > "$evidence/root-lock.log" 2>&1
# Account is provisionable in the generic tar, but receives no authorized key there.
chroot "$root" useradd -m -s /bin/bash -U razr
chroot "$root" usermod -p "$(openssl passwd -6 "$(openssl rand -hex 32)")" razr
mkdir -p "$root/etc/ssh/sshd_config.d" "$root/etc/systemd/network"
cat > "$root/etc/ssh/sshd_config.d/90-razr.conf" <<'SSHD'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
AllowUsers razr
SSHD
cat > "$root/etc/systemd/network/80-razr-qemu.network" <<'NET'
[Match]
Driver=virtio_net
[Network]
DHCP=ipv4
NET
systemctl --root="$root" enable systemd-networkd.service ssh.service > "$evidence/services-enable.log" 2>&1
# Host SSH keys are unique per boot, never distributed in the rootfs.
rm -f "$root"/etc/ssh/ssh_host_*
cat > "$root/etc/systemd/system/razr-ssh-hostkeys.service" <<'KEYS'
[Unit]
Description=Generate unique SSH host keys
Before=ssh.service
ConditionPathExists=!/etc/ssh/ssh_host_ed25519_key
[Service]
Type=oneshot
ExecStart=/usr/bin/ssh-keygen -A
[Install]
WantedBy=multi-user.target
KEYS
systemctl --root="$root" enable razr-ssh-hostkeys.service >> "$evidence/services-enable.log" 2>&1
mkdir -p "$root/usr/local/share"
printf 'UID/GID preservation fixture\n' > "$root/usr/local/share/razr-ownership-fixture"
chown 1234:1235 "$root/usr/local/share/razr-ownership-fixture"
mkdir -p "$root/usr/local/libexec" "$root/etc/systemd/system/multi-user.target.wants"
cat > "$root/usr/local/libexec/razr-userspace-smoke" <<'SMOKE'
#!/bin/sh
set -eu
test "$(uname -m)" = aarch64
test "$(dpkg --print-architecture)" = arm64
test -d /run/systemd/system
grep -Eq '(^| )razr.smoke=1( |$)' /proc/cmdline
printf 'RAZR_USERSPACE_SMOKE_PASS arch=arm64 init=systemd\n' > /dev/console
# Host must complete network and SSH acceptance before shutdown.
SMOKE
chmod 0755 "$root/usr/local/libexec/razr-userspace-smoke"
cat > "$root/etc/systemd/system/razr-userspace-smoke.service" <<'UNIT'
[Unit]
Description=QEMU-only ARM64 userspace smoke verification
ConditionKernelCommandLine=razr.smoke=1
After=local-fs.target systemd-udevd.service systemd-networkd.service
[Service]
Type=oneshot
ExecStart=/usr/local/libexec/razr-userspace-smoke
TimeoutStartSec=30
[Install]
WantedBy=multi-user.target
UNIT
ln -s ../razr-userspace-smoke.service "$root/etc/systemd/system/multi-user.target.wants/razr-userspace-smoke.service"
mapfile -t kernels < <(find "$root/boot" -maxdepth 1 -type f -name 'vmlinuz-*' -printf '%f\n' | sort)
[[ ${#kernels[@]} -eq 1 ]] || { echo "Expected one generic Debian kernel" >&2; exit 1; }
kernel_release="${kernels[0]#vmlinuz-}"
[[ -s "$root/boot/initrd.img-$kernel_release" ]]
echo "$kernel_release" > "$evidence/qemu-kernel-release.txt"
cp "$root/boot/vmlinuz-$kernel_release" "$work/vmlinuz"
cp "$root/boot/initrd.img-$kernel_release" "$work/initrd.img"
cp "$work/vmlinuz" "$evidence/qemu-vmlinuz"
cp "$work/initrd.img" "$evidence/qemu-initrd.img"
chroot "$root" apt-get clean
rm -f "$root/usr/sbin/policy-rc.d" "$root/usr/bin/qemu-aarch64-static" "$root/var/log/bootstrap.log" "$root/var/lib/dbus/machine-id" "$root/etc/resolv.conf"
rm -f "$root"/etc/ssh/ssh_host_*
: > "$root/etc/machine-id"
umount "$root/dev"
umount "$root/sys"
umount "$root/proc"
echo 'tar sorted rootfs -> rootfs.tar.zst; mkfs.ext4 -d rootfs -> rootfs.ext4' >> "$evidence/commands.txt"
tar --sort=name --numeric-owner --mtime="@$SOURCE_DATE_EPOCH" --pax-option=delete=atime,delete=ctime -C "$root" -cf - . | zstd -T0 -12 -o "$evidence/rootfs.tar.zst"
bash scripts/verify-rootfs-ownership.sh "$root" "$evidence/rootfs.tar.zst" "$evidence"
# Ephemeral CI SSH credential lives in the disposable QEMU disk only, NOT the tar.
ssh-keygen -q -t ed25519 -N '' -f "$work/ssh_id_ed25519"
ssh-keygen -lf "$work/ssh_id_ed25519.pub" > "$evidence/ssh-ci-public-fingerprint.txt"
install -d -m 0700 "$root/home/razr/.ssh"
install -m 0600 "$work/ssh_id_ed25519.pub" "$root/home/razr/.ssh/authorized_keys"
chown -R "$(stat -c %u:%g "$root/home/razr")" "$root/home/razr/.ssh"
install -d -m 0755 "$root/etc/sudoers.d"
printf 'razr ALL=(root) NOPASSWD: /usr/bin/systemctl poweroff\n' > "$root/etc/sudoers.d/99-qemu-only"
chmod 0440 "$root/etc/sudoers.d/99-qemu-only"
truncate -s "$ROOTFS_SIZE_MIB"M "$work/rootfs.ext4"
mkfs.ext4 -F -q -L RAZRROOT -d "$root" "$work/rootfs.ext4" > "$evidence/mkfs.log" 2>&1
sha256sum "$work/rootfs.ext4" > "$evidence/qemu-disk-sha256.txt"
(cd "$evidence" && sha256sum rootfs.tar.zst qemu-vmlinuz qemu-initrd.img packages.tsv inputs.env ownership-verification.txt > SHA256SUMS)
echo 'Built Debian ARM64 userspace and generic virt disk, not oneli boot firmware.'
