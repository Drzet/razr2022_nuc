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
| Baseline / boot | [Baseline comparison](sm8475_baseline_comparison_2026-10-11.md) and [boot handoff](handoffs/2026-10-11-boot-oneli.md) | Initial SM8475/oneli DTS and bindings on `razr/boot` at [cb9105e](https://github.com/Drzet/linux/commit/cb9105ebeb9485e31d044d4fa69396b415523669) | [Baseline configuration blocked](../tests/results/2026-10-11-baseline-build.md); boot branch not compiled | Not recorded | Run branch DTB/schema build; obtain actual oneli firmware/revision; reconcile UFS/USB/power shared-DT proposals |
| GPU | [Driver inventory](tables/linux_drivers.csv) | Not recorded | Not recorded | Not recorded | Pin relevant support and firmware requirements against selected baseline |
| USB / Type-C | [Hardware audit](razr2022_linux_audit_readme_2026-10-11.md) | Not recorded | Not recorded | Not recorded | Resolve controller, role/orientation and redriver dependencies |
| DisplayPort | [DisplayPort handoff](handoffs/2026-10-11-displayport-oneli.md) and [dock test plan](../tests/procedures/2026-10-11-displayport-dock.md); pinned MSM DRM, DP AUX, GPIO-SBU and Type-C/PS5169 source review | No kernel changes; `razr/displayport` created at baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` | Not recorded | Not recorded | Verify GPIO2/71 AUX mux hardware and polarity; integrate reviewed USB/PS5169/PMIC GLINK and regulator prerequisites; Boot owns DP board DT enablement |
| VPU | [Focused investigation](razr2022_vpu_investigation_2026-10-11.md) | Not recorded | Not recorded | Not recorded | Validate firmware/protocol and upstream platform approach |
| Power / charging / thermal | [Hardware audit](razr2022_linux_audit_readme_2026-10-11.md) and [Power handoff](handoffs/2026-10-11-power-oneli.md) | No power-specific kernel patch; research branch `razr/power` based on Boot `cb9105e` | Not recorded | Not recorded | Integrate Boot-owned regulator DT proposal; verify live GLINK/dual-battery/thermal evidence |

## Open coordination decisions

- Kernel fork `Drzet/linux` is verified, with read/write access and default branch `master` (2026-10-11). Upstream baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` is selected; toolchain remains unavailable/unselected.
- Actual device firmware and selected board revision remain unrecorded.
- The VPU investigation adds sources not yet reconciled into the hardware database. Pin the appropriate source revision before reconciliation; preserve its current evidence qualifications.
- `razr/boot` now contains an initial reconciled SM8475 include, minimal oneli board DTS and binding support at `cb9105ebeb9485e31d044d4fa69396b415523669`. These are **source-only changes, not DTB-build- or hardware-validated**. No completed kernel configuration, integration branch or image preparation parameters have been established. [Boot handoff](handoffs/2026-10-11-boot-oneli.md).

## Handoffs

Place completed handoffs in `docs/handoffs/` using [the template](templates/subsystem-handoff.md), then link them from this page. The coordinator reconciles dependencies and selects integration order; subsystem chats supply code and evidence.

- [2026-10-11 boot / SM8475 / oneli handoff](handoffs/2026-10-11-boot-oneli.md) (implemented; no build or hardware results).
- [2026-10-11 DisplayPort handoff](handoffs/2026-10-11-displayport-oneli.md) and [dock validation procedure](../tests/procedures/2026-10-11-displayport-dock.md) (researched only; no kernel patch, build or hardware tests).
- [2026-10-11 power / regulators / charging / thermal handoff](handoffs/2026-10-11-power-oneli.md) (researched; no power-specific kernel implementation, build or hardware results).

## Build automation

[GitHub Actions baseline build](BUILD_CI.md) supplies the cross-toolchain on a hosted runner. Workflow creation is not build success; the first run must be inspected before updating evidence status.
