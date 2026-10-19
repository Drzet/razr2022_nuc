#!/usr/bin/env bash
# Reuse accepted radio QEMU construction with EXACT reduced-profile substitutions.
# The original tested preparer remains unchanged and its identity gates are not bypassed.
set -Eeuo pipefail
[[ $EUID -eq 0 && $# -eq 4 ]] || { echo "usage: sudo bash $0 REDUCED-TAR PRODUCER-RELEASE SHA NEW-WORKDIR" >&2; exit 2; }
script_dir=$(cd "$(dirname "$0")" && pwd -P)
tarball=$(realpath "$1")
producer=$(realpath "$2")
expected=$3
work=$(realpath -m "$4")
[[ "$expected" =~ ^[0-9a-f]{64}$ ]] || exit 2
[[ ! -e "$work" ]] || { echo "Workdir already exists" >&2; exit 2; }
printf '%s  %s\n' "$expected" "$tarball" | sha256sum -c -
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
# The legacy accepted preparer embeds the old release and pinned source hashes.
# Rebind ALL of them in a one-use copy with exact expected old literals; failure
# to find exactly the recorded old profile is a hard failure, never a skipped gate.
python3 - "$script_dir/prepare-radio-rootfs-qemu.sh" "$tmp/preparer.sh" "$expected" <<'PY'
import pathlib,sys
source=pathlib.Path(sys.argv[1]).read_text()
replace={
 "7.3.0-rc6-g7f3865ee17c3":"7.3.0-rc6-oneli-reduced1-g7f3865ee17c3",
 "1cfb7b29b6502c08fc5e9d1139c98c8ef78012c5a46d5c24962646045372865b":sys.argv[3],
 "0a28060210e747f8c63755142935feda101df4f5d9759f4e876bc2bb1373fb2e":"279431f997fc2334d92760d47c01aec2b8e12cf47e6d149d6a078f2347c330e8",
 "e10f77e9c982a4c3c81c94e69922ad8ae623b71e99df88e40c415e5a6fc0b273":"97ee634780847771163608e353e0086eceee6347ccd42a4d9d87d04f967981be",
}
for old,new in replace.items():
    n=source.count(old)
    if n<1: raise ValueError("Expected original immutable parameter not found: "+old)
    source=source.replace(old,new)
for old in replace:
    if old in source: raise ValueError("Stale original field still present: "+old)
pathlib.Path(sys.argv[2]).write_text(source)
PY
bash -n "$tmp/preparer.sh"
bash "$tmp/preparer.sh" "$tarball" "$producer" "$expected" "$work"
# The inherited QEMU-only test harness generates its initramfs and verifies
# that matching pre-power .ko appears there. Reuse all of that behavior.
root="$work/rootfs"
test -s "$work/initrd.img"
test -f "$root/usr/lib/modules/7.3.0-rc6-oneli-reduced1-g7f3865ee17c3/modules.dep"
test ! -e "$root/usr/lib/modules/7.3.0-rc6-g7f3865ee17c3"
cp "$script_dir/reduced-radio-guest.sh" "$root/usr/local/libexec/razr-radio-runtime-smoke"
chmod 0755 "$root/usr/local/libexec/razr-radio-runtime-smoke"
# Rematerialize ONLY the disposable virtio disk for the combined one-pass guest.
mkfs.ext4 -q -F -L RAZRREDUCED -d "$root" "$work/rootfs.ext4"
sha256sum "$work/vmlinuz" "$work/initrd.img" "$work/rootfs.ext4" > "$work/evidence/reduced-qemu-artifacts.txt"
echo RAZR_REDUCED_QEMU_PREP_PASS
