# Next assignments — fourth coordinator review, 2026-10-12

Read [FOURTH_REVIEW.md](FOURTH_REVIEW.md) for reviewed SHAs, independently checked CI and source findings. These assignments replace [THIRD_REVIEW.md](THIRD_REVIEW.md). Work without phone access. Baseline unchanged; Boot owns shared DT, coordinator owns integration and aggregate status. Do not repeat successful builds or generic audits without a changed input or concrete remaining question.

## Priority and ownership

Two concurrent priorities: **one shared stock DT property export** and **one combined kernel/artifact build**. Firmware location is resolved; active DT selection is not. Keep unresolved hardware consumers disabled. All hardware assumptions remain `[INFERRED]`.

### VPU — complete the shared evidence handoff, then resource closure

1. Own a single bounded export for all requests in issue #10. First reuse any retained parsed output. If required fields/bytes were not retained, use the existing verified ZIP-range machinery for only `dtbo.img`, `vendor_boot.img` and, if needed for header/compression validation, `boot.img`. This explicitly permits bounded member retrieval; do not repeat the 4.35 GB archive/super/radio scan. Verify known member hashes and publish derived metadata only.
2. Export all four overlays and every valid vendor_boot base FDT: numeric root IDs, paths, raw values, status/ancestor status, supplies, GPIOs, clocks, resets, IOMMUs, interconnects, reserved-memory, USB repeaters, PS5169 and AUX/DP. Include fixups/symbols and source hashes/offsets. Distinguish absent, unparsed and unresolved. Give Boot all needed parsed structure, not another manifest containing only hashes/root strings. Redact device-specific identifiers if any occur; record omissions.
3. Include header address fields, ramdisk compression and fragment descriptors. Boot handles candidate composition and packaging. Do not claim the live overlay selected solely from PVT identity.
4. After export, reconcile Iris IOMMU stream IDs/aperture, four-domain OPPs and ICC/bandwidth against actual stock properties plus pinned driver sources. Publish a field-by-field supported/unresolved delta. Consume GPU's completed UBWC review. Determine Linux loader/request path and split-file requirements from actual code; basename discovery is already complete.

Acceptance: machine-readable per-FDT values sufficient for the four waiting consumers; explicit Iris resource/loader disposition. No runnable node with guessed resources. If a resource cannot be justified, hold that field and state the exact evidence needed.

### Boot — resolve GCC and make packaging inputs explicit

1. Trace the seven GCC PHY-clock parents through the pinned clock framework/provider registration and probe paths. Determine whether each creates an orphan clock, deferred probe or usable path for the minimal console kernel. Document exact source paths; QEMU cannot validate Qualcomm GCC. Patch only demonstrated problems; retain explicit uncertainty otherwise.
2. Consume the shared FDT export, compare all variant IDs/properties and compose candidate base+overlay pairs only where symbols/fixups and matching rules support it. Publish per-candidate results; physical bootloader selection may remain unknown. Coordinate USB/Power/DP interpretations in one shared report.
3. Correct packaging prototype: reference loading addresses and OS-version fields are currently copied implicitly. Make inherited fields explicit, provenance-backed manifest inputs or an explicitly rejected unresolved state. Separate structural-format validation, native composition readiness and hardware acceptance. Do not set a generic `verified` flag to appease Userspace.
4. Agree a versioned machine-readable contract with Userspace. Validate generated candidate layout using an independent AOSP parser/packer at a pinned revision, including payload identity and changed-size/alignment cases; an identity copy plus own parser is insufficient independent evidence. Use bounded real-member data when available, without requiring a full ROM download. No flashing task.
5. Correct schema CI provenance: run 38182280401 checked out `2b473619...`, not `525b504...`; the latter only changes the FDT workflow pin and has its own passing FDT run. Keep disabled USB2/GLINK staging. The USB PHY binding is already present on Boot; do not apply it twice.

Acceptance: seven-clock disposition, usable per-variant comparison, explicit packaging inputs and compatible Userspace schema. These do not block starting a disabled-peripheral combined compile.

### GPU — consume completed firmware evidence; keep vote work bounded

1. Update handoff: full Image/modules run 38178986611 passed at kernel `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`. GMU fix is a candidate for combined integration; no unchanged isolated rebuild.
2. Replace stale “ZAP unlocated” report with VPU's actual SQE/GMU/ZAP records. Compare with pinned linux-firmware revisions using exact hashes/formats and source request names. Determine whether proposed filename installation is sufficient or format differs; a rename is not evidence of compatibility. Reuse existing extraction evidence and coordinate any genuinely required bytes with VPU.
3. Use shared DT/driver evidence to resolve the specific CX-floor and bandwidth-index gaps. Give a patch only where translation is justified; otherwise leave a concrete hold. No repeated general GPU audit. Shared UBWC source review is complete; retain its `[INFERRED]` physical-profile limit.

Acceptance: exact firmware install/compatibility matrix and vote-gap disposition. GPU stays disabled; device firmware authentication/rendering await hardware.

### USB — fix durable PS5169 failure semantics

1. On the owned `razr/usb-ps5169` candidate, propagate register/EQ write failures through initialization and mode callbacks. Ensure failed transitions can be retried; do not update cached mode/orientation/SVID as successfully applied before writes succeed. Inspect unchanged-mode/new-SVID handling and downstream mux/switch failure ordering.
2. Add meaningful injected-I/O-failure coverage for probe and transitions, validating returned errors, cached state/retry and supply cleanup. Compile changed driver with dependency-complete linking. Preserve original authorship and separate changes.
3. Correct endian-safe interpretation of `__le16` chip ID/revision. Resolve reset-versus-enable API only from source/binding/electrical evidence, not pulse guesses; document suspend/resume ownership and required reinitialization. An explicit hold is acceptable where evidence stops.
4. Consume the shared stock property export once: enabled NXP/Diodes variants, exact supplies/reset/tuning, PS5169 pinctrl/EQ. Send Boot only supported contract corrections. Physical repeater identity cannot be inferred from compatible-string presence alone.

Acceptance: reviewable error-handling series with failure tests; bounded reset/PM and variant disposition. Existing full build is accepted; PS5169 remains an experimental disabled-board candidate.

### Power — integration review and minimal read-only scope

1. Review standalone series `564f2c7df60316db86e36d7267ddadf07bc32b7e` in combined build; retain original UML arithmetic tests. Fix CI trigger scope so cumulative PR diffs do not rebuild unchanged kernel objects on each documentation commit.
2. Consume stock rail/consumer properties and update only evidence-backed parent mappings. Review Boot's current `525b504...` staging, replacing stale `6eec...` reference. Prioritize dependencies required by minimal boot and USB2.
3. Define a minimal read-only battery/thermal reporting plan: exact supported protocols, ownership, missing driver behavior, and which paths must remain disabled to avoid charger/load-switch writes. Identify the exact oneli driver source or authoritative variant data before proposing SGM41516D support; the SM8250-family comparator is not that proof.
4. Keep dual-battery charge control and active policy on hold until variant and fail-safe ownership are established. Do not start a wholesale Motorola charging-manager port to keep the agent occupied.

Acceptance: combined temperature-fix review, stock rail delta, bounded read-only reporting contract with explicit stops.

### DisplayPort — wait for actual properties, then one disposition

Existing generic source/graph audit is complete. **Wait for the shared FDT export for the stock variant task.** USB driver failure-path/graph review may proceed concurrently if useful. Once actual AUX properties arrive, update the matrix once; determine whether evidence supports an existing binding, a defensible new binding, or no identification. If unresolved, remain on hold pending attributable part information/hardware. Do not invent compatible strings, bind PS5169 as the independent AUX mux, or patch DRM to bypass missing routing.

### Userspace — project-kernel interface next

1. Record fresh full-build success 38180519542 at `e14f618fc1c55b3581e3bf082c1d12bbb0b05e03`, not only the replay. Retain ownership/SSH/clean-shutdown evidence. Current test establishes configured IPv4 and host SSH; do not call it external-network validation.
2. Align artifact schema with Boot. Separate file consistency, structural packaging, native readiness and hardware validation. Represent an explicitly justified empty firmware/module requirement set for a selected QEMU or minimal configuration without allowing unknown requirements to pass. Do not require oneli packaging or Qualcomm firmware for QEMU virt.
3. Prepare a consumer for coordinator's exact combined Image, generated config, release, Module.symvers and matching installed modules. Build a new matching initramfs; preserve same-build provenance and module hashes. Use QEMU virt's DT, never the oneli DT, and perform a real module load plus systemd/network/SSH/shutdown checks. A module deliberately built for a mismatched release must fail the gate.
4. Design a separate native early-initramfs diagnostic artifact using Boot's eventual native contract. No guessed console, storage device, root partition or firmware requirement. This preparation can proceed before combined artifacts exist; execution of project-kernel smoke waits for them.

Acceptance: schema agreement and ready project-kernel test consumer; then one exact combined-artifact QEMU pass when supplied. Desktop/Docker expansion remains lower priority than this interface.

## Coordinator integration work package

Select a minimal candidate from Boot `525b504b82dbca593a9a697af9be63f53915e0a3`, GPU chip-ID `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`, GMU fix `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`, and the isolated Power series ending `564f2c7df60316db86e36d7267ddadf07bc32b7e`. Review/replay exact source commits and record new SHAs. Boot already contains the USB PHY binding. Exclude branch-mutating import workflows and unrelated inherited history.

The single UBWC commit `7f1d729b6f458f1e76efe2894eb3c544bc9db856` may be included as a separately labelled provisional SoC prerequisite after its source review; do not merge its Iris ancestors. Keep Iris RFC and PS5169 experimental series separate from the first minimal candidate; add them only through explicit later candidate selection, with USB fixes reviewed. No active GPU/VPU/USB/DP/charging consumer enablement is implied.

Produce one combined ARM64 Image/modules and oneli DT/schema/FDT pass with ordinary modpost. Export actual Image, installed modules, Module.symvers, generated config, kernel release, DTB, tool versions, hashes and ordered commit manifest. Ensure the selected configuration supports QEMU virt without substituting the oneli DT. Share immutable artifact IDs/digests with Userspace. Integrate selected project tooling/evidence into coordinator main through reviewed file sets; do not merge stale aggregate STATUS/NEXT_TASKS from subsystem branches.

This review defines the package; **no combined branch/build has been created or accepted by this review**. The combined compile does not wait for stock DT export or hardware; later board enablement does.

## Concurrency and stop conditions

| Owner | Work immediately | Wait only for |
| --- | --- | --- |
| VPU | Bounded shared FDT export, then resource/loader reconciliation | Physical PAS/HFI/decode |
| Boot | GCC trace, explicit packaging/schema work | Shared properties for variant composition |
| GPU | Firmware manifest comparison, targeted power-vote work | Stock fields or hardware for specifically unresolved claims |
| USB | PS5169 error/retry/cleanup fixes | Shared properties for board corrections |
| Power | CI scoping, standalone review, read-only plan | Shared rails and exact variant evidence for driver enablement |
| DP | Optional USB review; otherwise scoped hold | Actual AUX properties, then part evidence/hardware if still unknown |
| Userspace | Schema alignment and project-kernel consumer | Combined artifacts for the new kernel smoke run |
| Coordinator | Selected integration/build/artifact publication | Only concrete source-review/build failures; no phone needed |

Runtime phone gates remain native boot/diagnostics, firmware authentication, DMA/HFI, rendering/decode, USB/DP and electrical/thermal/charging behavior. Neither QEMU nor successful source/schema checks closes them.
