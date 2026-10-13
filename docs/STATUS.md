# Project status

Updated 2026-10-13, tenth coordinator review. **VPU has a source-supported IOVA reservation mechanism and is authorized to implement a disabled consumer prototype. USB's profile/lifecycle candidate passed full ARM64 build and host fault tests.** Native handset execution remains untested.

See [TENTH_REVIEW.md](TENTH_REVIEW.md) and [NEXT_TASKS.md](NEXT_TASKS.md).

| Workstream | Verified progress | Next action |
| --- | --- | --- |
| Boot | Diagnostic v2 host packaging and digest correction accepted | Pause; future shared-DTS request or new loader evidence |
| Userspace | Project-kernel QEMU and diagnostic v2 accepted within their scopes | Pause |
| VPU | Upstream IOVA-only reservation API confirmed; topology remains experimental | Binding/fixture and DMA-consumer lifecycle prototype |
| USB | 27-entry profile, production-function fault tests, schema and full ARM64 build passed at 8356706 | Board-specific schema fixtures and build-record update, then pause |
| GPU / Power | Previously reviewed source/integration work unchanged | Pause |
| DisplayPort | Reference AUX analysis complete; IC identity unresolved | Evidence hold |

VPU and USB's assigned tasks may run concurrently. Boot is needed only for a later shared-DTS change. No other agent depends on VPU to preserve the accepted minimal build.

Accepted integration is unchanged at `2b5acf108ae37040ac1e652e029bb37f5609e886`. Experimental Iris and PS5169 are excluded. [Diagnostic v2 record](../configs/accepted-native-console-v2-2026-10-13.json) remains authoritative; no new kernel/ramdisk/boot image is selected.

Native loader-populated memory, placement/DT/ramdisk handling and accessible output remain unresolved. VPU PAS/HFI/DMA/decode and USB powered communication/link/wake tests require the handset. Identity/wiring questions may also be resolved by attributable documentation. Source checks and QEMU do not establish these device outcomes.
