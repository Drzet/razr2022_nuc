#!/usr/bin/env bash
# Layer only Debian's signed wireless-regdb package on the IMMUTABLE accepted radio rootfs.
# No package reinstallation for existing radio stack, no kernel rebuild or native root device.
set -Eeuo pipefail
[[ $EUID == 0 && $# == 3 ]] || { echo 'usage: sudo bash scripts/stage-radio-regdb.sh ACCEPTED-TAR ACCEPTED-SHA NEW-WORKDIR' >&2; exit 2; }
src=$(realpath "$1"); expected=$2; work=$(realpath -m "$3")
[[ "$expected" == 1cfb7b29b6502c08fc5e9d1139c98c8ef78012c5a46d5c24962646045372865b ]] || exit 2
[[ ! -e "$work" ]] || { echo 'Workdir exists' >&2; exit 2; }
printf '%s  %s\n' "$expected" "$src" | sha256sum -c -
mkdir -p "$work/root" "$work/evidence"
root="$work/root"
tar --zstd --numeric-owner -xf "$src" -C "$root"
[[ -f "$root/etc/apt/keyrings/razr-debian-trixie.gpg" ]] || { echo 'Pinned Debian keyring missing' >&2; exit 1; }
grep -Fq 'signed-by=/etc/apt/keyrings/razr-debian-trixie.gpg' "$root/etc/apt/sources.list"
grep -Fq 'snapshot.debian.org/archive/debian/20261011T000000Z' "$root/etc/apt/sources.list"
[[ -x /usr/bin/qemu-aarch64-static ]] || exit 2
mkdir -p "$root/usr/bin" "$root/usr/sbin" "$root/proc" "$root/sys" "$root/dev"
cp /usr/bin/qemu-aarch64-static "$root/usr/bin/qemu-aarch64-static"
cp /etc/resolv.conf "$root/etc/resolv.conf"
cat > "$root/usr/sbin/policy-rc.d" <<'POLICY'
#!/bin/sh
exit 101
POLICY
chmod 755 "$root/usr/sbin/policy-rc.d"
cleanup() {
 rc=$?
 trap - EXIT INT TERM
 for p in "$root/dev" "$root/sys" "$root/proc"; do
    if mountpoint -q "$p"; then umount "$p" || rc=1; fi
 done
 echo "$rc" > "$work/evidence/staging-exit.txt"
 exit "$rc"
}
trap cleanup EXIT INT TERM
mount -t proc proc "$root/proc"
mount -t sysfs sysfs "$root/sys"
mount --bind /dev "$root/dev"
# Use only the accepted signed trixie snapshot. Do not download unsigned regdb files.
chroot "$root" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get update > "$work/evidence/apt-update.log" 2>&1
chroot "$root" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends wireless-regdb > "$work/evidence/apt-install.log" 2>&1
# Custom upstream mainline kernel trusts sforshee/wens, not Debian's separate signer.
chroot "$root" update-alternatives --set regulatory.db /lib/firmware/regulatory.db-upstream \
    > "$work/evidence/selected-alternative.txt" 2>&1
chroot "$root" update-alternatives --display regulatory.db > "$work/evidence/alternatives.txt"
chroot "$root" dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n' wireless-regdb > "$work/evidence/regdb-package.tsv"
chroot "$root" dpkg -V wireless-regdb > "$work/evidence/dpkg-verify.txt"
[[ ! -s "$work/evidence/dpkg-verify.txt" ]]
# Both active names MUST resolve to matching upstream files, not Debian-only signatures.
for file in regulatory.db regulatory.db.p7s; do
    selected=$(chroot "$root" readlink -f "/usr/lib/firmware/$file")
    [[ "$selected" == "/usr/lib/firmware/$file-upstream" ]] || {
      echo "Wrong selected trusted signature for $file: $selected" >&2; exit 1;
    }
    [[ -s "$root$selected" ]] || exit 1
    printf '%s  %s\n' "$(sha256sum "$root$selected" | cut -d' ' -f1)" "usr/lib/firmware/$file-upstream" \
       >> "$work/evidence/regdb-sha256.txt"
done
# Existing source firmware and matching module ABI are retained.
test -f "$root/usr/lib/modules/7.3.0-rc6-g7f3865ee17c3/modules.dep"
test ! -e "$root/home/razr/.ssh/authorized_keys"
rm -f "$root/usr/bin/qemu-aarch64-static" "$root/usr/sbin/policy-rc.d" "$root/etc/resolv.conf"
for p in "$root/dev" "$root/sys" "$root/proc"; do umount "$p"; done
tar --sort=name --numeric-owner --mtime='@1791676800' \
    --pax-option=delete=atime,delete=ctime -C "$root" -cf - . | \
    zstd -T0 -10 -o "$work/radio-rootfs-regdb-v2.tar.zst" > "$work/evidence/compress.log" 2>&1
sha256sum "$work/radio-rootfs-regdb-v2.tar.zst" > "$work/evidence/rootfs-sha256.txt"
echo RADIO_REGDB_LAYER_PASS
