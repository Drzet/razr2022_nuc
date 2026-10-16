# Current assignments — 2026-10-16 afternoon

Supersedes previous queues. [Review](COORDINATOR_REVIEW_2026-10-16.md#delivery-review--2026-10-16-afternoon-current) · [Status](STATUS.md) · [Policy](WORKFLOW.md).

## Active implementation: VPU — framework-aware cleanup correction

**Delivered, changes requested:** project `razr/vpu@be103e0fc0dbedefbf647dfea46c51ad5301e501`; kernel `razr/vpu-provenance-v5@3086118adc521943bd533f98d53b136cf4694bc2`. Inspect actual heads and preserve intervening work. Submitted 52 scenarios / 2321 assertions independently pass, but do not cover the blocking framework paths below.

1. Correct failed-start ownership. Actual VB2 forcibly reclaims ACTIVE buffers when start_streaming returns failure. A failed STREAMON leaves q.streaming=false, and current iris_policy_streamoff then bypasses the STOP/CLOSE preflight and calls cancellation despite an uncertain, unclosed reservation. Protect real firmware-owned memory across start failure, subsequent STREAMOFF/REQBUFS/file-close and cancellation. A queue error or PM ref is not a substitute for this ownership contract.
2. Correct normal teardown: successful iris_sm8475_release clears reservation.closed before iris_close removes the session and releases its VB2 context. Preserve definitive CLOSE/quiescence through callbacks or reorder teardown so no STOP/CLOSE is emitted for the already-closed removed session and no survivor is spuriously faulted.
3. Extend production tests to include actual VB2 start/cancel control flow and real driver callbacks, not only mocked v4l2_m2m_ioctl_streamoff. Cover partial deferred submission then error/CLOSE timeout, nonstreaming cancellation, late CLOSE, successful file release with streaming queues, retained mappings and exact-once completion, surviving sessions and PM/module/device ownership. Demonstrate fail-before/pass-after for both findings. Keep mocked provider boundaries explicit.
4. Use the smallest supported correction in Iris. If safe completion requires a missing firmware/DMA-quiescence primitive, inspect existing upstream/vendor lifecycle support and state the exact dependency before inventing recovery. No generic VB2/IOMMU rewrite, fake CLOSE success, arbitrary reset or premature freeing.
5. Preserve already-reviewed arithmetic, three-route/OPP policy, user-accepted [INFERRED] /3, conservative startup and legacy-platform behavior. No startup expansion, cache feature or broad unrelated fault campaign. Rerun changed production tests and relevant legacy cases; focused ARM64 objects/modpost/link for changed integration, no duplicate full Image build.
6. Publish exact project/kernel commits and one canonical handoff in issue #10, then stop for review.

**Unchanged boundary:** SM8475 remains disabled/unintegrated. No shared DTS, active DMA, native test or combined artifact. IOVA failure behavior, general-purpose startup and full recovery/reclamation remain separate future decisions.

## Active independent source review: Power — shared USB/DP supply contract

**Project branch:** `razr/power@1013ef56961716e6afb93321036c300a9f62cbf9`; inspect actual head first. Fixed inputs: current canonical schematic record; Boot board-contract proposal `812172869a8c9665c6a39004aad9b1c52cf036bf`; accepted integration `2b5acf108ae37040ac1e652e029bb37f5609e886`; DP handoff `186a7f251397c87f8a68a37afa8cf0556e579c01`; PTN3222 `1e5268277f6d4c25cde2f3e2b3f00439107e087a`; PS5169 `4dcbc7ba1c04afea37ab0b0caf6b4c16bfcc3dfe`.

1. Resolve the minimal RPMh producer/parent contract for shared **L2B → PTN3222 VDD3V3 and WAS7227Q VCC**, S10B, L8C→S1C, BOB and its variable B_PLUS input. Reuse existing source and new schematic; replace obsolete HDK parent assumptions. Identify exact supported binding/property/provider ownership; do not invent fixed 3.7V or phandles.
2. Reconcile schematic L2B 3.07V, vendor nominal 3.072V and PTN3222's current minimum 3.075V against actual Linux regulator ranges/steps/rounding. Deliver an exact supported constraints/request proposal or the precise missing source datum. No guessed safe voltage.
3. Choose a minimal supply-lifetime policy for AUX independent of PTN3222 session votes. gpio-sbu-mux currently ignores vcc-supply; identify whether an evidenced existing owner guarantees power through DP, detach and suspend, or propose the smallest reusable regulator-management adaptation with error/unwind semantics. Do not assume another consumer always keeps L2B on.
4. Give Boot a compact provider/consumer/voltage/lifetime table and DP a concrete binding/driver delta decision. Keep PM8350/PM8350C/PM8350BH/PM8450 distinctions and physical vs source vs [INFERRED] facts explicit.
5. Update the existing Power regulator report and canonical handoff; post exact project commit to issue #9, cross-link supply conclusion in #11/#2, then stop. No kernel/DTS changes, enablement, charger programming, new extraction, repeated GLINK audit or full build.

**Concurrency:** VPU is the sole implementation stream. Power's bounded source review has independent fixed inputs/files and resolves the next USB/DP integration dependency.

## Accepted and paused

- **DisplayPort:** project `186a7f251397c87f8a68a37afa8cf0556e579c01` accepted as source/binding/graph contract. Existing gpio-sbu-mux reuse selected; `willsemi,was7227q` and vendor prefix are queued minimal binding work after Power's supply decision. No kernel change delivered. Preserve TLMM2 active-low enable, TLMM71 active-high select; FSA4480 disabled; PS5169 has no AUX port. Installed correspondence [INFERRED].
- **USB:** prior isolated PTN3222/PS5169 acceptance stands. Unknown readable IDs remain diagnostic; no BUK allowlist prerequisite or repeated lifecycle campaign.
- **Boot/research:** b2f9aea / 0acccb3 acceptance stands. No repeated loader research or packaging. Actual runtime composition/placement and early output remain handset observations.
- **GPU / Userspace:** no changed accepted input; paused.
- **Power charger/battery implementation:** not assigned. GPIO endpoint evidence is retained; paired-pack charging policy remains separate from this supply-only task.

## Integration and coordinator

Accepted integration `2b5acf108ae37040ac1e652e029bb37f5609e886` and diagnostic-v2 images remain unchanged. Coordinator reviews corrected VPU and Power contracts before selecting subsequent binding/board work. Boot alone owns shared DTS and builds a specifically selected combined artifact. USB/DP/VPU progress is not a prerequisite for an otherwise ready minimal UART boot.

Review deliveries, update status/queue and publish issue instructions together. No blanket implementation round, automatic enablement or test replay for unchanged inputs.
