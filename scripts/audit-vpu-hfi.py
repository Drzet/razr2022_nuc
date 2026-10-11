#!/usr/bin/env python3
"""Pinned, read-only SM8475/Waipio HFI Gen2 host ABI comparison.

No firmware image is loaded or executed. This is *not* an oneli firmware ABI test.
Run: python3 scripts/audit-vpu-hfi.py --json-out tests/results/vpu-hfi-audit.json
Offline: python3 scripts/audit-vpu-hfi.py --source-dir /path/to/six/source/files
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

VENDOR_REPO = "LowTension/android_kernel_xiaomi_sm8475"
VENDOR_COMMIT = "39382bf760ccf05a8fb4dddee7138ecac02d4a59"
UPSTREAM_REPO = "Drzet/linux"
UPSTREAM_COMMIT = "a5ebb76233b79db01e82e061173cb73c6d2b5c6b"

# The SHA here is the Git blob object SHA (not SHA-256).
SOURCES = {
    "vendor-command.h": (VENDOR_REPO, VENDOR_COMMIT,
        "techpack/video/driver/vidc/inc/hfi_command.h",
        "e7128f3ab9428569a7ec7f37493ec86ca9e0111f"),
    "vendor-property.h": (VENDOR_REPO, VENDOR_COMMIT,
        "techpack/video/driver/vidc/inc/hfi_property.h",
        "23de0e57667a8e7d412f08f831a7e424f01c75d5"),
    "vendor-packet.c": (VENDOR_REPO, VENDOR_COMMIT,
        "techpack/video/driver/vidc/src/hfi_packet.c",
        "533a39e8077b21ddf3be04f2419af70c684355c6"),
    "upstream-defines.h": (UPSTREAM_REPO, UPSTREAM_COMMIT,
        "drivers/media/platform/qcom/iris/iris_hfi_gen2_defines.h",
        "f43aea10090d8f1d6ae5c20547e5f6321b2ca203"),
    "upstream-packet.h": (UPSTREAM_REPO, UPSTREAM_COMMIT,
        "drivers/media/platform/qcom/iris/iris_hfi_gen2_packet.h",
        "25b9582349ca1a0ce6efc0b146a3abb798485c45"),
    "upstream-packet.c": (UPSTREAM_REPO, UPSTREAM_COMMIT,
        "drivers/media/platform/qcom/iris/iris_hfi_gen2_packet.c",
        "0d05dd2afc07d830cc8502ab5f28001312991ba8"),
}

DIRECT_NUMBER = re.compile(r"^\s*#define\s+(HFI_[A-Z0-9_]+)\s+(0[xX][a-fA-F0-9]+|\d+)(?=\s|$)", re.M)
FIELD = re.compile(r"(u8|u32|u64)\s+([a-zA-Z_]\w*)\s*(?:\[\s*(\d*)\s*\])?\s*;")
PRIMITIVES = {"u8": (1, 1), "u32": (4, 4), "u64": (8, 8)}
PAIRS = (("hfi_header", "iris_hfi_header"),
         ("hfi_packet", "iris_hfi_packet"),
         ("hfi_buffer", "iris_hfi_buffer"))


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def get_sources(local_dir):
    result, metadata = {}, {}
    for name, (repo, commit, path, expected) in SOURCES.items():
        url = f"https://raw.githubusercontent.com/{repo}/{commit}/{path}"
        if local_dir:
            data = (local_dir / name).read_bytes()
        else:
            request = urllib.request.Request(url, headers={"User-Agent": "razr-vpu-audit/1.0"})
            with urllib.request.urlopen(request, timeout=40) as response:
                data = response.read()
        sha = git_blob_sha(data)
        if sha != expected:
            raise ValueError(f"{name}: Git blob SHA {sha} != pinned {expected}")
        result[name] = data.decode("utf-8")
        metadata[name] = {"source": url, "git_blob_sha1": sha,
                          "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    return result, metadata


def direct_definitions(src):
    values = {}
    for key, literal in DIRECT_NUMBER.findall(src):
        val = int(literal, 0) if literal.lower().startswith("0x") else int(literal, 10)
        if key in values and values[key] != val:
            raise ValueError(f"Conflicting numeric macro {key}")
        values[key] = val
    return values


def remove_comments(src):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"//[^\n]*", "", src)


def struct_fields(src, name):
    src = remove_comments(src)
    match = re.search(r"\bstruct\s+" + re.escape(name) + r"\s*\{([^{}]*)\}\s*;", src, re.S)
    if not match:
        raise ValueError(f"Cannot find struct {name}")
    body = match.group(1).strip()
    fields = []
    while body:
        m = FIELD.match(body)
        if not m:
            raise ValueError(f"Unrecognized {name} field near {body[:75]!r}")
        typ, field, count = m.groups()
        # flexible array is used by upstream iris_hfi_packet only.
        flex = m.group(0).find("[]") >= 0
        fields.append({"type": typ, "name": field, "count": int(count) if count else 1,
                       "flexible": flex})
        body = body[m.end():].strip()
    return fields


def layout(fields):
    """Host-side AArch64 LP64 layout model for simple u8/u32/u64 fixed arrays.

    This does not replace target-compiler sizeof/offsetof validation.
    """
    offset, maximum, entries = 0, 1, []
    for f in fields:
        size, alignment = PRIMITIVES[f["type"]]
        maximum = max(maximum, alignment)
        offset += (-offset) % alignment
        entries.append({**f, "offset": offset})
        if not f["flexible"]:
            offset += size * f["count"]
    return {"fields": entries, "size": offset + (-offset) % maximum, "align": maximum}


def find_function(src, name):
    match = re.search(r"\b" + re.escape(name) + r"\s*\([^;]*?\)\s*\{", src, re.S)
    if not match:
        raise ValueError(f"Missing function {name}")
    i, depth = match.end(), 1
    while i < len(src) and depth:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    if depth:
        raise ValueError(f"Unterminated function {name}")
    return src[match.end():i-1]


def ubwc_payload_expressions(body):
    """Last payload assignment before each actual property token in sys_init.

    These are source expressions, not evaluated runtime values. Downstream uses
    board-provided ubwc_config; upstream derives values from qcom_ubwc_cfg_data.
    """
    result = {}
    for key in sorted(set(re.findall(r"\bHFI_PROP_UBWC_[A-Z0-9_]+\b", body))):
        idx = body.rfind(key)  # Vendor source also mentions IDs in comments.
        assignments = list(re.finditer(r"\bpayload\s*=\s*([^;]+);", body[:idx]))
        result[key] = assignments[-1].group(1).strip() if assignments else None
    return result


def semantic_checks(vendor_src, upstream_src):
    vendor = find_function(vendor_src, "hfi_packet_sys_init")
    upstream = find_function(upstream_src, "iris_hfi_gen2_packet_sys_init")
    must_match = ["HFI_VIDEO_ARCH_LX", "HFI_CMD_INIT",
                  "HFI_HOST_FLAGS_RESPONSE_REQUIRED", "HFI_HOST_FLAGS_INTR_REQUIRED",
                  "HFI_HOST_FLAGS_NON_DISCARDABLE", "HFI_PAYLOAD_U32", "HFI_PORT_NONE"]
    presence = {name: {"vendor": bool(re.search(r"\b" + name + r"\b", vendor)),
                       "upstream": bool(re.search(r"\b" + name + r"\b", upstream))}
                for name in must_match}
    property_re = re.compile(r"\bHFI_PROP_UBWC_[A-Z0-9_]+\b")
    vendor_properties = sorted(set(property_re.findall(vendor)))
    upstream_properties = sorted(set(property_re.findall(upstream)))
    vendor_payloads = ubwc_payload_expressions(vendor)
    upstream_payloads = ubwc_payload_expressions(upstream)
    vendor_builder = find_function(vendor_src, "hfi_create_packet")
    upstream_builder = find_function(upstream_src, "iris_hfi_gen2_create_packet")
    semantic_delta = {
        "vendor_has_optional_ubwc_config_gate":
            bool(re.search(r"if\s*\(!core->platform->data\.ubwc_config\)", vendor)),
        "upstream_ubwc_source_is_smembacked_config":
            "core->ubwc_cfg" in upstream,
        "vendor_builder_checks_packet_capacity":
            bool(re.search(r"packet_size\s*<\s*hdr->size\s*\+\s*pkt_size", vendor_builder)),
        "upstream_builder_checks_packet_capacity":
            bool(re.search(r"packet_size\s*<\s*hdr->size\s*\+\s*pkt_size", upstream_builder)),
        "ubwc_payload_formula_differences":
            [{"property": key, "vendor": vendor_payloads.get(key),
              "upstream": upstream_payloads.get(key)}
             for key in vendor_properties if vendor_payloads.get(key) != upstream_payloads.get(key)]
    }
    return {"sys_init": presence,
            "semantic_differences": semantic_delta,
            "vendor_ubwc_payload_expressions": vendor_payloads,
            "upstream_ubwc_payload_expressions": upstream_payloads,
            "vendor_ubwc_property_names": vendor_properties,
            "upstream_ubwc_property_names": upstream_properties,
            "ubwc_property_name_difference":
                sorted(set(vendor_properties) ^ set(upstream_properties)),
            "note": "Matching token presence is not proof of matching packet behavior, "
                    "runtime firmware generation, buffer ownership, or UBWC parameter values."}


def audit(sources, metadata):
    vendor = direct_definitions(sources["vendor-command.h"] + "\n" + sources["vendor-property.h"])
    upstream = direct_definitions(sources["upstream-defines.h"])
    shared = sorted(vendor.keys() & upstream.keys())
    differences = [{"name": name, "vendor": vendor[name], "upstream": upstream[name]}
                   for name in shared if vendor[name] != upstream[name]]
    structs = {}
    for vn, un in PAIRS:
        v = layout(struct_fields(sources["vendor-command.h"], vn))
        u = layout(struct_fields(sources["upstream-packet.h"], un))
        v_fixed = [f for f in v["fields"] if not f["flexible"]]
        u_fixed = [f for f in u["fields"] if not f["flexible"]]
        # Field naming is meaningful; compare the full fixed field layout.
        match = (v["size"] == u["size"] and v["align"] == u["align"]
                 and v_fixed == u_fixed)
        structs[vn] = {"vendor": v, "upstream": u, "match": match}
    semantics = semantic_checks(sources["vendor-packet.c"], sources["upstream-packet.c"])
    ok = not differences and all(x["match"] for x in structs.values()) and all(
        x["vendor"] and x["upstream"] for x in semantics["sys_init"].values())
    return {"status": "PASS_HOST_SOURCE_SUBSET" if ok else "FAIL_HOST_SOURCE_SUBSET",
            "scope": "Pinned Xiaomi SM8475 host driver vs upstream Iris HFI Gen2; NOT Motorola signed firmware",
            "sources": metadata,
            "numbers": {"vendor_count": len(vendor), "upstream_count": len(upstream),
                        "shared_count": len(shared), "equal_count": len(shared)-len(differences),
                        "mismatch_count": len(differences), "mismatches": differences,
                        "vendor_only": sorted(vendor.keys()-upstream.keys()),
                        "upstream_only": sorted(upstream.keys()-vendor.keys())},
            "structures": structs, "semantics": semantics,
            "limits": ["Host code only; no signed vpu20_4v bytes inspected",
                       "Only directly numeric HFI_* macros compared",
                       "Simple LP64 struct layout model, not a target compiler",
                       "No proof of oneli DTBO, secure PAS acceptance, or real decode"]}


def self_test():
    sample = "struct check { u32 first; u64 second; u32 spare[2]; };"
    assert layout(struct_fields(sample, "check")) == {
        "fields": [{"type": "u32", "name": "first", "count": 1, "flexible": False, "offset": 0},
                   {"type": "u64", "name": "second", "count": 1, "flexible": False, "offset": 8},
                   {"type": "u32", "name": "spare", "count": 2, "flexible": False, "offset": 16}],
        "size": 24, "align": 8}
    assert direct_definitions("#define HFI_CMD_X 0x12\n#define HFI_CMD_Y 17\n") == {
        "HFI_CMD_X": 18, "HFI_CMD_Y": 17}
    print("PASS: synthetic parser/layout self-test (no external firmware or kernel involved)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, help="Folder with six pinned source files")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    try:
        sources, metadata = get_sources(args.source_dir)
        report = audit(sources, metadata)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"AUDIT FAILED: {exc}", file=sys.stderr)
        return 2
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    numbers = report["numbers"]
    print(f"{report['status']}: numeric {numbers['equal_count']}/{numbers['shared_count']} "
          f"match; {numbers['mismatch_count']} mismatches")
    for name, item in report["structures"].items():
        print(f"  {name}: {'match' if item['match'] else 'DIFF'}; "
              f"vendor size={item['vendor']['size']}, upstream size={item['upstream']['size']}")
    print("  firmware compatibility and real decoding: NOT TESTED")
    return 0 if report["status"] == "PASS_HOST_SOURCE_SUBSET" else 1


if __name__ == "__main__":
    sys.exit(main())
