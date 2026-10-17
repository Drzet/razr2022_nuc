# Current assignments — 2026-10-17 Wireless/Boot review

Supersedes the morning implementation assignments. [Review](COORDINATOR_REVIEW_2026-10-17.md) · [Status](STATUS.md) · [Policy](WORKFLOW.md).

## Active: Wireless — close the actual ARM64 validation failure

Project **razr/wireless@e5176e18199377d51e6782915dc27c3018ec9257**; kernel **razr/wireless@3b674aa5c15e9334878b0241a4664f4fe88d413d**. Preserve intervening work.

1. Correct the provider assertion in .github/workflows/razr-wireless-pwrseq.yml. Run **39016225711**, job **117348898289**, failed with `Missing actual built-in provider: of_parse_phandle` after successful AArch64 vmlinux compilation. In this exact tree, include/linux/of.h defines that function inline and calls **__of_parse_phandle_with_args**, exported by drivers/of/base.c. Assert the real provider; inspect the other listed helpers for the same mistake before pushing.
2. Retain automatic cheap-first validation, real matching vmlinux exports, ordinary modules MODPOST/link, AArch64/vermagic/config checks and artifact identities. Do not suppress unresolved symbols, fabricate symvers, or change production code solely to satisfy this incorrect assertion. Batch the focused correction; no speculative trigger changes or new broad research.
3. Reuse the 17-scenario/326-assertion production-source harness and clearly retain its mocked regulator/shared-consumer boundary. Complete the automatic ARM64 job through module link. Report any further actual error rather than claiming success from vmlinux alone.
4. Update the canonical handoff's stale “running” result with the failed run, correction SHA and final completed run/job/module/config hashes. Post to #14 and stop for acceptance.

Driver design/source review is complete with no blocking source defect identified in the inspected delta. Final source/build acceptance remains pending the link result. No DTS edits or radio enablement.

## Boot — accepted disabled staging; pause

Project **razr/boot@37dba10d18516e5f4295e637013d529314a2caa4**; kernel **razr/boot@5d261b415a494621c276f8a680286c66971dc57b** accepted for disabled DTS/configuration scope. Run **39026414041**, job **117378234746** passed. No repeat build, extraction, or staging assignment.

Next integration is queued, not active: after coordinator accepts Wireless's completed module evidence, select its immutable final SHA together with this Boot staging commit for one combined enabled radio candidate/build. Review provider/ancestor enablement, shared regulator users and GPIO80 startup state against the existing pwrseq GPIOD_ASIS behavior at that point. Keep UART7 diagnostics intact; retain [INFERRED] hardware/parent assumptions. Do not simply enable every disabled board node. No physical chip-ID gate.

## Active documentation closure: DisplayPort

Kernel **d28598f544682eed5997ac9d57d423e9a5031624** is accepted for isolated AUX source/build scope. Successful automatic **38987006218** includes host/schema plus dependency-complete ARM64 link. Project **60fbc3a3dbc28d173cc67e632f57f25d99a3e58e** handoff is stale.

Append exact final run/job/artifact, config/module hashes and acceptance to the existing DP handoff; remove the obsolete current Actions hold. Preserve historical failures as history. **Do not rerun the successful build or expand driver/DRM/PHY/DTS scope.** Post the documentation commit to #11; pause.

## Accepted / paused / queued

- **Power:** b8e85bb wireless source contract accepted. Paused; respond only to a specific dependency from active owners. USB/DP 8mV and chip-ID policy stays closed. No broad voltage research.
- **Boot observability:** accepted. UART-first conditional recommendation and exact metadata retained; physical access/live RAM/retention await device observations. No repeated FDT extraction, packing or speculative framebuffer/ramoops activation.
- **USB:** 3c949fe project; 57d4d32 PS5169 and 305bc34 USB CI maintenance accepted. PTN remains 1e5268277f6d4c25cde2f3e2b3f00439107e087a. Paused.
- **VPU:** ac293ee project / c318805 kernel CI maintenance accepted; production source identical to accepted 905d2403. RESUME quirk remains queued after current radio prerequisite; not active. Preserve VPU2, disabled gate, user-accepted /3 and current startup policy.
- **GPU:** paused.
- **Userspace:** queued after accepted enabled kernel/config contract; ordinary Linux firmware, matching modules, NetworkManager/BlueZ and device-identity provenance. No rebuild now.
- **Battery/charging:** no implementation assigned.

## CI and integration

CI maintenance assignments are complete. Builds remain automatic with relevant path/branch filters, cheap gates, reuse of identical inputs and scoped supersession cancellation. No blanket cleanup or manual-only migration.

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. Disabled board delivery is accepted; after Wireless's corrected module validation, coordinator selects exact commits for enabled integration and one meaningful combined validation. DP AUX is now eligible for a separately selected integration; neither working DP nor VPU is a prerequisite for minimal native boot. No handset operation or flash assigned.
