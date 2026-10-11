# Validation evidence

Keep procedures and results separate. No kernel build or device test is claimed by these templates.

For each build, complete [the build record](templates/build-record.md). For device tests, record device revision, stock firmware identity, kernel/image SHA-256, exact command and tool versions, logs, expected result and observed result. Store compact text evidence under `tests/results/`; link large artifacts with checksums instead of committing binaries.

| Area | Validation scope to establish |
| --- | --- |
| Boot | Diagnostic output, kernel start, initramfs userspace and relevant device enumeration |
| GPU | Driver/firmware initialization, selected renderer and a reproducible rendering workload |
| USB / Type-C | Required host/device roles, connector orientations and peripheral enumeration |
| DisplayPort | Detected modes and stable output through the identified dock/display |
| VPU | Firmware load, decoder registration/compliance and standalone decode before browser playback |
| Power | Supply/battery reporting, charging behavior and thermal observations |

These are test scopes, not verified commands or pass results. Subsystem owners supply executable procedures against the selected software and identified hardware.
