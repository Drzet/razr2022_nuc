# ARM64 baseline build on GitHub Actions

[Open workflow](https://github.com/Drzet/razr2022_nuc/actions/workflows/arm64-baseline.yml).

The workflow runs when its workflow file, build script or baseline manifest changes on main. To rerun manually, select **Run workflow** on main. It reads the exact upstream SHA from `configs/baseline.json` and checks out `Drzet/linux` at that revision. It does not follow the moving razr/boot branch.

## Build scope

Ubuntu 24.04 runner with the ARM64 GCC/binutils cross-toolchain and host dependencies installed through apt. Actions are pinned to commit SHAs. The job has read-only repository permissions and a 120-minute timeout.

Targets are ARM64 defconfig, Image and dtbs. This establishes the clean upstream baseline only. Modules are not built, and DT schema validation, Razr packaging and device boot tests are not included. Empty fragments/patchsets are required; unsupported non-empty inputs cause a failure instead of being silently ignored. A future board-build workflow must explicitly select board-support commits and configuration.

## Evidence

Download `arm64-baseline-<run-id>-<attempt>` from the completed run. Artifacts are retained for 30 days. Preserve any accepted milestone evidence before expiration.

- Configuration and build logs; apt logs even if dependency installation fails.
- Exact kernel and project SHAs, runner image identity, compiler/tool versions and installed package versions.
- Manifest, workflow and build script used.
- Generated configuration, Image, System.map, kernel release and compressed device-tree build directory when successful.
- SHA256SUMS for the primary outputs; build exit code if the build script was reached.

Artifact upload runs after failures too. Partial artifacts do not mean the build succeeded: check the job conclusion and build exit code. Dependency-install failures may precede creation of build-exit-code.txt.

The source and action revisions are pinned; the hosted runner and apt package versions can change. Each run records their resolved versions. This is a traceable build, not a claim of bit-for-bit reproducibility across future runner images.

## Current validation

Workflow YAML and embedded shell syntax, plus the build script's shell syntax, were checked locally. The local environment could not run a kernel build. Only a successful Actions run can advance the project to build-tested status; no hardware success follows from it.
