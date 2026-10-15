# Motorola Razr 2022 (oneli): schematic evidence — 2026-10-15

**Evidence captured:** 2026-10-15  
**Target:** XT2251-1, oneli; user's phone is UK/RETEU, observed PVT / hwrev `0xC000` in the project's earlier stock ADB capture.  
**Schematic source:** DZKJ Schematics, `Schematics_256_MP_0616.pdf`, 84 sheets; Motorola engineering drawing project **`maven.cpm`**, rev **03**, dates shown 2022. User inspected the source in DZKJ and supplied screenshots of the pages below.  
**Evidence classification:** **Schematic-confirmed** means documented for the reference design, *not* that the exact revision is populated on the user's PVT handset or that native Linux was tested. Stock Motorola DT/ADB evidence is independent and noted when it corroborates a schematic connection.  
**Handling:** Some screenshots bear a Motorola confidential/restricted legend. This report records derived technical observations without embedding or redistributing those drawings. Check redistribution permissions before posting the source screenshots to a public repository.

## Provenance and correction authority

Coordinator read the auditor's derived report `razr2022_oneli_schematic_findings_2026-10-15.md` and the user's subsequent explicit endpoint transcription in this project conversation (2026-10-15, approximately 20:03 Europe/Lisbon). Coordinator has not independently inspected the complete schematic or verified these endpoints on the handset. “Schematic-confirmed” below denotes the auditor/user's inspection of the reference drawing, not a new coordinator measurement. Original PDF and screenshot images are not included in this repository.

The follow-up explicitly corrects **CHG_EN from GPIO1 to PM8350C GPIO2, pin 134** and adds UART/battery endpoints below. Preserve PM8350, PM8350C and PM8350BH names as drawn; do not silently substitute one provider for another. Mapping schematic package labels to Linux PMIC nodes and GPIO numbering is an implementation review, not an assumed identity.

## Executive decision

The two previously unknown USB/DisplayPort IC identities are now documented. More importantly, the **PM8350/PM8350C actual regulator input topology** and a **specific flip-battery power-path switch** are identified. Coordinator should update the hardware evidence database and replace corresponding `[INFERRED]` board-wiring entries with **schematic-derived** entries, while retaining separate effective-PVT and runtime validation gates. These discoveries warrant bounded USB/DP/Power/Boot review, **not** immediate hardware enablement or a blanket agent round. Existing accepted integration remains unchanged.

## 1. Identification and interface facts

| Function | Schematic evidence | Project implication |
| --- | --- | --- |
| **USB eUSB2 repeater** | **U1720 = NXP `PTN3222BUK`**, **sheet 68/84**, block `USB_REPEATER 1720-1749`; printed **7-bit I²C address `0x4F`**. `EDP/EDN` from `EUSB0_HS_DP/DM`, `DP/DN` to `USB0_HS_DP/DM`, `APPS_I2C_SDA/SCL` on pins A2/A3. `ADDR` strapped to ground through **0 Ω** (R1721). | Confirms the exact PTN3222 **BUK** variant and I²C address. This is no longer an unknown/generic NXP compatible at the **schematic** level. Existing isolated upstream-PTN3222 adaptation is the right reuse direction. |
| Repeater power/reset | **Sheet 68:** U1720 `VDD1V8` = `VREG_S10B_1P8`; `VDD3V3` = `VREG_L2B_3P07` (the schematic labels the nominal rail **3.07 V**, despite the VDD3V3 pin name); reset net = **`EUSB_RPTR_RST_N`**, active-low at chip pin `RST_N`. **PM8350C CTRL/GPIO** schematic shows **PM8350C GPIO7** on the reset net. | Confirms the two rail endpoints and physical reset-signal polarity, already suggested by Motorola DT. The Linux GPIO descriptor logical polarity must be reconciled against active-low `RST_N` and vendor active-high DT flags; do not copy the flag mechanically. |
| **Separate DisplayPort AUX/SBU switch** | **U4500 = `WAS7227Q-10/TR`** (sheet **8/84**, `DP: DP AUX SWITCH`). Pin 9 VCC from `VREG_L2B_3P07` via 0 Ω R4500; pin 3 GND. `USB_SBU1/SBU2` to pins 1/2; `DP_AUX_P/M` on switched outputs. Control: **pin 8 `OE_N`** = `AUX_SW_OE_N` (active-low enable); **pin 10 `SEL`** = `AUX_SW_FLIP`. | Resolves the previously unknown AUX IC and supports a GPIO-controlled switch model. This is **not the PS5169**, and the stock oneli DT explicitly disables the inherited FSA4480 node. Check existing Linux `gpio-sbu-mux` compatible/binding for this exact part before requesting a new binding; no new I²C switch driver is indicated. |
| AUX GPIO mapping | Motorola stock four-DTBO audit already maps `mmi,aux-switch-enable-gpio` to **TLMM GPIO2** and `mmi,aux-switch-flip-gpio` to **TLMM GPIO71**. Vendor truth table: disable `(1,0)`, CC1 `(0,0)`, CC2 `(0,1)` for `(enable,flip)`. | Schematic pins/active-low naming corroborate software GPIO mapping. Still requires a reviewed DT binding/connector graph and on-device DP test. |

**Important PTN3222 variant check:** The isolated `Drzet/linux:razr/usb-ptn3222@61202a82` currently accepts chip-ID constants named **CUK** (`0x023222`) and **HUK** (`0x013222`). The schematic explicitly states **BUK**. **Do not assume** the BUK's reported register ID must be distinct or must match either accepted constant: check the BUK register-ID specification or read-only identity before enabling a strict reject-on-ID path. An otherwise correct driver could refuse to probe the fitted board. This is a *focused compatibility review*, not grounds for a new driver.

## 2. Power input topology: material new Boot/Power evidence

All entries below are **wires directly visible in the reference schematic**, not voltages measured on the handset.

| IC / diagram | Regulator input source(s) seen | Outputs/notes |
| --- | --- | --- |
| **PM8350C BOB/FLASH** | `B_PLUS` → PM8350C `VDD_BOB` | PM8350C's buck-boost (`BOB`) generates **`VREG_BOB`**. The diagram explicitly labels the BOB input as `B_PLUS`. |
| **PM8350 LDOs/GND** | **L1/L4 and L3/L5 ← `VREG_S11B_0P95`**; **L2/L7 ← `VREG_BOB`**; **L6/L9/L10 ← `VREG_S12B_1P25`**; **L8 ← `VREG_S2H_0P95`**. | This differs from any simplistic copy of another Qualcomm development-board parent topology. Supplies for UFS and the eUSB repeater can now be traced against concrete board sources. |
| **PM8350C LDOs/GND** | **L1/L12 and L2/L8 ← `VREG_S1C_1P86`**; **L3/L4/L5/L7/L13 and L6/L9/L11 ← `VREG_BOB`**; **L10 ← `VREG_S12B_1P25`**. | Replaces previously inferred upstream HDK group-parent inputs with reference-schematic connections. Note, in particular, **L8C** is supplied by **S1C**, not by BOB. |
| **PM8350 BUCKS, sheet 72/84** | Buck/SMPS inputs originate at **`B_PLUS`**. | Outputs include **`VREG_S10B_1P8`**, **`VREG_S11B_0P95`**, **`VREG_S12B_1P25`**, tying directly into the LDO parent tree and repeater 1.8 V supply. |
| **PM8350C BUCKS** | Buck/SMPS inputs originate at **`B_PLUS`**. | Outputs include **`VREG_S1C_1P86`**, plus SoC MXC/CX and other SMPS rails. |
| **PM8350 / PM8350C CTRL/GPIO** | Their `VPH_PWR`/`VPH_PWRx` input pins visibly tie to **`B_PLUS`**. | Confirms B_PLUS is the physical high-level input distribution, **not** a fixed-voltage `vph_pwr` source. PM8350C control page shows `CHG_EN` on **GPIO2, pin 134** (user's follow-up correction; the auditor's initial GPIO1 transcription is superseded) and `EUSB_RPTR_RST_N` on GPIO7. |

**Practical Boot consequence:** Earlier Power analysis marked grouped PMIC parent supplies **[INFERRED]** from SM8450 HDK. We now have oneli **schematic-level** input-source evidence and can reconcile `vdd-*-supply` relationships for PM8350/PM8350C without inventing fixed battery voltage. **Do not automatically change regulators to enabled or hard-code an always-on 3.7 V source.** Parent topology still needs to be expressed in the correct RPMh binding/provider design and checked against the actual PVT board variant.

## 3. Dual-battery / charger circuitry

| Schematic item | Evidence | Consequence |
| --- | --- | --- |
| **Flip charger** | Block `CHARGER: SMG41516D` (heading spelling as printed); silicon U500 clearly marked **`SGM41516D`**. `USB_VBUS` feeds its input; charging output is **`BATT_FLIP`**. Lines include `CHG_EN`, `FLIP_CHG_INT_N`, and `CHG_I2C_SDA/SCL`; reference **1.8 V S10B** for pullups. | Confirms physical flip charger / power inlet and control wiring, consistent with stock DT and Android driver. No direct inference that generic SGM41542 driver safely implements Motorola's two-battery policy. |
| **Main charging PMIC** | `PM8350BH: CHARGE/FG/OLEDB`, sheet **81/84**. Main USB VBUS/CC and charging/power circuitry are integrated into this PMIC. | There are **separate main and flip charging paths**, so the Linux policy should not treat the SGM charger as the entire system charging solution. |
| **Flip battery bridge/power switch** | **Sheet 19/84**, `BRIDGE: CONNECTORS`: dedicated **U900 = `WS4695C-12`** switch, with `BATT_FLIP` on its input, output joined to **`PM8350_BATT` / `BATT_PLUS_BASE`** rail, and dedicated **`FLIP_BATTPLUS_EN`** control. Nearby **Q902/Q903** form additional MOSFET balancing/switching circuitry driven by **`FLIP_BALANCE_EN_N`**; connector includes battery voltage sense. | A material identification beyond the charger itself. The project must preserve appropriate load/balancing-switch ownership, sequencing and fail-safe behavior; **do not simply enable the SGM charger in isolation**. The presence of circuit elements in the drawing does not prove every optional/DNI part is populated. |


## 4. Follow-up: UART and battery control endpoints

User-transcribed schematic findings, 2026-10-15. Individual sheet numbers for these endpoint crops were not supplied; do not invent them.

| Signal | Endpoint / component | Evidence limit |
| --- | --- | --- |
| `CHG_EN` | **PM8350C GPIO2, pin 134** | Corrects initial auditor GPIO1 entry; agrees with the existing Power stock-source GPIO2 record. Electrical polarity still follows the complete circuit/driver contract, not the net name alone. |
| `FLIP_BALANCE_EN_N` | **PM8350BH GPIO1, pin 114** | Physical endpoint reported; preserve BH designation when reconciling older source's PM8350B label. |
| `FLIP_BATTPLUS_EN` | **PM8350BH GPIO3, pin 139** | Control for the bridge/load-switch circuit described above. |
| Balance-control pull-down | **R909, 470 kΩ** in earlier bridge schematic | Pull-down reported; does not alone establish the complete power-path default state or software sequencing. |
| `SDM_DBG_UART_TX` | **SM8475 GPIO26, ball D24** | Application-processor debug TX net reported. |
| `SDM_DBG_UART_RX` | **SM8475 GPIO27, ball C24** | Application-processor debug RX net reported. |

**UART unresolved:** physical test points/connector/access pads and voltage domain were not identified. Do not infer a 1.8 V or 3.3 V receiver level. Reconcile GPIO26/27 with the existing GENI UART7/pinctrl configuration before claiming the current console reaches these nets. No UART bytes received or native boot demonstrated. Loader RAM-map/placement/DT/ramdisk gates remain separate.

**Battery ownership:** the three physical control endpoints are now recorded; no further generic endpoint search is required. Linux provider identity, polarity/numbering, PMIC-firmware versus AP ownership and paired-pack sequencing still require source reconciliation. No charge or balance control writes are authorized by this evidence record.

## 5. Disposition requested from coordinator (minimal, ordered)

1. **Evidence update only:** Record U1720 `PTN3222BUK`, U4500 `WAS7227Q-10/TR`, U900 `WS4695C-12`, and the physical PMIC parent-rail matrix above in the shared hardware database/status or one canonical review. Cite **DZKJ Motorola `maven.cpm` rev03 `Schematics_256_MP_0616.pdf`, sheets 8, 19, 68, 72, 81** and the exact named PMIC drawings. Mark **schematic-confirmed, installed-PVT unverified**.
2. **USB bounded selection:** Check **BUK register identity** against candidate CUK/HUK ID-check policy and confirm physical `RST_N` polarity under Linux descriptors. Retain accepted isolated `61202a82` candidate and existing PS5169 work; no new USB driver or immediate active shared DTS.
3. **DisplayPort bounded selection:** Use **WAS7227Q-10/TR** to decide an attributable part-specific `gpio-sbu-mux` binding (or existing exact match), active-low enable/select semantics, GPIO2/71 ownership, and `connector@0/port@2` graph. Keep FSA4480 disabled. Actual DP attach/EDID/wake test remains later.
4. **Power/Boot bounded selection:** Reconcile the **schematic-derived PM8350/PM8350C parent group matrix** against qcom RPMh regulator schemas and Boot's disabled oneli DTS. Separately record **WS4695C-12** and MOSFET balancing controls for the dual-pack charging implementation. Preserve staged/disabled consumers until owner-reviewed.
5. **Do not re-open solved work:** No need for a new firmware extraction, repeated generic upstream audits, probing unreviewed register writes, or a blanket multi-agent implementation round. Existing VPU calculator/OPP/IOVA gates and native bootloader/phone runtime remain **independent** of these schematic findings.

## Existing corroborating project and source references

- [Power rail contract v2](https://github.com/Drzet/razr2022_nuc/blob/razr/power/docs/power_oneli_rail_contract_v2_2026-10-11.md): lists earlier **HDK-inferred** PMIC parent mappings needing replacement where the schematic differs.
- [DisplayPort four-DTBO AUX matrix](https://github.com/Drzet/razr2022_nuc/blob/razr/displayport/docs/displayport_oneli_four_dtbo_aux_matrix_2026-10-11.md): stock GPIO2/71 and explicit FSA4480 disablement.
- [PTN3222 experimental kernel candidate](https://github.com/Drzet/linux/blob/61202a82ad004302fcc04e321075e190f00b29ed/drivers/phy/phy-nxp-ptn3222.c): existing CUK/HUK identity check and oneli profile.
- [PTN3222 coordinator review](https://github.com/Drzet/razr2022_nuc/blob/main/docs/USB_REVIEW_2026-10-14.md): tested, offline-accepted lifecycle adaptation, not integrated.
- [Power charger/policy review](https://github.com/Drzet/razr2022_nuc/blob/razr/power/docs/power_oneli_sgm41516d_policy_stock_review_2026-10-12.md): Motorola dual-pack regulation and switch-control dependencies.
- [Current authoritative queue](https://github.com/Drzet/razr2022_nuc/blob/main/docs/NEXT_TASKS.md), [status](https://github.com/Drzet/razr2022_nuc/blob/main/docs/STATUS.md): only assigned tasks may trigger implementation, and the on-device boot/integration claims remain untested.

Essential board identification/source-wiring reconnaissance is recorded for this round; UART physical access and voltage remain unresolved. The report supplies actionable *design evidence*, not a green light for active rails, charging or USB/DP under native Linux.

## Coordinator disposition

Current assignments are exclusively in [NEXT_TASKS](NEXT_TASKS.md). This evidence supersedes earlier unknown-part and HDK-inferred wiring statements only for the reported reference design. Historical reviews and the 2026-10-11 database remain dated source snapshots. No driver, shared DTS, accepted integration or diagnostic artifact changed in this documentation update.
