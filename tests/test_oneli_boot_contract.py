#!/usr/bin/env python3
"""Check Boot's typed six-FDT reference against a pinned VPU JSON source."""
import json
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
VPU = Path(os.environ.get("ONELI_STOCK_FDT_SOURCE",
                        "external-stock-metadata/docs/vpu/2026-10-12-oneli-stock-fdt-properties.json"))


@unittest.skipUnless(VPU.is_file(), "pinned VPU JSON source checkout required")
class TestPVTResolution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(VPU.read_text())
        cls.matrix = json.loads((ROOT / "configs/oneli-pvt-symbolic-composition-v1.json").read_text())
        cls.packaging = json.loads((ROOT / "configs/oneli-boot-packaging-v2.json").read_text())

    def test_two_unpadded_base_ids_and_pvt_candidate(self):
        source = self.source
        m = self.matrix
        base = source["vendor_boot"]["embedded_dtb"]["two_unpadded_images"]
        self.assertEqual([(x["offset"], x["size"], x["msm_id"][0]) for x in base],
                         [(0, 479481, 530), (479481, 479481, 540)])
        self.assertEqual([(x["relative_offset"], x["bytes"], x["msm_id"][0])
                          for x in self.packaging["reference_images"]["vendor_boot"]["embedded_dtb_roots"]],
                         [(0, 479481, 530), (479481, 479481, 540)])
        self.assertEqual(m["overlay"]["board_id"], [69, 49152])
        self.assertTrue(all(x["pvt_overlay_symbolic_compatibility"] for x in m["bases"]))
        self.assertFalse(m["overlay"]["applied_with_libfdt"])
        self.assertIsNone(self.packaging["reference_images"]["dtbo"]["effective_overlay_index"])

    def test_typed_supply_gpio_aux_and_variant_differences(self):
        m, src = self.matrix, self.source
        pvt = src["dtbo_overlays"][3]
        dev = m["resolved_component_truth"]
        self.assertEqual(dev["nxp"]["reg"], pvt["usb"]["nxp"]["reg"])
        self.assertEqual(dev["nxp"]["vdd18"], dev["ps5169"]["vcc"])
        self.assertEqual(dev["nxp"]["vdd3"],
                         "/soc/rsc@17a00000/rpmh-regulator-ldob2/regulator-pm8350-l2")
        self.assertEqual(dev["ps5169"]["vio"],
                         "/soc/rsc@17a00000/rpmh-regulator-ldoc8/regulator-pm8350c-l8")
        self.assertEqual(dev["aux"]["enable"]["cells"][1], 2)
        self.assertEqual(dev["aux"]["flip"]["cells"][1], 71)
        self.assertEqual(dev["ps5169"]["enable_gpio"]["cells"][1], 19)
        self.assertEqual(dev["ps5169"]["orientation_gpio"]["cells"][1], 91)
        self.assertEqual(dev["diodes"]["source_status"], "disabled")
        self.assertEqual(dev["fsa4480"]["pvt_overlay_status"], "disabled")
        self.assertEqual([x["index"] for x in m["variants"]
                          if x["extra_pm8010_source"]], [2])
        self.assertEqual(len(m["bases"][0]["typed_fixup_paths"]), 12)
        self.assertEqual(m["bases"][0]["typed_fixup_paths"],
                         m["bases"][1]["typed_fixup_paths"])

    def test_packaging_reference_fields_are_not_approved_native_inputs(self):
        p, src = self.packaging, self.source["vendor_boot"]
        ref = p["reference_images"]["vendor_boot"]
        for key in ("kernel_addr", "ramdisk_addr", "tags_addr", "dtb_addr"):
            self.assertEqual(ref[key], src[key])
        self.assertEqual(ref["ramdisk_compression"].split()[0], "legacy-LZ4")
        self.assertIsNone(p["reference_images"]["boot"]["os_version_raw"])
        self.assertIsNone(p["prototype"]["native_header_inputs_example"]["os_version_raw"])
        self.assertFalse(p["prototype"]["native_ready"])
        self.assertFalse(p["prototype"]["hardware_accepted"])
        self.assertEqual(p["prototype"]["validation_stages"]["independent_aosp_parser"]["result"],
                         "passed-synthetic")
        self.assertIn("header-inputs", p["prototype"]["requires_explicit_payload_paths"])


if __name__ == "__main__":
    unittest.main()
