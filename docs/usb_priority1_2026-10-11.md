# USB priority-1 source audit and Boot handoff (Motorola oneli)

Date: 2026-10-11. Owner: USB / Type-C. **No target handset was available.**
This supplements [the USB investigation](usb_oneli_investigation_2026-10-11.md) and [original handoff](handoffs/usb_2026-10-11.md). It follows coordinator main `AGENTS.md` and `docs/NEXT_TASKS.md` reviewed 2026-10-11.

## Exact revisions and executed schema check

- Kernel baseline: `Drzet/linux@a5ebb76233b79db01e82e061173cb73c6d2b5c6b`; USB binding implementation: `0119d73b40bed1041278cf9307bdec9c17880618`; GitHub Actions workflow: `6ab3f710b2c8e9a455bc356673ca67293ad4d322` on `razr/usb`.
- [GitHub Actions USB PHY schema run 38164052929](https://github.com/Drzet/linux/actions/runs/38164052929): **passed** 2026-10-11, job `114542804907`, testing PR **test-merge SHA** `32156ad974d0d22282d1beabb9aee8385ca11bfc` (not the USB branch commit). It ran `PATH="$PWD/.venv/bin:$PATH" make DT_SCHEMA_FILES=Documentation/devicetree/bindings/phy/qcom,snps-eusb2-phy.yaml dt_binding_check` with `set -euo pipefail`. Log includes `SCHEMA`, `LINT`, `STYLE`, `DTEX` and `DTC [C]` without diagnostic failure. Artifact: [logs and tool versions](https://github.com/Drzet/linux/actions/runs/38164052929/artifacts/11710884372). Runner: Ubuntu 24.04; host `dtc` 1.7.0; `dtschema` 2026.9; `pylibfdt` 1.7.2.post2. This validates **the PHY binding only**. It does **not** validate oneli PHY node usage or the Boot DTB, or prove driver initialization.
- Motorola device tree: `MotorolaMobilityLLC/kernel-devicetree@90fa7be1db5bd47202673d4431408659149a7359`; kernel driver: `MotorolaMobilityLLC/kernel-msm@9511d6b2dc469e5bd836992e3bdd6d19ace112e0`. Boot board-support prerequisite reviewed: `cb9105ebeb9485e31d044d4fa69396b415523669` (Boot branch continued afterward; integration head not selected).

## NXP I2C repeater: pin/register/driver comparison

Motorola [cape-moto-common-overlay-base.dtsi](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-common-overlay-base.dtsi) declares **active** `nxp,eusb2-repeater` at `0x4f` on SE5, versus disabled Diodes `0x6c`. GPIO controller **PM8350C GPIO7**, vendor `reset-gpio = <&pm8350c_gpios 7 GPIO_ACTIVE_HIGH>`, supply `S10B` (1.8 V) and `L2B` (3.075–3.3 V). [cape-pmic-overlay.dtsi](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-pmic-overlay.dtsi) configures that GPIO7 as normal function with input and output enabled, power source 1.8 V, but **does not encode physical reset polarity** beyond the driver phandle. Note the vendor driver's `reset(bool bring_out_of_reset)` sets its logical GPIO to the argument but prints confusing “assert” text for the true case; this must not be translated into a guessed mainline polarity.

[Motorola driver](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/9511d6b2dc469e5bd836992e3bdd6d19ace112e0/drivers/usb/repeater/repeater-i2c-eusb2.c) defines NXP registers: `0x01 RESET_CONTROL`, `0x02 LINK_CONTROL1`, `0x03 LINK_CONTROL2`, `0x04 eUSB2_RX_CONTROL`, `0x05 eUSB2_TX_CONTROL`, `0x06 USB2_RX_CONTROL`, `0x07 USB2_TX_CONTROL1`, `0x08 USB2_TX_CONTROL2`, `0x09 USB2_HS_TERMINATION`, `0x0d RAP_SIGNATURE`, `0x0e VDX_CONTROL`, `0x0f DEVICE_STATUS`, `0x10 LINK_STATUS`, **`0x13 REVISION_ID`**, **`0x14..0x16 CHIP_ID_0..2`**. Motorola only reads `0x13` at init and does **not** check chip IDs.

The oneli override sequence stores **value before register**:

| Register / function | Motorola programmed value | PTN3222 CUK 2023 datasheet POR default | PTN3222HUK 2026 datasheet POR default |
| --- | --- | --- | --- |
| `0x06`, USB2 RX control | `0x40` | `0x50` | `0x40` |
| `0x07`, USB2 TX control 1 | `0x22` | `0x00` | `0x22` |
| `0x08`, USB2 TX control 2 | `0x64` | `0x62` | `0x63` |
| `0x13`, revision ID (read-only) | read without equality check | `0xa2` | `0xa4` |
| `0x14:0x15:0x16`, chip ID (read-only) | **not read in Motorola init** | `22:32:02` | `22:32:01` |

Sources: NXP [PTN3222 CUK, Rev 1.2, 2023, PDF p.12, Table 9](https://www.nxp.com/docs/en/data-sheet/PTN3222_CUK.pdf); NXP [PTN3222HUK, Rev 2.0, May 2026, PDF p.17, Table 8](https://www.nxp.com/docs/en/data-sheet/PTN3222HUK.pdf). This register layout is stronger **family evidence**, but **not an oneli part identification**: the 2026 HUK datasheet is not evidence of what was assembled in 2022. **[INFERRED]** a PTN3222-family chip is plausible; retain SKU unknown until revision/chip ID or BOM establishes it.

| Dimension | Motorola downstream eUSB2 repeater | Linux baseline `drivers/phy/phy-nxp-ptn3222.c` |
| --- | --- | --- |
| Compatible and provider | Generic vendor `nxp,eusb2-repeater` / old USB repeater framework | **Only** exact `nxp,ptn3222`; generic PHY with `#phy-cells = <0>` |
| 1.8V supply | `vdd18`, vendor `S10B`, 1.8 V, 32 mA load; enabled **first** | `vdd1v8`, bulk load 55 mA; in bulk list **second** |
| ~3.3V supply | `vdd3`, vendor `L2B`, 3.075–3.3 V, 3.5 mA; enabled second | `vdd3v3`, bulk load 11 mA; in bulk list **first** |
| Reset | Vendor singular `reset-gpio`, reset callback and power control; physical polarity unresolved | `reset-gpios` optional descriptor; `GPIOD_OUT_HIGH` at probe, deassert during generic PHY init |
| Registers | Reads revision; applies **three oneli-specific I2C writes**; the init helper ignores write failures | **Does not access I2C registers**, read revision/chip ID or apply tunings |
| eUSB2 integration | Vendor `usb-repeater`/ `dummy-supply` | `phys = <&repeater>` on mainline `qcom,sm8475-snps-eusb2-phy`, `qcom,sm8550-snps-eusb2-phy` |
| Confidence | Direct source evidence of Linux configuration, not measured physical operation | Repeater driver only usable when device identity is established and differences evaluated |

No new chip-compatible or register-tuning driver patch is justified yet: binding an unknown silicon revision to `nxp,ptn3222`, or ignoring the three vendor writes, would claim compatibility not established. Once hardware/stock firmware provides identifying evidence, choose explicit silicon binding and implement only chip-specific tuning backed by datasheet and testing. **Future read-only identity inspection:** with the selected oneli controller, power and reset correctly managed, read I2C `0x4f` registers `0x13`, `0x14`, `0x15`, `0x16`; report bytes, firmware version, board revision. This is **not performed**.

## PS5169 adaptation disposition

Pinned external, **unmerged** series: Esteban Urrutia, [`[PATCH v3 0/2]` posted 10–11 August 2026](https://patchew.org/linux/20260810-ps5169-bup-v3-0-a2178b2834d7@proton.me/), base `3d08ff75a47a3e7e2ab45a3bcab6723b4d906422`, change-id `20260726-ps5169-bup-8076851dc255`; adds `parade,ps5169.yaml` plus `drivers/usb/typec/mux/ps5169.c` (592 lines). Maintainer [Heikki Krogerus, 14 August 2026](https://lists.openwall.net/linux-kernel/2026/08/14/861) explicitly flagged **compile failure due to missing direct includes**. Do **not** import v3 unchanged or claim a driver build. Review a subsequently corrected version, if one exists, before attributing/rebasing; no PS5169 kernel patch is committed here.

Oneli-specific evidence: Motorola [cape-oneli-common-overlay.dtsi](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-oneli-common-overlay.dtsi) defines **TLMM GPIO19** `redriver_enable` as `output-high` and `redriver_disable` as `output-low`. Vendor [PS5169 driver](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/9511d6b2dc469e5bd836992e3bdd6d19ace112e0/drivers/usb/misc/ssusb-redriver-ps5169.c) selects these states and waits **10 ms** after enabling. This supplies a real GPIO19 *enable signal*, **not independent proof of the v3 binding's required `reset-gpios` physical active polarity or reset pulse contract**. The upstream v3 driver pulses logical reset for 1 ms and waits 10 ms after deassertion; test whether GPIO19 may safely serve it. **[INFERRED]** GPIO19 may be wired to a chip enable/reset input, but no part-pin connection or reset datasheet has been established. Keep PS5169 disabled pending resolution; do not fabricate a separate reset GPIO.

[Motorola PS5169 DT](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-common-redriver.dtsi): `0x30`, SE18; VCC `S10B`, VIO `L8C` (boot-on in oneli); physical **GPIO91** orientation input (low = CC1, high = CC2 in vendor driver); `config-seq` contains per-board equalization values. V3 binding needs `parade,ps5169`, graph ports 0/1, `orientation-switch`, `retimer-switch`, regulator and reset, but proposed driver only requests **VCC**, not VIO. Therefore **VIO power ownership and register default differences need explicit review** before use. PS5169 is *not* an AUX/SBU switch; unlike PS5170, it has no integrated AUX switch. Do not route DisplayPort AUX GPIO2/71 through PS5169.

Recommended sole owner of physical GPIO91: **PMIC GLINK `orientation-gpios`** (subject to compatible actual firmware events), one input per connector; share orientation via Type-C switch/retimer framework to QMP and PS5169. The [PMIC GLINK binding](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/Documentation/devicetree/bindings/soc/qcom/qcom,pmic-glink.yaml) defines active indication as CC2. Do **not** request GPIO91 again from PS5169. GLINK charge/PD protocol coordination: Power. Independent SBU/AUX GPIO2/71 ownership: DisplayPort.

## Boot-owned translation/dependency matrix

Checked `arch/arm64/boot/dts/qcom/sm8450.dtsi` at baseline and the Boot branch. **Important naming fix:** Motorola `qupv3_se5_i2c` / `qupv3_se18_i2c` are **not** mainline labels. Mainline already has both controllers and complete clocks, DMA, interconnect and pinctrl assignments; no new I2C controller nodes needed.

| USB dependency | Motorola source | Mainline label, resources and Boot action | Gate |
| --- | --- | --- | --- |
| NXP repeater I2C | SE5, address `0x4f` | `&i2c5` at `i2c@994000`, GIC_SPI 606, existing `qup_i2c5_data_clk` pinctrl; **enable parent `&qupv3_id_0`**, plus `&i2c5`; device compatible requires confirmed SKU | Early USB2, identity and power |
| NXP reset | `pm8350c_gpios` 7, vendor ACTIVE_HIGH | `&pm8350c_gpios` exists; mainline `reset-gpios` needs physical polarity verification | Early USB2 |
| NXP rails | `S10B` 1.8V, `L2B` ~3.075–3.3V | Power must provide proper mainline regulators, parents, limits; PTN3222-specific `vdd1v8-supply`, `vdd3v3-supply` **only after identification** | Early USB2 |
| SNPS eUSB2 PHY | `eusb2_phy0` `0x088e3000`, `L5B` 0.88V, `L10C` 1.2V | Boot **replace** inherited `&usb_1_hsphy` legacy SM8450 HS PHY resource layout; compatible `qcom,sm8475-snps-eusb2-phy`, `qcom,sm8550-snps-eusb2-phy`, correct ref clock/reset, supplies; `phys = <&verified_repeater>` | Early USB2 |
| DWC3 | vendor `&usb0`, nested DWC3 | `&usb_1` at `0x0a600000`, existing role endpoint `&usb_1_dwc3_hs`; **no nested child**; enable when HS PHY and role defined | Gadget/debug |
| Type-C PD/data-role | vendor UCSI connector | Boot PMIC GLINK provider and `connector@0` / `port@0` to `usb_1_dwc3_hs`, parent/subsystem dependencies; `orientation-gpios=<&tlmm 91 ...>` requires verified logical polarity | Gadget/dual-role |
| PS5169 I2C | SE18, address `0x30` | `&i2c18` at `i2c@88c000`, GIC_SPI 585, `qup_i2c18_data_clk`; **enable parent `&qupv3_id_2`**, plus `&i2c18` | SuperSpeed + DP, later |
| PS5169 rails/control | `S10B`, `L8C`, GPIO19 high-enable; GPIO91 orientation | Power translates supplies; Boot configures TLMM GPIO19 using validated reset/enable semantics; GLINK single owner of GPIO91; Type-C redriver graph | After v3+ driver reviewed |
| QMP combo PHY | vendor `usb_qmp_dp_phy`, `0x088e8000`, `L1B` and `L10C` | `&usb_1_qmpphy`, Boot already overrides compatible `qcom,sm8475-qmp-usb3-dp-phy`; enable only after supplies and SS retimer, preserve `&usb_1_qmpphy_out`, `&usb_1_qmpphy_usb_ss_in`, `&usb_1_qmpphy_dp_in` graphs | SuperSpeed/DP |
| DP AUX/SBU mux | separate vendor DP GPIO2 and GPIO71 | DisplayPort owns GPIO controls, electrical polarity and switch identity; no PS5169 AUX `port@2` | DP only |

The two QUP wrappers and child I2C nodes are all **`status = "disabled"`** in inherited SM8450 SoC DTS. An enabled child does not probe through a disabled ancestor; Boot may have already enabled `&qupv3_id_0` for UART7, but **must check both parents on its final branch**. Clock/DMA/pinctrl definitions come from mainline, not invented addresses. Power-owned actual RPMh regulator labels are **not yet selected**. Adding I2C device nodes with an unsupported compatible or made-up supplies is not an accepted hardware patch.

### Exact minimal shared-DT edit request to Boot

1. Select board/firmware-dependent, source-supported RPMh rails with Power. Fix eUSB2 PHY resource layout at `0x088e3000` in shared `sm8475.dtsi` (replace SM8450 QUSB2 node; do not merely append compatible). Target `#phy-cells = <0>`, proper 19.2 MHz or 38.4 MHz reference as verified, reset, vdd/vdda12; match validated binding and mainline driver.
2. In `sm8475-motorola-oneli.dts`, ensure `&qupv3_id_0` and `&i2c5` enabled, plus `&pm8350c_gpios` reset, verified NXP-compatible regulator-backed provider; **do not choose `nxp,ptn3222` without the ID**. Provide a disabled candidate node only when explicit unconfirmed placeholders are kept out of binding-checked DT.
3. Enable `&usb_1` with `usb-role-switch`, `dr_mode = "otg"` and a real `usb2-phy`; mainline already defines `&usb_1_dwc3_hs`. [INFERRED] For a separate, deliberately temporary HS-only debug build, use `maximum-speed = "high-speed"` and `qcom,select-utmi-as-pipe-clk` per upstream DWC3 binding to avoid QMP before PS5169 readiness. Verify resulting `phys`/`phy-names` and clock behaviour with build checks. Do not permanently constrain SuperSpeed.
4. Add correct PMIC GLINK `connector@0` port@0 role graph and unambiguous GPIO91 policy after coordinating firmware behaviour with Power. The current minimal Boot board DTS has **no USB node usage** to validate, so a passing PHY binding sample is not a board schema result.
5. Later, after PS5169 driver, reset and rails are identified, enable `&qupv3_id_2` and `&i2c18`, attach Type-C retimer graph, then QMP USB3/DP. Independent AUX/SBU remains with DisplayPort.

Build acceptance when Boot contributes the proposed DT: `make ARCH=arm64 ... qcom/sm8475-motorola-oneli.dtb`, `make ARCH=arm64 ... dtbs_check` with recorded toolchain, exact SHAs and warnings; verify `dtc -I dtb -O dts` has parent `status = "okay"`, compatible/supply phandles, reciprocal role/retimer graph and no duplicate GPIO91 consumer. USB subsystem's current check covers only standalone **binding schema**, not this integration.

## Workstream ownership and unresolved blockers

- **USB owns**: standalone PHY binding `0119d73`, schema CI workflow `6ab3f710`, candidate repeater/PS5169 driver and binding changes only after identified evidence, Type-C role/redriver graph proposal.
- **Boot owns**: all shared `sm8475.dtsi`, `sm8475-motorola-oneli.dts`, chosen PMIC GLINK nodes and DTB/schema checks. Do not cherry-pick an unreviewed PTN3222 compatible.
- **Power owns**: primary RPMh rail/provider topology and GLINK charging protocol compatibility; USB needs six vendor rail identities translated to actual upstream nodes.
- **DisplayPort owns**: AUX/SBU GPIO2/GPIO71 switch identity and routing; depends on USB GPIO91/orientation/PS5169 graph.

**Evidence stages:** researched **yes**; binding patched **yes**; schema-tested binding **pass** at exact test-merge SHA above; driver build **not done**; Boot board USB usage schema **not done**; hardware tests **deferred**. Next physical acceptance is *reliably enumerated USB2 gadget for serial/network debug*, then host mode and both plug orientations, only then SS/DP. No device runtime or electrical test is claimed.
