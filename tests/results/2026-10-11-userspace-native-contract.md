# Userspace native-artifact contract fixture validation

Date: 2026-10-11. Scope: synthetic AArch64 ELF module and minimal initramfs fixtures, not the Motorola oneli native kernel.

- Completed run: https://github.com/Drzet/razr2022_nuc/actions/runs/38179683577, job `114589402535`, conclusion **success**.
- Branch implementation revision tested: `ed536a2745286552166fd929018f407ba28ba9ab`.
- Actual PR #7 test-merge checkout: `2b623aa24b4469b254ff9ffd2b0900bfc944fe7a`, from the Actions checkout log (merged `ed536a2745286552166fd929018f407ba28ba9ab` into coordinator base `417ffb165f7fccf6a97cca1182c7fa8f8a659f36`).
- Command: `python3 -m py_compile scripts/validate-native-kernel-inputs.py tests/userspace/test_native_contract.py && python3 tests/userspace/test_native_contract.py`.
- Environment: ubuntu-24.04 hosted runner, `clang`, `kmod/modinfo`, `cpio`, `initramfs-tools-core/unmkinitramfs`, `zstd`, `xz-utils` installed by the workflow. Resolved apt versions are not retained in this fixture job.
- Tests: **6 passed in 4.806 seconds**: positive synthetic ARM64 module+initramfs manifest; negative tampered native Image, altered module vermagic with recalculated module hash, modified embedded initramfs module with recalculated outer initramfs hash, missing embedded firmware, and empty/unresolved firmware manifest.
- Test source used a synthetic `.modinfo` `vermagic` section compiled as AArch64 relocatable ELF. It did **not** use a module compiled from Drzet/linux or any proprietary firmware; hence the result validates the gate logic rather than actual kernel compatibility.
- Later branch work may extend or improve the contract; this record belongs to the exact SHAs above, not future moving branch tips.

This is host-only validation. No QEMU guest, oneli hardware, kernel-module loading, symbol CRC resolution, secure firmware authentication, or native boot is demonstrated.
