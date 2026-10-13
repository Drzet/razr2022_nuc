> Historical assignment; not an active queue. Follow current NEXT_TASKS.md.

# Next assignments — fifth coordinator review, 2026-10-12

Read [FIFTH_REVIEW.md](FIFTH_REVIEW.md). This queue supersedes [the fourth assignments](FOURTH_ASSIGNMENTS.md). Work without phone access. Keep speculative hardware claims labelled `[INFERRED]`, shared DT with Boot, and aggregate status/promotion with coordinator. No unchanged builds, full ROM rescans or repeat generic audits.

## Boot — priority 1: produce the combined build candidate

**New explicit delegation:** Boot may create and build `Drzet/linux:razr/integration-candidate` from the exact reviewed inputs below. This supersedes the earlier coordinator-only execution restriction for this candidate. Do not overwrite an existing branch; append to an attributable candidate or use a uniquely named candidate if it exists. Coordinator alone accepts/promotes `razr/integration` and edits aggregate status. Keep `master`, other agents' branches and their work intact.

1. Start from Boot `525b504b82dbca593a9a697af9be63f53915e0a3`. Review/replay GPU `4955f07a94ea3c51e423e34d819ac3f76f1c9d37` and `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`, plus only the isolated Power source series ending `564f2c7df60316db86e36d7267ddadf07bc32b7e`. Enumerate exact Power commits before replay. Record ordered original/resulting SHAs and conflict resolutions. Do not import branch-mutating workflows or unrelated inherited history. USB PHY binding is already in Boot.
2. Optional separately identified UBWC source commit `7f1d729b6f458f1e76efe2894eb3c544bc9db856` may be replayed after checking the reviewed delta; do not import its Iris ancestors. Exclude experimental Iris/PS5169 from this first candidate. Keep GPU/VPU/USB/DP/charging consumers disabled. Do not change baseline.
3. Build full ARM64 Image/modules with ordinary modpost, oneli DTB and applicable DT/schema/FDT checks. Agree a virt-capable config with Userspace before building: built-in serial, interrupt, storage, network/rootfs/initramfs facilities required by its exact QEMU command, plus one harmless loadable module for an actual guest modprobe check. A single appropriately configured Image may be used on QEMU virt with its generated DT. Do not substitute oneli DT there.
4. Publish **actual binaries**, not only build logs/hashes: Image, DTB, generated config (explicitly included even if hidden), kernel.release, Module.symvers, fully installed matching module tree with modules.dep and per-file hashes, source/ordered-commit/toolchain manifest, selected test-module identity, artifact IDs and ZIP/file SHA256. Exclude dangling build/source symlinks from portable modules archive. Keep proprietary firmware out. Match Userspace schema v3 or provide a deterministic adapter agreed with its owner.
5. Send immutable artifact references directly into the handoff/coordination issue. Success means the complete artifact set exists and can be consumed, not merely that a workflow was added. If build fails, fix concrete integration errors or publish the precise blocker; do not resume another broad stock audit instead.

Secondary: give Userspace the pinned Boot-v2 contract and confirm its semantics. Keep symbolic PVT resolution separate from actual apply. Any actual libfdt application needs original base/PVT bytes; a filtered projection is insufficient. The remaining bounded GCC device-link review and stock member work must not delay this build.

## Userspace — align v2 now, execute combined kernel when available

1. Consume Boot project `cfdecbf41a329bcc0fa3074f8de708e95ef698b1`, `configs/oneli-boot-packaging-v2.json` and its explicit-input interface. Update the pinned bridge/fixtures to v2; retain structural-only, native-not-ready and hardware-unvalidated semantics. Reject missing/null required header inputs. Do not require phone packaging or Qualcomm firmware for QEMU.
2. Coordinate the exact build/artifact contract and virt config with Boot immediately. Remove pathname-based rejection of an Image containing `oneli`; validate configuration/provenance and prohibit the oneli DT/phone packaging in the QEMU profile. Install mount cleanup before the first mount in prepare-project-qemu.sh. Exercise its actual preflight with wrong-release modules and incomplete inputs; validator-only tests and bash -n do not cover the staging code.
3. Once Boot publishes the candidate artifacts, prepare a matching initramfs and disposable disk using the already verified Debian rootfs. Execute project-kernel smoke with release and test-module settings **required**, checking uname -r, actual modprobe plus /proc/modules, systemd, configured IPv4, authenticated SSH and clean shutdown. Archive full provenance/logs and distinguish this result from the older Debian-kernel pass. No external-network claim without a corresponding test.
4. Record latest fixture success 38245293728 at `9b168c89f5d0328fd0c9a690ffd6808ffb73333d`; preserve the documented false-green correction. Native diagnostic packaging remains separate and cannot invent a console/root device/accepted placement.

Wait only for combined artifacts to run the real project-kernel guest test; interface fixes proceed now.

## VPU — bounded shared evidence plus resource translation

The accepted six-FDT extraction is unchanged at `1a59d79fda42a977956de8e06c3a60d44b2971f4`. Do not repeat it wholesale.

1. Preserve the complete derived JSON durably with SHA256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465` before artifact expiry. Its filtered nature must remain explicit. Centralize only genuinely missing raw-member access here; other agents send exact requests rather than downloading the ROM independently.
2. One bounded follow-up export, if original members can be obtained: all properties under both bases' GPU/GMU/power-level and bus-vote nodes, PVT fragment48 and relevant regulator provider properties; Boot's requested missing header fields; loadable/hash segment metadata for recovered VPU and ZAP firmware. Preserve source hashes, exact paths, raw bytes and units. A missing export field is not a missing source property. No payload binaries in git. If access requires another full ROM scan, stop and report the limitation instead of repeating the scan automatically.
3. Complete the previously assigned SID `0x2180`/`0x2187` and second-cell `0x400` semantics review; downstream flags are not automatically upstream masks or separate DMA domains. Map VIDEOCC/RPMh corners to required-opps and four required domains; resolve whether vendor clock 4 is an implicit parent. Map CNOC/DDR/LLCC aggregation through upstream topology; don't invent a third ICC handle from name counts alone.
4. Finish MBN/MDT segment bounds, relocation and split-index packaging checks. Coordinate source-request/install names with GPU/Userspace; proposed `qcom/vpu/vpu20_4v.mbn` is not hardware-loader acceptance. Retain Gen2 selection as source-based and Iris disabled/experimental.

Accept specific translation decisions or precise unresolved dependencies, not another general overview. Integration and USB work do not wait for this.

## USB — turn stock sequence evidence into a reviewable candidate

1. Full build, binding and host fault tests are now accepted at kernel `2875777fef3496f33ad6862678251d1de00ee7f6`, run 38243032057. Update stale pending-build text; no unchanged rebuild.
2. Compare all **27** stock PS5169 triplets (81 cells, 324 bytes) against candidate register programming. Propose a typed, attributable board-specific initialization/profile design preserving order/delays. Explain each supported register field and unsupported residue; do not add an opaque generic config-seq binding or silently claim EQ properties reproduce the baseline. Keep driver changes isolated and board disabled.
3. Close the real probe/unwind coverage gap with meaningful tests of production lifecycle behavior, or explicitly document what host extraction cannot cover. Inject failures after partial power-up/registration and show error return, cleanup and retry semantics. Do not count textual checks as executing probe.
4. Keep GPIO19 enable distinct from reset; no arbitrary pulse. Document suspend/resume/DP-only power retention and register replay contract from pinned vendor source. Implement active PM only if ownership and failure handling are justified; otherwise retain a concrete hold. NXP @0x4f is the reference-selected repeater, but exact compatible/silicon remains unresolved. No active repeater/Type-C graph until binding and Power/Boot dependencies are ready.

Can run concurrently with Boot, VPU and Power. Future board enablement waits for actual dependencies, not the initial combined compile.

## Power — finish read-only contract; review combined power result

1. Review the isolated signed-temperature series in Boot's combined build when available; preserve existing UML arithmetic evidence. Do not repeat unchanged builds for docs.
2. Treat known S10B/L2B/L8C mappings as consumer-provider identities. Base voltage ranges are not fully composed PVT constraints; fragment48 properties were filtered. Consume VPU's bounded export if available and have Boot confirm typed composition before promoting effective values. Electrical input-parent values remain unknown: supported binding key names do not prove oneli wiring. Keep donor VPH/BOB and A100-only PM8010 guesses out.
3. Deliver the remaining read-only GLINK/BQ27426 plan: enumerate probe, initialization, periodic and error-path writes, exact supported protocols/variants, and what must be disabled. A read-only userspace interface does not imply a driver performs no writes. Implement only justified reporting changes, independently of active SGM41516D or dual-battery charging policy.
4. Select one canonical current supply report and link it from the handoff; mark overlapping older reports superseded without erasing provenance.

Read-only audit proceeds now. Effective PVT delta waits only for missing fields; combined-link acceptance waits for Boot artifact. Active charging remains held.

## GPU — bounded follow-up; no repeated source audit

Firmware location, generic/stock differences and symbolic GX/CX/ICC mapping are accepted. Kernel `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3` has no new delta; no isolated rebuild needed.

Send VPU one exact missing-property list and ZAP loadable-segment bounds request. In parallel, finish an exact source-request/install-name/hash/format matrix, distinguishing proposed renames from loader compatibility and equal byte sizes from equal hashes. Once bounded fields arrive, decide CX-floor/bus-index translation from their units/driver semantics; hold unsupported changes. Do not require this for the disabled-GPU combined build. Keep one canonical current report and link older overlapping reports as superseded. After these bounded items, wait for new evidence/hardware; no busywork.

## DisplayPort — wait

The four-overlay matrix and binding disposition are complete. No new DP assignment or unchanged CI run is needed. Resume only with attributable AUX IC evidence (BOM/schematic/part marking/authoritative source) or a justified binding proposal. Do not invent a compatible, re-enable FSA4480 or use PS5169 as the AUX switch. USB graph review is optional only if its graph changes. Physical HPD/AUX/EDID/modeset tests await hardware and integrated USB/Power.

## Dependencies and acceptance

| Owner | Start now | Specific wait |
| --- | --- | --- |
| Boot | Combined candidate/config/build/artifact publication; v2 handoff | No phone/VPU dependency for minimal build |
| Userspace | v2 alignment, direct staging checks, config agreement | Boot artifacts for project-kernel QEMU |
| VPU | Bounded missing-field request/export and DMA/OPP/ICC/loader work | Original member access for omitted data; hardware for execution |
| USB | 27-triplet profile, lifecycle failure coverage, PM contract | Power/Boot/identity for enabled board graph |
| Power | Read-only write audit | Export for effective rail deltas; Boot for combined link |
| GPU | Exact firmware matrix/request list | Missing fields for vote decision, then hardware |
| DisplayPort | No compulsory new work | AUX part evidence and later integrated hardware |
| Coordinator | Review candidate, collect immutable evidence, promote accepted integration and selected project tooling | Boot build and Userspace guest result for those acceptance claims |

No new phone boot, secure-loader, DMA/HFI, rendering/decode, USB/DP or electrical/charging validation is claimed. A combined compile and QEMU test establish only their stated software scope.
