# USB fifth-round: source-backed oneli PS5169 profile and probe lifecycle

Date 2026-10-13. This is a deliberately **disabled-board experimental candidate**, not a new native hardware result. Fifth-review assignment [FIFTH_ASSIGNMENTS.md](https://github.com/Drzet/razr2022_nuc/blob/main/docs/FIFTH_ASSIGNMENTS.md), despite the later ninth-review scheduling queue. User explicitly requested execution of these queued tasks.

## Pinned inputs and contract

- Motorola stock reference archive: public Android14 `U2SLS34.1-42-14-11`, ZIP SHA256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`, VPU extraction [run 38220276125](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125). Uncomposed six-FDT JSON SHA256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`; compact [summary](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-12-oneli-stock-fdt-properties.json). Four stock DTBOs contain **identical 27** `config-seq` register/value/delay triplets, not 29. See [USB per-variant evidence table](usb_stock_pvt_variant_ps5169_2026-10-12.md).
- Vendor behavior comparator: [MotorolaMobilityLLC/kernel-msm @0450c5076a8ec9415a10888c8c183ef6ff5f91b8:drivers/usb/misc/ssusb-redriver-ps5169.c](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/0450c5076a8ec9415a10888c8c183ef6ff5f91b8/drivers/usb/misc/ssusb-redriver-ps5169.c), source Git blob `01ca89030bfd830c777d96efe67e8d0889235e5c`. Its `ssusb_redriver_enable_chip` drives GPIO19 **high to enable**, delays 10ms, and low to disable. `config_seqs_init` calls `regmap_register_patch` on the vendor array, followed by a config active-bit update. Vendor's suspend/resume policy is detailed below.
- Device reference: overlays index 0-3, last is observed PVT hwrev `0xc000` *candidate*, not confirmed installed FDT; NXP repeater 0x4f selected (local status absent, ancestor `ok`), Diodes 0x6c disabled, PS5169 0x30 `ok`. NXP supply symbols S10B/L2B; PS5169 S10B/L8C. No exact soldered NXP SKU/active runtime wiring proven.

## New driver architecture

Kernel `Drzet/linux:razr/usb-ps5169`; source path `drivers/usb/typec/mux/ps5169.c`, binding `Documentation/devicetree/bindings/usb/parade,ps5169.yaml`.

A board **compatible pair** `"motorola,oneli-ps5169", "parade,ps5169"` selects a private compile-time `struct ps5169_reg_init { u8 reg; u8 value; u16 delay_us; }` array. The driver does **not** consume Motorola's untyped `config-seq` vendor ABI. The 27-entry table is a pinned *source comparator*, not proof that every register meaning is identified or that hardware accepts this profile. The original generic `parade,ps5169` path remains unchanged as a separate generic EQ/gain configuration. The Motorola profile expressly excludes generic EQ/gain/LFPS overrides in both binding and runtime to prevent conflicting partial tuning.

**Field-class translation and unsupported residue** (full numeric order/raw triplets are in the linked per-variant evidence table):

| Vendor entries | Known upstream decoded fields | Disposition |
| --- | --- | --- |
| #1-2, `0x9d=0x80` delay `10000us`, then `0x9d=0` | No verified register field | Preserve exact writes/order/delay as `PS5169_ONELI_PROFILE_CONTROL_9D`; do not call an external GPIO reset pulse |
| #3 `0x40=0x80` | Bit 7 of configuration register | `PS5169_CONFIG_REG`, later SAFE/USB/DP mode writes remain separate |
| #4-5 `0x8d=1`, `0x90=1` | USB RX LFPS register bits | Name both register addresses; use full OEM values not re-derived generic toggle |
| #6-10 `0x51=0x87,0x50=0x20,0x54=0x11,0x5d=0x66,0x52=0x50` | Shared USB RX/TX/DP EQ registers | Source-named decoded register classes; full values remain exact |
| #11-17 `0x55..0x5b=0` | Unverified field meaning | Preserve numeric register addresses, do not fabricate driver knobs |
| #18 `0x5e=7` | DP EQ | Name register class; full value |
| #19-24 `0x5f=0,0x60=0,0x61=3,0x65=0x40,0x66=0,0x67=3` | Unverified fields | Preserve exact values and ordering |
| #25 `0x75=0x0c` | Unverified field | Preserve numeric register |
| #26-27 `0x77=0,0x78=0x7c` | USB RX EQ | Full OEM values |

`ps5169_apply_oneli_profile()` writes one entry at a time with checked `regmap_write` and `usleep_range(10000,11000)` after #1. Failure aborts immediately. After rails, GPIO enable, ID/revision and profile checks, the probe applies the table, programs and verifies its SAFE mode, and **only then** exposes the Type-C switch/retimer callbacks. A failure returns an error and unwinds registered devices, GPIO enable, bulk regulators and acquired mux/switch dependencies. Original Esteban Urrutia external v3 driver/binding authorship is preserved on their original ancestor commits; oneli changes are separate USB-authored commits.

**Boundaries:** A fixed driver profile selected by board compatible is attributable but not a complete register-field definition. Exact 0x9d meaning, zero-cleared OEM residue and analog/electrical compatibility remain a review hold; activating the profile on a board requires review of these bytes and powered testing. Do not claim `parade,*-eq-db` is equivalent to this table or infer reset from 0x9d.

## True lifecycle testing, not only code-string checks

A new `scripts/razr/ps5169-probe-fault-injection.py` compiles **the actual function bodies** `ps5169_probe`, `ps5169_remove`, `ps5169_init`, `ps5169_set`, `ps5169_write`, `ps5169_eq_from_dt` and the real 27-entry profile into a userspace executable with fault-injectable kernel-service shims. Independent test reference lists all 27 triplets. It exercises acquisition failures, regulator enable failures, chip ID and revision errors, bridge/typec registration failures, writes after actual mock rail power-up, cleanup (GPIO low, rails off, release of mux/switch, unregister) and *fresh reprobe after each injected write failure*. The earlier `ps5169-fault-injection.py` retains switch/mux/SVID/EQ transition tests.

This verifies **production function control flow** against deterministic injected errors, not actual kernel I²C/regulator implementations, managed resource disposal, devres teardown, hardware GPIO timing or silicon responses. `regulator_bulk_enable`'s internal partial-supply rollback remains a kernel-provider implementation rather than simulated electrical behavior. These limits are explicit. The dedicated [fault and ARM64 workflow](https://github.com/Drzet/linux/actions/workflows/razr-ps5169-fault-ci.yml) provides actual job conclusions, exact source SHA, logs and linked module hashes when successful.

## GPIO19 and suspend/resume disposition

Motorola reference code drives active-high **enable** on GPIO19. The oneli profile uses `enable-gpios = <&tlmm 19 GPIO_ACTIVE_HIGH>` (separate from original upstream `reset-gpios` contract), asserted after both supplies with a 10ms settling delay. GPIO91 is vendor read-only orientation; Boot's PMIC GLINK remains its sole native controller. No mainline oneli board PS5169 node is enabled. Separate eUSB2 NXP reset is PM8350C GPIO7; no conflation.

Pinned vendor `redriver_i2c_suspend`: **USB3 or USB3+DP** drives enable low; **DP-only**, NONE and default skip; `redriver_i2c_resume` mirrors that condition and reasserts enable, then **replays the full config sequence and mode**. Original vendor return paths ignore some I²C errors and manage UCSI retry separately. A native PM implementation must use mutex-protected Type-C state, distinguish DP-only retention, establish when regulator/enable actually lose power and replay the *whole* 27-entry profile and mode on resume; any failing restore must invalidate cached state and surface or retain errors for retry. Ordering relative to UCSI/Type-C wake, live DP session, regulator suspend states and rail parents is **not source-established** for this mainline driver. The safe candidate **does not add suspend disable/re-enable callbacks** and holds its supplies and active-high enable during the normal system lifetime. This is a deliberate scoped PM hold, not proof that deep-suspend power retention is guaranteed.

## Integration/acceptance

No modification to Boot-owned shared SoC/board DTS or accepted `razr/integration` `2b5acf108ae37040ac1e652e029bb37f5609e886`. VPU and display path remain independent. Additional enablement requires Boot/Power confirmation of full node/pinctrl/supply parents, PS5169 profile review and physical test for NXP SKU/GPIO timing. No phone USB/DP hardware validation or native boot claim.

At initial publication check the latest source-sensitive CI run to distinguish host function tests, binding and full ARM64 Image/modules results; do not inherit the earlier `2875777...` success for new source.
