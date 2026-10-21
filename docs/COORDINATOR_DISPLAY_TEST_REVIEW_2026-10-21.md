# Coordinator display test review — 2026-10-21

## Decision

Accept kernel **0739fea79154fd43658c86533e2f254ebb8a52f2** (test implementation parent **045d80c65e077f131c640b7f8ca6a3d6168a4585**) and project handoff **cd98f2a8f61a3d2b465548f4c552f9ac159326db** for the precise host-fixture and object-build scope below. No blocking production regression identified in this delta. Pause GPU/display. No display activation, native DSI selection or integration into the reduced radio build.

## Source and execution review

Inspected both kernel commit diffs, the full production-test translation unit and host shim. The actual earlycon source is included; production parser, renderer and remap routines execute. The production source delta only selects host headers under SIMPLEFB_EARLYCON_HOST_TEST; normal kernel functionality is unchanged.

Real flattened DT blobs exercise scanner traversal/property checks, including absent/disabled/duplicate nodes, malformed fields, cell layouts and rejected geometry. Rendering exercises glyph pixels, padded stride, line/screen wraps, unsupported-character fallback, small geometry and early-map failures. Mapping-state cases cover registration, permanent-map success, failure disabling later output, retained mapping and unregister cleanup.

Independently inspected [run 39262243264](https://github.com/Drzet/linux/actions/runs/39262243264), job **118092625502** logs: prior predicate checks PASS, production-path test **1082 checks PASS**, ARM64 earlycon object compilation completes. Guard-byte assertions account for many checks; this is not 1082 independent scenarios. No coordinator rebuild or repeat host run.

Downloaded artifact **12191942615** and independently hashed ZIP **200e47ba77cfdb4fb44f25bd0790f087737a363d97f1c27698618f2bf9887cab**. Archive now contains the non-hidden resolved configuration, object file-type result and object hash record. Config SHA256 **3a99e100c66063db438d2a10c1f7874cee37c5294cd580ba15743d47f3bd6da2** independently verified; opted-in SERIAL_EARLYCON_SIMPLEFB and ARCH_USE_MEMREMAP_PROT present. CI checks default-off before opting in. The actual object is not archived: **d3ef7bc60cbfb860b79c623172d862821bbe0ab8914c49b4a85dcbb339e385bc** remains a CI-produced object hash, not independently rehashed binary evidence.

Workflow-scoped cancellation and resolved-config archival corrections are complete. Initial host compilation failed on five pre-existing sign-compare diagnostics; the follow-up suppresses that warning in this host translation unit only. This is disclosed warning-policy alignment, not a production correctness fix. Targeted compilation only; no full kernel build.

## Coverage limits

The suite uses Ubuntu libfdt 1.7.0 rather than the pinned kernel library. Thin OF lookup wrappers use real libfdt, but of_flat_dt_translate_address is a limited identity/single-range mock. Therefore successful translation fixtures do not prove the real kernel translation implementation. Physical mappings, console registration and font selection are mocked. Guards surround the host allocation, not each declared framebuffer extent; production bounds checks and selected pixel assertions remain additional protection, not exhaustive memory-safety proof.

The assignment's parser/rendering gap is materially addressed at this declared host scope. Full OF translation, real early boot lifetime/WC semantics, later unregister mapping retention, actual RAM ownership and live scanout remain outside acceptance. No new broad test round is selected for these hardware-dependent outcomes.

## Project disposition

Reduced kernel and Debian rootfs retain accepted QEMU compatibility. Neither internal panel has native DSI support selected or enabled. The earlycon remains an isolated default-disabled option; no invented framebuffer node/geometry or unconditional splash writes.

The useful next display step is missing on-device framebuffer/panel/handoff evidence. UART7 remains the first evidenced diagnostic route conditional on physical access and voltage confirmation. Main versus cover is not selected. All agents pause; queued evidence prerequisites and exact restrictions are in [NEXT_TASKS](NEXT_TASKS.md).
