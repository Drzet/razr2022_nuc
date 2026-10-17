#!/usr/bin/env bash
# Make a DISPOSABLE QEMU virt disk + initramfs from already-published radio inputs.
# No Debian package installation, kernel compilation, native root selection or phone boot.
set -Eeuo pipefail
[[ "$EUID" == 0 && $# == 4 ]] || { echo "usage: sudo bash $0 ROOTFS-TAR RADIO-RELEASE-DIR ROOTFS-SHA NEW-WORKDIR" >&2; exit 2; }
tarball=$(realpath "$1")
release_root=$(realpath "$2")
expected_sha=$3
work=$(realpath -m "$4")
release=7.3.0-rc6-g7f3865ee17c3
[[ "$expected_sha" == 1cfb7b29b6502c08fc5e9d1139c98c8ef78012c5a46d5c24962646045372865b ]] || exit 2
[[ ! -e "$work" ]] || { echo 'Work directory already exists' >&2; exit 2; }
printf '%s  %s\n' "$expected_sha" "$tarball" | sha256sum -c -
(
  cd "$release_root"
  sha256sum -c SHA256SUMS >/dev/null
  test "$(cat kernel.release)" = "$release"
  echo '0a28060210e747f8c63755142935feda101df4f5d9759f4e876bc2bb1373fb2e  Image' | sha256sum -c -
  echo 'e10f77e9c982a4c3c81c94e69922ad8ae623b71e99df88e40c415e5a6fc0b273  kernel.config' | sha256sum -c -
)
[[ -x /usr/bin/qemu-aarch64-static ]] || { echo 'qemu-user-static needed' >&2; exit 2; }
mkdir -p "$work/rootfs" "$work/evidence"
root="$work/rootfs"
tar --zstd --numeric-owner -xf "$tarball" -C "$root"
test "$(find "$root/usr/lib/modules" -mindepth 1 -maxdepth 1 -type d -printf '%f\n')" = "$release"
test -s "$root/usr/lib/modules/$release/modules.dep"
test ! -e "$root/etc/resolv.conf" || echo 'Note: prepared rootfs already has resolver path'
test ! -e "$root/home/razr/.ssh/authorized_keys"
test -f "$root/etc/NetworkManager/NetworkManager.conf"
test -x "$root/usr/sbin/update-initramfs"
test -f "$root/etc/systemd/system/multi-user.target.wants/NetworkManager.service"
# Explicit matching pre-power module in initramfs, no native storage support implied.
test -f "$root/usr/lib/modules/$release/kernel/drivers/pci/pwrctrl/pci-pwrctrl-pwrseq.ko"
cp "$release_root/kernel.config" "$root/boot/config-$release"
cp "$release_root/Image" "$work/vmlinuz"
mkdir -p "$root/etc/initramfs-tools"
printf '\npci-pwrctrl-pwrseq\n' >> "$root/etc/initramfs-tools/modules"
# QEMU-only serial tests, removed with the disposable image after this job.
install -d -m 0755 "$root/usr/local/libexec" "$root/etc/systemd/system/multi-user.target.wants"
cat > "$root/usr/local/libexec/razr-radio-runtime-smoke" <<'SMOKE'
#!/bin/sh
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
failures=0
say() { printf '%s\n' "$*" >/dev/console 2>/dev/null || :; }
bad() { say "RAZR_RADIO_CHECK_FAIL=$1"; failures=$((failures+1)); }
say "RAZR_RADIO_RUNTIME_BEGIN"
test "$(cat /proc/1/comm)" = systemd && say RAZR_RADIO_SYSTEMD_PID1_PASS || bad PID1
test "$(dpkg --print-architecture)" = arm64 || bad USERSPACE_ARCH
test "$(uname -r)" = 7.3.0-rc6-g7f3865ee17c3 && say RAZR_RADIO_RELEASE_PASS || bad KERNEL_RELEASE
if grep -q '^pci_pwrctrl_pwrseq ' /proc/modules; then say RAZR_RADIO_PREPOWER_PRESENT_PASS; else bad PREPOWER_EARLY; fi
if modprobe --show-depends dummy >/run/razr-dummy-deps.log 2>&1 && modprobe dummy &&
    grep -q '^dummy ' /proc/modules; then say RAZR_RADIO_MODULE_LOAD_PASS; else bad MODULE_LOAD; fi
if command -v busctl >/dev/null && busctl --system list --no-pager >/run/razr-dbus.log 2>&1; then
    say RAZR_RADIO_DBUS_PASS
else bad DBUS; fi
if test -f /lib/systemd/system/bluetooth.service || test -f /usr/lib/systemd/system/bluetooth.service; then
    say RAZR_RADIO_BLUEZ_UNIT_PRESENT
else bad BLUEZ_PACKAGE; fi
# No Bluetooth controller exists in QEMU virt; an absent adapter is expected.
if test -d /sys/class/bluetooth; then say RAZR_RADIO_BLUEZ_SYSFS_PRESENT; fi
systemctl is-active bluetooth.service 2>&1 | while read -r line; do say "RAZR_RADIO_BLUEZ_STATE=$line"; done
nmcli general status 2>&1 | while read -r line; do say "RAZR_RADIO_NM_STATUS=$line"; done
for attempt in $(seq 1 55); do
    systemctl is-active --quiet NetworkManager.service &&
      ip -4 -o address show scope global | grep -q 'inet ' &&
      ip -4 route show default | grep -q '^default ' && break
    sleep 2
done
if systemctl is-active --quiet NetworkManager.service; then say RAZR_RADIO_NM_ACTIVE_PASS; else bad NETWORKMANAGER; fi
ip -4 -o address show scope global > /run/razr-addresses.txt 2>&1 || :
ip -4 route show > /run/razr-routes.txt 2>&1 || :
while IFS= read -r line; do say "RAZR_RADIO_IP=$line"; done < /run/razr-addresses.txt
while IFS= read -r line; do say "RAZR_RADIO_ROUTE=$line"; done < /run/razr-routes.txt
if grep -q 'inet ' /run/razr-addresses.txt; then say RAZR_RADIO_IPV4_PASS; else bad IPV4; fi
if grep -q '^default ' /run/razr-routes.txt; then say RAZR_RADIO_ROUTE_PASS; else bad DEFAULT_ROUTE; fi
nmcli -t -f GENERAL.STATE,GENERAL.CONNECTION device show 2>&1 |
    while IFS= read -r line; do say "RAZR_RADIO_NM_DEVICE=$line"; done
if test -s /etc/resolv.conf && grep -Eq '^nameserver[[:space:]]+[^[:space:]]+' /etc/resolv.conf; then
    say RAZR_RADIO_RESOLVER_CONFIG_PASS
    while IFS= read -r line; do say "RAZR_RADIO_RESOLVER=$line"; done < /etc/resolv.conf
else
    bad RESOLVER_MISSING
    ls -l /etc/resolv.conf /run/NetworkManager/resolv.conf 2>&1 |
        while IFS= read -r line; do say "RAZR_RADIO_RESOLVER_DEBUG=$line"; done
fi
if getent ahostsv4 deb.debian.org >/run/razr-dns-test.log 2>&1; then
    say RAZR_RADIO_DNS_LOOKUP_PASS
else
    say RAZR_RADIO_DNS_LOOKUP_FAILED
fi
say "RAZR_RADIO_RUNTIME_FAILURES=$failures"
if test "$failures" -eq 0; then say RAZR_RADIO_RUNTIME_SMOKE_PASS; else say RAZR_RADIO_RUNTIME_SMOKE_FAIL; fi
sync
systemctl --no-block poweroff || /usr/sbin/poweroff -f
exit 0
SMOKE
chmod 0755 "$root/usr/local/libexec/razr-radio-runtime-smoke"
cat > "$root/etc/systemd/system/razr-radio-runtime-smoke.service" <<'SERVICE'
[Unit]
Description=QEMU-only prepared radio Debian integration smoke
ConditionKernelCommandLine=razr.radio_runtime_smoke=1
After=NetworkManager.service dbus.service systemd-udevd.service
Wants=NetworkManager.service dbus.service
[Service]
Type=oneshot
TimeoutStartSec=220
ExecStart=/usr/local/libexec/razr-radio-runtime-smoke
[Install]
WantedBy=multi-user.target
SERVICE
ln -s ../razr-radio-runtime-smoke.service "$root/etc/systemd/system/multi-user.target.wants/razr-radio-runtime-smoke.service"
cp /usr/bin/qemu-aarch64-static "$root/usr/bin/qemu-aarch64-static"
cleanup() {
  rc=$?
  trap - EXIT INT TERM
  for path in "$root/dev" "$root/sys" "$root/proc"; do
    if mountpoint -q "$path"; then umount "$path" || rc=1; fi
  done
  printf '%s\n' "$rc" > "$work/evidence/staging-exit.txt"
  exit "$rc"
}
trap cleanup EXIT INT TERM
mount -t proc proc "$root/proc"
mount -t sysfs sysfs "$root/sys"
mount --bind /dev "$root/dev"
chroot "$root" update-initramfs -c -k "$release" > "$work/evidence/update-initramfs.log" 2>&1
for path in "$root/dev" "$root/sys" "$root/proc"; do umount "$path"; done
rm -f "$root/usr/bin/qemu-aarch64-static"
test -s "$root/boot/initrd.img-$release"
cp "$root/boot/initrd.img-$release" "$work/initrd.img"
lsinitramfs "$work/initrd.img" > "$work/evidence/initramfs-file-list.txt"
grep -q 'pci-pwrctrl-pwrseq.ko' "$work/evidence/initramfs-file-list.txt"
grep -Eq '(^|/)init$' "$work/evidence/initramfs-file-list.txt"
# QEMU virtio disk is a disposable test wrapper, not a phone partition.
truncate -s 3072M "$work/rootfs.ext4"
mkfs.ext4 -q -F -L RAZRTEST -d "$root" "$work/rootfs.ext4"
{
 sha256sum "$tarball" "$release_root/Image" "$work/vmlinuz" "$work/initrd.img" "$work/rootfs.ext4"
 printf 'native_root_device=unresolved\nqemu_only_disk=/dev/vda\n'
} > "$work/evidence/staging-provenance.txt"
echo RADIO_ROOTFS_QEMU_STAGE_PASS
