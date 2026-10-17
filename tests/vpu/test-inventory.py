#!/usr/bin/env python3
"""Synthetic tests for the *read-only* stock firmware inventory tool.

Fixtures contain fabricated headers/text only, no proprietary firmware bytes.
"""
import importlib.util
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "oneli_firmware_inventory", ROOT / "scripts/inventory-oneli-firmware.py")
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    def test_fake_android_dtbo_candidate(self):
        dt = b"\xd0\x0d\xfe\xed"  # four placeholder bytes; NOT a valid FDT
        header = struct.pack(">8I", inventory.DTBO_MAGIC, 68, 32, 32, 1, 32, 4096, 0)
        entry = struct.pack(">8I", 4, 64, 530, 2, 0, 0, 0, 0)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "fake-stock.zip"
            with zipfile.ZipFile(path, "w") as zf:
                zf.writestr("dtbo.img", header + entry + dt)
            result = inventory.inventory_zip(path)
            self.assertEqual(result["dtbo_candidates"][0]["entry_count"], 1)
            self.assertEqual(result["dtbo_candidates"][0]["entries"][0]["id"], 530)
            self.assertEqual(result["dtbo_candidates"][0]["entries"][0]["rev"], 2)
            self.assertEqual(result["entries"][0]["name"], "dtbo.img")

    def test_reject_out_of_bounds_dtbo_table_and_entry(self):
        magic = inventory.DTBO_MAGIC
        # Table claims 2 entries but image holds only one entry.
        truncated = struct.pack(">8I", magic, 64, 32, 32, 2, 32, 4096, 0)
        self.assertEqual(inventory.dtbo_header(truncated + b"\0" * 32)["state"],
                         "invalid_dtbo_header")
        # Single entry extends beyond the advertised image size.
        header = struct.pack(">8I", magic, 68, 32, 32, 1, 32, 4096, 0)
        overflow = struct.pack(">8I", 8, 64, 530, 2, 0, 0, 0, 0)
        self.assertEqual(inventory.dtbo_header(header + overflow + b"\0" * 4)["state"],
                         "invalid_dtbo_entry_bounds")
        # Entry overlaps the table itself.
        overlap = struct.pack(">8I", 4, 48, 530, 2, 0, 0, 0, 0)
        self.assertEqual(inventory.dtbo_header(header + overlap + b"\0" * 4)["state"],
                         "invalid_dtbo_entry_bounds")

    def test_fake_firmware_marker_and_digest(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "extracted"
            firmware = root / "vendor/firmware/vpu20_4v.mbn"
            firmware.parent.mkdir(parents=True)
            firmware.write_bytes(b"not firmware\0QC_IMAGE_VERSION_STRING=vfw.test\0")
            result = inventory.inventory_extracted(root)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["relative_path"],
                             "vendor/firmware/vpu20_4v.mbn")
            self.assertEqual(result[0]["qc_image_version_string"], "vfw.test")
            self.assertEqual(len(result[0]["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
