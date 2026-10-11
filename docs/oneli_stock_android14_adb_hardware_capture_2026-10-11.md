# Oneli stock Android 14 physical-device ADB evidence (2026-10-11)

**Status:** [HARDWARE-OBSERVED] read-only ADB session on an actual Motorola Razr 2022; **not** native Linux validation. This session occurred after the coordinator's second review, whose `docs/STATUS.md` and `docs/NEXT_TASKS.md` still state that the physical phone was unavailable. The device was briefly available on 2026-10-11, then disconnected. Do not rewrite the historical reports; consume this as subsequent evidence.

**Device:** Motorola Razr 2022, `oneli`, model `XT2251-1`, hardware PVT, stock Android 14, locked bootloader. **Scope:** properties, sysfs links, Android service diagnostics, and partial filesystem inventory. No root, no firmware extraction, no writes to partitions, no kernel flash, no bootloader unlock, no native boot and no physical DisplayPort dock validation.

## Executive findings for coordinator

1. **Exact physical board identification is confirmed:** `ro.boot.hardware.revision=pvt`, `ro.vendor.hw.hwrev=0xC000`, `ro.boot.hardware.sku=XT2251-1`, `ro.boot.product.hardware.sku=dn`, `ro.boot.product.vendor.sku=cape`, `ro.soc.model=SM8475`, `ro.board.platform=taro`. Prefer the Motorola **oneli PVT** overlays when reconciling board DT; do not assume this uniquely identifies the final loaded DTB/DTBO without its board-ID property.
2. **Installed firmware is newer than the source research snapshot:** Android 14 fingerprint `motorola/oneli_ge/oneli:14/U2SLS34.1-42-14-11/e37c37-31202:user/release-keys`; running kernel `5.10.233-android12-9-00008-gf5ac1bdc50ed-ab13743812`, built 2025-07-07. The published Android 12 device-tree snapshot remains useful as a source reference but is not established as the precise installed DT.
3. **Locked/green boot:** `verifiedbootstate=green`, `vbmeta.device_state=locked`, `flash.locked=1`, current `slot_suffix=_a`. A native unsigned boot image has not been attempted. The locked state constrains future boot testing.
4. **USB roles:** Android's USB HAL reports dual-role Type-C with role combinations including **sink power + host data**; a separate host-manager log records attach/detach events. This is firmware-level role-capability evidence, **not** proof of an externally powered USB hub actually working.
5. **DisplayPort:** Android DRM enumerates `card0-DP-1` alongside `card0-DSI-1`, `card0-DSI-2`, `card0-Virtual-1`. DP `enabled=disabled` at capture, `status` and `modes` inaccessible; no physical display connection was tested. Connector enumeration does **not** establish a functioning signal path.
6. **Dual batteries/charging confirmed live:** Qualcomm PMIC GLINK battery supply, Motorola `mmi_battery` aggregation, main GLINK supply, flip TI BQ27426 fuel gauge on I²C `1-0055`, SGM41516D charger on `1-006b`. Stock Linux reports the charger online and the flip battery charging. Keep main and flip reporting distinct; avoid claiming that the complete Motorola battery-management policy is already supported under mainline.
7. **Device tree could not be exported completely:** root `/proc/device-tree` exists but property reads are denied to SELinux-enforcing ADB shell. Two archived attempts were verified: one symbolic-link-only, the other 83 directories and **zero property files**. Do not treat these as flattened DT blobs or resolved DT properties.

## 1. Raw identity and version evidence

| Source command/property | Exact observed value | Classification |
| --- | --- | --- |
| `getprop ro.product.device` | `oneli` | [HARDWARE-OBSERVED] |
| `getprop ro.build.fingerprint` | `motorola/oneli_ge/oneli:14/U2SLS34.1-42-14-11/e37c37-31202:user/release-keys` | [HARDWARE-OBSERVED] |
| `getprop ro.boot.hardware` | `qcom` | [HARDWARE-OBSERVED] |
| `getprop ro.boot.hardware.revision` | `pvt` | [HARDWARE-OBSERVED] |
| `getprop ro.boot.revision`; `getprop ro.revision` | `pvt`; `pvt` | [HARDWARE-OBSERVED] |
| `getprop ro.boot.hardware.sku` | `XT2251-1` | [HARDWARE-OBSERVED] |
| `getprop ro.boot.product.hardware.sku` | `dn` | [HARDWARE-OBSERVED] |
| `getprop ro.boot.product.vendor.sku` | `cape` | [HARDWARE-OBSERVED] |
| `getprop ro.vendor.product.hardware.sku.variant` | `dn` | [HARDWARE-OBSERVED] |
| `getprop ro.vendor.hw.hwrev` | `0xC000` | [HARDWARE-OBSERVED] |
| `getprop ro.board.platform` | `taro` | [HARDWARE-OBSERVED] |
| `getprop ro.soc.model` | `SM8475` | [HARDWARE-OBSERVED] |
| `getprop ro.soc.manufacturer` | `QTI` | [HARDWARE-OBSERVED] |
| `getprop ro.boot.boot_devices` | `soc/1d84000.ufshc` | [HARDWARE-OBSERVED] |
| `getprop ro.boot.slot_suffix` | `_a` | [HARDWARE-OBSERVED] |
| `getprop ro.mot.platform.build_id` | `MU-190` | [HARDWARE-OBSERVED] |
| `getprop ro.boot.hwrev` | empty (different from `ro.boot.hardware.revision`) | [HARDWARE-OBSERVED] |
| `getprop ro.boot.bootloader` | `MBM-3.0-oneli-c66ed235df0-250923-U2SLS34.1-42-14-11-e37c37` | [HARDWARE-OBSERVED] |
| `uname -a` | `Linux localhost 5.10.233-android12-9-00008-gf5ac1bdc50ed-ab13743812 #1 SMP PREEMPT Mon Jul 7 16:32:51 UTC 2025 aarch64 Toybox` | [HARDWARE-OBSERVED] |
| `ro.boot.verifiedbootstate` | `green` | [HARDWARE-OBSERVED] |
| `ro.boot.vbmeta.device_state` | `locked` | [HARDWARE-OBSERVED] |
| `ro.boot.flash.locked` | `1` | [HARDWARE-OBSERVED] |

Notes: `ro.boot.hwrev` was initially queried and returned empty; subsequent `getprop | grep` found the correct revision keys. The bootloader string embeds `250923`; its interpretation as a build date has **not** been independently verified.

## 2. Boot partitions and security

The `ls -l /dev/block/by-name` output enumerated a Qualcomm UFS-backed A/B scheme. Observed symlinks (the `/dev/block` name is part of the actual result):

| Partition | Slot A | Slot B |
| --- | --- | --- |
| boot | `/dev/block/sdd23` | `/dev/block/sdf23` |
| vendor_boot | `/dev/block/sdd25` | `/dev/block/sdf25` |
| dtbo | `/dev/block/sdd26` | `/dev/block/sdf26` |
| recovery | `/dev/block/sdd24` | `/dev/block/sdf24` |
| vbmeta | `/dev/block/sdd16` | `/dev/block/sdf16` |
| vbmeta_system | `/dev/block/sdd17` | `/dev/block/sdf17` |
| abl | `/dev/block/sdd11` | `/dev/block/sdf11` |
| modem | `/dev/block/sdd19` | `/dev/block/sdf19` |
| dsp | `/dev/block/sdd21` | `/dev/block/sdf21` |
| xbl | `/dev/block/sdb1` | `/dev/block/sdc1` |
| uefi | `/dev/block/sdd1` | `/dev/block/sdf1` |

Additional observed partitions: `super -> /dev/block/sde30`, `userdata -> /dev/block/sde31`, `metadata -> /dev/block/sde9`, `persist -> /dev/block/sde2`, `prodpersist -> /dev/block/sde3`, `devinfo -> /dev/block/sde17`, `uefivarstore -> /dev/block/sde21`, `ramdump -> /dev/block/sde32`. No partition contents were read or exported. These observed mappings describe this stock layout, not a validated native boot-image packing recipe.

## 3. Active kernel power-supply topology

`ls -l /sys/class/power_supply` showed these symlink targets:

| Supply | Underlying kernel device (abbreviated) | What this proves |
| --- | --- | --- |
| `battery` | `soc:qcom,pmic_glink/...:qcom,battery_charger/power_supply/battery` | Qualcomm firmware-backed battery supply registered |
| `usb` | `soc:qcom,pmic_glink/...:qcom,battery_charger/power_supply/usb` | Qualcomm GLINK USB power supply registered |
| `wireless` | `soc:qcom,pmic_glink/...:qcom,battery_charger/power_supply/wireless` | Wireless supply interface registered; no hardware functionality inferred |
| `main_battery` | `soc:qcom,pmic_glink/...:mmi,qti-glink-charger/power_supply/main_battery` | Motorola main battery via GLINK |
| `mmi_battery` | `soc:mmi,charger/power_supply/mmi_battery` | Motorola battery aggregation/policy node |
| `flip_battery` | `988000.i2c/i2c-1/1-0055/power_supply/flip_battery` | Physical secondary gauge at I²C address `0x55` |
| `charger` | `988000.i2c/i2c-1/1-006b/power_supply/charger` | Physical secondary charger at I²C address `0x6b` |
| `ucsi-source-psy-soc:qcom,pmic_glink:qcom,ucsi1` | `soc:qcom,pmic_glink/...:qcom,ucsi/power_supply/...` | Firmware-backed UCSI source power-supply interface |

The `1-0055` and `1-006b` addresses agree with the earlier Motorola oneli overlay analysis ([pinned reference](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-oneli-common-overlay.dtsi)). This is stronger evidence than source-only node presence, **but does not prove mainline drivers work**.

### Power-supply `uevent` snapshots

Collected on stock Android on 2026-10-11. Units are the kernel interface units, e.g. microvolts, microamps, microamp-hours and tenths of a degree C.

| Property | `main_battery` | `flip_battery` |
| --- | --- | --- |
| `TYPE` | `Mains` (reported, even though this is a battery-named supply) | `Unknown` |
| `STATUS` | `Not charging` | `Charging` |
| `PRESENT` | `1` | `1` |
| `CAPACITY` | `88` | `84` |
| `VOLTAGE_NOW` | `4022000` (4.022 V) | `4475000` (4.475 V) |
| `CURRENT_NOW` | `-292000` (-292 mA as reported) | `535000` (+535 mA as reported) |
| `TEMP` | `270` (27.0 °C) | `299` (29.9 °C) |
| `CHARGE_FULL` | `1776000` | `414000` |
| `CHARGE_FULL_DESIGN` | `2660000` | `712000` |
| `CHARGE_COUNTER` | `1555000` | `345000` |
| `HEALTH` | not supplied in copied output | `Good` |
| `TECHNOLOGY` | not supplied in copied output | `Li-poly` |
| `VOLTAGE_OCV` | not supplied in copied output | `4352000` |

Simultaneous main negative current and flip positive current are **one instantaneous observation**. They do not by themselves establish the precise interbattery transfer circuit or charging policy.

`charger/uevent` reported:

```text
POWER_SUPPLY_NAME=charger
POWER_SUPPLY_TYPE=Unknown
POWER_SUPPLY_MANUFACTURER=Texas Instruments
POWER_SUPPLY_MODEL_NAME=sgm41516D
POWER_SUPPLY_STATUS=Charging
POWER_SUPPLY_ONLINE=1
POWER_SUPPLY_HEALTH=Good
POWER_SUPPLY_VOLTAGE_NOW=4873000
POWER_SUPPLY_CURRENT_NOW=0
POWER_SUPPLY_CHARGE_CONTROL_LIMIT=0
POWER_SUPPLY_CHARGE_CONTROL_LIMIT_MAX=3
POWER_SUPPLY_INPUT_CURRENT_LIMIT=811000
POWER_SUPPLY_CONSTANT_CHARGE_CURRENT=840000
POWER_SUPPLY_CHARGE_TYPE=Fast
POWER_SUPPLY_USB_TYPE=Unknown SDP DCP CDP ACA C [PD] PD_DRP PD_PPS BrickID
POWER_SUPPLY_PRESENT=1
```

**Data-quality warning:** stock sysfs reports `MANUFACTURER=Texas Instruments` while `MODEL_NAME=sgm41516D` identifies an SGMicro charger according to the Motorola board overlay. Record this as an inconsistency in the driver-provided manufacturer string; do **not** re-identify the physical charger as TI.

`dumpsys battery` at a nearby instant: AC powered true, USB powered false, Wireless powered false, Dock powered false, status `2` (charging), health `2`, present true, level `86`, voltage `4204` mV, temperature `260` (26 °C), charge counter `1879000`, reported full capacity `2192000`, full design capacity `3372000`, charge watt `15`, charging limit `1000000` µA at `5000000` µV, cycle count `5`. Motorola health HAL present: `motorola.hardware.health@2.0::IMotHealth@Proxy`. Readings were obtained at different moments and may represent different aggregation policies; do not treat cross-command differences as contradictions.

## 4. USB-C / Type-C behaviour from `dumpsys usb`

At capture:

```text
current_functions_applied=true
connected=true
configured=true
host_connected=false
source_power=false
sink_power=true
kernel_state=CONFIGURED
port=port0
supported_modes=dual
current_mode=ufp
power_role=sink
data_role=device
can_change_mode=true
can_change_power_role=true
can_change_data_role=true
usb_hal_version=12
```

Reported allowed combinations were:
- source power + host data
- source power + device data
- **sink power + host data**
- sink power + device data

`host_manager.num_connects=6` and the supplied log shows **three paired attach/detach cycles** for `/dev/bus/usb/002/002` with reported manufacturer `8888` and product `11906` on attaches. The identity and nature of that USB device were **not** established. Current Android connection was USB gadget/device as a power sink (expected for ADB from another Android phone). These observations justify implementing USB role handling and power-role independence; they do **not** verify a powered NUC dock or kernel USB host functionality.

`ls -l /sys/class/typec` returned `Permission denied` under ADB shell; `dumpsys usb` provides the current firmware-role information instead.

## 5. DRM graphics and external display

Observed `/sys/class/drm` links:

- `card0` and `renderD128` under `/devices/platform/soc/ae00000.qcom,mdss_mdp/drm/`.
- `card0-DP-1`, `card0-DSI-1`, `card0-DSI-2`, `card0-Virtual-1`.
- `sde-crtc-0` through `sde-crtc-5`.

`cat /sys/class/drm/card0-DP-1/enabled` returned **`disabled`**. Reads of `status` and `modes` returned `Permission denied`. No monitor, HDMI adapter, DP dock, EDID or active mode was measured. Therefore `card0-DP-1` is **proof of a registered DRM connector**, not confirmed DisplayPort electrical operation. The presence of `renderD128` does not prove functioning upstream GPU acceleration.

## 6. Device-tree availability and SELinux constraints

`ls /proc/device-tree` produced root node names including: `compatible`, `model`, `soc`, `cpus`, `reserved-memory`, `firmware`, `hypervisor`, `qcom,board-id`, `qcom,msm-id`, `qcom,battery-data`, `chosen`, `memory`, `hw`, `utags`.

Reading `/proc/device-tree/model` and `/proc/cmdline` returned `Permission denied`; reading `/proc/device-tree/compatible` or numeric board-ID data was **not demonstrated**. `ls -lZ /proc/device-tree/model` returned `Permission denied`. `ls -ldZ /proc/device-tree/soc` succeeded and showed:

```text
drwxr-xr-x 560 root root u:object_r:vendor_sysfs_devicetree_soc:s0 ...
```

`id` showed `uid=2000(shell) gid=2000(shell)` with `context=u:r:shell:s0`; `getenforce` returned `Enforcing`. Hence property-read access is restricted for this shell. The precise denial mechanism (mode, SELinux policy, etc.) is **not fully isolated**. `sudo` was unavailable.

Archive attempts, verified by inspecting uploaded files:

| Attempt | Capture method | Actual archive | SHA-256 | Inspected contents |
| --- | --- | --- | --- | --- |
| 1 | `tar -czf /sdcard/Download/oneli-live-dt.tar.gz -C /proc device-tree` | `oneli-live-dt.tar.gz`, 118 bytes | `a9ecb6a4d2a223e590ff1c02b103db34c0e3003a2866d34b3c52c59a7cc66c14` | 1 symlink entry, `device-tree`; the target was not traversed |
| 2 | `tar -czf /sdcard/Download/oneli-live-dt.tar.gz -C /sys/firmware/devicetree base` | `oneli-live-dt.tar (1).gz`, ~1.7 KB | `69d307560554a0c59f62438e6cf567b06e955653d3f25bada70ae13a81ec7ee6` | **83 directories and 0 regular files** |

The second archive establishes directory names only. Examples: `base/hypervisor/qcom,gunyah-vm`, `base/reserved-memory/gpu_microcode_region@8b91a000`, `base/reserved-memory/video_region@9fd00000`, `base/reserved-memory/adsp_region@85700000`, `base/reserved-memory/cnss_wlan_region`, `base/reserved-memory/mmi_annotate_mem_region`. These names are evidence of exposed directories; numerical `@address` fragments are *node-name strings*, not verified `reg` sizes or reserved-memory semantics. `tar: write: Broken pipe` occurred only while piping an archive *listing* to `head`, and is not itself an archive-content failure.

The raw uploads were used only for audit and are **not committed** to GitHub. Retain the hashes to reconnect any later private archive.

## 7. Guidance / owners / remaining verification

| Owner | New evidence and required follow-up |
| --- | --- |
| **Coordinator** | Record that *physical device inspection on 2026-10-11 succeeded*, limited to stock ADB. Replace broad unknown board revision with **XT2251-1 PVT, hwrev 0xC000, SKU dn**, with citation to this report. Don't convert stock validation into mainline validation. Existing aggregate docs may be updated by coordinator. |
| **Boot** | Prioritise oneli PVT overlay; use running Android 14 `U2SLS34.1-42-14-11` for firmware/boot/vbmeta/DTBO acquisition; know slot A was active at capture. Preserve locked/green constraints. A real flattened DTB/DTBO was **not obtained**; board-id and msm-id property values remain unknown. Vendor boot packaging remains unverified. |
| **Power** | Live secondary gauge at I²C `0x55`, SGM41516D at `0x6b`; main Qualcomm GLINK + Motorola battery aggregator; flip charging on stock. Inspect the `Texas Instruments` vs `sgm41516D` string discrepancy and capacity aggregation only if relevant. Hardware operation on mainline remains untested. |
| **USB** | Stock port supports dual-role, including advertised sink+host; host attach/detach history exists. Preserve source-vs-observed distinction; USB2-first port is still untested. A future powered-dock test should exercise sink+host simultaneously. |
| **DisplayPort** | DP DRM connector enumerated but disabled. Actual DP signal, PS5169/repeater wiring, DP AUX mux and dock success remain untested. Continue binding/graph work from source, request on-hardware DP dock/EDID test during next device access. |
| **GPU** | DRM render node exists on stock; no native GPU performance, GPU firmware load or Mesa test was done. |
| **VPU** | Stock reserved-memory *directory names* include video and codec-related regions; no property values or stock video firmware were captured. Obtain firmware package inventory as planned. |
| **Userspace** | Stock board is ARM64/SM8475; native Debian and QEMU development remains independent of this stock Android session. |

### Next physical-device session (if one becomes available)

1. If available, test **USB-C powered dock + USB peripheral + DP/HDMI monitor** on stock Android and capture `dumpsys usb` and `/sys/class/drm/card0-DP-1/enabled` before/after; separately record whether display mode actually appears.
2. Acquire matching **official stock firmware** for the exact `U2SLS34.1-42-14-11` build, preserving source URL, downloaded archive hash, and boot/vendor_boot/dtbo header metadata. A public firmware candidate is not automatically proven to be installed firmware.
3. During the eventual unlocked native-boot phase, capture UART/USB console and boot logs, not merely Android sysfs.

## Source and reproducibility pointers

- The present report derives from the **user-supplied live ADB command outputs** and two user-uploaded device-tree archives, inspected on 2026-10-11. No publicly hosted file can replace that physical provenance.
- [Pinned Motorola oneli common overlay](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-oneli-common-overlay.dtsi) for published I²C/charger node comparison.
- [Pinned Motorola Cape SoC tree](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape.dtsi) for GLINK and UCSI layout.
- [Initial hardware database](razr2022_native_linux_hardware_database_2026-10-11.json) and [project workflow](WORKFLOW.md).

**Evidence legend:** [HARDWARE-OBSERVED] means read from actual stock phone; [SOURCE-OBSERVED] means published source, and [INFERRED] identifies an unproven interpretation. None of this is mainline hardware validation.
