#!/usr/bin/env python3
"""Positive/negative synthetic newc fixtures; real ELF and QEMU tested separately in CI."""
import importlib.util
from pathlib import Path
import stat
import struct
import tempfile
import unittest

source = Path(__file__).resolve().parents[2] / "scripts" / "build-native-diag.py"
spec = importlib.util.spec_from_file_location("native_diag", source)
diag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diag)

def synthetic_arm64_static_elf():
    data = bytearray(120)
    data[:6] = b"\x7fELF\x02\x01"
    struct.pack_into("<H", data, 18, 183)
    struct.pack_into("<Q", data, 32, 64)
    struct.pack_into("<H", data, 54, 56)
    struct.pack_into("<H", data, 56, 1)
    struct.pack_into("<I", data, 64, 1)  # PT_LOAD, not PT_INTERP
    return bytes(data)

def entries():
    return [
        diag.record("tmp", "dir", mode=0o1777),
        diag.record("sys", "dir"),
        diag.record("run", "dir"),
        diag.record("proc", "dir"),
        diag.record("init", "file", b"#!/bin/sh\n"),
        diag.record("dev/null", "char", mode=0o666, major=1, minor=3),
        diag.record("dev/console", "char", mode=0o600, major=5, minor=1),
        diag.record("dev", "dir"),
        diag.record("bin/sh", "link", b"busybox", 0o777),
        diag.record("bin/busybox", "file", synthetic_arm64_static_elf()),
        diag.record("bin", "dir"),
    ]

class NativeDiagFixtureTests(unittest.TestCase):
    def test_static_elf_accepts_arm64(self):
        diag.assert_elf_static_arm64(synthetic_arm64_static_elf())

    def test_static_elf_rejects_other_arch(self):
        wrong = bytearray(synthetic_arm64_static_elf())
        struct.pack_into("<H", wrong, 18, 62)  # x86_64
        with self.assertRaisesRegex(ValueError, "AArch64"):
            diag.assert_elf_static_arm64(wrong)

    def test_static_elf_rejects_dynamic_interpreter(self):
        wrong = bytearray(synthetic_arm64_static_elf())
        struct.pack_into("<I", wrong, 64, 3)  # PT_INTERP
        with self.assertRaisesRegex(ValueError, "PT_INTERP"):
            diag.assert_elf_static_arm64(wrong)

    def test_newc_stable_and_owned(self):
        blob = diag.archive(entries())
        self.assertEqual(blob, diag.archive(list(reversed(entries()))))
        found = diag.unpack(blob)
        names = [x[0] for x in found]
        self.assertEqual(names, sorted(names))
        self.assertEqual(found[0][0], "bin")
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / "test.cpio"
            raw.write_bytes(blob)
            files, result = diag.validate_archive(raw)
            self.assertTrue(stat.S_ISREG(files["init"][0]))
            self.assertEqual(len(result), len(entries()))

    def test_duplicate_names_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "duplicate.cpio"
            p.write_bytes(diag.archive(entries() + [diag.record("init", "file", b"dup")]))
            with self.assertRaisesRegex(ValueError, "unique"):
                diag.validate_archive(p)

    def test_malformed_device_rejected(self):
        bad = [diag.record("dev/console", "char", mode=0o600, major=3, minor=1)
               if x[0] == "dev/console" else x for x in entries()]
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.cpio"
            p.write_bytes(diag.archive(bad))
            with self.assertRaisesRegex(ValueError, "bad /dev/console"):
                diag.validate_archive(p)

    def test_nondeterministic_time_rejected(self):
        b = bytearray(diag.archive(entries()))
        # First 110-byte newc header: mtime is field #6 at offset 6+5*8.
        b[46:54] = b"00000001"
        with self.assertRaisesRegex(ValueError, "metadata"):
            diag.unpack(bytes(b))

    def test_truncated_payload_rejected(self):
        b = diag.archive(entries())
        with self.assertRaises(ValueError):
            diag.unpack(b[:120])

if __name__ == "__main__":
    unittest.main(verbosity=2)
