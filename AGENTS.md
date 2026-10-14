# Project rules

Read current `docs/STATUS.md`, `docs/NEXT_TASKS.md`, `docs/WORKFLOW.md` and your canonical handoff before acting. Only NEXT_TASKS assigns work. Historical reviews, archived queues and old issue comments do not reactivate tasks.

- Target native mainline Linux with Debian userspace. Kernel source, drivers, bindings and DTS belong in `Drzet/linux`; evidence, tooling and manifests belong here. Do not duplicate kernel source or proprietary firmware.
- Use the hardware database and newer pinned evidence. Mark hardware assumptions `[INFERRED]`. Distinguish source inspection, compilation, emulation and hardware results. Never invent identifiers, parameters, compatibility or tests.
- Hardware is currently unavailable. Preserve the 2026-10-11 stock ADB evidence; the subsequent failed session does not invalidate it. Unlock is not an offline blocker. Native behavior remains untested.
- Reuse before new implementation: inspect current mainline, pending upstream/maintainer series, relevant out-of-tree Linux/mobile projects and vendor sources. Record closest code, exact revisions, coverage limits and minimal delta. Missing support in our pinned baseline does not justify new code. Preserve authorship/licensing; update existing research only where stale or missing.
- Default: one active implementation stream. Coordinator may select a second only with fixed inputs, independent interfaces/files and a concrete benefit. No blanket rounds. Stop at the assignment's deliverable or named blocker; do not self-assign follow-up work.
- Sequence: reuse decision, interface agreement, implementation, focused validation, integration, downstream consumption. Do not build consumer work against unsettled producer contracts.
- Coordinator owns aggregate status, queue, policy and integration acceptance. Boot owns shared board/SoC DTS. Subsystem owners edit assigned files and one canonical handoff; request shared-file changes rather than editing concurrently.
- Work on the exact assigned branch/base. Never reset another agent's work or rewrite tested history. Superseded prototypes remain evidence, not implementation candidates. In `Drzet/linux`, `razr/vpu` and `razr/vpu-upstream` are frozen historical branches; the sole canonical VPU candidate is `razr/vpu-provenance-v5`, currently paused. In this coordinator repository, `razr/vpu` remains the evidence/handoff branch.
- Reuse existing artifacts, exports and test results for identical inputs. Run focused tests for changed behavior; full builds for meaningful dependency/link/integration changes. No build for documentation-only edits. Cancel superseded duplicate CI when safe; never cancel another owner's run without coordination.
- Every handoff names exact commits, dependencies, changed files, reuse source, relevant tests and stop condition. Keep one current report; link historical evidence instead of copying it.

Detailed operating policy: `docs/WORKFLOW.md`. Cleanup disposition: `docs/CLEANUP_2026-10-13.md`.
