#!/usr/bin/env python3
"""Offline-only synthetic tests for the Motorola ABL PE/RVA literal decoder.

Do not download stock firmware or execute the analyzer's main() here.
"""
import importlib.util
import struct
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts" / "analyze-oneli-mbm-placement-constants.py"
spec = importlib.util.spec_from_file_location("oneli_mbm_constants", SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def synthetic_pe():
    """Two AArch64 sections where both RVA bases differ from raw offsets."""
    data = bytearray(0x1200)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3c, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HH", data, 0x84, 0xaa64, 2)
    struct.pack_into("<H", data, 0x94, 0xf0)
    start = 0x80 + 24 + 0xf0
    for i, (name, rva, raw, size) in enumerate([
        (b".text", 0x2000, 0x400, 0x200),
        (b".data", 0x4000, 0x900, 0x200),
    ]):
        at = start + i * 40
        data[at:at+len(name)] = name
        struct.pack_into("<IIII", data, at+8, size, rva, size, raw)
    return data


class TestLiteralDecoder(unittest.TestCase):
    def setUp(self):
        self.data = synthetic_pe()
        self.sections = mod.pe_sections(self.data)

    def test_nonidentity_rva_in_both_sections(self):
        self.assertEqual(mod.rva_to_raw(self.data, self.sections, 0x2010), 0x410)
        self.assertEqual(mod.rva_to_raw(self.data, self.sections, 0x4040), 0x940)
        self.assertEqual([x["name"] for x in self.sections], [".text", ".data"])

    def test_full_uefi_variable_names_and_end_code_units(self):
        for rva, name in [(0x2020, "KernelBaseAddr"), (0x4040, "KernelSize")]:
            encoded = (name + "\0").encode("utf-16le")
            offset = mod.rva_to_raw(self.data, self.sections, rva, len(encoded))
            self.data[offset:offset+len(encoded)] = encoded
            self.assertEqual(mod.literal(self.data, self.sections, rva, utf16=True), name)

    def test_utf16_non_ascii_and_odd_byte_alignment(self):
        offset = mod.rva_to_raw(self.data, self.sections, 0x2021)
        self.data[offset:offset+6] = "AΩ\0".encode("utf-16le")
        self.assertEqual(mod.literal(self.data, self.sections, 0x2021, utf16=True), "AΩ")

    def test_unterminated_utf16_fails(self):
        off = mod.rva_to_raw(self.data, self.sections, 0x2020)
        self.data[off:off+6] = "ABC".encode("utf-16le")
        with self.assertRaisesRegex(ValueError, "unterminated UTF-16"):
            mod.literal(self.data, self.sections, 0x2020, maxbytes=6, utf16=True)

    def test_section_boundary_limits_utf16(self):
        off = mod.rva_to_raw(self.data, self.sections, 0x21fc, 4)
        self.data[off:off+4] = b"A\0B\0"
        with self.assertRaisesRegex(ValueError, "unterminated UTF-16"):
            mod.literal(self.data, self.sections, 0x21fc, utf16=True)

    def test_literal_ascii(self):
        off = mod.rva_to_raw(self.data, self.sections, 0x4080)
        self.data[off:off+11] = b"/kernel\0xyz"
        self.assertEqual(mod.literal(self.data, self.sections, 0x4080), "/kernel")

    def test_numeric_little_endian_read_from_rva(self):
        off = mod.rva_to_raw(self.data, self.sections, 0x2040, 4)
        struct.pack_into("<I", self.data, off, 0x06400000)
        self.assertEqual(struct.unpack("<I", mod.read_rva(self.data, self.sections, 0x2040, 4))[0], 0x06400000)

    def test_virtual_or_gapped_rva_rejected(self):
        for rva in (0x1000, 0x2200, 0x2fff, 0x3fff, 0x4200):
            with self.subTest(rva=rva), self.assertRaisesRegex(ValueError, "unmapped"):
                mod.rva_to_raw(self.data, self.sections, rva)

    def test_cross_section_read_rejected(self):
        with self.assertRaisesRegex(ValueError, "unmapped"):
            mod.read_rva(self.data, self.sections, 0x21ff, 2)

    def test_invalid_pe_signature_or_machine(self):
        corrupt = bytearray(self.data)
        corrupt[0x80:0x84] = b"XXXX"
        with self.assertRaises(ValueError):
            mod.pe_sections(corrupt)
        corrupt = bytearray(self.data)
        struct.pack_into("<H", corrupt, 0x84, 0x8664)
        with self.assertRaises(ValueError):
            mod.pe_sections(corrupt)

    def test_truncated_raw_data_rejected(self):
        corrupt = self.data[:0xa00]
        with self.assertRaisesRegex(ValueError, "truncated"):
            mod.pe_sections(corrupt)

    def test_saved_real_section_bounds(self):
        # Actual section numbers from accepted run 38808611568, artifact 12007666834.
        saved = [
            (".text", 0x1000, 0x1000, 978944),
            (".data", 0xf0000, 0xf0000, 102400),
            (".reloc", 0x109000, 0x109000, 4096),
        ]
        rvas = list(mod.OFFSETS.values()) + [0xeeb20]
        for rva in rvas:
            found = [s for s in saved if s[1] <= rva < s[1] + s[3]]
            self.assertEqual(len(found), 1, hex(rva))
            self.assertEqual(found[0][0], ".text")
            self.assertEqual(found[0][1], found[0][2])
        self.assertEqual(max(rvas), 0xeeb20)

if __name__ == "__main__":
    unittest.main()
