# VPU upstream adaptation review — 2026-10-13

**Disposition: reuse direction and recorded build/schema/routing results accepted; candidate needs bounded provenance and validation closure before integration review.** No accepted kernel or board change. Do not resume the abandoned peer driver or expand to OPP/ICC.

Reviewed project `a01da16` canonical handoff; kernel `ec9a8949cfbd1b05cf01553bffc39719ee1a16a7`, relative to `869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf`. Coordinator inspected the complete source delta, test bodies, commit metadata and actual job logs. [Canonical handoff](https://github.com/Drzet/razr2022_nuc/blob/a01da16/docs/handoffs/2026-10-13-vpu-tenth-recovery.md).

## Verified progress

- Existing Qualcomm v5 common subnodes, IOMMU range support, context creation and VB2/internal/HFI routing are reused. No bespoke peer consumer driver appears in this branch. Local SM8475 changes add a nonsecure contract, conservative pixel floor, contiguous 32-bit DMA mask and an early `-EOPNOTSUPP` gate. That gate prevents handset probing, including runtime child creation; this is a disabled candidate, not functioning decode.
- Full ARM64 Image/modules/modpost, including linked qcom-iris.ko, passed at `fa89904487d4a465eb6df3f14db123d553be9502`: [run 38431204894](https://github.com/Drzet/linux/actions/runs/38431204894), job 115413530352. Overall run failed because its separate schema job failed. This distinction is accurately reported.
- Final schema/host [run 38431847444](https://github.com/Drzet/linux/actions/runs/38431847444), job 115415753529, passed at ec9a8949: enabled positive fixture, eight expected-invalid schema fixtures, 53 executable production routing-selector checks. Subsequent changes from the successful full-build source affect only workflow and fixture; no new full build is required for identical driver inputs.
- HFI/internal alloc/free and child-lifecycle checks are textual assertions, not execution. Range negatives compare fixture values to a Python constant table, not `of_iommu_derive_resv_regions`. These are useful limited checks but do not close the stated allocator/failure-path validation.

## Required closure

1. **Provenance:** five commits labelled upstream-authored (`7d7038b2`, `b8d974e5`, `6619b5ec`, `3e4c8aae`, `48606cc3`) have Git author Drzet and abbreviated replacement messages. Original-author/Message-ID links provide attribution, but original authorship and upstream trailers are not preserved as the handoff claims. The reviewed upstream context patch includes co-development, sign-off and review trailers absent here. Supply the requested source mbox/hash and a per-patch original/backport identity and conflict/delta record. Reconstruct an attributed submission series on a **new** branch without rewriting tested ec9a8949 history. Retain upstream trailers only on their legitimate source patches; never invent a personal sign-off or transfer upstream review approval to local modifications.
2. **Production range enforcement:** test the actual added IOMMU range helper (kernel test or extracted production function with explicit mocks), not a rewritten algorithm. Check the two normal window complements, malformed/zero/overflow inputs, translation and allocation-failure behavior. Pinned source currently can return no reservations if no valid ranges survive; this is not rejection of malformed input. Record inherited upstream limitations accurately and assess the intended validated-DT path; no blanket core rewrite is authorized.
3. **Child lifecycle:** exercise actual create/init/deinit control flow for absent legacy children, first/second registration failure, partial cleanup and subsequent V4L2-registration failure. Source presence/count assertions do not show error propagation or balanced node/device references. Keep provider/kernel runtime limits explicit.

If a real failure requires source changes, keep them separate from the imported patches and check current upstream fixes first. Tests must resolve the named risks; do not build a general framework or repeat a broad audit. If provenance reconstruction leaves the source tree identical, record tree equality and reuse the earlier build evidence.

## Correction to earlier coordinator reasoning

An unbound platform child is **not necessarily missing DMA configuration** in this baseline. `drivers/iommu/iommu.c::iommu_bus_notifier` handles BUS_NOTIFY_ADD_DEVICE; `iommu_init_device` invokes the bus dma_configure for an unbound device lacking fwspec, and the IOMMU probe path sets up its domain. Coordinator traced this pinned path and compared the [upstream context patch](https://lists.openwall.net/linux-kernel/2026/09/26/350). A separate driver must not be added merely to satisfy the earlier incorrect blanket statement. Actual setup failure/deferral remains a distinct behavior to assess; no handset domain success is claimed.

The [upstream range patch](https://lists.openwall.net/linux-kernel/2026/09/26/362) remains pending source to backport, not proof of faultless operation. Synthetic fixture resource placeholders are test-only and must never become board values.

## Sequencing

VPU alone closes these three concrete gaps in one handoff update. Boot/shared DTS, USB NXP work and all other streams remain queued/paused. Do not advance to resource policy or active board integration yet. Accepted integration remains `2b5acf108ae37040ac1e652e029bb37f5609e886` and diagnostic v2 is unchanged. Device PAS/HFI/DMA/decode remain deferred hardware outcomes, not prerequisites for the offline closure.
