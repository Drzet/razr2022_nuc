# Coordinator review — 2026-10-16

## Decisions

| Delivery | Disposition |
| --- | --- |
| VPU project `29c59a2cb58559e0c00c2b5baead5bb5f8c95d32` | Consumer-policy contract accepted for the disabled development candidate, with the explicit startup limitation below. Proceed to bounded implementation. |
| Boot project `b2f9aea38b5581781e8b07aa98a85dbbeddaa237` | Loader/readiness update accepted; original kernel, DTB and diagnostic-v2 identities preserved. |
| MBM research `0acccb329521d91b84fdcfb4bf9d7dcc25f44a25` | UTF-16 and RVA-mapping correction accepted; all 12 submitted synthetic tests independently pass. |

Accepted integration remains `2b5acf108ae37040ac1e652e029bb37f5609e886`. No new kernel delivery, combined build, handset boot or working USB/DP/VPU hardware is claimed. This review selects VPU implementation and an independent DisplayPort source-contract review; Boot pauses after completion. [Current assignments](NEXT_TASKS.md).

## VPU contract review

Read the complete new consumer-policy section in the [canonical handoff](https://github.com/Drzet/razr2022_nuc/blob/29c59a2cb58559e0c00c2b5baead5bb5f8c95d32/docs/handoffs/2026-10-13-vpu-tenth-recovery.md#consumer-policy-contract--2026-10-16). Verified kernel head remains `7ac8d3afedfde74286b52e11aaa1eca42a1329a5`. Independently inspected its power, resources, VPU2 frequency, platform-capability, decoder-rate and core-lock source paths. The legacy power path skips zero-byte sessions, uses DEFAULT_FPS bandwidth, updates cached votes before provider success and uses an OPP helper with devfreq fallback; the proposed SM8475 path explicitly replaces those semantics without changing other platforms.

Accept the specified explicit reservation lifetime, checked input/aggregate admission, independent D/L sums on disjoint routes, strict OPP ceiling, provider readback, PM-before-core-lock ordering, and failure/rollback state. The existing pure calculator remains accepted; unchanged 1362-vector/3157-assertion evidence was not replayed. The new contract is documentation, not executable proof of transactions, lock ordering or HFI suppression; those require production-path tests in the selected implementation.

**Startup limitation is stronger than the handoff's 4K example.** Independently evaluated its pinned VPU2 formula with zero compressed-payload contribution:

| Format at retained 480-fps startup | Macroblocks/s | Minimum VPP demand | 444 MHz ceiling |
| --- | ---: | ---: | --- |
| 1280x720 | 1,728,000 | 362,880,000 Hz | Passes this clock check only |
| 1920x1080 (height rounded to 1088) | 3,916,800 | 822,528,000 Hz | Rejects |
| 3840x2160 | 15,552,000 | 3,265,920,000 Hz | Rejects; also exceeds core MB/s limit |

This is a computed policy restriction, not a measured hardware capability. A 720p row is not a full admission or decode guarantee. Accept the current contract as an intentionally restricted implementation target; do not advertise 1080p/4K startup support or silently lower startup to bypass rejection. A useful broader startup/rate policy is a separate future change, required before claiming general-purpose decode support. No physical divider search is reintroduced: /3 remains **[INFERRED, USER-ACCEPTED FOR DEVELOPMENT]**.

Implement the reviewed contract behind the existing disabled SM8475 gate, including input validation, committed reservations, strict clock selection, transactional ICC/OPP changes and caller errors. Cover the lifecycle, rollback and asynchronous buffer-completion cases in the handoff. Required-opps/ICC binding and test-fixture contract may be staged; Boot-owned shared DTS and enablement are excluded. Source-resolved MXC/MMCX ordering and accepted assumptions remain fixed.

The inherited IOVA reservation error behavior remains a separate active-DMA defect. Physical PAS/HFI/decode and LLCC behavior remain untested. This assignment does not approve active DMA, cache changes or probe-gate removal.

## Boot and research review

Inspected all three Boot changed-file diffs: loader/output decision, JSON readiness and canonical handoff. They preserve full Image size 53,215,232 bytes, source hashes, OR-based fallback, zero-size pre-fixup FDT memory, final-runtime uncertainties and conditional trial planning. They no longer use stock literal header addresses as actual placement. Existing host packaging remains accepted; no identical repackaging is needed. Historical payload-wait wording in the JSON is superseded by its explicit accepted v2 identities and current queue.

Inspected the complete constants-tool and synthetic-test diff. UTF-16 now terminates at aligned code units; numeric/string/GUID reads map raw-backed PE sections instead of assuming RVA=file offset. Executed the exact submitted 12-test suite locally using the three pinned script/test files; **12/12 PASS**, including both full names, nonidentity RVA, section-boundary and malformed-header/raw-bound cases. The tool is a bounded trusted-reference extractor, not a generally hardened arbitrary-PE parser.

The saved section numbers in the submitted readiness/test data place all selected RVAs within identity-mapped .text. Coordinator checked their consistency; Boot's independent artifact inspection remains attributed owner evidence, not a new coordinator download of artifact 12007666834. Corrected names were tested synthetically, not freshly decoded from original firmware. No firmware download/disassembly rerun, kernel build or device operation occurred.

Boot's assigned offline work is complete. Runtime branch/bases, final RAM/FDT/ramdisk composition and accessible early output remain observations for a separately selected phone trial. These do not block VPU software or the newly identified AUX switch review.

## Next independent source task: DisplayPort

Reference identity is **WAS7227Q-10/TR**, per [canonical schematic evidence](oneli_schematic_evidence_2026-10-15.md). The old unknown-part hold in DisplayPort head `d5b45132914f075c784c6bbb2ca2e604cd262f86` is superseded for the reference design. Installed-board correspondence remains [INFERRED]. Do not substitute AW35615 or re-enable FSA4480.

Activate only the missing exact-part reuse/binding and GPIO/connector contract. Reuse the completed stock-overlay and software truth-table work, accepted PS5169 evidence and Boot rail proposal. This source review is independent of VPU files and can run alongside its single implementation stream. No new DP driver, shared-DTS enablement or duplicated firmware extraction is selected.
