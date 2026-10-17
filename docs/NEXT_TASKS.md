# Current assignments — 2026-10-17 Wireless acceptance

Supersedes the earlier Wireless CI correction assignment. [Review](COORDINATOR_REVIEW_2026-10-17.md) · [Status](STATUS.md) · [Policy](WORKFLOW.md).

## Active implementation: Boot — combined radio development candidate

Work on existing project/kernel **razr/boot** branches; preserve intervening commits. Reviewed Boot inputs: project **37dba10d18516e5f4295e637013d529314a2caa4**, kernel **5d261b415a494621c276f8a680286c66971dc57b**. Reviewed Wireless producer: kernel **5d191e2dd449cb226eecd7086f76fc202a6f2257**, project handoff **44f57b4bed055a843e0f829bea79353ca548360b**. Power contract **b8e85bbe4936814d29ac1db770e2b286c69e9dca**. Accepted integration remains **2b5acf108ae37040ac1e652e029bb37f5609e886** until coordinator promotes the new candidate.

1. Combine accepted Wireless production delta/tests with accepted Boot staging, retaining commit provenance. Do not merge unrelated historical workflow definitions or revert Boot CI consolidation. Reuse the existing combined workflow; scope it to this branch and relevant inputs, cheap checks first.
2. Enable the intended PMU, PCIe0/PHY/WLAN and QUP2/UART20/BT paths with their required RPMh/regulator/provider ancestors. Review all consumers affected by shared PM8350/PM8350C provider activation; preserve deliberate voltage envelopes, selector intersections and [INFERRED] PMR735A parent qualifications. Resolve concrete source-level dependencies; no blanket enabling of other board nodes, invented B_PLUS fixed voltage or new physical chip-ID gate.
3. Review GPIO80 output-low pinctrl against the upstream GPIOD_ASIS preservation behavior before enabling the PMU. Preserve single ownership of GPIO80/81/204, no invented GPIO82 output, and UART7/serial0 diagnostics. Document the chosen startup policy from existing source evidence.
4. Resolve a complete kernel configuration and module availability/load-order contract for providers, PMU, PCI pre-power, ath11k and BT serdev. Trace the actual PCI pre-enumeration dependency/deferred-probe path; do not assume modules on disk suffice or require built-ins without a source reason. Preserve the existing diagnostic boot contract.
5. Adapt the existing compiled-DTB checker for explicitly enabled radio state, retaining supply, selector, pin, ancestry and diagnostics assertions. Run focused host/config/schema checks before one dependency-complete combined Image/DTB/modules/MODPOST build. Reuse the same compiled DTB across checks and retain inherited-warning comparison. No duplicate owner builds.
6. Deliver exact source/config/toolchain identities, Image/DTB/matching modules artifact hashes, enabled-node/shared-supply change summary and module/firmware timing contract in the existing Boot handoff/readiness record. Publish to #12 and stop for coordinator review. Do not promote accepted manifests, flash hardware, build a new rootfs, or add DP/VPU/GPU changes in this candidate.

This is the sole implementation stream. Software integration does not establish radio operation. Once accepted, Userspace receives the immutable kernel/module contract for ordinary Linux firmware and NetworkManager/BlueZ integration.

## Wireless — accepted; documentation closure only

Kernel **5d191e2dd449cb226eecd7086f76fc202a6f2257** accepted for isolated source/build scope. Run **39037486109**: cheap job **117410138942** and ARM64 module/MODPOST job **117410265783** both PASS; coordinator inspected actual final log and workflow-only correction.

Project **44f57b4bed055a843e0f829bea79353ca548360b** canonical handoff still says the final build is pending. Replace that current status with completed job/artifact/config/module hashes from the coordinator review; retain historical failures and mock-boundary disclosure. No repeat build or further driver work. Post the documentation commit to #14 and pause; respond only to concrete Boot dependencies.

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

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. Wireless and disabled board deliveries are accepted; Boot is now assigned the exact-input combined radio integration above. DP AUX is now eligible for a separately selected integration; neither working DP nor VPU is a prerequisite for minimal native boot. No handset operation or flash assigned.
