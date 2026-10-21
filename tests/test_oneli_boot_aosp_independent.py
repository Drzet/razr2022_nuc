#!/usr/bin/env python3
"""Independent pinned AOSP v4 mkbootimg/unpack_bootimg cross-check; synthetic only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from test_oneli_boot_v4_layout import sample_pair

ROOT = Path(__file__).resolve().parents[1]
OWN = ROOT / "scripts" / "oneli_boot_v4_layout.py"
AOSP = os.environ.get("ONELI_AOSP_MKBOOTIMG")


@unittest.skipUnless(AOSP, "AOSP source must be pinned in CI")
class TestIndependentAOSP(unittest.TestCase):
    def run_cmd(self, *args):
        p = subprocess.run([sys.executable, *map(str, args)],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + "\n" + p.stderr)
        return p.stdout

    def test_altered_payloads_and_independent_pack_unpack(self):
        aosp = Path(AOSP).resolve()
        pack, unpack = aosp / "mkbootimg.py", aosp / "unpack_bootimg.py"
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            bp, vp, _, _ = sample_pair(p)
            # Every size deliberately crosses a 4096 page boundary.
            files = {}
            for key, content in {
                "kernel": b"K" * 4319,
                "ramdisk": b"R" * 5027,
                "dtb": bytes.fromhex("d00dfeed") + (4129).to_bytes(4, "big") + b"D" * (4129 - 8),
                "vendor": b"V" * 4915,
                "bootconfig": b"native.test=1\n" * 37
            }.items():
                f = p / key
                f.write_bytes(content)
                files[key] = f
            values = p / "header.json"
            values.write_text(json.dumps({
                "purpose": "structural-only", "phone_boot_validated": False,
                "os_version_raw": 0, "kernel_addr": 0x8000,
                "ramdisk_addr": 0x1000000, "tags_addr": 0x100,
                "dtb_addr": 0x1f00000
            }))
            desc = p / "fragment.json"
            desc.write_text(json.dumps({
                "name": "native", "type": 1, "board_id": [0] * 16
            }))
            out = p / "ours"
            self.run_cmd(OWN, "prototype", bp, vp, "--out-dir", out,
                         "--kernel", files["kernel"],
                         "--initramfs", files["ramdisk"],
                         "--dtb", files["dtb"],
                         "--vendor-ramdisk", files["vendor"],
                         "--bootconfig", files["bootconfig"],
                         "--ramdisk-descriptor", desc,
                         "--header-inputs", values,
                         "--cmdline", "console=0",
                         "--vendor-cmdline", "native=1",
                         "--vendor-name", "oneli")
            our_boot = out / "boot-candidate.UNSIGNED.img"
            our_vendor = out / "vendor_boot-candidate.UNSIGNED.img"
            self.run_cmd(unpack, "--boot_img", our_boot, "--out", p / "unpack_boot")
            self.run_cmd(unpack, "--boot_img", our_vendor, "--out", p / "unpack_vendor")
            for key, extracted in {
                "kernel": p / "unpack_boot/kernel",
                "ramdisk": p / "unpack_boot/ramdisk",
                "dtb": p / "unpack_vendor/dtb",
                "vendor": p / "unpack_vendor/vendor_ramdisk00",
                "bootconfig": p / "unpack_vendor/bootconfig"
            }.items():
                self.assertEqual(hashlib.sha256(extracted.read_bytes()).hexdigest(),
                                 hashlib.sha256(files[key].read_bytes()).hexdigest(), key)
            aosp_boot, aosp_vendor = p / "aosp_boot.img", p / "aosp_vendor.img"
            self.run_cmd(pack, "--header_version", "4", "--kernel", files["kernel"],
                         "--ramdisk", files["ramdisk"], "--cmdline", "console=0",
                         "--output", aosp_boot)
            self.run_cmd(pack, "--header_version", "4", "--pagesize", "4096",
                         "--base", "0", "--kernel_offset", "0x8000",
                         "--ramdisk_offset", "0x1000000",
                         "--tags_offset", "0x100", "--dtb_offset", "0x1f00000",
                         "--board", "oneli", "--vendor_cmdline", "native=1",
                         "--dtb", files["dtb"], "--vendor_bootconfig", files["bootconfig"],
                         "--ramdisk_type", "platform", "--ramdisk_name", "native",
                         "--vendor_ramdisk_fragment", files["vendor"],
                         "--vendor_boot", aosp_vendor)
            ours = json.loads(self.run_cmd(OWN, "inspect", our_boot, our_vendor))
            independent = json.loads(self.run_cmd(OWN, "inspect", aosp_boot, aosp_vendor))
            for section in ("kernel", "ramdisk"):
                a = next(x for x in ours["boot"]["sections"] if x["name"] == section)
                b = next(x for x in independent["boot"]["sections"] if x["name"] == section)
                self.assertEqual((a["bytes"], a["sha256"]), (b["bytes"], b["sha256"]))
            for section in ("vendor_ramdisk", "dtb_region", "bootconfig"):
                a = next(x for x in ours["vendor_boot"]["sections"] if x["name"] == section)
                b = next(x for x in independent["vendor_boot"]["sections"] if x["name"] == section)
                self.assertEqual((a["bytes"], a["sha256"]), (b["bytes"], b["sha256"]))
            self.assertEqual(ours["vendor_boot"]["kernel_addr_raw"],
                             independent["vendor_boot"]["kernel_addr_raw"])
            self.assertEqual(ours["vendor_boot"]["dtb_addr_raw"],
                             independent["vendor_boot"]["dtb_addr_raw"])


if __name__ == "__main__":
    unittest.main()
