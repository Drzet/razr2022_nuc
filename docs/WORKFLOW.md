# Architecture and coordination

Decision recorded: 2026-10-11. Scope: native mainline Linux, with separate subsystem chats and this project repository as the durable coordination record.

## Repository responsibilities

- `Drzet/linux`: one kernel source of truth, containing board/SoC device trees, bindings, drivers and a traceable patch history. Leave its default upstream branch unchanged by project development.
- `Drzet/razr2022_nuc`: evidence, configuration fragments, baseline metadata, build/image tooling, firmware inventory, validation procedures and results.
- Motorola and other external trees: references pinned to exact revisions. Port justified changes as individual commits, preserving authorship, source links and applicable licensing. Record unmerged patchset versions and dependencies.

The kernel fork `Drzet/linux` and read/write access were verified on 2026-10-11. Its default branch is `master`. On 2026-10-11, upstream commit `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` was selected as the initial baseline and `razr/boot` was created at that SHA. This now deliberately matches the research snapshot; its clean ARM64 Image/dtbs build has passed (see `tests/results/2026-10-11-baseline-ci.md`); subsystem patches are not covered. See [the comparison](sm8475_baseline_comparison_2026-10-11.md).

## Planned kernel branches

All six subsystem branches exist; see `STATUS.md` for their reviewed commits. `razr/integration` now records the sixth-review accepted source/build/QEMU commit (see the dated acceptance below). GPU and USB currently contain standalone baseline-based patches; board-dependent additions must name their Boot dependency.

| Branch | Responsibility | Dependency |
| --- | --- | --- |
| `razr/boot` | Shared board support, minimal boot and diagnostic output | Selected upstream commit |
| `razr/gpu` | GPU enablement and rendering | Explicit `razr/boot` commit |
| `razr/usb` | USB host/device, Type-C role and orientation work | Explicit `razr/boot` commit |
| `razr/displayport` | External display routing and output | Board support plus required USB/Type-C commits |
| `razr/vpu` | Decoder platform support and firmware interface | Explicit `razr/boot` commit |
| `razr/power` | Power, charging and thermal integration | Explicit `razr/boot` commit |
| `razr/integration` | Combined candidates for validation | Recorded subsystem commits |

Use one selected upstream baseline across active work. Each handoff names exact dependency commits; branch names alone are insufficient. Coordinate shared device-tree changes through board support, keeping bindings and device-tree changes in separate commits. Introduce additional subsystem branches when there is concrete work to own.

## Integration procedure

1. Record a subsystem handoff using the template. Identify shared files and unresolved assumptions.
2. Resolve dependencies and shared-file conflicts; integrate only the reviewed commit set. Record whether it was merged or cherry-picked, including resulting SHAs where changed.
3. Build the combined kernel and affected device trees; validate bindings when changed. Preserve commands, tool versions, resulting configuration and logs.
4. Record device tests independently of compilation. Keep failures and regressions visible.
5. Update `STATUS.md` with evidence links. Tag hardware-tested integration commits with the scope of tests in the tag/release record. An integration branch may contain candidates that are not yet hardware-tested.

Do not rewrite a published integration commit used by a recorded test. Baseline changes require a recorded reason, new exact upstream SHA and a re-evaluation of dependent branches.

## Reproducible build record

`configs/baseline.json` records the selected project inputs once known. Each actual build also needs a completed `tests/templates/build-record.md` containing the exact kernel and project revisions, ordered fragments, toolchain, external patches, firmware manifest, commands, image preparation inputs and artifact hashes. Preserve the generated kernel configuration with the build evidence.

The initial structure deliberately contains no guessed kernel config or boot-image commands. Populate those after checking the selected kernel and the phone's boot requirements.

## First milestones

1. Completed: pin the initial upstream commit and create `razr/boot`.
2. Completed: clean baseline ARM64 Image and device-tree build. Next: compile subsystem candidates, including modules, and validate changed schemas.
3. Implement minimal board support using the hardware evidence and actual boot artifacts.
4. Demonstrate native boot with usable diagnostic output and record the exact image/commit.
5. Integrate subsystem work incrementally; test standalone decode before browser acceleration.

Research for GPU, VPU, USB and power can proceed while boot support is developed. The VPU driver approach remains unresolved: an Iris platform extension is a hypothesis to validate, not an accepted implementation result.

## Fifth-review execution delegation (2026-10-12)

Boot may prepare and build the isolated `razr/integration-candidate` specified in NEXT_TASKS. Coordinator retains commit selection, review and promotion of accepted `razr/integration`; this is a candidate, not an accepted integration branch. Userspace consumes the exact published artifacts for a separate QEMU virt run. Keep default upstream and subsystem branches intact.

## Sixth-review acceptance (2026-10-12)

Coordinator accepted and promoted `2b5acf108ae37040ac1e652e029bb37f5609e886` unchanged to `razr/integration` after reviewing the exact combined diff, complete artifacts and project-kernel guest evidence. See `configs/accepted-integration-2026-10-12.json`. This supersedes earlier candidate-only/planned language; the upstream baseline remains unchanged. No hardware-tested tag or phone acceptance is implied. Future candidate changes remain separate until reviewed. The next milestone and staged owner dependencies are in NEXT_TASKS.
