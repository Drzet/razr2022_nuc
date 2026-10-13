> Historical review. Current STATUS.md and NEXT_TASKS.md supersede all work instructions below.

# Tenth coordinator review — 2026-10-13

**VPU's allocator feasibility finding is accepted; proceed to a disabled experimental binding/consumer prototype. USB's new profile and lifecycle candidate passed host tests and full ARM64 build; it remains outside accepted integration.**

## Reviewed revisions

| Submission | Exact revision |
| --- | --- |
| VPU project | `2a1e3a23253f45ff0eaaf44f531bcc248379c954` |
| VPU kernel, unchanged | `869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf` |
| USB project | `bb0087babcf29553eb00e0b8414da512264f5380` |
| USB experimental kernel | `8356706a0e58916bd6149da085db6072b8feeee8` |

[VPU report](https://github.com/Drzet/razr2022_nuc/blob/2a1e3a23253f45ff0eaaf44f531bcc248379c954/docs/vpu/2026-10-13-iova-window-enforcement-child-topology.md) and [USB handoff](https://github.com/Drzet/razr2022_nuc/blob/bb0087babcf29553eb00e0b8414da512264f5380/docs/handoffs/2026-10-13-usb-fifth-round.md) are the reviewed source records. USB execution was explicitly reactivated by the owner; its work is independent of VPU.

## VPU: concrete allocator mechanism found

Coordinator independently inspected pinned `of_iommu_get_resv_regions`, `of_translate_dma_region`, `platform_dma_configure`, the DMA allocator and the downstream `qcom-iommu-util.c` helper. The findings support the report:

- Vendor `virtual-addr-pool` parsing/logging is distinct from the `qcom,iommu-dma-addr-pool` property used by the comparator's reservation helper. Neither establishes the installed Motorola kernel's actual behavior.
- Upstream consumer `memory-region` plus matching `iommu-addresses` can create IOVA-only reservations without a physical `reg` carveout. The normal DMA allocator reserves those regions. A custom Qualcomm IOMMU-core implementation is not needed for this proposed lower-bound policy.
- Platform bus DMA configuration/default-domain setup occurs as part of binding. An unbound placeholder device is insufficient.
- Translation consumes address/size cells from the actual DMA parent. Copying the illustrative two-address/two-size-cell excerpt without checking the composed hierarchy is insufficient.

Retaining the stock low floors is **[INFERRED] conservative software policy**, not a proven silicon requirement. Two independent peer consumer devices are approved as an **experimental RFC topology**, not as an established upstream hardware ABI or proof that nesting is impossible. The report's phrase physically peer devices must not be interpreted as observed physical topology.

The remaining questions are now executable: schema representation, real OF translation, complete lower/upper window enforcement, consumer binding and reference/unbind lifecycle. The unusual numeric mask `0xdfffffff` is not automatically accepted as a portable DMA-mask contract. Resolve it with supported DMA/reservation semantics. No more general DMA survey is assigned.

## USB: implemented and build-tested

Coordinator inspected the new driver/binding diff, workflow, both actual job logs and artifact metadata for [run 38323664587](https://github.com/Drzet/linux/actions/runs/38323664587), exact source `8356706a0e58916bd6149da085db6072b8feeee8`.

- Host job **115057293653 passed**: extracted production function tests cover the ordered 27-entry profile, 30 partial-write failure/cleanup/reprobe positions, acquisition/registration errors, and existing mode/EQ/rollback paths. These execute with provider shims; kernel devres, real buses and electrical effects are not tested.
- ARM64/binding job **115057293411 passed**, completed **2026-10-13 00:27:35 UTC**. Full `Image modules` with normal modpost completed; the log identifies the linked PS5169 module as AArch64 ELF. The handoff's in-progress build statement is stale.
- Build-record artifact **11781795488**, reported ZIP SHA256 `996acbe635a6c33240ccc04f83e4f727af56a320fec94cce02f570427dcabb65`; host artifact **11779857817**, reported ZIP SHA256 `af465de6bc88d720d23b2f23fa531a26a78098a4f0aec4e390cd00e2cf9820c2`.
- Build log reports Image SHA256 `c437c7e71743e21cbfa1d00c6ec24468f9ffee4fc4bf1c7757c393c11e0759ea`, Module.symvers `ad4f64708b64e132fea71feb4602c437831a2ba1c4f267708f2f8cfcf63725d9`, PS5169 module `4d141eb37d3a1fc090aafacf182fc99c9ec77d6da45a4c84dbad9edc8fd473e2`. These are CI-produced hashes, not independently downloaded binary hashes. The workflow archives build records/configuration, not the Image/module binaries; this is build evidence, not a deployable artifact bundle.

The code applies the typed profile and initial SAFE-mode writes before switch/retimer publication, checks write errors, and excludes conflicting generic tuning properties. Successful writes are not hardware readback verification. Unknown OEM register semantics remain explicitly unknown. No active suspend/resume cycling is added; absence of PM callbacks does not guarantee physical rail retention.

One narrow validation gap remains: the schema's provided example uses only generic `parade,ps5169`, so the passing binding job does not itself demonstrate acceptance of the new board-compatible instance or rejection of its forbidden overrides. Exercise that conditional branch directly before closing the USB source assignment. No repeat full build is required for fixtures/documentation alone.

## Dependencies and hardware blockers

VPU prototype work and USB's small validation/record update can run concurrently: separate files, no shared artifact dependency. Boot joins only after a reviewable VPU fixture/binding exists and a shared-DTS change is requested. Userspace/GPU/Power/DP need no new round.

Device-only results still outstanding: native loader handoff/output, VPU domain behavior/PAS/HFI/decode, and USB chip communication/orientation/link/wake behavior. USB NXP repeater identity, AUX identity and electrical parents remain evidence gaps; attributable documentation could resolve identities/wiring without hardware, otherwise physical inspection is needed. They do not block VPU's offline prototype or USB schema fixtures.

Accepted integration remains `2b5acf108ae37040ac1e652e029bb37f5609e886`; diagnostic v2 is unchanged. No experimental USB/VPU merge or native acceptance is made. See [NEXT_TASKS.md](NEXT_TASKS.md).

## Reuse-policy addendum — 2026-10-13

The owner requested an explicit mainline/pending-patch/out-of-tree/vendor search before new driver development. Earlier review verified reuse of upstream Iris/DMA APIs and pinned vendor comparators, but did not establish complete current-community coverage for the proposed VPU consumer driver and binding. Prototype authorization is therefore subject to the reuse prerequisite in NEXT_TASKS. Existing PS5169 work preserves the external driver series; its current fixture task does not introduce a new driver. The rule applies project-wide to future new implementation, without restarting completed unrelated work.
