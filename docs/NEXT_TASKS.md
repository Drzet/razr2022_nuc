# Current assignments — 2026-10-17 Userspace and earlycon review

[Review](COORDINATOR_USERSPACE_DISPLAY_REVIEW_2026-10-17.md) · [Status](STATUS.md) · [Policy](WORKFLOW.md). Supersedes previous Userspace smoke and display port assignments.

## Active: Userspace — regulatory database packaging correction

Tested source **e5de7e3961bf16fe65fd599514a6804316ef5a49**, handoff **f84d71e5e126d9f74a43b555a3062a3c3c153767** accepted for actual Debian QEMU software scope. No repeat of the unchanged completed systemd/NM/DNS smoke.

1. Confirm the handoff-reported cfg80211 regulatory.db ENOENT against preserved serial log in artifact **12110358882**, run **39058718000**. Identify the exact missing filename and configured signature requirements.
2. Use the same signed Debian snapshot to obtain the normal **wireless-regdb** package; verify actual package contents, install paths, signature and matching kernel support. Do not modify regulatory rules, fabricate a country setting or substitute a custom/unsigned database. If a different package/path is required, explain it from inspected inputs.
3. Update the existing staging recipe and produce a versioned corrected rootfs by layering only the required package/dependencies onto accepted tar **1cfb7b29b6502c08fc5e9d1139c98c8ef78012c5a46d5c24962646045372865b**. No kernel rebuild, base bootstrap or repeat firmware extraction. Preserve old artifact identities.
4. Verify installed database/signature and package hashes cheaply, then one focused guest cfg80211 load check with accepted kernel **7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce**. Check actual database acceptance, not just absence of a grep match. Reuse existing runtime harness and avoid duplicate full suites. Record exact new rootfs/package hashes and logs in canonical handoff, then stop. No physical radio claims.

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
- **VPU:** ac293ee project / c318805 kernel CI maintenance accepted; production source identical to accepted 905d2403. RESUME quirk remains queued after current radio prerequisite; not active. Preserve VPU2, disabled gate, user-accepted /3 and current startup policy.
- **GPU/display:** isolated earlycon port accepted and paused; Adreno implementation remains paused.
- **Userspace:** active only for the regulatory database correction above.
- **Battery/charging:** no implementation assigned.

## CI and integration

CI maintenance assignments are complete. Builds remain automatic with relevant path/branch filters, cheap gates, reuse of identical inputs and scoped supersession cancellation. No blanket cleanup or manual-only migration.

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. Combined radio development build 7f3865e is accepted for Userspace consumption; Boot implementation is complete. DP AUX is now eligible for a separately selected integration; neither working DP nor VPU is a prerequisite for minimal native boot. No handset operation or flash assigned.

## Build cost discipline

No rebuild of accepted 7f3865e for documentation or Userspace work. The broad ARM64 defconfig + full modules build took about 48 minutes on this runner. Before a later kernel implementation requires another expensive build, select a separate reviewed oneli configuration reduction retaining diagnostic/QEMU and required subsystem dependency closure; do not trim/rebuild now. Resolve Kconfig and align config-affecting tools before compilation. Check post-build assertions against the actual Kbuild target's output contract. For failures after compilation, preserve reusable build outputs where practical and rerun only the necessary failed packaging/check stage when those outputs are available; a missing build tree must be disclosed, not replaced with mismatched modules. Builds remain automatic and cheap-gated.
