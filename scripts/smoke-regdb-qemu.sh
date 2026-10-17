#!/usr/bin/env bash
# One focused QEMU cfg80211 NL80211_CMD_RELOAD_REGDB validation.
set -Eeuo pipefail
[[ $# == 2 ]] || { echo "usage: bash $0 WORK EVIDENCE" >&2; exit 2; }
work=$(realpath "$1")
out=$(realpath -m "$2")
mkdir -p "$out"
test -s "$work/vmlinuz" && test -s "$work/initrd.img" && test -s "$work/rootfs.ext4"
test -r /usr/lib/ipxe/qemu/efi-virtio.rom
cmd=(qemu-system-aarch64 -L /usr/lib/ipxe/qemu -machine virt -cpu cortex-a57
 -m 2048 -smp 2 -accel tcg -nodefaults -nographic -monitor none -serial stdio -no-reboot
 -kernel "$work/vmlinuz" -initrd "$work/initrd.img"
 -append 'console=ttyAMA0,115200 root=/dev/vda rw rootwait systemd.unit=multi-user.target razr.radio_runtime_smoke=1'
 -drive "file=$work/rootfs.ext4,if=none,format=raw,id=vd0" -device virtio-blk-device,drive=vd0
 -netdev 'user,id=net0' -device 'virtio-net-device,netdev=net0,mac=52:54:00:12:34:56')
printf '%q ' "${cmd[@]}" > "$out/qemu-command.txt"
printf '\n' >> "$out/qemu-command.txt"
set +e
timeout --signal=TERM --kill-after=10s 240s "${cmd[@]}" > "$out/qemu-serial.log" 2>&1
rc=$?
set -e
echo "$rc" > "$out/qemu-exit-code.txt"
if [[ $rc != 0 ]]; then
  tail -n 80 "$out/qemu-serial.log" >&2
  exit 1
fi
python3 - "$out/qemu-serial.log" <<'PY'
import pathlib,sys
s=pathlib.Path(sys.argv[1]).read_text(errors="replace")
markers=("RAZR_REGDB_TEST_START","RAZR_REGDB_KERNEL_MATCH",
         "RAZR_REGDB_DB_SHA256=", "RAZR_REGDB_SIG_SHA256=",
         "RAZR_REGDB_KERNEL_SIGNATURE_ACCEPTED","RAZR_REGDB_DOMAIN=global",
         "RAZR_REGDB_TEST_PASS","reboot: Power down")
missing=[m for m in markers if m not in s]
errors=[line for line in s.splitlines() if "RAZR_REGDB_FAIL=" in line or "RAZR_REGDB_TEST_FAIL" in line]
if missing or errors:
 print("RAZR_REGDB_QEMU_ASSERT_FAIL",missing,errors,file=sys.stderr)
 print("\n".join(s.splitlines()[-80:]),file=sys.stderr)
 sys.exit(1)
print("RAZR_REGDB_QEMU_PASS")
PY
