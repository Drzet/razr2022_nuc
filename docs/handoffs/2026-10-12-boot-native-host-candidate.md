# Boot handoff: unsigned native early-initramfs host candidate (2026-10-12)

**Owner/branch:** Boot, `Drzet/razr2022_nuc:razr/boot`. **Source under test:** `1e35aad6b6a856f6f86cdf9ba897aee5004e9abd`. **Accepted kernel:** `Drzet/linux:razr/integration@2b5acf108ae37040ac1e652e029bb37f5609e886`. No kernel source, shared DT, aggregate coordinator status/tasks, integration promotion, phone flash or repeat kernel/Debian build was performed.

## Result and immutable evidence

The previously agreed [Boot native interface v1](../oneli-native-early-initramfs-interface-v1.md) was ACKed unchanged by Userspace against contract blob `710c2681734f699e456d3a673a27f851f202a7e3`. Userspace's new no-disk QEMU diagnostic `/init` and its exact checksummed payload were delivered as [run 38307910388](https://github.com/Drzet/razr2022_nuc/actions/runs/38307910388), artifact **11772559465**. This artifact is now **consumed and independently verified**, not outstanding.

**Boot packaging CI:** [successful run 38310449244](https://github.com/Drzet/razr2022_nuc/actions/runs/38310449244), job **115014596145**, at source commit `1e35aad6b6a856f6f86cdf9ba897aee5004e9abd`. All stages succeeded, including four fail-closed local fixture tests, actual hashed accepted Image/config/oneli DTB, 15 verified Userspace SHA256SUMS entries, newc/gzip/PID1 log validation, self-layout audit, independently pinned **AOSP v4 unpack**, an independently packed AOSP counterpart and section-by-section hash/table comparison. The independent AOSP tools are pinned to `ntherning/mkbootimg@7209a7164f1772db43f92928012c86a00f6202ff`. We did not repeat the existing Debian/systemd QEMU run.

**Result artifact:** `oneli-native-host-only-v1`, ID **11774750168**. Independent ZIP download SHA256 **`79b865936a426e76971bacb0b91fe5a9ec0943430ae0e0cbdf4af8d477daf378`**, matching GitHub digest. All **eight** internal `SHA256SUMS` entries independently verified. Machine-readable project record: [`tests/results/2026-10-12-oneli-native-host-validation.json`](../../tests/results/2026-10-12-oneli-native-host-validation.json).

| Produced section | SHA256 / fact |
| --- | --- |
| `boot-candidate.UNSIGNED.img` | `f47686e4cff28d9491ece814dd6c91c6f22eab32b3061a46f9bb935ae1fcda74`, 53,395,456 bytes |
| `vendor_boot-candidate.UNSIGNED.img` | `1b4f6379b41e22735176bf63c725d3455d47c7b510f29d0de62b408da5f47572`, 118,784 bytes |
| Embedded kernel Image | `3a8fa9620e0fc8de68ce8db45dacdfd811a2ba2c9718f9cddee3893ec9af0939` |
| Embedded generic ramdisk `newc.gz` | `3d7a08022bdff062455099d509d54c9aa571cb9c289d89a431b7edb892846f3b` |
| Embedded mainline oneli DTB | `d3c9abcea9950200babbcf6c979073dc94c6af5cac68578540ad570db4a14a03` |
| New vendor platform fragment | `af39e1c19af478aef7a03be98efa9d9baa228fb9f93e3842d6d7b14a1465a459`, 48-byte `gzip -n -9` empty newc |

## Exact chosen native-host-only policy

The chosen external manifest [`configs/oneli-native-host-header-inputs-v1.json`](../../configs/oneli-native-host-header-inputs-v1.json) requires `purpose=structural-only`, `phone_boot_validated=false`, all five explicit raw placement fields and reference provenance. These address values are the **public reference**, **not native bootloader approval**. Image construction deliberately uses Android boot-v4 and vendor_boot-v4 headers, 4096-byte pages, `os_version_raw=0`, zero boot signature, zero reserved words, empty boot/vendor command lines, and zero bootconfig. Vendor fragment entry is platform type 1, name `native-diag`, 16 explicit zero board-ID words, one 108-byte table entry. No stock Android vendor ramdisk, signature or bootconfig bytes were copied. AOSP's independent unpack output confirms the exact four reference address fields, section sizes, table fields and empty bootconfig; all payload files hash-identically after extraction.

The fragment is a deliberately **empty** `newc` with deterministic gzip wrapper, not an attempt to provision Motorola proprietary services. The useful diagnostic `/init` is in the **generic** ramdisk. Neither these choices nor the successful AOSP round-trip establish actual OEM bootloader acceptance. Boot-v4 signature and partition AVB are separately unresolved; there is no signing/AVB authentication or native flash authorization.

## Changed files / dependencies

Boot-owned commits add:
- `configs/oneli-native-host-header-inputs-v1.json` (explicit host-only policy).
- `scripts/build_oneli_native_host_candidate.py` (read-only input hashing, independent root-owned newc and evidence checks, new empty vendor platform archive, unsigned v4 image generation, fail-closed section checks).
- `tests/test_oneli_native_host_candidate.py` (four negative/positive regression cases).
- `.github/workflows/boot-native-host-candidate.yml` (pin/download consumed binary artifacts and AOSP source, independent pack/unpack/hash/table verification, publish full ZIP).
- `tests/results/2026-10-12-oneli-native-host-validation.json` (reviewable machine evidence).
- This handoff. Prior `tests/results/2026-10-12-oneli-native-packaging-blocked.json` remains an accurate historical *pre-payload* result; it is superseded for host construction, not overwritten.

## Remaining gates

**Host structure has now passed. Phone validation has not begun.** The following remain unresolved and cannot be inferred from AOSP unpack or QEMU virt: actual Motorola native Image/DTB/vendor_boot placement and DT/overlay selection, bootloader command-line control, physically reachable/safely characterized UART or independently demonstrated alternative early console, AVB/vbmeta and recovery-safe device experiment, actual early kernel output, and bootloader acceptance of this diagnostic payload. No UFS root, GPU, VPU, USB, DisplayPort or charge-control enablement is needed for this milestone.

The optional actual application of stock PVT DTBO index 3 to **each original stock base FDT** remains a reference-only binary task. No full firmware rescan or JSON-to-FDT reconstruction was performed; it is not required by the already accepted mainline oneli DTB structural host candidate.

**Coordinator handoff:** review the current Boot branch and the immutable artifact SHA256 above; do not merge or promote while unavailable. If further offline work is selected, it should be bounded by a specific native placement/logging evidence requirement, not a repeat combined build or QEMU smoke.
