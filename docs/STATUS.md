# Project status

Updated2026-10-15 after [MBM/VPU/USB coordinator review](COORDINATOR_REVIEW_2026-10-15.md). **VPU calculator review is complete; user-accepted hardware assumption now permits the next consumer-policy task. USB's relaxed ID policy is accepted. MBM static placement contract is accepted for planning, with runtime values still unobserved.**

[Assignments](NEXT_TASKS.md) · [Policy](WORKFLOW.md) · [Cleanup](CLEANUP_2026-10-13.md)

| Owner | Current evidence/state | Next action |
| --- | --- | --- |
| VPU | Latest kernel7ac8d3af / project0c50bf1; reviewed unwired calculator;1362 vectors/3157 assertions previously reproduced | Active consumer-policy contract; /3 hardware assumption user-accepted for development |
| USB | Kernel1e526827 / project481c399; unknown readable IDs warn/continue;44 provider scenarios independently pass | Accepted isolated scope; paused; BUK ID capture is no prerequisite |
| Boot / research | MBM5a8d6ab static placement formula; Boot8121728 schematic contract proposal | Active bounded readiness update and evidence-tool correction |
| Userspace | Debian/QEMU and diagnostic-v2 accepted | Paused |
| GPU / Power | Existing accepted integration retained | Paused; named power/provider follow-ups queued |
| DisplayPort | Reference AUX WAS7227Q-10/TR identified | Exact-part binding/graph follow-up queued |

Accepted kernel **2b5acf108ae37040ac1e652e029bb37f5609e886**, [integration record](../configs/accepted-integration-2026-10-12.json) and [diagnostic-v2 record](../configs/accepted-native-console-v2-2026-10-13.json) are unchanged. Experimental VPU/USB remain unintegrated; no new combined build or handset result.

## Decisions and remaining work

- **VPU:** no new commit beyond7ac8d3af was found. Completed [calculator review](VPU_REVIEW_2026-10-13.md#checked-calculator-review--2026-10-15-evening) stands. Clock division by three is [INFERRED, USER-ACCEPTED FOR DEVELOPMENT], no longer a prerequisite for offline progress. Rate/rounding, admission/errors, route aggregation and cap policy are the active contract task. Physical cache adequacy, PAS/HFI and inherited IOVA failure behavior are separate from that accepted assumption.
- **USB:** [review](USB_REVIEW_2026-10-14.md) now accepts the delivered diagnostic-ID policy. Failed reads still abort before tuning; reset/lifecycle semantics preserved. PM8350C GPIO7 active-low descriptor is source-resolved; L2B constraints/rounding and board providers remain future integration work.
- **MBM:** successful UEFI route uses Image.text_offset; fallback constants are0x80000/100MiB. Literal stock header addresses no longer justify a generic placement blocker. Runtime K/E/O, RAM/carveouts, DT/ramdisk selection and accessible output remain unknown. Fallback can violate alignment of the accepted text_offset=0 Image; full image_size must fit. Numeric capacity arithmetic verified. Constants extractor has a reproduced UTF-16 name-truncation defect; correction assigned, numeric values unaffected.
- **Boot:** GPIO26/27 are both qup7 despite opposite inherited TX/RX labels; no demonstrated functional mux fix is needed. Parent mapping remains a source proposal, with missing producer phandles and variable B_PLUS ownership explicitly retained.

## Schematic evidence

[Canonical record](oneli_schematic_evidence_2026-10-15.md) preserves auditor/user transcription of the reference design; installed-PVT correspondence remains [INFERRED].

- U1720 PTN3222BUK, I2C0x4f, S10B/L2B, PM8350C GPIO7 active-low reset. Unknown-ID allowlist hold removed.
- U4500 WAS7227Q-10/TR AUX; TLMM2/71 software mapping.
- PM8350/PM8350C input groups and B_PLUS/BOB topology recorded; use the reviewed proposal before shared-DTS changes.
- SGM41516D flip charger, PM8350BH main controller, WS4695C-12 bridge. CHG_EN=C GPIO2pin134; balance=BH GPIO1pin114; bridge=BH GPIO3pin139; R909470kΩ.
- UART TX=SM8475 GPIO26/D24, RX=GPIO27/C24; physical pads/connector and voltage unknown.

Current queue selects VPU policy plus independent Boot evidence work. DP/Power follow-ups remain queued. No repeated full build or unchanged firmware extraction.
