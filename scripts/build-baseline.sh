#!/usr/bin/env bash
# Build only the selected, unmodified upstream baseline.
set -euo pipefail

project_dir=$(pwd)
kernel_dir=$(realpath "${1:?kernel checkout path required}")
evidence_dir=$(realpath -m "${2:?evidence directory required}")
output_dir="$kernel_dir/.baseline-build"
mkdir -p "$evidence_dir"

finish() {
    result=$?
    trap - EXIT
    printf '%s\n' "$result" > "$evidence_dir/build-exit-code.txt"
    if [[ -f "$output_dir/.config" ]]; then
        cp "$output_dir/.config" "$evidence_dir/kernel.config"
    fi
    exit "$result"
}
trap finish EXIT

expected_sha=$(python3 - <<'PY'
import json, re
from pathlib import Path
b = json.loads(Path('configs/baseline.json').read_text())
assert b['kernel_repository'] == 'https://github.com/Drzet/linux'
assert b['configuration_base'] == 'arch/arm64/configs/defconfig'
assert not b['configuration_fragments'] and not b['external_patchsets']
assert re.fullmatch(r'[0-9a-f]{40}', b['upstream_commit'])
print(b['upstream_commit'])
PY
)
actual_sha=$(git -C "$kernel_dir" rev-parse HEAD)
[[ "$actual_sha" == "$expected_sha" ]]
[[ -z "${KERNEL_SHA:-}" || "$KERNEL_SHA" == "$expected_sha" ]]
[[ -z "$(git -C "$kernel_dir" status --porcelain --untracked-files=normal)" ]]
[[ ! -e "$output_dir" ]] # No incremental output may contaminate the clean baseline.

cp configs/baseline.json "$evidence_dir/baseline.json"
cp scripts/build-baseline.sh "$evidence_dir/build-baseline.sh"
cp .github/workflows/arm64-baseline.yml "$evidence_dir/arm64-baseline.yml"
{
    printf 'kernel_commit=%s\n' "$actual_sha"
    printf 'project_commit=%s\n' "$(git -C "$project_dir" rev-parse HEAD)"
    printf 'run_url=https://github.com/%s/actions/runs/%s\n' "${GITHUB_REPOSITORY:-local}" "${GITHUB_RUN_ID:-local}"
    printf 'runner_image=%s\nrunner_image_version=%s\n' "${ImageOS:-unknown}" "${ImageVersion:-unknown}"
    printf 'started_utc=%s\n' "$(date -u +%FT%TZ)"
    uname -a
    aarch64-linux-gnu-gcc --version
    aarch64-linux-gnu-ld --version
    gcc --version
    make --version
    flex --version
    bison --version
    cat /etc/os-release
} > "$evidence_dir/environment.txt" 2>&1
dpkg-query -W -f='${Package}\t${Version}\n' > "$evidence_dir/packages.tsv"

export ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-
export KBUILD_BUILD_USER=razr-builder KBUILD_BUILD_HOST=github-actions
export KBUILD_BUILD_VERSION=1
KBUILD_BUILD_TIMESTAMP=$(git -C "$kernel_dir" show -s --format=%cD HEAD)
export KBUILD_BUILD_TIMESTAMP
export LC_ALL=C TZ=UTC
jobs=$(nproc)
printf 'make -C %q O=%q ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig\nmake -C %q O=%q ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j%s Image dtbs\n' \
    "$kernel_dir" "$output_dir" "$kernel_dir" "$output_dir" "$jobs" > "$evidence_dir/commands.txt"
make -C "$kernel_dir" O="$output_dir" defconfig 2>&1 | tee "$evidence_dir/configure.log"
make -C "$kernel_dir" O="$output_dir" -j"$jobs" Image dtbs 2>&1 | tee "$evidence_dir/build.log"

cp "$output_dir/.config" "$evidence_dir/kernel.config"
cp "$output_dir/arch/arm64/boot/Image" "$evidence_dir/Image"
cp "$output_dir/System.map" "$evidence_dir/System.map"
cp "$output_dir/include/config/kernel.release" "$evidence_dir/kernel.release"
tar -C "$output_dir/arch/arm64/boot" -cJf "$evidence_dir/device-trees.tar.xz" dts
(
    cd "$evidence_dir"
    sha256sum Image System.map kernel.config kernel.release device-trees.tar.xz baseline.json > SHA256SUMS
)
