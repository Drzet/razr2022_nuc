# Baseline CI result — 2026-10-11

- Result: **success**, verified from GitHub Actions run/job records and logs.
- [Run 38144632260, attempt 1](https://github.com/Drzet/razr2022_nuc/actions/runs/38144632260), job `114485299222`.
- Project commit: `98a8c35f492ed8f1eedcd2a6b472ea587c894026`.
- Kernel commit: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- Hosted runner: Ubuntu 24.04; distribution AArch64 GCC/binutils installed by workflow. Exact versions and generated configuration are in the evidence artifact; this is not a pinned toolchain image.
- Targets: ARM64 defconfig, Image and dtbs, using `scripts/build-baseline.sh` at the project commit above.
- Build step: 13:49:04–14:01:22 UTC; run completed 14:01:28 UTC.
- Artifact: `arm64-baseline-38144632260-1`, ID `11704169446`, 26,325,286 bytes; GitHub-reported digest `sha256:fd8488a0f82f8a0142a5d72dcbe46e785e91be609ed2156150b64844f57886ea`. The digest is metadata, not an independently recomputed local hash. Retention is 30 days.
- Scope excluded: subsystem patches, oneli DTB, modules, DT schema validation, boot image preparation, emulation and hardware tests.

The earlier local build failure remains a record of that environment. Hosted CI establishes that baseline compilation is no longer blocked by it.

The final summary step accidentally interpreted backtick-wrapped commit values as shell commands. This produced summary errors/empty commit text without failing the preceding build or artifact upload. The coordination review fixes those two lines to print literal values; the original run above predates that formatting fix.
