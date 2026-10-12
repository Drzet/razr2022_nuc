# Project status

Updated 2026-10-12, fourth coordinator review. Work continues without hardware access. Earlier stock ADB observations remain valid; both uploaded live-DT archives contain zero property files. No native Linux phone test has passed.

See [FOURTH_REVIEW.md](FOURTH_REVIEW.md) for exact heads, source findings and evidence corrections; [NEXT_TASKS.md](NEXT_TASKS.md) contains current assignments and concurrency.

| Workstream | Accepted result | Next gate |
| --- | --- | --- |
| Boot | All-applicable schema pass at `2b473619`; same DT source at `525b504` with independent FDT pass; warnings reduced 35→7; disabled USB2 staging; synthetic v4 packaging tests pass | Deferred PHY-input review (not an identified UART/initramfs blocker), stock variant composition, explicit packaging contract |
| GPU | GMU error fix `3baaec59` passes full Image/modules and normal modpost; shared UBWC reviewed | Actual stock firmware comparison, CX/bandwidth disposition; combined integration |
| VPU | VPU20_4V, SQE, GMU and signed ZAP located and hashed; prior Iris build passes | Six-FDT export complete; translate IOMMU/OPP/ICC and loader contract |
| USB | Attributable PS5169 `4cbfc014` passes full ARM64 Image/modules and binding checks | Register-error/retry semantics, reset/PM disposition; board consumers disabled |
| Power | Signed-temperature fix and UML tests pass; standalone series isolated; charger policy researched | Combined link, stock rail delta and bounded read-only plan |
| DisplayPort | Source/graph audit complete; missing actual AUX variant properties explicitly recorded | Consume completed AUX export now; remain held if part/binding unresolved |
| Userspace | Fresh full Debian ARM64 build + ownership + QEMU systemd/SSH/shutdown [38180519542](https://github.com/Drzet/razr2022_nuc/actions/runs/38180519542) passed; native artifact fixtures pass | Boot schema alignment, combined project-kernel QEMU test |

Next integration milestone: a selected combined kernel, matching installed modules/config/DTB and immutable build manifest, followed by Userspace testing with QEMU virt's DT. No combined kernel has been built by this review. Firmware acquisition is complete; six-FDT stock property publication is now complete; composition/typed translation remain. No repeat full ROM scan is needed.

Physical-only gates: native boot, secure firmware loading, GPU/VPU operation, USB/DP, charging and electrical/thermal behavior. Public stock reference is not proof of installed byte identity or the running overlay.

Historical queues: [THIRD_REVIEW.md](THIRD_REVIEW.md), [SECOND_REVIEW.md](SECOND_REVIEW.md).

Clock severity correction: [source-based reclassification](GCC_PHY_CLOCK_RECLASSIFICATION.md) confirms CCF orphan handling and UART clock independence. Seven static PHY references are not seven missing hardware dependencies. Actual mux states and runtime behavior remain untested.

Fourth-assignment amendment: [VPU extraction review](FOURTH_REVIEW_VPU_UPDATE.md). Coordinator verified artifact and JSON hashes and inspected raw properties/fixup targets. All agents can resume; no agent needs to wait for another extraction round before starting. Boot owns composition, while interpretation and independent coding proceed concurrently.
