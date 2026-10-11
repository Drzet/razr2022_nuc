#!/usr/bin/env python3
"""Reproduce 23 source-level oneli DisplayPort/Type-C assertions.

These checks inspect pinned source text and verify Git blob identities. They do
not compile any device tree, exercise a kernel driver, or validate hardware.
Use --cache DIR to reuse downloaded source and --offline to prohibit downloads.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# (repository, immutable revision, path, expected Git blob SHA-1)
SOURCES = {
    "vendor_aux": (
        "MotorolaMobilityLLC/kernel-msm-5.4-techpack-display",
        "701a48c1db80eda2ff17154a9017783230cc22aa",
        "msm/dp/dp_aux.c", "633e1324ca2447635dfd829fd823e24b98fc46ac"),
    "vendor_dp": (
        "MotorolaMobilityLLC/kernel-msm-5.4-techpack-display",
        "701a48c1db80eda2ff17154a9017783230cc22aa",
        "msm/dp/dp_display.c", "5e674280ad38f3fb556cf4cdde60b782dac2bb42"),
    "vendor_cape": (
        "MotorolaMobilityLLC/kernel-display-devicetree",
        "80b207bf35be5da38375e755506f136558ad24b5",
        "display/cape-sde.dtsi", "27ddad0485389b4c55f6f4d2f002252f29e440ed"),
    "vendor_oneli": (
        "MotorolaMobilityLLC/kernel-display-devicetree",
        "80b207bf35be5da38375e755506f136558ad24b5",
        "display/cape-sde-display-oneli-common-base.dtsi",
        "5b5fa9790828b587bc584dba54d6c1171aa122f5"),
    "mainline_sbu": (
        "Drzet/linux", "a5ebb76233b79db01e82e061173cb73c6d2b5c6b",
        "drivers/usb/typec/mux/gpio-sbu-mux.c",
        "1834f1a2dd9dd082648050c6aace4124ed70fd38"),
    "mainline_sbu_binding": (
        "Drzet/linux", "a5ebb76233b79db01e82e061173cb73c6d2b5c6b",
        "Documentation/devicetree/bindings/usb/gpio-sbu-mux.yaml",
        "793662f6f3bff4a4b4b73b38983abca12e1e61d2"),
    "mainline_soc": (
        "Drzet/linux", "a5ebb76233b79db01e82e061173cb73c6d2b5c6b",
        "arch/arm64/boot/dts/qcom/sm8450.dtsi",
        "b8793482b1815babe50a8cb8f9869d5d1a46938f"),
    "mainline_hdk": (
        "Drzet/linux", "a5ebb76233b79db01e82e061173cb73c6d2b5c6b",
        "arch/arm64/boot/dts/qcom/sm8450-hdk.dts",
        "4ade28f40cae08717c82d6cf5db431c36ba7906c"),
    "mainline_dp": (
        "Drzet/linux", "a5ebb76233b79db01e82e061173cb73c6d2b5c6b",
        "drivers/gpu/drm/msm/dp/dp_display.c",
        "4dcbd9b99d06b8b3ef9082bbc440163853547f98"),
    "mainline_qmp": (
        "Drzet/linux", "a5ebb76233b79db01e82e061173cb73c6d2b5c6b",
        "drivers/phy/qualcomm/phy-qcom-qmp-combo.c",
        "c39ced168d035ef200af301feb7bf45bb764aaaa"),
}

# The 13 checks first reported in the 2026-10-11 vendor AUX investigation.
# The GPIO patterns are evaluated within the corresponding pinned vendor files.
GPIO_CHECKS = [
    ("vendor_cc1_enable_unflipped", "vendor_aux",
     r"orientation == ORIENTATION_CC1 && enable[\s\S]{0,120}switch_enable = true[\s\S]{0,100}switch_flip = false"),
    ("vendor_cc2_enable_flipped", "vendor_aux",
     r"orientation == ORIENTATION_CC2 && enable[\s\S]{0,120}switch_enable = true[\s\S]{0,100}switch_flip = true"),
    ("vendor_gpio_enable_low", "vendor_aux",
     r"gpio_set_value\(dp_aux->dp_aux_switch_enable_gpio,\s*switch_enable \? 0 : 1\)"),
    ("vendor_gpio_flip_high", "vendor_aux",
     r"gpio_set_value\(dp_aux->dp_aux_switch_flip_gpio,\s*switch_flip \? 1 : 0\)"),
    ("vendor_init_enable_high", "vendor_dp",
     r"gpio_direction_output\(dp->aux->dp_aux_switch_enable_gpio, 1\)"),
    ("vendor_init_flip_low", "vendor_dp",
     r"gpio_direction_output\(dp->aux->dp_aux_switch_flip_gpio, 0\)"),
    ("vendor_configure_gate", "vendor_dp",
     r"!dp->parser->gpio_aux_switch && dp->aux_switch_node"),
    ("oneli_gpio2_enable", "vendor_oneli",
     r"mmi,aux-switch-enable-gpio\s*=\s*<&tlmm 2 0x00>"),
    ("oneli_gpio71_flip", "vendor_oneli",
     r"mmi,aux-switch-flip-gpio\s*=\s*<&tlmm 71 0x00>"),
    ("vendor_legacy_fsa_handle", "vendor_cape",
     r"qcom,dp-aux-switch = <&fsa4480>"),
    ("oneli_fsa_disabled", "vendor_oneli",
     r"&fsa4480 \{[\s\S]{0,50}status = \"disabled\""),
    ("generic_sbu_dp_modes", "mainline_sbu",
     r"case TYPEC_DP_STATE_C:[\s\S]*?case TYPEC_DP_STATE_D:[\s\S]*?case TYPEC_DP_STATE_E:[\s\S]*?enabled = true"),
    ("sbu_binding_part_compatible", "mainline_sbu_binding",
     r"compatible:[\s\S]{0,420}gpio-sbu-mux"),
]

# The 10 baseline graph / driver bridge checks from the second source review.
GRAPH_CHECKS = [
    ("dpu_to_dp", "mainline_soc",
     r"dpu_intf0_out:\s*endpoint\s*\{\s*remote-endpoint = <&mdss_dp0_in>"),
    ("dp_to_dpu", "mainline_soc",
     r"mdss_dp0_in:\s*endpoint\s*\{\s*remote-endpoint = <&dpu_intf0_out>"),
    ("dp_to_qmp", "mainline_soc",
     r"mdss_dp0_out:\s*endpoint\s*\{\s*remote-endpoint = <&usb_1_qmpphy_dp_in>"),
    ("qmp_to_dp", "mainline_soc",
     r"usb_1_qmpphy_dp_in:\s*endpoint\s*\{\s*remote-endpoint = <&mdss_dp0_out>"),
    ("qmp_usb3_input_to_dwc3", "mainline_soc",
     r"usb_1_qmpphy_usb_ss_in:\s*endpoint\s*\{\s*remote-endpoint = <&usb_1_dwc3_ss>"),
    ("qmp_output_port0", "mainline_soc",
     r"port@0\s*\{\s*reg = <0>;\s*usb_1_qmpphy_out:\s*endpoint"),
    ("hdk_reference_sbu_port2", "mainline_hdk",
     r"port@2\s*\{\s*reg = <2>;\s*pmic_glink_sbu:\s*endpoint"),
    ("hdk_reference_pmic_glink", "mainline_hdk",
     r"pmic-glink\s*\{\s*compatible = \"qcom,sm8450-pmic-glink\", \"qcom,pmic-glink\""),
    ("msm_dp_bridge_output1", "mainline_dp",
     r"devm_drm_of_get_bridge\(&dp->pdev->dev,\s*dp->pdev->dev.of_node,\s*1,\s*0\)"),
    ("qmp_aux_bridge_register", "mainline_qmp",
     r"drm_aux_bridge_register\(dev\)"),
]


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def read_source(name: str, cache: Path, offline: bool) -> dict:
    repo, rev, path, expected_blob = SOURCES[name]
    cache_path = cache / (name + ".src")
    url = f"https://raw.githubusercontent.com/{repo}/{rev}/{path}"
    if cache_path.is_file():
        data = cache_path.read_bytes()
    elif offline:
        raise RuntimeError(f"{name}: absent cached source: {cache_path}")
    else:
        req = urllib.request.Request(url, headers={"User-Agent": "oneli-displayport-source-audit/1"})
        with urllib.request.urlopen(req, timeout=30) as reply:
            # Bound downloads; largest pinned source is about 212 KB.
            data = reply.read(2_000_001)
            if len(data) > 2_000_000:
                raise RuntimeError(f"{name}: source exceeds 2 MB bound")
        cache.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(data)

    actual_blob = git_blob_sha(data)
    if actual_blob != expected_blob:
        raise RuntimeError(
            f"{name}: Git blob SHA mismatch, expected {expected_blob}, got {actual_blob}"
        )
    return {
        "repository": repo, "revision": rev, "path": path,
        "git_blob": actual_blob, "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data), "text": data.decode("utf-8"),
    }


def run(cache: Path, offline: bool) -> dict:
    loaded = {name: read_source(name, cache, offline) for name in SOURCES}
    cases = []
    for group, definitions in (("gpio", GPIO_CHECKS), ("graph", GRAPH_CHECKS)):
        for name, source_name, pattern in definitions:
            # This tests source assertions, not a parsed FDT or active hardware.
            text = loaded[source_name]["text"]
            match = re.search(pattern, text, re.MULTILINE)
            cases.append({
                "group": group, "name": name, "source": source_name,
                "passed": match is not None,
                "line": text.count("\n", 0, match.start()) + 1 if match else None,
            })

    passed = sum(case["passed"] for case in cases)
    assert len(GPIO_CHECKS) == 13 and len(GRAPH_CHECKS) == 10
    return {
        "purpose": "pinned source text assertions only; no DT schema, kernel or hardware test",
        "sources": {
            name: {key: value for key, value in item.items() if key != "text"}
            for name, item in loaded.items()
        },
        "checks": cases, "passed": passed, "total": len(cases),
        "status": "passed" if passed == len(cases) else "failed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path(".oneli-dp-source-cache"))
    parser.add_argument("--offline", action="store_true", help="Use previously validated cache only")
    parser.add_argument("--output", type=Path, help="Write JSON report to this file")
    args = parser.parse_args()
    try:
        report = run(args.cache, args.offline)
    except (OSError, UnicodeError, RuntimeError, urllib.error.URLError) as error:
        print(f"SOURCE_ERROR: {error}", file=sys.stderr)
        return 2

    manifest = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(manifest, encoding="utf-8")
    else:
        print(manifest, end="")
    print(f"Source assertions: {report['passed']}/{report['total']} {report['status']}",
          file=sys.stderr)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
