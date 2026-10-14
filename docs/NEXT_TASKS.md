# Current assignments — 2026-10-14

This queue supersedes all earlier rounds, including tenth prototype instructions. [Policy](WORKFLOW.md) · [Status](STATUS.md) · [Disposition](CLEANUP_2026-10-13.md).

## USB / local Codex — lifecycle closure accepted, paused

Keep kernel `razr/usb-ptn3222@61202a82ad004302fcc04e321075e190f00b29ed` and project `razr/usb@63cf2a5388ad406e58ccf42344936f14c3868a54`. [Review](USB_REVIEW_2026-10-14.md) records independently reproduced before/after failures and passing 12 core/consumer plus 37 provider cases. Existing PS5169 evidence remains accepted. No further USB implementation, repeated tests, ABI redesign, combined build or active DTS is assigned. Hardware/board-contract and experimental-ABI review remain gates before integration/enablement.

## Active: VPU — resolve the remaining power and ICC source contract

**Sole active subsystem task; source analysis, not gate removal.** Project `Drzet/razr2022_nuc:razr/vpu` starts at `efadd1b29f5162369c54c33cf1c19cdeb2e293d1`; read policy/queue from current coordinator main. Kernel input is immutable `razr/vpu-provenance-v5@a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac`. Update the existing `docs/handoffs/2026-10-13-vpu-tenth-recovery.md` with one dated source-contract decision; keep detailed earlier evidence linked.

**Already complete, do not repeat:** Qualcomm v5 provenance/context/routing closure; SID mask interpretation; qualified firmware MDT/MBN span and segment lookup; PAS9 source match; stock resource extraction; basic clock-parent tracing. Start from `docs/vpu/2026-10-12-bounded-resource-translation-decisions.md`, `2026-10-12-iris-resource-loader-contract.md`, and the committed focused stock JSON on the project branch. Older provisional DMA-mask/topology statements are superseded by the corrected candidate; do not reintroduce them.

1. **Power/OPP:** trace the candidate's MXC/MMCX required-OPP consumers against the pinned SM8450/SM8475 VIDEOCC, RPMh provider and relevant vendor voltage/frequency tables. Determine which provider/corner mapping is actually evidenced and which remains unknown. Do not derive voltage corners from four frequencies alone or assume the unread divider is three. For each proposed mapping give exact source revision, symbol/property and consumer path; if absent, name the missing datum and a realistic source or hardware check.
2. **ICC:** resolve the three recorded stock routes into mainline provider/endpoint symbols and explain whether video-mem voting already traverses the LLCC segment or needs a distinct dynamic vote. Trace actual interconnect topology and vendor average/peak policy. Do not add a third path merely because stock lists three, copy vendor numeric IDs into upstream namespaces, or reuse SM8250 bandwidth tables without justification. Name the smallest necessary Iris adaptation only after the route/aggregation contract is established.
3. **Decision:** deliver a compact resolved/unresolved table, a minimal source-backed next patch plan (or specific evidence hold), and dependencies for eventual Boot-owned DTS. Keep firmware loader/PAS structural conclusions linked; signature acceptance and HFI execution remain hardware gates, not another extraction assignment.

**Stop:** commit the source-contract result and post exact SHA in issue #10. No kernel edits, new driver, shared DTS, firmware download, provenance rewrite, broad audit, schema/ARM64 rebuild or SM8475 enablement in this task. Reuse research first; a targeted upstream/vendor lookup is warranted only for a named missing mapping. USB/Power/Boot do not run concurrent implementations against this unsettled contract.

## Coordinator decision: inherited VPU IOVA failure behavior

The tested v5 helper can omit reservations on malformed input/allocation failures. Retain the disabled candidate, but do not authorize active DMA on the strength of host tests/schema alone. No local IOMMU rewrite is selected. Coordinator's 2026-10-14 narrow update check found no newer resolution in the inspected results; mainline `4056b3c9d3c92ea45955641dbafeb9b960e146ef` `drivers/iommu/of_iommu.c` still lacks this helper and `iommu-ranges` support. This is a bounded search result, not proof that no unpublished/maintainer fix exists. Recheck the relevant series/provider behavior when an enablement task is selected, then prefer an upstream fix and focused provider validation.

## Queued after VPU source-contract review — not active

Coordinator selects only the smallest supported resource patch or records the precise evidence hold. A change requiring shared DTS is handed to Boot only after its interface is fixed. Boot then builds a specifically selected combined artifact; Userspace consumes that pinned artifact. No speculative consumer work or all-agent round.

## Paused

- **Boot:** resume only for a reviewed shared-DTS/candidate request or attributable new loader evidence. No packaging replay.
- **Userspace:** resume only after an actual accepted kernel/artifact/interface change affects its tests.
- **GPU:** no new work without a named source defect or hardware result.
- **Power:** retain SGM41516D vendor-source lead for future variant adaptation; no charger implementation or repeat audit now.
- **DisplayPort:** AUX-identity hold; no guessed compatible.

## Coordinator

Maintain one authoritative queue and notify the relevant issue when selecting, completing or blocking a task. Review VPU's exact source-contract result before selecting implementation or advancing integration. Do not wait for fresh user permission for routine coordination within the authorized project scope. Do not label work active unless its assignment is published.

When a task arrives, inspect its actual diff and applicable evidence, accept or name the specific gap, update STATUS/NEXT_TASKS and publish the next bounded instruction in the same coordination pass. Hardware-only blockers pause that workstream, not the whole project. Do not invent dependencies between independent subsystems. No blanket round or second active subsystem is selected.
