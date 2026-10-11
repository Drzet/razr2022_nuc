# Razr 2022 Linux hardware audit (11 October 2026)

Source-backed research for building a native mainline Linux kernel for Motorola Razr 2022 (`oneli`). This is a **documentation snapshot, not a verified boot**.

## Reference documents

- [Technical summary, device-tree source hierarchy and next checks](razr2022_linux_audit_readme_2026-10-11.md)
- [Complete JSON evidence database](razr2022_native_linux_hardware_database_2026-10-11.json) (authoritative structured data)

## Focused investigations

- [VPU / 4K browser video feasibility audit (11 October 2026)](razr2022_vpu_investigation_2026-10-11.md) — Motorola video DT source, Iris driver gap, firmware and VP9 validation plan

## GitHub-viewable tables

- [hardware.csv](tables/hardware.csv) (33 records)
- [linux_drivers.csv](tables/linux_drivers.csv) (26 records)
- [dt_nodes.csv](tables/dt_nodes.csv) (33 records)
- [source_index.csv](tables/source_index.csv) (35 records)
- [board_revisions.csv](tables/board_revisions.csv) (4 records)
- [open_questions.csv](tables/open_questions.csv) (16 records)
- [guide.csv](tables/guide.csv) (18 records)

All source links use pinned Motorola or upstream Linux commit IDs where available. `Evidence tier` distinguishes Razr-specific vs inherited SoC data; `Support state` does not imply a working Razr port.

**Unverified:** device's running firmware/DTB, actual QCA6490 revision/firmware, DisplayPort and USB dock operation under mainline, battery charging policy. No kernel flashing or boot tests were performed.

## Project coordination

- [Status and milestones](STATUS.md)
- [Architecture and integration workflow](WORKFLOW.md)
- [Subsystem handoff template](templates/subsystem-handoff.md)

- [postmarketOS source and reuse review (11 October 2026)](postmarketos_review_2026-10-11.md) — pinned package/tooling sources, community SM8475 references and packaging recommendation
