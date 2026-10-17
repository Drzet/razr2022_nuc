# USB canonical handoff: automatic CI maintenance (2026-10-17)

**Owner:** USB / local Codex. **Scope:** the limited CI-maintenance exception in coordinator [0e10c58e58f220b7e39acf60532945d0940b9320](https://github.com/Drzet/razr2022_nuc/commit/0e10c58e58f220b7e39acf60532945d0940b9320). Read that revision's AGENTS, STATUS, NEXT_TASKS and WORKFLOW, and this canonical handoff before editing. USB driver implementation remains paused; automatic checks for these workflow changes are authorized. No driver, binding, DTS or accepted integration change.

## Exact heads, ownership and changed files

Inspected remote heads before acting; preserved their histories with native, non-force pushes:

| Repository / branch | Input → delivered head | Maintenance |
| --- | --- | --- |
| Drzet/linux `razr/usb` | `87d7277ced4c562e2379ee58aaed5c5fd7db4f32` → **[`305bc34cac710adc9fe7c4794a6e909abdf83ee0`](https://github.com/Drzet/linux/commit/305bc34cac710adc9fe7c4794a6e909abdf83ee0)** | Delete `.github/workflows/razr-ps5169-candidate.yml`; maintain `razr-usb-schema.yml`. |
| Drzet/linux `razr/usb-ps5169` | `4dcbc7ba1c04afea37ab0b0caf6b4c16bfcc3dfe` → **[`57d4d32b614cf23c2d9f60cdb06daa30870d7b61`](https://github.com/Drzet/linux/commit/57d4d32b614cf23c2d9f60cdb06daa30870d7b61)** | Delete candidate, durable-import and separate conditional-schema workflows; consolidate `razr-ps5169-fault-ci.yml`; maintain `razr-usb-schema.yml`. |
| Drzet/linux `razr/usb-ptn3222` | **`1e5268277f6d4c25cde2f3e2b3f00439107e087a`**, unchanged | No `.github/workflows` directory at this head. Existing PTN tests/evidence are retained; no new PTN pipeline or duplicate run was commissioned. |

Project branch is **razr/usb**, starting from fetched **`481c399cee777014586b083f0305614e09aa9c68`**. Project changes are this handoff, `tests/usb/test_ci_workflows.py`, and scoped `tests/results/2026-10-17-usb-ci-maintenance/` logs/results. The project baseline workflow belongs to another owner and is unchanged. No frozen branch, repository setting, default branch, archived evidence or other owner's workflow/run was altered.

## Retirement and replacement coverage

- **`razr-ps5169-candidate.yml`** is removed from both maintained USB branches. Its ephemeral mbox import, include/supply patching, binding test and standalone object compile are superseded by the already attributed committed PS5169 driver/binding and current host/schema/dependency-complete module pipeline. Original scripts, author history and accepted artifacts remain available.
- **`razr-ps5169-durable.yml`** is removed from the PS5169 branch. Re-importing and pushing a candidate from CI is obsolete now that the attributed implementation is committed. Its binding and ARM64/MODPOST/module-link checks remain in the maintained pipeline. Removing its write-capable automation does not remove provenance or acceptance evidence.
- **`razr-ps5169-conditional-schema.yml`** is merged into the maintained **`razr-ps5169-fault-ci.yml`** cheap `checks` job. This retains the binding document/example check, all 1-positive/8-negative DTB fixtures, actual GPIO19 cells, seven generic-override probe rejections and clean reprobe. The conditional runner already executes the full original probe/remove harness; the former separate invocation is eliminated. Transition/SVID/downstream error tests still run once separately.
- **`razr-usb-schema.yml`** remains a distinct lightweight check for the SNPS eUSB2 binding, rather than confusing it with PS5169 validation. Relevant push coverage on both maintained USB branches, existing pull-request path filters and explicit dispatch remain automatic.

## Gate, triggers and dependency contract

`arm64-and-binding` now has **needs: checks** and requires **needs.checks.outputs.build == true**. Default successful-needs semantics prevent expensive compilation after a failed cheap job. Binding examples, fixture validation and production-host assertions run before any ARM64 build job; no parallel expensive start or repeated schema-tool installation inside the build job.

The previous selector searched `github.event.commits` text for a source path, but [GitHub documents that Actions push commit objects omit file-path lists](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#push). The replacement executes the actual **before/head Git diff**, including multi-commit pushes and deletions/renames. Checkout depth is2; an older push base is fetched by exact SHA when needed. Source, direct build-dependency and defconfig changes retain automatic compilation. Binding/fixture/test/workflow-only pushes run cheap checks without rebuilding an unchanged accepted driver. Documentation-only changes match neither workflow's path filter. Explicit dispatch and unresolvable/new-branch ranges conservatively retain compilation, still behind the cheap gate.

The dependency-complete **Image modules** command, real `Module.symvers`, linked PS5169 module and AArch64 ELF checks are preserved. This task does not replace them with isolated object compilation, fake symbols or unresolved-symbol suppression. Future build artifacts retain exact source SHA, compiler, resolved config plus its hash and output hashes. No ARM64 build is needed to reproduce unchanged driver evidence for this maintenance change.

Both retained workflow names use **`${{ github.workflow }}-${{ github.ref }}` / cancel-in-progress:true**, following [GitHub's workflow/ref scope](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#concurrency). This cancels superseded runs within that workflow/ref, without cross-owner cancellation. No runs were manually cancelled. dtschema is pinned to the existing **2026.6** validation input; checkout/upload-artifact v4 are pinned to exact official tag commits **11d5960a326750d5838078e36cf38b85af677262 / ea165f8d65b6e75b540449e92b4886f43607fa02**. Read-only contents permission, finite25/90-minute job timeouts and evidence uploads remain explicit.

## Validation and Actions receipts

Local checks before pushing:

- **actionlint1.7.12 PASS** for all three maintained definitions; release archive SHA256 verified. ShellCheck is unavailable and disabled in actionlint; embedded Bash syntax is checked separately.
- **25 actual Git selector cases PASS**, executing the real workflow step, including workflow/binding/fixture-only changes, relevant source/dependency changes, multi-commit push, missing/invalid base, failed and successful shallow-base fetch, rename and explicit dispatch. Assertions also check trigger coverage, required job dependency, cancellation scope and retained build assertions.
- **Transition production-body faults PASS**. Consolidated conditional runner **PASS** with dtschema2026.6:1-positive/8-negative actual DTB fixtures, full existing production-probe/remove suite and seven override cases. No standalone duplicate probe invocation or PTN lifecycle replay.
- Both kernel diffs contain only `.github/workflows` paths. Whitespace checks pass. No local Image, module, combined artifact, firmware extraction or hardware operation.

Commands:

```sh
/tmp/razr-usb-ci-tools/actionlint -shellcheck='' \
  /tmp/razr-usb-ci-ps5169/.github/workflows/*.yml \
  /tmp/razr-usb-ci-legacy/.github/workflows/*.yml
/tmp/razr-ptn3222-schema-venv/bin/python tests/usb/test_ci_workflows.py \
  /tmp/razr-usb-ci-ps5169 /tmp/razr-usb-ci-legacy \
  /tmp/razr-usb-ci-validation/selector-result.json
python3 /tmp/razr-usb-ci-ps5169/scripts/razr/ps5169-fault-injection.py
PATH="/tmp/razr-ptn3222-schema-venv/bin:$PATH" \
  /tmp/razr-ptn3222-schema-venv/bin/python \
  /tmp/razr-usb-ci-ps5169/scripts/razr/ps5169-conditional-validation.py
```

Automatic push runs scheduled on the exact delivered heads: [PS5169 gate38986262436](https://github.com/Drzet/linux/actions/runs/38986262436), [PS5169-branch SNPS schema38986262582](https://github.com/Drzet/linux/actions/runs/38986262582), [USB-branch SNPS schema38986268226](https://github.com/Drzet/linux/actions/runs/38986268226). **All three runs concluded success.** PS5169 cheap job117258336384 passed; dependent ARM64 job117258746214 was correctly **skipped** for the workflow-only push. Both standalone SNPS schema jobs passed. Exact steps and GitHub-reported artifact IDs/digests are in the [Actions receipt](../../tests/results/2026-10-17-usb-ci-maintenance/actions-receipt.json); artifact binaries were not independently downloaded/hash-verified. No dispatch or redundant rerun was requested. Local logs, tool/input hashes and exact coverage limits: [maintenance manifest](../../tests/results/2026-10-17-usb-ci-maintenance/manifest.json). These are automation/host/schema results, not new driver build acceptance or handset operation.

## Retained acceptance and stop

Coordinator [99b37f4 review](https://github.com/Drzet/razr2022_nuc/blob/99b37f464fedca0caacc47b59fa3b2fa525ccacf/docs/COORDINATOR_REVIEW_2026-10-15.md) accepted project481c399 / kernel1e526827, independently reproducing44 PTN provider scenarios. Unknown readable chip IDs remain diagnostic; failed reads abort before tuning. PM8350C physical GPIO7 / DT7 / offset6 active-low descriptor semantics remain source-resolved. Later Power acceptance, carried in current main STATUS, selects3.080V on the supported L2B grid for the unchanged3.075–3.300V request; the stock3.072V difference is not a new development blocker. No BUK or8mV research was repeated.

The [previous canonical handoff at481c399](https://github.com/Drzet/razr2022_nuc/blob/481c399cee777014586b083f0305614e09aa9c68/docs/handoffs/2026-10-13-usb-tenth-round.md) retains exact runtime-policy/register/supply provenance, PS5169 history and original test/build links. Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts are unchanged. Installed-board correspondence remains [INFERRED]; native USB enumeration and wake are untested.

**Stop:** publish this project handoff/evidence commit and the exact two workflow-only kernel commits to issue#2, then stop. The CI-maintenance exception does not activate driver/DTS implementation, shared board integration or another subsystem task.
