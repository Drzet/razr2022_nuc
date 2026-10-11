# External eUSB2 NXP repeater: driver/binding RFC, identity held

2026-10-11. **USB source-level implementation disposition, not an approved oneli compatible.** Sole hardware decision still blocked on NXP SKU/revision and external reset polarity; this **does not** block the separate [Boot USB2-first disabled DTS contract](usb2_first_boot_contract_v1_2026-10-11.md).

Pinned evidence: Motorola `kernel-devicetree@90fa7be1db5bd47202673d4431408659149a7359` [NXP + overridden registers](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-common-overlay-base.dtsi), [PM8350C GPIO7 pinctrl](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-pmic-overlay.dtsi), Motorola kernel `9511d6b2dc469e5bd836992e3bdd6d19ace112e0` [`drivers/usb/repeater/repeater-i2c-eusb2.c`](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/9511d6b2dc469e5bd836992e3bdd6d19ace112e0/drivers/usb/repeater/repeater-i2c-eusb2.c). Mainline kernel `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`: [`drivers/phy/phy-nxp-ptn3222.c`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/phy/phy-nxp-ptn3222.c), [its exact-silicon binding](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/Documentation/devicetree/bindings/phy/nxp,ptn3222.yaml) and [SNPS mainline eUSB2 consumer](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/phy/phy-snps-eusb2.c).

## Motorola evidence at the register boundary

Vendor active I²C address `0x4f` on qupv3 SE5 (mainline `&i2c5`), **`nxp,eusb2-repeater`** family-level compatible, supplies **S10B = 1.8 V**, **L2B = nominal ~3.072 V from Motorola init setting** (vendor 2.7–3.3 V allowed), `reset-gpio = <&pm8350c_gpios 7 GPIO_ACTIVE_HIGH>`. An alternative Diodes `0x6c` node is explicitly **disabled**. This proves the downstream node's intended software provider/IO route, not populated NXP part revision.

Vendor **value/register** tuple sequence (decoded from `eusb2_repeater_update_seq()`; not inverted):
| Address | Register definition in Motorola source | Written value |
| --- | --- | --- |
| `0x06` | `USB2_RX_CONTROL` | `0x40` |
| `0x07` | `USB2_TX_CONTROL1` | `0x22` |
| `0x08` | `USB2_TX_CONTROL2` | `0x64` |

Vendor register definitions `REVISION_ID=0x13` and `CHIP_ID_0..2=0x14,0x15,0x16`. **Current Motorola init reads ONLY 0x13** and prints it; **no chip-ID equality check**. `eusb2_repeater_update_seq` writes all three but its return is `void`, and the internal `eusb2_i2c_write_reg` error results are ignored. A correct native driver should propagate I2C errors and avoid treating a partial tuning sequence as initialized.

`reset-gpio` vendor DT uses GPIO_ACTIVE_HIGH, but downstream `eusb2_repeater_reset(..., bool bring_out_of_reset)` directly sets its GPIO to that argument while its debug text appears to invert assert/deassert description. No reliable **physical reset active polarity, power-to-reset delay, or pulse sequence** follows from that alone. The vendor power helper enables 1.8 V **first**, then ~3V rail; the current mainline PTN3222 `regulator_bulk_data` array lists 3.3 V **first**, 1.8 V **second**, then deasserts a descriptor asserted at probe. Exact sequencing semantics need device evidence and datasheet review; do **not** silently assume both paths interchangeable.

## Candidate family comparisons and actual supported software

| Capability | Downstream generic NXP | Baseline mainline `nxp,ptn3222` |
| --- | --- | --- |
| Identity | `nxp,eusb2-repeater`, no SKU; NXP revision read `0x13` only | Matches exact `nxp,ptn3222`, no I2C chip-ID/revision read |
| Supplies | `vdd18` / `vdd3` with vendor programmed constraints/loads; 1.8 V first | `vdd1v8` / `vdd3v3` bulk; 3.3 V first, own load numbers |
| Reset | vendor callback with disputed printed polarity, PM8350C GPIO7 | `reset-gpios` active-descriptor polarity, GPIOD_OUT_HIGH at probe and deassert on generic PHY init |
| Tuning | writes registers `0x06=0x40, 0x07=0x22, 0x08=0x64` with errors ignored | **no regmap reads or tuning writes** |
| Consumer | old vendor USB repeater framework | mainline `phy-snps-eusb2` uses `phys=<&repeater>` generic PHY; optional at driver probe but physical NXP repeater required oneli |

NXP [PTN3222_CUK datasheet Rev 1.2 2023](https://www.nxp.com/docs/en/data-sheet/PTN3222_CUK.pdf) and [PTN3222HUK Rev 2.0 May 2026](https://www.nxp.com/docs/en/data-sheet/PTN3222HUK.pdf) document related register maps and chip IDs with differing defaults. **[INFERRED]** oneli uses a PTN3222-family device. Shared address/register names *do not identify the soldered SKU*. In particular a datasheet issued in 2026 is not proof of which revision populated a 2022 phone.

## Conditional driver patch contract (USB owned; NOT committed)

**Path A, if read-only identity agrees with supported upstream `nxp,ptn3222`:**
- Preserve existing `nxp,ptn3222` compatible and generic PHY ops, add a *narrow* optional variant/board-specific tune table only with a justified silicon compatible or documented board quirk. Avoid a generic `qcom,param-override-seq` raw register ABI copied from vendor Android; prefer a reviewed variant-specific driver table where possible.
- Add `devm_regmap_init_i2c` with explicit reg/val width 8/8 (already compatible with mainline kernel); after verified reset and power, read `0x13..0x16`, reject known incompatible identity and emit exact actual observed revision. **Do not hardcode PTN3222 CUK/HUK readings until the selected part is established**.
- Sequence supply enables and reset according to the identified data sheet and board polarity, then apply exact oneli register values `{0x06,0x40}, {0x07,0x22}, {0x08,0x64}` only if supported by the identified revision's register semantics. Propagate `regmap_write` errors and unwind reset/regulators in reverse on failure. Preserve phandle `#phy-cells=<0>`; no downstream `usb-repeater` or `dummy-supply` properties.
- Enable only after Boot + Power validate parent supplies and PM8350C GPIO7 input/output ownership; `phys = <&actual_repeater>` on `&usb_1_hsphy`.

**Path B, if identity differs:** use an accurately identified compatible and a separate small `drivers/phy` I2C generic PHY/binding implementation rather than falsely bind to PTN3222. Prove which reset/supply/tuning resources it needs. Do not copy Qualcomm's unrelated PMIC eUSB repeater driver.

**Before identity, a generic `nxp,eusb2-repeater` upstream binding plus automatic tuning is *not* accepted as a patch**: the software cannot prove which chip interprets those registers. No vendor-only property has been added to the mainline board tree, no NXP-specific kernel driver patched on `razr/usb`, and no hardware success is claimed.

## Next exact verification when available

1. Pin oneli firmware/board SKU and board's actual stock DT/DTBO selection (public archive alone is comparator, not live chip proof).
2. After establishing actual I²C bus powered state, safely read-only 0x4f registers `0x13` and `0x14..0x16` and record values/return codes with host driver, SoC firmware SHA and reset state; do not probe electrically off an uncertain regulator.
3. Compare identity bytes to *datasheet of the observed SKU*, then write limited driver/binding patch with reproducible schema/compile gates and a disabled board node. Use mainline generic PHY `phys` consumer contract.
4. First actual USB2 debug acceptance remains serial/network gadget enumeration. **Phone currently unavailable.**

Status: **research and bounded driver design only**, no driver code patch because chip identity/physical reset semantics are unresolved, no driver build or oneli hardware test for this repeater.
