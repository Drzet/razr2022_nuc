# Project status

Updated 2026-10-16 afternoon after [VPU/DisplayPort delivery review](COORDINATOR_REVIEW_2026-10-16.md#delivery-review--2026-10-16-afternoon-current).

**Kernel, Debian/QEMU and diagnostic boot images exist; Linux has not booted on the phone. DisplayPort's AUX reuse contract is accepted. VPU consumer code is delivered but needs two cleanup corrections before acceptance.**

[Assignments](NEXT_TASKS.md) · [Policy](WORKFLOW.md) · [Branch disposition](CLEANUP_2026-10-13.md)

| Owner | Current state | Next action |
| --- | --- | --- |
| VPU | Kernel 3086118 / project be103e0; 52 scenarios / 2321 assertions independently reproduced; two framework cleanup defects | Active targeted correction |
| DisplayPort | Project 186a7f2 exact-part reuse/binding/graph proposal accepted | Paused; minimal binding work queued behind supply contract |
| Power | USB/DP shared-rail contract unresolved | Active independent source review |
| USB | PTN3222/PS5169 isolated software acceptance retained | Paused; supply/board integration pending |
| Boot / research | b2f9aea / 0acccb3 accepted | Paused; handset runtime/early-output observations remain |
| GPU / Userspace | Existing accepted evidence retained | Paused |

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886**, [integration record](../configs/accepted-integration-2026-10-12.json) and [diagnostic-v2 record](../configs/accepted-native-console-v2-2026-10-13.json) remain unchanged. No new combined image or working phone USB/DP/VPU claim.

## Current review decisions

- **VPU:** submitted arithmetic/resource tests pass, but VB2 forcibly returns retained buffers after failed start; nonstreaming STREAMOFF bypasses the new cleanup preflight. Successful resource release also clears confirmed-CLOSE state before file teardown. Independent boundary probes reproduce these missing protections; full Linux concurrency is not tested. Delivery is **changes requested**, not accepted. Disabled gate remains.
- **VPU assumptions/limits:** /3 is [INFERRED, USER-ACCEPTED FOR DEVELOPMENT]. Conservative 480-fps startup still rejects 1080p/4K under current policy. IOVA failures, uncertain OPP recovery and general-purpose startup remain separate future issues.
- **DP:** use existing gpio-sbu-mux for reference WAS7227Q-10/TR; no new I2C/DP driver. A narrow compatible/vendor-prefix addition is proposed. The generic driver does not manage its allowed vcc-supply property, so Power must settle shared L2B voltage/provider/lifetime before integration.
- **USB:** unknown readable chip IDs warn/continue; failed reads abort. Existing acceptance does not imply enumeration or wake on hardware.
- **Boot:** reference-firmware loading formula is known and extraction defect fixed. Runtime RAM/FDT/ramdisk selection, alignment and accessible early logs remain unobserved. No further identical packaging or firmware download needed.

## Next native milestone

An observable controlled boot with supported image/DT/ramdisk composition and recovery arrangements. UART pins are identified; accessible pads/voltage or another early-output route remain unresolved. Check full Image allocation and selected memory tree when observable; do not guess runtime addresses. VPU and external display are not prerequisites for a minimal UART boot.

[Canonical schematic evidence](oneli_schematic_evidence_2026-10-15.md) preserves all reported UART, battery GPIO, rail and switch findings. Installed-board correspondence remains [INFERRED]. Reference AUX is WAS7227Q-10/TR; FSA4480 stays disabled.
