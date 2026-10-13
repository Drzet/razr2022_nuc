# Next assignments — tenth coordinator review, 2026-10-13

Read [TENTH_REVIEW.md](TENTH_REVIEW.md). Prior queue: [NINTH_ASSIGNMENTS.md](NINTH_ASSIGNMENTS.md). Preserve accepted integration and diagnostic v2. Work without hardware access.

## VPU — implement the bounded disabled prototype

Start from project `2a1e3a23253f45ff0eaaf44f531bcc248379c954` and kernel `869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf`. Coordinator approves the proposed independently enumerated two-consumer topology for an experimental RFC. This is sufficient authorization to produce reviewable code; do not return another report asking for the same approval. New compatible/phandle names remain proposed ABI, not upstream acceptance or observed physical topology.

1. Commit separate binding and disabled fixture patches in Drzet/linux. Describe both role-specific consumer nodes, one SID/mask each, and the controller relationship. Keep secure contexts out. Use IOVA-only reservation nodes; keep PAS physical carveout distinct. Do not edit Boot's shared DTS; create a fixture using the actual pinned bus hierarchy/cell conventions and record the exact integration-source dependency.
2. Verify OF address translation and both address-window boundaries with the pinned implementation. Include reservation target matching, zero-size/invalid translation rejection and buffer-end bounds. Resolve the unusual provisional upper mask explicitly; consider a supported contiguous mask plus upper IOVA exclusion if justified by source. Do not claim an ordinary unit model proves runtime SMMU allocation. No custom IOMMU core or private DMA-cookie manipulation.
3. Implement the small consumer driver and controller supplier acquisition/lifetime checks: normal DMA configuration, bound suppliers, distinct domains/groups, role/duplicate validation, deferral, checked device links, balanced refs and failure/unbind ordering. Preserve existing supported-platform behavior. The partial SM8475 path must not expose a usable V4L2 decoder while allocations still use the old parent; gate it explicitly until the later routing patch.
4. Validate compilation and affected schemas, positive/negative DT fixtures, and meaningful lifecycle failures against production code where feasible. Record what host tests cannot exercise. Deliver exact commits, logs and the remaining allocation-routing interface; no phone execution claim.

Stop at this foundation. Full VB2/internal/HFI ownership routing, OPP/ICC changes and active board enablement require the next review. Actual firmware ACK is not a prerequisite for this disabled prototype. Do not repeat extraction or the completed allocator survey.

## USB — close conditional-schema coverage and update the completed build record

Use project `bb0087babcf29553eb00e0b8414da512264f5380` and kernel `8356706a0e58916bd6149da085db6072b8feeee8`.

1. Replace stale in-progress text with actual successful run 38323664587, job 115057293411 and artifact 11781795488. Preserve the exact tested source and distinguish CI-reported hashes from independently downloaded bytes. The existing artifact contains build records, not deployable binaries. No rebuild to update documentation.
2. Add a valid oneli-compatible schema fixture with active-high enable semantics and no generic tuning overrides. Add invalid fixtures proving rejection of the prohibited EQ/gain/LFPS overrides. Execute actual schema validation, assert expected diagnostics, and avoid false-green expected-failure handling. Exercise the production runtime override rejection if the current host harness does not cover it. Do not rerun unchanged full ARM64 compilation merely for fixtures.
3. Record results, then pause. Do not enable board nodes, invent register meanings or implement speculative PM cycling. No broad new profile audit. Reopen only for a concrete defect, attributable new register/identity/wiring evidence, or selected hardware work.

## Concurrency and other agents

VPU and USB can run concurrently now; neither waits for the other. USB should finish its small closure task and pause while VPU continues implementation.

Boot remains paused until VPU supplies a reviewed binding/fixture and requests shared-DTS integration, or new loader/device evidence becomes available. Userspace, GPU and Power remain paused. DisplayPort retains its AUX-identity hold. No all-agent round, repeated minimal build or new image packaging.

## Coordinator

Review the actual VPU patch and USB fixture results. Keep experimental candidates outside accepted integration. Separate source/build evidence from handset behavior. Do not treat missing hardware as a reason to block the authorized offline implementation.
