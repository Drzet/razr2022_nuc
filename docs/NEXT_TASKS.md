# Current assignments — 2026-10-16 evening

Supersedes previous queues. [Review](COORDINATOR_REVIEW_2026-10-16.md#evening-delivery-review--2026-10-16-current) · [Status](STATUS.md) · [Policy](WORKFLOW.md).

## Active implementation: DisplayPort — AUX supply lifetime and binding

Project branch **razr/displayport**, current accepted handoff **186a7f251397c87f8a68a37afa8cf0556e579c01**. Kernel branch **razr/displayport** currently remains baseline **a5ebb76233b79db01e82e061173cb73c6d2b5c6b**. Inspect actual heads; fast-forward that kernel branch to accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** before the isolated change if still at the named ancestor. Preserve any intervening work; no reset or force update. Power contract: project **b7d80a25a19b1a581880062463f468f1ce19f9ab**, canonical supply report and handoff. PTN kernel **1e5268277f6d4c25cde2f3e2b3f00439107e087a**, PS5169 kernel **4dcbc7ba1c04afea37ab0b0caf6b4c16bfcc3dfe** are reference interfaces, not permission to merge shared board code.

1. Check maintained upstream/pending gpio-sbu-mux and closest regulator-owning Type-C mux implementation for an existing equivalent. Pin the reuse source; adapt the smallest missing generic change.
2. Add WAS7227Q compatible/vendor-prefix binding support with gpio-sbu-mux fallback and required vcc-supply for this part. Preserve existing compatibles and supply-absent users.
3. If vcc-supply is present, acquire a real regulator using existing consumer APIs; propagate missing/deferred/error results, no dummy fallback. Establish disconnected OE state; enable supply before callbacks can activate OE or the Type-C objects become visible. Retain an independent enable reference throughout the bound lifetime, including PTN power-off and cable detach. No mode-by-mode rail toggling.
4. Make callback publication/unregistration, disconnected state, regulator disable and devm unwind correctly ordered for every partial probe and removal. Synchronize against callbacks; no double disable or GPIO use after release. Keep old property-absent behavior. Do not invent system-sleep retention, always-on flags or a new switch driver.
5. Focused validation: schema positive/negative WAS supply cases and existing compatible regression; execute production probe/unwind/remove boundaries with mocked regulator/GPIO/registration failures. Check no callbacks exposed on failure, no active OE before supply, and balanced lifetime including detach/PTN-off independence. Build changed ARM64 object/module and modpost/link with real regulator/Type-C dependencies; no full Image.
6. In the same canonical handoff, provide a **source-only** Xiaomi DP comparison: product kernel **fe81794b5e1b8a3f11a165f3acbfdb8fa671dbb3**, ancestor **a19585977c11fa662435b607cb9ff4ac7133092e**, our accepted integration and a pinned maintained upstream revision. Inspect dp_ctrl.c, dp_display.c, dp_aux.c, phy-qcom-qmp-combo.c and relevant GLINK code. Classify PHY-before-AUX, negotiated-rate reconfiguration/error unwind, initial DPCD retries, HPD state/IRQ semantics and QMP tables as already present, justified missing delta, or board-specific/unproven. No DRM/QMP/GLINK implementation in this assignment. No SVID patch: 0xff01 is already standard. Oneli already has 0/1/other orientation decoding.
7. Preserve sole GLINK GPIO91 ownership, PS5169 enable GPIO19 and AUX GPIO2/71. Shared DTS remains Boot-owned. Use shared L2B supplier contract; keep PTN 3.075–3.300V request (3.080V selectable, non-blocking 8mV difference). No new BUK ID/voltage-document gate, provider programming, firmware extraction or node enablement.
8. Deliver exact kernel/project commits, focused evidence and one canonical handoff in issue #11; stop for coordinator review.

**Scope:** generic GPIO mux driver, existing binding/vendor-prefix files, focused tests/evidence. Reference hardware WAS7227Q-10/TR; installed-board correspondence [INFERRED]. Full sleep/wake, parent-rail programming and phone behavior are later integration outcomes.

## Active independent source review: VPU — Xiaomi Iris compatibility comparison

Accepted correction: project **53608e54e600a8800b665772dc5c63f5ed859c56** on razr/vpu; kernel **905d2403c451838a408f6bb44e80a7cf9aa6ed10** on razr/vpu-provenance-v5. Both cleanup findings are closed for disabled development scope; do not rerun unchanged suites.

1. Compare fixed liuqin product kernel **fe81794b5e1b8a3f11a165f3acbfdb8fa671dbb3**, ancestor **a19585977c11fa662435b607cb9ff4ac7133092e**, corrected oneli candidate and maintained upstream. Inspect Iris platform table/probe, Gen2 RESUME construction, capability/clock/bandwidth policy, binding and relevant DTS. Pin upstream references and preserve attribution.
2. Explain exact resume_without_payload behavior versus oneli's current encoding and existing Motorola firmware/source evidence. Record actual firmware identity/version evidence already available; do not infer compatibility from the filename vpu20_4v.mbn alone. No new firmware download/disassembly.
3. Reconcile reported four-pipe/vpu3_ops platform selection with oneli VPU2 source evidence. Compare capabilities, resets, PAS/IOMMU, OPP/required-domain and ICC interfaces. Distinguish reused upstream support from private changes and borrowed static tables.
4. Deliver a compact table: already covered / source-supported adaptation / unresolved firmware-specific evidence, with the smallest justified future delta and precise verification. Include whether startup policy differs and why; no silent rate reduction, static-table transplant or new /3 hardware-proof gate.
5. Update the existing reuse audit/canonical handoff and post exact project commit to #10; stop. **No kernel edits, builds, broader recovery work, shared DTS or enablement.**

**Concurrency:** DP is the sole implementation stream. VPU's source comparison uses independent fixed inputs/files and resolves a concrete firmware-protocol reuse question from the corrected Xiaomi audit.

## Accepted and paused

- **Power:** b7d80a25a19b1a581880062463f468f1ce19f9ab accepted for source supply/voltage/lifetime contract. No further BUK or 8mV research. B_PLUS remains variable; BOB/S1C live programming and full sleep retention are separate later integration decisions.
- **USB:** prior isolated PTN3222/PS5169 acceptance retained. No driver/ID policy changes assigned.
- **Boot/research:** b2f9aea / 0acccb3 accepted. Queued next bounded observability review: existing Motorola framebuffer/ramoops and final-FDT/overlay evidence. Not active; no repeated package/extraction, Xiaomi addresses/IDs/v2 header or overlay sink.
- **GPU / Userspace:** paused, no changed accepted inputs.
- **Battery/charging:** no implementation assigned.

## Integration and next selection

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. After these deliveries coordinator selects Boot board staging and any justified generic DP follow-up. Boot alone owns shared DTS and specifically selected combined artifacts. DP, GPU and VPU are not prerequisites for a minimal observable native boot.

The corrected Xiaomi audit is a research input with coordinator qualifications in the current review, not authority to import its kernel, firmware, charging or partition layout. Runtime evidence on liuqin is not oneli hardware acceptance.
