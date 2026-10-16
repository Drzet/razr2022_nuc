# Current assignments — 2026-10-16

Supersedes earlier queues and dated review task-selection statements. [Review](COORDINATOR_REVIEW_2026-10-16.md) · [Status](STATUS.md) · [Policy](WORKFLOW.md).

## Active implementation: VPU — implement reviewed consumer policy

**Inputs:** project `razr/vpu@29c59a2cb58559e0c00c2b5baead5bb5f8c95d32`; kernel `razr/vpu-provenance-v5@7ac8d3afedfde74286b52e11aaa1eca42a1329a5`. Inspect actual heads and preserve intervening work. The full consumer-policy section in the pinned canonical handoff is accepted with this review's explicit startup limitation.

1. Implement SM8475-specific input adapter and checked frequency/admission calculations using the accepted pure calculator. Preserve per-session reserved/error state and outstanding work; zero bytes are not inactivity. Propagate invalid/range/over-cap errors before dispatch. No upper clamp, stale-vote fallback or reuse of the SM8250 table for this profile.
2. Implement the three-path CNOC/L/D contract and strict four-row OPP selection, required-domain order, requested/rounded/readback checks and rollback. Keep clock division by three **[INFERRED, USER-ACCEPTED FOR DEVELOPMENT]**; no new physical-divider prerequisite. Do not guess MVS0C division.
3. Wire the reviewed streaming/enqueue/deferred/DRC/PM error paths. Preserve lock order, PM references, committed versus applied state, survivor reservations and exact-once buffer completion. Failed/uncertain rollback blocks dispatch and retains resources pending explicit recovery.
4. Limit production edits to the Iris adapters/resources/state and adjacent caller/resume files named in the accepted handoff, plus necessary binding descriptions/constraints and disabled test fixtures. Reuse existing Linux frameworks; no generic ICC/IOMMU rewrite, new controls, cache lifecycle or arithmetic-domain expansion. Keep other platforms' behavior unchanged.
5. Retain startup 480 in this implementation. Explicitly test **1080p startup clock rejection** as well as 4K and the 409/410-fps narrow-frame boundaries. Do not describe the resulting restricted candidate as general-purpose video support. Broader startup policy is a later reviewed change.
6. Execute production-path host tests for adapter, admission, aggregate/session lifetime, strict OPP, partial provider failure/rollback/unvote, no-dispatch on error and PM/buffer ownership. Include legacy-platform regression coverage. Reuse unchanged calculator/reference vectors. Run focused schema/fixture tests for changed binding and ARM64 compilation plus module/modpost linkage for changed objects/dependencies; no duplicate full Image build merely to retest the same scope.
7. Publish exact kernel/project commits, commands/results and one canonical handoff to issue #10. Stop for coordinator review.

**Hard scope boundary:** retain disabled SM8475 probe gate and accepted integration. No Boot-owned shared SoC/board DTS, native trial, active DMA or combined artifact. IOVA reservation failure remains a separate source issue to address before enablement; PAS/HFI and hardware behavior remain untested.

## Active independent review: DisplayPort — exact AUX switch contract

**Project branch:** `razr/displayport@d5b45132914f075c784c6bbb2ca2e604cd262f86`, inspect before editing. Use accepted kernel `2b5acf108ae37040ac1e652e029bb37f5609e886`, canonical schematic record, completed stock four-overlay AUX matrix, reviewed USB PS5169 `4dcbc7ba1c04afea37ab0b0caf6b4c16bfcc3dfe`, and Boot board-contract proposal at `812172869a8c9665c6a39004aad9b1c52cf036bf`.

1. Replace obsolete unknown-reference-part hold with **U4500 WAS7227Q-10/TR**, keeping installed-board correspondence [INFERRED]. Use the actual schematic record, not AW35615 recollections. Keep FSA4480 disabled.
2. Check current upstream/pending/community gpio-sbu-mux support and attributable exact-part information only for the missing match. Decide existing binding/driver reuse versus the minimum evidenced compatible addition. No guessed compatible or new I2C driver.
3. Reconcile physical OE_N/SEL with existing stock outputs: disconnected(1,0), CC1(0,0), CC2(0,1), TLMM2/71. Specify descriptor polarity, NONE/orientation transition behavior, enable/select ordering and L2B supply ownership; separate proven requirements from [INFERRED] behavior.
4. Produce one precise AUX/PS5169/QMP/connector graph and ownership proposal consistent with existing Linux interfaces. Account for PS5169 having no AUX port and avoid duplicate orientation GPIO ownership. List only remaining implementation dependencies, including unresolved supply providers.
5. Update canonical DP handoff and exact-part evidence in place. Post exact project commit to issue #11 (graph interface also #3), then stop for review. No kernel/DTS edit, driver, board enablement, full build, repeated stock-property audit or firmware extraction.

**Concurrency:** VPU is the sole implementation stream. DP is an independent bounded source review with fixed inputs and separate files; resolving the newly identified AUX part advances external-display work while VPU implements its settled policy.

## Completed and paused

- **Boot:** `b2f9aea38b5581781e8b07aa98a85dbbeddaa237` accepted. Research `0acccb329521d91b84fdcfb4bf9d7dcc25f44a25` accepted; coordinator independently reproduced 12/12 synthetic tests. No repeated decoder correction, loader formula research, packaging or build. Runtime observations remain for a selected handset trial, not a blanket offline blocker.
- **USB:** project `481c399cee777014586b083f0305614e09aa9c68`, PTN3222 kernel `1e5268277f6d4c25cde2f3e2b3f00439107e087a` accepted in isolated scope. Unknown readable IDs warn/continue; failed reads remain errors. No BUK allowlist proof prerequisite. GPIO7 provider/pinctrl and L2B constraint/rounding remain integration work.
- **Userspace/GPU:** unchanged accepted evidence; resume only for changed inputs or a named defect.
- **Power:** queued variable B_PLUS/provider-parent representation and paired-pack polarity/ownership task; no charger enablement.

## Subsequent integration

After exact driver/binding/producer contracts are reviewed, coordinator assigns Boot the specific shared-DTS changes and one combined artifact. VPU, USB and DP are not prerequisites for a minimal UART boot merely because they are being developed. Userspace consumes a changed artifact only after its interface is fixed.

Before active VPU DMA, review a supported resolution of inherited IOVA reservation failure; do not substitute model-test success for that fix. Before a handset trial, select the actual image composition, recovery and observable output arrangements; successful kernel entry is an outcome, not a prerequisite for planning.

Coordinator reviews deliveries and publishes status, queue and issue instructions in one pass. No blanket agent round, unchanged test replay or speculative enablement.
