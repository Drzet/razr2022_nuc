# First subsystem review and next assignments

Reviewed 2026-10-11. Working constraint: the owner has no access to the phone. All assignments below have deliverables achievable in GitHub; physical tests are deferred explicitly. Inferred hardware claims must retain `[INFERRED]` labels.

## Review outcome

The clean upstream ARM64 Image/dtbs build passed [run 38144632260](https://github.com/Drzet/razr2022_nuc/actions/runs/38144632260). This does not cover any subsystem patch, kernel modules, schema validation or phone operation. The previous local toolchain failure is historical, not a current project-wide build blocker.

Seven kernel commits are present beyond the baseline across the reviewed branches: five Boot commits, one GPU commit and one USB commit. Power, DisplayPort and VPU have research deliverables but no subsystem implementation yet. Kernel integration is pending the checks below; documentation consolidation does not merge kernel branches.

| Owner | Reviewed kernel head | Assessment |
| --- | --- | --- |
| Boot | `cb9105ebeb9485e31d044d4fa69396b415523669` | SM8475 include, minimal oneli DTS, DTB target and bindings; source-only. Fix disabled UART parent before normal console support can be claimed. |
| GPU | `4955f07a94ea3c51e423e34d819ac3f76f1c9d37` | Adds chip ID `0x07030002` to existing A730 profile. Profile reuse remains a compatibility hypothesis requiring further audit and runtime testing. |
| USB | `0119d73b40bed1041278cf9307bdec9c17880618` | Adds SM8475 eUSB2 PHY binding fallback. This is a binding addition, not complete USB enablement. |
| VPU | `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` | HFI/platform investigation only. Iris platform extension remains a hypothesis. |
| Power | `cb9105ebeb9485e31d044d4fa69396b415523669` | Inherits Boot changes; no power-specific patch. Useful rail and charging evidence. |
| DisplayPort | `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` | Routing audit and dock test procedure; no kernel patch. |

## Boot Sol — priority 1

1. Fix the enabled `uart7` node's disabled `qupv3_id_0` parent in the oneli DTS. Inherited `sm8450.dtsi` marks `geniqup@9c0000` disabled; normal OF platform enumeration cannot probe this child through that disabled bus. Earlycon is a separate path and is not proof of normal UART operation. Audit pinctrl, clock and interconnect dependencies too.
2. Build the oneli DTB and run applicable board, pinctrl and SoC binding checks against the exact branch SHA. Report newly introduced warnings separately from baseline warnings. Do not interpret successful dtc compilation as a full schema pass.
3. Audit all inherited reserved-memory regions against pinned Motorola sources and the selected public stock DTB/DTBO, not only ADSP/video. Record any overlap and unresolved revision-dependent selection. Keep consumers disabled where their memory or power contract is unknown.
4. Own shared board/SoC DT edits. Incorporate source-supported regulator and USB/GPU proposals as separate reviewable changes after reconciling labels and dependencies. Inspect stock boot headers and packaging offline; record a candidate layout without claiming it matches the unavailable phone.

Acceptance: parent-bus fix commit, exact DTB/schema commands and logs, resolved-DT dependency/reservation report, explicit unknowns. Physical UART accessibility and actual boot remain deferred.

## GPU Sol — priority 1

1. Compile the changed MSM/Adreno driver. ARM64 defconfig uses MSM as a module, so the existing Image-only build does not validate this patch. Record the resolved configuration and module or equivalent driver build output.
2. Audit revision-specific downstream quirks against the reused A730 profile, with pinned source citations; a matching chip ID alone does not establish identical programming or firmware requirements.
3. Submit a Boot-owned SM8475 OPP proposal that removes inherited SM8450-only entries before adding Cape entries. Include a compiled-DT check of the final frequency set and relevant voltage/corner data; avoid silently combining two OPP tables.
4. Share the stock-firmware manifest work with VPU: identify SQE, GMU and board-specific signed ZAP files and hashes. Record uncertainties about secure loading and firmware/profile compatibility.

Acceptance: driver build evidence, profile/OPP comparison and reviewable DT proposal. GMU startup, secure firmware acceptance, rendering, stability and frequency transitions require the phone later.

## USB Sol — priority 1

1. Run `dt_binding_check` for the modified PHY binding; validate the corresponding DT usage with the Boot branch when available. Separate binding acceptance from driver and board readiness.
2. Complete the NXP repeater audit: downstream initialization, register IDs, reset and supply sequencing versus the proposed upstream PTN3222 implementation. Treat PTN3222 identification as unconfirmed unless independent source evidence establishes it. Check vendor register writes explicitly; do not assume generic I2C address agreement proves identity.
3. Pin the PS5169 patch series/version and dependencies, review its reset requirement against oneli evidence, and propose a source-supported adaptation where appropriate. Do not fabricate a reset GPIO.
4. Hand Boot a dependency matrix for PHYs, repeater, redriver, I2C buses, supplies and Type-C ownership. Translate vendor labels to upstream labels. Coordinate GPIO91 ownership with DisplayPort and GLINK behavior with Power.

Acceptance: schema results, repeater compatibility matrix, PS5169 patch disposition and board proposal. USB enumeration, speed, role swaps, both orientations and electrical behavior remain physical tests.

## VPU Sol — priority 2

1. Turn the reported HFI comparison into a reproducible script with pinned input SHAs and output. The handoff reports 97 shared numeric definitions with zero mismatches; the coordinator has not independently reproduced that count. Cover packet structures, sizes/alignment and semantic differences, not only numeric IDs.
2. Lead a shared public-stock-firmware inventory with GPU and Boot. Record exact package URL/version/hash, extraction commands, firmware filenames/hashes and relevant DTB/DTBO selection evidence. A selected public image is a reference, not evidence of what is installed on the unavailable phone. Commit no proprietary blobs.
3. Complete the vendor-to-upstream resource matrix: MMIO, IRQ, clocks, resets, interconnect votes, power domains, PAS ID, memory/DMA constraints, VPU generation and pipe count. Keep Motorola evidence distinct from Xiaomi comparator evidence.
4. Produce a minimal Iris platform/binding patch only for fields justified by this audit. Compile it; use synthetic packet tests where useful, labelled as host-side tests. Do not claim firmware compatibility or decoding from those tests.

Acceptance: reproducible audit, firmware manifest or exact missing-download blocker, completed resource matrix and justified candidate patch if supportable. Firmware boot, HFI negotiation, real decode and performance remain hardware-blocked.

## Power Sol — priority 2

1. Deliver a source-backed regulator proposal to Boot with parent supplies, voltage constraints, consumer mapping, enable dependencies and board-revision caveats. Separate observed vendor settings from inferred upstream mapping. Disabled candidate nodes may be reviewed and schema-tested before electrical validation.
2. Compare Motorola charging/GLINK service and message formats with upstream support. Produce an opcode/payload compatibility table and identify actual driver gaps. Use fixtures for parsers or unit conversion where meaningful.
3. Keep BQ27426 evidence separate from unsupported charger assumptions; do not alias SGM41516D to SGM41542 without compatibility evidence. Document the dual-battery reporting and thermal-source mapping from code.

Acceptance: rail/consumer matrix, Boot proposal and charging/thermal protocol gap report. Actual rail voltages, charging control, battery reporting accuracy, thermal response and suspend power require hardware.

## DisplayPort Sol — priority 2

1. Trace vendor AUX routing code and DT to derive any supported GPIO2/GPIO71 truth table. Mark electrical polarity and the actual mux identity unresolved where sources cannot prove them. PS5169 is the redriver, not evidence for an integrated AUX switch.
2. Agree with USB on connector, orientation, HPD, redriver and independent AUX-mux ownership. Give Boot an exact graph/dependency proposal with pinned sources; keep unresolved nodes disabled.
3. Review the appropriate existing GPIO-SBU/AUX implementation and binding requirements. Do not invent a part-compatible string or a new MSM DRM driver solely to bypass missing identification. Validate candidate graph structure/schema offline where supportable.

Acceptance: ownership/routing matrix, source-backed truth table or precisely bounded evidence gap, graph proposal and existing dock test procedure updated with deferred status. HPD, AUX/EDID exchange, link training and real monitor output in both orientations require the phone and accessories.

## Coordinator — integration and CI

Next CI milestone: allow exact candidate kernel SHAs, compile the affected modules, build oneli DTB and run changed-schema checks. Preserve SHA, resolved config, tool versions and logs per run. Current baseline CI is not a subsystem branch validator.

Integration order: Boot UART correction and DT checks; GPU ID and USB binding checks; reviewed shared rail/PHY/OPP additions; protocol-dependent VPU/charging and DP enablement only as evidence permits. Independent driver/binding patches can compile before board enablement. Create `razr/integration` from an explicitly recorded commit set, not moving branch names.

Generic QEMU ARM64 `virt` can exercise a generic kernel/initramfs, userspace services, packaging and test harnesses. It does not represent the SM8475 phone or validate Qualcomm GPU/VPU firmware, physical USB/DP or charging. Use the virtual machine's own DT; do not present booting `virt` as oneli boot validation. See [QEMU virt documentation](https://www.qemu.org/docs/master/system/arm/virt.html). No emulator test is claimed in this review.

## Hardware blocker boundary

| Evidence needed | Can proceed now | Requires actual hardware later |
| --- | --- | --- |
| Board identity and boot | Inspect source variants, public DTB/DTBO and boot headers | Installed firmware, populated revision, unlock/bootloader behavior, real boot and console |
| Firmware | Public package extraction, hashes, format/protocol inspection | Secure-world acceptance and actual subsystem startup |
| USB/DP wiring | Vendor code/BOM/schema audit and candidate driver compilation | Unresolved physical part/polarity confirmation, signaling and connector behavior |
| Power/thermal | Rail mappings, source constraints, protocol comparisons | Electrical validation, real charge/temperature/current and suspend behavior |
| Performance | Build tools and synthetic harnesses | GPU rendering, VPU decode, throughput, stability and thermals |

No physical runtime milestone is currently achievable. This does not block the next source, firmware, build or userspace-emulation milestones.

## Handoff provenance

Boot, Power and DP handoffs were reviewed from coordinator main `99809d7`. New handoff files were copied verbatim from these coordination-repository branch heads; their older status statements remain historical and are superseded by this review:

- GPU: `6ea001d9f18549a35605492ce4a5acd3a697a43b`, `docs/handoffs/gpu-2026-10-11.md`.
- USB: `81da32ca96cc20bed37a73b6dbab93c0f1cbbf64`, `docs/handoffs/usb_2026-10-11.md` and `docs/usb_oneli_investigation_2026-10-11.md`.
- VPU: `b88d47de8436f0e52c9f5e4603314ce8e4e762a3`, `docs/handoffs/2026-10-11-vpu-hfi-audit.md`.

Their branch versions of STATUS.md were not copied over main. This avoids overwriting newer subsystem evidence. These instructions are published for the separate chats; publication is not confirmation that another chat has read or acted on them.
