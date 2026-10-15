# Motorola oneli MBM: binary-backed loading analysis
Date: 2026-10-15
Scope: read-only public stock firmware; NO kernel edits or hardware flash.

## Provenance
Public Android 14 RETEU U2SLS34.1-42-14-11 stock ZIP, existing verified archive metadata. Bounded ZIP64 byte-range retrieval of compressed `bootloader.img` (~6.8 MB, not 4.35 GB archive). CRC32 verified; bootloader image SHA-256: `bcb596054b276aa3e314412e32b274be8c33b4d93dde9550f55f9a7376496ab3`.
Motorola container has `abl.elf` (SHA-256 `904890ff5ecd4e81d2e57caef883ac91d5cc8918375cf1e12017f5a846fa6e04`) and `uefi.elf` (SHA-256 `84bfc263e1b731d048c02d9523c974ee7de2fb2fc381e491985ee2331d8994ba`).
EFI firmware volumes were decompressed in isolated GitHub Actions; actual AArch64 PE modules and PC-relative string/code references traced. Raw proprietary bytes stayed ephemeral.

## Direct Motorola firmware evidence
- **Fastboot boot is coded, with a locked-device guard.** Actual ABL AArch64 at RVAs `0x8cfc-0x8d4c` branches after testing an apparent lock-state result; rejection string at RVA `0xc6954`: "Fastboot boot command is not available in locked device". The accepted path parses downloaded boot image metadata around `0x8d50`, then attempts image loading around `0x8db0`. This establishes code support, NOT that the physical phone has accepted a test.
- **Loader functions exist in the OEM executable.** Code xrefs to "LoadImageAndAuth failed: %r" at `0x2d70`, "BootLinux() failed: %r" at `0x2dbc`, and "Failed to load/authenticate boot image: %r" at `0x8dbc`.
- **Unlocked AVB continuation**: ABL code at `0x55080` logs "State: Unlocked, AvbSlotVerify returned %a, continue boot"; the UEFI `VerifiedBootDxe` module (GUID `a25f5839-4d55-428f-8f0b-5ce1d565f53e`) includes "Device is unlocked! Skipping verification!". No claim that *all* integrity or policy checks are bypassed.
- **DTB/DTBO:** actual Motorola code parses `qcom,board-id`, performs board/PMIC matching, can reuse preselected FDT (`0x200b8`) and recognizes exact DTB matches for which further DTBO search is not required (`0x6e078`). UFDT overlays, `user_dtbo` and board index selection are implemented. Stock overlay index 3 is a candidate, not proof of observed device selection.
- **Boot image/vendorramdisk:** actual executable checks vendor_boot headers and memory bounds, and references "Ramdisk Load Address" (`0x65fbc`), "Ramdisk Size Actual" (`0x66014`), `UpdateBootParamsSizeAndCmdLine` (`0x66cfc`), and Motorola bootconfig overlay (`0x8506c`). The generic/vendor ramdisk outcome for a temporary downloaded image remains untested.
- **Kernel placement:** executable references UEFI variable `KernelBaseAddr` at `0x6b598`, via a firmware call, and the FDT base memory offset at `0x6778c`. Actual placement must be derived from runtime-selected variables and subsequent relocations, not literal header offsets.
- **Memory reservations:** executable handles queries/overflows of EFI memory map and DTB/ramdisk bounds; cannot yet state exact per-device RAM map population.

## Evidence boundaries and next decisive test
Static disassembly proves the fastboot command path is *present*, but oneli is **locked in the most recent ADB capture**. Do not flash based solely on this report. The decisive next work is runtime verification on an unlocked unit, using non-flashing fastboot capability checks and a purpose-built RAM boot artifact, while capturing the selected kernel base, ramdisk and DTB details (boot logs if available). Full relocation call graph remains to be established if exact addresses are required ahead of that test.

## Reproduce
- [Successful stock member inventory](https://github.com/Drzet/razr2022_nuc/actions/runs/38804442883)
- [Decompressed EFI module inventory](https://github.com/Drzet/razr2022_nuc/actions/runs/38806210011)
- [Code xrefs and bounded AArch64 disassembly](https://github.com/Drzet/razr2022_nuc/actions/runs/38806852600)
- [Research branch](https://github.com/Drzet/razr2022_nuc/tree/research/oneli-mbm-readonly-20261015)

No release branches, coordinator docs, or kernel modified. No proprietary raw firmware checked in.
