# Subsystem handoff: Boot seventh-round native loader/output decision

- **Date / originating chat:** 2026-10-12, Boot resumed after coordinator seventh review and issue #10/#13 instructions.
- **Repository / branch / exact decision commits:** Drzet/razr2022_nuc, razr/boot. Decision document commit **70edf1cc27eee6b33c8a01b35a2bf0481b0e386f**, machine-readiness commit **506f24ba0e480f8fa08a594753414039720c8de3**. This handoff advances the branch head.
- **Initial upstream baseline:** a5ebb76233b79db01e82e061173cb73c6d2b5c6b. Accepted combined kernel: **2b5acf108ae37040ac1e652e029bb37f5609e886** (unchanged Drzet/linux:razr/integration).
- **Required board/support / Userspace:** accepted oneli mainline DTB SHA256 d3c9abcea9950200babbcf6c979073dc94c6af5cac68578540ad570db4a14a03. Accepted Userspace v1 diagnostic artifact 11772559465, exact source 0bd65e40466254c47b63f4f671f758946209fec5. Boot v1 host candidate artifact 11774750168, source 1e35aad6b6a856f6f86cdf9ba897aee5004e9abd. All accepted artifacts preserved.
- **Evidence classes:** direct accepted-binary inspection **performed**; pinned ARM64/AOSP/driver source interpretation **researched**; versioned document + machine record **implemented**; prior unchanged kernel/QEMU/AOSP host packaging **accepted**; no new executable test, no fresh build, no Motorola runtime test.

## Changes and provenance

[Decision report](../oneli_native_loader_output_decision_2026-10-12.md) and [machine readiness](../../configs/oneli-native-loader-readiness-v1.json) follow current [SEVENTH_REVIEW](https://github.com/Drzet/razr2022_nuc/blob/main/docs/SEVENTH_REVIEW.md) and [NEXT_TASKS](https://github.com/Drzet/razr2022_nuc/blob/main/docs/NEXT_TASKS.md).

1. Independently extracted and SHA-verified accepted kernel **Image** from combined artifact 11768562884. Parsed AArch64 header: file length **52,369,920**; effective image_size **53,215,232**, text_offset **0**, flags **0xa**, magic **0x644d5241**, PE header offset **64**. [Pinned kernel boot protocol](https://github.com/Drzet/linux/blob/2b5acf108ae37040ac1e652e029bb37f5609e886/Documentation/arch/arm64/booting.rst) requires the 2MiB-aligned base plus offset, full effective Image reservation, 8-byte aligned DTB, and a qualifying initrd window. File-end alone understates needed image memory by **845,312** bytes.
2. Proved the existing public stock raw vendor header addresses **cannot simply be accepted as absolute physical locations**: hypothetical kernel [0x8000,0x32c8000) is unaligned and contains nominal ramdisk 0x1000000 and DTB 0x1f00000. AOSP [bootimg v4 source](https://android.googlesource.com/platform/system/tools/mkbootimg/+/refs/heads/main/include/bootimg/bootimg.h) describes addresses as physical. [INFERRED] MBM may adjust a vendor base or perform relocation, but no oneli-specific loader code/trace proves it; actual placements remain null.
3. Parsed accepted mainline DTB as FDT (898 nodes, 3,418 properties): /memory@a0000000/reg **size zero**, no /chosen/bootargs or /__symbols__, and source-backed /chosen/stdout-path alias to enabled UART7 0x99c000. Real RAM topology and console command source require loader input. Motorola's PVT index-3 overlay uses OEM symbol fixups; it cannot be assumed to apply unchanged to the symbol-less mainline compiled DTB. Do not apply stock DTBO or reconstruct FDTs from filtered JSON.
4. Distinguished AOSP generic vendor-then-generic ramdisk order/bootconfig trailer, the deliberate host empty gzip vendor newc + diagnostic generic newc, OEM-specific still-unobserved vendor selection, command line and AVB policy. Verified device stock ADB source reports exact MBM string, model/board PVT, slot _a at capture and separately named A/B boot/vendor_boot/dtbo/recovery/vbmeta. Those are *names*, not partition dumps or proven restore coverage.
5. Restricted output path to GENI UART7 source candidate, **no physical pinout/voltage/receiver evidence**; no invented pstore carveout, USB/display console. Required precise on-device observations, coherent original image/restoration inventory and read-only bootloader capability before any native trial. No flashing or assumed safe unused slot.

## Shared files / integration

Only Boot-owned new document, new configs JSON and this handoff were added. **No** Drzet/linux changes, main aggregate STATUS/NEXT_TASKS edits, Userspace changes, kernel/integration branch movement or candidate rebuild. The accepted sixth/seventh CI artifacts remain immutable. Do not overwrite the prior blocked-before-Userspace JSON (historical state).

## Validation

- Input Image SHA256 verified against accepted integration manifest; ARM64 header decoded from actual 64-byte file prefix. Effective-size/memory-conflict arithmetic checked.
- Mainline DTB SHA256 verified, FDT header/token scan (898 nodes, 3,418 properties), and chosen/aliases/memory properties inspected from actual compiled blob. /__symbols__ absence checked on parsed FDT node inventory.
- Reviewed source: exact Drzet/linux ARM64 boot protocol, Image definitions, oneli DTS and GENI driver; AOSP boot-v4 header, vendor-ramdisk order, bootconfig, AVB and A/B docs; actual 2026-10-11 Motorola ADB observation and VPU stock derived hashes.
- **No new CI or hardware test**; prior accepted Image/modules/DT run 38292394177, diskless Userspace PID1 run 38307910388 and Boot unsigned structural run 38310449244 are *not* new evidence produced by this decision round.

## Blockers / concrete next acceptance check

1. Obtain **attributable oneli MBM** kernel/DTB/ramdisk placement and source or physical boot trace; establish non-overlap using actual memory map and the Image header's effective allocation.
2. Determine selected loader FDT/DTBO and injected real RAM, actual bootargs, ramdisk concatenation/compression and AVB per-slot treatment.
3. Establish safe reachable UART receiver or independently proven early output route.
4. Inventory installed per-slot partition hashes, status, original OEM recovery images, read-only bootloader temporary-boot capability and a **demonstrated** restoration path. Do not assume flash commands or unchanged inactive slot solve it.
5. **Hold native trial** until all gates above are evidenced and coordinator reviews readiness. Optional stock-base+PVT overlay application is not the missing native loader selection. No broad stock download or unchanged build.
6. Userspace seventh-round summary-to-console change proceeds separately. Boot consumes a newer payload **only after** changed hash manifest and distinct diskless QEMU proof; preserve accepted v1 until then.

**Disposition:** host-validated, native device handoff blocked; exact blocking facts published for coordinator. No ROM/hardware access was assumed.
