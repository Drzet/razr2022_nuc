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

## VPU closure review and branch repair — 2026-10-14

The latest agent work did not corrupt the tested kernel branch: `razr/vpu-upstream` still points to ec9a8949 and accepted integration remains 2b5acf10. Three additional branches had distinct purposes but the handoff duplicated its closure report and still called the old implementation active. Coordinator corrected that ambiguity without resetting history.

- **Provenance accepted:** all thirteen reconstructed commit trees at f8d742ff match their corresponding historical trees locally; original author and trailers are restored on the five imports. CI [38486727933](https://github.com/Drzet/linux/actions/runs/38486727933), job 115602051003, records five matching upstream patch IDs and exact mbox hashes. Coordinator inspected the job log and commit metadata; mbox bytes were not independently downloaded.
- **Host closure accepted:** CI [38486683289](https://github.com/Drzet/linux/actions/runs/38486683289), job 115601903926, passes child lifecycle, twelve reservation cases and ten production probe/unwind scenarios. Coordinator inspected the tests and reran all three locally against corrected f8d742ff, also PASS. These extract production C and mock external APIs; no kernel bus/provider or handset result is implied.
- **Consolidation:** sole candidate `razr/vpu-provenance-v5@a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac` adds the three unchanged tests and read-only host workflow, and redirects validation filters to this branch. Drivers and bindings are unchanged. Reconstruction automation remains only in historical test branches. Existing schema/full ARM64 evidence is reused; duplicate CI skipped for the consolidation commit.
- **Historical branches:** `razr/vpu-upstream@ec9a8949` preserves original evidence; `razr/vpu-closure-tests@816b6e07` preserves test/reconstruction history; `razr/vpu-provenance-closure@228e7406` is a metadata-capture scaffold on the old base, not an incomplete replacement to merge. All are frozen by policy. No force push or branch deletion.
- **Remaining gate:** inherited malformed/failed range reservations may omit restrictions. This behavior was characterized, not repaired. SM8475 remains gated; firmware/resource policy and hardware operation remain unresolved. Closure acceptance is not integration approval. VPU pauses; queued USB research has no technical dependency on VPU.

## Enablement disposition and next source task — 2026-10-14

Retain the reviewed disabled candidate. Existing host tests demonstrate the upstream v5 missing-reservation failure behavior, not fail-closed DMA. No local IOMMU rewrite or active-DMA authorization is selected. A narrow current-source check inspected `torvalds/linux@4056b3c9d3c92ea45955641dbafeb9b960e146ef:drivers/iommu/of_iommu.c`, which lacks the helper and device iommu-ranges support; targeted series/failure searches surfaced the existing [v5 series](https://lists.openwall.net/linux-kernel/2026/09/26/358) and [v5 helper patch](https://lists.openwall.net/linux-kernel/2026/09/26/362), not a verified newer correction. This is limited coverage, not an exhaustive absence claim. Revisit that exact gate at an enablement decision.

After accepting USB lifecycle closure, coordinator activates only VPU power/OPP and ICC source-contract resolution in NEXT_TASKS. Already qualified MDT/MBN/PAS source facts and context/provenance work are not reopened. Firmware authentication/HFI remain runtime gates.

## Power/ICC source-contract review — 2026-10-14 evening

**Accepted source analysis:** project `8add1e1e055b79bb5568669d6202e2c3ab3a2376`, a single canonical-handoff change. No kernel/DT/build result is claimed. Keep the result on the owner branch at this [pinned handoff](https://github.com/Drzet/razr2022_nuc/blob/8add1e1e055b79bb5568669d6202e2c3ab3a2376/docs/handoffs/2026-10-13-vpu-tenth-recovery.md#source-contract-decision--2026-10-14); do not wholesale merge stale owner-branch policy.

Coordinator independently inspected pinned Motorola VIDEOCC RCG and Cape PLL tables, the candidate Iris MXC/MMCX order and current video-mem-only resource helper, the mainline SM8450 route graph and RPMh aggregation, and the comparator Iris2 calculation/voting bodies. Reconstructed graph routes directly from mainline node links: VIDEO→mem_noc_sf→mnoc_sf→LLCC→llcc_mc→EBI; VIDEO→LLCC and llcc_mc→EBI split without shared nodes. The vendor calculation's LLCC result includes DDR traffic, while mainline sums average requests. A long D path plus a full L path therefore double-counts the shared segment.

The 720 MHz RCG level is VDD_LOWER but Cape PLL0 skips that level and requires VDD_LOW for MXC. This supports the asymmetric parent-level vote table, not a verified consumer OPP table. Actual read-only divider and rounded-rate mapping remains missing; software scaling by three is not a divider measurement. Keep final OPP rows held.

The source decision closes the route/topology question, but does not supply a justified workload bandwidth producer. Candidate `sm8475_data` still uses the provisional SM8250 table. Next task is the exact decoder-input mapping and, only where inputs are justified, an extracted vendor-calculator host reference. No new driver, ICC provider, shared DTS, full build or active VPU is selected. No reason to repeat completed firmware/provenance work.

**Evidence boundaries:** coordinator source checks above are independent. Stock-export hashes, both-base comparison and Motorola/comparator whole-file hash equality remain the agent's reported checks; not newly rerun here. Current commit records Drzet author metadata; the user identifies the current VPU executor as the local Codex bot. Do not infer authentication identity from author metadata or rewrite the evidence to normalize it.

**Status:** source-contract task accepted; decoder producer task active. USB, Boot, Userspace, GPU, Power and DP stay paused. No functional dependency on USB; one active stream remains the resource policy. Accepted integration `2b5acf108ae37040ac1e652e029bb37f5609e886` and disabled VPU kernel candidate a1f0288d remain unchanged.
