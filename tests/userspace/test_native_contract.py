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
            "module_symvers_path": "boot/Module.symvers",
            "dtb_path": "boot/oneli.dtb",
            "initramfs_path": "boot/initrd.img",
            "firmware_manifest_path": "manifests/firmware.json",
            "boot_packaging_manifest_path": "manifests/boot.json",
            "native_header_inputs_path": "manifests/explicit-native-header.json"
        }
        for k in ("image_path", "config_path", "module_symvers_path", "dtb_path"):
            p = self.root / self.paths[k]
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes((k + " synthetic fixture").encode())
        firmware = self.root / "firmware/fixture.bin"
        firmware.parent.mkdir()
        firmware.write_bytes(b"nonproprietary synthetic fixture")
        fw_manifest = {
            "schema_version": 2, "target_environment": "oneli_native",
            "assessment": "complete", "unknown_requirements": [],
            "required_files": [{"path": "fixture.bin", "sha256": hash_file(firmware),
                                "consumer": "synthetic-fixture", "in_initramfs": True}]
        }
        for k, val in (("firmware_manifest_path", fw_manifest),
                       ("boot_packaging_manifest_path", {
                           "schema": "oneli-native-boot-packaging-contract-v2",
                           "reference_images": {
                               "boot": {"header_version": 4, "header_bytes": 1584,
                                        "os_version_raw": None},
                               "vendor_boot": {"header_version": 4, "header_bytes": 2128,
                                               "page_bytes": 4096, "ramdisk_table_entries": 1,
                                               "ramdisk_table_entry_bytes": 108,
                                               "ramdisk_fragment_type": 1,
                                               "ramdisk_fragment_board_id_words": [0] * 16,
                                               "kernel_addr": 32768, "ramdisk_addr": 16777216,
                                               "tags_addr": 256, "dtb_addr": 32505856,
                                               "embedded_dtb_count": 2,
                                               "embedded_dtb_roots": [
                                                   {"relative_offset": 0},
                                                   {"relative_offset": 479481}]}},
                           "prototype": {"flash_recipe": False, "candidate_signed": False,
                                         "boot_tested": False, "native_ready": False,
                                         "hardware_accepted": False,
                                         "implicit_reference_placement_inheritance": False,
                                         "header_inputs_require_explicit_os_version": True,
                                         "header_inputs_fields":
                                         ["os_version_raw", "kernel_addr", "ramdisk_addr",
                                          "tags_addr", "dtb_addr", "purpose", "phone_boot_validated"],
                                         "requires_explicit_payload_paths": ["header-inputs"]},
                           "fixture": True}),
                       ("native_header_inputs_path", {
                           "os_version_raw": 0, "kernel_addr": 32768,
                           "ramdisk_addr": 16777216, "tags_addr": 256,
                           "dtb_addr": 32505856, "purpose": "structural-only",
                           "phone_boot_validated": False})):
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
            "schema_version": 3, "repository": "https://github.com/Drzet/linux",
            "target_environment": "oneli_native",
            "kernel_commit": "a" * 40, "kernel_release": RELEASE,
            **self.paths,
            "modules_directory": "lib/modules/" + RELEASE,
            "firmware_directory": "firmware",
            "sha256": {k: hash_file(self.root / v) for k, v in self.paths.items()},
            "modules_sha256": {self.mod_relative: hash_file(mod)},
            "initramfs_modules": [self.mod_relative],
            "zero_initramfs_modules_reason": None,
            "same_build": {
                "build_id": "synthetic-module-fixture",
                "kernel_commit": "a" * 40,
                "kernel_release": RELEASE,
                "config_sha256": hash_file(self.root / self.paths["config_path"]),
                "module_symvers_sha256": hash_file(self.root / self.paths["module_symvers_path"]),
                "image_sha256": hash_file(self.root / self.paths["image_path"])}
            
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
        self.assertIn("firmware manifest scope or version unresolved", self.check(False).stderr)

    def test_qemu_virt_empty_scoped_requirements(self):
        self.manifest["target_environment"] = "qemu_virt"
        for name in ("dtb_path", "boot_packaging_manifest_path", "native_header_inputs_path"):
            del self.manifest[name]
            del self.manifest["sha256"][name]
        self.manifest["firmware_directory"] = None
        self.manifest["initramfs_modules"] = []
        self.manifest["zero_initramfs_modules_reason"] = (
            "virtio and root drivers are assumed builtin in this synthetic target fixture")
        fw = self.root / self.paths["firmware_manifest_path"]
        fw.write_text(json.dumps({"schema_version": 2, "target_environment": "qemu_virt",
                                  "assessment": "complete", "unknown_requirements": [],
                                  "required_files": [], "zero_requirements_reason":
                                  "no proprietary or board-specific firmware required in synthetic virt profile"}))
        self.manifest["sha256"]["firmware_manifest_path"] = hash_file(fw)
        self.check(True)

    def test_qemu_forbids_oneli_dtb(self):
        self.manifest["target_environment"] = "qemu_virt"
        self.assertIn("oneli packaging forbidden", self.check(False).stderr)

    def test_empty_firmware_without_reason_rejected(self):
        fw = self.root / self.paths["firmware_manifest_path"]
        fw.write_text(json.dumps({"schema_version": 2, "target_environment": "oneli_native",
                                  "assessment": "complete", "unknown_requirements": [],
                                  "required_files": []}))
        self.manifest["sha256"]["firmware_manifest_path"] = hash_file(fw)
        self.assertIn("scope justification", self.check(False).stderr)

    def test_missing_same_build_rejected(self):
        self.manifest["same_build"]["module_symvers_sha256"] = "0" * 64
        self.assertIn("build provenance", self.check(False).stderr)

    def test_boot_reference_never_promoted_to_native_ready(self):
        self.manifest_path.write_text(json.dumps(self.manifest))
        r = subprocess.run([sys.executable, str(CHECKER), str(self.manifest_path),
                            "--artifact-root", str(self.root), "--output",
                            str(self.base / "result.json")], text=True, capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        p = json.loads((self.base / "result.json").read_text())["packaging"]
        self.assertTrue(p["structural_reference_audited"])
        self.assertFalse(p["native_composition_ready"])
        self.assertFalse(p["hardware_accepted"])

    def test_boot_v2_missing_header_rejected(self):
        self.manifest["native_header_inputs_path"] = None
        self.assertIn("relative path required", self.check(False).stderr)

    def test_boot_v2_null_os_version_rejected(self):
        path = self.root / self.paths["native_header_inputs_path"]
        header = json.loads(path.read_text())
        header["os_version_raw"] = None
        path.write_text(json.dumps(header))
        self.manifest["sha256"]["native_header_inputs_path"] = hash_file(path)
        self.assertIn("native header os_version_raw requires explicit", self.check(False).stderr)

    def test_boot_v1_manifest_rejected(self):
        path = self.root / self.paths["boot_packaging_manifest_path"]
        header = json.loads(path.read_text())
        header["schema"] = "oneli-native-boot-packaging-contract-v1"
        path.write_text(json.dumps(header))
        self.manifest["sha256"]["boot_packaging_manifest_path"] = hash_file(path)
        self.assertIn("Boot v2 reference contract required", self.check(False).stderr)

    def test_missing_firmware_in_initramfs_rejected(self):
        (self.initroot / "usr/lib/firmware/fixture.bin").unlink()
        self.make_initramfs()
        self.manifest["sha256"]["initramfs_path"] = hash_file(self.root / self.paths["initramfs_path"])
        self.assertIn("firmware missing from initramfs", self.check(False).stderr)

if __name__ == "__main__":
    unittest.main(verbosity=2)
