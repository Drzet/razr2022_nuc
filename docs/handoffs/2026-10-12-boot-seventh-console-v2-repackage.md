# BOOT handoff: seventh-round console-summary v2 one-time host refresh

- **Date / chat:** 2026-10-12, BOOT continuation of seventh coordinator review.
- **Source branch:** `Drzet/razr2022_nuc:razr/boot`.
- **Exact tested packaging source:** `0b2ee0709987831ede07a1494117c7abd3485075`.
- **Accepted kernel and DT unchanged:** `Drzet/linux:razr/integration@2b5acf108ae37040ac1e652e029bb37f5609e886`, `Image` SHA256 `3a8fa9620e0fc8de68ce8db45dacdfd811a2ba2c9718f9cddee3893ec9af0939`, mainline oneli DTB SHA256 `d3c9abcea9950200babbcf6c979073dc94c6af5cac68578540ad570db4a14a03`.
- **Upstream baseline:** `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- **Evidence levels:** v2 Userspace diagnostic output tested in QEMU; BOOT unsigned AOSP v4 image **host-tested**; Motorola phone hardware **not tested**.

## Changed input and source provenance

Userspace completed the independent seventh-review console-summary fix: actual diskless test [run 38317559417](https://github.com/Drzet/razr2022_nuc/actions/runs/38317559417) at exact Userspace commit `64b7a3358d3250dbe92518e548517ddfd038b149`. Its 15/15 artifact checksums pass. Downloaded Userspace v2 artifact **11777077254**: ZIP SHA256 `3625ebfdaf83edd4628791f8a818ecaea357aeabcb354b062e00911124f4ed76`. The raw cpio SHA256 `cf00eb88014e177a48164f5d70ee8ee277ebe5936a8808bf80885ae8818a408e`; gzip cpio SHA256 `ccd4c96b2cb05ff695175af8625dbbf8fe2f822d32fafaa5ae930e7796b7a93b`; embedded `/init` SHA256 `d23e8bd9662a91d9cd1b6edaa1db49ed5ec8ea6aec70f9763cddab4a6e8989e9`. Both positive and negative QEMU console logs include **one nonempty summary line between PROBE_ERRORS_BEGIN/END**. The marker `RAZR_NATIVE_PROBE_ERROR_FIXTURE_CI_ONLY` is supplied through QEMU's test command line and is **not evidence of an actual oneli probe failure**.

For this *single* changed-payload-only repackaging, BOOT added [input lock](../../configs/oneli-native-host-console-v2-input-lock.json), [bounded wrapper](../../scripts/repackage_oneli_native_console_v2.py) and [isolated CI](../../.github/workflows/boot-native-console-v2.yml). Original BOOT v1 packer blob `8221b23255489f7e94d3b267106c36db02c31df5` and accepted vendor_boot v1 remain pinned. This workflow **does not regenerate or publish vendor_boot**; the v1 file is consumed and independently SHA verified byte-for-byte against a recomputed identical vendor layout. The new generic v2 gzip only replaces the boot-v4 ramdisk section.

## Validation / exact artifact

First new run [38318193635](https://github.com/Drzet/razr2022_nuc/actions/runs/38318193635) **failed** after successful input downloads/checksums due to a wrapper bug passing a filesystem Path instead of bytes to SHA256. Corrected at BOOT commit `0b2ee0709987831ede07a1494117c7abd3485075`. Retain this failed test in history.

**Successful [BOOT run 38318260840](https://github.com/Drzet/razr2022_nuc/actions/runs/38318260840)**, job **115039980166**, checked source commit `0b2ee0709987831ede07a1494117c7abd3485075`. All CI jobs passed: pin accepted kernel+v2 payload+v1 vendor inputs; verify their hashes; check v2 `/init`, actual QEMU probe fixture and hold logs; pack only a changed boot image; inspect with BOOT parser; independently unpack/repack with pinned AOSP tools and compare section sizes/hashes, command line and signature policy. No kernel or Debian rebuild.

- Artifact **11777433748**, `oneli-native-boot-console-v2`, independently downloaded ZIP SHA256 **`c2f7353a652d60c4d3e0282dfa101ab421d1dfd605c571c509194f25b26cb00b`**, **5/5 internal SHA256SUMS passed**.
- `boot-console-v2.UNSIGNED.img`, 53,395,456 bytes, SHA256 **`1e00e4f998f5001bc08d9d4e4465664100194ce211cd9eb8b329612b5563bb`**. Embedded kernel identical; generic gzip changed to v2 sha `ccd4c96b2cb05ff695175af8625dbbf8fe2f822d32fafaa5ae930e7796b7a93b`. OS version field 0; no boot-v4 signature; empty cmdline; Android image structure only.
- Previous v1 `boot-candidate.UNSIGNED.img` remains accepted for its former payload and untouched: SHA256 `f47686e4cff28d9491ece814dd6c91c6f22eab32b3061a46f9bb935ae1fcda74`.
- **No new vendor_boot output.** The exact existing v1 vendor image SHA256 `1b4f6379b41e22735176bf63c725d3455d47c7b510f29d0de62b408da5f47572` remains the paired *structural* host reference. Neither v1 nor v2 is native-phone accepted or AVB signed.
- Machine output artifact includes `boot-console-v2-inspection.json`; durable [result record](../../tests/results/2026-10-12-oneli-native-console-v2-repackage.json) with all identities and distinct historical failure.

## Shared files, dependencies and next action

Only BOOT-owned project files are touched, no kernel/DT/schema/baseline edits, no `razr/integration` movement, no coordinator STATUS/NEXT_TASKS changes. Separate seventh BOOT decision report [native loader/output decision](../oneli_native_loader_output_decision_2026-10-12.md), machine [readiness record](../../configs/oneli-native-loader-readiness-v1.json) and [handoff](2026-10-12-boot-seventh-loader-output.md) establish the actual remaining oneli unknowns.

**Phone readiness remains BLOCKED:** actual Motorola bootloader Image base/relocation, bootloader-supplied RAM, DT/DTBO selection, generic/vendor ramdisk and cmdline priority, observed physical UART/early diagnostic route, AVB/rollback and independently verified reversible restoration. The *only* next physical acceptance path requires evidenced loader placement and a safe observable recovery-capable experiment; no flash command is supplied or approved. Do not repeat unchanged host image builds or generic ROM scans. Coordinator reviews these BOOT artifacts and is sole owner of any aggregate readiness change.
