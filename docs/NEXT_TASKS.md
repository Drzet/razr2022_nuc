# Current assignments — 2026-10-17 combined radio build accepted

[Review](COORDINATOR_REVIEW_2026-10-17.md) · [Status](STATUS.md) · [Policy](WORKFLOW.md). Supersedes Boot's implementation assignment.

## Active implementation: Userspace — consume the accepted radio build

Project branch **razr/userspace**, reviewed head **428274b220e38d242b1cda2cfca63706f7374074**; preserve intervening work. Reuse existing Debian builder, native payload tooling and boot interface. Exact kernel **7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce**, release **7.3.0-rc6-g7f3865ee17c3**. Successful run **39050113058**, combined artifact **12109240146** (`oneli-radio-combined-39050113058-1`), ZIP SHA256 **d5ad99f03097655f03bc25b243ef2c1758b183bb49963167437750a3781a9de1**. Read the final coordinator review for Image/DTB/config hashes and qualifications.

1. Download once, verify ZIP and internal SHA256SUMS, consume the existing Image/DTB and matching radio-modules.tar.zst. No kernel rebuild; no mixing modules from a different release or the generic Debian QEMU kernel.
2. Extend existing Debian ARM64 packaging with these modules, normal firmware-atheros from signed Debian non-free-firmware, NetworkManager, BlueZ and focused diagnostics (iw, pciutils, rfkill). Pin actual package/source versions and hashes. Reuse existing Motorola inventory only if an observed firmware request later requires fallback; no speculative extraction, board-data fabrication or Xiaomi identity/NVM.
3. Include pci-pwrctrl-pwrseq and its actual dependency closure in an early initramfs and explicitly arrange its loading. Built-in PCIe host defers until the power-control child binds. Preserve modules.dep/aliases and verify module vermagic. Arrange ath11k_pci/hci_uart loading once their matching modules and firmware are accessible. Do not mistake host modprobe --show-depends for runtime operation.
4. Preserve the accepted diagnostic-v2 payload and its resident HOLD behavior as a separate release. Deliver a versioned radio-development payload/rootfs using existing interface schemas where applicable; explain any necessary extension. UFS/USB storage paths remain disabled: do not invent a native root device, partition or claim this rootfs is bootable on oneli. Keep a self-contained early diagnostic path, without requiring native storage.
5. Validate changed packaging/configuration cheaply first, inspect archive/module/firmware closure, and perform one relevant QEMU userspace/payload smoke test with explicit emulation boundaries. QEMU does not validate the oneli DTB, PMIC, PCIe radio or BT. Do not rebuild the kernel for these tests or repeat unchanged diagnostic suites without a concrete regression risk.
6. Deliver exact artifacts/hashes/package inventory, boot-interface/load-order contract and focused test results in one current Userspace handoff; post to #13 and stop for coordinator acceptance. No phone operations or Boot/kernel/DTS edits.

Sole implementation stream. VPU RESUME remains queued until this immediate radio packaging handoff; no new blanket subsystem round.

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
- **GPU:** paused.
- **Userspace:** active only under the exact-artifact assignment above.
- **Battery/charging:** no implementation assigned.

## CI and integration

CI maintenance assignments are complete. Builds remain automatic with relevant path/branch filters, cheap gates, reuse of identical inputs and scoped supersession cancellation. No blanket cleanup or manual-only migration.

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. Combined radio development build 7f3865e is accepted for Userspace consumption; Boot implementation is complete. DP AUX is now eligible for a separately selected integration; neither working DP nor VPU is a prerequisite for minimal native boot. No handset operation or flash assigned.

## Build cost discipline

No rebuild of accepted 7f3865e for documentation or Userspace work. The broad ARM64 defconfig + full modules build took about 48 minutes on this runner. Before a later kernel implementation requires another expensive build, select a separate reviewed oneli configuration reduction retaining diagnostic/QEMU and required subsystem dependency closure; do not trim/rebuild now. Resolve Kconfig and align config-affecting tools before compilation. Check post-build assertions against the actual Kbuild target's output contract. For failures after compilation, preserve reusable build outputs where practical and rerun only the necessary failed packaging/check stage when those outputs are available; a missing build tree must be disclosed, not replaced with mismatched modules. Builds remain automatic and cheap-gated.
