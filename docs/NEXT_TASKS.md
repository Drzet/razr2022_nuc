# Current assignments — 2026-10-21 loader composition

[Review](COORDINATOR_BOOT_PACKAGE_REVIEW_2026-10-21.md) · [Status](STATUS.md) · [Policy](WORKFLOW.md). Component-acquisition findings accepted for bounded static scope; Boot now packages the v2 RAM-trial candidate.

## Active assignment — Boot: package one self-contained v2 RAM-trial candidate

**Owner:** Boot, project `razr/boot` from **d6b21609fd549c44614194c8b137f88072bb7178**, preserving later work. Component-source research accepted as bounded evidence; no executable route or hardware success claimed. Coordinator selects **offline v2 packaging**, not another disassembly round. Other agents remain paused.

### Immutable payloads

Reuse accepted producer run **39170486506**, artifact **12153785196**, kernel source **7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce**, release **7.3.0-rc6-oneli-reduced1-g7f3865ee17c3**:
- Image SHA256 **279431f997fc2334d92760d47c01aec2b8e12cf47e6d149d6a078f2347c330e8**.
- Oneli DTB SHA256 **70d5c7b08ddda1c0974ac85e95bb1328528bb533c344a0681b5e95b88cd17435**.
- Native early gzip initramfs from Userspace run **39237882830**, artifact **12180445735**, SHA256 **875eb0a1b0f63dbecaefb5160775da01bd8a3bc445ca1eb016effe3717875b7c**. No Debian QEMU-only initrd substitution.

### Deliverable

1. Use the existing pinned AOSP mkbootimg/unpack tools (**7209a7164f1772db43f92928012c86a00f6202ff**) and reviewed Xiaomi v2 packaging as a format comparator. Assemble one separately named Android header-v2 candidate containing the accepted raw Image, generic early initramfs and mainline DTB in its explicit embedded DTB region. Empty recovery-DTBO/second-stage fields unless a concrete source requirement is demonstrated. Record every header field and its evidence; header address fields are not proof of final physical placement.
2. Preserve UART-first cmdline `console=ttyMSM0,115200n8 loglevel=8 printk.time=1 rdinit=/init`; exclude `razr.radio_qemu_shutdown=1`. Keep the DTB byte-identical. Do not copy Xiaomi geometry, board IDs, stock overlays or vendor ramdisks.
3. Cheap input/recipe checks first, then one packaging-only job. Independently unpack and compare all three payload hashes, field sizes, page boundaries and file bounds. Retain the actual ARM64 Image runtime size/alignment constraints separately from image-file padding. Verify empty optional regions and resident init. Publish candidate, checksum manifest, exact tool/source identity and results. No kernel/DT build or duplicate QEMU test.
4. Update the existing launch-decision/readiness/handoff with a concrete proposed single RAM-only trial and stock-return procedure for later review. Explicit unknowns: downloaded-buffer vs installed-buffer selection in Motorola AvbOps callbacks, firmware mode result, board/DTBO selection, memory fixups and actual kernel placement. These are trial observations, not a demand for prior successful Linux boot. Include observable acceptance/rejection criteria and what silence cannot establish. Use only verified command syntax; do not execute handset commands.
5. Preserve stock **vendor_boot**, boot partitions, DTBO, vbmeta and slots. This v2 candidate is designed to supply DTB with the downloaded image; success on Motorola remains **[INFERRED]/UNTESTED**. Existing split-v4 artifact **12338654148** remains unchanged as fallback evidence. No partition-writing fallback is selected.

**Stop:** downloadable host-validated v2 trial candidate plus the proposed runbook, submitted for coordinator review. No device boot/flash, unlock or slot/AVB changes. Do not rerun the static trace merely to turn its historical CI status green; its salvaged artifact is already reviewed.

## GPU/display — production-path tests accepted, pause

Kernel **0739fea79154fd43658c86533e2f254ebb8a52f2**, project **cd98f2a8f61a3d2b465548f4c552f9ac159326db**, run **39262243264**, job **118092625502** accepted for production scanner/rendering/remap host-fixture scope and targeted ARM64 object compilation. Production functional logic is unchanged; the only production-file delta selects a test header under a host-only macro.

Real libfdt blobs now exercise the production scanner; actual rendering/remap code executes with host hooks. Full kernel OF address translation and hardware WC mappings remain mocked. The host suite uses distro libfdt 1.7.0, not the pinned kernel copy. Do not describe this as full kernel parser/address-translation or physical display validation.

Default remains disabled; no oneli framebuffer node, boot arguments, DSI panel or merge is assigned. No repeat build or standalone documentation closure.

## Later display activation prerequisites — device evidence

When oneli is available, select one bounded stock-side observation task for Boot with GPU/display supplying the exact framebuffer questions. Reuse captured stock evidence; collect only missing installed-panel identity, framebuffer dimensions/stride/format/base/ownership and visible screen behavior through the intended boot transition. A reservation alone is insufficient. UART7 physical pad/connector and logic-level confirmation remains an independent early-output route.

This is a queued prerequisite for display activation, not for offline Boot packaging, not authorization for flashing, guessed framebuffer writes, new source enablement or commands against an unavailable device. No native DSI panel is selected: main and cover remain unimplemented. If native panel work is selected later, compare actual vendor panel descriptions and bring up one panel first. Do not substitute another device's init tables based only on controller family.

## Userspace — reduced compatibility accepted, pause

Tested **c1b8f0aafde4133553308316dcc38f9620308873**, handoff **b82a4f1b32a0be81bf8f47a82a32d7dcdea435f1**, run **39237882830** accepted for QEMU software scope. Both diskless early loader and combined Debian guest pass using release **7.3.0-rc6-oneli-reduced1-g7f3865ee17c3**.

Rootfs artifact **12180241062**, inner tar SHA256 **d83f787677df38656c6df0a16002d98c3a93910aa717db6d7ad84b1ed80301fb**; evidence/early initramfs artifact **12180445735**, early gzip SHA256 **875eb0a1b0f63dbecaefb5160775da01bd8a3bc445ca1eb016effe3717875b7c**. Reuse these exact artifacts; no repeat guest or kernel build. Boot may consume the existing early payload in the assigned native image packaging. Native root storage/boot and physical radios remain untested.

## Boot — reduced producer and offline packaging accepted

Delivery **b34ff6d7aafd920187155d5d8d7a8c6a7e3e4bc7**, run **39170486506**, artifact **12153785196** accepted for Image/modules/MODPOST and packaging. Coordinator independently verified release checksums and all 1,179 module hashes/vermagic identities. No repeat compilation, DT/schema tests or documentation-only closure round. Native bundle run 39585458990 is also accepted for offline structure; investigate only the loader route above.

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
- **Boot observability:** accepted. UART-first conditional recommendation and exact metadata retained; physical access/live RAM/retention await device observations. Reuse existing FDT/loader evidence for the assigned packaging; no speculative framebuffer/ramoops activation.
- **USB:** 3c949fe project; 57d4d32 PS5169 and 305bc34 USB CI maintenance accepted. PTN remains 1e5268277f6d4c25cde2f3e2b3f00439107e087a. Paused.
- **VPU:** RESUME accepted and paused; recovery/resource work remains unassigned.
- **GPU/display:** host production-path tests accepted; paused. Adreno remains paused.
- **Userspace:** reduced-build QEMU compatibility accepted; paused.
- **Battery/charging:** no implementation assigned.

## CI and integration

CI maintenance assignments are complete. Builds remain automatic with relevant path/branch filters, cheap gates, reuse of identical inputs and scoped supersession cancellation. No blanket cleanup or manual-only migration.

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. Combined radio development build 7f3865e is accepted for Userspace consumption; native image packaging is complete; loader composition is assigned above. DP AUX is now eligible for a separately selected integration; neither working DP nor VPU is a prerequisite for minimal native boot. No handset operation or flash assigned.

## Build cost discipline

No rebuild for documentation or unchanged Userspace work. The reduced configuration's first build is complete; reuse its artifacts. The broad ARM64 defconfig + full modules build took about 48 minutes on this runner. The reduced configuration has now been built and accepted for Userspace consumption; no further build is assigned. Resolve Kconfig and align config-affecting tools before compilation. Check post-build assertions against the actual Kbuild target's output contract. For failures after compilation, preserve reusable build outputs where practical and rerun only the necessary failed packaging/check stage when those outputs are available; a missing build tree must be disclosed, not replaced with mismatched modules. Builds remain automatic and cheap-gated.
