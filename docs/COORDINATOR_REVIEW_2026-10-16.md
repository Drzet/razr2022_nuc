# Coordinator review — 2026-10-16

## Decisions

| Delivery | Disposition |
| --- | --- |
| VPU project `29c59a2cb58559e0c00c2b5baead5bb5f8c95d32` | Consumer-policy contract accepted for the disabled development candidate, with the explicit startup limitation below. Proceed to bounded implementation. |
| Boot project `b2f9aea38b5581781e8b07aa98a85dbbeddaa237` | Loader/readiness update accepted; original kernel, DTB and diagnostic-v2 identities preserved. |
| MBM research `0acccb329521d91b84fdcfb4bf9d7dcc25f44a25` | UTF-16 and RVA-mapping correction accepted; all 12 submitted synthetic tests independently pass. |

Accepted integration remains `2b5acf108ae37040ac1e652e029bb37f5609e886`. No new kernel delivery, combined build, handset boot or working USB/DP/VPU hardware is claimed. This review selects VPU implementation and an independent DisplayPort source-contract review; Boot pauses after completion. [Current assignments](NEXT_TASKS.md).

## VPU contract review

Read the complete new consumer-policy section in the [canonical handoff](https://github.com/Drzet/razr2022_nuc/blob/29c59a2cb58559e0c00c2b5baead5bb5f8c95d32/docs/handoffs/2026-10-13-vpu-tenth-recovery.md#consumer-policy-contract--2026-10-16). Verified kernel head remains `7ac8d3afedfde74286b52e11aaa1eca42a1329a5`. Independently inspected its power, resources, VPU2 frequency, platform-capability, decoder-rate and core-lock source paths. The legacy power path skips zero-byte sessions, uses DEFAULT_FPS bandwidth, updates cached votes before provider success and uses an OPP helper with devfreq fallback; the proposed SM8475 path explicitly replaces those semantics without changing other platforms.

Accept the specified explicit reservation lifetime, checked input/aggregate admission, independent D/L sums on disjoint routes, strict OPP ceiling, provider readback, PM-before-core-lock ordering, and failure/rollback state. The existing pure calculator remains accepted; unchanged 1362-vector/3157-assertion evidence was not replayed. The new contract is documentation, not executable proof of transactions, lock ordering or HFI suppression; those require production-path tests in the selected implementation.

**Startup limitation is stronger than the handoff's 4K example.** Independently evaluated its pinned VPU2 formula with zero compressed-payload contribution:

| Format at retained 480-fps startup | Macroblocks/s | Minimum VPP demand | 444 MHz ceiling |
| --- | ---: | ---: | --- |
| 1280x720 | 1,728,000 | 362,880,000 Hz | Passes this clock check only |
| 1920x1080 (height rounded to 1088) | 3,916,800 | 822,528,000 Hz | Rejects |
| 3840x2160 | 15,552,000 | 3,265,920,000 Hz | Rejects; also exceeds core MB/s limit |

This is a computed policy restriction, not a measured hardware capability. A 720p row is not a full admission or decode guarantee. Accept the current contract as an intentionally restricted implementation target; do not advertise 1080p/4K startup support or silently lower startup to bypass rejection. A useful broader startup/rate policy is a separate future change, required before claiming general-purpose decode support. No physical divider search is reintroduced: /3 remains **[INFERRED, USER-ACCEPTED FOR DEVELOPMENT]**.

Implement the reviewed contract behind the existing disabled SM8475 gate, including input validation, committed reservations, strict clock selection, transactional ICC/OPP changes and caller errors. Cover the lifecycle, rollback and asynchronous buffer-completion cases in the handoff. Required-opps/ICC binding and test-fixture contract may be staged; Boot-owned shared DTS and enablement are excluded. Source-resolved MXC/MMCX ordering and accepted assumptions remain fixed.

The inherited IOVA reservation error behavior remains a separate active-DMA defect. Physical PAS/HFI/decode and LLCC behavior remain untested. This assignment does not approve active DMA, cache changes or probe-gate removal.

## Boot and research review

Inspected all three Boot changed-file diffs: loader/output decision, JSON readiness and canonical handoff. They preserve full Image size 53,215,232 bytes, source hashes, OR-based fallback, zero-size pre-fixup FDT memory, final-runtime uncertainties and conditional trial planning. They no longer use stock literal header addresses as actual placement. Existing host packaging remains accepted; no identical repackaging is needed. Historical payload-wait wording in the JSON is superseded by its explicit accepted v2 identities and current queue.

Inspected the complete constants-tool and synthetic-test diff. UTF-16 now terminates at aligned code units; numeric/string/GUID reads map raw-backed PE sections instead of assuming RVA=file offset. Executed the exact submitted 12-test suite locally using the three pinned script/test files; **12/12 PASS**, including both full names, nonidentity RVA, section-boundary and malformed-header/raw-bound cases. The tool is a bounded trusted-reference extractor, not a generally hardened arbitrary-PE parser.

The saved section numbers in the submitted readiness/test data place all selected RVAs within identity-mapped .text. Coordinator checked their consistency; Boot's independent artifact inspection remains attributed owner evidence, not a new coordinator download of artifact 12007666834. Corrected names were tested synthetically, not freshly decoded from original firmware. No firmware download/disassembly rerun, kernel build or device operation occurred.

Boot's assigned offline work is complete. Runtime branch/bases, final RAM/FDT/ramdisk composition and accessible early output remain observations for a separately selected phone trial. These do not block VPU software or the newly identified AUX switch review.

## Next independent source task: DisplayPort

Reference identity is **WAS7227Q-10/TR**, per [canonical schematic evidence](oneli_schematic_evidence_2026-10-15.md). The old unknown-part hold in DisplayPort head `d5b45132914f075c784c6bbb2ca2e604cd262f86` is superseded for the reference design. Installed-board correspondence remains [INFERRED]. Do not substitute AW35615 or re-enable FSA4480.

Activate only the missing exact-part reuse/binding and GPIO/connector contract. Reuse the completed stock-overlay and software truth-table work, accepted PS5169 evidence and Boot rail proposal. This source review is independent of VPU files and can run alongside its single implementation stream. No new DP driver, shared-DTS enablement or duplicated firmware extraction is selected.

## Delivery review — 2026-10-16 afternoon (current)

This section supersedes the earlier assignment disposition above.

### VPU: changes requested; implementation not accepted

Reviewed project **be103e0fc0dbedefbf647dfea46c51ad5301e501**, kernel **3086118adc521943bd533f98d53b136cf4694bc2**, against calculator base 7ac8d3af. Inspected the changed resource/admission and lifecycle paths, submitted harness and actual pinned VB2 core. Preserve the delivered commits; no rollback/history rewrite or integration promotion.

**Independent execution:** submitted production-function harness passes **52 scenarios / 2321 assertions**, including 8 update, 7 repair and 4 unvote positions. All 18 recorded production-source hashes and all three test hashes match the published JSON. Used a minimal local source snapshot with its own staging Git identity, not a full kernel checkout; pinned bytes establish provenance. No unchanged calculator-vector replay. Inspected owner-produced final ARM64 modpost/module-link log, framework imports and schema log (1 positive / 11 negative); no independent ARM64 rebuild, binary/config hash verification or Linux runtime claim.

Two blocking lifecycle findings remain:

1. **Failed STREAMON can defeat the retention strategy.** In `iris_vb2_start_streaming()`, deferred work can already have been submitted before a later queue/start failure. If CLOSE then fails, the new error path returns without returning driver-owned buffers. Actual `videobuf2-core.c::vb2_start_streaming()` forcibly completes remaining ACTIVE buffers as QUEUED after any start callback error and clears start_streaming_called. On the STREAMON path, q->streaming never becomes true. The new `iris_policy_streamoff()` then skips its STOP/CLOSE preflight because it checks only vb2_is_streaming(q), and delegates to VB2 cancellation even while resources are uncertain and CLOSE unconfirmed. `vb2_core_streamoff()` deliberately cancels even nonstreaming queues. Queue-error flags and held PM refs do not change that framework contract.
   - Coordinator executed the unchanged extracted VB2 start function under a callback mock that returns -EIO while retaining one ACTIVE buffer: VB2 forcibly completed it to QUEUED and driver-owned count became zero.
   - Separately extended a temporary copy of the submitted harness with a reserved, uncertain, unclosed instance and q.streaming=false. The assertion that `iris_policy_streamoff()` must reject without invoking cancellation **fails** on the published implementation. Existing cases test streaming=true and miss this state.
   - This establishes the framework ownership mismatch and cancellation bypass, not a physical DMA corruption experiment. Fix the actual ownership/quiescence boundary; refusing to call buffer_done from the callback alone is insufficient.

2. **Successful release erases confirmed CLOSE before file teardown.** `iris_sm8475_release()` replaces the reservation with a zero-initialized inactive struct, clearing closed. `iris_close()` then removes the session and calls `v4l2_m2m_ctx_release()`. Its streaming-queue callbacks can now enter `iris_session_streamoff()` without the closed short-circuit and attempt STOP/CLOSE for an already-closed/removed session. The final HFI membership guard rejects that session, and fault processing can affect other sessions.
   - Adding only `CHECK(inst[0].reservation.closed)` immediately after the submitted successful release case fails (check 291). The cleared state is independently executed; the subsequent whole file-release/VB2 stack is source-traced, not runtime-executed.
   - Keep definitive firmware quiescence valid across resource release and context cancellation, or restructure teardown to achieve the same ordering. Do not merely suppress the callback error.

**Next VPU task:** correct these boundaries and execute regression tests through actual framework control flow, including successful file release and nonstreaming cancellation after failed start. If a supported DMA-quiescence operation is genuinely required, identify/reuse it and report that precise dependency; do not fake successful CLOSE, arbitrarily free retained mappings or rewrite generic VB2. Existing disabled probe gate stays. This correction takes precedence over startup broadening, recovery features and IOVA enablement.

The retained failed-OPP uncertainty is an explicitly reported limitation, not newly claimed recovery. No claim that a same-old-OPP cached success repairs required domains. Existing /3 assumption remains [INFERRED, USER-ACCEPTED FOR DEVELOPMENT]; it is unrelated to these software defects.

### DisplayPort: source contract accepted

Accept project **186a7f251397c87f8a68a37afa8cf0556e579c01** for exact-part reuse/binding/graph proposal scope. Independently inspected accepted-kernel gpio-sbu-mux driver, its binding and PMIC GLINK callback order. Checked the original WILLSEMI rev1.2 p2 datasheet transcription at [manufacturer-document mirror](https://www.alldatasheet.es/html-pdf/1140435/WILLSEMI/WAS7227Q-10SLASHTR/923/2/WAS7227Q-10SLASHTR.html): OE high disconnects; SEL chooses the channel when enabled. This supports the proposed active-low enable / active-high select mapping when combined with the recorded board wiring. Installed-board correspondence remains [INFERRED].

Select existing gpio-sbu-mux reuse and a narrow future `willsemi,was7227q` compatible plus vendor-prefix addition. No new I2C/DP driver. Retained SEL on NONE is disconnected under OE high; do not assert break-before-make for live orientation swaps. Reference chip is WAS7227Q-10/TR, not AW35615; keep FSA4480 disabled.

**Confirmed integration gap:** YAML permits vcc-supply but the inspected generic driver neither acquires nor enables a regulator. Merely adding an L2B phandle cannot power U4500. L2B is also used by PTN3222, whose current request minimum differs from the stock nominal rail. Power now owns the bounded provider/voltage/lifetime source decision; generic driver reuse is accepted subject to that power contract. No board enablement or external-display hardware acceptance follows.

### Current selection

VPU remains the only implementation stream, now a targeted correction. Power performs an independent source-only USB/DP supply contract, using fixed schematic/driver/Boot inputs. DP pauses after accepted delivery; its minimal binding implementation is queued after the supply decision so the consumer contract is complete. Boot, USB, GPU and Userspace remain paused. Accepted integration and boot artifacts are unchanged.

## Evening delivery review — 2026-10-16 (current)

This section supersedes the afternoon queue. Accepted integration remains **2b5acf108ae37040ac1e652e029bb37f5609e886**; no new combined artifact or handset operation.

### VPU cleanup correction accepted for disabled development scope

Reviewed kernel **905d2403c451838a408f6bb44e80a7cf9aa6ed10**, direct child of 3086118, and project **53608e54e600a8800b665772dc5c63f5ed859c56**. Inspected all four changed Iris files and the framework harness/mocks. The SM8475 callback now commits VB2 ownership without firmware submission, and the guarded ioctl performs fallible firmware work afterward. A failed ioctl can deliberately leave VB2 streaming with retained buffers; subsequent cancellation is guarded. Legacy platforms retain the original callback path. Resource release preserves confirmed CLOSE through actual file/context teardown.

Independent host verification:
- All three named regression assertions fail on the old candidate: failed-start ownership, nonstreaming cancellation, lost CLOSE during file release.
- Corrected production-function suite: **6 framework cases / 645 assertions PASS**.
- Existing consumer suite: **52 cases / 2325 assertions PASS**.
- All **24 production source hashes and 6 harness hashes** match the published framework result after preserving exact file endings. Local review uses a minimal source snapshot and local staging Git identity, not a full kernel-history checkout.
- Inspected the ARM64 build record and incremental module log showing Iris link, MODPOST and qcom-iris.ko link. Compilation, binary/config hashes and target execution remain owner evidence; no independent ARM64 rebuild.
- External firmware/provider/allocator/scheduler boundaries remain mocks. This is executable control-flow evidence, not full Linux concurrency, hardware DMA or firmware operation.

The requested correction is accepted. Disabled gate, retained 480 startup restriction (including 1080p/4K rejection), uncertain OPP recovery, full quarantine reclamation and inherited IOVA failure limitations remain explicit. /3 remains **[INFERRED, USER-ACCEPTED FOR DEVELOPMENT]**; no new physical-proof requirement. Do not repeat the closed cleanup assignment or enable the candidate. Next VPU work is a bounded source-only Xiaomi Iris comparison.

### DisplayPort and Power disposition

Project **razr/displayport remains 186a7f251397c87f8a68a37afa8cf0556e579c01**; its kernel branch remains a5ebb76233b79db01e82e061173cb73c6d2b5c6b. No new DP implementation commit was found. Prior exact-part/graph acceptance stands.

Power project **b7d80a25a19b1a581880062463f468f1ce19f9ab** is accepted as the source contract for the next bounded AUX change. Read current report/handoff; independently checked the pinned RPMh PM8350 L2B mapping, 1.504 V + 8 mV selector grid, supply-group names and ACTIVE_ONLY writes. Current PTN request 3.075–3.300 V selects 3.080 V, versus stock initial vote 3.072 V. Accept keeping the existing request: **8 mV is not a development/integration blocker**. Exact BUK datasheet provenance remains a documentation gap, not a new mandatory search. No measured voltage or universal electrical qualification is claimed.

Use one shared L2B regulator for PTN and WAS7227Q. L2B parent is PM8350C BOB; L8C parent is PM8350C S1C. B_PLUS is variable, not a fabricated fixed 3.7 V provider. Preserve the separate later provider/board-integration decision rather than letting it block an isolated generic mux change.

Select generic gpio-sbu-mux property-present regulator support: a real supply acquired/enabled before Type-C publication, independent enable reference for the bound lifetime, disconnected GPIO state and balanced unregister/disable on failure/remove. Older nodes without vcc-supply retain behavior. Require the supply for the new WAS7227Q binding; optional regulator API must propagate lookup/enable errors and never silently substitute a dummy on a property-present node. Active-lifetime ownership does not establish full system-sleep retention. DP suspend/wake acceptance remains separate.

### Corrected Xiaomi audit: accepted research with coordinator qualifications

Read the complete current **xiaomi_pad6pro_sm8475_oneli_reuse_audit_2026-10-16.md**, saved revision modified **2026-10-16T16:59:06.607902Z**. Source pins: integration **f5a535f5c1c980f042b58cb77467ff8f02a5518e**, product kernel **fe81794b5e1b8a3f11a165f3acbfdb8fa671dbb3**, ancestor **a19585977c11fa662435b607cb9ff4ac7133092e**. Later branch heads are not substituted for product provenance.

The SVID correction is correct: both macros are 0xff01, so no extra compatibility is added. Previous independent coordinator inspection also established that oneli already decodes orientation 0/1/other as normal/reverse/none. Corrected prose still calls orientation a substantive fork change without distinguishing an internal fork regression from a missing feature in our baseline; **do not assign an orientation patch** on that basis.

The audit's oneli GPIO91-to-PS5169 wording is misleading for the accepted Linux ownership contract: **GLINK alone consumes TLMM91**, PS5169 receives Type-C notifications and owns enable GPIO19, AUX owns GPIO2/71. Preserve the current canonical DP contract over historical donor descriptions.

The report still describes Power's voltage decision as unresolved; this is superseded by b7d80a2 and the acceptance above. Its generic conclusions do not reopen BUK chip-ID or 8 mV gates.

Selected reuse:
- **DP:** compare actual PHY-before-AUX, rate reconfiguration/unwind, bounded initial DPCD retry, HPD-state versus IRQ handling, and SM8475 QMP table differences against our baseline and maintained upstream. Report already-present versus missing changes separately. Source inspection can happen before hardware; implementation beyond the selected AUX supply/binding scope needs review. Do not blindly suppress legitimate HPD IRQ service or copy fixed two-lane/RBR assumptions.
- **VPU:** compare the small sm8450 platform path and resume_without_payload option with our actual firmware/HFI/resource paths. Independently confirmed the option exists during the previous coordinator audit review. Four-pipe/vpu3_ops and borrowed bandwidth data are comparator inputs, not accepted replacements for the current VPU2 policy.
- **Boot (queued):** framebuffer/ramoops observability and final-FDT/overlay-symbol comparison methods merit a later bounded check against existing oneli exports. No Xiaomi addresses, board IDs, overlay sink, v2 boot format, partition scheme or renewed full firmware extraction.
- **USB/GPU acceptance:** distinct hardware tests for HS gadget, host, SS, hubs, Ethernet, simultaneous DP+USB, actual GPU renderer and actual V4L2 decode. Pad owner reports are not independently reproduced oneli results.
- No FSA4480, charger, Xiaomi firmware or broad fork transplant. Installed-board applicability remains [INFERRED] wherever not established by oneli evidence.

Pinned source entry points:
- [DP control](https://github.com/yzddmr6/linux-sm8450-liuqin/blob/fe81794b5e1b8a3f11a165f3acbfdb8fa671dbb3/drivers/gpu/drm/msm/dp/dp_ctrl.c), adjacent dp_display.c / dp_aux.c.
- [QMP combo](https://github.com/yzddmr6/linux-sm8450-liuqin/blob/fe81794b5e1b8a3f11a165f3acbfdb8fa671dbb3/drivers/phy/qualcomm/phy-qcom-qmp-combo.c).
- [Iris platform](https://github.com/yzddmr6/linux-sm8450-liuqin/blob/fe81794b5e1b8a3f11a165f3acbfdb8fa671dbb3/drivers/media/platform/qcom/iris/iris_platform_gen2.c), adjacent iris_hfi_gen2_command.c and iris_platform_common.h.
- [Boot symbol tool](https://github.com/yzddmr6/xiaomipad-6pro-mainline/blob/f5a535f5c1c980f042b58cb77467ff8f02a5518e/tools/lib/abl-symbols.py).

### Selected sequence

DP is the sole implementation stream: AUX binding/supply ownership plus bounded source comparison, with no DRM/QMP patch authorization. VPU performs the independent source-only Iris comparison on fixed inputs. Power stops after accepted delivery. Boot/USB/GPU/Userspace remain paused. After these deliverables, coordinator selects board staging and any justified generic DP fixes; minimal observable phone boot remains independent of VPU and external display.
