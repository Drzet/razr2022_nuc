# Current assignments — 2026-10-15

This queue supersedes earlier rounds and same-day pauses. [Policy](WORKFLOW.md) · [Status](STATUS.md) · [Current review](COORDINATOR_REVIEW_2026-10-15.md).

## Active: VPU — consumer-policy contract

Fixed inputs: project razr/vpu@0c50bf141dbb2a96cd19e79eb35e27bb1e807a63; kernel razr/vpu-provenance-v5@7ac8d3afedfde74286b52e11aaa1eca42a1329a5. Both remain latest and the pure calculator is reviewed/accepted. Inspect heads before editing; preserve later work.

**User-accepted hardware assumption:** clock consumer division by three is [INFERRED, USER-ACCEPTED FOR DEVELOPMENT]. Retain four-pipe/no-cache-discount model. Do not keep development paused awaiting physical divider proof or repeat the broad search. This does not assert measured rates or physical cache disablement.

Update the canonical VPU handoff with one implementable policy:
1. Map actual decoder controls/queued bytes, frame/operating rates and the retained480 startup rule to calculator inputs. State when votes change and what zero queued bytes means.
2. Specify admission and errors: unsupported or checked-range failure must propagate; do not continue with zero/stale votes. Raw outputs exceeding a route limit need admission rejection or a separately justified policy, not silent clamp-as-adequacy. Include the known96x8192/409 and410fps boundaries and startup effects.
3. Specify disjoint VIDEO→LLCC and LLCC→DDR votes, concurrent-session aggregation and update/rollback/unvote ordering. Avoid duplicated L on a long DDR route.
4. Map source-resolved MXC/MMCX ordering/table using the accepted /3 assumption; distinguish requested, rounded and achieved rates and failure handling. Specify bounded later code/files/tests.
5. Deliver exact project commit in issue#10 and stop for coordinator review. Reuse unchanged calculator/reference results. This task settles the consumer interface; no runtime caller, shared DTS, cache lifecycle or full build yet.

Native PAS/HFI/DMA outcomes await hardware. The inherited IOVA reservation failure behavior is an independent demonstrated source gate for active DMA; no custom IOMMU rewrite assigned. Check the relevant upstream fix/provider behavior when enablement is actually selected.

## Active independent review: Boot — incorporate MBM address contract

Inputs: research/oneli-mbm-readonly-20261015@5a8d6ab606c825dbe776db43955c44214f7c64e3; Boot handoff812172869a8c9665c6a39004aad9b1c52cf036bf; accepted kernel2b5acf108ae37040ac1e652e029bb37f5609e886 and existing diagnostic-v2 artifacts.

1. Update existing loader/output decision, readiness record and canonical handoff: static placement formulas are resolved for planning; runtime branch/base/offset, RAM fixup, final FDT/ramdisk composition and physical output remain observations. Preserve fallback alignment hazard and full Image.image_size overlap check. Do not require successful kernel entry before planning its test.
2. Repair the research constants script's UTF-16 truncation with aligned code-unit termination and synthetic cases. Check literal-section RVA mapping against saved PE metadata. Use the research branch for its tooling; Boot branch for Boot records. Preserve existing artifacts, no firmware download or broad disassembly rerun. If saved metadata is insufficient, state that exact limitation.
3. Describe the minimal future read-only observations and conditional temporary-load experiment, including alignment/overlap, selected DT/memory, observable output and restoration checks. Do not guess runtime addresses or claim fastboot-boot composition tested.
4. Post exact commits/evidence in issue#13, then stop for review. No kernel/DTS, charging, boot-image rebuild or device operation.

Concurrency is explicitly allowed: VPU's source-policy contract and Boot's independent evidence/readiness work have fixed separate inputs/files. Neither waits on the other; this is not a blanket implementation round.

## USB — accepted, paused

Project razr/usb@481c399cee777014586b083f0305614e09aa9c68; kernel razr/usb-ptn3222@1e5268277f6d4c25cde2f3e2b3f00439107e087a. Relaxed identity policy accepted after source review and independent44-scenario host pass. Unknown readable IDs are diagnostic; read errors remain fatal. No further BUK-ID allowlist search/capture prerequisite. No new USB implementation or repeated lifecycle tests.

Future Boot integration must reconcile actual PM8350C GPIO7 active-low provider/pinctrl and L2B voltage constraints/rounding before enabling supplies. Preserve S10B/L2B evidence, existing PS5169 acceptance and distinction between schematic nominal3.07V, vendor3.072V and candidate3.075V minimum. No integration assignment yet.

## Queued schematic follow-ups

- DisplayPort: exact WAS7227Q-10/TR reuse/binding/graph decision, TLMM2/71 enable/select. Keep FSA4480 disabled.
- Power: SGM41516D / PM8350BH / WS4695C-12 paired-pack ownership/polarity, CHG_EN=C GPIO2pin134, balance=BH GPIO1pin114, bridge=BH GPIO3pin139 and R909470kΩ. Also resolve variable B_PLUS representation and required RPMh producer/parent phandles without fixed3.7V fiction.
- Boot integration: after reviewed contracts, coordinator selects exact changes and one combined artifact. Boot owns shared DTS. Userspace resumes only for changed accepted input.

## Paused and coordinator responsibilities

GPU, Userspace, Power implementation and DP implementation remain paused. Accepted integration and diagnostic-v2 artifacts are unchanged. No hardware-only uncertainty blocks independent offline work.

Coordinator reviews each exact delivery, updates STATUS/NEXT_TASKS and posts the bounded next instruction together. Preserve hardware assumptions as [INFERRED] while honoring user-accepted development policy. Historical review pauses do not override this queue. GitHub instructions do not launch another chat.
