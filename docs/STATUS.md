# Project status

Updated 2026-10-17 after [Wireless/Boot delivery review](COORDINATOR_REVIEW_2026-10-17.md). [Assignments](NEXT_TASKS.md) · [Policy](WORKFLOW.md).

**Boot's disabled wireless board/configuration staging is accepted. Wireless's shared antenna-supply implementation is reviewed, but final ARM64 validation failed on an incorrect CI symbol assertion before module link. Correct that gate, then review the completed link before selecting enabled integration. Linux has not booted on the phone.**

| Owner | Reviewed state | Next action |
| --- | --- | --- |
| DP | Kernel d28598f; run 38987006218 host/schema and real ARM64 module/modpost PASS | Final handoff documentation only, then pause |
| Boot | Project 37dba10; kernel 5d261b4 disabled wireless staging accepted; run 39026414041 PASS | Paused at accepted staging; combined integration follows Wireless acceptance |
| Wireless | Project e5176e1; kernel 3b674aa reviewed; cheap tests PASS; ARM64 run 39016225711 FAILED before module link | Correct inline-function export assertion; complete real module/modpost evidence |
| Power | b8e85bb wireless map/L7E review accepted | Paused; answer concrete integration dependencies |
| USB | Project 3c949fe; CI 57d4d32 / 305bc34 accepted | Paused |
| VPU | Project ac293ee; workflow-only c318805 accepted; production 905d2403 acceptance retained | Paused; RESUME adaptation queued |
| GPU / Userspace | Prior acceptance unchanged | Paused; Userspace awaits selected kernel contract |

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886**, [integration manifest](../configs/accepted-integration-2026-10-12.json) and [diagnostic-v2 manifest](../configs/accepted-native-console-v2-2026-10-13.json) unchanged. Branch acceptance is not integration promotion.

## Remaining work and qualifications

- Wireless branch implements optional WCN6855 vddasd in the existing common regulator sequence. Host coverage uses mocked regulator/shared-consumer accounting; it is not kernel lifetime or hardware proof. ARM64 vmlinux built, but CI incorrectly requires exported of_parse_phandle (an inline wrapper). Module link remains unverified.
- Boot has encoded deliberate active radio voltage envelopes and verified supported selectors in disabled staging. Low stock initial voltage is not itself a fault. Parent mapping and installed hardware compatibility retain [INFERRED] labels where based on reference evidence.
- Normal Linux drivers select firmware revisions; physical PCI/HCI identity and missing board-data entries are runtime checks, not requirements before disabled staging.
- SWCTRL GPIO82 is not actively consumed by current upstream PMU; do not invent output behavior. Preserve diagnostic UART7 and established USB/DP pins.
- DP source/build acceptance does not establish external-display operation, board power or sleep/wake.
- VPU remains disabled/unintegrated. /3 is [INFERRED, USER-ACCEPTED FOR DEVELOPMENT]; retained 480-fps startup limits, IOVA errors, uncertain OPP recovery and reclamation remain explicit.
- Shared USB/DP L2B and PTN 3.080V selector result remain accepted; 8mV rounding is non-blocking. No new BUK chip-ID gate.
- UART7 is the best evidenced early-output route, conditional on physical access/logic level. Stock splash/ramoops reservations are not working consoles; live memory/retention/readback remain untested. No repeated broad bootloader research is selected.

[Canonical schematic evidence](oneli_schematic_evidence_2026-10-15.md) remains authoritative. No phone Linux execution, wireless association, BT pairing or DP display result is claimed.
