# Razr 2022 NUC

Native mainline Linux port for the Motorola Razr 2022 (`oneli`, Snapdragon 8+ Gen 1 / SM8475).

## Start here

- [Project status](docs/STATUS.md) and [current assignments](docs/NEXT_TASKS.md)
- [Cleanup and retained/retired work](docs/CLEANUP_2026-10-13.md)
- [Repository architecture and integration workflow](docs/WORKFLOW.md)
- [Hardware evidence and subsystem investigations](docs/README.md)
- [Subsystem handoff template](docs/templates/subsystem-handoff.md)

## Repository layout

| Location | Purpose |
| --- | --- |
| `docs/` | Hardware evidence, investigations, decisions and project status |
| `configs/` | Kernel configuration fragments and selected baseline record |
| `scripts/` | Reproducible build and image preparation tooling, once inputs are verified |
| `firmware/` | Firmware inventories, hashes, provenance and extraction notes |
| `tests/` | Validation procedures and recorded build/device results |

Kernel source, drivers, bindings and device trees belong in the [Drzet/linux](https://github.com/Drzet/linux) fork. This repository coordinates that work and records exact inputs and results. Motorola sources remain pinned references.

## Evidence baseline

The [hardware audit overview](docs/razr2022_linux_audit_readme_2026-10-11.md) summarises the findings. The [machine-readable hardware database](docs/razr2022_native_linux_hardware_database_2026-10-11.json) contains components, upstream driver mappings, device-tree records, board revisions and source links. [Focused investigations](docs/README.md#focused-investigations) may contain newer findings awaiting reconciliation into that database.

Research snapshot: **11 October 2026**, supplemented by dated investigations. Combined ARM64 kernel/modules, device-tree validation, project-kernel QEMU and diagnostic-v2 host packaging have passed within their recorded scopes. Native handset boot remains untested. Current status and assignments above supersede historical plans.
