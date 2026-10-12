#!/usr/bin/env python3
"""Execute the REAL Boot bundle preflight on synthetic AArch64 module artifacts."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/preflight-project-qemu.py"
RELEASE = "6.12.991-combined-fixture-arm64"
SHA = "b" * 40
BUILTIN = (
    "CONFIG_ARM64", "CONFIG_SERIAL_AMBA_PL011", "CONFIG_SERIAL_AMBA_PL011_CONSOLE",
    "CONFIG_ARM_GIC", "CONFIG_VIRTIO_MMIO", "CONFIG_VIRTIO_BLK", "CONFIG_VIRTIO_NET",
    "CONFIG_EXT4_FS", "CONFIG_DEVTMPFS", "CONFIG_DEVTMPFS_MOUNT",
    "CONFIG_BLK_DEV_INITRD", "CONFIG_RD_GZIP", "CONFIG_INET", "CONFIG_UNIX",
    "CONFIG_PACKET", "CONFIG_TMPFS", "CONFIG_BINFMT_ELF")

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

class Preflight(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "bundle"
        self.root.mkdir()
        self.module = self.root / "lib/modules" / RELEASE / "kernel/drivers/net/dummy.ko"
        self.module.parent.mkdir(parents=True)
        code = ('__attribute__((section(".modinfo"), used)) static const char v[] = '
                '"vermagic=' + RELEASE + ' SMP mod_unload aarch64";\n'
                'int init_module(void) { return 0; }\n')
        subprocess.run(["clang", "--target=aarch64-linux-gnu", "-c", "-x", "c",
                        "-o", str(self.module), "-"], input=code.encode(),
                       capture_output=True, check=True)
        self.dep = self.module.parents[3] / "modules.dep"
        self.dep.write_text("kernel/drivers/net/dummy.ko:\n")
        filemap = {
            "image": "boot/Image",
            "config": "boot/kernel.config",
            "module_symvers": "boot/Module.symvers",
            "kernel_release": "boot/kernel.release",
            "oneli_dtb": "boot/oneli.dtb",
            "modules_directory": "lib/modules/" + RELEASE,
        }
        payloads = {
            "image": b"synthetic Image, only host preflight structural fixture",
            "config": ("\n".join(k + "=y" for k in BUILTIN) +
                       "\nCONFIG_MODULES=y\nCONFIG_DUMMY=m\n").encode(),
            "module_symvers": b"synthetic Module.symvers\n",
            "kernel_release": (RELEASE + "\n").encode(),
            "oneli_dtb": b"synthetic oneli DTB; never passed to QEMU",
        }
        for k, p in filemap.items():
            if k == "modules_directory":
                continue
            file = self.root / p
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(payloads[k])
        self.manifest = {
            "schema": "oneli-combined-kernel-build-v1",
            "repository": "https://github.com/Drzet/linux",
            "kernel_commit": SHA, "kernel_release": RELEASE,
            "build_id": "synthetic-fixture-attempt-1",
            "files": filemap,
            "sha256": {k: digest(self.root / p) for k, p in filemap.items()
                       if k != "modules_directory"},
            "modules_sha256": {"kernel/drivers/net/dummy.ko": digest(self.module)},
            "qemu_runtime_module": {
                "name": "dummy", "relative_path": "kernel/drivers/net/dummy.ko"},
            "qemu_virt_config": {
                "machine": "virt", "console": "ttyAMA0",
                "virtio_transport": "mmio", "root_disk": "virtio-blk",
                "network": "virtio-net", "root_fs": "ext4",
                "required_builtin": list(BUILTIN),
                "required_loadable": ["CONFIG_DUMMY"],
                "required_enabled": ["CONFIG_MODULES"]},
            "toolchain": {"compiler": "clang cross AArch64 synthetic",
                          "linker": "test fixture linker",
                          "build_command": "clang --target=aarch64-linux-gnu -c"},
            "commits": [{"original": SHA, "applied": SHA}],
            "evidence": {"modpost_completed": True, "oneli_dtb_compiled": True,
                         "phone_tested": False},
        }
        self.manifest["sha256"]["modules_dep"] = digest(self.dep)
        self.manifest_path = self.root / "manifests/combined-kernel-build-v1.json"
        self.manifest_path.parent.mkdir(parents=True)

    def check(self, ok):
        self.manifest_path.write_text(json.dumps(self.manifest))
        p = subprocess.run([sys.executable, str(SCRIPT),
                            "--bundle-root", str(self.root)],
                           capture_output=True, text=True)
        if ok:
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("PROJECT_QEMU_PREFLIGHT_PASS", p.stdout)
        else:
            self.assertNotEqual(p.returncode, 0, p.stdout)
            self.assertIn("PROJECT_QEMU_PREFLIGHT_FAILED", p.stderr)
        return p

    def test_valid_bundle_preflight_direct(self):
        self.check(True)

    def test_mismatched_release_module_fails_even_with_matching_hash(self):
        raw = self.module.read_bytes()
        replacement = b"6.12.992-combined-fixture-arm64"
        self.assertEqual(len(replacement), len(RELEASE.encode()))
        self.module.write_bytes(raw.replace(RELEASE.encode(), replacement))
        self.manifest["modules_sha256"]["kernel/drivers/net/dummy.ko"] = digest(self.module)
        self.assertIn("wrong-release module vermagic", self.check(False).stderr)

    def test_required_virtio_blk_not_builtin_fails(self):
        conf = self.root / self.manifest["files"]["config"]
        conf.write_text(conf.read_text().replace("CONFIG_VIRTIO_BLK=y", "CONFIG_VIRTIO_BLK=m"))
        self.manifest["sha256"]["config"] = digest(conf)
        self.assertIn("CONFIG_VIRTIO_BLK is not built", self.check(False).stderr)

    def test_required_loadable_module_builtin_rejected(self):
        conf = self.root / self.manifest["files"]["config"]
        conf.write_text(conf.read_text().replace("CONFIG_DUMMY=m", "CONFIG_DUMMY=y"))
        self.manifest["sha256"]["config"] = digest(conf)
        self.assertIn("CONFIG_DUMMY must be an actual loadable module", self.check(False).stderr)

    def test_missing_module_symvers_fails(self):
        (self.root / self.manifest["files"]["module_symvers"]).unlink()
        self.assertIn("artifact path", self.check(False).stderr)

    def test_tampered_image_fails(self):
        (self.root / "boot/Image").write_bytes(b"wrong kernel binary")
        self.assertIn("SHA256 mismatch", self.check(False).stderr)

    def test_missing_modules_dep_fails(self):
        self.dep.unlink()
        self.assertIn("artifact path", self.check(False).stderr)

    def test_source_symlink_in_modules_fails(self):
        (self.dep.parent / "build").symlink_to("/unrelated/kernel/build")
        self.assertIn("installed modules contain", self.check(False).stderr)

    def test_incomplete_build_identity_fails(self):
        self.manifest["build_id"] = None
        self.assertIn("unknown build ID", self.check(False).stderr)

    def test_missing_config_declaration_fails(self):
        self.manifest["qemu_virt_config"]["required_builtin"].remove("CONFIG_VIRTIO_NET")
        self.assertIn("omits mandatory QEMU", self.check(False).stderr)

    def test_boot_oneli_dtb_does_not_become_qemu_dtb(self):
        self.check(True)
        self.assertNotIn("oneli_dtb_path", self.manifest["qemu_virt_config"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
