# Motorola oneli reduced native diagnostic v4: offline launch and recovery decision

Date: **2026-10-21**. Owner: **BOOT**. State: **OFFLINE PACKAGED; HARDWARE UNTESTED; NOT APPROVED FOR FLASH OR DEVICE EXECUTION**.

## Exact, immutable offline candidate

- Pinned kernel source: `Drzet/linux@7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce`.
- Accepted reduced producer: [run 39170486506, artifact 12153785196](https://github.com/Drzet/razr2022_nuc/actions/runs/39170486506/artifacts/12153785196); release `7.3.0-rc6-oneli-reduced1-g7f3865ee17c3`; Image SHA256 `279431f997fc2334d92760d47c01aec2b8e12cf47e6d149d6a078f2347c330e8`; unchanged mainline oneli DTB SHA256 `70d5c7b08ddda1c0974ac85e95bb1328528bb533c344a0681b5e95b88cd17435`; matching module bundle SHA256 `53223f163ebf1939192d85002939b4f201cff9abf7feb5160acf63c7eebbe908`.
- Accepted native **diskless** Userspace early payload: [run 39237882830, evidence/early artifact 12180445735](https://github.com/Drzet/razr2022_nuc/actions/runs/39237882830/artifacts/12180445735), `reduced-early/radio-early.cpio.gz` SHA256 `875eb0a1b0f63dbecaefb5160775da01bd8a3bc445ca1eb016effe3717875b7c`. **Not** the Debian QEMU-only initrd or a native-storage rootfs.
- New **separate** versioned host bundle: [run 39585458990, artifact 12338654148](https://github.com/Drzet/razr2022_nuc/actions/runs/39585458990/artifacts/12338654148), ZIP SHA256 **`ad38b4167b36e7ff73baf5d82efcdd5e5fd9dafe35e8c91787e0d07953afbff8`**, **13,753,327 bytes**.
- `oneli-reduced-radio-diag-boot-v4.UNSIGNED.img`: **37,462,016 bytes**, SHA256 **`f564b46465a654ce5130095ed039f08e1ffcf7659b0d162ddb8e92f203f73d1f`**.
- `oneli-reduced-radio-diag-vendor_boot-v4.UNSIGNED.img`: **122,880 bytes**, SHA256 **`f866638f2975355ee3a9c415dd8a40b114b3468d0c1528f73b13966f26e28b61`**.
- `SHA256SUMS` plus `offline-validation.json`, AOSP unpack logs, secondary binary round-trip, source/tool identity and tested-early-init evidence are included in the downloadable artifact. All **9/9 inner checksums** were independently verified after downloading the final ZIP; the actual boot Image slice, generic gzip newc and command-line bytes were independently rehashed/read. The workflow independently used pinned AOSP `ntherning/mkbootimg@7209a7164f1772db43f92928012c86a00f6202ff` and passed unpack and matching repacked component/descriptor comparisons.

### Deterministic assembly and narrow validation

Packaging code: `scripts/package_oneli_reduced_native_diag.py` and `.github/workflows/boot-native-reduced-diag-v1.yml` at project **`razr/boot@31d75a7d784e6ed7d6d107ef2b8d2e808da13a48`**. This reuses `scripts/build_oneli_native_host_candidate.py`, `scripts/oneli_boot_v4_layout.py` and reviewed `configs/oneli-native-host-header-inputs-v1.json`. No kernel rebuild, new DTB, QEMU rerun, Motorola stock data substitution, firmware extraction or phone operation.

`boot`: Android header v4, 4096-byte layout pages, raw **uncompressed AArch64 Image** and exact **gzip radio-early newc** in the generic ramdisk field. Chosen boot header command line: `console=ttyMSM0,115200n8 loglevel=8 printk.time=1 rdinit=/init`. The **handset boot arguments deliberately omit** `razr.radio_qemu_shutdown=1`. Empty boot signature; raw OS version field 0; no AVB signature. Actual loader-supplied/overridden arguments are unobserved.

`vendor_boot`: Android header v4, 4096-byte layout pages, one raw **mainline oneli DTB**, one `platform` vendor-ramdisk entry named `native-diag` containing only a deterministic 48-byte gzip of empty newc. No stock DTB/DTBO overlays, vendor files, stock bootconfig or signing material; bootconfig size 0. Vendor header's stock-derived `kernel_addr=0x8000`, `ramdisk_addr=0x1000000`, `tags_addr=0x100`, `dtb_addr=0x1f00000` are **structural template values**, explicitly **not** asserted runtime physical placements. The Motorola ABL code instead derives placements from UEFI variables or a runtime base-memory fallback.

Userspace `/init`: verified executable, matching `pci-pwrctrl-pwrseq.ko` embedded, `RADIO_EARLY_INSMOD_OK` or failure marker followed by `RADIO_EARLY_READY_V1` and resident `RADIO_EARLY_HOLD` loop. A ready marker alone is not proof the module bound or radio enumerated. No persistent-storage root device or write operation is selected. Existing QEMU evidence belongs to Userspace, not this physical-image test.

### Actual AArch64 header and placement arithmetic

From the **new** Image: file length **36,436,480**, ARM64 magic `0x644d5241` (`ARMd`), `text_offset=0`, **`image_size=37,158,912`**, flags **`0xa`** (little endian, 4 KiB pages, physical placement); requires a **2 MiB aligned kernel base**. Image header size is **not** the same as file length, and using only file length for collision checks is incorrect.

Reused [exact Motorola MBM disassembly](https://github.com/Drzet/razr2022_nuc/blob/5a8d6ab606c825dbe776db43955c44214f7c64e3/docs/oneli_mbm_kernel_load_address_contract_2026-10-15.md) establishes on the UEFI-variable path `K=KernelBaseAddr+text_offset+O` and `E=KernelBaseAddr+KernelSize+O`. Runtime FDT offset `O`, `KernelBaseAddr`, `KernelSize` and `BaseMemory` remain unknown. With ABL's default 2 MiB DTB allowance, page 4096 and sum of the candidate generic+vendor compressed ramdisks **1,018,709 bytes**, page-rounded **1,019,904 bytes**, the conservative offline nonoverlap condition is:

`E - K >= Image.image_size + align_up(R,4096) + 2 MiB + 8192 = 40,284,160 bytes`.

This checks a **necessary nominal memory budget**, not where Motorola actually places anything. ABL's checked `dtb_address > K` is weaker than `dtb_address >= K+Image.image_size`. The 64-bit fallback `K=BaseMemory | 0x80000` may violate 2 MiB alignment, absent other runtime offsets/relocation. The unpatched native DTB also has a **zero-size /memory entry**, requiring bootloader memory fixups not demonstrated for downloaded v4 boot images. Actual RAM, carveouts, final DTB, ramdisk location and usable UART7 signal are unknown.

## Launch decision: HOLD, no demonstrated complete temporary-boot composition

The [Motorola MBM actual-code audit](https://github.com/Drzet/razr2022_nuc/blob/5a8d6ab606c825dbe776db43955c44214f7c64e3/docs/oneli_mbm_actual_code_analysis_2026-10-15.md) verifies a **coded `fastboot boot` path** and a locked-device rejection branch. It **does not** establish a command accepting both candidate images in RAM, or show that an ordinary downloaded `boot.img` causes ABL to replace the installed `vendor_boot`, use its mainline DTB, avoid a vendor DTBO override, and assemble the generic/vendor ramdisks as intended. A one-file temporary boot could instead combine the candidate boot image with **existing stock vendor_boot, vendor DTBs and DTBO**, which is *not* this tested bundle. The unsigned v4 candidate also has **no demonstrated AVB/bootloader authorization**.

A defensible hardware launch requires **all** of the following as *future observations/approvals*, not assertions: (1) appropriate authorized loader mode; (2) a demonstrated non-writing RAM-only path for **both** these boot and vendor_boot components, or a separately approved equivalent loader capable of explicitly loading the mainline DTB; (3) log/probe evidence of actual chosen DTB, ramdisk, bootargs and 2 MiB-aligned Image placement without reserved-memory overlaps; (4) usable UART7 physical TX/ground/logic reference or another proved diagnostic output; and (5) a demonstrated method of returning to original stock state. **No device-side boot command is currently approved because the full composition path is unproved.**

### Bounded recovery plan (future authorized trial only)

Keep existing stock boot/vendor_boot/DTBO/vbmeta, slots and AVB state **unchanged**; do not flash, switch slots, or overwrite partitions to test this bundle. First establish an approved **temporary**, no-write load route and a known-good recovery/exit from that route on the device. If a later controlled temporary trial hangs or produces no UART output, stop it using the device's supported hardware reboot/recovery route and verify return to the unchanged stock system before trying anything else. If the only available launch route writes partitions, this candidate must **remain on hold** until a separate, source-backed installation, rollback, compatible stock-image backup/restore and authorization plan is reviewed. This document intentionally supplies **no partition names, flashing or slot commands**.

Existing accepted diagnostic-v2 artifacts, full radio build and accepted integration manifest remain untouched. BOOT delivers the **offline bundle** for coordinator review and stops.
