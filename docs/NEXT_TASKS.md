# Current assignments — 2026-10-17 signed regdb review and VPU activation

[Review](COORDINATOR_REGDB_REVIEW_2026-10-17.md) · [Status](STATUS.md) · [Policy](WORKFLOW.md). Supersedes the Userspace regulatory correction and queued VPU state.

## Active: VPU — bounded firmware-specific RESUME adaptation

Userspace regulatory prerequisite is accepted; VPU is now the sole implementation stream. Continue kernel `razr/vpu-provenance-v5@c31880525671f65c2d10d8d60d2ab9475c0797e4` (production 905d2403) and project `razr/vpu@ac293ee4c22e4407d53f03ed55809da1b3eeddf4`. Read the canonical VPU handoff and its already accepted fixed-revision Xiaomi comparison; do not repeat the broad audit.

1. Implement the narrowly scoped payload-free Gen2 RESUME option for the oneli development firmware profile, preferably in its existing firmware descriptor. Cover both DRC/settings-change and drain/restart command paths. Preserve default U32 reason payloads for other profiles. Preserve upstream attribution and record the donor revision.
2. Enabled option must emit NONE/NULL/zero payload bytes, with the expected 64-byte single-command message instead of 68; preserve response/interrupt flags, session, port and command/packet IDs. Do not transplant Xiaomi VPU3 operations, limits, bandwidth tables or 30-fps policy.
3. Add cheap tests against actual production serialization for both reasons, applicable ports, option states and queue-write failure propagation. Assert exact packet fields/lengths and unchanged defaults. Reuse current harness and consolidated automatic CI; run cheap gates before the existing required ARM64 build, once for the final source. No new full-build matrix or unrelated regression campaign.
4. Record exact kernel/project commits, test/run/artifact identities and scope in the canonical handoff and issue #10, then stop for coordinator review. Keep SM8475 disabled and unintegrated; no shared DTS, release, firmware or Userspace changes.

Applicability to reference Motorola firmware `video-firmware.2.4-33580ad5a949b4d45b3b008988280e60573cd894` remains [INFERRED]. No physical chip-ID or /3 proof gate: /3 stays [INFERRED, USER-ACCEPTED FOR DEVELOPMENT]. Retain VPU2, 480-fps startup and existing admission/resource/ownership policies. On-device acceptance later needs PAS/init/version, DRC/reallocation/resume and drain/LAST/restart with verified frames, not init-only success.

## Userspace — regulatory correction accepted, pause

Tested source **840d53bbceadc4fb33248c2d2487795d35160dd0**, documentation **eff19bcff7d5eb0fc1f181f4c86b9aa32bb18846**, automatic run **39061160706** accepted for package and focused QEMU scope. New rootfs tar SHA256 **630738c3ac43726199f56d326511fb8a69a443a01eea8e0a234318de5d3e8b38**; artifact **12111471711**. Debian wireless-regdb uses its upstream-signed alternative with existing kernel 7f3865e; no kernel rebuild. No repeated smoke, bootstrap or firmware extraction assigned. Native root-device selection and handset radio behavior remain unverified.

## GPU/display — isolated port accepted, pause

Project **401d2d8006707a4f7c2ebb11d03ac2b465916d3f**, kernel **5d9e2e7b5461ad421ad74fe2b0b1f79ca05f1fdf** accepted for default-disabled source/production-predicate tests and targeted ARM64 object compilation only. Run **39058524964**, job **117471377860** PASS. Not merged into accepted radio kernel or board configuration.

No more compilation or board activation assigned. Production libfdt traversal/rendering execution and physical mapping/scanout remain outside tested scope; use real parser fixtures before a future activation/integration decision. Preserve UART-first baseline.

Workflow follow-up for the next assigned source change: add workflow/ref-scoped cancellation and upload resolved config under a non-hidden filename (current upload path out/.config lacks include-hidden-files). The current ZIP is only 494 bytes, so do not describe it as a complete archived resolved configuration. CI log establishes selected config assertions/object result; default-disabled source acceptance does not require repeating this build merely to repair evidence packaging.

## Boot — documentation closure only, no build

Accepted kernel **7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce**: run **39050113058**, DT job **117446794445** and combined job **117447403567** PASS. Image/modules/MODPOST, installation/depmod, three load-order records and final manifest verification completed.

Project handoff at **372fabd6a0688e2bbe08a2bb6e80bb4deb122fc2** still describes failed predecessor 8603c55 as current. Update its top section and machine readiness to the final successful SHA/run/artifact and completed module packaging. Preserve failed attempts as history. Do not rerun DT or kernel compilation. Pause after documentation; respond only to concrete Userspace interface dependencies.

## Wireless — paused

Accepted 5d191e2 source/build scope. Canonical handoff now records final PASS; documentation closure is complete. No repeat tests or new implementation.

## Active documentation closure: DisplayPort

Kernel **d28598f544682eed5997ac9d57d423e9a5031624** is accepted for isolated AUX source/build scope. Successful automatic **38987006218** includes host/schema plus dependency-complete ARM64 link. Project **60fbc3a3dbc28d173cc67e632f57f25d99a3e58e** handoff is stale.

Append exact final run/job/artifact, config/module hashes and acceptance to the existing DP handoff; remove the obsolete current Actions hold. Preserve historical failures as history. **Do not rerun the successful build or expand driver/DRM/PHY/DTS scope.** Post the documentation commit to #11; pause.

## Accepted / paused / queued

- **Power:** b8e85bb wireless source contract accepted. Paused; respond only to a specific dependency from active owners. USB/DP 8mV and chip-ID policy stays closed. No broad voltage research.
- **Boot observability:** accepted. UART-first conditional recommendation and exact metadata retained; physical access/live RAM/retention await device observations. No repeated FDT extraction, packing or speculative framebuffer/ramoops activation.
- **USB:** 3c949fe project; 57d4d32 PS5169 and 305bc34 USB CI maintenance accepted. PTN remains 1e5268277f6d4c25cde2f3e2b3f00439107e087a. Paused.
- **VPU:** active only for the bounded RESUME adaptation above; all other recovery/resource work remains queued.
- **GPU/display:** isolated earlycon port accepted and paused; Adreno implementation remains paused.
- **Userspace:** regulatory correction accepted; paused.
- **Battery/charging:** no implementation assigned.

## CI and integration

CI maintenance assignments are complete. Builds remain automatic with relevant path/branch filters, cheap gates, reuse of identical inputs and scoped supersession cancellation. No blanket cleanup or manual-only migration.

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. Combined radio development build 7f3865e is accepted for Userspace consumption; Boot implementation is complete. DP AUX is now eligible for a separately selected integration; neither working DP nor VPU is a prerequisite for minimal native boot. No handset operation or flash assigned.

## Build cost discipline

No rebuild of accepted 7f3865e for documentation or Userspace work. The broad ARM64 defconfig + full modules build took about 48 minutes on this runner. Before a later kernel implementation requires another expensive build, select a separate reviewed oneli configuration reduction retaining diagnostic/QEMU and required subsystem dependency closure; do not trim/rebuild now. Resolve Kconfig and align config-affecting tools before compilation. Check post-build assertions against the actual Kbuild target's output contract. For failures after compilation, preserve reusable build outputs where practical and rerun only the necessary failed packaging/check stage when those outputs are available; a missing build tree must be disclosed, not replaced with mismatched modules. Builds remain automatic and cheap-gated.
