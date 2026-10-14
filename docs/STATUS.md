# Project status

Updated 2026-10-14 after VPU branch review and consolidation. **VPU bounded offline closure is accepted: original authorship restored, production-path host tests verified. VPU source-contract work is active; it remains disabled and unintegrated.** Bespoke VPU peer-driver work is superseded. USB's PS5169 and NXP reuse-decision tasks are complete. PTN3222 lifecycle correction at 61202a82 is accepted for its bounded offline scope; USB is paused and remains unintegrated. Native handset execution remains untested.

[Assignments](NEXT_TASKS.md) · [Policy](WORKFLOW.md) · [Cleanup and branch disposition](CLEANUP_2026-10-13.md)

| Owner | Current evidence/state | Next action |
| --- | --- | --- |
| VPU | Canonical candidate a1f0288d on razr/vpu-provenance-v5; production tree unchanged, provenance corrected, host error paths pass | Active: resolve power/OPP and ICC source contract; no kernel edit or enablement |
| USB | PS5169 ARM64 build passed at 8356706; conditional-schema/probe tests passed at 4dcbc7b, fixing a real YAML bug | PTN3222 correction accepted at 61202a82; pause for board/ABI/hardware gates |
| Boot | Combined kernel and diagnostic-v2 host packaging accepted; digest corrected | Pause until concrete integration/new loader input |
| Userspace | Project-kernel Debian/QEMU and diagnostic v2 tests accepted | Pause |
| GPU / Power | Existing narrow fixes and accepted integration retained | Pause |
| DisplayPort | Source routing research complete; AUX identity unresolved | Evidence hold |

Accepted kernel `2b5acf108ae37040ac1e652e029bb37f5609e886`, [integration record](../configs/accepted-integration-2026-10-12.json), and [diagnostic v2 record](../configs/accepted-native-console-v2-2026-10-13.json) are unchanged. Experimental USB/VPU remain excluded. No new combined build or image is needed for this cleanup.

Native loader/memory/DT/ramdisk handoff and accessible output remain unresolved. VPU PAS/HFI/DMA/decode and USB powered link/wake behavior require device validation. NXP/AUX identities and electrical parents remain specific evidence gaps, potentially resolvable from attributable documentation. Do not confuse these with missing generic drivers.

Latest decision: [VPU candidate review](VPU_REVIEW_2026-10-13.md). VPU power/OPP and ICC source-contract decision is the sole active subsystem task. USB and other owners remain paused. Inherited VPU IOVA failure behavior remains an enablement gate; no new IOMMU implementation is assigned. No unchanged full build is requested.

Latest USB decision: [PTN3222 review](USB_REVIEW_2026-10-14.md). Keep project evidence at 63cf2a53 and corrected isolated kernel candidate 61202a82; source/host evidence does not establish handset operation. No rollback or merged integration change.
