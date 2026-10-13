# Project status

Updated 2026-10-13 after reuse audit and cleanup. **VPU upstream adaptation is delivered and build-tested; bounded provenance and production-path validation closure remains.** Bespoke VPU peer-driver work is superseded. USB's PS5169 source/test task is complete. Native handset execution remains untested.

[Assignments](NEXT_TASKS.md) · [Policy](WORKFLOW.md) · [Cleanup and branch disposition](CLEANUP_2026-10-13.md)

| Owner | Current evidence/state | Next action |
| --- | --- | --- |
| VPU | Qualcomm-derived candidate ec9a8949 has full-build evidence at fa899044 and final schema/routing pass | Correct provenance and execute range/lifecycle failure tests; no integration yet |
| USB | PS5169 ARM64 build passed at 8356706; conditional-schema/probe tests passed at 4dcbc7b, fixing a real YAML bug | Pause; NXP reuse decision queued |
| Boot | Combined kernel and diagnostic-v2 host packaging accepted; digest corrected | Pause until concrete integration/new loader input |
| Userspace | Project-kernel Debian/QEMU and diagnostic v2 tests accepted | Pause |
| GPU / Power | Existing narrow fixes and accepted integration retained | Pause |
| DisplayPort | Source routing research complete; AUX identity unresolved | Evidence hold |

Accepted kernel `2b5acf108ae37040ac1e652e029bb37f5609e886`, [integration record](../configs/accepted-integration-2026-10-12.json), and [diagnostic v2 record](../configs/accepted-native-console-v2-2026-10-13.json) are unchanged. Experimental USB/VPU remain excluded. No new combined build or image is needed for this cleanup.

Native loader/memory/DT/ramdisk handoff and accessible output remain unresolved. VPU PAS/HFI/DMA/decode and USB powered link/wake behavior require device validation. NXP/AUX identities and electrical parents remain specific evidence gaps, potentially resolvable from attributable documentation. Do not confuse these with missing generic drivers.

Latest decision: [VPU candidate review](VPU_REVIEW_2026-10-13.md). VPU remains the sole selected stream; no unchanged full build is requested.
