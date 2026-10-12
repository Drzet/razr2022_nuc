# Motorola oneli DisplayPort: actual stock DTBO AUX variant matrix and binding decision

**Updated:** 2026-10-12; DisplayPort fourth coordinator assignment. **Status:** the four reference DTBO AUX property rows are now **inspected and resolved at the symbolic-fixup level**. **No live effective DT, actual AUX IC identification, schema-valid new AUX node, or native output test.**

Kernel DisplayPort branch `Drzet/linux:razr/displayport` is unchanged at **`a5ebb76233b79db01e82e061173cb73c6d2b5c6b`**. Boot alone owns changes to the shared `sm8475.dtsi` and `sm8475-motorola-oneli.dts`.

## Evidence: verified six-FDT export, not the failed phone DT capture

- **New direct reference evidence:** [VPU compact extracted property JSON](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-12-oneli-stock-fdt-properties.json), blob **`51a3ea64119a4f39de7be2197f1d706a97f5f939`**, and [VPU consumer analysis](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-12-stock-fdt-consumer-report.md). The [full six-FDT raw-property export artifact](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125/artifacts/11734430639) is metadata-only: internal `stock-per-fdt-property-export.json` **15,862,099 bytes**, SHA-256 **`1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`**; artifact ZIP SHA-256 **`485ff37b87cff2e6432928cfd4c0d4168bb3c10af163f6e68b6adfba35a528ae`**. [Run 38220276125](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125) passed with checkout **`3dfc56966217dbcadb7107d4df5c913a043b996a`**, Python 3.12.3, parser Git blob `273517eeb62f7333f678b2722d4389743757982e`. [Coordinator verification](https://github.com/Drzet/razr2022_nuc/blob/main/docs/FOURTH_REVIEW_VPU_UPDATE.md) separately checked artifact/file digests and sampled the actual raw properties and fixups.
- **Source container:** public Motorola `XT2251-1_ONELI_RETEU_14_U2SLS34.1-42-14-11...` reference ZIP, **4,353,164,507 bytes**, SHA-256 **`620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`**. Typed, bounded retrieval of `dtbo.img` SHA-256 **`daf02eb24af55cf4c20569db51b5bca70f0550d035846672ef3054f0c0484bd0`** and `vendor_boot.img` SHA-256 **`1c27e22565f6f50919812bfcb5254cea2f3b629d98f5c26a7b54f5ece452036e`**. No DP-owned ROM re-download.
- **Physical ADB distinction:** stock [read-only capture](https://github.com/Drzet/razr2022_nuc/blob/main/docs/oneli_stock_android14_adb_hardware_capture_2026-10-11.md) showed XT2251-1 **PVT**, hwrev **`0xc000`**, SKU `dn`, and `card0-DP-1` **registered but disabled**; neither uploaded “live DT” archive contains property files. The reference ZIP's matching build label does not prove identical installed bytes, bootloader overlay selection or external display operation.

## 1. Four *actual extracted* overlay AUX rows

These are the standalone FDTs decoded from reference `dtbo.img`, **not** the bootloader-composed live tree. All use root compatibles `qcom,cape-mtp`, `qcom,cape`, `qcom,mtp`, `moto,oneli` and root `qcom,msm-id` triplet `<531 65536>, <540 65536>, <530 65536>`. DTBO *table-level* ID/revision values are zero, while the **embedded root** `qcom,board-id` differs by variant.

| DTBO | Embedded root `qcom,board-id` | FSA4480 **target fragments**: each `status="disabled"` | Independent AUX control fragment | Exact property cells within AUX fragment |
| --- | --- | --- | --- | --- |
| **0** | `<0x45 0xb1b0>` | `/fragment@75/__overlay__`, `/fragment@88/__overlay__` | `/fragment@76/__overlay__` | enable `<0xffffffff 2 0>`, flip `<0xffffffff 71 0>` |
| **1** | `<0x45 0xb2a0>` | `/fragment@76/__overlay__`, `/fragment@89/__overlay__` | `/fragment@77/__overlay__` | enable `<0xffffffff 2 0>`, flip `<0xffffffff 71 0>` |
| **2** | `<0x45 0xa100>` | `/fragment@79/__overlay__`, `/fragment@97/__overlay__` | `/fragment@80/__overlay__` | enable `<0xffffffff 2 0>`, flip `<0xffffffff 71 0>` |
| **3, PVT reference candidate** | `<0x45 0xc000>` | `/fragment@76/__overlay__`, `/fragment@89/__overlay__` | `/fragment@77/__overlay__` | enable `<0xffffffff 2 0>`, flip `<0xffffffff 71 0>` |

Each of the **eight** FSA status records is `status = "disabled"` with `raw_status_hex = 64697361626c656400`, and its `__fixups__` target symbol is **`fsa4480`**. Across all four, the separate AUX fragment contains precisely `mmi,aux-switch-enable-gpio` with cells `[0xffffffff, 2, 0]` and `mmi,aux-switch-flip-gpio` with cells `[0xffffffff, 71, 0]`. The `0xffffffff` first cell is an **unapplied external phandle fixup placeholder**, not GPIO controller ID `0xffffffff`; the final `0` is the vendor GPIO flags cell, **not** proof of the upstream active polarity.

For full per-entry provenance, table offset/length/hash from the accepted source:

| DTBO | Byte offset | FDT bytes | SHA-256 |
| --- | ---: | ---: | --- |
| 0 | 160 | 227,694 | `10c199f0176717d93eb2e99ae7a19e2fcaf3669d96655a0b31a8feff6e4a0f19` |
| 1 | 227,854 | 227,761 | `1adcb600d11d3d2b1e25a75fc16e8b754439f279acea2dcecf97dec7d488752b` |
| 2 | 455,615 | 230,522 | `bdfc575aa20f2ccb00e9a2414119b03ac6229af531c906ff3f3068fc995cdf28` |
| 3 | 686,137 | 227,761 | `4fd14c771ecf9f6eadd8e9e56215bcb2858beda6808ce107ae45a9ce18173aad` |

Variant 2 additionally carries PM8010 i/j regulator fragments and a `qcom,pmic-id` tuple not present in the other variants; it **must not** be treated as PVT. PVT hwrev `0xc000` points to variant 3 as the **best reference candidate**, not proof of the bootloader's actual chosen FDT.

## 2. Base FDTs, symbols and *what is resolved*

Reference `vendor_boot` v4 embeds **two** Cape base FDTs, each **479,481 bytes**, concatenated **without padding**, at DTB-region offsets **0** and **479481**. Region begins at vendor_boot offset **13,340,672**, total **958,962** bytes, SHA-256 **`88b605e746f829545f3a5ceabc8ac669eee803db1397d32cc7f49ec91fbba71e`**.

| Base FDT | MSM ID | SHA-256 | Stock DP/FSA facts |
| --- | --- | --- | --- |
| 0 | `<530 65536>` | `8e269672cd9d77da8575bf201c646c966219064cc0f9001bf512e7bf47455652` | `/soc/qcom,dp_display@ae90000` `qcom,dp-aux-switch=<855>` → `/soc/i2c@994000/fsa4480@42` |
| 1 | `<540 65536>` | `b8a243a0ae0569e64dfc85bc5ee15e2eeddf65aa2f4df406c24a8467e739c843` | Same source-path/DP/FSA reference; distinct base MSM ID |

The **base** FSA node has `compatible = "qcom,fsa4480-i2c"`, `reg = <0x42>`, local `status` **absent** and an `ok` I²C parent. Base phandle 855 and a legacy `qcom,dp-aux-switch` property are **not evidence that FSA4480 is enabled after applying the oneli overlays**. Each oneli overlay directs **two explicit disabling assignments** to that same FSA target.

**Symbolic reference resolution verified against the exported PVT index-3 `__fixups__` and base `__symbols__` by the coordinator:**

| Overlay property/target | Overlay symbol | Exact reference base target |
| --- | --- | --- |
| `mmi,aux-switch-enable-gpio = <0xffffffff 2 0>` | `tlmm` | `/soc/pinctrl@f000000`, GPIO **2** |
| `mmi,aux-switch-flip-gpio = <0xffffffff 71 0>` | `tlmm` | `/soc/pinctrl@f000000`, GPIO **71** |
| Both FSA `status="disabled"` fragments | `fsa4480` | `/soc/i2c@994000/fsa4480@42` |
| PS5169 control and orientation GPIO19/91 | `tlmm` | `/soc/pinctrl@f000000` (USB-owned) |

This resolves the intended external symbol providers/paths. It **does not claim libfdt applied the overlay**, resolve all phandles into a byte-identical final FDT, or identify which base and variant bootloader actually uses. Boot owns that future composition audit. It is correct to interpret the AUX path as separate GPIO-controlled logic and **incorrect to re-enable FSA4480 based on its base-node presence**.

## 3. Interaction with PS5169, USB and Motorola AUX driver

The recovered independent stock Motorola AUX path is consistent across all four board variants. Pinned Motorola [display software source](https://github.com/MotorolaMobilityLLC/kernel-msm-5.4-techpack-display/blob/701a48c1db80eda2ff17154a9017783230cc22aa/msm/dp/dp_aux.c#L714-L778) proves its **software** GPIO truth table:

| State | GPIO2 output | GPIO71 output |
| --- | --- | --- |
| Disconnected / initialization | **1** (disable) | **0** (normal) |
| DP Alt Mode CC1 | **0** (enable) | **0** (normal) |
| DP Alt Mode CC2 | **0** (enable) | **1** (flip) |

All four DTBOs separately define **PS5169** `/fragment@49/__overlay__/redriver@30`: compatible `parade,ps5169-redriver`, `reg=<0x30>`, local `status="ok"`, `redriver,enable-gpio=<0xffffffff 19 0>`, `redriver,orientation-gpio=<0xffffffff 91 0>`. The PS5169 is a USB3/DP high-speed redriver; it **does not contain the DP SBU/AUX switch** (contrast PS5170). Never use PS5169's ports as the connector SBU `port@2`. The exact USB/Type-C graph and sole GPIO91 input owner are retained in [USB graph contract v1](https://github.com/Drzet/razr2022_nuc/blob/razr/usb/docs/typec_graph_contract_v1_2026-10-11.md) and [issue #3](https://github.com/Drzet/razr2022_nuc/issues/3).

The pinned upstream `gpio-sbu-mux.c` implements Type-C orientation and DP mode C/D/E enable logic. **[INFERRED]** If and only if oneli's actual AUX device is an evidenced supported GPIO-SBU design, `enable-gpios = <&tlmm 2 GPIO_ACTIVE_LOW>` and `select-gpios = <&tlmm 71 GPIO_ACTIVE_HIGH>` model the active vendor software writes. Vendor `<... 0>` flags and software writes are distinct representations. Upstream `gpio-sbu-mux.yaml` requires a real part-specific first compatible from its enumerated devices, followed by `"gpio-sbu-mux"`; **no verified part number** is present in this four-variant export. Do not write a generic-only or fabricated compatible.

**NONE-state behavioural difference:** vendor disconnect explicitly sets GPIO71 to 0; generic `gpio_sbu_switch_set(TYPEC_ORIENTATION_NONE)` deasserts enable but can retain the previous select state after CC2. Because mux output is disabled in this state, the difference is **not proven harmful**, and no generic driver change is justified from source alone. Retest CC2-detach-reconnect when hardware is accessible.

All four overlays also select the source NXP eUSB repeater @0x4f as an *enabled-by-default overlay child* (missing local `status`, parent `ok`) while the Diodes @0x6c child is explicitly disabled. This is **USB evidence**, not AUX identity. It does not turn either repeater or the FSA4480 into a stand-alone AUX switch.

## 4. Fourth-round verification, disposition and consumer handoff

**New input audit in this DisplayPort round:** directly read the immutable VPU compact JSON and checked **40/40 indexed structural invariants** across the four variants: root variant IDs, FSA fragment indices, both explicit disabled statuses and raw bytes, AUX fragment indices, GPIO2 and GPIO71 raw cell arrays, PS5169 status/GPIO19/91 and NXP-vs-Diodes statuses. These are programmatic **JSON consistency assertions**, not a new CI job, independent full-artifact reparse, compiled DT/schema or hardware validation. Source full-artifact hash/contents were independently checked by the coordinator (see linked amendment). The existing [23/23 pinned-source CI run 38174309894](https://github.com/Drzet/razr2022_nuc/actions/runs/38174309894) was **not rerun** because the sources did not change.

**Final AUX binding decision:** among (a) existing supported part, (b) justified new part-specific binding, (c) unknown IC, evidence supports **(c), identity unresolved**. The stock reference strongly rules out **FSA4480 enablement** in every oneli overlay and establishes the **GPIO2/71 control path**, but **never identifies the discrete switch device or compatible**. Existing mainline GPIO-SBU mode/orientation logic is a behavioural *candidate*, not an attributable hardware compatible. No new kernel driver, binding, or shared board node should be committed on this evidence alone.

**Gate / handoff:** DisplayPort's **variant-property audit is complete**. Boot consumes PVT variant-3 reference and both base variants to inspect type-correct applied overlay composition; USB continues PS5169 error handling and power/reset proof. Boot alone owns shared DTS. **Hold DP board enablement** until a justified AUX binding/device identity and USB/Type-C driver/graph integration exist. Actual DP/HPD/AUX/DPCD/EDID/monitor operation and FSA physical presence remain **hardware-untested**. No phone access or binary firmware authorization is implied.

**No DisplayPort kernel patch**: `Drzet/linux:razr/displayport` remains at baseline. No integration, compiled oneli DP DTB, schema-validation candidate, DRM probe or device test was performed in this round.


## 6. Fourth-review correction: ACTUAL six-FDT export consumed (2026-10-12)

**This section supersedes the earlier “not extracted into manifest” entries in section 2 and the property-export wait in sections 4–5.** VPU's subsequently accepted [six-FDT compact export](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-12-oneli-stock-fdt-properties.json) and [consumer report](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-12-stock-fdt-consumer-report.md) now contain actual standalone overlay values, not source-only assumptions. Coordinator [fourth-review VPU amendment](https://github.com/Drzet/razr2022_nuc/blob/main/docs/FOURTH_REVIEW_VPU_UPDATE.md) independently checked [successful run 38220276125](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125), full JSON SHA-256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465` and artifact ZIP SHA-256 `485ff37b87cff2e6432928cfd4c0d4168bb3c10af163f6e68b6adfba35a528ae`. This report consumes those *published metadata*; it does not reparse original FDT bytes or rerun the existing source CI.

### Corrected, complete four-overlay DP/AUX matrix

All GPIO triples below are **raw big-endian 32-bit FDT cells**, shown as `<external-fixup-placeholder GPIO flags>`. `0xffffffff` is not an actual provider phandle; `__fixups__` references the base symbol `tlmm`.

| DTBO | Board ID | Two fragments targeting base `fsa4480` and writing `status="disabled"` | Independent AUX GPIO fragment | `mmi,aux-switch-enable-gpio` | `mmi,aux-switch-flip-gpio` |
| --- | --- | --- | --- | --- | --- |
| 0 | `<0x45 0xb1b0>` | `/fragment@75/__overlay__`, `/fragment@88/__overlay__` | `/fragment@76/__overlay__` | `<0xffffffff 2 0>` | `<0xffffffff 71 0>` |
| 1 | `<0x45 0xb2a0>` | `/fragment@76/__overlay__`, `/fragment@89/__overlay__` | `/fragment@77/__overlay__` | `<0xffffffff 2 0>` | `<0xffffffff 71 0>` |
| 2 | `<0x45 0xa100>` | `/fragment@79/__overlay__`, `/fragment@97/__overlay__` | `/fragment@80/__overlay__` | `<0xffffffff 2 0>` | `<0xffffffff 71 0>` |
| 3 | `<0x45 0xc000>` **PVT reference candidate** | `/fragment@76/__overlay__`, `/fragment@89/__overlay__` | `/fragment@77/__overlay__` | `<0xffffffff 2 0>` | `<0xffffffff 71 0>` |

**Source-derived common conclusion:** Every reference variant independently provides the GPIO2 enable and GPIO71 orientation controls and explicitly disables the base FSA4480 via *two* fragment overrides. The FSA override's raw `status` bytes are `64697361626c656400` (ASCII `disabled\0`). This is a positive finding about the actual **standalone reference overlays**, not merely Motorola source. The PVT/hwrev `0xc000` observed via stock ADB makes index 3 the closest **reference** candidate, but neither active bootloader selection nor fully composed runtime tree is proven.

### Base target and symbol resolution

The extracted `vendor_boot.img` v4 region contains **two unpadded base FDTs**, both 479,481 bytes:
- Base 0 at region offset 0, MSM ID `<530 0x10000>`, SHA-256 `8e269672cd9d77da8575bf201c646c966219064cc0f9001bf512e7bf47455652`.
- Base 1 at region offset 479481, MSM ID `<540 0x10000>`, SHA-256 `b8a243a0ae0569e64dfc85bc5ee15e2eeddf65aa2f4df406c24a8467e739c843`.

Both have base `/soc/qcom,dp_display@ae90000` with `qcom,dp-aux-switch=<855>` referencing **`/soc/i2c@994000/fsa4480@42`** (`compatible="qcom,fsa4480-i2c"`, `reg=<0x42>`, base node `status` absent and I²C parent `status="ok"`). **This base phandle does not override the board overlay's two explicit `disabled` writes**. PVT overlay index 3 `__fixups__` symbol `fsa4480` targets this base node for fragments 76 and 89; symbol `tlmm` targets `/soc/pinctrl@f000000` for AUX GPIO2 and GPIO71. This is **symbolically resolved** against exported base `__symbols__`, not a claimed libfdt-applied final tree. The same external GPIO placeholders occur in all four standalone overlays. Boot owns actual base/overlay composition and selection.

### Final binding/ownership disposition

1. **Confirmed stock software topology:** independent GPIO2/GPIO71 AUX controls exist in all four overlays; FSA4480 is **explicitly disabled** in all four, despite the inherited base DP phandle; PS5169 is a distinct high-speed redriver, **not** an integrated AUX/SBU switch. Do not enable FSA4480 or assign PS5169 a fabricated AUX port.
2. **Unresolved physical IC identity:** neither exported overlay contains a defensible discrete AUX-switch part-compatible. Existing upstream `gpio-sbu-mux.yaml` requires a listed part-specific compatible. The candidate `GPIO_ACTIVE_LOW` enable and `GPIO_ACTIVE_HIGH` select are **[INFERRED]** mainline descriptors matching vendor software writes, not proof of the actual IC. **Binding choice: unresolved identity; HOLD board enablement.** No new driver/binding or DTS patch justified.
3. **Boot contract:** preserve `connector@0/port@2` for a future independent AUX switch, with DP0, PS5169, QMP, GLINK and GPIO91 ownership per [USB graph v1](https://github.com/Drzet/razr2022_nuc/blob/razr/usb/docs/typec_graph_contract_v1_2026-10-11.md). Boot alone may compose/apply and integrate shared board DTS; avoid importing the disabled FSA4480 vendor phandle as an active Linux route.
4. **Stop criterion met:** final actual variant matrix and symbol targets are documented. No more generic AUX source audit, re-download or unchanged CI is needed. Resume binding work only upon attributable AUX IC identification (BOM, schematic, readable chip marking or other authoritative evidence); physical DP tests remain deferred.

**Evidence classification:** source reference FDT values **verified in VPU's accepted extraction**, cross-source software GPIO truth table **verified previously**, base-to-overlay target resolution **symbolic**, physical switch identity **unknown**, on-device active overlay/DP operation **not tested**.
