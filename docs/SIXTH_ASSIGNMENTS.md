# Next assignments — sixth coordinator review, 2026-10-12

Read [SIXTH_REVIEW.md](SIXTH_REVIEW.md). The combined build and matching-kernel Debian QEMU milestone is accepted at **Drzet/linux `2b5acf108ae37040ac1e652e029bb37f5609e886`**, now `razr/integration`. Preserve this tested commit. [Accepted manifest](../configs/accepted-integration-2026-10-12.json) pins artifacts and scope; upstream baseline remains unchanged.

## Execution order

1. **Boot starts:** publish a short, versioned native early-initramfs payload interface for Userspace, using the newly completed VPU evidence. Correct the stale pending-build handoff. This is an interface deliverable, not another full build.
2. **Userspace acknowledges that exact interface.** Boot's packaging work and Userspace's payload construction can then overlap on their own branches. Do not independently invent two incompatible native contracts.
3. **Boot consumes the produced diagnostic payload** and validates native image structure. Coordinator reviews the complete result and remaining phone-only tests.
4. **Optional separate VPU task:** one DMA ownership design decision, described below. It has no dependency edge into steps 1–3.

GPU, Power, USB and DisplayPort are paused for this milestone. No all-agent concurrent round, unchanged full builds, full ROM rescans or repeat generic audits. Record specific blocked inputs instead of generating more audit documents.

## Boot — native early-boot packaging and observable diagnostics

Work from accepted integration; keep new work on the owned Boot/candidate branch and preserve integration until reviewed.

- Consume VPU evidence at project `dadd330c3f09f715372da94091f04166f9f0c141`, especially `docs/vpu/evidence/focused-stock-properties.json`. Update the native packaging contract's stale unknown OS-version/signature fields with verified **reference** values and hashes. Packed OS version 402653593 is not itself a required native policy; explain selected values. Distinguish the boot-v4 signature section from partition AVB metadata; never carry an unchanged stock signature as authentication of modified payloads.
- Define the exact accepted Image/DTB inputs, diagnostic cpio compression/alignment/ownership, `/init` behavior, kernel command-line ownership, generic versus vendor ramdisk roles, bootconfig/table handling and remaining native-placement inputs. Derive syntax from pinned kernel/AOSP tools and source evidence. Explicitly distinguish unresolved values from intentional empty/zero fields. Keep unresolved native inputs fail-closed.
- Define how first-boot evidence could be collected: source-backed UART/console configuration and what physical connection is actually known. If a persistent-log fallback is proposed, establish its reserved-memory/readout prerequisites; do not invent a carveout or claim a usable console from a DTS label alone. No USB/gadget/DP dependence for the initial payload unless separately implemented and reviewed. State the exact physical observation needed if output routing cannot be established offline.
- Complete actual **PVT-index3 overlay application to both original base FDTs** if needed for the native-reference contract. Reuse the existing bounded member reader and exact hashes in one controlled job; keep original bytes ephemeral and publish derived effective properties/hashes. Do not reconstruct FDTs from filtered JSON. This narrow Boot-owned application is authorized; do not launch duplicate VPU/Boot downloads. Reference composition does not prove the phone's active selection, and vendor DT must not replace the mainline board DT.
- After Userspace supplies the payload, generate a **host-validation-only** native candidate using explicit inputs, or a precise machine-readable blocked result if a required input remains unresolved. Independently unpack with pinned tools and verify all payload hashes, section bounds, DT selection, compression and bootconfig/ramdisk composition. Preserve a separate reference signature/AVB disposition. Do not present a structurally valid candidate as approved for phone use.

Acceptance: one agreed interface, actual diagnostic-payload packaging/independent inspection where inputs permit, and a short list separating source-solvable gaps from phone-only tests. No flashing, UFS-rootfs enablement, broad peripheral activation or fresh kernel build unless a concrete necessary code/config change is selected.

## Userspace — minimal diagnostic initramfs, then hand to Boot

The combined Debian QEMU task is complete. Preserve run 38297826535 and the existing tested scripts; do not rebuild Debian or repeat its unchanged smoke test.

- Agree Boot's native payload interface before native packaging assumptions. Use the accepted kernel/release/config and a pinned ARM64 userspace tool source/package. Produce a small deterministic cpio with numeric ownership, required device/filesystem setup and a controlled `/init` that records kernel/cmdline/DT identity and probe failures, then remains available for diagnostics. Keep actions read-only with respect to persistent phone storage and charging controls. No guessed root partition or phone console.
- Derive any module requirements from this minimal profile, not all 1,702 modules and not a blanket Qualcomm firmware list. An intentionally empty module/firmware requirement set needs a config/scope justification. Keep phone-specific values out of the generic runtime harness.
- Test the actual new initramfs under the accepted kernel with **QEMU virt's DT and a separate QEMU command-line profile**, without mounting the Debian disk. Verify PID1 execution, diagnostic output and controlled termination. This is a new payload test; it does not validate native UART, oneli DT or Motorola bootloader acceptance.
- Publish cpio/compressed payload hashes, manifest, tool versions, test evidence and immutable artifact references for Boot. Hand off the exact payload, not only a design document. Preserve unknown phone settings explicitly for Boot's final input gate.

A small housekeeping fix when touching evidence collection: exclude SHA256SUMS itself from its own file enumeration and verify the resulting list after writing. This does not invalidate the independently ZIP-verified prior guest evidence.

## VPU — optional isolated DMA design, no further extraction

The focused fields, durable export and loader bounds are accepted. Do not repeat those jobs or re-audit firmware location.

Resolve **one question**: can upstream Iris preserve required bitstream/pixel address semantics with a single DMA domain, or is a distinct-device/domain design required? Trace actual allocation/map/unmap and HFI buffer ownership for each class through pinned downstream and current Iris paths. Compare IOVA constraints and security/stream routing; do not assume overlapping vendor ranges prove equivalence. Identify supported IOMMU APIs and lifetime/error cleanup from the pinned kernel before proposing code. Two iommus entries alone is not a two-domain solution.

Deliver a concise design with source references and falsifiable acceptance conditions. Implement an isolated disabled experimental patch only if the ownership model is justified; otherwise give the exact missing evidence and stop. No broad refactor, active board node or combined-kernel import. MXC/MMCX required-opps and LLCC policy remain distinct queued blockers, not permission to guess values. Hardware PAS/HFI/DMA tests remain deferred.

## GPU — pause

13×7 stock fields, the 12×3 HFI correspondence, loader bounds and combined replay are accepted. Do not re-extract, rebuild unchanged source or implement speculative CX/bandwidth changes. Resume on a separately selected A730-specific vote/transition design or hardware test request. The remaining six CX-floor ownership questions and dynamic bandwidth-index selection are not missing-export tasks.

## Power — pause

The PVT voltage/boot-on delta, write-path audit and combined signed-temperature build are accepted. No new BQ27426 read-only driver is selected for first boot. Keep BQ/charger/thermal/dual-pack controls disabled; retain known source ranges without donor-board electrical-parent guesses. Resume for a specific reporting profile or a concrete Boot dependency. Correct stale combined-build status when next editing the handoff; no new audit/CI required now.

## USB and DisplayPort — queued / held

USB's typed 27-triplet PS5169 profile and lifecycle-failure work from [the fifth assignments](FIFTH_ASSIGNMENTS.md) remains queued after native packaging; no new USB round is required now. DP stays held for attributable AUX-switch identity. Do not enable FSA4480, invent a compatible or use PS5169 as an AUX switch. These holds do not block an initramfs-only milestone.

## Coordinator

Integration promotion is complete at the exact tested commit. Maintain the immutable manifest and selected branch/tooling provenance. Review the Boot/Userspace native interface and produced artifacts before any subsequent integration move. Preserve successful current artifacts before their 30-day Actions retention expires; a release/archive workflow may copy existing verified artifacts without rebuilding them. Do not treat build/QEMU acceptance as native acceptance or start all paused agents merely to keep them occupied.
