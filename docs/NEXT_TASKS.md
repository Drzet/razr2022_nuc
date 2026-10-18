# Current assignments — 2026-10-18 reduced configuration build

[Review](COORDINATOR_CONFIG_REVIEW_2026-10-18.md) · [Status](STATUS.md) · [Policy](WORKFLOW.md). Supersedes the Boot configuration-only preparation assignment.

## Active: Boot — build and package the reviewed reduced configuration

Configuration preparation is accepted at project **a0726ef69177c21755bc28b60de244681bf80f40**, handoff **0e6728c8336dc6dd9b6c4dc6a46d99fe99d6a2cd**. Continue project `razr/boot` from that delivered head. Sole implementation stream.

1. Reuse exact kernel **7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce** and reduced config **97ee634780847771163608e353e0086eceee6347ccd42a4d9d87d04f967981be**, from artifact **12141466452**, run **39139991644**. Verify hashes and current contract checker before compilation. Preserve the accepted old artifacts and source. No additional trimming, source/DTS edits or subsystem merges.
2. Adapt the existing automatic build/packaging recipe in the project workflow to consume this pinned kernel/config. Keep cheap checks as prerequisites, scoped cancellation and finite timeout; documentation-only changes must not build. Do not rerun DT/schema/Wireless host suites for unchanged inputs. Reuse accepted DTB **70d5c7b08ddda1c0974ac85e95bb1328528bb533c344a0681b5e95b88cd17435** from artifact **12109240146**, with provenance/hash recorded.
3. Use a distinct explicit kernel release suffix for this configuration variant through the existing Kbuild LOCALVERSION mechanism; record the exact invocation and resolved kernelrelease. The old and new configurations must not install under the same module directory. Do not guess the resulting release string. Preserve resolved config identity, or explain any tool-derived change before compilation; match GCC/pahole and other config-affecting tools to the recorded evidence.
4. Build Image and modules once with normal MODPOST/link. Install matching modules, run depmod and capture the existing early PCI pre-power, ath11k_pci and hci_uart dependency records. Check actual Module.symvers output as in the corrected accepted recipe. Archive Image, reused DTB, resolved config, matching modules, release manifest and checksums. Keep reusable outputs if a later packaging check fails; do not repeat successful compilation unnecessarily.
5. Record elapsed compilation time, Image/module sizes and module counts against the old run with runner/config differences disclosed. Symbol-count reduction alone is not timing evidence. Record exact source/project/config/tool/run/artifact identities in the canonical handoff and readiness, then stop for review.

This is a new development build candidate, not a promoted release. No handset operation. Userspace remains paused until the exact producer artifact is reviewed; then its existing QEMU rootfs/early-loader/regdb checks will consume matching new modules without re-bootstrap or firmware extraction.

## VPU — RESUME adaptation accepted, pause

Kernel **daf47c502fe9c959d49fb37f10f79d5f7d037d8f**, project **c0a2ae91156f14d9000c9a159cd3178fd31fbb0b**, run **39074972666** accepted for source, production packet host tests and ARM64 Image/modules/modpost scope. Both RESUME paths honor the oneli descriptor option; six other Gen2 profiles preserve defaults. No repeated test/build or new implementation assigned.

Keep SM8475 disabled/unintegrated, VPU2, 480-fps startup and existing resource/ownership policy. Motorola firmware applicability remains [INFERRED]; /3 remains [INFERRED, USER-ACCEPTED FOR DEVELOPMENT]. Physical chip ID is not a new development gate. Hardware validation later requires PAS/init/version plus DRC and drain/restart with verified frames.

## Userspace — regulatory correction accepted, pause

Tested source **840d53bbceadc4fb33248c2d2487795d35160dd0**, documentation **eff19bcff7d5eb0fc1f181f4c86b9aa32bb18846**, automatic run **39061160706** accepted for package and focused QEMU scope. New rootfs tar SHA256 **630738c3ac43726199f56d326511fb8a69a443a01eea8e0a234318de5d3e8b38**; artifact **12111471711**. Debian wireless-regdb uses its upstream-signed alternative with existing kernel 7f3865e; no kernel rebuild. No repeated smoke, bootstrap or firmware extraction assigned. Native root-device selection and handset radio behavior remain unverified.

## GPU/display — isolated port accepted, pause

Project **401d2d8006707a4f7c2ebb11d03ac2b465916d3f**, kernel **5d9e2e7b5461ad421ad74fe2b0b1f79ca05f1fdf** accepted for default-disabled source/production-predicate tests and targeted ARM64 object compilation only. Run **39058524964**, job **117471377860** PASS. Not merged into accepted radio kernel or board configuration.

No more compilation or board activation assigned. Production libfdt traversal/rendering execution and physical mapping/scanout remain outside tested scope; use real parser fixtures before a future activation/integration decision. Preserve UART-first baseline.

Workflow follow-up for the next assigned source change: add workflow/ref-scoped cancellation and upload resolved config under a non-hidden filename (current upload path out/.config lacks include-hidden-files). The current ZIP is only 494 bytes, so do not describe it as a complete archived resolved configuration. CI log establishes selected config assertions/object result; default-disabled source acceptance does not require repeating this build merely to repair evidence packaging.

## Boot documentation closure — accepted

Project **53c1b7a58099c9ad0fb111edf9f62cad8cc9797a** records final kernel 7f3865e/run 39050113058 in the handoff and machine readiness. No repeat closure or build. The new Boot task above supersedes its historical paused/Userspace-active wording.

## Wireless — paused

Accepted 5d191e2 source/build scope. Canonical handoff now records final PASS; documentation closure is complete. No repeat tests or new implementation.

## DisplayPort — closure accepted, pause

Project **2f992d150b5c13b5f98c59e4b7fb9ee802ed918d** records the accepted d28598f source/build result, exact run/job/artifact/hash evidence and historical status of the Actions hold. Documentation closure is complete. No rebuild, merge or new DP implementation assigned.

## Accepted / paused / queued

- **Power:** b8e85bb wireless source contract accepted. Paused; respond only to a specific dependency from active owners. USB/DP 8mV and chip-ID policy stays closed. No broad voltage research.
- **Boot observability:** accepted. UART-first conditional recommendation and exact metadata retained; physical access/live RAM/retention await device observations. No repeated FDT extraction, packing or speculative framebuffer/ramoops activation.
- **USB:** 3c949fe project; 57d4d32 PS5169 and 305bc34 USB CI maintenance accepted. PTN remains 1e5268277f6d4c25cde2f3e2b3f00439107e087a. Paused.
- **VPU:** RESUME accepted and paused; recovery/resource work remains unassigned.
- **GPU/display:** isolated earlycon port accepted and paused; Adreno implementation remains paused.
- **Userspace:** regulatory correction accepted; paused.
- **Battery/charging:** no implementation assigned.

## CI and integration

CI maintenance assignments are complete. Builds remain automatic with relevant path/branch filters, cheap gates, reuse of identical inputs and scoped supersession cancellation. No blanket cleanup or manual-only migration.

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. Combined radio development build 7f3865e is accepted for Userspace consumption; Boot implementation is complete. DP AUX is now eligible for a separately selected integration; neither working DP nor VPU is a prerequisite for minimal native boot. No handset operation or flash assigned.

## Build cost discipline

No rebuild for documentation or unchanged Userspace work. The changed reduced configuration above warrants its first build. The broad ARM64 defconfig + full modules build took about 48 minutes on this runner. The reviewed reduced configuration is now selected for one automatic cheap-gated build under the Boot assignment above. Resolve Kconfig and align config-affecting tools before compilation. Check post-build assertions against the actual Kbuild target's output contract. For failures after compilation, preserve reusable build outputs where practical and rerun only the necessary failed packaging/check stage when those outputs are available; a missing build tree must be disclosed, not replaced with mismatched modules. Builds remain automatic and cheap-gated.
