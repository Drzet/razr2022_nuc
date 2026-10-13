# Next assignments — ninth coordinator review, 2026-10-13

Read [NINTH_REVIEW.md](NINTH_REVIEW.md). Boot's correction and VPU's bounded ownership decision are accepted within their documented scopes. Previous instructions are archived in [EIGHTH_ASSIGNMENTS.md](EIGHTH_ASSIGNMENTS.md). Preserve accepted integration `2b5acf108ae37040ac1e652e029bb37f5609e886` and diagnostic v2 artifacts.

## VPU — selected next: make the DMA proposal implementable

Start from project `5f6738589f4a339ed9fafd382715bc0f20c06777` and experimental kernel `869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf`. The two-consumer direction is conditionally accepted. Resolve these specific offline questions in order:

1. Trace **enforcement**, not just parsing, of the downstream nonpixel `[0x25800000, 0xe0000000)` and pixel `[0x00100000, 0xe0000000)` IOVA windows. Follow the pinned vendor DMA/IOMMU path consuming the pool; distinguish a hardware/firmware constraint from allocator policy and from an unused property. If necessity cannot be established, label it unresolved rather than silently assuming either unrestricted addressing or a mandatory hardware limit.
2. Establish a supported mechanism in our pinned mainline kernel for any constraints retained by the prototype. Inspect domain geometry/reserved-region hooks and their setup timing, including coherent allocations and imported DMA-bufs. A DMA mask supplies no lower bound. Do not use private DMA-cookie manipulation, raw mapping alongside vb2, arbitrary runtime geometry writes, or `dma-ranges` merely as an unexplained alias for vendor pools. Name any required core change explicitly; no broad IOMMU rewrite is authorized.
3. Supply a concrete proposed child-binding/topology and lifecycle patch sketch: creation, OF DMA configuration, driver binding/default-domain attachment, supplier dependencies, probe deferral, teardown and retained DMA-owner references. Check for parent/child probe dependency cycles. Show which device owns HFI queues, external queues and internal classes. This is a proposal for review, not an already upstream-approved ABI.

**Deliverable:** one focused handoff with exact source revisions/functions, the enforcement finding, proposed interfaces and a patch sketch (or the exact missing API/evidence and smallest next change). Update the existing decision if needed; do not produce another general architecture survey. If steps 1–3 establish a valid mechanism, an isolated disabled experimental patch is permitted, with compilation/schema checks appropriate to changed code. Keep binding and any DT proposal separate; Boot owns applying shared board/SoC DTS changes. Otherwise stop at the concrete limitation. Do not silently rebase, replace accepted artifacts or enable the phone VPU.

No native firmware ACK is needed to prepare a disabled prototype. Actual domain separation, IOVA behavior on the handset, HFI response, SMMU faults and decode are deferred hardware acceptance tests. Host models can check proposed arithmetic/ownership but cannot prove those device outcomes. Secure sessions, MXC/MMCX OPP, ICC policy and broad Iris refactoring remain outside this task. No repeated firmware extraction or unchanged kernel build.

## Boot / Userspace — complete; pause

Boot's digest correction matches the actual artifact bytes in both records. No further correction, repackaging or CI replay is assigned. Userspace's diagnostic v2 remains accepted. Resume Boot for a concrete reviewed shared-DTS request or new attributable loader/device evidence; resume Userspace for an actual interface/transport requirement. Do not require native boot success before a future controlled boot experiment can be planned.

## GPU / Power / USB / DisplayPort — unchanged

GPU and Power pause; USB's unfinished profile/lifecycle work remains queued in [FIFTH_ASSIGNMENTS.md](FIFTH_ASSIGNMENTS.md); DP retains the AUX-identity evidence hold. These are not all blocked by VPU. USB source work could run independently, but is not selected in this assignment. Do not restart completed audits or launch a blanket concurrent round.

## Coordinator — review before integration

Review VPU's concrete allocator/topology result before authorizing a wider routing/lifetime implementation. If no supported mechanism is found, choose explicitly between a narrowly scoped core proposal and another queued workstream; do not commission the same audit again. Boot joins only if an actual shared-DTS change is ready. No hardware access is assumed and no device action is assigned.
