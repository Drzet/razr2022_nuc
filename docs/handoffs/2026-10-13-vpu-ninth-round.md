# VPU ninth round: IOVA enforcement and DMA context topology handoff

- **Date and originating chat:** 2026-10-13, VPU-only ninth coordinator review assignment.
- **Project repository / branch:** Drzet/razr2022_nuc, razr/vpu. Source decision committed as 35d16fed45393678392b45448596e94e70881d5d; eighth decision forward reference at d657f0cb1c8f60a09f656e944c65708f2e66d461. This handoff is the new branch tip on publication; [draft project PR #1](https://github.com/Drzet/razr2022_nuc/pull/1).
- **Kernel source and baseline:** Drzet/linux:razr/vpu remains **869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf**; upstream base **a5ebb76233b79db01e82e061173cb73c6d2b5c6b**. Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** not touched. No shared Boot DTS, boot diagnostic image or vendor_boot changed.
- **Coordinator inputs:** main docs/NINTH_REVIEW.md blob **3a43518e11620e328a914d3bb30ec199a9f5fad4**, main NEXT_TASKS.md blob **b4e9fe744b31e6475cdd3dc5d970e25273b39b45**; prior VPU **5f6738589f4a339ed9fafd382715bc0f20c06777**.
- **Evidence stages:** source inspected / reasoned **YES**; driver/binding implemented **NO**; this ninth-round compile/schema test **NOT RUN**; native hardware **NOT TESTED**. Previously accepted unrelated source/image/build evidence stays unchanged.

## Changes and provenance

**Only new substantive deliverable:** [2026-10-13-iova-window-enforcement-child-topology.md](../vpu/2026-10-13-iova-window-enforcement-child-topology.md), which fixes the specific unsupported assumptions in the [accepted eighth ownership decision](../vpu/2026-10-13-nonsecure-dma-ownership-decision.md) without redoing the previous GPU/video firmware extraction.

**Vendor-side enforcement:** in pinned independent Waipio comparator LowTension/android_kernel_xiaomi_sm8475@39382bf760ccf05a8fb4dddee7138ecac02d4a59, msm_vidc_dt.c::msm_vidc_populate_context_bank only **reads/logs** virtual-addr-pool. msm_vidc_memory.c::msm_vidc_memory_map selects a per-region child DMA device for dma_buf_attach/map but **does not check cb->addr_range**. The actual Qualcomm region-limiting helper qcom_iommu_generate_resv_regions in drivers/iommu/qcom-iommu-util.c (blob **55a14ecc1a9ae1ac5e4da030492cddd9c0d7534f**) instead parses **qcom,iommu-dma-addr-pool** and reserves its complement through the vendor ARM SMMU get_resv_regions. This is a *different* property from the video pool. The selected installed Motorola driver and real silicon need for each floor are still **unproven**.

**Pinned MAINLINE solution:** Drzet/linux@869cf4 source:
1. of_iommu.c::of_iommu_get_resv_regions (blob **a18bb60f6f3dfdba853b6e16dd2a8616f6a731c7**) associates a **consumer's memory-region** with reserved-memory **iommu-addresses**. If reserved node omits physical reg, it becomes IOMMU_RESV_RESERVED, so no physical RAM is earmarked.
2. arm-smmu.c::arm_smmu_get_resv_regions (blob **889a0966d36cdba2c2c6478cf71a1e0894ca42a3**) calls dma-iommu's OF reserved region helper; dma-iommu.c::iommu_dma_init_domain / iova_reserve_iommu_regions (blob **68ee57800fefc15bc417cc2581c1a01acc8979ae**) reserves these addresses **before** normal coherent or scatter-gather DMA mapping.
3. Therefore two role-specific reservations of [0,0x25800000) (nonpixel) and [0,0x00100000) (pixel), each on its **own** real DMA device, are a source-supported mechanism for conserving the reference IOVA floors. The existing provisional numeric upper bound 0xdfffffff remains to validate separately. **No custom IOMMU-core code, late geometry mutation or private cookie** appears needed.
4. Independent [Qualcomm QCS6490 reference DTS](https://github.com/coolsnowwolf/lede/blob/ff7be3fa21cae4277a0b2e8d6653b8acce8ac236/target/linux/qcom/files-6.18/arch/arm64/boot/dts/qcom/qcs6490-radxa-dragon-q6a.dts) already uses the same Iris low-IOVA no-reg reserved-memory iommu-addresses pattern; it is not an Oneli compile/runtime test.

**Concrete child/topology sketch:** two **independent, physically peer /soc platform consumer devices** with distinct iommus and IOVA-only memory-region, referenced by video parent's *proposed* two-phandle property; controller acts as DMA consumer of those two platform suppliers. Each supplier's small future probe has OF DMA configure/default-domain attachment **before** its probe (drivers/base/dd.c::really_probe / drivers/base/platform.c::platform_dma_configure) and never waits for the controller. Controller returns -EPROBE_DEFER when either is unbound, checks distinct IOMMU group and domain, acquires device references/links, and registers V4L2 only after both ready. This avoids a synchronous **nested parent probe waits for its own children** cycle. It is a reviewable topology suggestion, not a claim of binding ABI approval. Source line/sha citations, illustrative DTS nodes, patch order, removal paths and negative tests are in the detailed report.

## Shared files, order and remaining limitations

Changes restricted to **VPU-owned project docs**; no kernel code, firmware binary or image changed. Boot remains shared SoC/board DTS owner. No Boot execution assigned until **reviewed binding and valid disabled-DT fixture** exists.

Next smallest review/implementation sequence:
1. Coordinator/DT and IOMMU reviewers accept or amend the two **peer** platform DMA-consumer ABI and OF address/size-cell translation; secure contexts deliberately absent.
2. Author separately a new DMA context binding + parent phandle interface in **Drzet/linux**; build a disabled DTS fixture and schema test. Boot integrates the reviewed board nodes only after request.
3. Implement only context-driver default-DMA-owner probes and parent lookup/ref/link/unwind; check -EPROBE_DEFER, missing provider, distinct SMMU group/domain, reserved address windows before exposing V4L2. No speculative active board node.
4. **Later authorized patch:** route VB2 compressed/raw, internal DPB/scratch and HFI command/message/debug/SFR allocations to the correct consumer; honor matching device on free/unmap, read-only DPB lifespan and failure teardown.

The actual Motorola silicon need for the candidate minima is **[INFERRED]**, not independently established by the video property; the intended software policy is conservative and reviewable, not a claim about hardware. Correct combined Oneli DT OF phandle/cell translations and binding acceptance are specific open evidence. No firmware PAS/HFI ACK is required *before developing a disabled host prototype*; actual SMMU, IOVA behavior, signature acceptance and decoded frames are future device results.

## Validation

PASS: pinned source/API audit proving a generic IOVA-only low-address reservation is possible without a mainline IOMMU-core change and identifying the genuine vendor Qualcomm enforcement hook and different property. Source-pin references and actual existing Qualcomm board usage supplied.

NOT RUN: kernel compile, schema fixture, emulator, native phone; no code changed requiring a rebuild. No new action or hardware acceptance asserted. Accepted integration, Boot/Userspace native diagnostic v2, and separate MXC/MMCX/ICC queue remain untouched.

**Disposition:** the ninth task's vendor-enforcement and mainline-allocator questions are answered; the last bounded blocker is **approval of the proposed two-consumer compatible/phandle/OF topology** before code. Do not commission another generic DMA audit, and do not resume all agents.
