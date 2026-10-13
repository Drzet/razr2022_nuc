> Historical assignment; not an active queue. Follow current NEXT_TASKS.md.

# Next assignments — eighth coordinator review, 2026-10-13

Read [EIGHTH_REVIEW.md](EIGHTH_REVIEW.md). Seventh-round diagnostic v2 and its single boot-image refresh are accepted for host/QEMU scope. [Accepted v2 record](../configs/accepted-native-console-v2-2026-10-13.json) contains the corrected image digest. Preserve integration `2b5acf108ae37040ac1e652e029bb37f5609e886`, original vendor_boot and historical v1 artifacts.

## Run next: VPU only — one DMA ownership decision

Promote the previously optional bounded DMA design to the next selected offline task. Read the current VPU handoff and `docs/vpu/2026-10-12-bounded-resource-translation-decisions.md` at project `dadd330c3f09f715372da94091f04166f9f0c141`; do not repeat extraction or loader-size work.

1. Trace actual downstream nonsecure bitstream and pixel allocation/map/unmap paths through HFI buffer ownership, including address constraints, shared buffers, cleanup and failure cases. Separate security requirements from allocator convenience. Pin exact source revisions/functions.
2. Compare those paths with current Iris DMA/IOMMU ownership. The upstream second cell is an SMR match mask; two stream identifiers on one Linux device still share its attached domain. Do not present a two-entry iommus property as two independent DMA domains.
3. Evaluate source-supported alternatives: a single-domain model preserving necessary constraints, or separate supported consumer devices/domains with explicit allocation and lifecycle ownership. Verify relevant APIs in the pinned kernel; do not invent auxiliary-domain support. Overlapping vendor IOVA ranges alone do not prove equivalence.
4. Deliver one recommendation with evidence, rejected alternatives, exact affected driver/binding interfaces and testable acceptance conditions. An isolated disabled prototype is permitted only if the model is justified; otherwise name the specific missing evidence and stop. Keep experimental Iris out of accepted integration. No active hardware enablement, broad refactor or generic audit.

MXC/MMCX required-opps and DDR/LLCC dynamic policy remain separate queued blockers. Do not expand this round into all three architecture questions. Phone PAS/HFI/DMA/decode tests remain deferred.

## Boot — metadata correction, then pause

Correct the malformed 62-character `boot_image_sha256` in `tests/results/2026-10-12-oneli-native-console-v2-repackage.json` and the corresponding handoff. Independently re-read the existing artifact/checksum record; correct full SHA256 is:

`1e00e4f998f5001bc08d9e0d4e4465664100194ce211cd9eb8b329612b5563bb`

No rebuild or artifact replacement is needed. Preserve existing v1/v2 evidence and commit provenance.

After this correction, stop. The current loader/output decision report is accepted as a bounded account of unresolved inputs. Resume only with attributable new MBM source/binary evidence or device observations addressing a named gap. Do not regenerate the same image, reconstruct stock FDTs from JSON, guess RAM size/load addresses, or demand another generic investigation.

Future physical-test planning must separate prerequisites from outcomes: restoration and observation arrangements precede a trial; actual kernel entry and native output are results to test, not pre-existing proofs required before any experiment. Owner-managed unlock is not an offline blocker. No device action is assigned now.

## Userspace — complete; pause

The console body fix is verified in both real positive and HOLD logs. Keep v2 payload and interface frozen. No new feature, QEMU replay, Debian build or diagnostic daemon is requested. Resume for a concrete Boot interface change or selected transport requirement.

## GPU / Power / USB / DisplayPort

Remain paused or queued as previously documented. No new work depends on them for this round. USB's unfinished profile/lifecycle tasks are retained in [fifth assignments](FIFTH_ASSIGNMENTS.md), not cancelled. DP's AUX identity hold and GPU/Power runtime/electrical questions remain unchanged. Do not launch all agents concurrently.

## Coordinator

Retain exact artifact references and the verified digest correction. Review VPU's one design decision before authorizing further experimental implementation or selecting the next queued workstream. Native status remains **host-validated; loader/device handoff unresolved**. Preserve artifacts before expiration using verified copies, not rebuilds. Any useful future Boot investigation must identify the specific new evidence it will inspect.
