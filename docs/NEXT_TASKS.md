# Current assignments — 2026-10-14

This queue supersedes all earlier rounds, including tenth prototype instructions. [Policy](WORKFLOW.md) · [Status](STATUS.md) · [Disposition](CLEANUP_2026-10-13.md).

## USB / local Codex — lifecycle closure accepted, paused

Keep kernel `razr/usb-ptn3222@61202a82ad004302fcc04e321075e190f00b29ed` and project `razr/usb@63cf2a5388ad406e58ccf42344936f14c3868a54`. [Review](USB_REVIEW_2026-10-14.md) records independently reproduced before/after failures and passing 12 core/consumer plus 37 provider cases. Existing PS5169 evidence remains accepted. No further USB implementation, repeated tests, ABI redesign, combined build or active DTS is assigned. Hardware/board-contract and experimental-ABI review remain gates before integration/enablement.

## Active: VPU / local Codex — decoder bandwidth producer contract

**Previous assignment accepted:** project `razr/vpu@8add1e1e055b79bb5568669d6202e2c3ab3a2376` resolves power-provider order, parent-clock voltage contributions and disjoint ICC routes. [Review](VPU_REVIEW_2026-10-13.md). Final divided-clock OPP rows remain held; do not repeat the completed route/voltage survey.

**Sole active subsystem task.** Continue project `razr/vpu` from 8add1e1; kernel input remains `razr/vpu-provenance-v5@a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac`, read-only. Owner is the user's VPU local Codex bot. Preserve actual author/publisher attribution; do not rewrite historical metadata. Update the same canonical handoff.

1. Map every input used by the pinned comparator's **decode** bandwidth calculator to an actual field/call path in the candidate Iris decoder: codec, dimensions/frame rate, bit depth, compression/complexity, DPB/reference traffic and cache-use state. Source: `LowTension/android_kernel_xiaomi_sm8475@39382bf760ccf05a8fb4dddee7138ecac02d4a59:techpack/video/driver/variant/iris2/src/msm_vidc_power_iris2.c` and its existing callers. Classify each input as available, source-defined default, or missing. Do not infer runtime syscache activation from a DT slice name, assume the comparator is the installed Motorola driver, or treat its formulas as measured SM8475 bandwidth.
2. Select the smallest reusable decoder calculation and define the exact output contract: independent DDR average D and cache-inclusive LLCC average L in kB/s, aggregation/clamp order, peak policy and zero/unvote. Check only relevant existing Iris/Venus calculation code or pending work if needed to avoid duplicating a suitable implementation. No generic community re-audit.
3. If all required inputs can be supplied without guessing, add one focused host reference test that extracts the pinned production calculation (no duplicate formula implementation), documents retrieval/hash and exercises supported representative and boundary inputs. Demonstrate cache-on/off differences, rounding/overflow bounds and output units; source policy is not hardware calibration. Do not copy vendor driver sources into the project repository. If an input cannot be justified, stop at that specific blocker with an implementable alternative or precise evidence request; do not build an arbitrary calculator around invented defaults.

**Deliverable/stop:** one input/output mapping and executable reference result where justified, with a minimal proposed Iris patch scope. Post exact commit to issue #10 and stop for coordinator selection. No kernel implementation, new ICC helper/binding, encoder expansion, OPP rows, gate removal, firmware extraction, schema/full build or shared DTS. Producer semantics must be fixed before a consumer helper or Boot graph is commissioned.

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
