> Historical review. Current STATUS.md and NEXT_TASKS.md supersede all work instructions below.

# Third coordinator review and next assignments

2026-10-11, after the third subsystem round. Supersedes the queue in [SECOND_REVIEW.md](SECOND_REVIEW.md). The latest ADB attempt was unsuccessful; plan without hardware access. Earlier [stock Android observations](oneli_stock_android14_adb_hardware_capture_2026-10-11.md) remain valid within their scope. Target: XT2251-1 PVT, hwrev 0xC000, SKU dn, observed Android 14 U2SLS34.1-42-14-11. User plans to unlock when the phone is fully in their possession; this is a future device-test prerequisite, not an offline development blocker.

## Assessment and verified gates

This round delivered substantial compile, schema, source and firmware-container evidence. It has not demonstrated native boot or peripheral operation. Coordinator checked branch changes, completed Actions results and selected logs, including the actual archive SHA, normal Iris modpost and Boot's full-schema/FDT results. No stock firmware binaries were independently extracted during this review.

| Workstream | Reviewed head(s) | Result |
| --- | --- | --- |
| Boot | kernel `6eec6ddd7842622668c937a466a8db47d20517b1`; project `e569b55` | [Run 38175014232](https://github.com/Drzet/linux/actions/runs/38175014232) passes target oneli compilation and all-applicable schema validation with no direct schema diagnostics. FDT audit: 39 reservations, zero overlaps, 888 parsed references, 13 GPU OPPs. **35 active-to-disabled provider references remain warnings**, not proven harmless dependencies. |
| GPU | kernel `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`; project `5f0b60b` | [Full Image/modules run 38174090675](https://github.com/Drzet/razr2022_nuc/actions/runs/38174090675) **passed**, superseding pending handoff wording. [Committed Boot OPP run 38174125440](https://github.com/Drzet/razr2022_nuc/actions/runs/38174125440) passed. CX, bandwidth and firmware behavior remain unresolved. |
| VPU | kernel `7f1d729b6f458f1e76efe2894eb3c544bc9db856`; project `810be63` | [Run 38170604512](https://github.com/Drzet/razr2022_nuc/actions/runs/38170604512) passes complete ARM64 Image/modules with ordinary modpost and Iris binding checks. Signed firmware extraction and probe contract remain incomplete; shared UBWC addition is explicitly [INFERRED]. |
| USB | kernel `87d7277ced4c562e2379ee58aaed5c5fd7db4f32`; project `e898742` | [Run 38170306651](https://github.com/Drzet/linux/actions/runs/38170306651) passes temporary PS5169 **x86 object** compile and candidate binding checks. Driver is fetched/patched in CI, not yet a durable kernel patch series. USB2 and Type-C contracts exist. |
| Power | kernel `3b02b11bc5abdc5c453fa4af16b71bd8e44c2056`; project `0f7ab81` | [Source audit](https://github.com/Drzet/razr2022_nuc/actions/runs/38168888153), [ARM64 objects](https://github.com/Drzet/razr2022_nuc/actions/runs/38169526109) and [real UML KUnit 3/3](https://github.com/Drzet/razr2022_nuc/actions/runs/38169484188) passed. Production helper fixes signed temperature arithmetic; no charging/transport runtime test. |
| DisplayPort | kernel unchanged baseline; project `9ae0c3f` | [Run 38174309894](https://github.com/Drzet/razr2022_nuc/actions/runs/38174309894) passes 23 pinned source assertions, offline replay and corruption rejection. USB/Power graph agreement recorded. AUX part/binding remains unresolved. |
| Userspace | implementation `ce17ea82c55a453ef593a7d0cbcb4f78520b2e67`; handoff `f785ae4` | Ownership and SSH/network implementation added. [Previous run 38177212005](https://github.com/Drzet/razr2022_nuc/actions/runs/38177212005) failed because package systemd-networkd was unavailable; replacement runs 38177545171/38177548051 were cancelled. Latest [run 38177877133](https://github.com/Drzet/razr2022_nuc/actions/runs/38177877133) at documentation head `f785ae444e904fe030baa8d745102d25a1fe2cde` is **in progress at review**. No complete guest SSH pass accepted yet. |

## Shared stock evidence is now usable

VPU's [stock manifest](https://github.com/Drzet/razr2022_nuc/blob/810be63/docs/vpu/2026-10-11-public-stock-reference-manifest.md) and [boot/DTBO report](https://github.com/Drzet/razr2022_nuc/blob/810be63/docs/vpu/2026-10-11-public-stock-boot-dtbo.md) replace the old download blocker. [Acquisition run 38169190369](https://github.com/Drzet/razr2022_nuc/actions/runs/38169190369) downloaded 4,353,164,507 bytes, SHA-256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`. Boot and vendor_boot headers are v4; four DTBO candidates were parsed and hashed. Matching build label is not proof of identical installed bytes or selected overlay.

The archive was deleted at job completion, so it is **not a retained binary workspace**. One controlled reacquisition or bounded member fetch for deeper analysis is expected. VPU owns acquisition/extraction tooling, not every subsystem's interpretation. Publish machine-readable, source-hashed metadata for consumers. No proprietary binaries in Git or automatically published artifacts.

**Correction to overly strong handoff wording:** the signed VPU/ZAP files have not been located. Their residence in super/vendor is not established. Inspect the actual image/mount layout, including the already listed `radio.img`, rather than assuming all firmware is in super. Outer ZIP absence is not filesystem absence.

## VPU — first priority: actual firmware and resource evidence

1. Extend the controlled stock job to inspect filesystem/partition containers and locate `vpu20_4v*`, A730 ZAP, SQE and GMU files wherever they reside. Identify image format before extraction. Reconstruct Android sparse chunks using an appropriate format-aware tool; do not concatenate them as raw bytes. Pin extraction tools and preserve package/member/filesystem provenance, paths, sizes, hashes and QC version strings where present.
2. Publish a shared manifest even if a named file is absent: enumerate which filesystems were searched. Inspect split MDT/Bxx or MBN/ELF formats actually found, including load ranges and signature metadata where parsable. Do not infer secure acceptance or HFI compatibility from a filename, string or successful host audit.
3. Export derived DTB/DTBO and vendor_boot metadata requested by Boot/USB/Power/DP in the same workflow. Use shared issue #10 for requests; consumers must not duplicate uncontrolled multi-GB downloads.
4. Reconcile Iris DMA/IOMMU, clock/OPP, bandwidth and UBWC assumptions against the extracted reference. Ask GPU to review the shared SoC UBWC match. The successful build closes the compiler gate; repeating it unchanged is not the next research milestone.

Acceptance: actual firmware file manifest or a precisely scoped negative search; identified resource changes; a Boot-facing disabled VPU node contract only for justified fields. Runtime PAS/HFI/decode remain deferred. If the archive lacks needed identities, report that bounded result rather than inventing a profile.

## Boot — first priority: packaging and dependency closure

1. Interpret vendor_boot v4 fully: embedded DTB region, vendor ramdisk table/fragments, bootconfig, alignment and compression; inspect all four DTBO roots for numeric board-id/msm-id and variant differences. Table-level zero IDs do not mean embedded root identity properties are absent. PVT matching may establish a **reference candidate**, not the live bootloader's choice.
2. Reconstruct the reference DT composition offline if its inputs/selection rules are known. Export a per-variant resource/property comparison for consumers. If composition cannot be proven, keep standalone fragments and missing base/selection inputs explicit.
3. Prepare a no-flash boot-image packaging prototype from verified header fields, with an unpack/repack structural roundtrip. Define how a mainline kernel/initramfs/DT replaces the reference inputs; do not replay stock bootconfig or vendor ramdisk blindly. Publish a machine-readable packaging contract for Userspace; no native boot success claim.
4. Classify the 35 active-to-disabled provider warnings by exact consumer/provider: minimal CPU/console/interrupt/timer/memory dependencies, inherited unused consumers, deferred subsystem dependencies or checker limitations. Fix or disable justified unnecessary consumers; do not whitelist all warnings just because inherited. Retain regression checks for the intended minimal boot dependency set.
5. Stage the available USB2-first contract against the chosen binding and Power range contract, keeping unresolved repeater and powered consumers disabled. Re-run target schema/FDT checks for the new committed tree. VPU staging waits for its source-supported contract, not merely a compiling driver.

Acceptance: reference image-layout/variant report, structural packaging roundtrip, classified dependency warnings and exact source-only USB2 staging commit. These tasks do not need the phone.

## GPU — source fixes now, firmware consumption when available

1. Record the now-completed full module build pass in the handoff; no unchanged rebuild needed.
2. Independently confirm and fix the discarded return from `a6xx_gmu_pwrlevels_probe()` in the pinned GMU probe path if correct cleanup/error propagation is demonstrable. Coordinator source inspection confirms the return is presently discarded. Keep this a narrow patch separate from chip ID and unproven power-vote changes; validate error-path cleanup and compilation.
3. Turn CX floor and bandwidth-index findings into a concrete mapping/implementation proposal with evidence per field. Distinguish firmware-supplied behavior from host votes; do not directly copy vendor bus indexes into the upstream table. If sources cannot justify translation, explicitly hold that feature instead of creating guessed numeric votes.
4. Review VPU's shared SM8475 UBWC addition against GPU/display consumers. Consume the common firmware manifest to compare SQE/GMU versions and signed ZAP path; firmware authentication still awaits hardware.

Acceptance: bounded error-handling fix or reasoned rejection, UBWC review, and an actionable disposition of CX/bandwidth gaps. Keep board GPU disabled until its enablement contract is supportable.

## USB — make the tested candidate durable

1. Convert the verified runner-only PS5169 import/repairs into an attributable reviewable kernel series on the USB branch (or an owned USB candidate branch). Preserve original authorship, separate include repairs and VCC/VIO changes, and record original patch provenance/source hashes. The result must not depend on scripts silently rewriting source at build time.
2. Compile the resulting driver for ARM64 with complete dependency-resolved linking and validate its binding. Review supply sequencing, unwind and suspend/resume paths, plus the board's enable-versus-reset contract. Object-only x86 success is an intermediate gate already completed.
3. Compare NXP/Diodes statuses, repeater reset/tuning and PS5169 enable/supply/EQ data across the four actual stock DTBO candidates and any base DT from Boot. Produce a per-variant diff; both compatible strings being present does not identify the enabled device. Use reference PVT evidence where supportable.
4. Supply Boot exact binding commits and any corrected USB2 contract. Physical chip identity may remain unresolved after this bounded stock audit; do not alias a part from matching registers alone.

Acceptance: durable PS5169 candidate and ARM64 link pass, stock-derived variant matrix and updated Boot contract. Native USB enumeration is still deferred.

## Power — targeted driver work and stock comparison

1. Record completed KUnit/source gates; prepare the existing signed-temperature series for integration as a standalone fix, excluding inherited old Boot commits. Its tests exercise the production helper, not the GLINK transport.
2. Audit the exact Motorola SGM41516D implementation and combined-battery policy: register definitions, identity checks, conversions, charger ownership and aggregation. Separate generally reusable driver support from Motorola policy. Give a concrete patch plan or precise missing evidence; no blanket alias to SGM41542.
3. Compare stock PVT regulator/consumer properties from Boot's extraction with the source-derived rail contract, particularly unresolved parent supplies. Hardware observations support stock topology; they do not identify an unobserved parent wire or full firmware protocol.
4. Use the upcoming combined kernel build for dependency-complete battmgr validation rather than scheduling another unchanged large isolated kernel build. Retain UML tests as the meaningful arithmetic regression gate.

Acceptance: integration-ready temperature patch list, charger/policy gap matrix and any stock-backed rail corrections. Active charging and electrical validation remain held.

## DisplayPort — bounded final offline task, then wait

Your reproducible source audit and graph agreement are complete; do not repeat them unchanged.

Inspect Boot/VPU's four reference DTBO variants and available base DT for actual AUX switch identity, GPIO2/71 properties and enabled routing. Compare to the existing software truth table and generic mux NONE-state behavior. Produce one variant/evidence matrix and a binding disposition. If the actual part or a justified binding remains unknowable, **pause AUX/board enablement pending new evidence or hardware**. No speculative compatible and no endless generic source audits.

USB candidate review and graph documentation can proceed concurrently. DP enablement still waits on USB driver/connector, justified AUX binding and Boot-owned DT. This is now a legitimate scoped hold, not a reason to keep inventing tasks.

## Userspace — finish one real pass, then connect native artifacts

1. Let the latest corrected job finish, inspect all steps and publish its final outcome. Repair actual failures until guest systemd, networking, authenticated SSH, clean shutdown and tar ownership roundtrip all pass. Do not mark code changes as validation or leave a failed gate labelled pending.
2. Avoid repeated push/PR runs cancelling useful work. Batch fixes and scope triggers; one completed exact-SHA run is the gate. Confirm the latest service package choice from the pinned Debian rootfs contents.
3. Strengthen the native artifact validator: currently a matching directory name, modules.dep and any .ko file do not establish module ABI compatibility. Check actual module vermagic against kernel release, manifest hashes, initramfs module contents and required firmware records. Add negative fixtures for a deliberately mismatched module and tampered artifact. Unknown firmware requirements must remain unresolved, not pass as an empty JSON object.
4. After the generic Debian-kernel gate passes, consume a coordinator-selected mainline Image plus matching modules in a **separate QEMU virt** test using the virtual machine's DT. This tests the project kernel/userspace interface; it must not use the oneli DT or be called phone emulation. Native phone packaging consumes Boot's contract independently.

Acceptance: a completed boot/network/SSH result, meaningful module/artifact consistency checks, then a pinned project-kernel QEMU run when supplied. Desktop/Docker expansion waits until the base gate passes.

## Concurrency and integration milestone

| Agent | Work now | Wait only for |
| --- | --- | --- |
| VPU | Container/firmware extraction and resource reconciliation | Actual phone for authentication/decode |
| Boot | Packaging parser, dependency classification, disabled USB2 staging | Shared extracted members/metadata for specific reference comparisons |
| GPU | Error propagation, vote analysis, UBWC review | Common firmware manifest for binary comparison |
| USB | Durable PS5169 series and ARM64 linking | Stock variant metadata for board-specific corrections |
| Power | Charger/policy audit and fix preparation | Stock rail properties for remaining mappings |
| DP | One stock AUX variant audit when metadata arrives; USB candidate review | New AUX identity/binding evidence after that; then native hardware |
| Userspace | Complete QEMU/SSH gate and artifact validator | Selected kernel artifacts only for mainline-kernel smoke test |

Coordinator's next integration target: an explicit candidate commit set from Boot, GPU chip-ID, USB PHY binding and the standalone Power fix, retaining unready hardware consumers disabled. Include VPU and PS5169 only as separately reviewed experimental candidates with their assumptions recorded. No integration has occurred in this review. Coordinator owns integration and aggregate status; Boot owns shared DT. Record resulting SHAs and run a combined Image/modules/oneli DT/schema build before using artifacts in Userspace. Do not confuse independent branch passes with this combined gate.

Firmware acquisition should be centralized, while interpretation is distributed. Exact immutable project/kernel revisions, generated configuration, logs and final run conclusions belong in every handoff. Successful past checks should not be rerun merely to keep an agent occupied. No firmware/bootloader runtime gate is satisfied by these offline tests.
