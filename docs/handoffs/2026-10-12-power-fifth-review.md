# Subsystem handoff: Power fifth review, VPU omission closure and read-only contract

## CURRENT handoff: 2026-10-16 USB/DP shared L2B supply (new coordinator task)

**This section is authoritative for Power's current assignment; the fifth-review sections below remain historical evidence.** Coordinator source [`432f2f84f6350f0c1b7670b751bf41fd349048ce`](https://github.com/Drzet/razr2022_nuc/commit/432f2f84f6350f0c1b7670b751bf41fd349048ce), branch **`Drzet/razr2022_nuc:razr/power`**. Previous HEAD `1013ef56961716e6afb93321036c300a9f62cbf9`; regulator report updated at **`d7cb74e317b6e74e6451cc9b2706682209f75889`**; this handoff will commit on top. **Kernel code unchanged**. Exact accepted integration `Drzet/linux@2b5acf108ae37040ac1e652e029bb37f5609e886`. Input owners: Boot board proposal `Drzet/razr2022_nuc@812172869a8c9665c6a39004aad9b1c52cf036bf`, DP source `186a7f251397c87f8a68a37afa8cf0556e579c01`, accepted PTN binding `Drzet/linux@1e5268277f6d4c25cde2f3e2b3f00439107e087a`, PS5169 `4dcbc7ba1c04afea37ab0b0caf6b4c16bfcc3dfe`. Existing source-only driver restrictions retained.

**One canonical Power supply report:** [`docs/power_oneli_pvt_usb_supply_audit_2026-10-12.md`](../power_oneli_pvt_usb_supply_audit_2026-10-12.md), now headed by complete 2026-10-16 electrical/voltage/lifetime decision. Earlier Power rail v2, fourth and fifth reports remain citations but their HDK-[INFERRED] parent unknowns are **superseded** by reported oneli rev03 reference schematic. No new stand-alone competing rail report.

### Definitive source-level results (physical reference schematic, handset not verified)

| Source device/rail | Parent at electrical input, ref board | Upstream binding/input property | Consumer / voltage, original source |
| --- | --- | --- | --- |
| PM8350 S10B | variable `B_PLUS` | PM8350 `vdd-s10-supply` | PTN3222 `vdd1v8`, PS5169 `vcc`; 1.800V |
| PM8350C BOB | variable `B_PLUS` | PM8350C `vdd-bob-supply` | PM8350 L2/L7 input; 3.008–3.960V, initial source 3.296V |
| PM8350 L2B | **PM8350C BOB** | PM8350 `vdd-l2-l7-supply` | **shared** PTN3222 `vdd3v3` and WILLSEMI WAS7227Q `vcc`; 2.7–3.3V, initial source 3.072V, schematic `VREG_L2B_3P07` |
| PM8350C S1C | variable `B_PLUS` | PM8350C `vdd-s1-supply` | PM8350C L2/L8 input; Motorola source initial 1.880V, schematic named 1P86 nominal |
| PM8350C L8C | **PM8350C S1C**, not BOB | PM8350C `vdd-l2-l8-supply` | PS5169 `vio`; 1.8–2.0V, initial 1.8V, reference PVT boot-on |
| PM8350BH / PM8450 | distinct devices, no evidence as shared L2B parents | no shared-chain edge | **exclude** from this USB/DP regulator graph |

The two evidenced internal parent phandles can be proposed to Boot: `vdd-l2-l7-supply=<&oneli_bobc>`, `vdd-l2-l8-supply=<&oneli_s1c>` on the **PM8350** and **PM8350C RPMh provider nodes**, respectively. These phandle **labels are illustrative**, not an authorized shared-DTS edit. Keep providers and consumers disabled. **B_PLUS is variable:** no invented fixed 3.7V voltage-source regulator or fake B_PLUS phandle. It is supported to state physical upstream parent wiring but **not** safe initial BOB/S1C programmability on installed PVT.

### Voltage collision and precise missing qualification

- Current PTN3222 driver `vdd3v3` consumer vote **3.075–3.300V**; stock base L2B `qcom,init-voltage=3.072V`, board label 3.07V. Mainline PM8350 L2B hardware is `pmic5_pldo` with selector voltage **1.504V + n×0.008V**. Exactly **3.072V=selector196**; current 3.075V minimum therefore chooses first valid **3.080V=selector197**. **An 8mV real target shift from the vendor's initial vote**, not a direct rounding to 3.075V. Native phone rail measurement absent.
- Published NXP **CUK** Rev1.2 recommends VDD3V3 2.85–3.63V; official source [NXP PDF](https://www.nxp.com/docs/en/data-sheet/PTN3222_CUK.pdf), section 11 table31. WILLSEMI original WAS7227Q allows 2.5–5.5V [rev1.4 PDF](https://www.omnivision-group.com/files/product/files/WAS7227Q_V1.4.pdf). **No published authoritative BUK-specific VDD3V3 supply range or explanation for Motorola's 3.075V minimum was established**; do not claim 3.080V proved safe for oneli BUK, or silently change PTN driver minimum to 3.072V. Leave both devices and rail disabled until the variant/voltage gate is satisfied.
- Even the stock BOB 3.296V and S1C 1.880V *initial votes* are not exact selectable points with present mainline PMIC5 maps: BOB 3.000V + 0.032Vn → nearest **3.288/3.320V**, S1C 0.320V + 0.016Vn → nearest **1.872/1.888V**. Their actual settings and PMIC headroom are not measured and should not be prescribed by rounding. Preserve source ranges; require supported vote/readback analysis at integration.

### Minimal accepted reuse direction for AUX lifetime

**Do not rely on PTN3222 `phy_power_on/off` votes.** Existing `gpio-sbu-mux.yaml` *permits* `vcc-supply`, but existing `gpio-sbu-mux.c` has no `regulator_get/enable`. **Direct Boot phandle alone does nothing**. DP should retain its accepted exact-part compatible `"willsemi,was7227q", "gpio-sbu-mux"` (vendor-prefix/binding delta separately queued), plus active-low OE_N GPIO2 and SEL GPIO71.

**Proposed smallest reusable generic change**, *not Power-authored code*: when a switch node declares `vcc-supply`, strictly obtain regulator through devm API, propagate `-EPROBE_DEFER` or failures rather than creating a dummy, `regulator_enable` **before Type-C switch/mux registration and any active OE_N output**, then retain that enable ref **for the entire bound lifetime**. GPIO callbacks only set OE_N/SEL; no supply toggles on DP mode or detach. Immediately register a devm disable action for late-probe unwind. Remove first physically disconnects the switch and unregisters Type-C consumers, then releases the enable ref, with no double disable. Older nodes without `vcc-supply` continue to work. No new AUX driver, no fixed regulator and no PTN-owned always-on vote.

**Suspend caveat:** mainline RPMh sends `RPMH_ACTIVE_ONLY_STATE`; no shown sleep-vote/retention support or firmware contract. Device-lifetime vote covers **DP attach/detach while active**, not proven suspend wake/DP routing through low-power collapse. Leave DP suspend/wake behaviour as specific later gate rather than invent `regulator-always-on`.

### Validation, dependencies, stop

**Source validated only:** exact schematic U1720/U4500 reference rail paths and PMIC names, pinned RPMh YAML group keys, pinned PM8350 regulator hardware tables & 8mV grid, accepted PTN request, generic gpio-sbu-mux's missing vcc handling, two manufacturers' public *non-BUK* operating conditions. **No new kernel patch, DTS, CI, full build, electrical test, native boot, USB enumeration, DP attach or suspend validation**. Oneli handset population [INFERRED] from same reference design. Authoritative reference-source revision is `maven.cpm` rev03; no schematic PDF redistributed.

**Delivery to Boot:** staged *disabled* provider/consumer phandles using the correct internal BOB/S1C supply parents; no guessing B_PLUS provider, no fixed battery voltage or unreviewed BOB/S1C programmed initial. **Delivery to DP:** binding alone inadequate; regulator lifetime adaptation with strict missing-supply failure/error-unwind is needed before node enable. **USB:** PTN 3.075V min vote conflicts with 3.072V original initial setting on an 8mV grid; precise BUK limit remains missing. **Coordinator:** source contract delivered, no implementation approval. Post current exact project commit to issue #9, crosslink #11 and #2 and stop.

- **Date / chat:** 2026-10-12, Power owner. Assignment: [coordinator fifth review](https://github.com/Drzet/razr2022_nuc/blob/main/docs/FIFTH_REVIEW.md), [current queue](https://github.com/Drzet/razr2022_nuc/blob/main/docs/NEXT_TASKS.md). This handoff **supersedes the fourth handoff as the active Power decision**, but preserves its source provenance and unchanged earlier tests.
- **Project:** `Drzet/razr2022_nuc:razr/power`, earlier fourth-round head `9a163f0cea7e93af6823b6e2581b7f1db775e782`. Fifth work comprises (1) corrective update of existing canonical [USB/supply audit](../power_oneli_pvt_usb_supply_audit_2026-10-12.md) at project commit `8f1f17a1530c5dd9570e3cb10b27902cd36d3c2b`, (2) new [GLINK and BQ27426 write-path audit](../power_oneli_read_only_driver_write_audit_2026-10-12.md) at `f327578d18c08509daed8f7e64d4f3f77da3bfbc`, and (3) this handoff. This branch alone was changed. No aggregate STATUS/NEXT_TASKS edits.
- **Kernel baseline:** `Drzet/linux@a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- **Required Boot board staging:** `Drzet/linux@525b504b82dbca593a9a697af9be63f53915e0a3`; Boot owns shared oneli DT, UFS/USB disabled peripheral decisions and later applied-FDT review. USB owns NXP/PS5169 enable/reset and lifecycle.
- **Power source:** `Drzet/linux:razr/power-temp-standalone@564f2c7df60316db86e36d7267ddadf07bc32b7e`, kernel PR #4. Existing earlier original-Power ARM64 object build and UML KUnit signed-temperature conversion **3/3 passed**; no new Power source patch.
- **Stage:** stock raw-property and source inspections **completed and recorded**; candidate integration source-blobs **compared**; combined Image/modules **not accepted from this handoff**; physical phone voltage, thermal, charging and GLINK protocol **untested**.

## 1. Consume VPU unfiltered PVT property evidence: delta closed

VPU has completed sixth-round bounded export on `Drzet/razr2022_nuc:razr/vpu@dadd330c3f09f715372da94091f04166f9f0c141`. [New focused JSON](https://github.com/Drzet/razr2022_nuc/blob/dadd330c3f09f715372da94091f04166f9f0c141/docs/vpu/evidence/focused-stock-properties.json) is 803,197 bytes, SHA-256 `f1bb6f41036aeb2e04ac289cfa803aab686cf92097a77444c9ed50c96397fe48`, [focused export 38291543595 PASS](https://github.com/Drzet/razr2022_nuc/actions/runs/38291543595). The older full six-FDT *filtered* JSON is also now durable in VPU's compressed derived evidence. No repeated ROM download/CI requested.

- Explicitly inspected `per_fdt_focus[3]` (`board-id=<0x45 0xC000>`) `/fragment@48/__overlay__`: **one and only one property, `regulator-boot-on`, zero bytes**. All four DTBO candidates have the same source fragment. `/fragment@48/target` stores external relocation sentinel `0xffffffff`. Named fixups and both vendor_boot base symbols symbolically resolve this to `L8C`. Neither source voltage nor upstream input-parent phandle is supplied by this overlay. **Old claim “fragment48 properties still filtered/unknown” is superseded.**
- Both independent MSM530 and MSM540 source regulator definitions agree: **PM8350 S10B 1,800,000..1,800,000 µV (initial 1,800,000)**; **PM8350 L2B 2,700,000..3,300,000 µV (initial 3,072,000)**; **PM8350C L8C 1,800,000..2,000,000 µV (initial 1,800,000)**. NXP eUSB2 `vdd18=S10B`, `vdd3=L2B`; PS5169 `vcc=S10B`, `vio=L8C` remains grounded by four overlay fixups. PVT fragment48 has **no voltage override** and separately requests boot-on.
- The one-Boolean source fragment does **not** establish a fully libfdt-composed running tree, physical active power or regulator *electrical input parents*. Mainline binding names `vdd-s10-supply`, `vdd-l2-l7-supply` and `vdd-l2-l8-supply` do not identify oneli's actual wiring. Donor HDK's fixed 3.7V VPH and BOB wiring remain **[INFERRED]** and **not accepted as parent mappings**; A100-only PM8010 i/j are excluded.
- **Actionable Boot contract:** optional disabled provider-child labels may use source voltages above; `regulator-boot-on` is a candidate annotation to review *separately*, **not `regulator-always-on`**. Do not turn on the currently disabled RPMh parents or either USB/DP consumer. There is no further Power-specific unfiltered PVT fragment48 field to wait for. Boot retains final effective-tree composition and activation authority.

**Canonical current supply report** is [`power_oneli_pvt_usb_supply_audit_2026-10-12.md`](../power_oneli_pvt_usb_supply_audit_2026-10-12.md), now corrected with new VPU evidence. The fourth handoff and older rail v2 retain source provenance, but should **not** be interpreted as current unresolved-fragment48 status.

## 2. Concrete read-only GLINK and BQ27426 initialization/write audit

Full [pinned-source write-path matrix](../power_oneli_read_only_driver_write_audit_2026-10-12.md) distinguishes bus protocol writes, persistent gauge configuration and charging controls:

- Mainline `qcom_battmgr` default SM8350 fallback: `qcom_battmgr_probe` initializes client and registers battery/USB/WLS supplies; service-up worker **sends PMIC GLINK `0x04` notification registration** (NOT I²C writes or charge control). Battery/USB/WLS getter paths send `GET=0x30/0x32/0x34`; signed temperature fix decodes battery property `BATT_TEMP=12`. Requests wait for ACK or return timeout and service-down reads give `-EAGAIN`.
- Common GLINK source contains a genuine write operation `BATTMGR_CHG_CTRL_LIMIT_EN=0x48` with `enable=1` in threshold setters. **Crucial branch condition:** `sm8350_bat_psy_desc` has no `set_property` or `property_is_writeable`; `sm8550_bat_psy_desc` exposes them. Therefore a verified SM8350 protocol-only report path is narrower than the globally write-capable driver. No connected oneli native firmware reply was observed.
- Mainline **already supports `ti,bq27426`** and standard gauge measurement reads, but its I²C bus has `write` and `write_bulk`. If battery-info supplies both design capacity+energy or minimum voltage, `bq27xxx_battery_settings` can **unseal, update data memory, reset and seal during probe**. Merely avoiding writable sysfs is not enough.
- The Motorola-derived `bq27426_fg_mmi` *family comparator* is more dangerous for a putative read-only boot: probe sends firmware subcommands; first heartbeat calls BQFS profile updater on mismatch and **unconditionally calls `fg_select_external_temp`**, a DM-class64 write transaction. The source also has explicit reset/chemistry/DM and debug update operations. **Do not transplant it as a read-only driver.**
- Suggested future strictly read-only BQ reporting needs an attributable `ti,bq27426` register measurement allowlist and an **enforced deny-write transport** in probe/periodic/IRQ/error/suspend paths with negative tests. Compare actual flip pack current-polarity inversion and external-temperature behavior rather than silently reusing mainline defaults. Keep gauge off until such a candidate is proved; no new code is justified in the first minimal image.
- **Active controls explicitly held:** SGM41516D charger I²C `0x6b`, Motorola paired battery/load GPIO switching and current allocation, `0x48` GLINK charge-limits, thermal mitigation and board GPIO regulators. Stock Android “combo battery” behavior is not a built-in upstream feature. Reporting `TEMP` is not active battery thermal protection.

## 3. Combined candidate source review and remaining integration test

Boot's newly delegated kernel candidate currently exists at **`Drzet/linux:razr/integration-candidate@2b5acf108ae37040ac1e652e029bb37f5609e886`**, starting from Boot `525b504b...`. Its history contains one GPU chip-ID, one GMU error cleanup and exactly five transplanted Power commits plus a workflow commit. Independently fetched **all five Power file blob SHA IDs** from this candidate and clean standalone `564f2c7d...`: **5/5 match**:
- `qcom_battmgr.c` `878eb0d58af5ae344b885a116c376656be76a1da`
- `qcom_battmgr_internal.h` `e38b368ca9cb68f0503d49021c9c8673c6ed990d`
- `qcom_battmgr_test.c` `c6afdba32b3ff0baa50717713465b4644b6f57dc`
- `drivers/power/supply/Kconfig` `1143622f7b06a113f9377ac5e8be533f32f227bd`
- `drivers/power/supply/Makefile` `3d91ebde77e6de5f66c937b5cf4dc569407e5ce1`

This is a **strong source-identity verification of the isolated signed-temp patch's replay**. The candidate's build workflow exists, but no accepted Image/modules ordinary-modpost run or exact artifact set was verified here. **No unchanged isolated rebuild** needed; Boot/Userspace follow through on the candidate kernel artifacts and QEMU module load, with coordinator acceptance/promotion.

## Files, evidence, blocker disposition and next tests

- **Changed here:** only Power project-owned corrected source report, new dedicated read-only audit and handoff. **No kernel edits, shared DTS, build configs, workflow triggers, status/next-tasks aggregate or firmware payload changes.**
- **PASS (source):** VPU's targeted unfiltered PVT one-property fragment48 inspected, both base provider values checked, existing consumer phandles preserved, GLINK/BQ probe+error+update+periodic write behavior audited, exact integrated Power five-file Git blobs compared.
- **NOT tested:** actual libfdt FDT apply/phone variant selection; physical upstream supply graph/voltage; GLINK oneli request/ACK; fuel-gauge no-write kernel test; charger, GPIOs or thermal behavior; accepted combined Image/modules and QEMU project-kernel run.
- **Stopped with specific dependency:** Power no longer waits for VPU fragment48 (closed). Optional physical upstream-parent wiring requires attributable oneli source or hardware, not repeated filtered export. The next *Power-owned implementation* is a small, enforced-no-write BQ27426 read-only candidate with tested I²C lifecycle if coordinator selects a reporting profile; until then driver/board remains disabled. Minimal ARM64 combined build may proceed independently.

**Handoff to Boot/USB:** consume canonical voltage and boot-on delta, never infer BOB/VPH electrical parents, do not enable USB/charging for integration convenience. **Handoff to coordinator:** Power's five changed kernel blobs already match integration candidate; normal modpost/artifact acceptance belongs to the delegated Boot build.
