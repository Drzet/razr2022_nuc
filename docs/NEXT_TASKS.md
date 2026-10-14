# Current assignments — 2026-10-14

This queue supersedes all earlier rounds, including tenth prototype instructions. [Policy](WORKFLOW.md) · [Status](STATUS.md) · [Disposition](CLEANUP_2026-10-13.md).

## VPU — closure accepted, paused

Coordinator reviewed the provenance reconstruction and executed the host failure-path checks. Sole canonical kernel candidate: `razr/vpu-provenance-v5@a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac`. Original tested upstream branch and temporary closure branches are historical; do not reset, merge wholesale, or rerun provenance reconstruction. The canonical [VPU handoff](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/handoffs/2026-10-13-vpu-tenth-recovery.md) records exact old/new mappings and evidence.

No VPU implementation is currently assigned. Keep SM8475 gated and accepted integration unchanged. Inherited IOMMU reservation failure behavior and unresolved VPU2 resource/firmware policy remain enablement gates; host mocks do not clear them. No fresh audit, extraction, rebuild, shared-DTS edit or additional documentation-only round.

## Active: USB / local Codex — PTN3222 lifecycle correction

Read [coordinator review](USB_REVIEW_2026-10-14.md). The reuse decision is complete and retained; the owner-authorized PTN3222 adaptation is retained as an experimental candidate with a concrete recovery defect. Do not repeat the identity/reuse survey or abandon the existing implementation.

**Exact inputs/ownership:** continue kernel `razr/usb-ptn3222` from `d513929e8c1ef2ea7f5158ebfb57fda99ff531e9`, project `razr/usb` from `2b64829bd78478a89e18d5bd50952f7a72e3f0c5`. No new branch needed. USB owns PTN3222 and scoped tests; this assignment also permits a minimal `drivers/phy/phy-snps-eusb2.c` error-propagation/unwind correction only if the required boundary tests demonstrate it is necessary. Shared DTS remains Boot-owned and unchanged.

1. Add a failing regression using actual production generic PHY `phy_init`/`phy_exit` dispatch/count behavior, not direct provider callback recovery. Reproduce init/tuning failure plus transient cleanup failure, then normal core init retry without unbind or direct provider exit. Correct PTN3222 recovery to retry pending cleanup safely, preserve the initiating error, avoid duplicate votes and retain faulted state on persistent cleanup failure.
2. Exercise successful init → provider exit cleanup failure → subsequent consumer reconnect through the real SNPS/core path. Check counts, reset, votes and returned errors. Prevent a successful consumer initialization that bypasses a still-faulted/reset repeater. Make only the smallest justified provider/adjacent consumer fix; no generic PHY core or DWC3 rewrite. Preserve legacy behavior and successful role replay.
3. Run focused host fault cases and compile/link affected modules against the existing reduced configuration. Reuse unchanged schema results; no full defconfig/combined image or PS5169 rebuild. Update the existing build record and canonical handoff, distinguishing direct callback tests from core/consumer-dispatched tests. Preserve tested-source/commit mapping and original source attribution; do not reconstruct historical commits just to change local author metadata.

**Deliverable/stop:** correction commits, failing-before/passing-after evidence and exact limits, posted in issue #2. Keep experimental profile ABI and board graph disabled/unselected; no datasheet sweep, extraction, binding redesign, board DTS or unrelated consumer work. The populated part remains [INFERRED]; offline correction does not require device access. Coordinator reviews this closure before moving to the queued VPU work.

## Queued after USB review — not active

1. **Coordinator: VPU enablement decision.** Review the already demonstrated missing-reservation behavior in the pinned upstream helper. Distinguish disabled-candidate acceptance from permission to enable; check narrowly for an upstream resolution before proposing any change. Record whether a source fix/provider test is needed, who owns it, and what remains hardware-dependent. Do not repeat the completed host tests or start a broad IOMMU rewrite.
2. **VPU: resource/firmware policy gap closure, subject to coordinator activation.** Use canonical kernel candidate `a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac` and existing extracted firmware/DT evidence. Reconcile only unresolved firmware/PAS, MXC/MMCX power-domain and interconnect requirements with reused Iris/remoteproc infrastructure. Deliver a source-backed resolved/unresolved table and minimal next change, or a precise evidence hold. No new firmware download/extraction, provenance reconstruction, gate removal, shared DTS edit or repeated architecture survey. Refine the exact remaining questions at activation so completed findings are not repeated.
3. **Boot then Userspace:** only after a concrete candidate/interface change is reviewed. Boot owns shared DTS and combined artifacts; Userspace consumes the resulting pinned artifact. No speculative consumer implementation or packaging replay.

## Paused

- **Boot:** resume only for a reviewed shared-DTS/candidate request or attributable new loader evidence. No packaging replay.
- **Userspace:** resume only after an actual accepted kernel/artifact/interface change affects its tests.
- **GPU:** no new work without a named source defect or hardware result.
- **Power:** retain SGM41516D vendor-source lead for future variant adaptation; no charger implementation or repeat audit now.
- **DisplayPort:** AUX-identity hold; no guessed compatible.

## Coordinator

Maintain one authoritative queue and notify the relevant issue when selecting, completing or blocking a task. Review USB's exact result before selecting implementation or advancing the VPU queue. Do not wait for fresh user permission for routine coordination within the authorized project scope. Do not label work active unless its assignment is published.

When a task arrives, inspect its actual diff and applicable evidence, accept or name the specific gap, update STATUS/NEXT_TASKS and publish the next bounded instruction in the same coordination pass. Hardware-only blockers pause that workstream, not the whole project. Do not invent dependencies between independent subsystems. No blanket round or second active subsystem is selected.
