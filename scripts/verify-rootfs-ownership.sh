#!/usr/bin/env bash
# Numeric UID/GID roundtrip for exported archive (not the QEMU ext4 disk).
set -Eeuo pipefail
root=$(realpath "${1:?rootfs required}")
archive=$(realpath "${2:?tarball required}")
evidence=$(realpath -m "${3:?evidence required}")
temp=$(mktemp -d)
trap 'rm -rf "$temp"' EXIT
tar -I zstd --numeric-owner -xf "$archive" -C "$temp" ./home/razr ./usr/local/share/razr-ownership-fixture
: > "$evidence/ownership-verification.txt"
for relative in home/razr usr/local/share/razr-ownership-fixture; do
    a=$(stat -c '%u:%g:%a' "$root/$relative")
    b=$(stat -c '%u:%g:%a' "$temp/$relative")
    [[ "$a" == "$b" ]] || { printf 'FAIL %s source=%s extracted=%s\n' "$relative" "$a" "$b" | tee -a "$evidence/ownership-verification.txt"; exit 1; }
    [[ "${a%%:*}" != 0 ]] || { echo "Unexpected root-owned fixture $relative" >&2; exit 1; }
    printf 'PASS %s source=%s extracted=%s\n' "$relative" "$a" "$b" | tee -a "$evidence/ownership-verification.txt"
done
[[ "$(stat -c %u:%g "$temp/usr/local/share/razr-ownership-fixture")" == '1234:1235' ]]
cmp "$root/usr/local/share/razr-ownership-fixture" "$temp/usr/local/share/razr-ownership-fixture"
