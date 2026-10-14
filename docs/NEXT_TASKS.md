# Current assignments — 2026-10-14

This queue supersedes all earlier rounds, including tenth prototype instructions. [Policy](WORKFLOW.md) · [Status](STATUS.md) · [Disposition](CLEANUP_2026-10-13.md).

## USB / local Codex — lifecycle closure accepted, paused

Keep kernel `razr/usb-ptn3222@61202a82ad004302fcc04e321075e190f00b29ed` and project `razr/usb@63cf2a5388ad406e58ccf42344936f14c3868a54`. [Review](USB_REVIEW_2026-10-14.md) records independently reproduced before/after failures and passing 12 core/consumer plus 37 provider cases. Existing PS5169 evidence remains accepted. No further USB implementation, repeated tests, ABI redesign, combined build or active DTS is assigned. Hardware/board-contract and experimental-ABI review remain gates before integration/enablement.

## Active: VPU / local Codex — no-cache-discount decoder reference test

**Mapping accepted:** project `razr/vpu@3b085bb0ae3493d4ff630027b035ccbadd0fc43e`. [Review](VPU_REVIEW_2026-10-13.md). The earlier missing-input stop was correct. Coordinator now selects the proposed **no-cache-discount reference policy**, without asserting that physical cache is disabled or that L=D is a safe production LLCC vote for every workload.

**Sole active subsystem task.** Continue that project branch/head; kernel `razr/vpu-provenance-v5@a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac` stays read-only. Owner: VPU local Codex bot (user: tl-raz). Update the same canonical handoff.

1. Implement one focused host harness fetching/hash-verifying the pinned comparator decoder and necessary helpers from `LowTension/android_kernel_xiaomi_sm8475@39382bf760ccf05a8fb4dddee7138ecac02d4a59`, using the handoff's source paths/hashes. Extract the unchanged production calculation; no rewritten bandwidth formula or committed vendor driver source. Preserve provenance/notices in generated test sources. Use 64-bit host semantics matching the source's ARM64 fixed-point representation; document mocks and any extraction-only changes.
2. Selected model: cache discount false, CR=1<<16, CF=4<<16; linear NV12/P010 split output only, with mapped H264/HEVC/VP9 combinations justified by candidate capabilities. Use explicit test fixtures. For a candidate-input adapter, select max(frame_rate, operating_rate), retaining the recorded 480 startup value; reject values outside the stated reference envelope rather than silently reducing them to 30 or claiming vendor-rate equivalence. Validate candidate admission limits separately from arithmetic limits. Queued-byte bitrate uses that same rate, checked before narrowing. Unsupported or unsafe combinations must fail explicitly; this is not a requirement to support every admitted candidate workload in the unchanged reference.
3. Establish a documented safe arithmetic envelope before invoking the original body: positive dimensions/denominators, valid formats, representable signed products and bitrate rounding additions, fixed-point multiply/shift/add bounds, and output conversion. Keep checks outside the extracted formula. Exercise representative codecs/depths, baseline dimension floor, split OPB traffic, startup/rate boundaries, Q16/rounding/unit edges, and rejection just beyond arithmetic limits. Use focused undefined-behavior checks; unsigned wrap requires explicit checking too. Never repair the reference silently or claim final saturation fixes intermediate overflow.
4. Demonstrate D=L under the selected model. A small paired cache-on set is permitted solely to characterize the original source branch, explicitly synthetic, with no candidate lifecycle claim or production-policy approval. Test independent sum-before-clamp D/L, peak zero, active minimum versus explicit unvote as **host contract fixtures**, distinct from calculator outputs and real ICC execution. Reuse existing fixtures where suitable; no consumer lifecycle framework.
5. Deliver the harness, exact retrieval/extraction/compiler/run instructions, actual results and rejected-domain limits, and a concise update to the canonical handoff. Report whether a later checked port is necessary; do not implement it now. Post the exact project commit to issue #10 and stop for review. If execution is blocked, name the failed operation and use focused CI once where feasible; do not report unexecuted tests as passes.

**Scope/stop:** offline reference only. No kernel changes, production voting approval, cache-lifecycle implementation, compressed capture/encoder expansion, new ICC helper/binding, OPP rows, gate removal, firmware extraction, full build or shared DTS. Cache-aware production voting requires a reviewed activation/submission/failure/release contract. Production LLCC adequacy remains separately unproven even with no discount. Other owners remain paused.

### Held separately

- **OPPs:** MXC/MMCX provider/order and parent-level table are source-resolved. Final consumer rates require attributable divider/rounded-rate evidence and installed-driver qualification. Hardware division by three remains [INFERRED]. No repeated search absent a named new source.
- **ICC:** use disjoint VIDEO→LLCC and LLCC→DDR routes if retaining independent L/D. A long DDR route plus full L duplicates averages on shared nodes. Do not authorize route code until the bandwidth producer above is agreed.
- **Firmware/PAS/HFI and IOVA:** previous structural/host evidence remains accepted; runtime acceptance and the inherited reservation failure gate are unchanged.

## Coordinator decision: inherited VPU IOVA failure behavior

The tested v5 helper can omit reservations on malformed input/allocation failures. Retain the disabled candidate, but do not authorize active DMA on the strength of host tests/schema alone. No local IOMMU rewrite is selected. Coordinator's 2026-10-14 narrow update check found no newer resolution in the inspected results; mainline `4056b3c9d3c92ea45955641dbafeb9b960e146ef` `drivers/iommu/of_iommu.c` still lacks this helper and `iommu-ranges` support. This is a bounded search result, not proof that no unpublished/maintainer fix exists. Recheck the relevant series/provider behavior when an enablement task is selected, then prefer an upstream fix and focused provider validation.

## Queued after decoder producer review — not active

Coordinator selects only the smallest supported resource patch or records the precise evidence hold. A change requiring shared DTS is handed to Boot only after its interface is fixed. Boot then builds a specifically selected combined artifact; Userspace consumes that pinned artifact. No speculative consumer work or all-agent round.

## Paused

- **Boot:** resume only for a reviewed shared-DTS/candidate request or attributable new loader evidence. No packaging replay.
- **Userspace:** resume only after an actual accepted kernel/artifact/interface change affects its tests.
- **GPU:** no new work without a named source defect or hardware result.
- **Power:** retain SGM41516D vendor-source lead for future variant adaptation; no charger implementation or repeat audit now.
- **DisplayPort:** AUX-identity hold; no guessed compatible.

## Coordinator

Maintain one authoritative queue and notify the relevant issue when selecting, completing or blocking a task. Review VPU's exact decoder-input/result contract before selecting implementation or advancing integration. Do not wait for fresh user permission for routine coordination within the authorized project scope. Do not label work active unless its assignment is published.

When a task arrives, inspect its actual diff and applicable evidence, accept or name the specific gap, update STATUS/NEXT_TASKS and publish the next bounded instruction in the same coordination pass. Hardware-only blockers pause that workstream, not the whole project. Do not invent dependencies between independent subsystems. No blanket round or second active subsystem is selected.
