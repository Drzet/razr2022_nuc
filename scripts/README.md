# Build and image tooling

`build-baseline.sh` builds the exact upstream revision selected in `configs/baseline.json`, using ARM64 defconfig with no project patches or fragments. It requires a clean checkout and an installed cross-toolchain. The GitHub Actions workflow supplies these dependencies and saves the evidence.

See [CI operation and scope](../docs/BUILD_CI.md). This script does not build modules, validate DT schemas, package a phone boot image or deploy to hardware.
