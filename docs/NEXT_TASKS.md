# Current assignments — cleanup reset, 2026-10-13

This queue supersedes all earlier rounds, including tenth prototype instructions. [Policy](WORKFLOW.md) · [Status](STATUS.md) · [Disposition](CLEANUP_2026-10-13.md).

## Active: VPU — close the reviewed candidate, no new feature work

Read [VPU review](VPU_REVIEW_2026-10-13.md). Candidate ec9a8949cfbd1b05cf01553bffc39719ee1a16a7 correctly reuses Qualcomm's v5 architecture and has verified build/schema/routing results. Preserve this tested history. Complete only:

1. Recover and pin exact source mbox/hash and selected patch identities. Reconstruct upstream author/message/trailers on a new provenance-corrected branch starting from 869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf; record old/new SHA mapping and backport deltas. Do not force-push razr/vpu-upstream or manufacture sign-offs. Keep local adaptations separate. Compare resulting tree to ec9a8949; reuse prior compile evidence for identical code.
2. Execute actual production IOMMU range-reservation logic for the intended windows and malformed/zero/overflow/translation/allocation failures. Current fixture equality assertions are not parser tests. Report inherited limitations honestly; no broad IOMMU rewrite. Reuse upstream fixes if a defect is found before creating local code.
3. Execute actual child create/init/deinit and failure unwind paths with explicitly scoped mocks or kernel tests: legacy absent children, first/second registration failure, partial cleanup, later V4L2 registration failure. Validate returned errors and balanced references/registration; do not count source-string assertions as execution.

**Deliverable/stop:** one canonical handoff update with source provenance, corrected branch/commit mapping, focused test results and remaining limitations. No fresh architecture survey, extraction, OPP/ICC, firmware-policy expansion or Boot DTS changes. Do not add a separate child driver: the pinned IOMMU notifier can configure unbound children, correcting an earlier coordinator overstatement. Keep SM8475 gated and accepted integration unchanged.

## Queued next: USB — NXP adaptation selection, not implementation

PS5169 tenth closure is complete; no additional PS5169 work or build. After coordinator selects this queued task, compare exact Motorola `repeater-i2c-eusb2.c@0450c5076a8ec9415a10888c8c183ef6ff5f91b8` and oneli overrides against mainline PHY/PTN3222 interfaces. Deliver one minimal reuse/adaptation decision covering IDs, reset/supplies, error handling and framework differences. Do not infer PTN3222 identity from the generic compatible or write a fresh repeater driver. No ROM extraction or active graph.

## Paused

- **Boot:** resume only for a reviewed shared-DTS/candidate request or attributable new loader evidence. No packaging replay.
- **Userspace:** resume only after an actual accepted kernel/artifact/interface change affects its tests.
- **GPU:** no new work without a named source defect or hardware result.
- **Power:** retain SGM41516D vendor-source lead for future variant adaptation; no charger implementation or repeat audit now.
- **DisplayPort:** AUX-identity hold; no guessed compatible.

## Coordinator

Review VPU's reuse/backport deltas before assigning Boot integration. Maintain frozen accepted artifacts and one canonical queue. No second implementation stream is selected. USB does not technically depend on VPU; its queue position is an explicit work-in-progress limit. No all-agent restart.
