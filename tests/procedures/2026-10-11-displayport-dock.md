# Motorola oneli: native Linux USB-C DisplayPort dock validation

**Date:** 2026-10-11. **Status:** physical execution **deferred: owner has no access to the handset**. No AUX/HPD/EDID/link-training/monitor results. **Hardware revision/firmware:** unknown. **Kernel baseline:** `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. **DisplayPort handoff:** [docs/handoffs/2026-10-11-displayport-oneli.md](../../docs/handoffs/2026-10-11-displayport-oneli.md).

## Offline results and next gate (2026-10-11)

- [Pinned vendor AUX-routing investigation](../../docs/displayport_oneli_aux_routing_2026-10-11.md) establishes **vendor software** outputs: GPIO2/GPIO71 = `1/0` when disconnected, `0/0` in DP CC1, `0/1` in DP CC2. Exact physical mux IC and runtime polarity remain unknown.
- 13/13 pinned-source assertions passed for the vendor GPIO path and existing mainline GPIO-SBU logic/binding. This is **source validation, not DT schema or hardware verification**.
- No switch compatible can be justified from available oneli hardware evidence. Do **not** create a false GPIO-SBU compatible or enable DP in the board tree simply to make `dtbs_check` pass; the independently-controlled SBU mux and USB/PS5169 graph must first be identified.
- [Cross-subsystem coordination issue #3](https://github.com/Drzet/razr2022_nuc/issues/3) tracks the Type-C connector, PS5169, GPIO91 and DP/AUX ownership.
- **All matrix entries below are deferred until the handset and required dock/monitor become available.** A subsequent passing CI DTB/schema check is not an on-device DP test.

## Required prerequisites

- Native kernel actually boots with repeatable console/pstore log retrieval, validated on the identified oneli hardware and firmware build. Record exact Boot, Power, USB and DisplayPort commit SHAs and full integrated kernel SHA; do not test an unvalidated boot image as if this plan were a flashing instruction.
- Active kernel configuration with `CONFIG_DRM_MSM`, `CONFIG_DRM_MSM_DPU`, `CONFIG_DRM_MSM_DP`, `CONFIG_PHY_QCOM_QMP_COMBO`, `CONFIG_QCOM_PMIC_GLINK` and relevant USB/Type-C support. If physical SBU switching uses the existing mainline driver, `CONFIG_TYPEC_MUX_GPIO_SBU`. Treat values as **required feature checklist** rather than a claim these symbols have been enabled or build-tested. Confirm symbols in the generated `.config`.
- Built and schema-validated `sm8475-motorola-oneli.dtb`, proper power rails and non-conflicting connector port graph. No guessed DP lane order, SBU mux IC name or GPIO polarity.
- Known-good external DisplayPort monitor (log EDID/advertised modes), direct USB-C DP Alt Mode adapter, separately a USB-C dock with HDMI/DP output, USB peripherals and PD input. Note which actual connectors support DP Alt Mode; USB-C alone does not establish support. A tested USB2 input device, a USB3 storage device and a known-good power source/cable. Record dock model, firmware and cable details.
- `modetest` from libdrm tools, kernel log reader (`journalctl` or `dmesg`), access to `/sys/class/drm` and `/sys/class/typec`. Test output can use KMS without requiring GPU 3D acceleration. Save raw logs; distinguish present utility from an installed one.

## Collection: run for every integration candidate

Record timestamp, device model/revision, actual firmware/build ID, DTB/DTBO selection, integrated kernel SHA and all component SHAs, `uname -a`, kernel command line, generated `.config`, toolchain/build logs, peripherals and cable details.

Commands on a booted native Linux image **when those tools exist**:

```sh
uname -a
cat /proc/cmdline
ls /sys/class/typec/
ls /sys/class/drm/
modetest -M msm -c
modetest -M msm -p
journalctl -k -b
```

Collect before attaching, after attaching, after modeset, after flipping connector orientation and after detaching. Where systemd/journalctl is not available, use `dmesg` and record that substitution. Use `ls` rather than relying on unconfirmed sysfs node naming conventions.

## Diagnostic sequence and acceptance criteria

| Step | Hardware/action | Expected observable outcome | Distinguish failures |
| --- | --- | --- | --- |
| 1. Driver/DT bind | Boot with dock unplugged | MSM DRM card/DP controller, power/clock/IOMMU and QMP PHY probe without errors or perpetual deferred probe | No card: MDSS/DPU/DP initialization; no PHY: supplies, clock or combo PHY; no Type-C: GLINK/UCSI |
| 2. Plain USB | Plug basic USB peripheral, both cable orientations | UCSI attach, USB host role, USB2 connectivity when ready; never claim DP from plain USB | Missing role/eUSB/repeater handled by USB; not a DP KMS regression |
| 3. Direct DP adapter | Plug DP Alt Mode-only adapter with known-good monitor | Firmware DP Alt Mode notification, Type-C orientation/mux/SBU state, HPD connected; DP controller attempts AUX | If no altmode, check firmware/UCSI/PS5169; if no AUX, check GPIO2/71 and polarity |
| 4. DP link/EDID | Keep external monitor attached | DPCD caps and EDID read succeed; `modetest -M msm -c` lists an external connected connector with monitor modes | HPD present but EDID absent implicates AUX routing; EDID but link failure implicates PHY/retimer/DP training |
| 5. KMS modeset | Identify real connector ID, CRTC ID and *advertised* mode using `modetest -M msm -c -p`; then request that mode | External monitor shows a stable image at an advertised mode | CRTC/encoder mapping, PLL/DP lane, DPU bandwidth and OPP errors |
| 6. Orientation | Unplug, rotate USB-C connector 180 degrees, repeat 3–5 | Same attach, hotplug, EDID and mode set outcomes both rotations | USB owner checks PS5169/QMP orientation; DisplayPort checks SBU mux GPIO71 |
| 7. HPD | Power monitor off/on, disconnect/reconnect cable, repeat 5 cycles | Connector status changes with physical events; display restores correct image; no stale connected state or unbounded errors | Missing HPD bridging or IRQ, stale PD Alt Mode and AUX mux state |
| 8. Dock I/O | Attach dock, monitor, USB2 input device and USB3 storage device | Monitor active and USB2 works; USB3 speed/availability recorded, not assumed guaranteed by every DP lane assignment | Check negotiated DP pin assignment; DP four-lane mode can remove SS lanes |
| 9. Power | Add PD charger through powered dock, record reported contract and battery/charger behavior | DP + input devices remain connected, safe charging reported by power subsystem | PMIC GLINK PD/charging policy owned by Power/USB |
| 10. Load and recovery | Sustained displayed image and monitor-mode changes; repeat suspend/resume only when working | No persistent link retraining loops, display underruns or Type-C deadlock | Clock/OPP/thermal/power-dependent failures separately |

Mode-setting command **template** after identifying connector ID, CRTC ID and actual EDID mode (substitute real values; placeholders are not hardware facts):

```sh
modetest -M msm -s '<connector-id>@<crtc-id>:<advertised-mode>'
```

Start with an advertised low-bandwidth mode; try 1920x1080 at 60 Hz **only if EDID lists it**. Record negotiated DP rate/lane count from actual diagnostics if available. Do not ascribe 4K capability to the phone before tests.

## Test matrix to preserve

| Cable orientation | Attachment | DP/EDID | USB2 | USB3 | Power delivery |
| --- | --- | --- | --- | --- | --- |
| Normal | Direct DP adapter | Deferred | N/A | N/A | N/A |
| Reversed | Direct DP adapter | Deferred | N/A | N/A | N/A |
| Normal | Unpowered multifunction dock | Deferred | To test | Deferred | N/A |
| Reversed | Unpowered multifunction dock | Deferred | To test | Deferred | N/A |
| Normal | Powered multifunction dock | Deferred | To test | Deferred | To test |
| Reversed | Powered multifunction dock | Deferred | To test | Deferred | To test |

For every test, save timestamped DRM connector state, Type-C role/orientation/Alt Mode state if exposed, PS5169 I2C probe log and debug data if available, AUX/DPCD/EDID result, negotiated lane/rate, USB speed, PD contract/battery indicators, errors and photo of screen output. Separate a physical dock failure from Linux/firmware failure by testing the adapter/dock on a known-good DP Alt Mode host first.

## Exit criteria and reporting

**Pass, basic DP:** native boot at exact named commits, monitor detected in both orientations, valid EDID, successful repeated modeset and hotplug, no persistent DRM/PHY/AUX failures. USB/PD **not implicit** in this pass.

**Pass, dock/NUC integration:** basic DP plus concurrent input, verified USB2 and USB3 behavior for negotiated dock mode, stable charging/power telemetry, repeatable unplug/replug and log retention. Record any negotiated four-DP-lane mode that limits SuperSpeed separately, rather than treating expected lane sharing as a failure.

**Fail or blocked:** record earliest failed stage, actual raw evidence and subsystem owner (Boot/Power/USB/DisplayPort). Never mark build or hardware-tested solely from source inspection.
