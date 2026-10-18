# Current assignments — 2026-10-19 reduced build acceptance

[Review](COORDINATOR_REDUCED_BUILD_REVIEW_2026-10-19.md) · [Status](STATUS.md) · [Policy](WORKFLOW.md). Supersedes the Boot reduced-build assignment.

## Active: Userspace — consume reduced build and validate compatibility

Sole active implementation stream. Continue `razr/userspace` from accepted **eff19bcff7d5eb0fc1f181f4c86b9aa32bb18846** after inspecting its current head; preserve intervening work. Boot producer is accepted for build/package scope, not yet runtime scope.

Immutable inputs:
- Kernel source **7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce**, workflow **ada56aded6fb6d75aea8e626e7150a7e8ea2729a**, Boot handoff **b34ff6d7aafd920187155d5d8d7a8c6a7e3e4bc7**.
- Run **39170486506**, artifact **12153785196** (`oneli-reduced-image-modules-39170486506-1`), ZIP SHA256 **550044f8b170d6dcaeeaec3f00ba71e3054655f651e28a806ab16ea5d44bccfb**.
- Exact release **7.3.0-rc6-oneli-reduced1-g7f3865ee17c3**. Config SHA256 **97ee634780847771163608e353e0086eceee6347ccd42a4d9d87d04f967981be**.
- Existing signed-regdb rootfs: artifact **12111471711**, run **39061160706**, inner tar SHA256 **630738c3ac43726199f56d326511fb8a69a443a01eea8e0a234318de5d3e8b38**.

1. Verify downloaded producer archive/release manifest, module hashes and exact kernel release. Reuse the accepted rootfs and firmware packages. Layer the new matching module tree into a versioned candidate; preserve old published archives. No bootstrap, kernel build, firmware re-extraction or package upgrades.
2. Adapt existing loader/rootfs/regdb harnesses minimally for the explicit new producer identity. Replace old hardcoded release/hash expectations with validated candidate inputs, not unchecked bypasses. Keep early initramfs loading of matching pci-pwrctrl-pwrseq; ensure no old module directory is used for the new running kernel.
3. Cheap checks first: package and dependency closure, initramfs contents, required modules, firmware/regdb signatures and immutable input hashes. Then reuse the existing diskless early-loader test and prepared Debian rootfs QEMU test for the changed kernel/config. Combine rootfs systemd/network/DNS/module and positive signed-regdb reload assertions into one guest run where practical; do not repeat duplicate comprehensive suites. Exercise actual module loading with the new release. QEMU cannot prove physical PCI enumeration or radio operation.
4. Record running release, systemd PID1, networking/DNS result, early-loader result, module loads and positive cfg80211 signed database acceptance; preserve serial logs and failure output. A changed kernel needs these compatibility checks despite unchanged Userspace packages.
5. Publish candidate rootfs/initramfs/manifests and exact source/run/artifact/hash identities in the canonical Userspace handoff. Stop for coordinator review. No phone flash, native root-device invention or promotion of diagnostic-v2.

## Boot — reduced build accepted, pause

Delivery **b34ff6d7aafd920187155d5d8d7a8c6a7e3e4bc7**, run **39170486506**, artifact **12153785196** accepted for Image/modules/MODPOST and packaging. Coordinator independently verified release checksums and all 1,179 module hashes/vermagic identities. No repeat compilation, DT/schema tests or documentation-only closure round. Respond only to concrete producer-interface defects found by Userspace.

## VPU — RESUME adaptation accepted, pause

Kernel **daf47c502fe9c959d49fb37f10f79d5f7d037d8f**, project **c0a2ae91156f14d9000c9a159cd3178fd31fbb0b**, run **39074972666** accepted for source, production packet host tests and ARM64 Image/modules/modpost scope. Both RESUME paths honor the oneli descriptor option; six other Gen2 profiles preserve defaults. No repeated test/build or new implementation assigned.

Keep SM8475 disabled/unintegrated, VPU2, 480-fps startup and existing resource/ownership policy. Motorola firmware applicability remains [INFERRED]; /3 remains [INFERRED, USER-ACCEPTED FOR DEVELOPMENT]. Physical chip ID is not a new development gate. Hardware validation later requires PAS/init/version plus DRC and drain/restart with verified frames.

## Userspace prior regulatory correction — accepted

Source 840d53b / handoff eff19bc / run 39061160706 remain accepted. Reuse that rootfs as the input above. The new task tests compatibility with the changed kernel/configuration, not another regulatory packaging fix.

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
- **Userspace:** active only for reduced-build consumption and compatibility testing above.
- **Battery/charging:** no implementation assigned.

## CI and integration

CI maintenance assignments are complete. Builds remain automatic with relevant path/branch filters, cheap gates, reuse of identical inputs and scoped supersession cancellation. No blanket cleanup or manual-only migration.

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. Combined radio development build 7f3865e is accepted for Userspace consumption; Boot implementation is complete. DP AUX is now eligible for a separately selected integration; neither working DP nor VPU is a prerequisite for minimal native boot. No handset operation or flash assigned.

## Build cost discipline

No rebuild for documentation or unchanged Userspace work. The reduced configuration's first build is complete; reuse its artifacts. The broad ARM64 defconfig + full modules build took about 48 minutes on this runner. The reduced configuration has now been built and accepted for Userspace consumption; no further build is assigned. Resolve Kconfig and align config-affecting tools before compilation. Check post-build assertions against the actual Kbuild target's output contract. For failures after compilation, preserve reusable build outputs where practical and rerun only the necessary failed packaging/check stage when those outputs are available; a missing build tree must be disclosed, not replaced with mismatched modules. Builds remain automatic and cheap-gated.
