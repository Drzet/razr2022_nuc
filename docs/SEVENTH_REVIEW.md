# Seventh coordinator review — 2026-10-12

**Accepted: the minimal diagnostic initramfs executes under the accepted kernel without a disk, and its exact bytes are packaged into independently inspected unsigned boot-v4/vendor_boot-v4 images.** This closes the sixth-round offline payload/structure milestone. It does not establish a runnable Motorola experiment. Kernel integration remains unchanged at `2b5acf108ae37040ac1e652e029bb37f5609e886`.

## Reviewed inputs and independently verified results

Project Boot head `cc0c55a` and Userspace head `45d75eb` were reviewed through their current handoffs and implementation. Exact tested revisions and immutable artifacts are below; no wholesale branch merge was performed.

| Owner | Tested project commit | Run / job | Accepted scope |
| --- | --- | --- | --- |
| Userspace | `0bd65e40466254c47b63f4f671f758946209fec5` | [38307910388](https://github.com/Drzet/razr2022_nuc/actions/runs/38307910388) / 115006307666 | Deterministic root-owned newc/gzip, static ARM64 BusyBox, actual diskless PID1 execution and no-trigger hold |
| Boot | `1e35aad6b6a856f6f86cdf9ba897aee5004e9abd` | [38310449244](https://github.com/Drzet/razr2022_nuc/actions/runs/38310449244) / 115014596145 | Exact accepted Image/DTB/payload construction, four fixtures and pinned independent AOSP pack/unpack section comparison |

Coordinator checked completed job steps and logs, downloaded both archives, verified ZIP digests and every enclosed checksum, and independently sliced the produced image sections from raw header sizes/offsets.

- Userspace artifact **11772559465**, ZIP SHA256 `9637a4a5e0090482428e6b9c8e8011a46131f831407352f40e381ba25fb6df6f`: **15/15** internal checksum entries match. Gzip decompresses exactly to the raw cpio. Serial records PID1=1, mount failures=0, exact release `7.3.0-rc6-g2b5acf108ae3`, READY, QEMU shutdown and Power down; exit **0**. The separate no-trigger test records HOLD, no shutdown, expected host-timeout exit **124**. It uses QEMU virt DT and no disk; neither test exercises oneli hardware.
- Boot artifact **11774750168**, ZIP SHA256 `79b865936a426e76971bacb0b91fe5a9ec0943430ae0e0cbdf4af8d477daf378`: **8/8** internal checksum entries match. AOSP crosscheck log passes. The coordinator's independent raw-header slicing reproduces accepted Image SHA256 `3a8fa9620e0fc8de68ce8db45dacdfd811a2ba2c9718f9cddee3893ec9af0939`, diagnostic gzip `3d7a08022bdff062455099d509d54c9aa571cb9c289d89a431b7edb892846f3b`, and mainline DTB `d3c9abcea9950200babbcf6c979073dc94c6af5cac68578540ad570db4a14a03`.
- `boot-candidate.UNSIGNED.img`: **53,395,456 bytes**, SHA256 `f47686e4cff28d9491ece814dd6c91c6f22eab32b3061a46f9bb935ae1fcda74`.
- `vendor_boot-candidate.UNSIGNED.img`: **118,784 bytes**, SHA256 `1b4f6379b41e22735176bf63c725d3455d47c7b510f29d0de62b408da5f47572`.

The useful `/init` is in the generic ramdisk. The vendor platform fragment is an explicitly empty 48-byte gzip/newc, named native-diag. Both command lines and bootconfig are empty; boot-v4 signature and OS-version fields are zero. Reference vendor address fields are explicit but not approved native placement. No stock signature authenticates the modified bytes; AVB is a separate unresolved handoff question. See [accepted record](../configs/accepted-native-host-2026-10-12.json).

## Source-review finding: incomplete console diagnostics

In Userspace `scripts/build-native-diag.py`, `record()` writes markers to both `/run/oneli-diag/000001.log` and `/dev/console`. However, the filtered dmesg/probe-error body is appended only to the RAM log. The console gets PROBE_ERRORS_BEGIN/END without that body. Full dmesg is also RAM-only. The payload has no shell, networking, storage persistence or log retrieval service. It therefore cannot be assumed that the user can retrieve its useful error summary merely because READY appears.

This does not invalidate the tested PID1/hold/shutdown or packaging results. It is a narrow diagnostic-quality follow-up: emit a bounded error summary to the selected console as well as RAM, with a test that checks an actual body between markers. Physical availability of that console remains a separate Boot decision. Avoid adding a new network/storage dependency to solve an output-format defect.

## Remaining decisions

1. **Native loader handoff:** which Image formats and fields the oneli bootloader actually consumes, placement/overlap constraints, mainline DT versus installed DTBO behavior, generic/vendor ramdisk concatenation and command-line merging. AOSP format correctness does not answer these Motorola-specific questions. The embedded raw Image is 52,369,920 bytes; treating reference address fields as validated absolute destinations would be unjustified.
2. **Observable early output:** a source-backed GENI UART description is not proof of an accessible physical connection. Determine the currently evidenced output/retrieval route; do not invent UART pins/voltage or persistent-memory reservations. If the route cannot be resolved offline, name the exact required physical observation and stop.
3. **Reversible first experiment:** define the minimum device observations and restoration prerequisites for the selected boot path, without assuming transient boot supports a replacement vendor_boot or that an A/B slot is automatically a backup. Unlock is not an offline blocker. No flash instruction or native-use approval is issued by this review.

Actual PVT stock overlay application remains optional reference work, not a prerequisite to re-accepting these mainline artifacts. No further stock rescan, unchanged kernel/Debian build or repeated packaging run is justified without a changed input or concrete question.

## Scheduling

Boot owns one bounded loader/output decision report. Userspace has one small diagnostic-output fix that can proceed independently against the frozen interface. Boot consumes any revised payload only after Userspace's new test and hashes are published; existing artifacts remain the accepted v1 evidence. Other agents remain paused/queued; the optional VPU DMA design remains outside this path.

If Boot reaches a genuine hardware-only evidence boundary, stop that path rather than scheduling another generic audit. Source/host validation is now substantially ahead of physical evidence; additional identical CI cannot close that gap.
