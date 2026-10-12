# Project status

Updated 2026-10-12, sixth coordinator review. **The first combined kernel and matching-kernel Debian QEMU milestone has passed.** Coordinator promoted the exact tested commit `2b5acf108ae37040ac1e652e029bb37f5609e886` to `Drzet/linux:razr/integration`. No native phone execution has been tested.

Read [SIXTH_REVIEW.md](SIXTH_REVIEW.md) for independently verified evidence and reviewed heads, [accepted build manifest](../configs/accepted-integration-2026-10-12.json) for hashes, and [NEXT_TASKS.md](NEXT_TASKS.md) for staged assignments.

| Workstream | Current accepted result | Next action |
| --- | --- | --- |
| Boot/integration | Image, 1,702 modules, oneli DT/schema and complete artifact bundle passed; coordinator checked all 1,735 bundle checksums | Native early-initramfs interface, diagnostic-output prerequisites and host-validated packaging |
| Userspace | Exact combined Image booted Debian/systemd in QEMU; real dummy module load, IPv4/SSH and exit-0 poweroff passed | After Boot interface agreement, build/test minimal diagnostic initramfs and hand exact artifact to Boot |
| VPU | Missing properties closed; durable metadata and host loader bounds accepted; SMMU mask semantics resolved | Optional independent bounded DMA ownership design; Iris remains excluded |
| GPU | 13×7 stock properties and exact 12×3 HFI numerical crosswalk passed; prior patches build in integration | Pause; CX-floor ownership/dynamic bandwidth policy unresolved |
| Power | PVT L8C fragment only boot-on; read-only driver write risks documented; signed-temperature patch builds in integration | Pause; no new gauge/charge-control driver selected |
| USB | Prior PS5169 full build/binding/fault tests accepted | Board profile/lifecycle work queued after native packaging |
| DisplayPort | Reference AUX matrix complete | Hold pending actual AUX part evidence |

Verified runs: [combined build 38292394177](https://github.com/Drzet/linux/actions/runs/38292394177), [project-kernel guest 38297826535](https://github.com/Drzet/razr2022_nuc/actions/runs/38297826535), [focused stock fields 38291543595](https://github.com/Drzet/razr2022_nuc/actions/runs/38291543595), [loader audit 38292192600](https://github.com/Drzet/razr2022_nuc/actions/runs/38292192600), [GPU crosswalk 38297688741](https://github.com/Drzet/razr2022_nuc/actions/runs/38297688741).

**Next milestone:** offline construction/validation of an initramfs-only native early-boot image path. Boot defines the interface first; Userspace acknowledges, then their implementation work can overlap. No all-agent concurrent round. Completed VPU extraction no longer blocks consumers.

Physical gates remain actual Motorola bootloader/DT selection, accessible diagnostic output, secure firmware loading, GPU/VPU execution, USB/DP and electrical/thermal/charging behavior. Unlock is not an offline coding blocker. UFS rootfs and high-speed peripherals are not prerequisites for the early initramfs milestone. The seven [PHY clock warnings](GCC_PHY_CLOCK_RECLASSIFICATION.md) retain their source-based downgraded severity.

Previous queues and findings remain historical: [fifth review](FIFTH_REVIEW.md), [fifth assignments](FIFTH_ASSIGNMENTS.md). Their missing-artifact, missing-property and pending-build statements are superseded by this review.
