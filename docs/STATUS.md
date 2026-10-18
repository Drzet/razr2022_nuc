# Project status

Updated 2026-10-19 after [reduced build review](COORDINATOR_REDUCED_BUILD_REVIEW_2026-10-19.md). [Assignments](NEXT_TASKS.md) · [Policy](WORKFLOW.md).

**Combined radio kernel 7f3865e is accepted for development source/build scope: Image, DTB, matching modules and dependency records pass. Userspace radio packaging and diskless early-loader QEMU tests are accepted. Prepared Debian rootfs systemd/network/DNS/module smoke now passes. The signed regulatory database correction passes focused QEMU validation with the existing kernel. VPU RESUME adaptation passes source/host/build review and remains disabled. The reduced Image/modules build is accepted; Userspace compatibility testing is active. Linux has not booted on the phone.**

| Owner | Reviewed state | Next action |
| --- | --- | --- |
| DP | Kernel d28598f; run 38987006218 host/schema and real ARM64 module/modpost PASS | Closure 2f992d1 accepted; paused |
| Boot | Kernel 7f3865e; run 39050113058 full combined build PASS | Reduced build b34ff6d / run 39170486506 accepted; paused |
| Wireless | Kernel 5d191e2 accepted; final successful result now recorded in handoff | Paused |
| Power | b8e85bb wireless map/L7E review accepted | Paused; answer concrete integration dependencies |
| USB | Project 3c949fe; CI 57d4d32 / 305bc34 accepted | Paused |
| VPU | Kernel daf47c5 / project c0a2ae9 accepted; packet tests and ARM64 build PASS | Paused; disabled/unintegrated |
| Userspace | Tested 840d53b; delivery eff19bc; run 39061160706 signed-regdb QEMU PASS | Test reduced build with existing signed-regdb rootfs; no rebuild |
| GPU/display | Kernel 5d9e2e7 isolated earlycon source/predicate/object scope accepted | Paused, default disabled; no board display activation |

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

Reduced development artifact **12153785196**, release **7.3.0-rc6-oneli-reduced1-g7f3865ee17c3**, is accepted for build/package scope. Image 36,436,480 bytes; 1,179 matching modules. It reuses kernel source 7f3865e and the accepted DTB. QEMU compatibility for this variant is pending; neither older release is replaced.
