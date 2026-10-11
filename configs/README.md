# Kernel configuration and baseline

`baseline.json` pins the initial upstream commit and names `razr/boot`. The selection is build-unverified. ARM64 defconfig is the clean-build starting point, not a working Razr configuration. Null fields remain unresolved; no external patchsets or configuration fragments have been applied.

Record fragment application order and retain the generated configuration with each successful build. Kernel source and device trees belong in `Drzet/linux`. See [comparison and build blockers](../docs/sm8475_baseline_comparison_2026-10-11.md).
