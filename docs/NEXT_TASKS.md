# Current assignments — 2026-10-14

This queue supersedes all earlier rounds, including tenth prototype instructions. [Policy](WORKFLOW.md) · [Status](STATUS.md) · [Disposition](CLEANUP_2026-10-13.md).

## VPU — closure accepted, paused

Coordinator reviewed the provenance reconstruction and executed the host failure-path checks. Sole canonical kernel candidate: `razr/vpu-provenance-v5@a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac`. Original tested upstream branch and temporary closure branches are historical; do not reset, merge wholesale, or rerun provenance reconstruction. The canonical [VPU handoff](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/handoffs/2026-10-13-vpu-tenth-recovery.md) records exact old/new mappings and evidence.

No VPU implementation is currently assigned. Keep SM8475 gated and accepted integration unchanged. Inherited IOMMU reservation failure behavior and unresolved VPU2 resource/firmware policy remain enablement gates; host mocks do not clear them. No fresh audit, extraction, rebuild, shared-DTS edit or additional documentation-only round.

## Active: USB — NXP reuse/adaptation decision

**Sole active subsystem task.** Work on `Drzet/razr2022_nuc:razr/usb`, current reviewed base `f0557d04c1ec93d668998a7d1dc29195fcc320be`. Read rules and this queue from coordinator **main**, not stale copies on the owner branch. Update `docs/handoffs/2026-10-13-usb-tenth-round.md` in place with a clearly dated NXP decision; retain links to completed PS5169 evidence.

**Pinned inputs:** MotorolaMobilityLLC/kernel-msm `0450c5076a8ec9415a10888c8c183ef6ff5f91b8`, `drivers/usb/repeater/repeater-i2c-eusb2.c`; existing oneli NXP-configured/Diodes-disabled stock reference and overrides; project baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. Kernel PS5169 candidate `4dcbc7ba1c04afea37ab0b0caf6b4c16bfcc3dfe` and accepted integration `2b5acf108ae37040ac1e652e029bb37f5609e886` remain unchanged.

1. Compare that vendor implementation and recorded oneli properties/register overrides with the closest existing mainline PHY/repeater implementation, including PTN3222. Pin the actual compared upstream revision; check relevant pending/community work only for the specific remaining gap. Generic `nxp,eusb2-repeater` compatibility is not proof of PTN3222 silicon identity.
2. Produce one compact mapping: compatible/identity evidence, register access and override ordering, reset versus enable GPIO semantics, supplies/delays, probe/defer/error handling, PHY/repeater consumer API and suspend/resume ownership. Link exact source locations and already-extracted stock evidence; mark assumptions `[INFERRED]`.
3. Choose direct reuse, minimal adaptation, or an evidence hold. Name exact missing evidence, smallest prospective code/binding changes, interface owner and focused validation required before implementation. Separate source-resolvable uncertainties from hardware-only checks.

**Deliverable/stop:** one updated canonical handoff with a concrete recommendation and exact references. Commit it, post the commit and decision in issue #2, then stop for coordinator review. No driver implementation, kernel branch creation, active graph/shared DTS changes, ROM extraction, generic audit, PS5169 retesting or full build. USB has no dependency on VPU; this selection reflects sequencing/resource control.

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
