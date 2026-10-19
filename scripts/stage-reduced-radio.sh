#!/usr/bin/env bash
# Prepare a new reduced-release rootfs by replacing ONLY the installed module ABI.
set -Eeuo pipefail
[[ $EUID -eq 0 && $# == 5 ]] || {
  echo "usage: sudo bash $0 SIGNED-REGDB-TAR VERIFIED-SHA PRODUCER-RELEASE INSTALLED-MODULES NEW-WORKDIR" >&2
  exit 2
}
rootfs_tar=$(realpath "$1")
expected=$2
producer=$(realpath "$3")
installed=$(realpath "$4")
work=$(realpath -m "$5")
old=7.3.0-rc6-g7f3865ee17c3
new=7.3.0-rc6-oneli-reduced1-g7f3865ee17c3
[[ "$expected" == 630738c3ac43726199f56d326511fb8a69a443a01eea8e0a234318de5d3e8b38 ]] || exit 2
[[ ! -e "$work" ]] || { echo "Output exists" >&2; exit 2; }
printf '%s  %s\n' "$expected" "$rootfs_tar" | sha256sum -c -
python3 scripts/consume-reduced-radio.py --release "$producer" --installed "$installed" --output /tmp/razr-reduced-preflight-$$.json
rm -f /tmp/razr-reduced-preflight-$$.json
mkdir -p "$work/root" "$work/evidence"
root="$work/root"
tar --zstd --numeric-owner -xf "$rootfs_tar" -C "$root"
test -f "$root/usr/lib/modules/$old/modules.dep"
test "$(find "$root/usr/lib/modules" -mindepth 1 -maxdepth 1 -type d -printf '%f\n')" = "$old"
test ! -e "$root/home/razr/.ssh/authorized_keys"
for firmware in regulatory.db-upstream regulatory.db.p7s-upstream; do
  test -s "$root/usr/lib/firmware/$firmware"
done
echo '2fb33ca0074db573e05ef7dd50bb45b63c0ff98b7e852e1105ebad536fae8e6b  regulatory.db-upstream' |
  (cd "$root/usr/lib/firmware" && sha256sum -c -)
echo 'c941c08f51c93e46722293b85631604c3740d86c3de0c75f79aef50d2e919179  regulatory.db.p7s-upstream' |
  (cd "$root/usr/lib/firmware" && sha256sum -c -)
test "$(readlink "$root/etc/alternatives/regulatory.db")" = /lib/firmware/regulatory.db-upstream
# Existing firmware, services, package database and signed regulatory rules are frozen.
rm -rf "$root/usr/lib/modules"
mkdir -p "$root/usr/lib/modules"
cp -a "$installed/lib/modules/$new" "$root/usr/lib/modules/"
rm -f "$root/usr/lib/modules/$new/build" "$root/usr/lib/modules/$new/source"
depmod -b "$root" "$new"
test ! -e "$root/usr/lib/modules/$old"
test -s "$root/usr/lib/modules/$new/modules.dep"
for mod in pci-pwrctrl-pwrseq ath11k_pci hci_uart cfg80211; do
  modprobe -d "$root" -S "$new" --show-depends "$mod" > "$work/evidence/$mod-deps.txt"
  grep -Fq "/$new/" "$work/evidence/$mod-deps.txt"
done
printf 'reused_signed_regdb_rootfs_sha256=%s\nnew_release=%s\nold_release_absent=true\n' "$expected" "$new" > "$work/evidence/release-provenance.txt"
# Rootfs includes no injected QEMU smoke credentials, no native root device.
tar --sort=name --numeric-owner --mtime='@1791676800' --pax-option=delete=atime,delete=ctime \
  -C "$root" -cf - . | zstd -T0 -10 -o "$work/reduced-radio-rootfs.tar.zst" > "$work/evidence/compress.log" 2>&1
sha256sum "$work/reduced-radio-rootfs.tar.zst" > "$work/evidence/new-rootfs-sha256.txt"
echo RAZR_REDUCED_ROOTFS_STAGE_PASS
