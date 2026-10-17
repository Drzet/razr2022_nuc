#!/usr/bin/env bash
# Use the existing tested virtio/initramfs preparation, replacing only the disposable reporter.
set -Eeuo pipefail
[[ $EUID -eq 0 && $# == 4 ]] || { echo "usage: sudo bash $0 VERSIONED-ROOTFS RADIO-RELEASE-DIR ROOTFS-SHA NEW-WORKDIR" >&2; exit 2; }
script_dir=$(cd "$(dirname "$0")" && pwd)
bash "$script_dir/prepare-radio-rootfs-qemu.sh" "$@"
work=$(realpath "$4")
root="$work/rootfs"
test -s "$work/initrd.img"
# Replace the previous comprehensive QEMU-only service with ONE focused regdb check.
cat > "$root/usr/local/libexec/razr-radio-runtime-smoke" <<'GUEST'
#!/bin/sh
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
say() { printf '%s\n' "$*" >/dev/console 2>/dev/null || :; }
fail() { say "RAZR_REGDB_FAIL=$1"; say RAZR_REGDB_TEST_FAIL; systemctl --no-block poweroff || :; exit 1; }
say RAZR_REGDB_TEST_START
test "$(cat /proc/1/comm)" = systemd || fail PID1
test "$(uname -r)" = 7.3.0-rc6-g7f3865ee17c3 || fail KERNEL
say RAZR_REGDB_KERNEL_MATCH
db=$(readlink -f /usr/lib/firmware/regulatory.db) || fail DB_LINK
sig=$(readlink -f /usr/lib/firmware/regulatory.db.p7s) || fail SIG_LINK
test "$db" = /usr/lib/firmware/regulatory.db-upstream || fail DB_NOT_UPSTREAM
test "$sig" = /usr/lib/firmware/regulatory.db.p7s-upstream || fail SIG_NOT_UPSTREAM
test -s "$db" && test -s "$sig" || fail DB_FILES
say "RAZR_REGDB_DB_SHA256=$(sha256sum "$db" | cut -d' ' -f1)"
say "RAZR_REGDB_SIG_SHA256=$(sha256sum "$sig" | cut -d' ' -f1)"
modprobe cfg80211 || fail CFG80211_MODULE
# NL80211_CMD_RELOAD_REGDB enters kernel reg_reload_regdb -> valid_regdb,
# which checks regulatory.db format and its PKCS#7 signature against built-in keys.
if iw reg reload > /run/razr-regdb-reload.log 2>&1; then
    say RAZR_REGDB_KERNEL_SIGNATURE_ACCEPTED
else
    while IFS= read -r line; do say "RAZR_REGDB_RELOAD_ERROR=$line"; done < /run/razr-regdb-reload.log
    fail KERNEL_REGDB_RELOAD
fi
iw reg get > /run/razr-regdb-domain.log 2>&1 || fail REGDOMAIN_QUERY
grep -q '^global' /run/razr-regdb-domain.log || fail REGDOMAIN_MISSING
while IFS= read -r line; do say "RAZR_REGDB_DOMAIN=$line"; done < /run/razr-regdb-domain.log
# Do not treat a missing-error grep alone as a success condition, but surface it.
dmesg | grep -E '(regulatory.db|cfg80211:)' | tail -n 20 |
   while IFS= read -r line; do say "RAZR_REGDB_DMESG=$line"; done
say RAZR_REGDB_TEST_PASS
sync
systemctl --no-block poweroff || /usr/sbin/poweroff -f
GUEST
chmod 0755 "$root/usr/local/libexec/razr-radio-runtime-smoke"
# This ext4 disk remains test-only, and original published tar does not change.
mkfs.ext4 -F -q -L RAZRREGDB -d "$root" "$work/rootfs.ext4"
{
 sha256sum "$work/initrd.img" "$work/rootfs.ext4"
 echo 'regdb_test=single_nl80211_signed_reload'
 echo 'native_root_device=unresolved'
} > "$work/evidence/regdb-qemu-staging.txt"
echo RADIO_REGDB_QEMU_PREP_PASS
