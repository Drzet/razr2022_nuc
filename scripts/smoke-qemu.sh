#!/usr/bin/env bash
set -Eeuo pipefail
work=$(realpath "${1:?work}")
evidence=$(realpath "${2:?evidence}")
port=${RAZR_QEMU_SSH_PORT:-2222}
[[ "$port" =~ ^[0-9]+$ && "$port" -ge 1024 && "$port" -le 65535 ]]
[[ "$(cat "$evidence/build-exit-code.txt")" == 0 ]]
[[ -s "$work/vmlinuz" && -s "$work/initrd.img" && -s "$work/rootfs.ext4" && -s "$work/ssh_id_ed25519" ]]
test -r /usr/lib/ipxe/qemu/efi-virtio.rom || { echo "Missing efi-virtio.rom: install ipxe-qemu" >&2; exit 2; }
sha256sum /usr/lib/ipxe/qemu/efi-virtio.rom > "$evidence/qemu-rom-sha256.txt"
qemu-system-aarch64 --version > "$evidence/qemu-version.txt"
cmd=(qemu-system-aarch64 -L /usr/lib/ipxe/qemu -machine virt -cpu cortex-a57 -m 2048 -smp 2 -accel tcg -nodefaults -nographic -monitor none -serial stdio -no-reboot
 -kernel "$work/vmlinuz" -initrd "$work/initrd.img"
 -append "console=ttyAMA0,115200 root=/dev/vda rw rootwait systemd.unit=multi-user.target razr.smoke=1"
 -drive "file=$work/rootfs.ext4,if=none,format=raw,id=vd0" -device virtio-blk-device,drive=vd0
 -netdev "user,id=net0,restrict=on,hostfwd=tcp:127.0.0.1:$port-:22" -device virtio-net-device,netdev=net0,mac=52:54:00:12:34:56)
printf '%q ' "${cmd[@]}" > "$evidence/qemu-command.txt"
printf '\n' >> "$evidence/qemu-command.txt"
timeout --signal=TERM --kill-after=10s 600s "${cmd[@]}" > "$evidence/qemu-serial.log" 2>&1 &
pid=$!
cleanup() { kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; }
trap cleanup EXIT
fail() { echo "$1" >&2; tail -n 100 "$evidence/qemu-serial.log" >&2; tail -n 30 "$evidence/ssh-command.log" 2>/dev/null >&2 || true; exit 1; }
echo pending > "$evidence/qemu-boot-status.txt"
for ((i=0;i<150;i++)); do
  if grep -Fq 'RAZR_USERSPACE_SMOKE_PASS arch=arm64 init=systemd' "$evidence/qemu-serial.log"; then echo passed > "$evidence/qemu-boot-status.txt"; break; fi
  kill -0 "$pid" 2>/dev/null || break
  sleep 2
done
[[ "$(cat "$evidence/qemu-boot-status.txt")" == passed ]] || fail 'BOOT_FAILED: no guest systemd marker'
echo pending > "$evidence/qemu-ssh-status.txt"
echo 'guest SSH command checks architecture, PID 1, configured IPv4 and prints routing evidence' > "$evidence/ssh-acceptance-contract.txt"
opts=(-i "$work/ssh_id_ed25519" -p "$port" -o BatchMode=yes -o PreferredAuthentications=publickey -o PasswordAuthentication=no
 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=3 -o ConnectionAttempts=1)
for ((i=0;i<36;i++)); do
  if ssh "${opts[@]}" razr@127.0.0.1 'printf "RAZR_SSH_CONNECTED arch=%s pid1=%s\\n" "$(dpkg --print-architecture)" "$(cat /proc/1/comm)"; ip -4 -o address show scope global; ip -4 route show; test "$(dpkg --print-architecture)" = arm64 && test "$(cat /proc/1/comm)" = systemd && test -d /run/systemd/system && ip -4 -o address show scope global | grep -q "inet " && echo RAZR_NETWORK_SSH_PASS' > "$evidence/ssh-command.log" 2>&1; then
    if grep -Fq RAZR_NETWORK_SSH_PASS "$evidence/ssh-command.log"; then echo passed > "$evidence/qemu-ssh-status.txt"; break; fi
  fi
  kill -0 "$pid" 2>/dev/null || break
  sleep 2
done
[[ "$(cat "$evidence/qemu-ssh-status.txt")" == passed ]] || fail 'SSH_FAILED: no authenticated guest command after successful boot'
# Project staging creates an immutable tested kernel identity. Never allow this
# mode to silently fall back to the older generic Debian-kernel smoke path.
if [[ -f "$work/project-context.env" ]]; then
  source "$work/project-context.env"
  [[ -n "$RELEASE" && -n "$MODULE" ]] || fail 'PROJECT_MODULE_FAILED: incomplete bundle identity'
  [[ -z "${RAZR_PROJECT_KERNEL_RELEASE:-}" || "$RAZR_PROJECT_KERNEL_RELEASE" == "$RELEASE" ]] ||
    fail 'PROJECT_MODULE_FAILED: requested release mismatches selected Image'
  [[ -z "${RAZR_PROJECT_QEMU_MODULE:-}" || "$RAZR_PROJECT_QEMU_MODULE" == "$MODULE" ]] ||
    fail 'PROJECT_MODULE_FAILED: requested module mismatches selected build'
  RAZR_PROJECT_KERNEL_RELEASE="$RELEASE"
  RAZR_PROJECT_QEMU_MODULE="$MODULE"
fi
# Mandatory for a project-kernel test: real loadable project module.
if [[ -n "${RAZR_PROJECT_KERNEL_RELEASE:-}" || -n "${RAZR_PROJECT_QEMU_MODULE:-}" ]]; then
  release=${RAZR_PROJECT_KERNEL_RELEASE:-}
  module=${RAZR_PROJECT_QEMU_MODULE:-}
  [[ "$release" =~ ^[A-Za-z0-9._+~-]+$ && "$module" =~ ^[A-Za-z0-9_-]+$ ]] ||
    fail 'PROJECT_MODULE_FAILED: exact release and module are both required'
  normalized=${module//-/_}
  if ! ssh "${opts[@]}" razr@127.0.0.1 \
    "test \"\$(uname -r)\" = '$release' && sudo -n /usr/sbin/modprobe '$module' && grep -Eq '^$normalized[[:space:]]' /proc/modules && echo RAZR_PROJECT_MODULE_LOAD_PASS" \
    > "$evidence/project-module-command.log" 2>&1; then
    fail 'PROJECT_MODULE_FAILED: kernel release, real load or module listing did not pass'
  fi
  grep -Fq RAZR_PROJECT_MODULE_LOAD_PASS "$evidence/project-module-command.log" ||
    fail 'PROJECT_MODULE_FAILED: missing authenticated load marker'
fi
if ! ssh "${opts[@]}" razr@127.0.0.1 'sudo -n /usr/bin/systemctl poweroff' >> "$evidence/ssh-command.log" 2>&1; then
  echo "Shutdown command was not accepted" >&2
  exit 1
fi
set +e
wait "$pid"
rc=$?
set -e
echo "$rc" > "$evidence/qemu-exit-code.txt"
trap - EXIT
[[ "$rc" -eq 0 ]] || fail "SHUTDOWN_FAILED: QEMU exit=$rc"
echo 'QEMU_SYSTEMD_NETWORK_SSH_PASS'
