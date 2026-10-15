# Current assignments — 2026-10-15

This queue supersedes all earlier rounds, including tenth prototype instructions. [Policy](WORKFLOW.md) · [Status](STATUS.md) · [Disposition](CLEANUP_2026-10-13.md).

## USB / local Codex — lifecycle closure accepted, paused

Keep kernel `razr/usb-ptn3222@61202a82ad004302fcc04e321075e190f00b29ed` and project `razr/usb@63cf2a5388ad406e58ccf42344936f14c3868a54`. [Review](USB_REVIEW_2026-10-14.md) records independently reproduced before/after failures and passing 12 core/consumer plus 37 provider cases. Existing PS5169 evidence remains accepted. No further USB implementation, repeated tests, ABI redesign, combined build or active DTS is assigned. Hardware/board-contract and experimental-ABI review remain gates before integration/enablement.

## Active: VPU / local Codex — checked decoder calculator, no runtime wiring

**Accepted reference:** project `razr/vpu@3a6729caf68aea40cfb80a4f449f067b6208b682`. Coordinator independently reproduced 271 checks, 21 production calls and every published result row; source/extraction/fixture hashes match. See [review](VPU_REVIEW_2026-10-13.md#extracted-reference-review--2026-10-15).

**Sole active implementation task.** Continue project `razr/vpu` from that commit and kernel `razr/vpu-provenance-v5` from `a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac`; inspect actual heads before editing, preserve history. Owner: existing VPU local Codex bot. Shared DTS remains Boot-owned.

1. Reuse the pinned Qualcomm decoder and accepted mapping/reference. Before new port code, close only the missing reuse-check scope: inspect relevant pending Iris bandwidth patches and existing community checked implementations; record exact revisions and whether they eliminate the required arithmetic adaptation. Do not repeat firmware extraction, provenance reconstruction or the completed broad source analysis. If a suitable implementation changes the plan, report it before proceeding.
2. Implement a narrowly scoped, attributable **pure checked calculator** in Drzet/linux, with no runtime caller, ICC changes or enablement. Preserve Qualcomm notices and separate upstream-derived logic from local arithmetic adaptation. Explicit u64 Q16 arithmetic must retain operation order, truncation, unusual rounding and decimal units on the accepted reference domain; widen signed products before multiplication and check additions, shifts, products, divisions and output conversion. No silent saturation or 30-fps fallback.
3. Scope stays no-cache-discount, CR=1, CF=4, four pipes, mapped H264/NV12 and HEVC/VP9 NV12/P010 split output. Keep explicit rate/dimension/format validation and distinguish candidate admission, model restrictions, arithmetic representability and route-cap adequacy. Retain max(frame_rate, operating_rate), including 480 startup, as the offline adapter policy. Unsupported/unrepresentable inputs return a defined error without usable partial outputs. No cache-on production branch, compressed capture or encoder expansion.
4. Reuse the unchanged extracted reference as the differential oracle within its safe domain. Exercise representative/boundary vectors and a bounded deterministic cross-product of the supported codecs/depths/dimensions/rates. For inputs newly made representable (including the old pixel-product and bitrate boundaries), use independently calculated wide-integer intermediate/output expectations; never run the overflowing original as an oracle. Include failure/zero-denominator/output-conversion checks and UBSan; explicitly check unsigned overflow. Compile the new kernel helper in its intended build context, but do not rerun a full Image/modules build for an unwired pure helper absent a concrete link/dependency need.
5. Return raw D/L in kB/s, without a production route clamp. Values above 15000000 are not silently declared safe. Preserve the reference tests and results. Deliver exact commits, focused test evidence, supported/rejected domain and the minimal later consumer interface in the same canonical handoff. Post the exact project/kernel commits to issue #10 and stop.

**Stop/scope:** reviewed pure calculator and tests only. No call-site integration, new ICC helper/binding, cache lifecycle, OPP rows, gate removal, shared DTS, firmware download or combined build. A wider arithmetic domain does not validate physical bandwidth, runtime rate policy or LLCC adequacy. Coordinator reviews this producer before selecting any consumer task. Boot has the separate read-only review below; all other owners remain paused.

### Held separately

- **OPPs:** MXC/MMCX provider/order and parent-level table are source-resolved. Final consumer rates require attributable divider/rounded-rate evidence and installed-driver qualification. Hardware division by three remains [INFERRED]. No repeated search absent a named new source.
- **ICC:** use disjoint VIDEO→LLCC and LLCC→DDR routes if retaining independent L/D. A long DDR route plus full L duplicates averages on shared nodes. Do not authorize route code until the checked producer and production policy are reviewed.
- **Firmware/PAS/HFI and IOVA:** previous structural/host evidence remains accepted; runtime acceptance and the inherited reservation failure gate are unchanged.

## Active: Boot — read-only schematic-to-board contract review

**Explicit concurrency exception:** VPU remains the sole implementation stream. Boot may perform this bounded independent document/source review now: inputs are the fixed [schematic evidence](oneli_schematic_evidence_2026-10-15.md), accepted kernel `2b5acf108ae37040ac1e652e029bb37f5609e886`, and existing Boot/Power handoffs. It does not touch VPU files or require VPU output. Its benefit is resolving first-boot board assumptions while the implementation task completes. Inspect current `razr/boot` project head, preserve intervening work, and update only Boot's canonical handoff/contract.

1. Reconcile reported GPIO26 TX / GPIO27 RX with the accepted GENI UART7 mux/pinctrl and console configuration. Record an exact match or mismatch and the minimal proposed correction. Physical access pads/voltage are still unknown; do not claim a usable receiver.
2. Compare the reported PM8350/PM8350C parent matrix with accepted disabled board nodes and RPMh binding groups. Produce a small proposed property/parent table, naming any unresolved provider/rail rather than copying HDK assumptions. Preserve PM8350BH versus B/C distinctions. Do not invent fixed battery voltage or enable supplies.
3. Separate newly resolved schematic facts from remaining loader RAM/placement/DT/ramdisk and physical-output gates. Return the precise next source or handset observation needed; no repeated packaging, firmware extraction or build.
4. Post the exact document commit to issue #13 (rail findings also #9) and stop for coordinator review. No kernel/DTS edits, native trial or charging changes in this assignment.

## Ordered schematic follow-ups — queued, not active

These are independent of VPU correctness; sequencing limits resource use, not technical permission to investigate them. Coordinator selects one after reviewing the current deliverables.

1. **USB:** continue existing `razr/usb` evidence and isolated `razr/usb-ptn3222@61202a82` candidate. Resolve **PTN3222BUK** register-ID compatibility against CUK/HUK checks and PM8350C GPIO7 active-low RST_N descriptor semantics. Deliver attributable compatibility/polarity decision or exact missing datum. No speculative new ID, driver, active DTS or repeated unchanged tests.
2. **DisplayPort:** AUX identity hold is removed at reference-schematic level: **WAS7227Q-10/TR**. Check existing upstream/pending GPIO-SBU support for this exact part; deliver minimal reuse/binding decision and GPIO2/71 enable/select/connector graph contract. Keep FSA4480 disabled. No guessed compatible, new I2C driver or active board integration.
3. **Power:** reconcile **SGM41516D / PM8350BH / WS4695C-12**, CHG_EN=C GPIO2 pin134, balance=BH GPIO1 pin114, battery bridge=BH GPIO3 pin139 and R909=470kΩ with existing paired-pack ownership/polarity policy. Deliver only remaining source-contract gaps; do not repeat the generic charger audit or enable charging.
4. **Boot integration:** only after reviewed property/driver contracts, select exact changes and focused validation. Userspace resumes only if its accepted input actually changes.

## Coordinator decision: inherited VPU IOVA failure behavior

The tested v5 helper can omit reservations on malformed input/allocation failures. Retain the disabled candidate, but do not authorize active DMA on the strength of host tests/schema alone. No local IOMMU rewrite is selected. Coordinator's 2026-10-14 narrow update check found no newer resolution in the inspected results; mainline `4056b3c9d3c92ea45955641dbafeb9b960e146ef` `drivers/iommu/of_iommu.c` still lacks this helper and `iommu-ranges` support. This is a bounded search result, not proof that no unpublished/maintainer fix exists. Recheck the relevant series/provider behavior when an enablement task is selected, then prefer an upstream fix and focused provider validation.

## Queued after decoder producer review — not active

Coordinator selects only the smallest supported resource patch or records the precise evidence hold. A change requiring shared DTS is handed to Boot only after its interface is fixed. Boot then builds a specifically selected combined artifact; Userspace consumes that pinned artifact. No speculative consumer work or all-agent round.

## Paused

- **Boot implementation:** held; only the read-only review above is active. No packaging replay.
- **Userspace:** resume only after an actual accepted kernel/artifact/interface change affects its tests.
- **GPU:** no new work without a named source defect or hardware result.
- **Power:** retain SGM41516D vendor-source lead for future variant adaptation; no charger implementation or repeat audit now.
- **DisplayPort:** identity resolved for the reference design; exact-part binding/graph review queued above, runtime still untested.

## Coordinator

Maintain one authoritative queue and notify the relevant issue when selecting, completing or blocking a task. Review VPU's exact decoder-input/result contract before selecting implementation or advancing integration. Do not wait for fresh user permission for routine coordination within the authorized project scope. Do not label work active unless its assignment is published.

When a task arrives, inspect its actual diff and applicable evidence, accept or name the specific gap, update STATUS/NEXT_TASKS and publish the next bounded instruction in the same coordination pass. Hardware-only blockers pause that workstream, not the whole project. Do not invent dependencies between independent subsystems. No blanket round; the only exception is Boot's bounded read-only review above.
