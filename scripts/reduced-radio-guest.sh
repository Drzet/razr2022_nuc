#!/bin/sh
# QEMU-only one-pass reduced kernel + Debian radio compatibility check.
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
failures=0
say() { printf '%s\n' "$*" >/dev/console 2>/dev/null || :; }
bad() { say "RAZR_REDUCED_FAIL=$1"; failures=$((failures + 1)); }
release=7.3.0-rc6-oneli-reduced1-g7f3865ee17c3
say RAZR_REDUCED_GUEST_BEGIN
if test "$(cat /proc/1/comm)" = systemd; then say RAZR_REDUCED_SYSTEMD_PASS; else bad PID1; fi
if test "$(dpkg --print-architecture)" = arm64 && test "$(uname -r)" = "$release"; then
    say RAZR_REDUCED_RELEASE_PASS
else bad ABI; fi
if test "$(find /usr/lib/modules -mindepth 1 -maxdepth 1 -type d -printf '%f\n')" = "$release" &&
    test ! -e /usr/lib/modules/7.3.0-rc6-g7f3865ee17c3; then
    say RAZR_REDUCED_ONLY_MATCHING_MODULES_PASS
else bad MIXED_MODULE_DIR; fi
if grep -q '^pci_pwrctrl_pwrseq ' /proc/modules; then
    say RAZR_REDUCED_PREPOWER_PASS
else bad PREPOWER; fi
if modprobe --show-depends hci_uart >/run/reduced-hci-deps.log 2>&1 &&
    modprobe hci_uart &&
    grep -q '^hci_uart ' /proc/modules; then
    say RAZR_REDUCED_HCI_MODPROBE_PASS
else bad HCI; fi
if modprobe --show-depends ath11k_pci >/run/reduced-ath11k-deps.log 2>&1 &&
    modprobe ath11k_pci &&
    grep -q '^ath11k_pci ' /proc/modules; then
    say RAZR_REDUCED_ATH11K_MODPROBE_PASS
else
    bad ATH11K
    while IFS= read -r line; do say "RAZR_REDUCED_ATH11K_ERROR=$line"; done < /run/reduced-ath11k-deps.log
fi
if busctl --system list --no-pager >/run/reduced-dbus.log 2>&1; then
    say RAZR_REDUCED_DBUS_PASS
else bad DBUS; fi
if test -f /usr/lib/systemd/system/bluetooth.service ||
    test -f /lib/systemd/system/bluetooth.service; then
    say RAZR_REDUCED_BLUEZ_UNIT_PASS
else bad BLUEZ_UNIT; fi
say "RAZR_REDUCED_BLUEZ_STATE=$(systemctl is-active bluetooth.service 2>/dev/null)"
for attempt in $(seq 1 50); do
    if systemctl is-active --quiet NetworkManager.service &&
       ip -4 -o address show scope global | grep -q 'inet ' &&
       ip -4 route show default | grep -q '^default '; then break; fi
    sleep 2
done
if systemctl is-active --quiet NetworkManager.service; then
    say RAZR_REDUCED_NM_PASS
else bad NETWORKMANAGER; fi
ip -4 -o address show scope global |
    while IFS= read -r line; do say "RAZR_REDUCED_IPV4=$line"; done
ip -4 route show |
    while IFS= read -r line; do say "RAZR_REDUCED_ROUTE=$line"; done
if ip -4 -o address show scope global | grep -q 'inet '; then
    say RAZR_REDUCED_IPV4_PASS
else bad IPV4; fi
if ip -4 route show default | grep -q '^default '; then
    say RAZR_REDUCED_ROUTE_PASS
else bad ROUTE; fi
if test -s /etc/resolv.conf &&
    grep -Eq '^nameserver[[:space:]]+[^[:space:]]+' /etc/resolv.conf; then
    say RAZR_REDUCED_RESOLVER_PASS
else bad RESOLVER; fi
if getent ahostsv4 deb.debian.org >/run/reduced-dns.log 2>&1; then
    say RAZR_REDUCED_DNS_PASS
else bad DNS; fi
say RAZR_REGDB_TEST_START
say RAZR_REGDB_KERNEL_MATCH
if test "$(readlink -f /usr/lib/firmware/regulatory.db)" = /usr/lib/firmware/regulatory.db-upstream &&
    test "$(readlink -f /usr/lib/firmware/regulatory.db.p7s)" = /usr/lib/firmware/regulatory.db.p7s-upstream; then
    say RAZR_REDUCED_SIGNED_REGDB_FILES_PASS
    say "RAZR_REGDB_DB_SHA256=$(sha256sum /usr/lib/firmware/regulatory.db-upstream | cut -d' ' -f1)"
    say "RAZR_REGDB_SIG_SHA256=$(sha256sum /usr/lib/firmware/regulatory.db.p7s-upstream | cut -d' ' -f1)"
else bad REGDB_FILES; fi
if modprobe cfg80211 && iw reg reload >/run/reduced-regdb-reload.log 2>&1; then
    say RAZR_REGDB_KERNEL_SIGNATURE_ACCEPTED
else
    bad REGDB_KERNEL_SIGNATURE
    while IFS= read -r line; do say "RAZR_REDUCED_REGDB_ERROR=$line"; done < /run/reduced-regdb-reload.log
fi
if iw reg get > /run/reduced-regdomain.log 2>&1 &&
   grep -q '^global' /run/reduced-regdomain.log; then
    say RAZR_REDUCED_REGDOMAIN_PASS
else bad REGDOMAIN; fi
while IFS= read -r line; do
    say "RAZR_REDUCED_REGDOMAIN=$line"
    say "RAZR_REGDB_DOMAIN=$line"
done < /run/reduced-regdomain.log
say "RAZR_REDUCED_FAILURES=$failures"
if test "$failures" -eq 0; then
    say RAZR_REGDB_TEST_PASS
    say RAZR_REDUCED_ROOTFS_QEMU_PASS
else
    say RAZR_REDUCED_ROOTFS_QEMU_FAIL
fi
sync
systemctl --no-block poweroff || /usr/sbin/poweroff -f
