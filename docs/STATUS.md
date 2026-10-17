# Project status

Updated 2026-10-17 after [Wireless/Boot delivery review](COORDINATOR_REVIEW_2026-10-17.md). [Assignments](NEXT_TASKS.md) · [Policy](WORKFLOW.md).

**Combined radio kernel 7f3865e is accepted for development source/build scope: Image, DTB, matching modules and dependency records pass. Userspace radio packaging and diskless early-loader QEMU tests are accepted. The prepared Debian rootfs awaits its own systemd/service smoke test. Linux has not booted on the phone.**

| Owner | Reviewed state | Next action |
| --- | --- | --- |
| DP | Kernel d28598f; run 38987006218 host/schema and real ARM64 module/modpost PASS | Final handoff documentation only, then pause |
| Boot | Kernel 7f3865e; run 39050113058 full combined build PASS | Update stale handoff/readiness; no rebuild, then pause |
| Wireless | Kernel 5d191e2 accepted; final successful result now recorded in handoff | Paused |
| Power | b8e85bb wireless map/L7E review accepted | Paused; answer concrete integration dependencies |
| USB | Project 3c949fe; CI 57d4d32 / 305bc34 accepted | Paused |
| VPU | Project ac293ee; workflow-only c318805 accepted; production 905d2403 acceptance retained | Paused; RESUME adaptation queued |
| Userspace | Source 8f54a67; delivery 8aedb72; run 39056127007 packaging and diskless QEMU PASS | Boot existing prepared rootfs in QEMU; no kernel/rootfs rebuild |
| GPU/display | Internal-display audit reviewed; generic earlycon source inspected | Isolated default-disabled earlycon port/review; no board display enablement |

Accepted legacy diagnostic integration **2b5acf108ae37040ac1e652e029bb37f5609e886**, [integration manifest](../configs/accepted-integration-2026-10-12.json) and [diagnostic-v2 manifest](../configs/accepted-native-console-v2-2026-10-13.json) unchanged. New radio development build **7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce**, artifact **12109240146**, is accepted for Userspace consumption; it does not replace the packaged diagnostic-v2 release.

## Remaining work and qualifications

- Wireless branch implements optional WCN6855 vddasd in the existing common regulator sequence. Host coverage uses mocked regulator/shared-consumer accounting; it is not kernel lifetime or hardware proof. The incorrect inline-function export assertion is corrected; actual ARM64 module link/MODPOST passes. Runtime lifetime and hardware behavior remain untested.
- Boot has enabled the reviewed radio paths with deliberate voltage envelopes and supported selectors; unrelated UFS-only outputs remain disabled. Low stock initial voltage is not itself a fault. Parent mapping and installed hardware compatibility retain [INFERRED] labels where based on reference evidence.
- Normal Linux drivers select firmware revisions; physical PCI/HCI identity and missing board-data entries are runtime checks, not requirements before disabled staging.
- SWCTRL GPIO82 is not actively consumed by current upstream PMU; do not invent output behavior. Preserve diagnostic UART7 and established USB/DP pins.
- DP source/build acceptance does not establish external-display operation, board power or sleep/wake.
- VPU remains disabled/unintegrated. /3 is [INFERRED, USER-ACCEPTED FOR DEVELOPMENT]; retained 480-fps startup limits, IOVA errors, uncertain OPP recovery and reclamation remain explicit.
- Shared USB/DP L2B and PTN 3.080V selector result remain accepted; 8mV rounding is non-blocking. No new BUK chip-ID gate.
- UART7 is the best evidenced early-output route, conditional on physical access/logic level. Stock splash/ramoops reservations are not working consoles; live memory/retention/readback remain untested. No repeated broad bootloader research is selected.

[Canonical schematic evidence](oneli_schematic_evidence_2026-10-15.md) remains authoritative. No phone Linux execution, wireless association, BT pairing or DP display result is claimed.
