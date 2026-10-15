# USB PTN3222 review — 2026-10-14

**Latest disposition:** lifecycle correction at 61202a82 accepted for the assigned offline scope; see closure below. Earlier findings remain as historical before-fix evidence. USB is paused, not integrated.

## Initial disposition

Keep the reuse decision `fe6a73f769bb193988ce256066a2168b6940a85d`, tests/build record `acdc3f59e42e5a7fffd3e7770e513c814598182e`, and handoff `2b64829bd78478a89e18d5bd50952f7a72e3f0c5` on project `razr/usb`. Keep kernel `razr/usb-ptn3222@d513929e8c1ef2ea7f5158ebfb57fda99ff531e9` as an isolated experimental adaptation; **request lifecycle corrections before candidate acceptance/integration**. No reset, deletion or wholesale owner-branch merge. Existing PS5169 candidate and accepted integration 2b5acf10 remain unchanged.

The owner-directed offline adaptation reported in the handoff superseded the decision-only task; this is not rejected merely because that queue was older. Reuse of the existing PTN3222 provider is the selected engineering direction. Populated silicon remains [INFERRED]; identity and board wiring are separate from permission to develop and test offline. The experimental named profile is retained for iteration, not accepted as an upstream ABI. Do not redesign it or add a second implementation during lifecycle closure.

## Independently checked evidence

- Inspected all three changed kernel files: PTN3222 provider, REGMAP_I2C Kconfig selection, and opt-in binding. Changes remain isolated from shared DTS and other subsystem branches.
- Inspected production-driver tests, actual schema validation script, and committed build log. The log contains MODPOST, PTN3222/SNPS/regmap module links and Image output. This is the reported reduced tinyconfig ARM64 build, not an oneli/combined build. Binary hashes and the local f499a099-to-published d513929 tree mapping are owner-reported; coordinator did not retrieve the local commit or binary archive.
- Reran the submitted production host tests against published d513929 source: **37 scenarios PASS** with ASan/UBSan and leak detection disabled. This environment cannot run LeakSanitizer (`/proc` task inspection fails); the owner's leak-enabled pass remains separately reported.
- Inspected the 2-positive/7-negative schema test and recorded diagnostics; no duplicate schema/tool installation or ARM64 build was needed for this review. No new hardware or chip emulation result.

## Blocking source defect: failed-init cleanup is not recoverable through PHY core

At baseline a5ebb762, `drivers/phy/phy-core.c::phy_init()` increments `init_count` only after successful provider initialization. `phy_exit()` calls the provider exit callback only when `init_count == 1`. Calling provider `.exit()` directly is not equivalent to recovery through this interface.

In d513929, a tuning/init error followed by a transient regulator cleanup failure sets `faulted`. Every later provider `.init()` returns `-EBUSY` immediately, without retrying pending cleanup. SNPS's init failure path skips repeater exit, as expected after failed init. Therefore transient cleanup failure leaves no recovery through a normal repeated `phy_init()`; teardown/reprobe is currently required.

**Coordinator executable reproduction:** compile the submitted production driver/mock harness together with the unchanged production `phy_init()` body from a5ebb762 (only function name changed for host isolation). Set the harness's `fail_at=9` (first tuning write) and `disable_fail=1`. First core init returns `-EIO`, `init_count` stays zero, both votes remain and `faulted` is set. Remove faults and retry core init: returns `-EBUSY`, count remains zero and both votes remain. This reproduces the defect with real core control flow under scoped provider mocks; it is not handset execution.

The existing test instead calls `ptn3222_exit()` directly and declares recovery. Retain that unit-level coverage but stop treating it as consumer-reachable recovery.

## Related boundary to test in the same bounded correction

SNPS normal exit ignores repeater `phy_exit()` errors and returns success. The repeater core retains `init_count == 1` when provider exit fails. A later repeater `phy_init()` can then increment the count without invoking provider init, while the provider has reset asserted/faulted. This is an inspected source path, not yet an executed coordinator reproduction. Test it explicitly before claiming reconnect recovery. Also retain the powered-role rollback path and distinguish provider error handling from SNPS/DWC3 propagation.

USB may make only the minimal adjacent SNPS error-propagation/unwind change demonstrated necessary by these tests; no generic PHY core rewrite or broad DWC3 changes. Normal successful flows and legacy profile-absent behavior must remain covered.

## Next action and hardware boundary

USB remains the sole active stream for this narrow correction, with exact assignment in NEXT_TASKS. Require actual core-dispatched retry tests, balanced counts/votes, retained original errors and no falsely successful initialization with reset asserted. Then review once and decide whether the candidate can pause for hardware/ABI/board-contract work.

Phone validation remains outstanding for populated ID/effective DT, GPIO7 function/polarity, rail parents/physical transitions, enumeration and wake. These do not block the identified software correction. VPU policy work remains queued, and Boot/Userspace have no changed accepted input.

Canonical evidence: [USB handoff](https://github.com/Drzet/razr2022_nuc/blob/2b64829bd78478a89e18d5bd50952f7a72e3f0c5/docs/handoffs/2026-10-13-usb-tenth-round.md), [build record](https://github.com/Drzet/razr2022_nuc/blob/2b64829bd78478a89e18d5bd50952f7a72e3f0c5/tests/results/2026-10-14-usb-ptn3222-offline.md), [kernel candidate](https://github.com/Drzet/linux/commit/d513929e8c1ef2ea7f5158ebfb57fda99ff531e9).

## Lifecycle closure accepted — 2026-10-14, second review

**Reviewed kernel:** `61202a82ad004302fcc04e321075e190f00b29ed`, direct child of d513929e on `razr/usb-ptn3222`. Project evidence `835b06ed2c31811bc99c676497d7384c33253652`; canonical handoff `63cf2a5388ad406e58ccf42344936f14c3868a54`. Retain these commits and the original reuse/adaptation work. No reset or integration merge.

The correction changes only PTN3222 pending-cleanup retry and adjacent SNPS repeater-reference ownership (37 added, 4 removed lines). PTN3222 retries recorded cleanup before new votes; a persistent error remains an error. SNPS retains its owned repeater reference after failed exit/unwind and drains it before reconnect. Its own completed teardown returns success so outer PHY init dispatch can run again; merely returning the inner exit error would retain the outer count and bypass recovery. Initiating errors from later consumer init failures remain intact. Generic PHY core, DWC3, binding and board DTS are unchanged.

**Independent coordinator execution:** submitted tests compile production PHY-core init/exit/set-mode and SNPS/PTN3222 bodies under explicit mocks. Both regressions fail on old d513929 source; **all 12 boundary cases and 37 direct-provider cases pass** on published 61202a82. ASan/UBSan ran with leak detection disabled because of this environment's process-inspection restriction; owner leak-enabled result remains separately reported. Reviewed committed module log shows both changed objects, MODPOST and both module links. No duplicate build or schema installation. Local binary hashes and local-to-published tree mapping remain owner-reported, not independently downloaded binary evidence.

**Decision:** bounded software correction accepted. USB pauses. This is source/host/module-link acceptance, not an upstream-ABI endorsement, combined-kernel acceptance or handset result. The experimental profile remains isolated. Physical identity/effective DT, GPIO7 semantics, rail parents/transitions, enumeration and wake await hardware or attributable board evidence. Own-rail disable failures, independent concurrent repeater consumers and wider role-error propagation were explicitly outside this closure; no additional generic fault campaign is assigned.

**Next selected work:** VPU's narrowly scoped power/ICC resource contract. Boot and Userspace remain paused because accepted integration and artifacts did not change.

## Informational identity policy accepted — 2026-10-15

Accepted project **481c399cee777014586b083f0305614e09aa9c68**, kernel **1e5268277f6d4c25cde2f3e2b3f00439107e087a** (driver d87632e, binding-description correction 1e526827). Unknown readable IDs warn and continue for the existing oneli profile; identity-read failures remain fatal before tuning. No invented BUK constant or generic bypass. The user-authorized relaxed policy supersedes the BUK allowlist prerequisite.

Coordinator inspected both kernel diffs and independently ran the submitted production-provider harness: **44 scenarios PASS**, ASan/UBSan with leak detection disabled; source/test hashes match committed evidence. Inspected owner-produced ARM64 object/MODPOST/module-link log, not a coordinator rebuild or binary verification. Binding constraints unchanged; prior schema evidence reused. Source/host acceptance only, not handset or combined integration acceptance.

GPIO7 active-low descriptor proposal accepted at source-contract level. L2B voltage constraints/provider rounding and actual board providers remain future integration work. USB pauses; no additional ID search or capture is required to progress development. [Current review](COORDINATOR_REVIEW_2026-10-15.md) and [assignments](NEXT_TASKS.md) supersede earlier task-selection statements.
