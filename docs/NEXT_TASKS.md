# Current assignments — cleanup reset, 2026-10-13

This queue supersedes all earlier rounds, including tenth prototype instructions. [Policy](WORKFLOW.md) · [Status](STATUS.md) · [Disposition](CLEANUP_2026-10-13.md).

## VPU — closure accepted, paused

Coordinator reviewed the provenance reconstruction and executed the host failure-path checks. Sole canonical kernel candidate: `razr/vpu-provenance-v5@a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac`. Original tested upstream branch and temporary closure branches are historical; do not reset, merge wholesale, or rerun provenance reconstruction. The canonical [VPU handoff](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/handoffs/2026-10-13-vpu-tenth-recovery.md) records exact old/new mappings and evidence.

No VPU implementation is currently assigned. Keep SM8475 gated and accepted integration unchanged. Inherited IOMMU reservation failure behavior and unresolved VPU2 resource/firmware policy remain enablement gates; host mocks do not clear them. No fresh audit, extraction, rebuild, shared-DTS edit or additional documentation-only round.

## Queued next: USB — NXP adaptation selection, not implementation

PS5169 tenth closure is complete; no additional PS5169 work or build. After coordinator selects this queued task, compare exact Motorola `repeater-i2c-eusb2.c@0450c5076a8ec9415a10888c8c183ef6ff5f91b8` and oneli overrides against mainline PHY/PTN3222 interfaces. Deliver one minimal reuse/adaptation decision covering IDs, reset/supplies, error handling and framework differences. Do not infer PTN3222 identity from the generic compatible or write a fresh repeater driver. No ROM extraction or active graph.

## Paused

- **Boot:** resume only for a reviewed shared-DTS/candidate request or attributable new loader evidence. No packaging replay.
- **Userspace:** resume only after an actual accepted kernel/artifact/interface change affects its tests.
- **GPU:** no new work without a named source defect or hardware result.
- **Power:** retain SGM41516D vendor-source lead for future variant adaptation; no charger implementation or repeat audit now.
- **DisplayPort:** AUX-identity hold; no guessed compatible.

## Coordinator

VPU bounded closure is accepted; no implementation stream is active after branch repair. Select the already-scoped USB NXP decision explicitly when resuming project development. USB does not depend on VPU completion. No Boot integration or all-agent restart is authorized by this cleanup.
