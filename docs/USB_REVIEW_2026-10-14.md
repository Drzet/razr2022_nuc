# USB PTN3222 review — 2026-10-14

## Disposition

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
