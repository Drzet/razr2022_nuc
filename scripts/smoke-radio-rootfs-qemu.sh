#!/usr/bin/env bash
# Real QEMU virt boot of the immutable signed-radio Debian rootfs on its matching kernel.
set -Eeuo pipefail
[[ $# == 2 ]] || { echo "usage: bash $0 PREPARED-WORKDIR EVIDENCE-DIR" >&2; exit 2; }
work=$(realpath "$1")
evidence=$(realpath -m "$2")
mkdir -p "$evidence"
test -s "$work/vmlinuz"
test -s "$work/initrd.img"
test -s "$work/rootfs.ext4"
test -r /usr/lib/ipxe/qemu/efi-virtio.rom
qemu-system-aarch64 --version > "$evidence/qemu-version.txt"
cmd=(qemu-system-aarch64 -L /usr/lib/ipxe/qemu
    -machine virt -cpu cortex-a57 -m 2048 -smp 2 -accel tcg
    -nodefaults -nographic -monitor none -serial stdio -no-reboot
    -kernel "$work/vmlinuz" -initrd "$work/initrd.img"
    -append 'console=ttyAMA0,115200 root=/dev/vda rw rootwait systemd.unit=multi-user.target razr.radio_runtime_smoke=1'
    -drive "file=$work/rootfs.ext4,if=none,format=raw,id=vd0" -device virtio-blk-device,drive=vd0
    -netdev 'user,id=net0' -device 'virtio-net-device,netdev=net0,mac=52:54:00:12:34:56')
printf '%q ' "${cmd[@]}" > "$evidence/qemu-command.txt"
printf '\n' >> "$evidence/qemu-command.txt"
set +e
timeout --signal=TERM --kill-after=10s 360s "${cmd[@]}" > "$evidence/qemu-serial.log" 2>&1
rc=$?
set -e
echo "$rc" > "$evidence/qemu-exit-code.txt"
if [[ $rc != 0 ]]; then
    tail -n 125 "$evidence/qemu-serial.log" >&2
    echo "RADIO_ROOTFS_QEMU_FAILED: exit=$rc" >&2
    exit 1
fi
python3 - "$evidence/qemu-serial.log" <<'PY'
import pathlib,sys
raw=pathlib.Path(sys.argv[1]).read_bytes().decode("utf-8","replace")
markers = [
 "RAZR_RADIO_RUNTIME_BEGIN",
 "RAZR_RADIO_SYSTEMD_PID1_PASS",
 "RAZR_RADIO_RELEASE_PASS",
 "RAZR_RADIO_PREPOWER_PRESENT_PASS",
 "RAZR_RADIO_MODULE_LOAD_PASS",
 "RAZR_RADIO_DBUS_PASS",
 "RAZR_RADIO_BLUEZ_UNIT_PRESENT",
 "RAZR_RADIO_NM_ACTIVE_PASS",
 "RAZR_RADIO_IPV4_PASS",
 "RAZR_RADIO_ROUTE_PASS",
 "RAZR_RADIO_RESOLVER_CONFIG_PASS",
 "RAZR_RADIO_DNS_LOOKUP_PASS",
 "RAZR_RADIO_RUNTIME_FAILURES=0",
 "RAZR_RADIO_RUNTIME_SMOKE_PASS",
 "reboot: Power down",
]
missing=[marker for marker in markers if marker not in raw]
bad=[line for line in raw.splitlines() if "RAZR_RADIO_CHECK_FAIL=" in line or "RAZR_RADIO_RUNTIME_SMOKE_FAIL" in line]
if missing or bad:
    print("RADIO_ROOTFS_QEMU_ASSERTION_FAILED",missing,bad,file=sys.stderr)
    print("\n".join(raw.splitlines()[-125:]),file=sys.stderr)
    raise SystemExit(1)
print("RADIO_ROOTFS_QEMU_SMOKE_PASS")
PY
