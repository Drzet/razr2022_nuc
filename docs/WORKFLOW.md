# Development and integration policy

Current policy, 2026-10-17. Replaces accumulated round-specific instructions. Only [NEXT_TASKS](NEXT_TASKS.md) selects work; [STATUS](STATUS.md) records acceptance. Historical reports remain evidence.

## Stable project boundaries

`Drzet/linux` is the kernel source of truth. This repository contains evidence, build/configuration tooling, firmware inventories and results. Debian remains the userspace target; reuse AOSP image tools and existing Linux/mobile tooling rather than creating parallel frameworks.

Upstream baseline: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. Accepted integration: `2b5acf108ae37040ac1e652e029bb37f5609e886` for source/build/QEMU scope only. Preserve [integration record](../configs/accepted-integration-2026-10-12.json) and [diagnostic v2 record](../configs/accepted-native-console-v2-2026-10-13.json). Do not change baseline or replace tested commits silently.

## Task lifecycle

1. **Select/reuse:** define the actual missing function; inspect current mainline, maintainer/pending series, relevant community/mobile projects and vendor code. Record revision/series, closest implementation, licensing, differences and coverage limitations. Reuse, adapt or backport first. New code needs a concrete remaining gap reviewed by coordinator.
2. **Agree inputs:** name immutable producer commits/artifacts, interface and file owner. Do not commission dependent implementation before these exist.
3. **Implement:** one bounded deliverable, one owner, one assigned branch. Preserve upstream patches and project adaptations separately. Stop if a missing dependency changes the design; report it instead of filling gaps with guesses.
4. **Validate:** tests must detect plausible defects in the changed behavior. Schema compilation alone is not instance validation; expected-invalid cases must assert diagnostics. Host shims are not kernel/hardware execution. Compilation without modpost is not a complete module build.
5. **Integrate:** coordinator chooses exact commits; Boot applies shared DTS and assembles a specifically assigned candidate. Run applicable combined build/schema tests once, preserve required artifacts, then perform dependent Userspace tests if their inputs changed. Coordinator promotes only reviewed results.
6. **Stop:** deliver one concise canonical handoff with evidence and unresolved issues. Completion does not authorize another round. Hardware-only outcomes wait for hardware; source-resolvable gaps need a named source or concrete task.

## Concurrency and resources

Default is one implementation stream. An exception in NEXT_TASKS must identify independent inputs/interfaces/files and why parallel work is useful. A second agent may perform a bounded independent review; it must not duplicate implementation. No generic round for every subsystem.

Coordinator alone owns shared policy/status/queue and acceptance. Boot alone owns shared board/SoC DTS. Interface producer completes a reviewable contract before its consumer proceeds. Parallelism is not a substitute for sequencing.

Search existing reports/manifests before retrieval. Centralize stock extraction; never redownload/re-extract unchanged firmware for another subsystem. Do not repeat completed broad searches; check only missing scope or changed upstream versions. Reuse exact-input artifacts and logs. Pin external tools/schema versions used in acceptance.

Use focused schema/object/host tests during development. Full Image/modules/modpost is required when dependency or link changes need it and for a new combined kernel candidate; do not run it for docs or fixture-only edits. Avoid duplicate CI for the same purpose and head; fix cheap local/host failures before expensive builds. Download only artifacts needed for the decision. Record CI-produced versus independently verified hashes accurately.

## Durable records

One STATUS, one NEXT_TASKS, one canonical handoff per subsystem. Link exact revision evidence rather than creating overlapping reports. Historical decisions live in dated reviews or archive and do not grant work. [Cleanup disposition](CLEANUP_2026-10-13.md) records active/frozen branches and retained work.

Keep authored patch provenance, source and integration SHAs, configurations, relevant tool versions, logs and required binary artifacts. No proprietary firmware or generated image payloads in git. Use firmware manifests. Preserve the existing build-record schema; do not create another parallel schema without a demonstrated consumer need.

## Coordination and execution continuity

Owner authorization covers routine task selection, review, queue/status maintenance and posting project instructions. Coordinator completes these together; a recommendation in chat is not an assignment until recorded in NEXT_TASKS. Subsystem agents still stop at their deliverable and do not activate queued work themselves. GitHub comments publish instructions but do not launch or directly control another chat.

Test local Git access once per session when needed. If unavailable, use available GitHub connector operations and focused CI; do not repeatedly clone or re-check access. Report the exact failed operation and fallback outcome if execution remains blocked. Reuse existing objects/checkouts in an isolated worktree where available. Failed ref leases require inspecting the actual current head; they are not evidence of another writer by themselves. Preserve tested history and use expected-head updates.

## Automatic CI policy — user decision 2026-10-17

User reports workflows re-enabled and authorizes automatic builds for assigned work. This supersedes the earlier temporary Actions hold. Builds remain automatic; do not convert them to manual-only or require per-run permission. Do not change repository settings or default branches as part of this policy.

- Run cheap syntax/configuration, host and relevant schema checks first. Expensive compilation jobs must depend on their successful completion. Validate workflow syntax and available cheap tests before pushing; batch related fixes rather than probing triggers through repeated commits.
- Preserve automatic branch/path filters for relevant source changes. Documentation-only updates must not start kernel builds. Workflow-only changes should exercise the affected validation without unnecessarily rebuilding unrelated subsystems.
- Combine duplicate checks for identical source SHA, resolved configuration and toolchain. Build a DTB or module once and reuse it for its applicable checks; retain all distinct assertions and dependency/modpost requirements.
- Use concurrency scoped to workflow and branch with cancellation of superseded runs. Owners may cancel their own older redundant run after confirming the replacement covers the same validation purpose. Do not cancel another owner's work, a distinct configuration, or an explicitly retained acceptance run.
- Retire superseded prototype workflows from active use. Verify which current workflow replaces their necessary checks, then remove obsolete definitions from maintained branches or disable the exact obsolete workflow. Preserve historical commits, logs and accepted artifacts; do not rewrite frozen branches or delete evidence.
- Pin dependencies, retain exact tested SHA/config/toolchain identities and use finite timeouts. A workflow failing to schedule requires a read-only state/event diagnosis; do not repeatedly alter triggers speculatively.
- Workflow maintenance does not activate paused subsystem implementation or authorize a new combined kernel candidate.
