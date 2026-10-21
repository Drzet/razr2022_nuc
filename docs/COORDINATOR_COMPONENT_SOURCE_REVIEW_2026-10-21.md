# Coordinator component-acquisition review — 2026-10-21

Delivery **d6b21609fd549c44614194c8b137f88072bb7178** accepted for bounded static evidence and a packaging recommendation. No hardware or executable-route acceptance.

Coordinator independently downloaded artifact **12364725668** and verified ZIP SHA256 **32a0eecd53eda4ec6cb6dadcb3cd2364760502a4b6f8eb2a53ec2cb780a8fc68** plus all four member hashes against the report. Inspected recorded **0x4f0d8** coverage (750 instruction instances, ending 0x5033c), indirect-call sites, the bit-2 branch at **0x4f28c** and protocol indirect call at **0x5c05c**. This is a focused spot-check, not independent reconstruction of every callback or validation of automated function boundaries.

Run **39638655285**, job **119356074070**, failed the coverage assertion after output generation. The artifact contains four analysis files, not a completed CI identity/SHA256SUMS stage. Member hashes were calculated independently against the report. The corrected assertion was not rerun; do not claim CI PASS. Automated CFG overreach and the external generic tail are documented, so graph size is not semantic proof.

The report's libavb identification and flag interpretation narrow the problem; a NO_VBMETA_PARTITION interpretation does not imply no storage reads. Motorola callback registration and the downloaded-buffer mapping remain unresolved. Legacy header/embedded-DTB evidence is sufficient to justify a reversible offline v2 experiment candidate, not to guarantee its acceptance.

**Decision:** select one self-contained v2 packaging task using unchanged accepted kernel, ramdisk and DTB. Stop incremental disassembly as the active stream; no additional trace is assigned. The unknown callback and firmware DT behavior become explicit observations for the proposed later RAM-only trial. No prior successful Linux boot is required to plan that trial.

Stock vendor_boot stays untouched. The current split-v4 pair remains archived/accepted for offline scope; inactive-slot installation is not selected. Boot alone prepares the new package and proposed runbook, then coordinator reviews before device execution. Other agents remain paused.

[Boot findings](https://github.com/Drzet/razr2022_nuc/blob/d6b21609fd549c44614194c8b137f88072bb7178/docs/oneli-reduced-native-diag-launch-decision-2026-10-21.md).
