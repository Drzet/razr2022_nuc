# Reduced kernel build review — 2026-10-19

## Decision

Accept Boot **b34ff6d7aafd920187155d5d8d7a8c6a7e3e4bc7**, tested workflow **ada56aded6fb6d75aea8e626e7150a7e8ea2729a**, for reduced ARM64 build/package scope. No blocking finding. Assign Userspace compatibility validation; Boot pauses. Existing broad-radio and diagnostic-v2 artifacts remain unchanged.

## Independent verification

Inspected the complete build workflow and successful job **117802312561**, [run 39170486506](https://github.com/Drzet/razr2022_nuc/actions/runs/39170486506). Cheap immutable-input, tool-version, byte-identical olddefconfig and contract checks precede compilation in the same fail-fast job. Normal Image/modules/MODPOST, installation/depmod, provider export checks and three radio load-order records complete. DTB was reused, not rebuilt. The earlier malformed-expression run never compiled; the corrected run built once.

Downloaded artifact **12153785196** and independently verified ZIP SHA256 **550044f8b170d6dcaeeaec3f00ba71e3054655f651e28a806ab16ea5d44bccfb**, all **10 release manifest entries**, all **1,179 nested module hashes**, and every module's vermagic release prefix: zero mismatches. Reviewed recorded file types and release separation. No coordinator rebuild.

| Output | Verified identity |
| --- | --- |
| Kernel source | 7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce |
| Release | 7.3.0-rc6-oneli-reduced1-g7f3865ee17c3 |
| Config SHA256 | 97ee634780847771163608e353e0086eceee6347ccd42a4d9d87d04f967981be |
| Image SHA256 | 279431f997fc2334d92760d47c01aec2b8e12cf47e6d149d6a078f2347c330e8 |
| Modules archive SHA256 | 53223f163ebf1939192d85002939b4f201cff9abf7feb5160acf63c7eebbe908 |
| Reused DTB SHA256 | 70d5c7b08ddda1c0974ac85e95bb1328528bb533c344a0681b5e95b88cd17435 |

LOCALVERSION separates the new module directory from the old build despite identical source SHA. Host dependency enumeration is not execution of those modules on hardware.

## Measured results

Image falls from 52,632,064 to **36,436,480 bytes** (30.8% smaller); installed modules from 1,699 to **1,179**. Compressed module archive falls from 19,777,389 to **15,361,864 bytes**. CI job elapsed falls from approximately 47m42s to **38m17s** (9m25s shorter). The new isolated compilation record is **2231.11 seconds**. Different hosted jobs and preparation steps prevent attributing the whole timing difference solely to configuration reduction. No claim of measured boot-time or runtime memory improvement.

## Next decision

The kernel/configuration and release identifier changed, so prior QEMU results cannot establish compatibility of this build. Userspace must reuse its existing signed-regdb Debian rootfs, stage matching modules/initramfs and execute the existing early-loader and rootfs checks, combining overlapping guest assertions. Exact inputs and stop conditions are in [NEXT_TASKS](NEXT_TASKS.md). No kernel rebuild, DT rerun, firmware extraction or rootfs bootstrap.

Native oneli boot, storage, PCIe/radio and display remain untested. Firmware/hardware assumptions retain their existing [INFERRED] qualifications. VPU/DP/earlycon integration is unchanged. Other owners remain paused.
