# Ninth coordinator review — 2026-10-13 (Europe/Lisbon)

**Boot's metadata correction is accepted. VPU's DMA ownership decision is accepted as a conditional prototype direction, not an implemented or hardware-validated port.** No kernel, image, firmware or integration change is accepted in this review.

## Reviewed submissions

| Owner | Project revision | Result |
| --- | --- | --- |
| Boot | `3462c5e61c0defde33c49eee647064894dc5b24b` | Both malformed digest records corrected; assignment complete |
| VPU | `5f6738589f4a339ed9fafd382715bc0f20c06777` | Source-pinned nonsecure DMA ownership decision and handoff complete |

Boot's two-file diff changes only the erroneous digest. Coordinator recalculated SHA256 directly from the existing artifact 11777433748 ZIP's boot image and checked the corrected JSON: `1e00e4f998f5001bc08d9e0d4e4465664100194ce211cd9eb8b329612b5563bb`. It agrees with the [accepted v2 record](../configs/accepted-native-console-v2-2026-10-13.json). No rebuild is warranted. [Corrected Boot handoff](https://github.com/Drzet/razr2022_nuc/blob/3462c5e61c0defde33c49eee647064894dc5b24b/docs/handoffs/2026-10-12-boot-seventh-console-v2-repackage.md).

[VPU decision](https://github.com/Drzet/razr2022_nuc/blob/5f6738589f4a339ed9fafd382715bc0f20c06777/docs/vpu/2026-10-13-nonsecure-dma-ownership-decision.md) and [handoff](https://github.com/Drzet/razr2022_nuc/blob/5f6738589f4a339ed9fafd382715bc0f20c06777/docs/handoffs/2026-10-13-vpu-eighth-round.md) contain no new driver code or runtime result.

## Independent source checks and interpretation

Coordinator re-read the pinned Xiaomi Waipio comparator's [memory map/unmap implementation](https://github.com/LowTension/android_kernel_xiaomi_sm8475/blob/39382bf760ccf05a8fb4dddee7138ecac02d4a59/techpack/video/driver/vidc/src/msm_vidc_memory.c) and [context-bank setup](https://github.com/LowTension/android_kernel_xiaomi_sm8475/blob/39382bf760ccf05a8fb4dddee7138ecac02d4a59/techpack/video/driver/vidc/src/msm_vidc_dt.c). Mapping selects a region-specific `cb->dev`, attaches the DMA-buf to that device, and unmaps/detaches at the last mapping reference. Context setup stores the child device and obtains its domain. It reads/logs `virtual-addr-pool`; that code alone does not establish allocator enforcement. This is a source comparator, not proof of Motorola's executed kernel.

Coordinator also re-read experimental Iris [queue setup](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/media/platform/qcom/iris/iris_vidc.c) and [internal allocation](https://github.com/Drzet/linux/blob/869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf/drivers/media/platform/qcom/iris/iris_buffer.c): both vb2 queues and internal allocations currently use the parent device. Merely adding a second parent `iommus` entry does not implement separate DMA ownership.

The pinned [generic DMA allocator](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/iommu/dma-iommu.c) initializes its lower bound from domain geometry and reserves IOMMU-reserved regions; its allocation limit caps the upper address. A DMA mask alone does not impose the vendor pool minimum. These are investigation targets, not approval to mutate a live domain's geometry, reach into its private cookie, or invent a DT property.

**Accepted direction:** investigate two ordinary separately DMA-attached consumer devices for nonpixel and pixel buffers, with all allocations, imports and releases assigned to the correct owner. This is the best-supported proposal among the evaluated options. It is not proof that silicon requires two domains or that a single-domain alternative can never work. Distinct nonsecure contexts do not by themselves establish a security boundary.

**Correction to the handoff's final gate:** firmware/HFI acceptance is a native validation result. It is not required before developing an isolated disabled prototype. Source/API justification, reviewable binding semantics and correct ownership are offline prerequisites; actual grouping, firmware acceptance, fault-free DMA and decode remain later device tests.

## Next decision and dependency order

VPU alone receives a bounded address-window and child-device feasibility task, with a concrete patch sketch or a precise unsupported-API finding. First establish whether the vendor minima are actually enforced and necessary; then identify a valid upstream representation. Do not spend another round restating the two-device recommendation. See [NEXT_TASKS](NEXT_TASKS.md) for scope and stopping conditions.

Boot and Userspace are complete for the accepted diagnostic profile and pause. GPU/Power/USB/DP remain paused or queued; none is waiting for this VPU result to make the accepted console image valid. Boot is needed later only to integrate a reviewed shared-DTS change. USB's queued work is technically independent; keeping it queued is a scope decision, not a VPU dependency. No blanket concurrent round is requested.

Accepted kernel remains `2b5acf108ae37040ac1e652e029bb37f5609e886`; experimental Iris remains excluded. Native loader behavior and accessible diagnostic output are unresolved. MXC/MMCX OPP and DDR/LLCC policy remain separate VPU work. No hardware success, new CI success or device action is claimed.
