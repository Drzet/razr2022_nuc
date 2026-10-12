#!/usr/bin/env python3
"""Source-only consistency check for Motorola compiled GPU OPPs and A730 HFI votes.

Compare two SHA-pinned vendor_boot FDT property exports, the actual pinned
mainline a730_build_bw_table(), and VPU's qualified Qualcomm ZAP loader replay.
No ROM or proprietary firmware bytes, no phone and no kernel compilation.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

EXPECTED_FOCUSED_SHA256 = "f1bb6f41036aeb2e04ac289cfa803aab686cf92097a77444c9ed50c96397fe48"
EXPECTED_ZAP_SHA256 = "f5d8a41c1380ba2b42cd742538083306d245471ac5d51139e3bc8a6168ce84d2"
EXPECTED_ZAP_SEG_SHA256 = "1fc98f97cf354b9704b20d0848f7b2739638539a57d88ecf5cc71ca1c5c4e6b9"
FIELDS = ("qcom,gpu-freq", "qcom,level", "qcom,cx-level", "qcom,bus-freq",
          "qcom,bus-min", "qcom,bus-max", "qcom,acd-level")
PWRLEVEL = re.compile(r"^/soc/qcom,kgsl-3d0@3d00000/qcom,gpu-pwrlevels/qcom,gpu-pwrlevel@(\d+)$")


def cells(node, key):
    prop = node["properties"][key]
    assert prop["state"] == "published" and prop["bytes"] % 4 == 0, (node["path"], key)
    return prop["cells_be_u32"]


def bases_from_focused(focused):
    base = [b for b in focused["per_fdt_focus"] if b["source"]["member"] == "vendor_boot.img"]
    assert len(base) == 2, "expect both MSM530 and MSM540 stock FDTs"
    assert sorted(b["source"]["root_msm_id"][0] for b in base) == [530, 540]
    return base


def snapshot(base):
    parent = next(n for n in base["nodes"] if n["path"] == "/soc/qcom,kgsl-3d0@3d00000")
    levels = []
    for node in base["nodes"]:
        m = PWRLEVEL.fullmatch(node["path"])
        if m:
            x = {"index": int(m.group(1))}
            for name in FIELDS:
                val = cells(node, name)
                assert len(val) == 1
                x[name] = val[0]
            levels.append(x)
    levels.sort(key=lambda x: x["index"])
    assert [r["index"] for r in levels] == list(range(13)), "expected 13 exact rows"
    table = cells(parent, "qcom,bus-table-ddr")
    assert len(table) == 12 and table[0] == 0 and list(sorted(table)) == table
    assert cells(parent, "qcom,chipid") == [0x07030002]
    assert cells(parent, "qcom,initial-pwrlevel") == [11]
    assert cells(parent, "qcom,ubwc-mode") == [4]
    assert cells(parent, "qcom,min-access-length") == [32]
    assert cells(parent, "qcom,bus-table-cnoc") == [0, 100]
    assert all(0 <= x["qcom,bus-min"] <= x["qcom,bus-freq"] <= x["qcom,bus-max"] < len(table)
               for x in levels)
    return table, levels


def parse_hfi_table(source):
    begin = source.index("static void a730_build_bw_table(")
    end = source.index("static void a740_build_bw_table(", begin)
    fragment = source[begin:end]
    assert "msg->bw_level_num = 12;" in fragment
    assert "msg->ddr_cmds_num = 3;" in fragment
    assert all(f'cmd_db_read_addr("{name}")' in fragment for name in ("SH0", "MC0", "ACV"))
    items = re.findall(
        r"msg->ddr_cmds_data\[(\d+)\]\[(\d+)\]\s*=\s*(0x[0-9a-f]+);",
        fragment,
    )
    assert len(items) == 36, f"expected exactly 12x3 HFI assignments, got {len(items)}"
    vote = [[None] * 3 for _ in range(12)]
    for si, sj, sw in items:
        i, j = int(si), int(sj)
        assert 0 <= i < 12 and 0 <= j < 3 and vote[i][j] is None
        vote[i][j] = int(sw, 16)
    assert all(all(v is not None for v in row) for row in vote)
    return vote


def check_zap(loader):
    z = next(x for x in loader["files"] if x["filename"] == "a730_zap.mdt")
    assert z["sha256"] == EXPECTED_ZAP_SHA256
    assert z["size"] == 4044 and z["program_header_count"] == 3
    assert z["firmware_loader_split_detection"] and z["firmware_loader_relocatable"]
    assert z["qcom_mdt_get_size_bytes"] == 4096
    assert z["expected_reserved_region_bytes"] == 8192
    assert z["qcom_mdt_get_size_bytes"] <= z["expected_reserved_region_bytes"]
    req = z["segments_needed_at_runtime"]
    assert len(req) == 1 and req[0]["filename"] == "a730_zap.b01"
    assert req[0]["index"] == 1 and req[0]["actual_bytes"] == 2236
    assert req[0]["exact_size_matches"] and req[0]["sha256"] == EXPECTED_ZAP_SEG_SHA256
    assert len(z["pas_metadata_hash_segment_placement"]) == 1
    assert z["pas_metadata_hash_segment_placement"][0]["phdr_index"] == 2
    assert z["pas_metadata_hash_segment_placement"][0]["placement"] == "packed_directly_after_ELF_header"
    return {"mdt": z["sha256"], "load_segments": ["a730_zap.b01"], "required_bytes": 4096,
            "reserved_bytes": 8192, "hash_packed_in_mdt": True}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--focused", required=True, type=Path)
    p.add_argument("--loader", required=True, type=Path)
    p.add_argument("--hfi", required=True, type=Path)
    p.add_argument("--json-out", type=Path)
    args = p.parse_args()
    focus_raw = args.focused.read_bytes()
    assert hashlib.sha256(focus_raw).hexdigest() == EXPECTED_FOCUSED_SHA256, "focused FDT JSON hash mismatch"
    focused = json.loads(focus_raw)
    loader = json.loads(args.loader.read_bytes())
    bases = bases_from_focused(focused)
    a, b = map(snapshot, bases)
    assert a == b, "MSM530/540 GPU property contents differ"
    table, levels = a
    hfi = parse_hfi_table(args.hfi.read_text())
    matched = []
    for i, bw in enumerate(table):
        expect = ([0x40000000] * 3 if i == 0 else [
            0x60000000 | (bw // 1050),
            0x60000000 | (bw // 800),
            0x60000008,
        ])
        assert hfi[i] == expect, f"HFI-to-stock mapping differs at {i}: {hfi[i]} vs {expect}"
        matched.append({"vendor_index": i, "stock_kBps_raw": bw, "hfi_encoded": [hex(x) for x in hfi[i]]})
    six = [r["qcom,gpu-freq"] for r in levels if r["qcom,cx-level"] != r["qcom,level"]]
    assert six == [710000000, 580000000, 439000000, 364000000, 285000000, 220000000]
    result = {
        "status": "PASS", "scope": "source-verified stock FDT crosswalk, not device runtime",
        "focused_json_sha256": EXPECTED_FOCUSED_SHA256,
        "base_msm_ids": [b["source"]["root_msm_id"][0] for b in bases],
        "raw_power_rows_identical": 13, "complete_fields_per_power_row": len(FIELDS),
        "verified_hfi_ddr_levels": len(matched), "matched_indices": matched,
        "cx_above_gx_mhz": [x // 1000000 for x in six],
        "zap_loader": check_zap(loader),
        "firmware_authentication_or_hardware_tested": False,
    }
    output = json.dumps(result, sort_keys=True, indent=2)
    print("PASS: both compiled stock base FDTs have 13x7 matching GPU power fields")
    print("PASS: 12/12 A730 HFI SH0/MC0/ACV entries algebraically match stock DDR entries")
    print("PASS: ZAP MDT host load needs only indexed .b01, fits 4K into 8K carveout")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output + "\n")
    else:
        print(output)


if __name__ == "__main__":
    main()
