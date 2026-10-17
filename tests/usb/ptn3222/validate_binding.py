#!/usr/bin/env python3
"""Validate actual compiled PTN3222 fixtures, including conditional requirements."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

DTS = '''/dts-v1/;
/ {
    model = "PTN3222 synthetic validation fixture";
    compatible = "test,ptn3222-fixture";
    #address-cells = <1>;
    #size-cells = <1>;
    gpio: gpio-controller {
        compatible = "test,gpio";
        gpio-controller;
        #gpio-cells = <2>;
    };
    v18: regulator-1v8 {
        compatible = "regulator-fixed";
        regulator-name = "test-vdd1v8";
        regulator-min-microvolt = <1800000>;
        regulator-max-microvolt = <1800000>;
    };
    v33: regulator-3v3 {
        compatible = "regulator-fixed";
        regulator-name = "test-vdd3v3";
        regulator-min-microvolt = <3075000>;
        regulator-max-microvolt = <3300000>;
    };
    i2c@1000 {
        compatible = "test,i2c";
        reg = <0x1000 0x100>;
        #address-cells = <1>;
        #size-cells = <0>;
        redriver@4f {
            compatible = "nxp,ptn3222";
            reg = <0x4f>;
            #phy-cells = <0>;
            PROPERTIES
        };
    };
};
'''
PROFILE = 'nxp,usb2-tuning-profile = "motorola,oneli";'
RESET = 'reset-gpios = <&gpio 7 1>;'
V18 = 'vdd1v8-supply = <&v18>;'
V33 = 'vdd3v3-supply = <&v33>;'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kernel", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--tools", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    binding = args.kernel / "Documentation/devicetree/bindings/phy/nxp,ptn3222.yaml"

    def tool(name):
        return str(args.tools / name) if args.tools else name

    def run(argv, log):
        proc = subprocess.run(argv, text=True, capture_output=True, check=True)
        output = proc.stdout + proc.stderr
        log.write_text(output)
        return output

    documentation = run([tool("dt-doc-validate"), str(binding)],
                        args.output / "documentation.log")
    assert not documentation.strip(), documentation
    schema = args.output / "processed-schema.json"
    run([tool("dt-mk-schema"), "-j", "-o", str(schema), str(binding)],
        args.output / "process.log")
    cases = [
        ("legacy-minimal", [], None),
        ("profile-valid", [PROFILE, RESET, V18, V33], None),
        ("profile-no-reset", [PROFILE, V18, V33], "reset-gpios"),
        ("profile-no-v18", [PROFILE, RESET, V33], "vdd1v8-supply"),
        ("profile-no-v33", [PROFILE, RESET, V18], "vdd3v3-supply"),
        ("profile-unknown", [PROFILE.replace("motorola,oneli", "unknown"),
                             RESET, V18, V33], "nxp,usb2-tuning-profile"),
        ("profile-wrong-type", ['nxp,usb2-tuning-profile = <1>;',
                                RESET, V18, V33], "nxp,usb2-tuning-profile"),
        ("raw-normal-forbidden", [PROFILE, RESET, V18, V33,
                                  'qcom,param-override-seq = <0x40 6>;'],
         "qcom,param-override-seq"),
        ("raw-host-forbidden", [PROFILE, RESET, V18, V33,
                                'qcom,host-param-override-seq = <0x24 8>;'],
         "qcom,host-param-override-seq"),
    ]
    results = []
    for name, props, diagnostic in cases:
        dts, dtb = args.output / f"{name}.dts", args.output / f"{name}.dtb"
        dts.write_text(DTS.replace("PROPERTIES", "\n            ".join(props)))
        run(["dtc", "-I", "dts", "-O", "dtb", "-o", str(dtb), str(dts)],
            args.output / f"{name}-compile.log")
        log = run([tool("dt-validate"), "-s", str(schema), "-l", "nxp,ptn3222",
                   str(dtb)], args.output / f"{name}-validate.log")
        if diagnostic:
            assert "nxp,ptn3222.yaml" in log and diagnostic in log, (name, log)
        else:
            assert not log.strip(), (name, log)
        results.append({"fixture": name, "expected_diagnostic": diagnostic,
                        "result": "PASS"})
    (args.output / "schema-result.json").write_text(json.dumps({
        "binding_sha256": hashlib.sha256(binding.read_bytes()).hexdigest(),
        "scope": "synthetic DTBs; schema diagnostics, not board/hardware validation",
        "cases": results,
    }, indent=2) + "\n")
    print(f"PASS: {len(cases)} compiled schema fixtures (2 valid, 7 invalid)")


if __name__ == "__main__":
    main()
