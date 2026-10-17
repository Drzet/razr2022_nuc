# Userspace: native diagnostic console-summary payload v2

- Date / owner: 2026-10-12, Userspace.
- Repository / branch: `Drzet/razr2022_nuc:razr/userspace`.
- **Exact tested source commit:** `64b7a3358d3250dbe92518e548517ddfd038b149`.
- Kernel **unchanged**: `Drzet/linux:razr/integration@2b5acf108ae37040ac1e652e029bb37f5609e886`; release `7.3.0-rc6-g2b5acf108ae3`.
- Boot machine interface **unchanged**: `configs/oneli-native-early-initramfs-interface-v1.json` at `razr/boot@a7119d5f6b1c1f8be8fbbc018dbefcfccf796c7e`, Git blob `710c2681734f699e456d3a673a27f851f202a7e3`.
- Evidence stage: implemented, tests and QEMU host **passed**; actual oneli phone hardware **not tested**.

## Changes / resolution of seventh review

Prior diagnostic v1 wrote grep-filtered probe-error body only to volatile `/run/oneli-diag/000001.log`, while its `RAZR_NATIVE_DIAG_PROBE_ERRORS_BEGIN` / `END` delimiters appeared on the console without the body. The code now retains a bounded raw kernel `dmesg` snapshot entirely in `/run` tmpfs, filters `fail|error|probe|timeout|defer`, takes the last **80** matching lines and caps the console excerpt to **16384 bytes**. The bounded excerpt is emitted with `record()` to *both* RAM log and `/dev/console` between the original delimiters. Read/summary output failures are diagnosed and cannot intentionally terminate PID 1; console/log write errors are recorded once when an alternate sink is available. Boot contract/required paths, static BusyBox, no persistent writes, no network/modules/firmware, READY and default resident HOLD semantics remain unchanged.

For reproducible coverage, QEMU-only `-append` sets `razr.diag_probe_error_fixture=RAZR_NATIVE_PROBE_ERROR_FIXTURE_CI_ONLY`. Linux prints the supplied command line into its ring buffer, so the diagnostic grep must relay that known nonempty line to the serial console. The fixture is **not** embedded as a synthetic error in /init and is **not** a claim about a device probe error. Python fixture checks reject an absent marker, marker-only output, a fixture only *outside* delimiters, reordered markers, excessive lines and excessive bytes. `finalize` and manifest verification inspect both positive and HOLD serial logs, requiring the fixture **inside** the delimiters. 13 synthetic tests passed.

## Test evidence and exact hashes

- GitHub Actions green [run 38317559417](https://github.com/Drzet/razr2022_nuc/actions/runs/38317559417), job `115037714441`, on exact tested project commit `64b7a3358d3250dbe92518e548517ddfd038b149`; 13/13 Python fixtures, independent GNU cpio/extraction, accepted Image/config/DTB and BusyBox package checks, real diskless QEMU PID1+shutdown, separate 12-second negative HOLD, manifest verification and artifact upload all **success**.
- Immutable Actions artifact **`native-diag-v2-38317559417-1`**, ID **`11777077254`**, independently downloaded ZIP SHA256 **`3625ebfdaf83edd4628791f8a818ecaea357aeabcb354b062e00911124f4ed76`**. All **15/15** SHA256SUMS entries match.
- `oneli-diag-initramfs.cpio` SHA256 **`cf00eb88014e177a48164f5d70ee8ee277ebe5936a8808bf80885ae8818a408e`**.
- `oneli-diag-initramfs.cpio.gz` SHA256 **`ccd4c96b2cb05ff695175af8625dbbf8fe2f822d32fafaa5ae930e7796b7a93b`**. Independently gzip-decompressed and confirmed byte-for-byte identical to the raw newc.
- Extracted `/init` SHA256 **`d23e8bd9662a91d9cd1b6edaa1db49ed5ec8ea6aec70f9763cddab4a6e8989e9`**.
- Typed Boot-compatible `oneli-diag-payload-v1.json` preserves **v1 wire schema** and adds `payload_revision: console-summary-v2` plus console/hold evidence. Archive directory and artifact name distinguish this **v2 payload release**, not a change to Boot's contract.
- Actual `qemu-serial.log`: PID1=1, zero mount failures, exact release, matching kernel-cmdline fixture emitted *between* PROBE_ERRORS_BEGIN/END, READY, QEMU shutdown and poweroff; QEMU exit **0**.
- Actual `qemu-hold-serial.log`: PID1=1, same fixture within console probe delimiters, READY and HOLD, **no** QEMU shutdown; expected host timeout exit **124**.
- Accepted kernel Image SHA256 `3a8fa9620e0fc8de68ce8db45dacdfd811a2ba2c9718f9cddee3893ec9af0939`; oneli DTB SHA256 `d3c9abcea9950200babbcf6c979073dc94c6af5cac68578540ad570db4a14a03`. The **QEMU virt-generated DT** and ttyAMA0 command line are separate tests, not native boot configurations.

## Shared integration and next handoff

Only Userspace-owned `scripts/build-native-diag.py`, `tests/userspace/test_native_diag.py`, the native workflow and this handoff were changed. No aggregate coordinator files, Boot artifacts, kernel sources or device trees were modified. Preserve previously accepted v1 payload at [run 38307910388](https://github.com/Drzet/razr2022_nuc/actions/runs/38307910388), original ZIP `9637a4a5e0090482428e6b9c8e8011a46131f831407352f40e381ba25fb6df6f`, original compressed cpio `3d7a08022bdff062455099d509d54c9aa571cb9c289d89a431b7edb892846f3b`. **Do not overwrite its evidence or hashes.**

**Boot consumption:** fetch v2 artifact ID `11777077254`, verify outer ZIP and internal `SHA256SUMS`, consume exactly the revised compressed cpio and typed manifest for **one** deliberate host-only repackage **after** this test, if Boot selects it. Do not infer phone UART/USB access from QEMU output. Boot owns loader placement, mainline DT selection, cmdline, actual diagnostic route and recovery gates; stop at missing device-only evidence. No native flash instructions or physical acceptance.
