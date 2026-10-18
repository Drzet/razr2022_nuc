# Current assignments — 2026-10-18 VPU acceptance and Boot configuration

[Review](COORDINATOR_VPU_REVIEW_2026-10-18.md) · [Status](STATUS.md) · [Policy](WORKFLOW.md). Supersedes the VPU RESUME implementation and Boot/DP documentation closure assignments.

## Active: Boot — prepare a reduced oneli build configuration

Sole implementation stream. Continue project `razr/boot@53c1b7a58099c9ad0fb111edf9f62cad8cc9797a`; use immutable kernel `7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce` and its accepted resolved configuration (artifact 12109240146, config SHA256 e10f77e9c982a4c3c81c94e69922ad8ae623b71e99df88e40c415e5a6fc0b273). This selects the previously queued build-cost reduction, before another full integration build.

1. Inspect existing project fragments, accepted resolved config and kernel Kconfig/merge machinery. Reuse them to create a reproducible oneli-specific configuration candidate; no new configuration framework and no host `localmodconfig` (host hardware is not oneli).
2. Retain every dependency required by the accepted UART/early diagnostics, pstore/ramoops support, initramfs, Debian/systemd, QEMU virtio disk/network/console tests, module loading, signed firmware/regdb and enabled radio paths. Preserve early PCI pre-power module packaging/load contract and y/m choices where consumers rely on them. Preserve accepted USB/Type-C/DP support used by diagnostic tooling; do not enable board peripherals or remove unknown dependencies speculatively. Derive exact symbols from inspected source/config and consumer scripts.
3. Remove clearly unrelated architectures/platform drivers and peripherals from the build selection only where dependency closure permits. Record retained functional groups, removal rationale, before/after resolved config diff, exact source/tool versions and y/m counts. Counts are a scope estimate, not a measured build-time saving.
4. Resolve candidate with the existing pinned toolchain/Kconfig tools; run cheap contract/assertion checks against existing Boot and Userspace consumers. Ensure all required symbols survive resolution with intended y/m values. Do not run Image/modules compilation, DT recompilation or QEMU for this config-only preparation.
5. Commit the candidate recipe/fragment and evidence on the project branch; update the canonical Boot handoff and readiness only to describe this unbuilt candidate, preserving accepted artifact identities. Stop for coordinator review before wiring it into automatic expensive builds.

No kernel source/shared DTS changes, DP/VPU/display merge, release replacement, new firmware extraction or handset operation. Future selected builds remain automatic and cheap-gated; this preparation does not change Actions policy.

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

No rebuild of accepted 7f3865e for documentation or Userspace work. The broad ARM64 defconfig + full modules build took about 48 minutes on this runner. The Boot assignment above prepares the reduced configuration with cheap validation; full compilation awaits coordinator review. Resolve Kconfig and align config-affecting tools before compilation. Check post-build assertions against the actual Kbuild target's output contract. For failures after compilation, preserve reusable build outputs where practical and rerun only the necessary failed packaging/check stage when those outputs are available; a missing build tree must be disclosed, not replaced with mismatched modules. Builds remain automatic and cheap-gated.
