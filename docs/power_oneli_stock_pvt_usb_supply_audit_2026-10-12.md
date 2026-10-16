# Oneli PVT stock supply audit: NXP eUSB2 and PS5169

**Power owner, 2026-10-12, fourth coordinator round.** This is a source-hashed six-FDT **symbolic** analysis, not the handset's effective device tree and not an electrical test. Target stock reference: Motorola XT2251-1, build `U2SLS34.1-42-14-11`; observed handset PVT hwrev `0xC000`. Kernel baseline `Drzet/linux@a5ebb76233b79db01e82e061173cb73c6d2b5c6b`; source-reviewed current Boot `razr/boot@525b504b82dbca593a9a697af9be63f53915e0a3`.

## Audited evidence and repeatable method

- Source artifact: [VPU run 38220276125 / artifact 11734430639](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125/artifacts/11734430639); ZIP **SHA256 `485ff37b87cff2e6432928cfd4c0d4168bb3c10af163f6e68b6adfba35a528ae`**. Contained `stock-per-fdt-property-export.json`, **15,862,099 bytes**, SHA256 **`1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`**. The Power agent downloaded this *already existing* Actions artifact once (1.1 MB compressed), independently verified **both SHA256 digests**, inspected the parsed JSON's actual `nodes_with_requested_properties`, `/__fixups__` and `/__symbols__` records, rather than assuming a heuristic `candidate_phandle_edges` is a typed reference. No 4.35 GB ROM download or binary firmware copy.
- Supporting durable upstream references: [compact six-FDT summary](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-12-oneli-stock-fdt-properties.json), [consumer report](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-12-stock-fdt-consumer-report.md); VPU run was externally reviewed by coordinator in `FOURTH_REVIEW_VPU_UPDATE.md`.
- DTBO sha/index and board ID: index 0 `10c199f0…`, `0x45/0xb1b0`; 1 `1adcb600…`, `0x45/0xb2a0`; 2 `bdfc575a…`, `0x45/0xa100`; 3 `4fd14c77…`, **`0x45/0xc000`** (stock PVT reference candidate). Two separate embedded base FDTs SHA `8e269672…` MSM530 and `b8a243a0…` MSM540 are equal on these regulator facts, and both contain the `/__symbols__` entries below. Selected bootloader overlay/base identity remains unobserved.

**Direct audit assertions:** all four overlays' `/__fixups__` contain every one of the four requested exact `path:property:0` references below (16/16 checks passed), and both base FDTs' `/__symbols__` point S10B, L2B, L8C to the same expected provider paths (6/6 checks passed). Six base-provider voltage triples (two bases × three rails) are consistent. These assertions were executed locally against the byte-verified JSON using Python stdlib; **not CI or an FDT overlay-application test**.

## Confirmed consumers, supply-output regulators, voltages

| Vendor consumer | Original DTBO overlay property | Resolved base supplier symbol and path | Downstream declared min / initial / max µV |
| --- | --- | --- | --- |
| NXP `eusb2_repeater@4f`, under `/fragment@21/__overlay__` | `vdd18-supply` | **S10B** → `/soc/rsc@17a00000/rpmh-regulator-smpb10/regulator-pm8350-s10` | **1,800,000 / 1,800,000 / 1,800,000** |
| Same NXP node | `vdd3-supply` | **L2B** → `/soc/rsc@17a00000/rpmh-regulator-ldob2/regulator-pm8350-l2` | **2,700,000 / 3,072,000 / 3,300,000** |
| Parade PS5169 `redriver@30`, under `/fragment@49/__overlay__` | `vcc-supply` | **S10B**, same path above | **1,800,000 / 1,800,000 / 1,800,000** |
| Same PS5169 node | `vio-supply` | **L8C** → `/soc/rsc@17a00000/rpmh-regulator-ldoc8/regulator-pm8350c-l8` | **1,800,000 / 1,800,000 / 2,000,000** |

The exported standalone **base** phandle numbers are **S10B=62**, **L2B=758**, **L8C=772**, identical in both base FDTs. In the standalone overlays, cells contain `0xffffffff` placeholders; they become the supplier phandles *only after fixup against a compatible base*, **not** as direct integer references in a lone DTBO.

Other S10B consumers share the same symbol: BQ27426 flip gauge `bq27426-battery-flip@55:vdd-i2c-supply`, SGM41516D `sgm4154x@6B:vdd-i2c-supply`, and several audio/NFC consumers. This is **I²C/I/O supply**, not proof that S10B provides the flip charger's battery charge-power path. The alternate Diodes repeater `@6c` has the same rail fixups but is explicitly `status="disabled"` in all four overlays. NXP's *local* status is absent beneath an `ok` parent overlay, and PS5169's is `ok`; neither is proof of actual runtime powered/enumerated silicon or bootloader selection.

The source voltage ranges are regulator output capability/declared constraints, **not measured rails**, and `qcom,init-voltage` is a vendor initialization request, **not an assurance that power is presently on**. The three corresponding stock base regulator subtrees and their children have no explicit local `status` in the selected exports; **DT default-available** is not physical availability.

## Upstream parent-supply nomenclature is established; *which parent feeds oneli* is not

Pinned upstream driver source: [`qcom-rpmh-regulator.c`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/regulator/qcom-rpmh-regulator.c), PM8350 table around 1366–1393, PM8350C table around 1395–1421, and [binding](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml). `RPMH_VREG(..., supply_name)` selects a **grouped parent property name**. These names are **source-proven for mainline PMIC types**, but their corresponding **input phandle values and oneli board routing are unproven**.

| Supplier output | Correct mainline PMIC provider input property (established from driver) | HDK `sm8450-hdk.dts` value **[INFERRED] as oneli wiring** | Stock oneli parent conclusion |
| --- | --- | --- | --- |
| PM8350 **S10B** 1.8V | `vdd-s10-supply` | `<&vph_pwr>` (HDK models fixed 3.7V) | Physical handset VPH input supply not decoded; **do not invent fixed 3.7V** |
| PM8350 **L2B** 2.7–3.3V | `vdd-l2-l7-supply` | `<&vreg_bob>` (PM8350C BOB) | **[INFERRED]** BOB as L2B input; no oneli input-wire confirmation |
| PM8350C **L8C** 1.8–2.0V | `vdd-l2-l8-supply` | `<&vreg_bob>` (PM8350C BOB) | **[INFERRED]** BOB as L8C input; no oneli input-wire confirmation |
| PM8350C BOB (potential upstream branch parent) | `vdd-bob-supply` | `<&vph_pwr>` | Oneli stock provider output exists, **3,008,000 / 3,296,000 / 3,960,000 µV** min/init/max; its input and actual connection to L2B/L8C **not proven** |

Mainline grouped property `vdd-l2-l7-supply` means the PM8350 L2/L7 *share an input pin family*, **not** that L7's output powers L2. The same applies to PM8350C `vdd-l2-l8-supply`. The source HDK's BOB=3.296V initial setting does **not** prove dropout, sequencing, safe operating headroom or physical wiring for oneli. The full public stock *base* FDT's requested supplier properties contain the outputs and their voltage constraints, but **do not export any `vdd-s10-supply`, `vdd-l2-l7-supply`, `vdd-l2-l8-supply`, or parent-input `vdd-bob-supply` mapping on these downstream regulator nodes**. The downstream VRM representation has different regulator resource nodes; absence of mainline grouped inputs is **not** evidence of disconnected pins.

For UFS alone, the already-staged PM8350 L5B/L7B/L9B and PM8350C L10C source constraints and [prior review](power_oneli_rail_contract_v2_2026-10-11.md) still apply. PM8350 S12B is present at stock **1,224,000 / 1,256,000 / 2,040,000 µV**, but is **not** proven an input to S10B/L2B/L8C and does not belong in this USB supply chain. DTBO variant **2** has **A100-specific PM8010 i/j rails**; do not graft those onto PVT index 3.

## Exact Boot/USB disabled staging proposal and acceptance

**Current Boot kernel `525b504b82dbca593a9a697af9be63f53915e0a3`:** `arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dts` already defines **disabled** RPMh provider candidates `regulators-0` (PM8350 L5B, L7B, L9B) and `regulators-1` (PM8350C L10C) with disabled UFS/USB2 PHY. It does **not** yet instantiate S10B, L2B or L8C in mainline; the USB2 repeater and PS5169 do not have active board nodes. Their *source-proven output consumer connections* are now resolved sufficiently for a future **disabled only** staging review.

1. Boot may add inactive child candidates **`smps10` (S10B fixed 1.8V)** and **`ldo2` (L2B range 2.7–3.3V, vendor init 3.072V)** to existing disabled PM8350 provider, and **`ldo8` (L8C range 1.8–2.0V, vendor init 1.8V)** to existing disabled PM8350C provider. Preserve the distinction between range and set-point. Require current upstream binding/schema validation for declared child constraints. A source-defined *range* is not authorization to enable rail.
2. USB supplies the chosen NXP repeater driver/binding and the PS5169 error/unwind/reset/enable contract. Once these exist, Boot may stage **disabled consumer phandles** `vdd18/vdd3 → S10B/L2B` and `vcc/vio → S10B/L8C`. Do not equate reference enabled status with a mainline working driver. Diodes remains disabled for the PVT reference.
3. **No parent input phandle or `vph_pwr` board regulator is recommended for merge** until oneli source/effective composed DT, PMIC supply pin connection or hardware records substantiate it. Keep upstream parent **property names** recorded, but **[INFERRED] parent values** off DTS.
4. S10B serves charger *I²C* as well as USB and other consumers: Power owns any charger/paired battery activation; don't turn charging on while establishing USB2. Minimal UART/initramfs boot does **not** need USB repeater or PS5169. USB2-first needs correctly identified repeater power/reset; PS5169 is the later USB3/DP stage.
5. Exact missing *hardware* gates: PM8350 S10 input VPH; PM8350 L2/L7 input; PM8350C L2/L8 input; PM8350C BOB input; actual populated board revision/supply wiring, reset/power-up sequencing, I/O current/load budget and real regulator enabled state. No phone access for electrical measurements.

**Validation:** 16/16 overlay fixup assertions, 6/6 base symbol assertions, six consistent regulator range triples via local Python parsing of SHA-checked archived extraction metadata; pinned upstream C driver + schema and HDK source checked for precise input property names and comparison topology; current Boot source inspected. **No C/DT patch, dt-schema/build, libfdt overlay application, Linux regulator probe or phone test performed in this round**. Coordinator and Boot retain integration/build ownership; USB owns repeater/retimer driver/binding.
