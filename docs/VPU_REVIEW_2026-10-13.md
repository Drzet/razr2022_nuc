# VPU upstream adaptation review — 2026-10-13

**Disposition: reuse direction and recorded build/schema/routing results accepted; candidate needs bounded provenance and validation closure before integration review.** No accepted kernel or board change. Do not resume the abandoned peer driver or expand to OPP/ICC.

Reviewed project `a01da16` canonical handoff; kernel `ec9a8949cfbd1b05cf01553bffc39719ee1a16a7`, relative to `869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf`. Coordinator inspected the complete source delta, test bodies, commit metadata and actual job logs. [Canonical handoff](https://github.com/Drzet/razr2022_nuc/blob/a01da16/docs/handoffs/2026-10-13-vpu-tenth-recovery.md).

## Verified progress

- Existing Qualcomm v5 common subnodes, IOMMU range support, context creation and VB2/internal/HFI routing are reused. No bespoke peer consumer driver appears in this branch. Local SM8475 changes add a nonsecure contract, conservative pixel floor, contiguous 32-bit DMA mask and an early `-EOPNOTSUPP` gate. That gate prevents handset probing, including runtime child creation; this is a disabled candidate, not functioning decode.
- Full ARM64 Image/modules/modpost, including linked qcom-iris.ko, passed at `fa89904487d4a465eb6df3f14db123d553be9502`: [run 38431204894](https://github.com/Drzet/linux/actions/runs/38431204894), job 115413530352. Overall run failed because its separate schema job failed. This distinction is accurately reported.
- Final schema/host [run 38431847444](https://github.com/Drzet/linux/actions/runs/38431847444), job 115415753529, passed at ec9a8949: enabled positive fixture, eight expected-invalid schema fixtures, 53 executable production routing-selector checks. Subsequent changes from the successful full-build source affect only workflow and fixture; no new full build is required for identical driver inputs.
- HFI/internal alloc/free and child-lifecycle checks are textual assertions, not execution. Range negatives compare fixture values to a Python constant table, not `of_iommu_derive_resv_regions`. These are useful limited checks but do not close the stated allocator/failure-path validation.

## Required closure

1. **Provenance:** five commits labelled upstream-authored (`7d7038b2`, `b8d974e5`, `6619b5ec`, `3e4c8aae`, `48606cc3`) have Git author Drzet and abbreviated replacement messages. Original-author/Message-ID links provide attribution, but original authorship and upstream trailers are not preserved as the handoff claims. The reviewed upstream context patch includes co-development, sign-off and review trailers absent here. Supply the requested source mbox/hash and a per-patch original/backport identity and conflict/delta record. Reconstruct an attributed submission series on a **new** branch without rewriting tested ec9a8949 history. Retain upstream trailers only on their legitimate source patches; never invent a personal sign-off or transfer upstream review approval to local modifications.
2. **Production range enforcement:** test the actual added IOMMU range helper (kernel test or extracted production function with explicit mocks), not a rewritten algorithm. Check the two normal window complements, malformed/zero/overflow inputs, translation and allocation-failure behavior. Pinned source currently can return no reservations if no valid ranges survive; this is not rejection of malformed input. Record inherited upstream limitations accurately and assess the intended validated-DT path; no blanket core rewrite is authorized.
3. **Child lifecycle:** exercise actual create/init/deinit control flow for absent legacy children, first/second registration failure, partial cleanup and subsequent V4L2-registration failure. Source presence/count assertions do not show error propagation or balanced node/device references. Keep provider/kernel runtime limits explicit.

If a real failure requires source changes, keep them separate from the imported patches and check current upstream fixes first. Tests must resolve the named risks; do not build a general framework or repeat a broad audit. If provenance reconstruction leaves the source tree identical, record tree equality and reuse the earlier build evidence.

## Correction to earlier coordinator reasoning

An unbound platform child is **not necessarily missing DMA configuration** in this baseline. `drivers/iommu/iommu.c::iommu_bus_notifier` handles BUS_NOTIFY_ADD_DEVICE; `iommu_init_device` invokes the bus dma_configure for an unbound device lacking fwspec, and the IOMMU probe path sets up its domain. Coordinator traced this pinned path and compared the [upstream context patch](https://lists.openwall.net/linux-kernel/2026/09/26/350). A separate driver must not be added merely to satisfy the earlier incorrect blanket statement. Actual setup failure/deferral remains a distinct behavior to assess; no handset domain success is claimed.

The [upstream range patch](https://lists.openwall.net/linux-kernel/2026/09/26/362) remains pending source to backport, not proof of faultless operation. Synthetic fixture resource placeholders are test-only and must never become board values.

## Sequencing

VPU alone closes these three concrete gaps in one handoff update. Boot/shared DTS, USB NXP work and all other streams remain queued/paused. Do not advance to resource policy or active board integration yet. Accepted integration remains `2b5acf108ae37040ac1e652e029bb37f5609e886` and diagnostic v2 is unchanged. Device PAS/HFI/DMA/decode remain deferred hardware outcomes, not prerequisites for the offline closure.

## VPU closure review and branch repair — 2026-10-14

The latest agent work did not corrupt the tested kernel branch: `razr/vpu-upstream` still points to ec9a8949 and accepted integration remains 2b5acf10. Three additional branches had distinct purposes but the handoff duplicated its closure report and still called the old implementation active. Coordinator corrected that ambiguity without resetting history.

- **Provenance accepted:** all thirteen reconstructed commit trees at f8d742ff match their corresponding historical trees locally; original author and trailers are restored on the five imports. CI [38486727933](https://github.com/Drzet/linux/actions/runs/38486727933), job 115602051003, records five matching upstream patch IDs and exact mbox hashes. Coordinator inspected the job log and commit metadata; mbox bytes were not independently downloaded.
- **Host closure accepted:** CI [38486683289](https://github.com/Drzet/linux/actions/runs/38486683289), job 115601903926, passes child lifecycle, twelve reservation cases and ten production probe/unwind scenarios. Coordinator inspected the tests and reran all three locally against corrected f8d742ff, also PASS. These extract production C and mock external APIs; no kernel bus/provider or handset result is implied.
- **Consolidation:** sole candidate `razr/vpu-provenance-v5@a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac` adds the three unchanged tests and read-only host workflow, and redirects validation filters to this branch. Drivers and bindings are unchanged. Reconstruction automation remains only in historical test branches. Existing schema/full ARM64 evidence is reused; duplicate CI skipped for the consolidation commit.
- **Historical branches:** `razr/vpu-upstream@ec9a8949` preserves original evidence; `razr/vpu-closure-tests@816b6e07` preserves test/reconstruction history; `razr/vpu-provenance-closure@228e7406` is a metadata-capture scaffold on the old base, not an incomplete replacement to merge. All are frozen by policy. No force push or branch deletion.
- **Remaining gate:** inherited malformed/failed range reservations may omit restrictions. This behavior was characterized, not repaired. SM8475 remains gated; firmware/resource policy and hardware operation remain unresolved. Closure acceptance is not integration approval. VPU pauses; queued USB research has no technical dependency on VPU.

## Enablement disposition and next source task — 2026-10-14

Retain the reviewed disabled candidate. Existing host tests demonstrate the upstream v5 missing-reservation failure behavior, not fail-closed DMA. No local IOMMU rewrite or active-DMA authorization is selected. A narrow current-source check inspected `torvalds/linux@4056b3c9d3c92ea45955641dbafeb9b960e146ef:drivers/iommu/of_iommu.c`, which lacks the helper and device iommu-ranges support; targeted series/failure searches surfaced the existing [v5 series](https://lists.openwall.net/linux-kernel/2026/09/26/358) and [v5 helper patch](https://lists.openwall.net/linux-kernel/2026/09/26/362), not a verified newer correction. This is limited coverage, not an exhaustive absence claim. Revisit that exact gate at an enablement decision.

After accepting USB lifecycle closure, coordinator activates only VPU power/OPP and ICC source-contract resolution in NEXT_TASKS. Already qualified MDT/MBN/PAS source facts and context/provenance work are not reopened. Firmware authentication/HFI remain runtime gates.

## Power/ICC source-contract review — 2026-10-14 evening

**Accepted source analysis:** project `8add1e1e055b79bb5568669d6202e2c3ab3a2376`, a single canonical-handoff change. No kernel/DT/build result is claimed. Keep the result on the owner branch at this [pinned handoff](https://github.com/Drzet/razr2022_nuc/blob/8add1e1e055b79bb5568669d6202e2c3ab3a2376/docs/handoffs/2026-10-13-vpu-tenth-recovery.md#source-contract-decision--2026-10-14); do not wholesale merge stale owner-branch policy.

Coordinator independently inspected pinned Motorola VIDEOCC RCG and Cape PLL tables, the candidate Iris MXC/MMCX order and current video-mem-only resource helper, the mainline SM8450 route graph and RPMh aggregation, and the comparator Iris2 calculation/voting bodies. Reconstructed graph routes directly from mainline node links: VIDEO→mem_noc_sf→mnoc_sf→LLCC→llcc_mc→EBI; VIDEO→LLCC and llcc_mc→EBI split without shared nodes. The vendor calculation's LLCC result includes DDR traffic, while mainline sums average requests. A long D path plus a full L path therefore double-counts the shared segment.

The 720 MHz RCG level is VDD_LOWER but Cape PLL0 skips that level and requires VDD_LOW for MXC. This supports the asymmetric parent-level vote table, not a verified consumer OPP table. Actual read-only divider and rounded-rate mapping remains missing; software scaling by three is not a divider measurement. Keep final OPP rows held.

The source decision closes the route/topology question, but does not supply a justified workload bandwidth producer. Candidate `sm8475_data` still uses the provisional SM8250 table. Next task is the exact decoder-input mapping and, only where inputs are justified, an extracted vendor-calculator host reference. No new driver, ICC provider, shared DTS, full build or active VPU is selected. No reason to repeat completed firmware/provenance work.

**Evidence boundaries:** coordinator source checks above are independent. Stock-export hashes, both-base comparison and Motorola/comparator whole-file hash equality remain the agent's reported checks; not newly rerun here. Current commit records Drzet author metadata; the user identifies the current VPU executor as the local Codex bot. Do not infer authentication identity from author metadata or rewrite the evidence to normalize it.

**Status:** source-contract task accepted; decoder producer task active. USB, Boot, Userspace, GPU, Power and DP stay paused. No functional dependency on USB; one active stream remains the resource policy. Accepted integration `2b5acf108ae37040ac1e652e029bb37f5609e886` and disabled VPU kernel candidate a1f0288d remain unchanged.

## Decoder mapping review and reference-policy selection — 2026-10-14

**Accepted:** project [3b085bb0ae3493d4ff630027b035ccbadd0fc43e](https://github.com/Drzet/razr2022_nuc/commit/3b085bb0ae3493d4ff630027b035ccbadd0fc43e), direct child of 8add1e1, changes only the canonical handoff (+60/-1). It supplies the input/output mapping and explicit missing-cache-state alternative requested by the prior task. No harness, kernel change or executable success is claimed. Stopping at the prior policy boundary was compliant.

Coordinator inspected the actual diff and independently reread the pinned comparator decoder, fixed-point helpers and dynamic-statistics/caller path, plus candidate iris_power.c and iris_utils.c. These confirm source fallback selection, independent output fields, cache-off D=L, cache-on redistribution, original rounding behavior, the current hardcoded 30-fps ICC lookup, and candidate split-mode handling for compressed as well as linear capture. Full mapping/source hashes and other file comparisons remain owner-reported where not independently repeated in this review.

**Decision:** accept the auditor's distinction and select the handoff's no-cache-discount model for focused offline extraction/testing. Set use_sys_cache false as an explicit calculation policy, CR=1 and CF=4 source fallbacks; this does not assert physical cache is disabled. The model is not a proven upper bound or safe LLCC voting policy for every real workload. Cache-aware production policy and cache lifecycle remain separately gated; they need not block reference execution.

The next assignment starts with linear split NV12/P010, explicit codec/depth fixtures and a bounded checked input domain. For the reference adapter select max(candidate frame_rate, operating_rate), retaining the candidate's 480 startup value; reject unsafe combinations rather than hiding them with a 30-fps fallback. This is an offline policy selection, not approval of production startup/performance behavior. An unchanged vendor reference can have a smaller arithmetic-safe domain than candidate hardware admission; report that distinction and any need for a later checked port.

The harness must preserve the extracted production calculation and establish preconditions for signed intermediates, fixed-point operations and output conversions. Synthetic cache-on comparisons may characterize source behavior but do not establish a runtime cache contract. Aggregation/clamp/unvote fixtures are host contract checks, not exercised ICC consumers. No tests were run for this documentation-only review; executable validation is the newly assigned deliverable.

**Sequencing:** VPU alone proceeds with the bounded reference test in NEXT_TASKS. No consumer/Boot work is commissioned. Kernel candidate a1f0288d stays disabled/unintegrated; accepted integration 2b5acf10, diagnostic artifacts, OPP evidence holds and IOVA/PAS/HFI gates are unchanged.

## Extracted reference review — 2026-10-15

**Accepted for its assigned offline scope:** [3a6729caf68aea40cfb80a4f449f067b6208b682](https://github.com/Drzet/razr2022_nuc/commit/3a6729caf68aea40cfb80a4f449f067b6208b682), five files: canonical handoff, runner, C fixtures, arithmetic/reproduction documentation and results JSON. Keep these on the owner branch; do not merge its stale coordinator policy.

Coordinator retrieved all seven pinned files through GitHub, verified them with the unchanged runner and reran the exact committed C/Python fixtures using GCC 13.3.0 with the recorded UBSan flags. **PASS: 271 checks, 21 decoder calls (18 selected-model, three synthetic cache-on), 17 pre-calculation rejections.** All source hashes, extraction records, generated reference hash, fixture/runner hashes, candidate limits and result rows match the published JSON. Compiler differs from the owner's GCC 15.2.0; both results are host execution, not ARM64/kernel/hardware execution. An initial local staging newline mismatch was rejected by the source hash gate, corrected before the successful run; original pinned bytes and code were not altered.

Source review confirms unchanged decoder-body extraction and 64-bit fixed-point helpers; explicit guards cover signed area/rate and bitrate-rounding expressions. The documented unsigned interval bounds are conservative for the fixed model and accepted envelope. UBSan alone does not prove absence of unsigned wrap. The relational/helper/boundary tests and source execution do not provide independent physical calibration. Synthetic aggregation fixtures do not execute ICC.

**Consequences:** the arithmetic restriction is real, separate from candidate admission: 96×8192 at 205 fps passes the latter but fails the floored pixel-product bound. At 204 fps its raw output is 23577000 kB/s; 3840×2160 VP9 at 241 fps yields 19229000 kB/s. Both exceed the proposed 15000000 route cap. Thus neither arithmetic correctness nor clamping establishes adequate production bandwidth. Zero queued bytes is not an unvote. D=L describes this calculation policy, not disabled physical cache or universal LLCC safety.

**Next decision:** authorize only an attributable pure checked calculator, unwired, and differential tests against the accepted reference. This addresses a demonstrated arithmetic defect rather than speculative infrastructure. Preserve exact fixed-point semantics within the old safe domain; independently validate widened cases and explicit failures. Complete the narrowly missing pending/community reuse check before creating port code. No runtime consumer, shared DTS, cache lifecycle, OPP changes or full build is assigned. Production rate/startup policy, admission/cap interaction, LLCC adequacy, inherited IOVA failures and PAS/HFI remain separate gates.

Kernel candidate a1f0288d remains disabled/unintegrated at this review; accepted integration 2b5acf10 and diagnostic artifacts are unchanged. VPU is the only active owner; USB, Boot, Userspace, GPU, Power and DP remain paused. See NEXT_TASKS for exact deliverable and stop condition.

## Checked calculator review — 2026-10-15 evening

**Accepted for the assigned pure-calculator/offline scope:** project [0c50bf141dbb2a96cd19e79eb35e27bb1e807a63](https://github.com/Drzet/razr2022_nuc/commit/0c50bf141dbb2a96cd19e79eb35e27bb1e807a63), kernel [7ac8d3afedfde74286b52e11aaa1eca42a1329a5](https://github.com/Drzet/linux/commit/7ac8d3afedfde74286b52e11aaa1eca42a1329a5), direct child of reviewed a1f0288d. This closes the pending review; it does not authorize production voting or integration.

Coordinator inspected all three new kernel source/header files, the Makefile delta, full test runner/bridge, independent Python expectations, canonical handoff and build record. The patch preserves Qualcomm attribution, separates local checked math, and adds only an unwired calculator object to the Iris object list. It changes no caller, platform data, probe gate, ICC route, DTS or firmware policy. The new object is scheduled for linking by Makefile; it is not a runtime invocation. No blocking defect was found in the bounded model, input/error handling or arithmetic adaptation.

**Independent execution:** fetched the exact three kernel files and test files via pinned GitHub reads; fetched the seven pinned reference inputs; ran the unchanged submitted host runner with GCC 13.3.0 and its warnings/UBSan flags. Because this environment used a minimal temporary source snapshot rather than a complete kernel checkout, its local Git commit is a staging identity, not 7ac8d3af. Every tested kernel/test file hash was separately compared with the published evidence and matches. No kernel checkout or ARM64 build is claimed from this host snapshot.

Results reproduce exactly:
- 1,362 vectors / 3,157 C assertions, including 20 arithmetic/API checks.
- 810 exact unchanged-reference comparisons; 398 independent unlimited-integer comparisons beyond the original reference's accepted domain.
- All 1,344 grid representability classifications; 1,208 successes, 144 range errors, 10 invalid-input errors.
- Source/test hashes, input/output stream hashes, all named results and counts match the published JSON. No compiler/UBSan diagnostics.
- Original reference verification is rerun inside the submitted harness and matches its accepted hashes/results.

Source review confirms checked products before use, checked Q16 shifts/additions, nonzero denominators, source truncation/rounding order, and zero public outputs on errors. Model validation bounds the remaining dimension/alignment additions. The independently expressed Python equations preserve integer rounding rather than comparing floating-point approximations. This validates arithmetic within the tested/declared model, not empirical coefficients or hardware bandwidth.

**Build evidence:** inspected the submitted focused ARM64 W=1 object-build record/log and ELF header identifying ELF64 AArch64 relocatable output. The recorded source hashes match the independently tested source. ARM64 compilation remains owner-produced evidence, not a coordinator rerun; binary object/configuration hashes are not newly independently verified. This is not module linkage/modpost or a full Image build. No unchanged full build was requested.

**Limits remain explicit:** 382 successful vectors exceed 15,000,000 kB/s. At 96x8192, 409 fps returns 47,271,000 kB/s; 410 fps returns a checked range error despite candidate admission. A future consumer must handle those errors and cap/admission policy before use; clamp-to-cap is not proof of adequacy. No-cache-discount D=L remains a model choice, not physical-cache disablement or validated LLCC sufficiency. OPP divider/rate, IOVA reservation errors, PAS/HFI and native runtime gates remain.

**Disposition:** retain 7ac8d3af as the reviewed disabled/unintegrated VPU candidate and 0c50bf1 as its pinned evidence. VPU pauses; no consumer or further arithmetic expansion is assigned. Activate the previously queued USB BUK/reset source-contract decision, while Boot completes its independent read-only schematic review. Their fixed inputs/files are independent; neither needs further VPU work. No new implementation stream, blanket round or dependent Userspace build. Accepted integration 2b5acf10 remains unchanged.

## User-accepted hardware assumption and next task — 2026-10-15 late

Current heads verified unchanged: project 0c50bf1 / kernel 7ac8d3af. Previous calculator acceptance stands; no test replay needed. User explicitly confirms acceptance of the hardware assumption: consumer clock division by three is **[INFERRED, USER-ACCEPTED FOR DEVELOPMENT]**, no longer an offline development gate. Retain four-pipe/no-cache-discount model without asserting physical cache disablement. The earlier blanket pause is superseded by the active consumer-policy contract in [NEXT_TASKS](NEXT_TASKS.md). Admission/errors, rate/rounding, cap handling and disjoint ICC aggregation must be specified; native PAS/HFI and inherited IOVA failure behavior remain separate. [Current coordinator review](COORDINATOR_REVIEW_2026-10-15.md).

## Consumer-policy review — 2026-10-16

Project `29c59a2cb58559e0c00c2b5baead5bb5f8c95d32` is accepted as the disabled candidate's implementation contract. Kernel remains `7ac8d3afedfde74286b52e11aaa1eca42a1329a5`; no new runtime consumer is delivered yet. Coordinator inspected the policy and pinned producer/power/resources/platform/decoder/locking source paths. [Full review](COORDINATOR_REVIEW_2026-10-16.md) records independent startup arithmetic: 1080p at retained 480 fps requires at least 822,528,000 Hz under the source estimator, above the selected 444 MHz ceiling. This restricted startup policy must be explicit; it is not a measured hardware limit or general-purpose decode acceptance.

Proceed with the bounded implementation and production-path error/rollback tests in [NEXT_TASKS](NEXT_TASKS.md). Preserve the user-accepted [INFERRED] /3 assumption, four-pipe/no-cache-discount model, disabled gate and unchanged accepted integration. No silent startup reduction, stale/clamped votes, shared DTS or active DMA. Inherited IOVA reservation failure remains independently unresolved. Prior arithmetic/build evidence is reused for unchanged inputs.
