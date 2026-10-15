# Oneli Motorola ABL kernel load address contract: static reverse-engineering decision
**Date:** 2026-10-15. **Scope:** bounded independent read-only inspection of publicly distributed XT2251-1 RETEU Android 14 bootloader. **Status:** static address contract RESOLVED; final *runtime* physical locations require UEFI/FDT inputs. No kernel, coordinator, or device change.

## Exact source and reproducibility
- Motorola firmware `U2SLS34.1-42-14-11`, outer ZIP SHA-256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c` (verified in prior stock-source job; not re-downloaded here).
- Bounded HTTP 206 ZIP member `bootloader.img`: length 29,116,160 bytes, CRC32 `bf11c10f`, SHA-256 `bcb596054b276aa3e314412e32b274be8c33b4d93dde9550f55f9a7376496ab3`. Each research job downloaded ~6.76 MB compressed, never the ~4.35-GB archive.
- Embedded Motorola `abl.elf`, decompressed firmware-volume Linux loader PE: SHA-256 `5e6db9577a35ec5a5e9c848e271e13048b9ba71a47311d64f0a29b78500eb3ca`. Code architecture AArch64; offsets here are **PE RVAs, not RAM addresses**.
- Successful exact-code disassembly job [38808611568](https://github.com/Drzet/razr2022_nuc/actions/runs/38808611568); successful independent compiled-literal inspection job [38809199858](https://github.com/Drzet/razr2022_nuc/actions/runs/38809199858). Artifacts contain structural disassembly/metadata, **no firmware executables**.
- Accepted kernel [native loader decision](https://github.com/Drzet/razr2022_nuc/blob/razr/boot/docs/oneli_native_loader_output_decision_2026-10-12.md): Linux `Image` SHA-256 `3a8fa9620e0fc8de68ce8db45dacdfd811a2ba2c9718f9cddee3893ec9af0939`, ARM64 magic, `text_offset=0`, `image_size=0x032c0000=53,215,232` bytes, flags `0xa` (4K pages, relocatable physical placement). Its **file length is not the required RAM allocation**.

## Loader decisions proved by the actual Motorola code
1. ABL `QueryBootParams` at **RVA 0x6b508** reads UEFI variables `KernelBaseAddr` then `KernelSize` using indirect UEFI GetVariable calls (**0x6b598 / 0x6b5e0**). The result is treated as successful only when both calls return success (**0x6b5ec..0x6b640**).
2. In `UpdateBootParams` (**0x673d0..0x67914**) with successful UEFI queries:
   - `B = KernelBaseAddr` and `Z = KernelSize`;
   - for a 64-bit **uncompressed** ARM64 Image with **nonzero image_size**, `K = B + Image.text_offset` (**0x67584..0x675cc**); `E = B + Z` (**0x675ec..0x67600**);
   - for legacy Image `image_size=0`, or a gzip-compressed Image, `K = B + 0x80000` (**0x6759c..0x675e0**). ABL's gzip probe at **0x6c0a8..0x6c12c** requires bytes `1f 8b 08`. The current uncompressed accepted Image does not use this branch.
   - for 32-bit kernel, `K = B + 0x8000` (**0x67560..0x67580**).
3. If either UEFI GetVariable fails (**0x67608..0x676dc**), the **compiled 64-bit fallback** is `K = M | 0x80000` and `E = M + 0x06400000` (**100 MiB**), where `M = BootParamlist.BaseMemory`. The literal values were read from *this Motorola ABL* at PE RVAs **0xc4920 = 0x00080000**, **0xc4924 = 0x06400000**. The 32-bit fallback uses `M | 0x8000`, `E = M + 0x03c00000` (**60 MiB**) from RVAs **0xc492c** / **0xc4928**.
4. ABL reads optional FDT `/kernel/devicetree_space_size` (**0x674a0..0x67530**), overriding the default **0x200000 (2 MiB)**; a second `/kernel` property populates a 32-bit **base memory offset** `O`, added to **both** `K` and `E` at **0x67730..0x677ec**. Without an override, these default to 2 MiB and 0 respectively. The property value on the installed PVT has **not** been observed.
5. ABL then places the ramdisk and DTB **downward from the end of the reserved kernel region** (**0x677f4..0x6784c**):
   ```text
   P     = boot image page size (4,096 bytes in the v4 reference)
   R     = generic ramdisk size + vendor ramdisk size + recovery ramdisk size
   S     = /kernel/devicetree_space_size, default 0x200000
   K     = effective kernel load address above + O
   E     = effective kernel reserve end above + O
   initrd_address = E - (align_up(R, P) + P)
   dtb_address    = initrd_address - (S + P)
   ```
   ABL rejects `dtb_address <= K` at **0x67850..0x678cc**. This **only checks the start** of the kernel allocation; native boot verification must additionally establish **`dtb_address >= K + Image.image_size`**, no other reserved region overlap, and actual initrd/DTB sizes and the Linux 1-GiB initrd-window requirement.
6. ABL passes these computed addresses into the later DTB/ramdisk image relocation paths (**0x68c78 onward**); these are computed *runtime* physical pointers, not the `kernel_addr=0x8000`, `ramdisk_addr=0x1000000` or `dtb_addr=0x1f00000` fields found in the stock v4 reference vendor image.

## Exact impact on the accepted native 64-bit Image
- The native Image is **uncompressed**, has **nonzero image_size** and `text_offset=0`: on the successful UEFI-variable route, **`K = KernelBaseAddr + O`**. This rules out the feared automatic `0x8000`/old literal boot-header placement. `Image.image_size=0x32c0000` must fit.
- Assuming P=4096, S=2 MiB and any integer number of page-rounded initrd bytes, the **minimum separation** to avoid the kernel and DTB region overlap is:
  ```text
  E - K >= 0x032c0000 + align_up(R, 4096) + 0x200000 + 8192
        >= 0x034c2000 + align_up(R,4096)
        >= 55,320,576 bytes + align_up(R,4096).
  ```
  (This is a sufficient non-overlap condition, not evidence that ABL/UEFI has actually allocated it.)
- If the 64-bit fallback is taken **and M happens to be 2 MiB aligned**, `E-K` before any offsets is **99.5 MiB**. It could accommodate the accepted Image and up to **0x02ebe000 (46.7421875 MiB) of *page-rounded* ramdisks** with the default DTB allowance, from region-size arithmetic alone.
- **Alignment hazard in fallback:** `M | 0x80000` is generally **not itself 2-MiB aligned** when `M` is 2-MiB aligned. The pinned ARM64 boot specification requires Image start at `2MiB_aligned_base + text_offset`; with `text_offset=0`, a raw fallback `M|0x80000` and `O=0` would be incompatible. A nonzero FDT offset, later relocation or the successful UEFI-variable path could avoid it; their *runtime* selection cannot be proved offline. Do **not** mark native-Image alignment approved based on fallback capacity alone.
- Mainline DTB `/memory@a0000000/reg` contains **size zero** before bootloader updates. The DTB source address `0xa0000000` does not by itself prove `M`, `KernelBaseAddr` or a usable DRAM interval on the PVT, nor does it prove ABL supplies the required RAM-size fixup.

## Decision and stop boundary
**Resolved by source:** the exact branching and formulas for Motorola ABL's kernel, ramdisk, DTB, FDT-size allowance, 32/64-bit fallback constants and rejection checks. Repeating further ZIP acquisitions or disassembling unrelated firmware components is not required to determine these.

**Not statically identifiable as a single constant:** physical values of `KernelBaseAddr`, `KernelSize`, `BaseMemory`, selected `/kernel` overrides and final DRAM carveouts on the *installed* phone. These are explicitly queried/derived at runtime. Consequently a unique physical kernel start address and an assertion that the custom Image satisfies all alignment/overlap constraints **cannot** be verified from stock image code alone. Hardware-side read-only UEFI/bootloader memory-log capture or a rigorously checked temporary load experiment is the evidence needed, not speculative numeric addresses. The on-device bootloader identity was not reverified against the reference image bytes.

**Safe engineering decision:** keep the accepted kernel and packaging unchanged; check that the real Image (not just its file bytes) fits the computed `[K,dtb_address)` region and that `K` meets the pinned ARM64 alignment rule once runtime base/offsets are available. The ABL `fastboot boot` path was already identified but RAM-only behaviour with the chosen DTB/vendor composition remains a separate runtime question.

**Changes:** only the isolated `research/oneli-mbm-readonly-20261015` research branch. No coordinator MAIN, Drzet/linux, kernel, boot package or device operations.