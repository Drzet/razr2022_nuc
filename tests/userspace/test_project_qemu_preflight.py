#!/usr/bin/env python3
"""Execute the REAL Boot bundle preflight on synthetic AArch64 module artifacts."""
import copy
import hashlib
import json
import shutil
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

    def make_boot_producer_bundle(self):
        """Synthesize Boot's actual artifact-root tree and preflight JSON, not our old layout."""
        dest = Path(self.tmp.name) / "boot-producer"
        dest.mkdir()
        files = {"Image": "boot/Image", "kernel.config": "boot/kernel.config",
                 "Module.symvers": "boot/Module.symvers",
                 "kernel.release": "boot/kernel.release",
                 "sm8475-motorola-oneli.dtb": "boot/oneli.dtb"}
        for name, old in files.items():
            shutil.copy2(self.root / old, dest / name)
        shutil.copy2(dest / "kernel.config", dest / ".config")
        shutil.copytree(self.root / ("lib/modules/" + RELEASE),
                        dest / ("modules/" + RELEASE))
        logs = dest / "logs"
        logs.mkdir()
        (logs / "toolchain.txt").write_text("clang AArch64 cross synthetic fixture\n")
        fw = {"schema_version": 2, "target_environment": "qemu_virt",
              "assessment": "complete", "required_files": [], "unknown_requirements": [],
              "zero_requirements_reason":
              "No proprietary Qualcomm firmware used by this synthetic QEMU virt profile"}
        (dest / "firmware-qemu-virt.json").write_text(json.dumps(fw))
        original = self.manifest
        p = {
            "schema_version": 3, "repository": "https://github.com/Drzet/linux",
            "target_environment": "qemu_virt",
            "kernel_commit": SHA, "kernel_release": RELEASE,
            "same_build": {
                "build_id": original["build_id"],
                "kernel_commit": SHA, "kernel_release": RELEASE,
                "image_sha256": digest(dest / "Image"),
                "config_sha256": digest(dest / "kernel.config"),
                "module_symvers_sha256": digest(dest / "Module.symvers")},
            "image_path": "Image", "config_path": "kernel.config",
            "module_symvers_path": "Module.symvers",
            "modules_directory": "modules/" + RELEASE,
            "initramfs_path": None, "initramfs_modules": [],
            "firmware_manifest_path": "firmware-qemu-virt.json",
            "dtb_path": None, "boot_packaging_manifest_path": None,
            "modules_sha256": original["modules_sha256"],
            "qemu_runtime_module": original["qemu_runtime_module"],
            "sha256": {
                "image_path": digest(dest / "Image"),
                "config_path": digest(dest / "kernel.config"),
                "module_symvers_path": digest(dest / "Module.symvers"),
                "initramfs_path": None,
                "firmware_manifest_path": digest(dest / "firmware-qemu-virt.json"),
                "modules_dep": digest(dest / ("modules/" + RELEASE + "/modules.dep"))},
        }
        (dest / "qemu-native-inputs.v3.preflight.json").write_text(json.dumps(p))
        (dest / "module-sha256.json").write_text(json.dumps(original["modules_sha256"]))
        srcs = [{"original": SHA, "result": SHA} for _ in range(7)]
        b = {"schema": "oneli-combined-build-manifest-v1",
             "kernel_commit": SHA, "kernel_release": RELEASE,
             "build_id": original["build_id"],
             "module_tree": "modules/" + RELEASE,
             "module_count": len(original["modules_sha256"]),
             "module_sha256_manifest": "module-sha256.json",
             "files_sha256": {x: digest(dest / x) for x in files},
             "modules_dep_sha256": p["sha256"]["modules_dep"],
             "qemu_runtime_module": "dummy",
             "source_config_project_commit":
             "6a80ab302e9e2cf5aaf3ca0187baec106e985ade",
             "replayed_commits": srcs,
             "scope": "source build and static FDT schema only; phone untested"}
        (dest / "build-manifest.json").write_text(json.dumps(b))
        self.refresh_boot_checksum_list(dest)
        return dest

    @staticmethod
    def refresh_boot_checksum_list(root):
        lines = []
        for p in sorted(root.rglob("*")):
            if p.is_file() and p.name != "SHA256SUMS":
                lines.append(digest(p) + "  " + p.relative_to(root).as_posix() + "\n")
        (root / "SHA256SUMS").write_text("".join(lines))

    def normalize(self, boot, success):
        adapter = SCRIPT.with_name("normalize-boot-combined-bundle.py")
        target = Path(self.tmp.name) / "normalized"
        p = subprocess.run([sys.executable, str(adapter),
                            "--boot-root", str(boot),
                            "--output-root", str(target)],
                           capture_output=True, text=True)
        if success:
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("BOOT_COMBINED_BUNDLE_NORMALIZED", p.stdout)
        else:
            self.assertNotEqual(p.returncode, 0, p.stdout)
            self.assertIn("BOOT_BUNDLE_ADAPTER_FAILED", p.stderr)
        return target, p

    def test_boot_authoritative_bundle_normalizes_and_preflights(self):
        boot = self.make_boot_producer_bundle()
        target, result = self.normalize(boot, True)
        q = subprocess.run([sys.executable, str(SCRIPT),
                            "--bundle-root", str(target)],
                           capture_output=True, text=True)
        self.assertEqual(q.returncode, 0, q.stderr)
        self.assertIn("PROJECT_QEMU_PREFLIGHT_PASS", q.stdout)
        self.assertEqual((target / "producer-record/build-manifest.json").read_bytes(),
                         (boot / "build-manifest.json").read_bytes())

    def test_boot_bundle_rejects_tampered_image(self):
        boot = self.make_boot_producer_bundle()
        (boot / "Image").write_bytes(b"tampered upstream kernel bytes")
        self.assertIn("SHA256SUMS mismatch", self.normalize(boot, False)[1].stderr)

    def test_boot_bundle_rejects_hidden_config_drift(self):
        boot = self.make_boot_producer_bundle()
        (boot / ".config").write_text("CONFIG_MODULES=n\n")
        self.refresh_boot_checksum_list(boot)
        self.assertIn("hidden .config differs", self.normalize(boot, False)[1].stderr)

    def test_boot_bundle_rejects_invented_prebuilt_initramfs(self):
        boot = self.make_boot_producer_bundle()
        path = boot / "qemu-native-inputs.v3.preflight.json"
        data = json.loads(path.read_text())
        data["initramfs_path"] = "fake-prebuilt-initramfs.img"
        path.write_text(json.dumps(data))
        self.refresh_boot_checksum_list(boot)
        self.assertIn("nonexistent initramfs", self.normalize(boot, False)[1].stderr)

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

    def test_prepare_shell_calls_real_preflight_before_rootfs_io(self):
        self.check(True)
        stage = SCRIPT.with_name("prepare-project-qemu.sh")
        output = Path(self.tmp.name) / "would-write-here"
        p = subprocess.run(["bash", str(stage), str(self.root),
                            str(self.root / "unavailable-rootfs.tar.zst"),
                            "0" * 64, str(output)],
                           capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("PROJECT_QEMU_PREFLIGHT_PASS", p.stdout)
        self.assertFalse(output.exists(), "stage wrote files before rootfs hash check")

    def test_prepare_shell_blocks_wrong_release_before_writing(self):
        raw = self.module.read_bytes()
        self.module.write_bytes(raw.replace(RELEASE.encode(),
                          b"6.12.992-combined-fixture-arm64"))
        self.manifest["modules_sha256"]["kernel/drivers/net/dummy.ko"] = digest(self.module)
        self.manifest_path.write_text(json.dumps(self.manifest))
        stage = SCRIPT.with_name("prepare-project-qemu.sh")
        output = Path(self.tmp.name) / "must-not-write-here"
        p = subprocess.run(["bash", str(stage), str(self.root),
                            str(self.root / "unavailable-rootfs.tar.zst"),
                            "0" * 64, str(output)],
                           capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("PROJECT_QEMU_PREFLIGHT_FAILED", p.stderr)
        self.assertIn("wrong-release module vermagic", p.stderr)
        self.assertFalse(output.exists())

    def test_boot_oneli_dtb_does_not_become_qemu_dtb(self):
        self.check(True)
        self.assertNotIn("oneli_dtb_path", self.manifest["qemu_virt_config"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
