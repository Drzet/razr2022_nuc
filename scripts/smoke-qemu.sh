#!/usr/bin/env bash
set -Eeuo pipefail
work=$(realpath "$1")
evidence=$(realpath "$2")
[[ -s "$work/vmlinuz" && -s "$work/initrd.img" && -s "$work/rootfs.ext4" ]]
[[ "$(cat "$evidence/build-exit-code.txt")" == 0 ]]
cat > "$evidence/qemu-command.txt" <<'COMMAND'
qemu-system-aarch64 -machine virt -cpu cortex-a57 -m 2048 -smp 2 -accel tcg -nographic -monitor none -serial stdio -no-reboot -kernel vmlinuz -initrd initrd.img -append "console=ttyAMA0,115200 root=/dev/vda rw rootwait systemd.unit=multi-user.target razr.smoke=1" -drive file=rootfs.ext4,if=none,format=raw,id=vd0 -device virtio-blk-device,drive=vd0
COMMAND
set +e
timeout --signal=TERM --kill-after=15s 300s qemu-system-aarch64 -machine virt -cpu cortex-a57 -m 2048 -smp 2 -accel tcg -nographic -monitor none -serial stdio -no-reboot -kernel "$work/vmlinuz" -initrd "$work/initrd.img" -append "console=ttyAMA0,115200 root=/dev/vda rw rootwait systemd.unit=multi-user.target razr.smoke=1" -drive file="$work/rootfs.ext4",if=none,format=raw,id=vd0 -device virtio-blk-device,drive=vd0 > "$evidence/qemu-serial.log" 2>&1
rc=$?
set -e
echo "$rc" > "$evidence/qemu-exit-code.txt"
if [[ "$rc" -ne 0 ]] || ! grep -Fq 'RAZR_USERSPACE_SMOKE_PASS arch=arm64 init=systemd' "$evidence/qemu-serial.log"; then
  echo "QEMU smoke failed: exit=$rc" >&2
  tail -n 100 "$evidence/qemu-serial.log" >&2
  exit 1
fi
echo 'QEMU_SMOKE_PASS: ARM64 userspace service ran and system powered off'
