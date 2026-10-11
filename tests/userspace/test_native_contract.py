#!/usr/bin/env python3
"""Host-only fixtures; test the REAL static gate and reject compromised native inputs."""
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[2]
CHECKER = PROJECT / "scripts/validate-native-kernel-inputs.py"
RELEASE = "6.12.999-fixture-arm64"

def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, **kwargs)

class NativeContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "root"
        self.root.mkdir()
        self.release = RELEASE
        self.mod_relative = "kernel/fixture.ko"
        mod = self.root / "lib/modules" / RELEASE / self.mod_relative
        mod.parent.mkdir(parents=True)
        code = ('__attribute__((section(".modinfo"), used)) static const char v[] = '
                '"vermagic=' + RELEASE + ' SMP preempt mod_unload aarch64";\n'
                'int init_module(void) { return 0; }\n')
        run(["clang", "--target=aarch64-linux-gnu", "-c", "-x", "c",
             "-o", str(mod), "-"], input=code.encode())
        (mod.parents[1] / "modules.dep").write_text(self.mod_relative + ":\n")
        self.paths = {
            "image_path": "boot/Image",
            "config_path": "boot/kernel.config",
            "dtb_path": "boot/oneli.dtb",
            "initramfs_path": "boot/initrd.img",
            "firmware_manifest_path": "manifests/firmware.json",
            "boot_packaging_manifest_path": "manifests/boot.json"
        }
        for k in ("image_path", "config_path", "dtb_path"):
            p = self.root / self.paths[k]
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes((k + " synthetic fixture").encode())
        firmware = self.root / "firmware/fixture.bin"
        firmware.parent.mkdir()
        firmware.write_bytes(b"nonproprietary synthetic fixture")
        fw_manifest = {
            "schema_version": 1, "status": "complete", "unknown_requirements": [],
            "required_files": [{"path": "fixture.bin", "sha256": hash_file(firmware),
                                "consumer": "synthetic-fixture", "in_initramfs": True}]
        }
        for k, val in (("firmware_manifest_path", fw_manifest),
                       ("boot_packaging_manifest_path", {"status": "verified", "fixture": True})):
            p = self.root / self.paths[k]
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(val))
        self.initroot = self.base / "initroot"
        embedded_mod = self.initroot / "usr/lib/modules" / RELEASE / self.mod_relative
        embedded_mod.parent.mkdir(parents=True)
        embedded_mod.write_bytes(mod.read_bytes())
        embedded_fw = self.initroot / "usr/lib/firmware/fixture.bin"
        embedded_fw.parent.mkdir(parents=True)
        embedded_fw.write_bytes(firmware.read_bytes())
        self.make_initramfs()
        self.manifest = {
            "schema_version": 2, "repository": "https://github.com/Drzet/linux",
            "kernel_commit": "a" * 40, "kernel_release": RELEASE,
            **self.paths,
            "modules_directory": "lib/modules/" + RELEASE,
            "firmware_directory": "firmware",
            "sha256": {k: hash_file(self.root / v) for k, v in self.paths.items()},
            "modules_sha256": {self.mod_relative: hash_file(mod)},
            "initramfs_modules": [self.mod_relative]
        }
        self.manifest["sha256"]["modules_dep"] = hash_file(mod.parents[1] / "modules.dep")
        self.manifest_path = self.base / "native.json"

    def make_initramfs(self):
        names = [p.relative_to(self.initroot).as_posix() for p in sorted(self.initroot.rglob("*"))]
        r = run(["cpio", "--quiet", "-o", "-H", "newc"],
                input=("\n".join(names) + "\n").encode(), cwd=self.initroot)
        (self.root / self.paths["initramfs_path"]).write_bytes(gzip.compress(r.stdout))

    def check(self, expect_ok):
        self.manifest_path.write_text(json.dumps(self.manifest))
        result = subprocess.run([sys.executable, str(CHECKER), str(self.manifest_path),
                                 "--artifact-root", str(self.root)],
                                text=True, capture_output=True)
        if expect_ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("NATIVE_ARTIFACT_STATIC_PASS", result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("NATIVE_ARTIFACT_GATE_FAILED", result.stderr)
        return result

    def test_valid_synthetic_contract(self):
        self.check(True)

    def test_tampered_image_rejected(self):
        (self.root / self.paths["image_path"]).write_bytes(b"TAMPER")
        self.assertIn("SHA256 mismatch", self.check(False).stderr)

    def test_mismatched_vermagic_rejected_even_with_updated_hash(self):
        mod = self.root / self.manifest["modules_directory"] / self.mod_relative
        data = mod.read_bytes().replace(RELEASE.encode(), b"6.12.000-fixture-arm64")
        self.assertNotEqual(data, b"")
        mod.write_bytes(data)
        self.manifest["modules_sha256"][self.mod_relative] = hash_file(mod)
        self.assertIn("vermagic mismatch", self.check(False).stderr)

    def test_initramfs_module_tamper_detected(self):
        embedded = self.initroot / "usr/lib/modules" / RELEASE / self.mod_relative
        embedded.write_bytes(b"MODIFIED")
        self.make_initramfs()
        self.manifest["sha256"]["initramfs_path"] = hash_file(self.root / self.paths["initramfs_path"])
        self.assertIn("SHA256 mismatch", self.check(False).stderr)

    def test_unresolved_firmware_rejected(self):
        p = self.root / self.paths["firmware_manifest_path"]
        p.write_text("{}")
        self.manifest["sha256"]["firmware_manifest_path"] = hash_file(p)
        self.assertIn("firmware requirements unresolved", self.check(False).stderr)

    def test_missing_firmware_in_initramfs_rejected(self):
        (self.initroot / "usr/lib/firmware/fixture.bin").unlink()
        self.make_initramfs()
        self.manifest["sha256"]["initramfs_path"] = hash_file(self.root / self.paths["initramfs_path"])
        self.assertIn("firmware missing from initramfs", self.check(False).stderr)

if __name__ == "__main__":
    unittest.main(verbosity=2)
