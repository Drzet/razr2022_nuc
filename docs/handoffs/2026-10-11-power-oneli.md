# Subsystem handoff: Power / charging / thermal, Motorola oneli

- Date and originating chat: 2026-10-11, dedicated Power chat of the Linux on Motorola razr 2022 project.
- Repository / branch / exact commit: `Drzet/linux`, `razr/power`, created from **`cb9105ebeb9485e31d044d4fa69396b415523669`** (exact current head at branch creation). **No power-specific kernel commit or driver modification made.** Shared `master` remains unchanged.
- Upstream baseline SHA: **`a5ebb76233b79db01e82e061173cb73c6d2b5c6b`**.
- Required board-support and other subsystem SHAs: Boot **`cb9105ebeb9485e31d044d4fa69396b415523669`**; USB-dependent Type-C/PHY integration has no pinned accepted SHA yet. Shared board/SoC DT changes are **proposals for Boot**, not edits on this branch.
- Evidence stage: **researched: yes; implemented (power-specific): no; build-tested: no; hardware-tested: no**.

## Changes and provenance

Reviewed project rules and status, hardware JSON/CSV database, baseline comparison and Boot handoff, then the pinned source files below. Conclusions are about source-level support only; the actual retail handset firmware, populated board revision, battery state and live DT remain unknown.

Pinned evidence:
- Motorola board DT `90fa7be1db5bd47202673d4431408659149a7359`: [oneli overlay](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-oneli-common-overlay.dtsi), [Cape regulator definitions](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-regulators.dtsi), [common UFS/repeater supplies](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-common-overlay-base.dtsi), [Cape GLINK topology](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape.dtsi), [charger policy](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/waipio-moto-common-charger.dtsi), [charging override](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/waipio-li-charger-overlay.dtsi), [PMIC ADC](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-pmic-overlay.dtsi), [oneli thermal overlay](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-oneli-thermal-overlay.dtsi).
- Motorola downstream kernel reference `9511d6b2dc469e5bd836992e3bdd6d19ace112e0`: [PMIC GLINK](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/9511d6b2dc469e5bd836992e3bdd6d19ace112e0/drivers/soc/qcom/pmic_glink.c); no wholesale downstream driver import.
- Exact mainline baseline: [RPMh regulator driver](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/regulator/qcom-rpmh-regulator.c), [PMIC GLINK core](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/soc/qcom/pmic_glink.c), [GLINK power supply](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/power/supply/qcom_battmgr.c), [BQ gauge I2C](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/power/supply/bq27xxx_battery_i2c.c), [SGM41542 driver](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/power/supply/sgm41542_charger.c), [PMIC GLINK schema](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/Documentation/devicetree/bindings/soc/qcom/qcom,pmic-glink.yaml), [RPMh regulator schema](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml).

### Minimal boot versus sustained operation

**Early diagnostic boot:** Bootloader/firmware-established CPU/DDR/PMIC states and PSCI supply the initial platform. Mainline already contains RPMh RSC, RPMh power-domain, SPMI, PMIC GPIO, PMIC temperature and TSENS infrastructure. For *minimal UART plus initramfs boot*, do not make PMIC GLINK, fuel-gauge probing, charger register writes or flip-battery enablement hard dependencies. **[INFERRED]** An initially charged handset may reach a short-lived diagnostic shell relying on preconfigured PMIC/firmware state. This has not been demonstrated. Keep high-load peripherals disabled until their regulators are described and validated; do not assume an unmodeled rail remains powered after regulator cleanup.

**Read-only UFS and USB debugging:** These are distinct from early UART boot. Map the UFS and eUSB/USB supplies explicitly before enabling the consumers. PMIC GLINK/UCSI and USB port power negotiation are USB/Power shared dependencies for a powered debug dock.

**Sustained NUC operation:** require proven primary-battery state reporting and charging under mainline, safe secondary/flip-battery management or a demonstrated safely idle secondary charging path, predictable charger input and PD behavior, reliable live thermal sensing with real CPU/GPU cooling control, shutdown/reboot, and a stable source-to-battery power budget. **[INFERRED]** Charger firmware may autonomously enforce electrical limits, but Motorola user-space/kernel charge policy and flip-battery pairing do not transfer automatically. Do not promise batteryless or unattended powered operation until measured.

### Firmwares versus Linux responsibilities

| Facility | Established source behavior | Linux responsibilities / unknowns |
| --- | --- | --- |
| RPMh/PMIC | RPMh resources control PMIC VRM rails; boot firmware creates initial working state | Correct PMIC IDs, constraints, upstream RPMh provider/consumer descriptions, enable sequencing and votes. Firmware-set defaults do not replace Linux regulator dependencies. |
| Primary charging | Motorola exposes a charger service over ADSP PMIC GLINK, service path `msm/adsp/charger_pd` | GLINK transport/PDR, battery/USB `power_supply` telemetry, notification and limit-setting. Firmware compatibility and presence not hardware-tested. |
| Battery protocol | Baseline `qcom_battmgr` supports SM8350-style default and has threshold interfaces | Verify actual Motorola opcode/property semantics; do not assume Motorola `mmi` child node or combined-charge policy is implemented. |
| Type-C / PD | GLINK UCSI routing exists in Moto DT | USB branch owns orientation/connector graph/role-switch; Power validates charger/PD telemetry and supply budget. |
| Flip battery | BQ27426 `0x55`, SGM41516D `0x6b`, PMIC GPIO control | Gauge/profile/current polarity, charger-specific register driver and pair/load policy not established under Linux. Cellwise CW2217 `0x64` explicitly disabled in inspected oneli overlay. |
| Thermal | SoC TSENS, PMIC die alarms, PMK8350 ADC thermal monitor and vendor zones | Enable/translate valid sensors, select accurate channel semantics, build CPU/GPU cooling maps and test shutdown behavior; vendor userspace cooling maps cannot be copied verbatim. |

### Driver and policy gaps

1. **Not a regulator-driver gap:** baseline `qcom-rpmh-regulator.c` supports exact PM8350, PM8350B, PM8350C, PM8450 and PMR735A type compatibles. The missing work is oneli-specific regulator topology and correct dependencies; PMIC identity and live rail states remain unverified.
2. **GLINK service protocol is a verification gap:** baseline `pmic_glink.c` accepts `qcom,pmic-glink`, implements ADSP charger PDR, battery and UCSI auxiliary clients; `qcom_battmgr.c` implements battery/USB/charge-control properties with a default SM8350 protocol. Motorola supplies extra `mmi,qti-glink-charger`, `mmi,mmi-charger` and dual-battery properties which are not upstream `qcom_battmgr` policy. Neither successful probing nor Motorola-specific opcodes are established.
3. **Flip gauge driver exists:** baseline `bq27xxx_battery_i2c.c` matches `ti,bq27426`. The vendor `design-capacity=<712>` is profile data, not live capacity. Vendor current-inversion and named profile configuration require examination before representing accurate current/SoC.
4. **Flip charger driver gap is specific:** baseline has an `sgm41542_charger.c` driver bound to `sgmicro,sgm41542` with a device-ID test and active hardware initialization. Motorola describes **`sgm,sgm41516D`**, not 41542. No equivalence of chip ID, registers or parameter limits has been established; **do not add a compatible alias or bind the 41542 driver** without exact evidence. The driver writes charger settings on probe. Need downstream SGM41516D source and live chip ID/register checks, then an attributable driver/binding patch or separate driver as justified.
5. **Thermal integration gap:** baseline already has TSENS and PMK8350 ADC/ADC-TM framework; `pmk8350_adc_tm` in upstream PMK8350 DTS is disabled. Motorola's oneli active PMIC ADC thermal zones include MSM THM1, charger THM2/THM3, Wi-Fi THM4, camera THM5, quiet channel PM8350B GPIO2 and XO. Some alternative zones are disabled. Repeated vendor trip values `125000` m°C are not valid proof of a safe throttling policy; do not transplant unexamined cooling maps or modem/QMI controls.

### Proposed shared DT changes (Boot owner to incorporate after review)

All below are **proposals only**, not patches or validated fragments. Apply through separate Boot commits to `arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dts` and, only if justified, `sm8475.dtsi`. Preserve the existing Boot tree and exact USB controller labels; do not copy vendor old-node hierarchy.

**P0, initial regulator topology** under existing `&apps_rsc`: mainline `qcom,pm8350-rpmh-regulators` with PMIC resource ID `b`, `qcom,pm8350c-rpmh-regulators` with resource ID `c`, and only required physical `smps*/ldo*` children and parent supplies. Confirm PMIC IDs and upstream grouped input supply mapping from live oneli and mainline binding before final inclusion. Candidate labels map as follows:

| Motorola rail / candidate regulator child | Vendor initial voltage | Proven downstream consumer | Integration priority |
| --- | ---: | --- | --- |
| PM8350 `ldo5` / L5B | 880000 µV | UFS PHY `vdda-phy` | P0 UFS |
| PM8350C `ldo10` / L10C | 1200000 µV | UFS PHY `vdda-pll` | P0 UFS |
| PM8350 `ldo7` / L7B | 2504000 µV | UFS `vcc` | P0 UFS |
| PM8350 `ldo9` / L9B | 1200000 µV | UFS `vccq`, vendor ref-clock rail | P0 UFS |
| PM8350 `smps10` / S10B | 1800000 µV | BQ27426 and SGM I²C supply, eUSB repeater | P1 battery/USB |
| PM8350 `ldo2` / L2B | 3072000 µV | NXP eUSB2 repeater | P1 USB |
| PM8350C `ldo8` / L8C | 1800000 µV | PS5169 redriver; vendor boot-on | P1 USB |
| PM8350C `ldo11` / L11C | 3000000 µV | Oneli display peripheral | P2 display |

These are **pinned Motorola source default values, not independent measurements on the user's phone**. Choose actual min/max constraints from supported upstream operating requirements and live evidence. Never add all rails as permanently `regulator-always-on` or assume safe use of a fixed 3.7V `vph_pwr` model from another board.

**P0, UFS coordination:** request `&ufs_mem_phy` analog supply phandles for L5B/L10C and `&ufs_mem_hc` host `vcc`/ `vccq` rails L7B/L9B, translated to the baseline's exact node labels and bindings. Do **not** copy Motorola's `vdd-hba-supply=<&gcc_ufs_phy_gdsc>` as though a power-domain controller were an ordinary regulator. The Boot branch already preserves UFS_PHY_GDSC.

**P1, GLINK/charging after diagnostic boot:** propose a root `pmic-glink` node using **[INFERRED]** `"qcom,sm8450-pmic-glink", "qcom,pmic-glink"` per the currently supported binding and SM8450 reference, pending service compatibility evidence. Do not copy downstream `qcom,pmic-glink-channel`, `qcom,subsys-name`, `mmi,qti-glink-charger` or `qcom,battery-charger` child properties directly. USB owner supplies Type-C `connector@0`, controller/PHY graphs and orientation. Parent GLINK/protection-domain access and signed ADSP charger firmware must be checked. Enabling and reporting power supplies precedes any charging-policy writes.

**P2, flip battery:** `&qupv3_se2_i2c` must be translated to a known mainline QUP serial engine label and correct enabled bus. Then propose a `ti,bq27426` gauge at `reg=<0x55>` with proper supply/IRQ translation, **only after** checking profile handling and any inversion issues. Keep charger `sgm,sgm41516D` at `0x6b` **out of active mainline DT** until driver/binding/chip ID and charging policy validated; keep Cellwise disabled. PM8350C GPIO2 (active-low charge enable), PM8350B GPIO1/GPIO3 (paired load), TLMM43 (gauge IRQ) and TLMM51 (charger IRQ) are evidenced downstream but should only be requested by an accepted charger/pairing implementation.

**P1, thermal staged:** keep existing TSENS/PMIC die alarm zones; first capture baseline sensor inventory, then enable/describe `&pmk8350_adc_tm` channel children against upstream ADC7/ADC-TM binding for oneli's sourced channels. Map to upstream thermal zones and verified cooling devices, respecting deliberately disabled vendor sensors. Avoid reusing vendor placeholder `125000` m°C values as operating safety targets; set realistic limits only after measured sensor semantics, CPU cooling support and validation.

## Shared files and integration

- **Kernel shared files proposed, not touched:** `arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dts`, possibly `sm8475.dtsi` for SoC-level prerequisites.
- Other owners: USB (PMIC GLINK connector graph, orientation, eUSB2 repeater/PS5169), Boot (UFS enablement and DTS/regulator composition), GPU (OPP and cooling integration).
- No firmware files committed. No driver/binding patches accepted in this handoff. `razr/power` currently contains inherited Boot commits only. Integration order: Boot exact head → vetted regulator DT proposal via Boot → read-only storage/diagnostics → GLINK telemetry with USB coordination → independently reviewed gauge/charger/thermal integration. No cherry-picks, merges, or integration SHAs exist yet.

## Validation

**Source checks performed:** read `razr/boot` head `cb9105ebeb9485e31d044d4fa69396b415523669` and upstream `master` `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` from GitHub; read current board DTS (only PMIC includes, UART and carveouts), inspected pinned vendor oneli power/thermal and Cape regulators/GLINK, and compared exact mainline RPMh PMIC regulator matches, GLINK battery path, BQ27426 and SGM41542 IDs. Branch creation for `razr/power` succeeded from Boot head. These are file/API reads, **not kernel build or DT schema checks**.

**Not performed:** building source, `dtbs_check`, testing regulator phandles, probing live ADSP GLINK, I²C chip-ID, SoC/PMIC thermistor validation, charging current/voltage or thermal trips, 24/7 operation, flashing/booting oneli. A baseline CI workflow exists but is not evidence of any Power branch validation. Hardware revision, Android build fingerprint, selected live DTB/DTBO and firmware inventory are unrecorded.

## Blockers and next test

1. **Phone read-only evidence:** export Android build/board revision, running DT, loaded battery/charger driver identity and messages, available `power_supply` objects, GLINK charger service and PMIC/thermal readouts. Acceptance: identify actual regulator/PMIC population, SGM chip ID and battery profiles without modifying registers or flashing.
2. **Boot-owned regulator DT review:** map required UFS/eUSB supplies and parent PMIC input rails to upstream names, with reproducible schema and DTB build. Acceptance: no unresolved phandles or binding errors, stable regulator probe on actual handset and UFS initially read-only.
3. **Firmware protocol smoke test:** enable generic supported PMIC GLINK/charger service, preserve original charger behavior, read basic battery/USB telemetry, compare Android values and units. Acceptance: no PDR failures, unexpected charge-control writes or service resets. Coordinate Type-C/role graph with USB owner.
4. **Secondary charging:** derive exact SGM41516D compatibility from the relevant Motorola charger driver and read-only identification, then implement only an evidence-backed driver/binding and explicit dual-battery policy. Acceptance: measured and bounded current/voltage, gauge sign/SoC correct and charge transitions sane.
5. **Sustained thermal/power test:** validate TSENS/ADC channels and CPU cooling first; then instrument idle/medium/high load with USB input and both batteries, require throttling and shutdown behavior to work. Acceptance: stable PD/input power, no unnoticed discharge under specified continuous load, no unmonitored hotspot and a recorded thermal mitigation event.

**Decision:** no active charge-controller or thermal policy modifications until firmware/device-specific data are obtained; none of the proposed DTS changes is safe to merge solely from these reference files.
