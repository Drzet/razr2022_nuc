# Current assignments — 2026-10-17 morning delivery review

Supersedes previous queues. [Review](COORDINATOR_REVIEW_2026-10-17.md) · [Status](STATUS.md) · [Policy](WORKFLOW.md).

## Active implementation: Wireless — optional shared L7E supply

Project **razr/wireless@af57d1a8dc626992843079d987d49ac5338d780f**; kernel **razr/wireless@2b5acf108ae37040ac1e652e029bb37f5609e886**. Power contract **b8e85bbe4936814d29ac1db770e2b286c69e9dca**, docs/handoffs/2026-10-12-power-fifth-review.md. Preserve later intervening work if heads advance.

1. Perform only the focused maintained-upstream/pending-series reuse check for WCN6855 optional vddasd management. Pin closest implementation and licensing; reuse it if equivalent. No repeated radio/firmware inventory.
2. Implement the smallest missing extension in existing drivers/power/sequencing/pwrseq-qcom-wcn.c: when WCN6855 declares vddasd-supply, obtain a real regulator, propagate absent-provider/defer/errors and include its lifetime in the shared regulator dependency before radio enable. No dummy fallback. Keep property-absent WCN6855 and other variants, especially WCN6750, unchanged.
3. Use existing common pwrseq/regulator mechanisms. Ensure both radios share the vote; disabling one must retain it while the other remains active. Respect failures and balanced cleanup. Do not add a radio driver, change ath11k/HCI behavior, drive SWCTRL82, or hard-code oneli voltages into the generic driver.
4. Execute focused production-path tests for property absent/present, lookup/defer, enable failures, rollback, both target orders, stopping either target, final disable and failed second-target activation. Exercise actual shared-unit accounting or clearly distinguish mocked boundaries. Use binding fixtures where affected; vddasd is already schema-permitted, so no invented binding.
5. Cheap checks gate an automatic dependency-complete ARM64 object/module/modpost build with real regulator/pwrseq dependencies. Preserve exact code/config/toolchain/log/module identities. No unnecessary full boot image.
6. Update existing Wireless handoff with exact project/kernel commits and tests; stop for coordinator acceptance. Shared board DTS stays Boot-owned.

## Active independent implementation: Boot — disabled wireless board staging

Project **razr/boot@638a9d7989617783e2d2112847ca293cf08773a4**; kernel **razr/boot@7d30153d3b2d890a42b48b6b12bcc8e9fcc7810e**. Accepted functional integration remains **2b5acf108ae37040ac1e652e029bb37f5609e886**. Fixed inputs: Wireless af57d1a and Power b8e85bb canonical handoffs.

1. Stage the source-supported oneli PMU, ten inputs/internal LDO outputs, L7E provider/phandle, PCIe0/PHY and UART20/BT topology in Boot-owned board DTS. Use existing upstream bindings and inherited pinctrl/reset properties. Keep new providers/consumers effectively disabled and verify disabled ancestry prevents activation. Preserve UART7/serial0 and existing USB/DP pin ownership.
2. Encode deliberate source-supported active regulator constraints: S10B 1.800V; S11B 0.966–1.170V; S2E 1.012–1.040V; S12B common 1.350–2.024V; S1C 1.900–2.024V; L7E 2.800V. These are proposed consumer envelopes, not measured outputs. Check supported selector intersections and shared-consumer compatibility. Where a different constraint/vote mechanism is required, document the exact reason and implementation instead of copying broad stock initial ranges.
3. Preserve the reviewed parent graph, marking HDK-derived PMR735A connections [INFERRED]. Do not fabricate a fixed 3.7V B_PLUS provider. Use supported representation for an unmodelled physical input; report a concrete binding/provider obstacle if one exists. Unknown physical PCI/HCI revision is not a staging blocker.
4. Treat SWCTRL82 as reserved radio state/input evidence; no invented output control. Preserve inherited PCIe0 94–96 and UART20 76–79 muxing. Do not introduce a second GPIO80/81/204 owner.
5. Deliver the required config fragment and inspect resolved Kconfig (including PCI pre-power and BT_LE). Build only the staged DTB/schema and necessary configuration checks now, using consolidated automatic CI; no new Image/rootfs or firmware extraction. Confirm disabled nodes, supply phandles, pin ownership and unchanged diagnostics. Enabled runtime/module integration waits for accepted optional-supply implementation.
6. Update canonical handoff/readiness with exact commit and compiled evidence; post to #12 and stop.

**Concurrency exception:** Wireless changes generic power-sequencer code/tests; Boot changes disabled board description/config evidence. Their files are independent and the interface is the existing vddasd-supply property. This advances board preparation while the producer is validated. No merge of unreviewed producer code or radio enablement.

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

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. After the active producer and disabled board deliveries, coordinator selects enabled integration and one meaningful combined validation. DP AUX is now eligible for a separately selected integration; neither working DP nor VPU is a prerequisite for minimal native boot. No handset operation or flash assigned.
