# Current assignments — 2026-10-15

This queue supersedes all earlier rounds, including tenth prototype instructions. [Policy](WORKFLOW.md) · [Status](STATUS.md) · [Disposition](CLEANUP_2026-10-13.md).

## Active: USB / local Codex — PTN3222BUK identity and reset contract

**Source decision only.** Retain kernel `razr/usb-ptn3222@61202a82ad004302fcc04e321075e190f00b29ed`, existing PS5169 results and project evidence `razr/usb@63cf2a5388ad406e58ccf42344936f14c3868a54`. Inspect actual branch heads before acting; preserve intervening changes. The previous lifecycle closure remains accepted. New fixed input: [schematic evidence](oneli_schematic_evidence_2026-10-15.md), including user-corrected GPIO endpoints.

1. Resolve **PTN3222BUK** register-ID compatibility with the candidate's CUK/HUK checks using attributable NXP/other exact-part source evidence and existing Motorola implementation. Do not infer that package suffixes require distinct IDs or that matching register patterns prove a revision. Deliver a supported match decision or the exact read-only identity datum still missing; do not invent an accepted ID.
2. Reconcile physical **RST_N, PM8350C GPIO7**, active-low at the chip, with vendor DT flag/call semantics and Linux descriptor logical assertion/deassertion. State provider numbering and the required descriptor/call behavior explicitly. Reuse known S10B/L2B supply evidence.
3. Update USB's canonical handoff with the minimal patch/binding proposal, or precise evidence hold. Post exact project commit in issue #2 and stop for review. No kernel code, shared DTS, new driver, regulator enablement, repeated lifecycle tests or full build in this task.

**Concurrency:** Boot's read-only review below may continue alongside this source decision: fixed schematic input, separate handoffs and no shared-file edits. VPU is paused. This is not a blanket implementation round.

## VPU — checked calculator accepted; paused

**Accepted bounded deliverable:** project `razr/vpu@0c50bf141dbb2a96cd19e79eb35e27bb1e807a63`, kernel `razr/vpu-provenance-v5@7ac8d3afedfde74286b52e11aaa1eca42a1329a5`. Prior base a1f0288d is superseded as candidate head, preserved as history. [Coordinator review](VPU_REVIEW_2026-10-13.md#checked-calculator-review--2026-10-15-evening).

Coordinator reproduced 1,362 vectors, 3,157 C assertions, 810 safe-reference comparisons and 398 independent wider-input comparisons; hashes and result streams match. ARM64 object-build record inspected, not independently rebuilt. Acceptance covers the pure checked calculator and offline tests only; no module/full-build or hardware claim.

**Stop:** no further VPU implementation, test replay, runtime caller, ICC route/consumer, cache lifecycle, compressed capture, OPP, shared DTS, gate removal or combined build assigned. Retain raw-output and error-domain limits. A later consumer requires an explicit admission/error/rate/cache/cap policy; successful arithmetic alone cannot establish adequate physical bandwidth.

### Held separately

- **OPPs:** MXC/MMCX provider/order and parent-level table are source-resolved. Final consumer rates require attributable divider/rounded-rate evidence and installed-driver qualification. Hardware division by three remains [INFERRED]. No repeated search absent a named new source.
- **ICC:** use disjoint VIDEO→LLCC and LLCC→DDR routes if retaining independent L/D. A long DDR route plus full L duplicates averages on shared nodes. Do not authorize route code until the checked producer and production policy are reviewed.
- **Firmware/PAS/HFI and IOVA:** previous structural/host evidence remains accepted; runtime acceptance and the inherited reservation failure gate are unchanged.

## Active: Boot — read-only schematic-to-board contract review

**Active independent review:** VPU closure is accepted and paused; USB performs the independent source decision above. Boot may perform this bounded independent document/source review now: inputs are the fixed [schematic evidence](oneli_schematic_evidence_2026-10-15.md), accepted kernel `2b5acf108ae37040ac1e652e029bb37f5609e886`, and existing Boot/Power handoffs. It does not touch VPU files or require VPU output. Its benefit is resolving first-boot board assumptions while USB resolves its separate variant/reset contract. Inspect current `razr/boot` project head, preserve intervening work, and update only Boot's canonical handoff/contract.

1. Reconcile reported GPIO26 TX / GPIO27 RX with the accepted GENI UART7 mux/pinctrl and console configuration. Record an exact match or mismatch and the minimal proposed correction. Physical access pads/voltage are still unknown; do not claim a usable receiver.
2. Compare the reported PM8350/PM8350C parent matrix with accepted disabled board nodes and RPMh binding groups. Produce a small proposed property/parent table, naming any unresolved provider/rail rather than copying HDK assumptions. Preserve PM8350BH versus B/C distinctions. Do not invent fixed battery voltage or enable supplies.
3. Separate newly resolved schematic facts from remaining loader RAM/placement/DT/ramdisk and physical-output gates. Return the precise next source or handset observation needed; no repeated packaging, firmware extraction or build.
4. Post the exact document commit to issue #13 (rail findings also #9) and stop for coordinator review. No kernel/DTS edits, native trial or charging changes in this assignment.

## Ordered schematic follow-ups — queued, not active

These are independent of VPU correctness; sequencing limits resource use, not technical permission to investigate them. Coordinator selects one after reviewing the current deliverables.

1. **DisplayPort:** AUX identity hold is removed at reference-schematic level: **WAS7227Q-10/TR**. Check existing upstream/pending GPIO-SBU support for this exact part; deliver minimal reuse/binding decision and GPIO2/71 enable/select/connector graph contract. Keep FSA4480 disabled. No guessed compatible, new I2C driver or active board integration.
2. **Power:** reconcile **SGM41516D / PM8350BH / WS4695C-12**, CHG_EN=C GPIO2 pin134, balance=BH GPIO1 pin114, battery bridge=BH GPIO3 pin139 and R909=470kΩ with existing paired-pack ownership/polarity policy. Deliver only remaining source-contract gaps; do not repeat the generic charger audit or enable charging.
3. **Boot integration:** only after reviewed property/driver contracts, select exact changes and focused validation. Userspace resumes only if its accepted input actually changes.

## Coordinator decision: inherited VPU IOVA failure behavior

The tested v5 helper can omit reservations on malformed input/allocation failures. Retain the disabled candidate, but do not authorize active DMA on the strength of host tests/schema alone. No local IOMMU rewrite is selected. Coordinator's 2026-10-14 narrow update check found no newer resolution in the inspected results; mainline `4056b3c9d3c92ea45955641dbafeb9b960e146ef` `drivers/iommu/of_iommu.c` still lacks this helper and `iommu-ranges` support. This is a bounded search result, not proof that no unpublished/maintainer fix exists. Recheck the relevant series/provider behavior when an enablement task is selected, then prefer an upstream fix and focused provider validation.

## Deferred VPU consumer-policy decision — not active

The pure producer is reviewed. Before any runtime wiring, coordinator must select a bounded admission/error/rate/cache/route-cap policy task or record the precise evidence hold. No such VPU task is active now. A change requiring shared DTS is handed to Boot only after its interface is fixed. Boot then builds a specifically selected combined artifact; Userspace consumes that pinned artifact. No speculative consumer work or all-agent round.

## Paused

- **Boot implementation:** held; only the read-only review above is active. No packaging replay.
- **Userspace:** resume only after an actual accepted kernel/artifact/interface change affects its tests.
- **GPU:** no new work without a named source defect or hardware result.
- **Power:** retain SGM41516D vendor-source lead for future variant adaptation; no charger implementation or repeat audit now.
- **DisplayPort:** identity resolved for the reference design; exact-part binding/graph review queued above, runtime still untested.

## Coordinator

Maintain one authoritative queue and notify the relevant issue when selecting, completing or blocking a task. Review VPU's exact decoder-input/result contract before selecting implementation or advancing integration. Do not wait for fresh user permission for routine coordination within the authorized project scope. Do not label work active unless its assignment is published.

When a task arrives, inspect its actual diff and applicable evidence, accept or name the specific gap, update STATUS/NEXT_TASKS and publish the next bounded instruction in the same coordination pass. Hardware-only blockers pause that workstream, not the whole project. Do not invent dependencies between independent subsystems. No blanket round; only USB's source-contract decision and Boot's independent read-only review are active.
