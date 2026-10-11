# Motorola oneli: PMIC GLINK, dual-battery and thermal audit

2026-10-11 | Power workstream | Evidence: **source audit and synthetic fixtures only**, not connected-device compatibility.

Kernel baseline `Drzet/linux@a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. Boot dependency `cb9105ebeb9485e31d044d4fa69396b415523669`. Actual phone firmware and board revision unavailable. No charging/thermal driver modifications or active device-tree changes are authorized by this audit.

## Pinned primary sources

- Motorola Qualcomm battery-charger client: [`qti_battery_charger.c`](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/9511d6b2dc469e5bd836992e3bdd6d19ace112e0/drivers/power/supply/qti_battery_charger.c) (opcodes/structs lines 24–218; notifications 747–810; sysfs battery/USB 930–1166; `combo_batt_psy` 1272–1282).
- Motorola GLINK transport: [`drivers/soc/qcom/pmic_glink.c`](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/9511d6b2dc469e5bd836992e3bdd6d19ace112e0/drivers/soc/qcom/pmic_glink.c) and [vendor GLINK header](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/9511d6b2dc469e5bd836992e3bdd6d19ace112e0/include/linux/soc/qcom/pmic_glink.h).
- Baseline upstream: [`drivers/power/supply/qcom_battmgr.c`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/power/supply/qcom_battmgr.c), [`drivers/soc/qcom/pmic_glink.c`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/soc/qcom/pmic_glink.c), [GLINK header](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/include/linux/soc/qcom/pmic_glink.h).
- Board evidence: [oneli overlay](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-oneli-common-overlay.dtsi), [Moto charger policy](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/waipio-moto-common-charger.dtsi), [charger limit override](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/waipio-li-charger-overlay.dtsi), [PMIC thermistor channel definitions](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-pmic-overlay.dtsi), [oneli thermal overlay](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-oneli-thermal-overlay.dtsi).

The Motorola kernel-msm source here is the pinned **generic/vendor reference**. Some oneli-specific modules (notably `mmi,mmi-charger`, discrete charger and pairing integration) are *not contained in the inspected `kernel-msm/drivers/power/supply/` listing*. Therefore the presence of their oneli DT properties does not prove a particular Motorola code implementation or wire payload extension in this pinned kernel tree.

## A. GLINK owner and packet layout

Both source GLINK headers define three 32-bit fields `owner`, `type`, `opcode` (12 bytes). Motorola uses native `u32`, upstream explicit `__le32`. The shared owner is decimal **32778** (`MSG_OWNER_BC` vs `PMIC_GLINK_OWNER_BATTMGR`), request-response type is **1**, notification type **2**. An observed wire-endianness capture is unavailable. [INFERRED] Little-endian byte ordering is appropriate on the target ARM64 platform, but only source-level correspondence was tested.

| Message | Vendor opcode | Mainline opcode | Payload after 12-byte header | Source-level disposition |
| --- | --- | --- | --- | --- |
| Enable notification | `BC_SET_NOTIFY_REQ` = `0x04` | `BATTMGR_REQUEST_NOTIFICATION` = `0x04` | Request four u32 (battery_id, power_state, low_capacity, high_capacity), 28 bytes total | Same request struct |
| Notification | `BC_NOTIFY_IND` = `0x07` | `BATTMGR_NOTIFICATION` = `0x07` | One u32 notification ID, 16 bytes total | Common battery/USB/WLS notification codes; firmware events untested |
| Battery get | `BC_BATTERY_STATUS_GET` = `0x30` | `BATTMGR_BAT_PROPERTY_GET` = `0x30` | Request battery_id, property_id, value (24 total); integer response property_id, value, result (24 total) | Same integer wire layout |
| Battery set | `BC_BATTERY_STATUS_SET` = `0x31` | `BATTMGR_BAT_PROPERTY_SET` = `0x31` | Same numeric request/reply format | Upstream defines opcode but no SM8350-style SET reply switch case in inspected callback; supported writable surface differs |
| USB get | `BC_USB_STATUS_GET` = `0x32` | `BATTMGR_USB_PROPERTY_GET` = `0x32` | Same numeric layout | IDs 0..9 agree |
| USB set | `BC_USB_STATUS_SET` = `0x33` | `BATTMGR_USB_PROPERTY_SET` = `0x33` | Same numeric layout | Upstream has no corresponding SM8350-style SET reply switch case |
| Wireless get | `BC_WLS_STATUS_GET` = `0x34` | `BATTMGR_WLS_PROPERTY_GET` = `0x34` | Same numeric layout | IDs 0..6 agree |
| Wireless set | `BC_WLS_STATUS_SET` = `0x35` | `BATTMGR_WLS_PROPERTY_SET` = `0x35` | Same numeric layout | Upstream has no corresponding SM8350-style SET reply switch case |

**Independent source comparison:** eight opcode values match. **41 common property IDs match**: all 24 vendor battery properties (`BATT_STATUS` through `BATT_POWER_AVG`, IDs 0–23), ten USB fields (0–9), seven wireless fields (0–6). Test program: [`tools/power/glink_protocol_audit.py`](../tools/power/glink_protocol_audit.py), with six synthetic wire fixture tests.

**Not equal to complete protocol compatibility:**

- Vendor USB field enumeration continues `USB_TEMP`=10, `USB_REAL_TYPE`=11, `USB_TYPEC_COMPLIANT`=12. Baseline `qcom_battmgr` defines only USB IDs 0–9, exposes no USB temperature property on the SM8350 path, and does not reproduce those vendor extension fields.
- Upstream adds battery IDs `BATT_CHG_CTRL_EN`=24, `BATT_CHG_CTRL_START_THR`=25, `BATT_CHG_CTRL_END_THR`=26 and charge-control opcode **`0x48`**. The pinned vendor QTI implementation does not define those properties or opcode. Do not assume the target firmware understands or implements the threshold interface.
- Vendor `BC_GENERIC_NOTIFY`=0x80 is interpreted as a battery change notification. Upstream `NOTIF_BAT_STATUS`=0x80 also causes a battery supply change; semantic interpretation beyond triggering a refresh has not been verified.
- Vendor `handle_message` accepts the `0x04` notification-setup acknowledgement without a payload-length test. Upstream SM8350 callback requires **at least one 32-bit payload field** before any opcode dispatch. **[INFERRED]** If the actual firmware returns a 12-byte header-only ACK, upstream discards it and times out. Check response lengths in a future passive trace; do not assert it happens on oneli.
- The vendor `qti_battery_charger.c` responds to set opcodes `0x31`, `0x33`, `0x35`; mainline `qcom_battmgr` on the SM8350 path has no matching SET response cases. Existing threshold request `0x48` follows a different path. This needs a separate software interface design rather than changing opcode meanings.
- Signed temperature conversion: vendor casts raw battery/USB temperature to signed `int` before `DIV_ROUND_CLOSEST(...,10)`; upstream SM8350 battery callback assigns `le32` to `unsigned int val` and divides by ten. **A negative two's-complement temperature would be decoded differently**; a hypothetical -201 raw reads -20 on the vendor path. The fixture tests the signed conversion, **not an oneli sensor measurement**.
- The upstream `qcom_battmgr_charge_control_thresholds_init` reads NVMEM keys at probe but no charge-control write occurs on a missing optional NVMEM cell. Do not invent charge-limit NVMEM storage for oneli or assume the vendor 65/80% charging policy has migrated.

### Reproduce protocol/fixture validation

Fetch the exact two pinned C files above locally, preserving revisions, then run:

```sh
python3 tools/power/glink_protocol_audit.py \
  --vendor /path/to/vendor/drivers/power/supply/qti_battery_charger.c \
  --upstream /path/to/linux/drivers/power/supply/qcom_battmgr.c
```

The script prints compared opcode values, counts IDs, exits nonzero on a detected common-definition mismatch, and runs **six synthetic fixture cases**: property request (24 bytes), integer response (24), notification (16), subscribe (28), signed/unsigned temperature conversion and truncated packet length. No live device traffic or proprietary firmware is used. The 8/41 source result was independently reproduced directly against the pinned GitHub connector file contents; the six fixture operations were reproduced with Python `unittest` (6 passed). Executing the **exact committed script with downloaded original C files** and a kernel build has **not** been recorded in this session; do not mislabel this as a CI run.

## B. Dual battery: observed dependency versus missing policy

From [oneli's exact DT](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-oneli-common-overlay.dtsi#L194-L289):

| Element | Source-backed DT configuration | Does baseline Linux implement oneli policy? |
| --- | --- | --- |
| Main battery | `mmi,qti-glink-charger`: `mmi,main-battery-enabled`, paired ID `0x00010000`, `mmi,shutdown-empty-vbat-mv=3000`; generic PMIC GLINK child | Generic GLINK battery read path exists; Motorola pairing/mode policy not shown in mainline |
| Flip gauge | `ti,bq27426` at I²C `0x55`, IRQ TLMM43; vendor profile `NM40_ATL_712MAH`; `design-capacity=712`; `mmi,temp-source=1`, `mmi,ibat-invert-polority` | Mainline BQ27426 match exists, but these `mmi,*` profile/current/thermal-source properties are **not** automatically handled by that compatible |
| Alternate flip gauge | `cellwise,cw2217` at `0x64` | Explicitly **disabled** in vendor oneli overlay; do not enable it concurrently |
| Flip charger | `sgm,sgm41516D` at `0x6b`, IRQ TLMM51, charge EN PM8350C GPIO2 active-low; `init-charger-disabled` | Mainline SGM41542 driver has a **different** exact compatible and chip detection; no verified 41516D match |
| Battery pairing/load | Flip `paired-id=1`; PM8350B GPIO1 low-load and GPIO3 high-load; paired OCV/current mapping and load thresholds | Vendor-only policy; no equivalent baseline pair/load manager identified |
| Combined capacity | `&battery_charger` references `&mmi_charger` with `mmi,combo-batt-psy` | Vendor QTI client explicitly obtains power supply by this phandle; for capacity, status, current, full/counter it delegates to combined battery supply. Mainline registers generic `qcom-battmgr-bat` without that `mmi` combined supply |
| Charge thresholds | `mmi_charger`: lower 65%, upper 75% common, upper overridden to 80% by oneli | Mainline exposes optional threshold interface, but Motorola user policy and vendor opcode support have **not** been confirmed |

The paired charging/current data are **literal vendor policy tables**, not registers to transfer directly into a generic SGM charger driver. In oneli the charger table includes `mmi,mmi-temp-zones` with six quadruples, `mmi,paired-ichg-table` with four pairs, `mmi,paired-load-thres=<800 400>`, and `mmi,thermal-mitigation=<900000 600000 300000>`. Exact application semantics require the correct Motorola pairing source or hardware traces. No unsupported SGM compatible alias is proposed.

## C. Thermal-source mapping

The oneli source wires `&pmk8350_adc_tm` through shared `cape-pmic-overlay.dtsi`, and oneli's thermal override selects these existing vendor channels:

| Vendor thermal zone | Source sensor / SPMI ADC channel | Recorded state and caveat |
| --- | --- | --- |
| `msm-therm` | PM8350 THM1 100K pullup | Defined, with 125000 m°C vendor passive placeholders |
| `schg-therm` | PM8350 THM2 100K pullup | Defined |
| `chg-therm` | PM8350 THM3 100K pullup | Defined; **not** identical by naming alone to flip gauge battery temp |
| `wifi-therm` | PM8350 THM4 100K pullup | Defined |
| `cam-therm` | PM8350 THM5 100K pullup | Defined |
| `quiet-therm` | PM8350B GPIO2 100K pullup | Defined |
| `xo-therm` | PMK8350 XO thermistor channel | Source inherits vendor XO zone; overridden trip values 88/90/100°C |
| `skin-msm-therm`, `camera-therm`, `hot-pock-therm`, `rear-cam-therm`, `tof-therm`, `wlc-therm` | Per original shared PMIC channels | Explicitly **disabled** in oneli override where specified |

Upstream `pmk8350.dtsi` provides `pmk8350_vadc` and `pmk8350_adc_tm`, but `pmk8350_adc_tm` is disabled by default. Describing the exact ADC channels against mainline bindings precedes activating board zones. Mainline TSENS and PMIC die thermal alarms are already available at the infrastructure level. The vendor's repeated 125°C passive trips and modem/QMI cooling maps are **not** proof of an effective Linux CPU/GPU cooling policy.

The `mmi,temp-source=<1>` property appears on the **flip BQ27426**. Its numeric meaning is **unresolved**: the inspected pinned `qti_battery_charger.c` and upstream BQ27xxx code do not establish what `1` selects. **Do not relabel it 'battery NTC', 'charger ADC' or 'die sensor' without the source that consumes this vendor property.** Likewise the `mmi,mmi-temp-zones` table should not be used to program Linux thresholds until its consuming implementation and units are pinned. Hardware test deferred.

## D. Driver gaps and bounded next action

1. **Boot owns DTS:** review [source-backed rail proposal](power_oneli_regulators_2026-10-11.md); add separate disabled PM8350/PM8350C regulator candidates, reconcile parent supplies, schema-check, then selectively enable UFS before more peripherals. No validated physical input supply model exists.
2. **Power and USB jointly own GLINK telemetry contract:** use `qcom,sm8450-pmic-glink`/generic fallback only as **[INFERRED]** binding-compatible proposal; confirm ADSP `msm/adsp/charger_pd` lifecycle and read-only basic `power_supply` properties before enabling writes. USB owns connector graph, role and orientation. No Motorola-specific oneli notification/charge-limit behavior proven.
3. **Power owns pairing and charger implementation:** find a *pinned* SGM41516D downstream driver, exact compatible, reg map, chip-ID readout, and paired battery manager; implement bindings/driver without unproven 41542 alias. Preserve gauge and disabled CW2217 evidence.
4. **Power + Boot/GPU share thermal integration:** translate verified TSENS/PMIC ADC sensors and cooling device hooks; retain disabled placeholders; only test actual cooling and charge throttling on hardware later.
5. **No code merged / no runtime claim:** every tested fact above is read-only source parsing or synthetic host-side fixtures.

**Acceptance status:** regulator proposal complete; source opcode/property comparison complete; GLINK/charging/thermal gap table complete; device runtime and full scripts-in-CI validation deferred. 
