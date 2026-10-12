# Next assignments — seventh coordinator review, 2026-10-12

Read [SEVENTH_REVIEW.md](SEVENTH_REVIEW.md). The diskless diagnostic payload and unsigned host packaging are accepted. Kernel integration stays `2b5acf108ae37040ac1e652e029bb37f5609e886`; do not rebuild it unchanged. [Accepted artifact record](../configs/accepted-native-host-2026-10-12.json) pins the current result. These assignments supersede [the sixth queue](SIXTH_ASSIGNMENTS.md).

## Boot — primary: resolve the native loader/output handoff

The build/package task is finished. Produce one bounded decision document and machine-readable readiness record covering:

1. **Loader input and memory placement.** Use pinned oneli stock metadata and attributable bootloader/public source evidence to determine accepted kernel format, ARM64 Image-header size/offset semantics, fields actually consumed from boot/vendor_boot, placement and alignment constraints, and whether sections could overlap. Inspect the accepted Image header. Do not treat stock 0x8000/0x1000000/0x1f00000 fields as confirmed physical destinations, or AOSP unpack as proof of Motorola behavior. Distinguish generic documented behavior, device evidence and `[INFERRED]` assumptions.
2. **DT/ramdisk/cmdline selection.** Determine how the mainline DT would be selected and whether installed stock DTBO could be applied to it; define generic/vendor ramdisk combination and who supplies the early-console command line. Empty host-only headers are a deliberate test policy, not a finished phone configuration. Distinguish boot-v4 signature from partition AVB handling. Use existing derived artifacts first; retrieve only a specifically necessary bounded member with recorded hashes if evidence is genuinely missing. No broad ROM scan.
3. **Actual diagnostic route.** Inventory what is known about accessible UART or another early-log retrieval path. Separate the GENI source node/config from physical pin/voltage/access evidence. Do not select USB gadget, display or persistent logging merely because corresponding frameworks exist. State exactly what source work remains possible and which observation needs the device.
4. **First experiment prerequisites.** Describe the intended reversible test sequence and the exact device facts it requires: bootloader command capability, partition/slot behavior, available original recovery images and a proven restoration route. Do not assume a transient boot command replaces vendor_boot, or assume an untouched slot is a complete backup. No guessed executable flash commands and no device mutation. Unlock is already owner-managed, not a reason to stop offline work.

Acceptance: a small per-decision table with source, selected behavior or unresolved input, owner and next observable check. If device evidence is necessary, mark the path blocked there and stop. Do not create another structurally identical image or another broad report to occupy the round. Actual stock overlay apply is optional only if it resolves a named question above.

Userspace's small fix below is independent. Repackage only once a new tested payload exists and only to update its exact hashes; preserve accepted v1 provenance. Coordinator retains integration/aggregate ownership.

## Userspace — one bounded diagnostic-output fix

The initramfs producer, no-disk QEMU execution and intentional HOLD behavior are accepted. No repeat Debian/rootfs/kernel work.

- Correct `scripts/build-native-diag.py` so the bounded probe-error summary between PROBE_ERRORS_BEGIN/END reaches the console as well as the volatile log. Current code appends its body only to RAM; READY alone does not expose those diagnostics. Keep full dmesg storage bounded to the intended volatile scope and record read/output failures without crashing PID1.
- Exercise a deterministic nonempty error-summary fixture and assert that the console-facing output includes its content, not only the markers. Preserve no persistent writes, no storage/network dependencies, and resident PID1 behavior. Do not add a shell or daemon as an unrelated expansion.
- Because `/init` changes, publish a new versioned payload/hash manifest and one corresponding diskless QEMU run demonstrating the actual changed output/normal hold semantics. Hand the exact artifact to Boot. Do not silently replace v1 hashes or count old serial evidence as testing new bytes.

After the artifact handoff, wait for Boot's selected physical diagnostic route. Do not infer that QEMU ttyAMA0 is the phone console.

## Other agents

GPU and Power remain paused. USB remains queued; resume only if a separately reviewed USB diagnostic/access requirement or the existing PS5169 work is selected. DisplayPort remains held on AUX identity. VPU's optional bounded DMA ownership design from the sixth queue remains valid, independent of this milestone; no new extraction round or request to start all agents.

## Coordinator acceptance / stop conditions

Preserve current combined kernel and host-candidate references. Review Boot's loader/output decision and revised Userspace payload before changing the native readiness designation. Current designation is **host-validated, device handoff unresolved**. Retain successful artifacts before Actions expiry by copying verified outputs rather than rebuilding. Hardware-only unknowns require hardware evidence; neither repeated emulation nor more packaging tests can resolve them.
