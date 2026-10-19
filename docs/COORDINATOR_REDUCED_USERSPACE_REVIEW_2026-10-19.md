# Reduced Userspace compatibility review — 2026-10-19

## Decision

Accept tested source **c1b8f0aafde4133553308316dcc38f9620308873** and handoff **b82a4f1b32a0be81bf8f47a82a32d7dcdea435f1** for the assigned reduced-kernel/rootfs QEMU compatibility scope. No blocking finding. Userspace pauses. Select the previously documented production earlycon parser/rendering test gap as the next bounded offline task for GPU/display.

## Source and evidence review

Inspected all five new consumer/staging/preparation/guest/workflow files. Producer validation pins Image/config/modules/DTB and release identity, verifies all module digests and entry-point dependency closure, and reuses the accepted early cpio builder. Rootfs staging replaces only the old module tree and indexes in the signed-regdb parent; no apt/bootstrap or firmware extraction. The disposable QEMU wrapper substitutes the explicit new profile into the existing preparer and verifies original literals remain present before substitution. These substitutions are deliberately profile-specific, not a general configuration framework.

The combined guest positively checks systemd, exact release/only matching module directory, early pre-power presence, actual ath11k_pci and hci_uart loading, D-Bus/NM/IP/route/DNS, and successful signed-regdb reload. Failure counters and host-side failure-marker/exit checks prevent unrelated successful markers from masking a failure. BlueZ inactive without a QEMU adapter is correctly scoped as unit availability, not Bluetooth functionality.

Independently checked successful jobs **118011304092** and **118011342128** in [run 39237882830](https://github.com/Drzet/razr2022_nuc/actions/runs/39237882830). Downloaded evidence artifact **12180445735**, verified ZIP SHA256 **8c9ca5b0a2fd08294014f5678abafb9764da638e21822346881b0ceb8ddd56ac**, all **31 runtime manifest entries** and **3 early archive entries**. Read both actual serial logs and exit-code files: diskless early module insertion and combined Debian guest passed, both exit 0 and orderly poweroff. Guest reports zero failures, both radio entry-point modules present and positive kernel signed-regdb acceptance. No coordinator QEMU rerun.

| Artifact | Identity |
| --- | --- |
| Kernel producer | 12153785196, source 7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce |
| Running release | 7.3.0-rc6-oneli-reduced1-g7f3865ee17c3 |
| Rootfs | 12180241062; tar SHA256 d83f787677df38656c6df0a16002d98c3a93910aa717db6d7ad84b1ed80301fb |
| Rootfs ZIP | 1a0925aa0c80a6f25fa92325c234392f886b771e0bc99212eb4eb458d9be339c |
| Early gzip | 875eb0a1b0f63dbecaefb5160775da01bd8a3bc445ca1eb016effe3717875b7c |
| Diskless serial | 4a3df483c5769c8c14522ef4c0e4225ca4a1df272a95a057791d44340aa6f131 |
| Debian serial | 0649cd63e0cfd105e0de31f1e2c5cf550bfc52cd36f25ba56574aadd6e98f5e9 |

Rootfs ZIP/tar inventory verification is owner-reported; coordinator independently downloaded and verified the evidence/early archive, not the large rootfs ZIP. The hashed evidence manifest records the new rootfs identity. Prior independent kernel/module producer verification remains valid.

## Scope and next assignment

This closes reduced-build software compatibility. QEMU virt does not exercise oneli's DT, bootloader, real PCI power sequencing, firmware/controller attachment, WLAN association or Bluetooth pairing. Native root storage and first hardware boot remain unresolved; no device-ready promotion or flashing is assigned. Existing broad and diagnostic-v2 releases remain unchanged.

The isolated earlycon port still lacks real flattened-DT parser and production renderer execution coverage. Source inspection confirms its actual scanner, drawing and mapping transitions can be targeted without handset access. Select that concrete test task on the existing display branch, preserving default-disabled behavior. Reuse previous object compilation unless production code changes. Do not invent oneli framebuffer geometry or enable display hardware. [NEXT_TASKS](NEXT_TASKS.md) contains exact scope and inputs; all other owners pause.
