#!/usr/bin/env bash
# Prepare a separate QEMU virt image from ONE coordinator-selected combined build.
# No oneli DTB, proprietary board firmware, boot.img or phone flashing.
set -Eeuo pipefail
if [[ $# -ne 4 ]]; then
  echo 'usage: sudo bash scripts/prepare-project-qemu.sh BUNDLE-DIR verified-rootfs.tar.zst sha256 NEW-WORK-DIR' >&2
  exit 2
fi
script_dir=$(cd "$(dirname "$0")" && pwd -P)
bundle=$(realpath "$1")
tarball=$(realpath "$2")
rootfs_sha=$3
work=$(realpath -m "$4")
[[ "$rootfs_sha" =~ ^[0-9a-f]{64}$ ]] || { echo 'Expected pinned rootfs SHA256' >&2; exit 2; }
[[ ! -e "$work" ]] || { echo 'Refusing existing work directory' >&2; exit 2; }
# This is a NON-ROOT, EXECUTABLE preflight; the staging code uses the same tool.
python3 "$script_dir/preflight-project-qemu.py" --bundle-root "$bundle"
printf '%s  %s\n' "$rootfs_sha" "$tarball" | sha256sum -c -
[[ "$EUID" -eq 0 ]] || { echo 'Root needed only for filesystem staging' >&2; exit 2; }
[[ -x /usr/bin/qemu-aarch64-static ]] || { echo 'qemu-user-static is required' >&2; exit 2; }
mkdir -p "$work/evidence" "$work/rootfs"
python3 "$script_dir/preflight-project-qemu.py" --bundle-root "$bundle" --output "$work/project-context.env"
source "$work/project-context.env"
root="$work/rootfs"
mkdir -p "$root" "$work/evidence"
tar --use-compress-program=zstd --numeric-owner -xf "$tarball" -C "$root"
[[ ! -e "$root/home/razr/.ssh/authorized_keys" ]] || { echo 'Refusing preauthorized base rootfs' >&2; exit 2; }
# Remove distribution-kernel modules; project-kernel modules are the only set installed.
rm -rf "$root/lib/modules" "$root/usr/lib/modules"
mkdir -p "$root/usr/lib/modules/$RELEASE" "$root/boot" "$root/proc" "$root/sys" "$root/dev"
cp -a "$MODDIR/." "$root/usr/lib/modules/$RELEASE/"
cp "$CONFIG" "$root/boot/config-$RELEASE"
# Preserve build inputs; depmod creates the concrete staged dependency index.
depmod -b "$root" "$RELEASE"
cp "$IMAGE" "$work/vmlinuz"
# Fresh ephemeral credentials and module-loading grant ONLY in disposable QEMU disk.
ssh-keygen -q -t ed25519 -N '' -f "$work/ssh_id_ed25519"
install -d -m 0700 "$root/home/razr/.ssh"
install -m 0600 "$work/ssh_id_ed25519.pub" "$root/home/razr/.ssh/authorized_keys"
chown -R "$(stat -c %u:%g "$root/home/razr")" "$root/home/razr/.ssh"
install -d -m 0755 "$root/etc/sudoers.d"
printf 'razr ALL=(root) NOPASSWD: /usr/bin/systemctl poweroff, /usr/sbin/modprobe %s\n' "$MODULE" > "$root/etc/sudoers.d/99-qemu-only"
chmod 0440 "$root/etc/sudoers.d/99-qemu-only"
# Native initramfs from the matching project-kernel module tree, not Debian's kernel.
test -f "$root/usr/sbin/update-initramfs"
cp /usr/bin/qemu-aarch64-static "$root/usr/bin/qemu-aarch64-static"
# Install cleanup *before* the first mount. Failure at mount #2/#3 cannot leak.
cleanup() {
  rc=$?
  trap - EXIT INT TERM
  for target in "$root/dev" "$root/sys" "$root/proc"; do
    if mountpoint -q "$target"; then umount "$target" || rc=1; fi
  done
  if [[ -d "$work/evidence" ]]; then echo "$rc" > "$work/evidence/prepare-exit-code.txt"; fi
  exit "$rc"
}
trap cleanup EXIT INT TERM
mount -t proc proc "$root/proc"
mount -t sysfs sysfs "$root/sys"
mount --bind /dev "$root/dev"
chroot "$root" update-initramfs -c -k "$RELEASE"
for target in "$root/dev" "$root/sys" "$root/proc"; do umount "$target"; done
rm -f "$root/usr/bin/qemu-aarch64-static"
test -s "$root/boot/initrd.img-$RELEASE"
cp "$root/boot/initrd.img-$RELEASE" "$work/initrd.img"
# Independent generated initramfs check. Real module data/hashes are
# subsequently inspected by the full v3 validator against the Boot bundle.
lsinitramfs "$work/initrd.img" | grep -Eq '(^|/)init$' || {
  echo 'No /init in new kernel initramfs' >&2
  exit 1
}
truncate -s 3072M "$work/rootfs.ext4"
mkfs.ext4 -q -F -L RAZRROOT -d "$root" "$work/rootfs.ext4"
echo 0 > "$work/evidence/build-exit-code.txt"
{
  printf 'project_kernel_commit=%s\nproject_build_id=%s\nproject_kernel_release=%s\n' "$COMMIT" "$BUILD_ID" "$RELEASE"
  printf 'runtime_module=%s\nrootfs_source_sha256=%s\n' "$MODULE" "$rootfs_sha"
  printf 'qemu_dtb_source=QEMU_virt_generated_never_oneli\n'
  sha256sum "$work/vmlinuz" "$work/initrd.img" "$work/rootfs.ext4"
} > "$work/evidence/project-qemu-provenance.txt"
echo "Staged ONLY: new project initramfs and disk for release $RELEASE; no QEMU or phone test executed"
