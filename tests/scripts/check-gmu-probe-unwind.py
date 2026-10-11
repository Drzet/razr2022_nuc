#!/usr/bin/env python3
"""Static regression guard for the exact GMU error-propagation/unwind contract.

This deliberately tests source control flow, NOT runtime fault injection.
"""
import argparse
from pathlib import Path
import re


def function_body(text: str) -> str:
    head = "int a6xx_gmu_init(struct a6xx_gpu *a6xx_gpu, struct device_node *node)"
    at = text.index(head)
    next_end = text.index("\n}\n", at)
    return text[at:next_end]


def verify(source: str) -> None:
    body = function_body(source)
    assert re.search(
        r"ret\s*=\s*a6xx_gmu_pwrlevels_probe\(gmu\);\s*"
        r"if\s*\(ret\)\s*goto\s+detach_gxpd;",
        body,
    ), "pwrlevels failure must jump to GX/QMP/IRQ/memory unwind"
    assert re.search(
        r"ret\s*=\s*a6xx_gmu_acd_probe\(gmu\);\s*"
        r"if\s*\(ret\)\s*goto\s+detach_gxpd;",
        body,
    ), "existing ACD failure path must remain intact"

    expected = [
        "detach_gxpd:",
        "dev_pm_domain_detach(gmu->gxpd, false);",
        "qmp_put(gmu->qmp);",
        "device_link_del(link);",
        "detach_cxpd:",
        "dev_pm_domain_detach(gmu->cxpd, false);",
        "err_mmio:",
        "iounmap(gmu->mmio);",
        "free_irq(gmu->gmu_irq, gmu);",
        "free_irq(gmu->hfi_irq, gmu);",
        "err_memory:",
        "a6xx_gmu_memory_free(gmu);",
        "err_put_device:",
        "pm_runtime_disable(gmu->dev);",
        "put_device(gmu->dev);",
        "return ret;",
    ]
    last = -1
    for token in expected:
        found = body.find(token, last + 1)
        assert found > last, f"absent or out-of-order cleanup: {token}"
        last = found
    assert "if (!IS_ERR_OR_NULL(gmu->gxpd))" in body[
        body.index("detach_gxpd:"):body.index("detach_cxpd:")
    ], "must not detach absent/ERR_PTR GX"
    assert "if (!IS_ERR_OR_NULL(gmu->qmp))" in body[
        body.index("detach_gxpd:"):body.index("detach_cxpd:")
    ], "must not put absent/ERR_PTR QMP"
    assert "pm_runtime_enable(gmu->dev);" in body, "runtime PM balance needs preceding enable"
    assert body.count("pm_runtime_enable(gmu->dev);") == 1
    assert body.count("pm_runtime_disable(gmu->dev);") == 1


def negative_cases(source: str) -> None:
    changes = {
        "discarded-return": (
            "ret = a6xx_gmu_pwrlevels_probe(gmu);",
            "a6xx_gmu_pwrlevels_probe(gmu);",
        ),
        "skipped-resource-unwind": (
            "if (ret)\n\t\tgoto detach_gxpd;\n\n\tret = a6xx_gmu_acd_probe",
            "if (ret)\n\t\tgoto err_put_device;\n\n\tret = a6xx_gmu_acd_probe",
        ),
        "missing-runtime-PM-disable": (
            "err_put_device:\n\tpm_runtime_disable(gmu->dev);",
            "err_put_device:",
        ),
        "missing-gx-domain-detach": (
            "dev_pm_domain_detach(gmu->gxpd, false);",
            "/* removed GX detach */",
        ),
    }
    for label, (old, new) in changes.items():
        assert old in source, f"self-test setup missing expected case: {label}"
        mutant = source.replace(old, new, 1)
        try:
            verify(mutant)
        except AssertionError:
            print("PASS expected rejection:", label)
        else:
            raise AssertionError(f"false negative: {label}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    text = args.source.read_text()
    verify(text)
    print("PASS GMU power-level error return and cleanup ordering (static)")
    if args.self_test:
        negative_cases(text)
