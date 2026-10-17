# Current assignments — 2026-10-17 Userspace packaging accepted

[Review](COORDINATOR_REVIEW_2026-10-17.md) · [Status](STATUS.md) · [Policy](WORKFLOW.md). Supersedes the radio packaging implementation assignment.

## Active: Userspace — one prepared-rootfs runtime smoke test

Packaging source **8f54a679c2aa285398e4b12a5f370b5fb7f16201**, handoff **8aedb729895bfd47f19507d9b54e43c3bae8e73e**, run **39056127007** accepted for package/archive and diskless early-module QEMU scope. Work on razr/userspace, preserving intervening commits.

The new Debian rootfs was inspected and packaged, but the successful QEMU tests boot only the separate BusyBox early initramfs. This follow-up checks the changed systemd/network/service environment, not the already-proved early module insertion.

1. Reuse exact rootfs artifact **12109815613**, ZIP **74d4948115beff682e38b918854ab62cce756358998839cf63ecc6b5a83b3306**, rootfs tar **1cfb7b29b6502c08fc5e9d1139c98c8ef78012c5a46d5c24962646045372865b**. Reuse accepted kernel **7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce** from artifact **12109240146**, exact release **7.3.0-rc6-g7f3865ee17c3**. Verify hashes. No kernel rebuild, Debian bootstrap, apt reinstall or repeat firmware inventory.
2. Use existing project-kernel QEMU harness with a disposable copy of this rootfs and QEMU-only virtio disk/DT/PL011 settings. Generate only the test-specific boot wrapper/initramfs needed to mount the virtual disk. Preserve distributed rootfs/early payload hashes; no invented native oneli root device.
3. Verify actual systemd PID1, exact kernel release, matching module dependency resolution/loading, NetworkManager startup and virtual NIC address/route/DNS setup. Check D-Bus and BlueZ package/unit behavior; no Bluetooth controller exists in this QEMU setup, so a documented hardware-dependent unit skip/no-adapter result is not a failure. Test clean shutdown. Do not claim Wi-Fi association, firmware requests or Bluetooth pairing.
4. In particular verify resolver setup: staging deliberately removes temporary /etc/resolv.conf. Report whether the installed NetworkManager configuration supplies working resolver state in the booted guest; correct only demonstrated packaging defects. Preserve any temporary test credentials outside distributed artifacts.
5. Run this one meaningful automatic smoke test after cheap harness checks. Update the same canonical handoff with exact input hashes, guest outcomes, limitations and logs; post to #13 and stop. No repeat of completed diskless HOLD/early-loader tests for unchanged inputs.

All other subsystem implementation remains paused/queued. This is the sole active stream.

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
- **Userspace:** active only for the prepared-rootfs runtime smoke above.
- **Battery/charging:** no implementation assigned.

## CI and integration

CI maintenance assignments are complete. Builds remain automatic with relevant path/branch filters, cheap gates, reuse of identical inputs and scoped supersession cancellation. No blanket cleanup or manual-only migration.

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. Combined radio development build 7f3865e is accepted for Userspace consumption; Boot implementation is complete. DP AUX is now eligible for a separately selected integration; neither working DP nor VPU is a prerequisite for minimal native boot. No handset operation or flash assigned.

## Build cost discipline

No rebuild of accepted 7f3865e for documentation or Userspace work. The broad ARM64 defconfig + full modules build took about 48 minutes on this runner. Before a later kernel implementation requires another expensive build, select a separate reviewed oneli configuration reduction retaining diagnostic/QEMU and required subsystem dependency closure; do not trim/rebuild now. Resolve Kconfig and align config-affecting tools before compilation. Check post-build assertions against the actual Kbuild target's output contract. For failures after compilation, preserve reusable build outputs where practical and rerun only the necessary failed packaging/check stage when those outputs are available; a missing build tree must be disclosed, not replaced with mismatched modules. Builds remain automatic and cheap-gated.
