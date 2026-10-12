#!/usr/bin/env bash
# Prepare a separate QEMU virt image from ONE coordinator-selected combined build.
# No oneli DTB, proprietary board firmware, boot.img or phone flashing.
set -Eeuo pipefail
if [[ $# -ne 5 || $EUID -ne 0 ]]; then
  echo 'usage: sudo bash scripts/prepare-project-qemu.sh native-v3.json artifact-root debian-rootfs.tar.zst expected-rootfs-sha256 NEW-work-dir' >&2
  exit 2
fi
manifest=$(realpath "$1")
artifacts=$(realpath "$2")
tarball=$(realpath "$3")
rootfs_sha=$4
work=$(realpath -m "$5")
[[ ! -e "$work" ]] || { echo 'Refusing to overwrite existing work directory' >&2; exit 2; }
[[ "$rootfs_sha" =~ ^[0-9a-f]{64}$ ]] || exit 2
printf '%s  %s\n' "$rootfs_sha" "$tarball" | sha256sum -c -
mkdir -p "$work"
# Preflight: this is an artifact staging test, not acceptance of the unbuilt initramfs.
python3 - "$manifest" "$artifacts" "$work/project-context.env" <<'PY'
import hashlib
import json
import pathlib
import re
import shlex
import sys
d = json.loads(pathlib.Path(sys.argv[1]).read_text())
root = pathlib.Path(sys.argv[2]).resolve(strict=True)
out = pathlib.Path(sys.argv[3])
def need(ok, msg):
    if not ok: raise SystemExit("PROJECT_QEMU_PREFLIGHT_FAILED: " + msg)
need(d.get("schema_version") == 3 and d.get("target_environment") == "qemu_virt", "requires v3 qemu_virt")
need(d.get("dtb_path") is None and d.get("boot_packaging_manifest_path") is None,
     "QEMU virt rejects oneli DT and phone image packaging")
need(re.fullmatch("[0-9a-f]{40}", str(d.get("kernel_commit", ""))) is not None, "exact kernel commit missing")
release = d.get("kernel_release", "")
need(re.fullmatch("[A-Za-z0-9._+~-]+", release) is not None, "kernel release missing")
build = d.get("same_build", {})
need(build.get("kernel_commit") == d["kernel_commit"] and build.get("kernel_release") == release
     and isinstance(build.get("build_id"), str) and len(build["build_id"]) >= 8,
     "same-build provenance absent")
sha = d.get("sha256", {})
for path_key, digest_field in (("image_path", "image_sha256"), ("config_path", "config_sha256"),
                               ("module_symvers_path", "module_symvers_sha256")):
    relative = d.get(path_key)
    need(isinstance(relative, str) and not relative.startswith("/"), "missing " + path_key)
    p = (root / relative).resolve(strict=True)
    need(p.is_relative_to(root) and p.is_file(), path_key + " escapes artifact set")
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    need(sha.get(path_key) == h and build.get(digest_field) == h, path_key + " hash/provenance mismatch")
modules_dir = (root / d["modules_directory"]).resolve(strict=True)
need(modules_dir.is_relative_to(root) and modules_dir.name == release and
     modules_dir.parent.name == "modules", "wrong module tree")
files = sorted(p for p in modules_dir.rglob("*") if p.is_file() and
               p.name.endswith((".ko", ".ko.xz", ".ko.gz", ".ko.zst")))
expected = d.get("modules_sha256", {})
need(isinstance(expected, dict) and set(expected) == {p.relative_to(modules_dir).as_posix() for p in files},
     "module hashes do not exhaustively cover installed modules")
for p in files:
    rel = p.relative_to(modules_dir).as_posix()
    need(hashlib.sha256(p.read_bytes()).hexdigest() == expected[rel], "module SHA mismatch: " + rel)
    # Detect a mismatched-release module before creating a VM image.
    import gzip
    import lzma
    import subprocess
    import tempfile
    if p.name.endswith(".ko.xz"):
        elf = lzma.decompress(p.read_bytes())
    elif p.name.endswith(".ko.gz"):
        elf = gzip.decompress(p.read_bytes())
    elif p.name.endswith(".ko.zst"):
        elf = subprocess.run(["zstd", "-dc", str(p)], check=True, capture_output=True).stdout
    else:
        elf = p.read_bytes()
    need(len(elf) >= 20 and elf[:4] == bytes((127, 69, 76, 70)) and
         elf[4] == 2 and elf[5] == 1 and int.from_bytes(elf[18:20], "little") == 183,
         "module is not AArch64 ELF: " + rel)
    with tempfile.TemporaryDirectory() as temp:
        unpacked = pathlib.Path(temp) / "module.ko"
        unpacked.write_bytes(elf)
        magic = subprocess.run(["modinfo", "-F", "vermagic", str(unpacked)],
                               check=True, capture_output=True, text=True).stdout.strip()
    need(magic.split() and magic.split()[0] == release,
         "module vermagic release mismatch: " + rel)
dep = modules_dir / "modules.dep"
need(dep.is_file() and hashlib.sha256(dep.read_bytes()).hexdigest() == sha.get("modules_dep"),
     "matching depmod index required")
module = d.get("qemu_runtime_module")
need(isinstance(module, dict), "select real loadable QEMU runtime test module")
name, rel = module.get("name"), module.get("relative_path")
need(isinstance(name, str) and re.fullmatch("[A-Za-z0-9_-]+", name), "invalid module name")
need(isinstance(rel, str) and rel in expected, "runtime module absent from hashed module inventory")
need(re.search(r"(^|/)oneli([./_-]|$)", d.get("image_path", ""), re.I) is None,
     "oneli image cannot be QEMU kernel")
values = {"RELEASE": release, "MODULE": name,
          "IMAGE": str((root / d["image_path"]).resolve()),
          "CONFIG": str((root / d["config_path"]).resolve()),
          "MODDIR": str(modules_dir), "COMMIT": d["kernel_commit"],
          "BUILD_ID": build["build_id"]}
out.write_text("".join(k + "=" + shlex.quote(v) + "\n" for k, v in values.items()))
PY
source "$work/project-context.env"
root="$work/rootfs"
mkdir -p "$root" "$work/evidence"
tar --use-compress-program=zstd --numeric-owner -xf "$tarball" -C "$root"
[[ ! -e "$root/home/razr/.ssh/authorized_keys" ]] || { echo 'Refusing preauthorized base rootfs' >&2; exit 2; }
# Remove distribution-kernel modules; project-kernel modules are the only set installed.
rm -rf "$root/lib/modules" "$root/usr/lib/modules"
mkdir -p "$root/lib/modules/$RELEASE" "$root/boot"
cp -a "$MODDIR/." "$root/lib/modules/$RELEASE/"
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
mount -t proc proc "$root/proc"
mount -t sysfs sysfs "$root/sys"
mount --bind /dev "$root/dev"
cleanup() {
  umount "$root/dev" 2>/dev/null || true
  umount "$root/sys" 2>/dev/null || true
  umount "$root/proc" 2>/dev/null || true
}
trap cleanup EXIT
chroot "$root" update-initramfs -c -k "$RELEASE"
cleanup
trap - EXIT
rm -f "$root/usr/bin/qemu-aarch64-static"
test -s "$root/boot/initrd.img-$RELEASE"
cp "$root/boot/initrd.img-$RELEASE" "$work/initrd.img"
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
