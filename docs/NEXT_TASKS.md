# Current assignments — 2026-10-21 display test acceptance

[Review](COORDINATOR_DISPLAY_TEST_REVIEW_2026-10-21.md) · [Status](STATUS.md) · [Policy](WORKFLOW.md). Supersedes the earlycon parser/rendering test assignment.

## No active implementation assignment

The selected offline deliveries are complete. Do not generate another build/test round merely because an agent is idle. The reduced kernel/rootfs remains accepted for software/QEMU scope; native boot has not been demonstrated.

## GPU/display — production-path tests accepted, pause

Kernel **0739fea79154fd43658c86533e2f254ebb8a52f2**, project **cd98f2a8f61a3d2b465548f4c552f9ac159326db**, run **39262243264**, job **118092625502** accepted for production scanner/rendering/remap host-fixture scope and targeted ARM64 object compilation. Production functional logic is unchanged; the only production-file delta selects a test header under a host-only macro.

Real libfdt blobs now exercise the production scanner; actual rendering/remap code executes with host hooks. Full kernel OF address translation and hardware WC mappings remain mocked. The host suite uses distro libfdt 1.7.0, not the pinned kernel copy. Do not describe this as full kernel parser/address-translation or physical display validation.

Default remains disabled; no oneli framebuffer node, boot arguments, DSI panel or merge is assigned. No repeat build or standalone documentation closure.

## Next activation prerequisites — device evidence

When oneli is available, select one bounded stock-side observation task for Boot with GPU/display supplying the exact framebuffer questions. Reuse captured stock evidence; collect only missing installed-panel identity, framebuffer dimensions/stride/format/base/ownership and visible screen behavior through the intended boot transition. A reservation alone is insufficient. UART7 physical pad/connector and logic-level confirmation remains an independent early-output route.

This is a queued prerequisite, not authorization for flashing, guessed framebuffer writes, new source enablement or commands against an unavailable device. No native DSI panel is selected: main and cover remain unimplemented. If native panel work is selected later, compare actual vendor panel descriptions and bring up one panel first. Do not substitute another device's init tables based only on controller family.

## Userspace — reduced compatibility accepted, pause

Tested **c1b8f0aafde4133553308316dcc38f9620308873**, handoff **b82a4f1b32a0be81bf8f47a82a32d7dcdea435f1**, run **39237882830** accepted for QEMU software scope. Both diskless early loader and combined Debian guest pass using release **7.3.0-rc6-oneli-reduced1-g7f3865ee17c3**.

Rootfs artifact **12180241062**, inner tar SHA256 **d83f787677df38656c6df0a16002d98c3a93910aa717db6d7ad84b1ed80301fb**; evidence/early initramfs artifact **12180445735**, early gzip SHA256 **875eb0a1b0f63dbecaefb5160775da01bd8a3bc445ca1eb016effe3717875b7c**. Reuse these exact artifacts; no repeat guest, packaging or kernel build. Native root storage/boot and physical radios remain untested.

## Boot — reduced build accepted, pause

Delivery **b34ff6d7aafd920187155d5d8d7a8c6a7e3e4bc7**, run **39170486506**, artifact **12153785196** accepted for Image/modules/MODPOST and packaging. Coordinator independently verified release checksums and all 1,179 module hashes/vermagic identities. No repeat compilation, DT/schema tests or documentation-only closure round. Respond only to concrete producer-interface defects found by Userspace.

## VPU — RESUME adaptation accepted, pause

Kernel **daf47c502fe9c959d49fb37f10f79d5f7d037d8f**, project **c0a2ae91156f14d9000c9a159cd3178fd31fbb0b**, run **39074972666** accepted for source, production packet host tests and ARM64 Image/modules/modpost scope. Both RESUME paths honor the oneli descriptor option; six other Gen2 profiles preserve defaults. No repeated test/build or new implementation assigned.

Keep SM8475 disabled/unintegrated, VPU2, 480-fps startup and existing resource/ownership policy. Motorola firmware applicability remains [INFERRED]; /3 remains [INFERRED, USER-ACCEPTED FOR DEVELOPMENT]. Physical chip ID is not a new development gate. Hardware validation later requires PAS/init/version plus DRC and drain/restart with verified frames.

## Userspace prior regulatory correction — accepted

Source 840d53b / handoff eff19bc / run 39061160706 remain accepted. Reuse that rootfs as the input above. The new task tests compatibility with the changed kernel/configuration, not another regulatory packaging fix.

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
- **GPU/display:** host production-path tests accepted; paused. Adreno remains paused.
- **Userspace:** reduced-build QEMU compatibility accepted; paused.
- **Battery/charging:** no implementation assigned.

## CI and integration

CI maintenance assignments are complete. Builds remain automatic with relevant path/branch filters, cheap gates, reuse of identical inputs and scoped supersession cancellation. No blanket cleanup or manual-only migration.

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. Combined radio development build 7f3865e is accepted for Userspace consumption; Boot implementation is complete. DP AUX is now eligible for a separately selected integration; neither working DP nor VPU is a prerequisite for minimal native boot. No handset operation or flash assigned.

## Build cost discipline

No rebuild for documentation or unchanged Userspace work. The reduced configuration's first build is complete; reuse its artifacts. The broad ARM64 defconfig + full modules build took about 48 minutes on this runner. The reduced configuration has now been built and accepted for Userspace consumption; no further build is assigned. Resolve Kconfig and align config-affecting tools before compilation. Check post-build assertions against the actual Kbuild target's output contract. For failures after compilation, preserve reusable build outputs where practical and rerun only the necessary failed packaging/check stage when those outputs are available; a missing build tree must be disclosed, not replaced with mismatched modules. Builds remain automatic and cheap-gated.
