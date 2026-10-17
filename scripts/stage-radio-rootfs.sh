#!/usr/bin/env bash
# Stages Debian ARM64 firmware/services against exactly ONE custom module ABI.
# This rootfs has no oneli UFS, native root device or hardware-boot acceptance.
set -Eeuo pipefail
[[ $EUID -eq 0 && $# -eq 5 ]] || { echo 'usage: sudo bash scripts/stage-radio-rootfs.sh ROOTFS-TAR SHA MODULES-DIR NEW-OUTPUT-DIR RELEASE' >&2; exit 2; }
source_tar=$(realpath "$1")
source_sha=$2
modules=$(realpath "$3")
work=$(realpath -m "$4")
release=$5
[[ "$source_sha" =~ ^[0-9a-f]{64}$ && "$release" == '7.3.0-rc6-g7f3865ee17c3' ]] || exit 2
[[ ! -e "$work" ]] || { echo 'Output must not exist' >&2; exit 2; }
printf '%s  %s\n' "$source_sha" "$source_tar" | sha256sum -c -
mkdir -p "$work/root" "$work/evidence"
root="$work/root"
tar --zstd --numeric-owner -xf "$source_tar" -C "$root"
[[ ! -e "$root/home/razr/.ssh/authorized_keys" ]] || { echo 'Rootfs embeds QEMU SSH credentials' >&2; exit 1; }
# Debian's generic distribution modules must not be installed alongside project modules.
rm -rf "$root/lib/modules" "$root/usr/lib/modules"
mkdir -p "$root/usr/lib/modules/$release" "$root/boot" "$root/proc" "$root/sys" "$root/dev"
cp -a "$modules/lib/modules/$release/." "$root/usr/lib/modules/$release/"
rm -f "$root/usr/lib/modules/$release/build" "$root/usr/lib/modules/$release/source"
depmod -b "$root" "$release"
# Extend original signed Debian snapshot; preserve the pinned archive key and expiry policy.
grep -Fq 'signed-by=/etc/apt/keyrings/razr-debian-trixie.gpg' "$root/etc/apt/sources.list"
sed -i -E '/^deb /s/ main$/ main non-free-firmware/' "$root/etc/apt/sources.list"
cp "$root/etc/apt/sources.list" "$work/evidence/apt-sources.txt"
[[ -x /usr/bin/qemu-aarch64-static ]] || exit 2
cp /usr/bin/qemu-aarch64-static "$root/usr/bin/qemu-aarch64-static"
cat > "$root/usr/sbin/policy-rc.d" <<'POLICY'
#!/bin/sh
exit 101
POLICY
chmod 755 "$root/usr/sbin/policy-rc.d"
cleanup() {
  rc=$?
  trap - EXIT INT TERM
  for target in "$root/dev" "$root/sys" "$root/proc"; do
    if mountpoint -q "$target"; then umount "$target" || rc=1; fi
  done
  [[ -d "$work/evidence" ]] && printf '%s\n' "$rc" > "$work/evidence/stage-exit-code.txt"
  exit "$rc"
}
trap cleanup EXIT INT TERM
mount -t proc proc "$root/proc"
mount -t sysfs sysfs "$root/sys"
mount --bind /dev "$root/dev"
chroot "$root" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get update > "$work/evidence/apt-update.log" 2>&1
chroot "$root" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  firmware-atheros network-manager bluez iw pciutils rfkill > "$work/evidence/apt-install.log" 2>&1
systemctl --root="$root" disable systemd-networkd.service > "$work/evidence/services.log" 2>&1 || :
systemctl --root="$root" enable NetworkManager.service bluetooth.service >> "$work/evidence/services.log" 2>&1
mkdir -p "$root/etc/modules-load.d"
printf 'ath11k_pci\nhci_uart\n' > "$root/etc/modules-load.d/80-oneli-radio-late.conf"
# Never insert Xiaomi MAC/NVM or invent a persist partition.
rm -f "$root/etc/systemd/network/80-razr-qemu.network"
chroot "$root" /usr/bin/dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n' > "$work/evidence/packages.tsv"
chroot "$root" /usr/bin/dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n' \
  firmware-atheros network-manager bluez iw pciutils rfkill > "$work/evidence/radio-packages.tsv"
modprobe -d "$root" -S "$release" --show-depends pci-pwrctrl-pwrseq > "$work/evidence/prepower-deps.txt"
modprobe -d "$root" -S "$release" --show-depends ath11k_pci > "$work/evidence/ath11k-deps.txt"
modprobe -d "$root" -S "$release" --show-depends hci_uart > "$work/evidence/bluetooth-deps.txt"
[[ -s "$work/evidence/prepower-deps.txt" && -s "$work/evidence/ath11k-deps.txt" && -s "$work/evidence/bluetooth-deps.txt" ]]
# File inventories and hashes are obtained from actual installed Debian packages.
dpkg-query --admindir="$root/var/lib/dpkg" -W >/dev/null
find "$root/usr/lib/firmware" "$root/lib/firmware" -type f 2>/dev/null | LC_ALL=C sort -u | \
  sed "s!^$root!!" > "$work/evidence/firmware-files.txt" || :
[[ -s "$work/evidence/firmware-files.txt" ]] || { echo 'Firmware files not installed' >&2; exit 1; }
chroot "$root" /usr/bin/dpkg -V firmware-atheros network-manager bluez iw pciutils rfkill \
  > "$work/evidence/dpkg-verify.txt"
rm -f "$root/usr/bin/qemu-aarch64-static" "$root/usr/sbin/policy-rc.d"
rm -f "$root"/etc/ssh/ssh_host_*
: > "$root/etc/machine-id"
for target in "$root/dev" "$root/sys" "$root/proc"; do umount "$target"; done
tar --sort=name --numeric-owner --mtime='@1791676800' --pax-option=delete=atime,delete=ctime \
  -C "$root" -cf - . | zstd -T0 -10 -o "$work/radio-rootfs.tar.zst" > "$work/evidence/compress.log" 2>&1
sha256sum "$work/radio-rootfs.tar.zst" > "$work/evidence/rootfs-sha256.txt"
echo RADIO_ROOTFS_STAGE_PASS
