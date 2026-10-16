# Project status

Updated 2026-10-16 after [latest VPU / DP review](COORDINATOR_REVIEW_2026-10-16.md#latest-vpu--dp-delivery-review--2026-10-16-current).

**VPU source comparison accepted. DP source/host/schema evidence accepted; final ARM64 module validation pending. DP validation and Boot observability review are active. Linux has not booted on the phone.**

[Assignments](NEXT_TASKS.md) · [Policy](WORKFLOW.md) · [Branch disposition](CLEANUP_2026-10-13.md)

| Owner | Reviewed state | Next action |
| --- | --- | --- |
| VPU | Kernel 905d2403 cleanup acceptance retained; project adc83dc comparison accepted | Paused; narrow payload-free RESUME adaptation queued |
| DisplayPort | Project eb01acf / kernel 5499623 reviewed; independent 11 cases / 237 assertions and binding/equivalent-instance checks pass | Active dependency-complete ARM64 module/modpost validation; final acceptance pending |
| Power | b7d80a2 accepted source contract; 8mV L2B rounding non-blocking | Paused |
| USB | Isolated PTN3222/PS5169 acceptance retained | Paused; board integration pending |
| Boot / research | b2f9aea / 0acccb3 acceptance retained | Active source-only framebuffer/ramoops/final-FDT observability review |
| GPU / Userspace | Existing accepted evidence retained | Paused |

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886**, [integration record](../configs/accepted-integration-2026-10-12.json) and [diagnostic-v2 record](../configs/accepted-native-console-v2-2026-10-13.json) unchanged. No new combined image or working handset USB/DP/VPU claim.

## Decisions and remaining limits

- VPU now preserves VB2 ownership across failed firmware startup and confirmed CLOSE through teardown. Host production-control-flow tests pass; ARM64 link evidence inspected, not independently rebuilt. Full Linux concurrency/DMA remains untested. SM8475 stays disabled/unintegrated.
- VPU /3 is [INFERRED, USER-ACCEPTED FOR DEVELOPMENT]. Retained 480 startup rejects 1080p/4K. IOVA errors, uncertain OPP recovery and full quarantine reclamation remain separate future issues.
- Shared L2B feeds PTN3222 and WAS7227Q; keep PTN's 3.075–3.300V request, selecting 3.080V on the supported grid. The 8mV difference from the 3.072V stock initial vote is not a development blocker or a new BUK-document requirement.
- Generic gpio-sbu-mux must own its supply for the bound lifetime. Board parent-rail integration and full system-sleep retention are still separate work. No fixed 3.7V B_PLUS fiction.
- Xiaomi audit SVID correction accepted. Oneli already decodes orientation 0/1/other. Preserve GLINK-only GPIO91, PS5169 enable GPIO19, AUX GPIO2/71. No redundant SVID/orientation patch, FSA4480 or wholesale fork transplant.
- USB unknown readable chip IDs remain diagnostic; failed reads abort. Actual enumeration, DP display and wake are untested.

## Native milestone

An observable controlled boot using the accepted image composition and a verified recovery route. UART GPIO26/27 are identified; accessible pads/voltage or another early-output route remain unresolved. Existing Motorola framebuffer/ramoops and final-FDT evidence are the inputs to the active bounded observability review. Do not guess runtime addresses or copy Xiaomi memory layout.

[Canonical schematic evidence](oneli_schematic_evidence_2026-10-15.md) preserves UART, battery GPIO, rails and WAS7227Q findings. Installed-board correspondence remains [INFERRED]. VPU and external display are not prerequisites for minimal native boot.
