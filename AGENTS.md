# Project coordination rules

- Read `docs/STATUS.md`, `docs/NEXT_TASKS.md`, `docs/WORKFLOW.md` and the relevant investigation before changing project decisions or subsystem status.
- Use the hardware database in `docs/` as the primary structured evidence source; consult newer focused investigations for unresolved additions. Preserve evidence provenance and qualify inferred hardware claims with `[INFERRED]`.
- Keep kernel source, device trees, bindings and driver changes in `Drzet/linux`. Do not duplicate them here or import whole Android source trees.
- Do not invent GPIOs, firmware names, configuration symbols, build parameters or successful test results. Record missing inputs explicitly.
- Keep researched, implemented, build-tested and hardware-tested evidence separate. A merge or upstream driver match does not prove operation on this phone.
- Use `docs/templates/subsystem-handoff.md` for subsystem handoffs. Record exact commits, dependencies, shared files and results.
- Coordinate changes to shared board/SoC device trees and configuration before integration. Preserve concurrent work; do not overwrite another subsystem's updates.
- Record baseline selections and changes in `configs/baseline.json` and `docs/WORKFLOW.md`. The initial null fields mean no baseline has been selected.
- Keep proprietary firmware binaries and generated images out of this repository. Track provenance, filenames and hashes instead.

- A brief stock Android ADB session was captured on 2026-10-11; read `docs/oneli_stock_android14_adb_hardware_capture_2026-10-11.md` for observed board/build identity and its limits. The phone was then disconnected; do not assume ongoing access or native validation. Continue source audits, public stock-firmware inspection, compilation, schema checks and suitable generic emulation. Label physical runtime tests deferred; do not call a public reference image the installed firmware.

- Coordinator owns aggregate `docs/STATUS.md` and `docs/NEXT_TASKS.md`. Subsystem agents update their own handoffs/results on assigned branches and propose coordination changes; do not overwrite aggregate status from stale branches. Read coordinator main for the latest assignments and dependency gates.

- Latest user update: follow-up ADB was unsuccessful; plan without hardware access. Preserve earlier stock observations. The owner intends to unlock when the device is fully in their possession; do not treat unlock as an offline coding blocker. Follow scoped holds in NEXT_TASKS rather than repeating completed audits.

- Fourth review (2026-10-12): read `docs/FOURTH_REVIEW.md` and current `docs/NEXT_TASKS.md`. Firmware location is resolved; per-FDT stock properties remain a separate shared export. Both uploaded live-DT archives contain zero property files. Centralize bounded member retrieval; do not repeat full ROM scans or unchanged CI on documentation-only updates.

- Fifth review supersedes the fourth task queue: read `docs/FIFTH_REVIEW.md` and current `docs/NEXT_TASKS.md`. Boot is explicitly delegated execution of an isolated combined integration candidate and its full artifacts; coordinator retains acceptance/promotion and aggregate docs. This narrow delegation overrides earlier coordinator-only execution wording. DisplayPort is on an evidence hold; do not repeat completed audits.
