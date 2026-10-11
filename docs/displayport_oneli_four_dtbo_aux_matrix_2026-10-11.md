# Oneli DisplayPort: four stock DTBO AUX variants, evidence matrix and hold

**Review date:** 2026-10-11, third coordinator assignment. **Owner:** DisplayPort, project `razr/displayport`; kernel `Drzet/linux:razr/displayport` remains **`a5ebb76233b79db01e82e061173cb73c6d2b5c6b`** (no DP source patch).

## 1. Scope and immutable provenance

This is the bounded offline report requested by [coordinator NEXT_TASKS](https://github.com/Drzet/razr2022_nuc/blob/main/docs/NEXT_TASKS.md). It **consumes existing metadata**, not proprietary blobs and not a second large archive download.

- Public RE*TEU* Android 14 reference package: `XT2251-1_ONELI_RETEU_14_U2SLS34.1-42-14-11_subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.xml.zip`, **4,353,164,507 bytes**, SHA-256 **`620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`**. [Actual acquisition run 38169190369](https://github.com/Drzet/razr2022_nuc/actions/runs/38169190369); [VPU verified manifest](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/vpu/2026-10-11-public-stock-reference-manifest.md). Matching *build label* does not establish byte-identical firmware installed on the phone.
- Reference `dtbo.img`: **24,117,248 bytes**, SHA-256 **`daf02eb24af55cf4c20569db51b5bca70f0550d035846672ef3054f0c0484bd0`**, Android DT table v0, four entries with **zero** table IDs, revisions and custom fields. [VPU compiled-candidate report](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/vpu/2026-10-11-public-stock-boot-dtbo.md), backed by [range verification run 38170215643](https://github.com/Drzet/razr2022_nuc/actions/runs/38170215643). Individual candidate `dtc -I dtb -O dts` returned success in that report. The actual decompiled node/property lists **were not published** in these manifests.
- The later [VPU filesystem manifest](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/vpu/2026-10-11-stock-filesystem-firmware-manifest.json) confirms a reference `vendor_boot.img` v4 **embedded DTB region 958,962 bytes**, offset **13,340,672**, region SHA-256 **`88b605e746f829545f3a5ceabc8ac669eee803db1397d32cc7f49ec91fbba71e`**. Its **actual FDT count, subblob boundaries, compatible list and AUX/DP properties are not in the shared manifest**. A region hash is not a decoded reference base FDT.
- Physical stock ADB [capture](https://github.com/Drzet/razr2022_nuc/blob/main/docs/oneli_stock_android14_adb_hardware_capture_2026-10-11.md) observed `XT2251-1`, **PVT**, `0xC000`, SKU `dn`, Android 14 `U2SLS34.1-42-14-11`. `card0-DP-1` existed but was **disabled**; permissions denied reading connector status/modes. The captured live DT archives have **zero property files**, so they cannot establish active overlay index or AUX wiring.
- Source comparator: Motorola `kernel-devicetree@90fa7be1db5bd47202673d4431408659149a7359` `qcom/cape-oneli-pvt-overlay.dts` gives **`qcom,board-id = <0x45 0xC000>`**, `qcom,msm-id = <530 0x10000>, <531 0x10000>, <540 0x10000>`, and includes `cape-oneli-common-overlay.dtsi`. These are **Android-12 reference *source* properties**, not inspected values of the four Android-14 DTBO FDTs and not the actual bootloader selection.

## 2. Four per-entry reference DTBO matrix

The table contains **all** independently verified per-index values available from the shared manifests. “Not extracted into manifest” is **not a negative property search**.

| Index | DT offset (bytes) | DT size (bytes) | DTB SHA-256 | Model/root compatibles (reported) | AUX switch SKU / GPIO2,71 properties / enabled DP route |
| --- | ---: | ---: | --- | --- | --- |
| 0 | 160 | 227,694 | `10c199f0176717d93eb2e99ae7a19e2fcaf3669d96655a0b31a8feff6e4a0f19` | `oneli`; `qcom,cape-mtp`, `qcom,cape`, `qcom,mtp`, `moto,oneli` | **Not extracted into manifest** |
| 1 | 227,854 | 227,761 | `1adcb600d11d3d2b1e25a75fc16e8b754439f279acea2dcecf97dec7d488752b` | same | **Not extracted into manifest** |
| 2 | 455,615 | 230,522 | `bdfc575aa20f2ccb00e9a2414119b03ac6229af531c906ff3f3068fc995cdf28` | same | **Not extracted into manifest** |
| 3 | 686,137 | 227,761 | `4fd14c771ecf9f6eadd8e9e56215bcb2858beda6808ce107ae45a9ce18173aad` | same | **Not extracted into manifest** |

**Common evidence across indices 0–3:** VPU's decompile summary observed both string compatibles `diodes,eusb2-repeater` and `nxp,eusb2-repeater`. Their presence does **not** establish which repeater node is enabled, the physical chip, or an AUX/SBU switch. Zero DTBO table IDs/revisions do **not** select the live PVT variant. No published variant-specific `qcom,board-id`, `qcom,msm-id`, `mmi,aux-switch-*` GPIO property values, IC compatible, DP status or endpoint graph were found in the *metadata*, not proven absent from the actual DTBs.

**Base-DT evidence matrix:** `vendor_boot` contains an embedded DTB **region** of known hash, but its individual base FDT(s) and their relevant properties have **not yet been surfaced**. The Qualcomm oneli overlay composition and bootloader choice are also unknown. Consequently no base+DTBO resolved property comparison can be made, and no claim that one of the four DTBOs is the handset's applied overlay is supportable.

## 3. Proven source-level oneli AUX software path (all variants as comparator only)

The [prior DisplayPort pinned audit](displayport_oneli_aux_routing_2026-10-11.md) uses Motorola display-driver `kernel-msm-5.4-techpack-display@701a48c1db80eda2ff17154a9017783230cc22aa` and display DT `kernel-display-devicetree@80b207bf35be5da38375e755506f136558ad24b5`:

| DP state | TLMM GPIO2 vendor software output | TLMM GPIO71 vendor software output | Evidence |
| --- | --- | --- | --- |
| Initial/disconnected | 1 (disabled) | 0 (normal) | `msm/dp/dp_display.c` initial values; `msm/dp/dp_aux.c` disconnect |
| DP active, CC1 | 0 (enabled) | 0 (normal) | `msm/dp/dp_aux.c` CC1 branch |
| DP active, CC2 | 0 (enabled) | 1 (flipped) | `msm/dp/dp_aux.c` CC2 branch |

- Motorola oneli display DT explicitly places these as `mmi,aux-switch-enable-gpio = <&tlmm 2 0x00>` and `mmi,aux-switch-flip-gpio = <&tlmm 71 0x00>`, and disables `&fsa4480`. The parent Cape `qcom,dp-aux-switch = <&fsa4480>` acts as an old driver-code guard; the inspected FSA event/notifier calls are commented out. **It does not identify the physical AUX IC.**
- `cape-oneli-common-overlay.dtsi` separately enables the Parade PS5169 **redriver** on I²C 0x30, with GPIO19 enable/disable pinctrl and GPIO91 orientation input. **PS5169 does not contain the SBU/AUX switch**. Motorola board-source properties cannot be silently assumed to appear unchanged in the four extracted Android-14 reference DTBOs.
- The public ARM64 baseline's `gpio-sbu-mux.c` implements Type-C mode/orientation switching. **[INFERRED]** `enable-gpios = <&tlmm 2 GPIO_ACTIVE_LOW>` and `select-gpios = <&tlmm 71 GPIO_ACTIVE_HIGH>` would reproduce the **connected vendor software writes**, *if* the actual part qualifies. However the binding `gpio-sbu-mux.yaml` requires a listed specific IC compatible followed by `gpio-sbu-mux`; no oneli switch SKU is established. A generic-only compatible would be schema-invalid.
- **NONE-state distinction:** Motorola disconnect writes GPIO71=0; generic `gpio_sbu_switch_set(TYPEC_ORIENTATION_NONE)` disables the mux but does **not forcibly reset** the stored orientation-select bit after CC2. With the switch disabled, this difference alone does not demonstrate a functional problem or justify a new generic driver quirk. Once hardware exists, explicitly observe CC2→disconnect→CC1 and CC2→disconnect→CC2 sequences.

Existing 23/23 source assertions remain validated by [CI run 38174309894](https://github.com/Drzet/razr2022_nuc/actions/runs/38174309894). **They have not been rerun**, per coordinator instruction; they do not validate any of the *unpublished* reference DTBO GPIO/graph properties.

## 4. Exact remaining derived fields, sent to shared owner

DisplayPort requested [shared issue #10, comment 6114740867](https://github.com/Drzet/razr2022_nuc/issues/10#issuecomment-6114740867) from **VPU/Boot**, using the existing centrally controlled extraction, a machine-readable per-entry FDT/property inventory (and individually parsed `vendor_boot` base DTB(s)) with:

- Node path, compatible, `status` and ancestor status, phandle/fixup semantics for `mmi,aux-switch-{enable,flip}-gpio`, `qcom,dp-aux-switch`, FSA4480, GPIO2/GPIO71 references, any independent AUX switch node, `mode-switch`/`orientation-switch`/`enable-gpios`/`select-gpios`, connector `port@2` and its endpoints.
- Related PS5169, QMP, UCSI/PMIC GLINK and DP endpoints, GPIO19/91, numeric `qcom,board-id` and `qcom,msm-id` by FDT. Only compare **enabled routes** after the actual composed tree and selection are justified.
- Source member + byte offset + FDT SHA256, extraction/parser/tool versions and clear `not present` **versus** `not yet inspected` per candidate; no radio/VPU/GPU firmware binary publications.

VPU's 4.35-GB acquisition was already centrally completed, with [radio NON-HLOS firmware now found and hashed](https://github.com/Drzet/razr2022_nuc/issues/10#issuecomment-6114680664). **DisplayPort will not make a duplicate uncontrolled download.**

## 5. Binding disposition, acceptance and hold

1. **Available evidence does not identify the actual oneli AUX/SBU switch IC or establish a conforming kernel compatible.** The missing per-DTBO and base values are a real, precisely scoped *metadata gap*, not evidence that no switch exists.
2. Until new FDT/BOM/schematic evidence arrives, no valid oneli AUX board node can be landed; do not invent a compatible, assume FSA4480, attach AUX to PS5169 or patch MSM DRM to hide an incomplete Type-C graph.
3. USB [versioned Type-C graph v1](https://github.com/Drzet/razr2022_nuc/blob/razr/usb/docs/typec_graph_contract_v1_2026-10-11.md) and [GitHub issue #3](https://github.com/Drzet/razr2022_nuc/issues/3) remain the accepted ownership contract: `connector@0/port@0` USB2/DWC3, `port@1` PS5169/QMP, `port@2` independent AUX only; GPIO91 single PMIC-GLINK input owner, GPIO2/GPIO71 DisplayPort source model, Boot owns board DT.
4. If VPU/Boot can supply the requested candidate properties, update this matrix once with *per-FDT inspected* identity and optional composed-tree resolution. If they do not identify a legally bindable switch, **hold AUX/DP board enablement pending real hardware identification**. This is the coordinator's bounded stop criterion, not an invitation to repeated generic audits.
5. **No kernel patch, DTB, schema, DP link, HPD, AUX, EDID, KMS, USB dock or physical test** is claimed by this report. Stock Android DP connector was registered but disabled; the phone is again inaccessible. DP kernel branch unchanged, no shared DTS touched.

**Consumers:** VPU/Boot to export *existing controlled-job metadata only*, USB to continue PS5169 driver candidate independently, Boot alone to integrate eventual shared DT only when USB/power/AUX prerequisites are justified, Coordinator to review this bounded hold alongside PR #11.
