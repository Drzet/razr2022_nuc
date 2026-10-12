# Ninth VPU decision: enforce IOVA windows with pinned DMA APIs

**2026-10-13.** Coordinator main ninth-review NEXT_TASKS blob b4e9fe744b31e6475cdd3dc5d970e25273b39b45. Starting project VPU 5f6738589f4a339ed9fafd382715bc0f20c06777, kernel VPU 869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf. This is the requested focused follow-up to [eighth-round ownership tracing](2026-10-13-nonsecure-dma-ownership-decision.md), **not another general DMA design review**.

## 1. Source finding: video virtual-addr-pool is parsed, not shown enforced

**Waipio/SM8475 downstream comparator**, NOT proven Motorola-executed code: LowTension/android_kernel_xiaomi_sm8475 commit 39382bf760ccf05a8fb4dddee7138ecac02d4a59.

- [msm_vidc_dt.c, functions msm_vidc_populate_context_bank and msm_vidc_setup_context_bank, lines 774–919](https://github.com/LowTension/android_kernel_xiaomi_sm8475/blob/39382bf760ccf05a8fb4dddee7138ecac02d4a59/techpack/video/driver/vidc/src/msm_vidc_dt.c#L774-L919), blob 1430d8f717d1143e8264daf346cea877a845dfaf: reads virtual-addr-pool into cb->addr_range, **logs it**; child dev obtains iommu_get_domain_for_dev; vendor iommu_dma_enable_best_fit_algo selects allocation *algorithm*, not min/max; SG segment configuration is not range enforcement.
- [msm_vidc_memory.c, msm_vidc_memory_map, lines 182–315](https://github.com/LowTension/android_kernel_xiaomi_sm8475/blob/39382bf760ccf05a8fb4dddee7138ecac02d4a59/techpack/video/driver/vidc/src/msm_vidc_memory.c#L182-L315), blob fd810c781d67f7c1d459497fadeea20aae245e29: chooses context bank by region, dma_buf_attach(dmabuf, cb->dev), dma_buf_map_attachment, takes first DMA SG address. No comparison to cb->addr_range; [msm_vidc_memory_alloc, lines 343–446](https://github.com/LowTension/android_kernel_xiaomi_sm8475/blob/39382bf760ccf05a8fb4dddee7138ecac02d4a59/techpack/video/driver/vidc/src/msm_vidc_memory.c#L343-L446) selects heap by security/cache, not IOVA start.
- A **different** vendor mechanism actually reserves unwanted address ranges: [drivers/iommu/qcom-iommu-util.c, qcom_iommu_generate_dma_regions and qcom_iommu_generate_resv_regions, lines 100–222](https://github.com/LowTension/android_kernel_xiaomi_sm8475/blob/39382bf760ccf05a8fb4dddee7138ecac02d4a59/drivers/iommu/qcom-iommu-util.c#L100-L222), blob 55a14ecc1a9ae1ac5e4da030492cddd9c0d7534f, reads **qcom,iommu-dma-addr-pool**, constructs complementary IOMMU_RESV_RESERVED windows, called by vendor [arm_smmu_get_resv_regions, lines 3202–3217](https://github.com/LowTension/android_kernel_xiaomi_sm8475/blob/39382bf760ccf05a8fb4dddee7138ecac02d4a59/drivers/iommu/arm/arm-smmu/arm-smmu.c#L3202-L3217), blob b6b96e6d67cb8954519e33bdcb82b4c806b7d73b.

**Disposition:** the compiled Motorola reference FDT gives two distinct nonsecure IOVA policy ranges, bitstream/nonpixel [0x25800000,0xe0000000), pixel [0x00100000,0xe0000000), but the pinned video path does **not** demonstrate that virtual-addr-pool is enforced, nor that either lower floor is a hardware/firmware *necessity*. Conservatively retaining them for a future disabled prototype is [INFERRED] software policy, not proven mandatory silicon restriction. Do not silently assume source pools are either irrelevant or automatically active.

## 2. Valid MAINLINE low-IOVA reservation already exists

**No Qualcomm-specific IOMMU-core modification is necessary for the proposed low-floor allocator policy**, provided the child consumer really gets its own normal DMA domain and correctly wired OF reservation.

- Pinned kernel [drivers/iommu/of_iommu.c, of_iommu_get_resv_regions, lines 170–270](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/iommu/of_iommu.c#L170-L270), blob a18bb60f6f3dfdba853b6e16dd2a8616f6a731c7: walks the **consumer's memory-region** references and the reserved node's **iommu-addresses**. The target must match **exactly that consumer's OF node**. When no physical reg is supplied, creates IOMMU_RESV_RESERVED, an IOVA-only reservation. It does not reserve physical firmware RAM.
- Pinned [ARM SMMU get_resv_regions](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/iommu/arm/arm-smmu/arm-smmu.c#L1603-L1617), blob 889a0966d36cdba2c2c6478cf71a1e0894ca42a3, delegates to [dma-iommu.c iommu_dma_get_resv_regions](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/iommu/dma-iommu.c#L453-L471), blob 68ee57800fefc15bc417cc2581c1a01acc8979ae.
- [dma-iommu.c iova_reserve_iommu_regions, lines 553–589](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/iommu/dma-iommu.c#L553-L589) reserves the entire excluded low IOVA window in the allocator's IOVA tree, and is called by [iommu_dma_init_domain, 662–723](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/iommu/dma-iommu.c#L662-L723) **before any regular DMA allocation**. [iommu_dma_alloc_iova, 760–805](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/iommu/dma-iommu.c#L760-L805) uses that same allocator for mapping; coherent allocations and SG imports use the same DMA-IOMMU mechanism. This is an actual prospective *allocator enforcement*, not a post-map check or direct iommu_map bypass.
- **Independent DTS precedent**, not Oneli validation: [QCS6490 Radxa Dragon Q6A](https://github.com/coolsnowwolf/lede/blob/ff7be3fa21cae4277a0b2e8d6653b8acce8ac236/target/linux/qcom/files-6.18/arch/arm64/boot/dts/qcom/qcs6490-radxa-dragon-q6a.dts) has a no-reg reserved-memory iris-iova node with iommu-addresses referring to Venus, and Venus memory-region references its physical firmware carveout **and** that IOVA reservation. Its 0x25800000 low reservation matches the general Qualcomm video convention.

**Candidate DTS structure (illustrative, not an approved binding, NOT applied to Boot-owned DTS):**

    reserved-memory {
        vpu_nonpixel_iova: iris-nonpixel-iova {
            iommu-addresses = <&vpu_dma_ns 0x0 0x0 0x0 0x25800000>;
        };
        vpu_pixel_iova: iris-pixel-iova {
            iommu-addresses = <&vpu_dma_px 0x0 0x0 0x0 0x00100000>;
        };
    };

    vpu_dma_ns: video-nonpixel-dma {
        compatible = "qcom,sm8475-iris-dma-context"; /* PROPOSED, not upstream */
        iommus = <&apps_smmu 0x2180 0x400>;
        memory-region = <&vpu_nonpixel_iova>;
        status = "disabled";
    };
    vpu_dma_px: video-pixel-dma {
        compatible = "qcom,sm8475-iris-dma-context"; /* PROPOSED, not upstream */
        iommus = <&apps_smmu 0x2187 0x400>;
        memory-region = <&vpu_pixel_iova>;
        status = "disabled";
    };
    /* Existing disabled controller references BOTH consumer phandles,
       with a proposed reviewed property. Existing 7MiB PAS physical
       memory-region stays on controller, NOT on these children. */

**Exact cell count and OF DMA translations must be verified against the real combined Boot-owned DT**, not assumed from this excerpt (2 address + 2 size cells is the example). The two proposed consumer compatibles and controller property are unreviewed ABI proposals, not claimed existing bindings. No physical RAM is excluded by IOVA-only nodes. No private DMA-cookie access, raw iommu_map alongside VB2, runtime domain.geometry writes, or unexplained DMA-ranges. The current provisional 0xdfffffff DMA numeric mask on the consumer gives an **upper limit only**; even its unusual bit shape needs dma_supported and ABI validation. It does not set either minimum. All allocations and imports must use those configured consumer DMA devices, otherwise reservations are bypassed.

## 3. Concrete driver/OF topology sketch, no synchronous probe cycle

**Preferred first reviewable prototype:** two **independently enumerable /soc peer platform DMA-consumer devices** (logically the two downstream video context-bank children), each with a real OF node and single SMMU SID, and one disabled existing video-control parent referencing them by an explicitly *proposed* phandle list, e.g. vpu-dma-consumers in nonpixel,pixel order. The vendor's nested placement is not a hardware requirement. Peers avoid a potentially circular dependency in which the video-parent's probe creates nested children and synchronously waits for their driver binding while the children wait for the parent probe to finish.

**Consumer context probe, future separate small driver** (proposed iris_dma_context.c):
1. Bind independently by a reviewed compatible, never call/await the Iris parent. The pinned [drivers/base/dd.c really_probe, 652–706](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/base/dd.c#L652-L706) invokes bus DMA configure **before** platform driver probe; pinned [platform_dma_configure, 1540–1570](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/base/platform.c#L1540-L1570) configures OF DMA and uses the **default** IOMMU domain unless driver_managed_dma is set. The context driver must not opt into driver_managed_dma. [of_dma_configure_id, 83–169](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/of/device.c#L83-L169) handles IOMMU provider/probe deferral.
2. Before any allocation, check IOMMU DMA domain exists and suitable configured upper bound; publish role-typed drvdata only when ready. No secure support. A platform child device with **no bound driver** has not necessarily executed the needed full bus DMA/default-domain setup; do not use an unbound proxy.
3. Pins for exact two context entries are [arm_smmu_of_xlate, lines 1587–1600](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/iommu/arm/arm-smmu/arm-smmu.c#L1587-L1600): 0x400 is SMR match mask. [arm_smmu_find_sme, lines 1028–1068](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/iommu/arm/arm-smmu/arm-smmu.c#L1028-L1068) rejects overlapping entries; SID 0x2180 and 0x2187 differ in low three bits not masked by 0x400, so distinct stream match entries are source-plausible. Confirm actual separate groups/default domains, do not merely assume them.

**Controller probe** (iris_probe.c / iris_core.h, before video registration):
1. Parse two phandles and look up the separate consumer platform devices with pinned [of_find_device_by_node](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/of/platform.c#L36-L43). This returns a reference requiring put_device on each exit.
2. Missing/unbound supplier: -EPROBE_DEFER; wrong role, same node, same iommu_group or same iommu_get_dma_domain: hard failure. Use device_link_add(controller, child, DL_FLAG_PM_RUNTIME | DL_FLAG_AUTOREMOVE_CONSUMER), check non-null, hold explicit device refs; release after draining all session buffers and HFI queues. Device-link flags and device_is_bound APIs exist in pinned include/linux/device.h.
3. Register V4L2 only **after** both suppliers are configured; never fall back to core->dev. Consumer context driver has **no parent probe dependency**, so controller deferral is acyclic. Supplier detach/remove with active sessions requires links and teardown enforcement, not unchecked device pointers.

**Allocation patch interfaces, intentionally a later step:** iris_vidc.c::iris_m2m_queue_init chooses decoder compressed OUTPUT->nonpixel, raw CAPTURE->pixel, encoder reversed. VB2 DMA-contig handles the selected actual DMA consumer for mmap and DMABUF import. iris_buffer.c internal DPB uses pixel, nonpixel scratch uses nonpixel; **store struct device * owner per buffer** for matching dma_alloc_attrs/dma_free_attrs. iris_hfi_queue.c command/message/debug+SFR must use nonpixel for both alloc and free. iris_firmware.c signed PAS9 physical carveout remains independent and parent-owned. Imported identical DMABUFs across roles require two **separate** attachments/IOVAs/lifetimes.

**Patch order for review, not committed:** (1) standalone binding for two context consumers + controller phandle reference, compatible justification; (2) separately prepared disabled DT fixture, Boot owns true SoC/board DTS, check phandles and iommu-addresses translation; (3) small context-probe + parent dependency checks; (4) separate per-buffer/VB2/HFI routing only on further coordinator approval. Driver patch and binding patch remain separate, no schema or compiler success claimed.

## 4. Acceptance and exact remaining gate

Before code approval: review whether the two **peer, DMA-owning proxy devices** with actual SMMU streams correctly describe this hardware in mainline DT, and whether the real Oneli bus OF address translation permits the **per-device** iommu-addresses reservation and survives the default IOMMU domain setup. No evidence yet that these new compatible strings would be accepted upstream. This is a concrete ABI/topology review question, **not a missing IOMMU allocator API**.

Host negative tests when implemented: missing/duplicate/unbound contexts, missing SMMU supplier, -EPROBE_DEFER retry, wrong/missing reservation, max bound, invalid SG or mapped size, partial attach, two-role same DMABUF, deferred DPB release, streamoff/firmware fault/unbind; confirm exact matching unmap/free device and no leaked supplier reference. Unit tests of excluded address ranges **are not runtime evidence**. Phone-only later: real SIDs/domain allocation, IOVA values, HFI ACK, PAS9 signature acceptance, DMA faults and decode. These are test outcomes, not prerequisites for a *disabled* host prototype.

**Decision:** a pinned mainline allocator mechanism for the source IOVA floor is found, and an independent two-consumer topology with no synchronous parent/child probe wait is fully sketched. The hardware **necessity** of each floor is still unproven; correct binding topology and OF address translation remain the narrow review gates. Experimental VPU remains disabled; do not change kernel/integration 2b5acf108ae37040ac1e652e029bb37f5609e886, run unnecessary CI, touch Boot's DTS, or broaden into RPMh OPP/ICC.
