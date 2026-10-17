#!/usr/bin/env python3
"""Synthetic v4 boot/vendor_boot roundtrip + negative integrity tests."""
import hashlib
import json
import subprocess
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROG = ROOT / "scripts" / "oneli_boot_v4_layout.py"
PAGE = 4096


def padded(v):
    return v + bytes((-len(v)) % PAGE)


def sample_pair(tmp):
    k, ram, vr, bootcfg = b"\x04\x22\x4d\x18KERNEL", b"\x1f\x8bRAMDISK", b"\x1f\x8bVENDOR", b"example.key = 1\n"
    bh = bytearray(PAGE)
    bh[:8] = b"ANDROID!"
    struct.pack_into("<II", bh, 8, len(k), len(ram))
    struct.pack_into("<II", bh, 20, 1584, 0)
    struct.pack_into("<I", bh, 40, 4)
    boot = bytes(bh) + padded(k) + padded(ram) + bytes(32)
    vh = bytearray(PAGE)
    vh[:8] = b"VNDRBOOT"
    struct.pack_into("<II", vh, 8, 4, PAGE)
    struct.pack_into("<I", vh, 24, len(vr))
    struct.pack_into("<II", vh, 2096, 2128, 40)
    struct.pack_into("<IIII", vh, 2112, 108, 1, 108, len(bootcfg))
    fdt = b"\xd0\x0d\xfe\xed" + (40).to_bytes(4, "big") + bytes(32)
    table = struct.pack("<III32s16I", len(vr), 0, 1,
                        b"oneli-platform" + bytes(18), *([0]*16))
    vendor = (bytes(vh) + padded(vr) + padded(fdt) +
              padded(table) + padded(bootcfg) + bytes(48))
    bp, vp = tmp/"boot.img", tmp/"vendor_boot.img"
    bp.write_bytes(boot)
    vp.write_bytes(vendor)
    return bp, vp, boot, vendor


class TestV4(unittest.TestCase):
    def invoke(self, *args, expected=0):
        p = subprocess.run([sys.executable, str(PROG), *map(str, args)],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, expected, p.stdout + "\n" + p.stderr)
        return p

    def test_inspect_roundtrip_and_explicit_candidate(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            bp, vp, original_boot, original_vendor = sample_pair(root)
            result = json.loads(self.invoke("roundtrip", bp, vp).stdout)
            self.assertTrue(result["identity_roundtrip"])
            self.assertEqual(result["boot"]["sha256"],
                             hashlib.sha256(original_boot).hexdigest())
            self.assertEqual(result["vendor_boot"]["sha256"],
                             hashlib.sha256(original_vendor).hexdigest())
            self.assertEqual(result["vendor_boot"]["dtb_fdt_chunks"][0]["bytes"], 40)
            self.assertEqual(result["vendor_boot"]["ramdisk_table"][0]["type"], 1)
            files = {}
            for name, content in [
                ("kernel", b"mainline kernel"), ("initramfs", b"new initramfs"),
                ("dtb", bytes.fromhex("d00dfeed") + (40).to_bytes(4, "big") + bytes(32)), ("vendor_ramdisk", b"explicit vendor ramdisk"),
                ("bootconfig", b"custom.key = 3\n")]:
                path = root / name
                path.write_bytes(content)
                files[name] = path
            header = root / "header.json"
            header.write_text(json.dumps({
                "purpose": "structural-only", "phone_boot_validated": False,
                "os_version_raw": 0, "kernel_addr": 0x8000,
                "ramdisk_addr": 0x1000000, "tags_addr": 0x100,
                "dtb_addr": 0x1f00000}))
            descriptor = root / "table.json"
            descriptor.write_text(json.dumps(
                {"name": "new-platform", "type": 1, "board_id": [0]*16}))
            self.invoke("prototype", bp, vp, "--out-dir", root/"out",
                        "--kernel", files["kernel"],
                        "--initramfs", files["initramfs"],
                        "--dtb", files["dtb"],
                        "--vendor-ramdisk", files["vendor_ramdisk"],
                        "--bootconfig", files["bootconfig"],
                        "--ramdisk-descriptor", descriptor,
                        "--header-inputs", header,
                        "--cmdline", "console=ttyMSM0",
                        "--vendor-cmdline", "custom=1",
                        "--vendor-name", "testoneli")
            candidate = json.loads((root/"out/candidate-layout.json").read_text())
            self.assertFalse(candidate["avb_signed"])
            self.assertEqual(candidate["boot"]["os_version_raw"], 0)
            self.assertEqual(candidate["vendor_boot"]["kernel_addr_raw"], 0x8000)
            self.assertEqual(candidate["vendor_boot"]["ramdisk_addr_raw"], 0x1000000)
            self.assertEqual(candidate["vendor_boot"]["tags_addr_raw"], 0x100)
            self.assertEqual(candidate["vendor_boot"]["dtb_addr_raw"], 0x1f00000)
            self.assertEqual(candidate["validation_stages"]["independent_aosp_parser"],
                             "not-tested")
            self.assertFalse(candidate["flash_tested"])
            self.assertEqual(candidate["boot"]["sections"][1]["bytes"], 15)
            self.assertEqual(candidate["vendor_boot"]["ramdisk_table"][0]["name"],
                             "new-platform")
            self.assertEqual(candidate["vendor_boot"]["bootconfig_keys"], ["custom.key"])
            self.assertNotEqual((root/"out/boot-candidate.UNSIGNED.img").read_bytes(),
                                original_boot)
            self.assertNotEqual((root/"out/vendor_boot-candidate.UNSIGNED.img").read_bytes(),
                                original_vendor)

    def test_corrupt_header_and_bad_entry(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            bp, vp, _, _ = sample_pair(root)
            damaged = bytearray(vp.read_bytes())
            struct.pack_into("<I", damaged, 2120, 64)
            vp.write_bytes(damaged)
            p = subprocess.run([sys.executable, str(PROG), "inspect", str(bp), str(vp)],
                               capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("invalid vendor ramdisk table", p.stderr)

    def test_two_unpadded_oneli_base_fdts_and_exact_boundaries(self):
        """Regression: actual reference second FDT begins at byte 479481."""
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            bp, vp, _, vendor = sample_pair(root)
            one_size = 479481
            magic = bytes.fromhex("d00dfeed")
            one = magic + one_size.to_bytes(4, "big") + b"A" * (one_size - 8)
            two = magic + one_size.to_bytes(4, "big") + b"B" * (one_size - 8)
            unpadded = one + two
            self.assertEqual(len(unpadded), 958962)
            old_ram_bytes = vendor[PAGE:2 * PAGE]
            table = vendor[3 * PAGE:4 * PAGE]
            cfg = vendor[4 * PAGE:5 * PAGE]
            vh = bytearray(vendor[:PAGE])
            struct.pack_into("<I", vh, 2100, len(unpadded))
            fixed_vendor = (bytes(vh) + old_ram_bytes + padded(unpadded) +
                            table + cfg)
            vp.write_bytes(fixed_vendor)
            parsed = json.loads(self.invoke("roundtrip", bp, vp).stdout)
            chunks = parsed["vendor_boot"]["dtb_fdt_chunks"]
            self.assertEqual(len(chunks), 2)
            self.assertEqual([x["relative_offset"] for x in chunks], [0, 479481])
            self.assertEqual([x["bytes"] for x in chunks], [479481, 479481])
            self.assertEqual(chunks[1]["sha256"], hashlib.sha256(two).hexdigest())
            self.assertEqual(parsed["vendor_boot"]["dtb_unparsed_bytes"], 0)

            # A missing byte in the second image must fail rather than
            # silently suppress the second candidate.
            corrupt = bytearray(fixed_vendor)
            corrupt[2 * PAGE + 479481] = 0x41
            vp.write_bytes(corrupt)
            err = subprocess.run([sys.executable, str(PROG), "inspect", str(bp),
                                  str(vp)], capture_output=True, text=True)
            self.assertNotEqual(err.returncode, 0)
            self.assertIn("unparsed nonzero bytes", err.stderr)

    def test_header_input_validation(self):
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("oneli_boot_v4_layout", PROG)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "header.json"
            path.write_text(json.dumps({
                "purpose": "structural-only", "phone_boot_validated": False,
                "os_version_raw": 0, "kernel_addr": 0x8000,
                "ramdisk_addr": 0x1000000, "tags_addr": 0x100,
                "dtb_addr": 0x1f00000}))
            self.assertEqual(module.native_header_inputs(path)["dtb_addr"], 0x1f00000)
            bad = json.loads(path.read_text())
            del bad["os_version_raw"]
            path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError, "missing required"):
                module.native_header_inputs(path)
            bad["os_version_raw"] = None
            path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError, "explicit unsigned"):
                module.native_header_inputs(path)

    def test_stock_reference_offset_equations(self):
        # Validates the verified VPU *metadata* without needing binary.
        ram, dtb, entry = 13335589, 958962, 108
        align = lambda n: (n + 4095) // 4096 * 4096
        self.assertEqual(4096 + align(ram), 13340672)
        self.assertEqual(4096 + align(ram) + align(dtb), 14303232)
        self.assertEqual(4096 + align(ram) + align(dtb) + align(entry), 14307328)


if __name__ == "__main__":
    unittest.main()
