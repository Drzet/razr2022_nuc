#!/usr/bin/env python3
"""Focused fail-closed regression tests for standalone host packaging."""
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "build_oneli_native_host_candidate.py"
spec = importlib.util.spec_from_file_location("native_host", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class NativeHostTests(unittest.TestCase):
    def test_empty_vendor_fragment_is_a_valid_newc(self):
        b = mod.newc_empty()
        self.assertEqual(len(b), 124)
        self.assertEqual(mod.newc_parse(b), {})
        with self.assertRaises(ValueError):
            mod.newc_parse(b[:-4])

    def test_reject_reference_header_without_explicit_structural_status(self):
        obj = json.loads((SOURCE.parent.parent / "configs" / "oneli-native-host-header-inputs-v1.json").read_text())
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "header.json"
            for key, value in (("phone_boot_validated", True), ("purpose", "reviewed-native"), ("signature_size", 4096), ("dtb_addr", None)):
                new = dict(obj)
                new[key] = value
                p.write_text(json.dumps(new))
                with self.assertRaises(ValueError, msg=key):
                    mod.header_inputs(p)

    def test_section_bounds_signature_policy(self):
        h = json.loads((SOURCE.parent.parent / "configs" / "oneli-native-host-header-inputs-v1.json").read_text())
        dtb = b"\xd0\x0d\xfe\xed" + struct.pack(">I", 64) + bytes(56)
        initrd = b"\x1f\x8b" + bytes(32)
        kernel = b"ARMK" * 1025
        vendor = b"\x1f\x8b" + bytes(32)
        a, b = mod.build(kernel, initrd, dtb, vendor, h)
        rep = mod.validate_structures(a, b, kernel, initrd, dtb, vendor, h)
        self.assertEqual(rep["boot"]["os_version_raw"], 0)
        self.assertEqual(rep["vendor_boot"]["fragment_table_entries"], 1)
        for offset, val in ((1580, 42), (16, 3)):
            corrupted = bytearray(a)
            struct.pack_into("<I", corrupted, offset, val)
            with self.assertRaises(ValueError):
                mod.validate_structures(corrupted, b, kernel, initrd, dtb, vendor, h)
        corrupted = bytearray(b)
        struct.pack_into("<I", corrupted, 2116, 2)
        with self.assertRaises(ValueError):
            mod.validate_structures(a, corrupted, kernel, initrd, dtb, vendor, h)

    def test_newc_malformed_and_path_traversal(self):
        original = mod.newc_empty()
        with self.assertRaises(ValueError):
            mod.newc_parse(b"BORK" + original)
        with self.assertRaises(ValueError):
            mod.check_simple("../../evil")
        with self.assertRaises(ValueError):
            mod.check_simple("/init")
        with self.assertRaises(ValueError):
            mod.check_simple("a//b")


if __name__ == "__main__":
    unittest.main()
