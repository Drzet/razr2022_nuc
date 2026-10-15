# Project status

Updated 2026-10-15 after review of VPU reference commit `3a6729c`. **The bounded no-cache-discount reference is accepted: independent execution reproduced 271 checks, 21 decoder calls and all published result rows. VPU delivered the unwired checked calculator: project `0c50bf1`, kernel `7ac8d3af`; pending coordinator review, agent paused. Production voting and handset operation remain unapproved.** USB lifecycle closure remains accepted and paused; accepted integration is unchanged.

[Assignments](NEXT_TASKS.md) · [Policy](WORKFLOW.md) · [Cleanup and branch disposition](CLEANUP_2026-10-13.md)

| Owner | Current evidence/state | Next action |
| --- | --- | --- |
| VPU | Delivered project `0c50bf141dbb2a96cd19e79eb35e27bb1e807a63` and kernel `7ac8d3afedfde74286b52e11aaa1eca42a1329a5`; prior reviewed base a1f0288d | Pending coordinator review; VPU paused. Earlier reference 3a6729c remains accepted; new implementation/tests not yet accepted |
| USB | PS5169 ARM64 build passed at 8356706; conditional-schema/probe tests passed at 4dcbc7b, fixing a real YAML bug | PTN3222 correction accepted at 61202a82; pause for board/ABI/hardware gates |
| Boot | Host artifacts accepted; schematic reports debug UART GPIO26/27 and PMIC parent wiring | Active read-only board-contract reconciliation; no build or DTS changes |
| Userspace | Project-kernel Debian/QEMU and diagnostic v2 tests accepted | Pause |
| GPU / Power | Existing narrow fixes and accepted integration retained | Pause |
| DisplayPort | Reference AUX IC identified as WAS7227Q-10/TR | Exact-part reuse/binding/graph review queued; runtime untested |

Accepted kernel `2b5acf108ae37040ac1e652e029bb37f5609e886`, [integration record](../configs/accepted-integration-2026-10-12.json), and [diagnostic v2 record](../configs/accepted-native-console-v2-2026-10-13.json) are unchanged. Experimental USB/VPU remain excluded. No new combined build or image is needed for this cleanup.

Native loader/memory/DT/ramdisk handoff and accessible output remain unresolved. VPU PAS/HFI/DMA/decode and USB powered link/wake behavior require device validation. Reference-schematic NXP/AUX identities and PM8350/PM8350C parent wiring are now documented; exact installed-PVT correspondence and Linux binding/provider reconciliation remain separate.

Latest decision: [VPU candidate review](VPU_REVIEW_2026-10-13.md). VPU checked calculator has been delivered and awaits coordinator review; no VPU implementation remains assigned. Boot has a bounded independent read-only schematic/board-contract review. Provider/order and parent-level votes are resolved; disjoint DDR/LLCC routes avoid double counting. USB, DisplayPort and Power follow-ups are queued; GPU/Userspace remain paused. Inherited VPU IOVA failure behavior remains an enablement gate; no new IOMMU implementation is assigned. No unchanged full build is requested.

Latest USB decision: [PTN3222 review](USB_REVIEW_2026-10-14.md). Keep project evidence at 63cf2a53 and corrected isolated kernel candidate 61202a82; source/host evidence does not establish handset operation. No rollback or merged integration change.

## Schematic evidence update — 2026-10-15 evening

[Canonical schematic record](oneli_schematic_evidence_2026-10-15.md) preserves the auditor's findings plus the user's endpoint correction. Evidence is auditor/user-transcribed reference design, not independent coordinator inspection of the full drawing or handset validation.

- U1720 **PTN3222BUK**, I2C 0x4f, S10B/L2B supplies, active-low reset on PM8350C GPIO7. BUK ID-check compatibility remains a focused USB question.
- U4500 **WAS7227Q-10/TR** AUX switch; GPIO2/71 software mapping already known. The unknown-AUX-part hold is superseded.
- PM8350/PM8350C regulator input groups, B_PLUS and BOB topology recorded; replace conflicting HDK assumptions only after binding/provider reconciliation.
- Flip charger **SGM41516D**, main **PM8350BH**, bridge switch **WS4695C-12**. **CHG_EN=C GPIO2 pin134**, correcting auditor GPIO1; balance=BH GPIO1 pin114; battery bridge=BH GPIO3 pin139; R909 pull-down 470kΩ.
- Debug UART: TX=SM8475 GPIO26 ball D24; RX=GPIO27 ball C24. Test points/connector and voltage remain unknown; current UART7 mapping needs source comparison.

The schematic documentation update itself made no kernel change, hardware enablement, new build or altered accepted artifact. The separately delivered VPU kernel change is pending review. Boot review is active; USB→DP→Power follow-ups are explicitly queued, not an all-agent round.
