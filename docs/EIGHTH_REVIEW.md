> Historical review. Current STATUS.md and NEXT_TASKS.md supersede all work instructions below.

# Eighth coordinator review — 2026-10-13 (Europe/Lisbon)

**Seventh-round work accepted: the console-summary defect is fixed and the exact v2 payload has been repackaged once. Native device handoff remains unresolved.** Kernel, DTB and vendor_boot are unchanged. Stop repeated Boot/Userspace build rounds; resume only work that resolves a specific remaining input.

## Reviewed revisions and verification

| Owner | Project head | Tested commit | Verified run |
| --- | --- | --- | --- |
| Userspace | `428274b220e38d242b1cda2cfca63706f7374074` | `64b7a3358d3250dbe92518e548517ddfd038b149` | [38317559417](https://github.com/Drzet/razr2022_nuc/actions/runs/38317559417), job 115037714441 |
| Boot | `4c79b7dbe06075280fbb1ad1c0868dbad62e2f8c` | `0b2ee0709987831ede07a1494117c7abd3485075` | [38318260840](https://github.com/Drzet/razr2022_nuc/actions/runs/38318260840), job 115039980166 |

Coordinator inspected the changed source, successful jobs/logs, downloaded both ZIPs and verified all enclosed checksums. No new hardware evidence was submitted.

- **Userspace artifact 11777077254:** ZIP SHA256 `3625ebfdaf83edd4628791f8a818ecaea357aeabcb354b062e00911124f4ed76`, **15/15** file checksums pass; gzip equals raw cpio. Both actual serial logs contain the nonempty fixture line **inside** the probe-summary delimiters. Positive exit 0 and expected resident-HOLD host timeout 124 are recorded. The fixture is a QEMU command-line string, not a claimed phone probe error. Source now emits the bounded summary via record() to both RAM and console. The existing wire schema is unchanged, with payload revision console-summary-v2.
- **Boot artifact 11777433748:** ZIP SHA256 `c2f7353a652d60c4d3e0282dfa101ab421d1dfd605c571c509194f25b26cb00b`, **5/5** file checksums pass. Independent AOSP crosscheck passes. Coordinator independently extracted the generic ramdisk using raw boot-header offsets and verified gzip SHA256 `ccd4c96b2cb05ff695175af8625dbbf8fe2f822d32fafaa5ae930e7796b7a93b`. Image size 53,395,456 bytes. The original vendor_boot is retained, not regenerated.
- **Documentation correction:** the Boot handoff and committed result JSON truncate the boot-image digest to 62 hex characters. Actual downloaded `boot-console-v2.UNSIGNED.img` SHA256 is **`1e00e4f998f5001bc08d9e0d4e4465664100194ce211cd9eb8b329612b5563bb`**. The artifact SHA256SUMS agrees. Missing characters occur around `...c08d9e0d4...`. This is a transcription defect, not a failed build. The coordinator's [accepted v2 record](../configs/accepted-native-console-v2-2026-10-13.json) uses the calculated full digest; Boot should fix its two source records without rerunning CI.

The initial wrapper failure 38318193635 is historical; corrected run 38318260840 is the accepted result. V1 artifacts retain their original identity and acceptance scope.

## Independently checked loader findings

Coordinator inspected the already hash-verified Image and compiled oneli DTB directly:

- Image file is **52,369,920 bytes**; ARM64 header `text_offset=0`, `image_size=53,215,232`, flags `0xa`. The required allocation is **845,312 bytes larger than the file**. Section alignment in an Android image is distinct from the ARM64 kernel's physical placement requirements.
- `/memory@a0000000/reg` contains base `0xa0000000` and **size zero**. This is an unpopulated DT memory description, not evidence that the phone lacks RAM. The loader or another justified preparation stage must supply a valid actual memory map. Do not fill it with a guessed capacity/range.
- `/chosen/stdout-path` is `serial0:115200n8`; serial0 resolves to `/soc@0/geniqup@9c0000/serial@99c000`. There is no bootargs property in that chosen node. This establishes source routing only, not accessible board pads or a physical console.

Boot's literal-address arithmetic is a valid reason to reject an assumption: interpreting stock reference fields as the final addresses for this Image produces misalignment/overlap. It does **not** prove Motorola's actual loader overlaps buffers; its transformation/relocation behavior is not established. The current images remain host-only prototypes.

## What is actually blocked

The device experiment needs evidence for the actual MBM loading/relocation behavior, populated RAM map, DT/DTBO selection, ramdisk/command-line handling, an observable early-output route and a coherent restoration path. Public format documentation and QEMU cannot establish these device-specific behaviors. No attributable MBM implementation/trace resolving them has yet been reviewed.

Some unknowns could be resolved by a specific attributable source/binary analysis; they are **not intrinsically all hardware-only**. Do not restart a generic audit without identifying that new evidence first. With current inputs the practical Boot path is paused until additional loader/device evidence is available.

Correct the ordering of future acceptance: **successful kernel entry/output is an outcome of a controlled test, not a prerequisite that must already have happened before any test.** Prior prerequisites are an understood test scope, credible restoration route and a justified means to observe results. Do not require successful native boot to authorize investigating native boot. No executable device commands or flash approval are issued here.

## Decision and next work

Boot performs only the two-file digest correction, then pauses. Userspace is complete for this diagnostic profile and pauses. Do not repeat packaging, QEMU, kernel, firmware extraction or broad reporting work unchanged.

The next selected offline workstream is **VPU DMA ownership design**, already bounded in the sixth queue: trace real bitstream/pixel allocation and mapping ownership and decide whether a justified single-domain model is possible or separate devices/domains are required. That is independent of native boot and remains a real source-level blocker. Start VPU alone for that decision; no blanket concurrent round. GPU/Power/USB/DP retain their current queued/held states.
