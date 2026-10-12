# Userspace native diagnostic initramfs v1: accepted QEMU-only payload

- Date / owner: 2026-10-12, Userspace.
- Repository / source branch: Drzet/razr2022_nuc, \`razr/userspace\`.
- Exact tested Userspace commit: \`0bd65e40466254c47b63f4f671f758946209fec5\`.
- Accepted kernel: Drzet/linux \`razr/integration\` at \`2b5acf108ae37040ac1e652e029bb37f5609e886\`; baseline \`a5ebb76233b79db01e82e061173cb73c6d2b5c6b\` unchanged.
- Typed Boot contract: \`configs/oneli-native-early-initramfs-interface-v1.json\` at \`razr/boot\` revision \`a7119d5f6b1c1f8be8fbbc018dbefcfccf796c7e\`, exact JSON Git blob SHA1 \`710c2681734f699e456d3a673a27f851f202a7e3\`. Userspace explicitly ACKed unchanged on [coordination issue #13](https://github.com/Drzet/razr2022_nuc/issues/13#issuecomment-6132346098).
- Evidence: **new standalone no-disk QEMU-virt ARM64 PID1 execution PASS**; native Motorola phone **NOT tested**. Existing Debian/systemd/modprobe QEMU milestone was not repeated.

## Payload producer and runtime

- Script \`scripts/build-native-diag.py\`: checks accepted Image, generated config and mainline oneli DTB exact hashes; rejects wrong-arch or PT_INTERP/dynamic BusyBox ELF; builds C-sorted deterministic newc with UID/GID=0, mtime=0, aligned records, trailer, deliberate \`dev/console\` and \`dev/null\` char devices; \`gzip -n -9\` companion; independently parses/verifies both formats and exact bytes; issues typed \`oneli-diag-payload-v1.json\` only after actual QEMU evidence.
- The static runtime is SHA-pinned Debian trixie ARM64 \`busybox-static\` revision \`1:1.37.0-6+b9\`: package SHA256 \`c833be48abfa16bc19c4966ec93e289ff1ce5d2f1476cad3a57bd105378cd15c\`; extracted ELF SHA256 \`7d93682be37cf6ed46699f6fff546b80bf133cf8ec342c2d04bc23387f78bc34\`. Package architecture/version and static AArch64 ELF were checked.
- \`/init\` (PID1) mounts proc, sysfs, devtmpfs, tmpfs; captures failures, uname, cmdline, DT compatible, dmesg/probe events under volatile \`/run/oneli-diag/000001.log\`; emits \`RAZR_NATIVE_DIAG_READY_V1\` via console and best-effort kmsg; otherwise remains resident. Explicit \`razr.diag_test_shutdown=1\` only powers off when QEMU generated DT identifies \`linux,dummy-virt\`. It neither mounts nor writes persistent storage, loads modules, starts networking/USB, or calls vendor firmware.
- The accepted generated config checked \`CONFIG_ARM64\`, \`BLK_DEV_INITRD\`, \`RD_GZIP\`, \`BINFMT_SCRIPT\`, \`PROC_FS\`, \`SYSFS\`, \`DEVTMPFS\`, \`TMPFS\`, both PL011 and Qualcomm GENI UART/console built in. Module and firmware arrays are deliberately empty with separate scoped rationales; 1,702 combined-build modules do not belong in a minimal diagnostic archive.
- \`.github/workflows/userspace-native-diag.yml\`: pins the accepted producer tar SHA256, Boot contract Git blob and BusyBox package digest; tests eight synthetic positive/negative archive/ELF fixtures; independent GNU cpio list and root-owned extraction; exact Image-only QEMU virt with generated DT, no disk or Debian rootfs. Existing Debian/systemd and combined-kernel module CI are unchanged.

## Immutable result and exact hashes

- **Successful [Actions run 38307910388](https://github.com/Drzet/razr2022_nuc/actions/runs/38307910388)**, job \`115006307666\`, source commit \`0bd65e40466254c47b63f4f671f758946209fec5\`.
- Artifact \`native-diag-v1-38307910388-1\`, artifact ID \`11772559465\`; GitHub ZIP digest SHA256 \`9637a4a5e0090482428e6b9c8e8011a46131f831407352f40e381ba25fb6df6f\`. Artifact retention is 30 days from run (through about 2026-11-11).
- Raw \`oneli-diag-initramfs.cpio\` SHA256 \`6805a3482e2946c3aca60f52c9c91711f5cde5720e30a5230df3fb4829e2ea4e\`.
- \`oneli-diag-initramfs.cpio.gz\` SHA256 \`3d7a08022bdff062455099d509d54c9aa571cb9c289d89a431b7edb892846f3b\`.
- Embedded \`/init\` SHA256 \`31cba1801f6ecbd17a31b5b81755d6dc51071a8587bbb782ceecc3ec905328c4\`.
- Positive \`qemu-serial.log\` SHA256 \`84152346608e01fd719d60dde36c529bd4e78129845df0bd239d26206f782fa4\`. Full artifact has \`oneli-diag-payload-v1.json\`, \`build-inputs.json\`, \`newc-listing.json\`, independent GNU cpio listing and compressed-file listing, Boot source verification transcript, exact QEMU command, positive and hold serial logs, exit-code files, and \`SHA256SUMS\`.
- Independent ZIP download and inspection after CI: ZIP digest matches GitHub metadata; all 15 enclosed \`SHA256SUMS\` entries verified; raw/gzip bytes identical when decompressed; typed manifest's cpio, compressed, init and serial hashes validated. \`SHA256SUMS\` excludes itself and is checked after writing.

## Executed QEMU acceptance

The CI command uses \`qemu-system-aarch64 -L /usr/lib/ipxe/qemu -machine virt -cpu cortex-a57 -m 1024 -smp 2 -accel tcg -nodefaults -nographic -serial stdio -monitor none -no-reboot\`, accepted kernel Image and diagnostic gzipped newc, with **no block device** and **no manually supplied oneli DTB**. Positive test QEMU cmdline: \`console=ttyAMA0,115200 rdinit=/init razr.diag_test_shutdown=1\`.

Positive serial records exact kernel release \`7.3.0-rc6-g2b5acf108ae3\`, \`RAZR_NATIVE_DIAG_PID1=1\`, \`RAZR_NATIVE_DIAG_MOUNT_FAILURES=0\`, \`linux,dummy-virt\`, \`RAZR_NATIVE_DIAG_READY_V1\`, \`RAZR_NATIVE_DIAG_QEMU_SHUTDOWN\`, and \`reboot: Power down\`. QEMU exit code **0**.

Negative hold test omits \`razr.diag_test_shutdown\`, records \`RAZR_NATIVE_DIAG_READY_V1\` and \`RAZR_NATIVE_DIAG_HOLD\`, and detects **no** shutdown marker or kernel power down before the bounded 12-second host timeout. Exit **124** is an expected, validated *host timeout* in this negative test, not a crashing guest. Eight synthetic archive/ELF fixtures also passed. Neither test is hardware emulation of Qualcomm/oneli.

Earlier exploratory source commits had CI failures from a package URL 404, selecting same-named BusyBox packaging files, YAML heredoc indentation and missing QEMU ROM path; these failures remain visible in workflow history. Accepted run \`38307910388\` corrected and passed all steps; do not repeat it unchanged.

## Boot handoff and remaining gates

Boot should consume the **exact** artifact \`11772559465\` and typed payload manifest, independently validate both cpio hashes, \`/init\`, accepted Image/config/DTB identities and serial evidence, then perform its separately owned **unsigned, host-only** Android boot-v4/vendor_boot-v4 structure packing and independent AOSP unpack/hash/section-bound checks. Do not add stock Android vendor ramdisk implicitly or treat known stock reference load addresses, vendor fragments, boot signatures or overlays as approved native placement. If an exact required input is absent, publish machine-readable blocked evidence rather than inventing a flashable image.

Phone-only gates remain Motorola bootloader acceptance/AVB, selected native DT and cmdline, verified physical UART/console observation, and hardware runtime. No native phone image or flash procedure was approved. QEMU's PL011 serial \`ttyAMA0\` is not Motorola's physical Qualcomm \`ttyMSM\`.
