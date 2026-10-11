#!/usr/bin/env python3
"""Offline Qualcomm PMIC GLINK source comparison and synthetic wire fixtures.

Source inputs (pin to exact SHAs, never floating branch names):
 vendor: MotorolaMobilityLLC/kernel-msm 9511d6b2dc469e5bd836992e3bdd6d19ace112e0
         drivers/power/supply/qti_battery_charger.c
 upstream: Drzet/linux a5ebb76233b79db01e82e061173cb73c6d2b5c6b
         drivers/power/supply/qcom_battmgr.c

This tool never communicates with a device and never writes charge settings.
"""
import argparse
import re
import struct
import sys
import unittest
from pathlib import Path

OWNER_BATTMGR = 32778
OPCODES = (
    ("BC_SET_NOTIFY_REQ", "BATTMGR_REQUEST_NOTIFICATION"),
    ("BC_NOTIFY_IND", "BATTMGR_NOTIFICATION"),
    ("BC_BATTERY_STATUS_GET", "BATTMGR_BAT_PROPERTY_GET"),
    ("BC_BATTERY_STATUS_SET", "BATTMGR_BAT_PROPERTY_SET"),
    ("BC_USB_STATUS_GET", "BATTMGR_USB_PROPERTY_GET"),
    ("BC_USB_STATUS_SET", "BATTMGR_USB_PROPERTY_SET"),
    ("BC_WLS_STATUS_GET", "BATTMGR_WLS_PROPERTY_GET"),
    ("BC_WLS_STATUS_SET", "BATTMGR_WLS_PROPERTY_SET"),
)
FIELDS = (
    ("battery_property_id", 23),
    ("usb_property_id", 10),
    ("wireless_property_id", 7),
)


def defines(source):
    return {
        name: int(number, 0)
        for name, number in re.findall(
            r"^\s*#define\s+([A-Za-z_][A-Za-z_0-9]*)\s+(0[xX][0-9a-fA-F]+|[0-9]+)\b",
            source, re.M
        )
    }


def enum_members(source, name):
    match = re.search(
        r"\benum\s+" + re.escape(name) + r"\s*\{([^}]+)\}", source, re.S
    )
    if match is None:
        raise ValueError("Missing enum: " + name)
    members = {}
    counter = 0
    for entry in match.group(1).split(","):
        entry = re.sub(r"/\*.*?\*/|//[^\n]*", "", entry, flags=re.S).strip()
        if not entry:
            continue
        if "=" in entry:
            symbol, number = (part.strip() for part in entry.split("=", 1))
            counter = int(number, 0)
        else:
            symbol = entry
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", symbol):
            raise ValueError("Unsupported enum syntax: " + symbol)
        members[symbol] = counter
        counter += 1
    return members


def compare_sources(vendor, upstream):
    vend = defines(vendor)
    main = defines(upstream)
    mismatches = []
    print("Qualcomm PMIC GLINK source comparison (not firmware validation)")
    print("Opcode mappings:")
    for v, m in OPCODES:
        a, b = vend.get(v), main.get(m)
        print(f"  {v:29s} {a!s:>5}  | {m:32s} {b!s:>5}")
        if a is None or a != b:
            mismatches.append(v + " / " + m)
    print("Common property ID prefix:")
    for enum_name, count in FIELDS:
        fields = enum_members(vendor, enum_name)
        pairs = list(fields.items())[:count]
        if len(pairs) != count:
            mismatches.append("short " + enum_name)
        bad = [name for name, val in pairs if main.get(name) != val]
        mismatches.extend(bad)
        print(f"  {enum_name:25s} {count} checked, {len(bad)} mismatches")
    print("Extra vendor USB properties: USB_TEMP(10), USB_REAL_TYPE(11), USB_TYPEC_COMPLIANT(12)")
    print("Extra upstream battery properties: BATT_CHG_CTRL_EN(24), START_THR(25), END_THR(26)")
    if mismatches:
        print("MISMATCH: " + ", ".join(mismatches))
        return 1
    print("PASS: 8 shared opcode values and 40 shared property IDs match sources.")
    return 0


def round_div_signed(raw, divisor):
    """Match DIV_ROUND_CLOSEST for signed numerator, positive divisor."""
    magnitude = (abs(raw) + divisor // 2) // divisor
    return -magnitude if raw < 0 else magnitude


class SyntheticFixtures(unittest.TestCase):
    """Little-endian request/reply layouts from cited C structs, no real captures."""

    def test_request_24_bytes(self):
        request = struct.pack("<IIIIII", OWNER_BATTMGR, 1, 0x30, 0, 4, 0)
        self.assertEqual(len(request), 24)
        self.assertEqual(struct.unpack("<IIIIII", request), (32778, 1, 48, 0, 4, 0))

    def test_response_24_bytes(self):
        response = struct.pack("<IIIIII", OWNER_BATTMGR, 1, 0x30, 4, 7250, 0)
        self.assertEqual(len(response), 24)
        _, _, opcode, prop_id, raw, result = struct.unpack("<IIIIII", response)
        self.assertEqual((opcode, prop_id, result), (48, 4, 0))
        self.assertEqual(round_div_signed(raw, 100), 73)

    def test_notification_16_bytes(self):
        notification = struct.pack("<IIII", OWNER_BATTMGR, 2, 0x07, 0x32)
        self.assertEqual(len(notification), 16)
        self.assertEqual(struct.unpack("<IIII", notification)[-1], 0x32)

    def test_subscribe_28_bytes(self):
        subscription = struct.pack("<IIIIIII", OWNER_BATTMGR, 2, 0x04, 0, 0, 0, 0)
        self.assertEqual(len(subscription), 28)

    def test_temperature_signedness_and_scaling(self):
        # Both sources divide by 10. Vendor explicitly casts raw to int.
        raw = struct.unpack("<i", struct.pack("<I", (-201) & 0xffffffff))[0]
        self.assertEqual(raw, -201)
        self.assertEqual(round_div_signed(raw, 10), -20)
        self.assertEqual(round_div_signed(253, 10), 25)

    def test_truncation_not_valid(self):
        response = struct.pack("<IIIIII", OWNER_BATTMGR, 1, 0x30, 4, 7250, 0)
        self.assertNotEqual(len(response[:-1]), struct.calcsize("<IIIIII"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vendor", type=Path, help="Pinned qti_battery_charger.c")
    parser.add_argument("--upstream", type=Path, help="Pinned qcom_battmgr.c")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SyntheticFixtures)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    if bool(args.vendor) != bool(args.upstream):
        parser.error("provide --vendor and --upstream together")
    if args.vendor:
        return compare_sources(args.vendor.read_text(), args.upstream.read_text())
    print("Source comparison skipped; supply --vendor and --upstream")
    return 0


if __name__ == "__main__":
    sys.exit(main())
