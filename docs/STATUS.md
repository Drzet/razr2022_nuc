# Project status

Updated: 2026-10-11. This table describes evidence committed to this repository, not unreported work in other chats.

## Stage definitions

- **Researched:** relevant sources inspected and findings linked; does not establish device operation.
- **Implemented:** code exists at a named commit; does not establish compilation.
- **Build-tested:** a named configuration and toolchain produced recorded results.
- **Hardware-tested:** a named image was exercised on identified hardware with logs and outcomes.

Stages are evidence fields, not a single success label. Partial research and failed tests remain explicit.

| Workstream | Research evidence | Implementation | Build evidence | Hardware evidence | Next handoff |
| --- | --- | --- | --- | --- | --- |
| Baseline / boot | [Hardware audit](razr2022_linux_audit_readme_2026-10-11.md) | Not recorded | Not recorded | Not recorded | Select baseline, establish build and board-support plan |
| GPU | [Driver inventory](tables/linux_drivers.csv) | Not recorded | Not recorded | Not recorded | Pin relevant support and firmware requirements against selected baseline |
| USB / Type-C | [Hardware audit](razr2022_linux_audit_readme_2026-10-11.md) | Not recorded | Not recorded | Not recorded | Resolve controller, role/orientation and redriver dependencies |
| DisplayPort | [Hardware audit](razr2022_linux_audit_readme_2026-10-11.md) | Not recorded | Not recorded | Not recorded | Specify routing and USB/Type-C dependencies |
| VPU | [Focused investigation](razr2022_vpu_investigation_2026-10-11.md) | Not recorded | Not recorded | Not recorded | Validate firmware/protocol and upstream platform approach |
| Power / charging / thermal | [Hardware audit](razr2022_linux_audit_readme_2026-10-11.md) | Not recorded | Not recorded | Not recorded | Establish device-specific policy and boot dependencies |

## Open coordination decisions

- Kernel fork `Drzet/linux` is verified, with read/write access and default branch `master` (2026-10-11). Upstream baseline and toolchain remain unselected.
- Actual device firmware and selected board revision remain unrecorded.
- The VPU investigation adds sources not yet reconciled into the hardware database. Pin the appropriate source revision before reconciliation; preserve its current evidence qualifications.
- No subsystem branches, kernel configs or image preparation parameters have been established by this scaffolding commit.

## Handoffs

Place completed handoffs in `docs/handoffs/` using [the template](templates/subsystem-handoff.md), then link them from this page. The coordinator reconciles dependencies and selects integration order; subsystem chats supply code and evidence.
