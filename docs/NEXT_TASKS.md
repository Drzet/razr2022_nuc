# Current assignments — cleanup reset, 2026-10-13

This queue supersedes all earlier rounds, including tenth prototype instructions. [Policy](WORKFLOW.md) · [Status](STATUS.md) · [Disposition](CLEANUP_2026-10-13.md).

## Active: VPU — adapt Qualcomm's existing implementation

**Kernel branch:** `razr/vpu-upstream`, created at `869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf`, before the bespoke peer-device prototype. Project reports remain on `razr/vpu`; canonical handoff is `docs/handoffs/2026-10-13-vpu-tenth-recovery.md`, updated in place. Old kernel `razr/vpu` is frozen; do not refine or merge it.

**Deliverable:** one attributable, disabled SM8475/VPU2 adaptation candidate plus a concise patch/dependency record. Use Qualcomm's 13-patch v5 series `20260926-vpu_iommu_iova_handling-v5-0-0322ca5dc10c@oss.qualcomm.com`, base `f5f84daefcd92d7a630066635ecea1433ed5eac7`, and dt-schema #207 as the known starting evidence. Check only for a superseding series/status; no repeat general reuse audit.

1. Pin source mbox/hash, selected patches, dependencies and schema revision. Backport the coherent common binding/IOMMU/context-device/**existing buffer-routing** changes. Keep upstream attribution and adaptation commits separate. Exclude unrelated SoC DTS conversions unless required; document dependencies/conflicts. Do not reproduce upstream routing in new local code or omit required routing merely to split the round.
2. Add only justified VPU2/SM8475 deltas. Resolve generation-specific creation hooks, HFI/internal buffer ownership and Motorola pixel-floor difference explicitly. Keep PAS carveout separate, secure sessions out and board disabled. Do not introduce custom peer compatibles/phandles or IOVA-only reserved-memory ABI. No OPP/ICC expansion.
3. Reuse relevant assertions from old tests, rewritten around upstream interfaces; discard tests that merely preserve the abandoned topology. Validate actual positive/negative subnode schemas and relevant ownership/failure behavior. Compile affected code; run dependency-complete link validation when warranted by the new IOMMU/media dependencies. No repeat full image build for unchanged fixtures.
4. Record exact upstream/project deltas, results and unresolved evidence. Preserve other supported platforms. If the VPU2 adaptation cannot be justified, stop with the exact missing interface/evidence; do not substitute another bespoke architecture. Keep SM8475 gated until the implemented path is coherent; never present a disabled fixture as a decoder test.

**Stop:** after delivering this candidate for coordinator review. Do not edit Boot's shared DTS, accepted integration or diagnostic images. Native firmware ACK is a later hardware outcome, not a prerequisite for this work.

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
