> Historical assignment; not an active queue. Follow current NEXT_TASKS.md.

# Next assignments — fourth coordinator review, 2026-10-12

Read [FOURTH_REVIEW.md](FOURTH_REVIEW.md) for reviewed SHAs, independently checked CI and source findings. These assignments replace [THIRD_REVIEW.md](THIRD_REVIEW.md). Work without phone access. Baseline unchanged; Boot owns shared DT, coordinator owns integration and aggregate status. Do not repeat successful builds or generic audits without a changed input or concrete remaining question.

## VPU extraction amendment — 2026-10-12

**Shared extraction is complete. Start the other agents now.** Read [FOURTH_REVIEW_VPU_UPDATE.md](FOURTH_REVIEW_VPU_UPDATE.md) for verified artifact hashes, pinned source links and coordinator-checked symbolic supplies. This amends the fourth assignment; no other subsystem has completed its assigned work.

## Priority and ownership

Current parallel priorities: **consume the completed six-FDT export** and **build one combined kernel/artifact set**. Firmware location and requested stock property publication are resolved; active DT selection is not. Keep unresolved hardware consumers disabled. All hardware assumptions remain `[INFERRED]`.

### VPU — extraction accepted; resource translation next

1. The shared six-FDT export is accepted at project `1a59d79fda42a977956de8e06c3a60d44b2971f4`, run 38220276125. Do not repeat the extraction. Preserve the complete derived JSON durably with its verified digest before the Actions artifact expires; a versioned compressed metadata file or equivalent durable project asset is appropriate. No raw proprietary firmware payloads.
2. Focus on translating downstream nonsecure contexts SID `0x2180` and `0x2187` into upstream DMA ownership/allocation. Audit the meaning of the second IOMMU cell, including `0x400`; do not presume downstream flags equal upstream mask semantics or that listing two SIDs creates two independent DMA domains for one device.
3. Trace VIDEOCC/RPMh voltage-corner data to the four required upstream domains/OPPs. Exact stock rates are available, but frequency alone does not supply required-opps mappings. Determine whether the fourth vendor clock is an implicit upstream parent rather than another required consumer clock.
4. Map CNOC/DDR/LLCC endpoints and vote semantics into upstream topology. Determine whether existing paths aggregate the required LLCC vote or need an additional path, then propose only justified code. Three vendor names versus two upstream names alone is not proof that a third handle is the correct fix. Retain unsupported bandwidth interpolation as a hold.
5. Complete the bounded loader-format check for the recovered MBN/MDT (loadable segment and hash-segment bounds, relocation and indexed split filenames). Treat `qcom/vpu/vpu20_4v.mbn` as a proposed install convention until accepted by Boot/Userspace; Gen2 remains statically selected, not verified by the version string. No new full compile for comment-only `869cf4a6...`.

Acceptance: durable shared metadata, specific DMA/OPP/ICC translation decisions and loader packaging checks. Keep the experimental Iris series separate from minimal integration and the VPU node disabled.

### Boot — resolve GCC and make packaging inputs explicit

1. Follow [GCC_PHY_CLOCK_RECLASSIFICATION.md](GCC_PHY_CLOCK_RECLASSIFICATION.md): coordinator verified CCF orphan handling and UART clock independence. Downgrade the seven warnings to deferred feature inputs, not demonstrated minimal-boot blockers. Complete only the remaining bounded device-link/probe-order review and future runtime checklist. Associate UFS with internal-storage boot, USB3 with SuperSpeed and PCIe with later link consumers. Do not wait for firmware extraction or enable unused PHYs to clear warnings.
2. Consume the completed export now. First fix `inspect_vendor()` unpadded concatenation: the second 479481-byte FDT starts at offset 479481, not a four-byte boundary. Add this regression case. Resolve PVT overlay index 3 (`0x45/0xc000`) against base candidates MSM530 and MSM540 using typed properties, symbols and fixups; document what is symbolically resolved versus actually applied with libfdt. Use the other variants for differences, particularly A100-only PM8010 data. Do not claim active bootloader selection or reconstruct original DTB bytes from a filtered JSON projection. Publish one shared effective-property report for USB/Power/DP.
3. Correct packaging prototype: vendor reference addresses are now published (`0x8000`, `0x1000000`, `0x100`, `0x1f00000`), with legacy-LZ4 magic and fragment metadata. Boot image OS-version data was not extracted in this run. Reference loading addresses and OS-version fields are currently copied implicitly. Make inherited fields explicit, provenance-backed manifest inputs or an explicitly rejected unresolved state. Separate structural-format validation, native composition readiness and hardware acceptance. Do not set a generic `verified` flag to appease Userspace.
4. Agree a versioned machine-readable contract with Userspace. Validate generated candidate layout using an independent AOSP parser/packer at a pinned revision, including payload identity and changed-size/alignment cases; an identity copy plus own parser is insufficient independent evidence. Use bounded real-member data when available, without requiring a full ROM download. No flashing task.
5. Correct schema CI provenance: run 38182280401 checked out `2b473619...`, not `525b504...`; the latter only changes the FDT workflow pin and has its own passing FDT run. Keep disabled USB2/GLINK staging. The USB PHY binding is already present on Boot; do not apply it twice.

Acceptance: seven-clock disposition, usable per-variant comparison, explicit packaging inputs and compatible Userspace schema. These do not block starting a disabled-peripheral combined compile.

### GPU — consume completed firmware evidence; keep vote work bounded

1. Update handoff: full Image/modules run 38178986611 passed at kernel `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`. GMU fix is a candidate for combined integration; no unchanged isolated rebuild.
2. Replace stale “ZAP unlocated” report with VPU's actual SQE/GMU/ZAP records. Compare with pinned linux-firmware revisions using exact hashes/formats and source request names. Determine whether proposed filename installation is sufficient or format differs; a rename is not evidence of compatibility. Reuse existing extraction evidence and coordinate any genuinely required bytes with VPU.
3. Inspect the completed export for GPU/GMU OPP, CX and bus properties; use its typed raw values and pinned driver evidence to resolve the specific CX-floor and bandwidth-index gaps. Give a patch only where translation is justified; otherwise leave a concrete hold. No repeated general GPU audit. Shared UBWC source review is complete; retain its `[INFERRED]` physical-profile limit.

Acceptance: exact firmware install/compatibility matrix and vote-gap disposition. GPU stays disabled; device firmware authentication/rendering await hardware.

### USB — fix durable PS5169 failure semantics

1. On the owned `razr/usb-ps5169` candidate, propagate register/EQ write failures through initialization and mode callbacks. Ensure failed transitions can be retried; do not update cached mode/orientation/SVID as successfully applied before writes succeed. Inspect unchanged-mode/new-SVID handling and downstream mux/switch failure ordering.
2. Add meaningful injected-I/O-failure coverage for probe and transitions, validating returned errors, cached state/retry and supply cleanup. Compile changed driver with dependency-complete linking. Preserve original authorship and separate changes.
3. Correct endian-safe interpretation of `__le16` chip ID/revision. Resolve reset-versus-enable API only from source/binding/electrical evidence, not pulse guesses; document suspend/resume ownership and required reinitialization. An explicit hold is acceptable where evidence stops.
4. Consume the export now: all four overlays favor NXP @0x4f and explicitly disable Diodes @0x6c. PS5169 @0x30 is `ok` and GPIO19 is named enable. Trace vendor operations/pinctrl sequencing against the candidate reset API and exact 29 configuration triplets; no automatic reset-pulse translation. Coordinator resolved symbolic NXP supplies to S10B/L2B and PS5169 supplies to S10B/L8C (see amendment). Confirm provider definitions and local reset GPIO with Boot/Power, and send precise contract corrections. Exact NXP silicon/compatible support and physical sequencing remain unproven; stop describing reference repeater selection as wholly unknown.

Acceptance: reviewable error-handling series with failure tests; bounded reset/PM and variant disposition. Existing full build is accepted; PS5169 remains an experimental disabled-board candidate.

### Power — integration review and minimal read-only scope

1. Review standalone series `564f2c7df60316db86e36d7267ddadf07bc32b7e` in combined build; retain original UML arithmetic tests. Fix CI trigger scope so cumulative PR diffs do not rebuild unchanged kernel objects on each documentation commit.
2. Consume the completed PVT index-3/base symbol export now. NXP S10B/L2B and PS5169 S10B/L8C consumer references can be symbolically resolved; distinguish these from each regulator’s upstream electrical parent and enabled state. Audit actual min/max voltage and upstream parent properties; exclude A100-only PM8010 i/j rails from PVT without evidence. Update only evidence-backed parent mappings. Review Boot's current `525b504...` staging, replacing stale `6eec...` reference. Prioritize dependencies required by minimal boot and USB2.
3. Define a minimal read-only battery/thermal reporting plan: exact supported protocols, ownership, missing driver behavior, and which paths must remain disabled to avoid charger/load-switch writes. Identify the exact oneli driver source or authoritative variant data before proposing SGM41516D support; the SM8250-family comparator is not that proof.
4. Keep dual-battery charge control and active policy on hold until variant and fail-safe ownership are established. Do not start a wholesale Motorola charging-manager port to keep the agent occupied.

Acceptance: combined temperature-fix review, stock rail delta, bounded read-only reporting contract with explicit stops.

### DisplayPort — resume the final variant disposition now

The property wait is closed. Consume all four overlays: each disables two FSA4480-targeted fragments and supplies independent AUX GPIO2/71 properties. Coordinator verified the PVT fixups resolve those GPIO references to the base TLMM symbol. Update the pending matrix with actual values and symbol targets, coordinating composition with Boot. Base FSA4480 presence is not an enablement argument.

Complete one binding disposition: existing supported part, defensible new binding with evidence, or unresolved identity. If the independent AUX part remains unknown, hold board enablement pending attributable part information/hardware. Review USB graph/failure handling concurrently if useful; do not repeat generic audits or force PS5169 to represent the AUX mux.

### Userspace — project-kernel interface next

1. Record fresh full-build success 38180519542 at `e14f618fc1c55b3581e3bf082c1d12bbb0b05e03`, not only the replay. Retain ownership/SSH/clean-shutdown evidence. Current test establishes configured IPv4 and host SSH; do not call it external-network validation.
2. Consume the new header/fragment and proposed VPU firmware-install metadata, then align artifact schema with Boot. Native stock addresses remain reference inputs, not accepted load-placement values. Keep VPU firmware requirements scoped to a future enabled VPU profile; do not require those binaries for QEMU or minimal initramfs.  Separate file consistency, structural packaging, native readiness and hardware validation. Represent an explicitly justified empty firmware/module requirement set for a selected QEMU or minimal configuration without allowing unknown requirements to pass. Do not require oneli packaging or Qualcomm firmware for QEMU virt.
3. Prepare a consumer for coordinator's exact combined Image, generated config, release, Module.symvers and matching installed modules. Build a new matching initramfs; preserve same-build provenance and module hashes. Use QEMU virt's DT, never the oneli DT, and perform a real module load plus systemd/network/SSH/shutdown checks. A module deliberately built for a mismatched release must fail the gate.
4. Design a separate native early-initramfs diagnostic artifact using Boot's eventual native contract. No guessed console, storage device, root partition or firmware requirement. This preparation can proceed before combined artifacts exist; execution of project-kernel smoke waits for them.

Acceptance: schema agreement and ready project-kernel test consumer; then one exact combined-artifact QEMU pass when supplied. Desktop/Docker expansion remains lower priority than this interface.

## Coordinator integration work package

Select a minimal candidate from Boot `525b504b82dbca593a9a697af9be63f53915e0a3`, GPU chip-ID `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`, GMU fix `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`, and the isolated Power series ending `564f2c7df60316db86e36d7267ddadf07bc32b7e`. Review/replay exact source commits and record new SHAs. Boot already contains the USB PHY binding. Exclude branch-mutating import workflows and unrelated inherited history.

The single UBWC commit `7f1d729b6f458f1e76efe2894eb3c544bc9db856` may be included as a separately labelled provisional SoC prerequisite after its source review; do not merge its Iris ancestors. Keep Iris RFC and PS5169 experimental series separate from the first minimal candidate; add them only through explicit later candidate selection, with USB fixes reviewed. No active GPU/VPU/USB/DP/charging consumer enablement is implied.

Produce one combined ARM64 Image/modules and oneli DT/schema/FDT pass with ordinary modpost. Export actual Image, installed modules, Module.symvers, generated config, kernel release, DTB, tool versions, hashes and ordered commit manifest. Ensure the selected configuration supports QEMU virt without substituting the oneli DT. Share immutable artifact IDs/digests with Userspace. Integrate selected project tooling/evidence into coordinator main through reviewed file sets; do not merge stale aggregate STATUS/NEXT_TASKS from subsystem branches.

This review defines the package; **no combined branch/build has been created or accepted by this review**. The combined compile does not wait for completed stock composition or hardware; later board enablement needs its own evidence.

## Concurrency and stop conditions

| Owner | Work immediately | Wait only for |
| --- | --- | --- |
| VPU | DMA/OPP/ICC translation, loader checks, durable metadata preservation | Physical PAS/HFI/decode |
| Boot | Unpadded FDT parser fix, composition/symbol resolution, packaging | Runtime selection only; extraction no longer blocks |
| GPU | Firmware comparison and exported GPU/CX/bus property analysis | Hardware for specifically unresolved runtime claims |
| USB | PS5169 fixes and actual NXP/PS5169 property translation | Boot composition/Power review for final board changes |
| Power | PVT supply/voltage mapping, standalone review, read-only plan | Exact charger variant evidence for active driver support |
| DP | Complete actual AUX variant matrix and binding disposition | Part evidence/hardware if identity remains unknown |
| Userspace | Schema alignment and project-kernel consumer | Combined artifacts for the new kernel smoke run |
| Coordinator | Selected integration/build/artifact publication | Only concrete source-review/build failures; no phone needed |

Runtime phone gates remain native boot/diagnostics, firmware authentication, DMA/HFI, rendering/decode, USB/DP and electrical/thermal/charging behavior. Neither QEMU nor successful source/schema checks closes them.
