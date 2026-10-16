# Subsystem handoff: Power, third coordinator review

- **Date / owner:** 2026-10-11, Power workstream, third coordinator review `docs/NEXT_TASKS.md` from `Drzet/razr2022_nuc/main`.
- **Kernel upstream baseline:** `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`, unchanged.
- **Power driver implementation, original tested branch:** `Drzet/linux razr/power@3b02b11bc5abdc5c453fa4af16b71bd8e44c2056` (inherited obsolete Boot ancestor `cb9105ebeb9485e31d044d4fa69396b415523669`).
- **NEW clean integration series:** `Drzet/linux razr/power-temp-standalone@564f2c7df60316db86e36d7267ddadf07bc32b7e`, **based directly on upstream baseline**, [kernel review PR #4](https://github.com/Drzet/linux/pull/4) against master; separate from historical [PR #3](https://github.com/Drzet/linux/pull/3). Exact sequential branch commits: `add9522b3a7ba4ae9d34ee670577c1a0f742585e` (decoder call and signed status), `a645ca00d80c8def170878e2283975ccacc209a8` (helper), `b08688eb8f8905da4a37a7644c381f0d579b7ff8` (KUnit), `0a7af7aeb9aa843547aa3bddc6b326fb04c49808` (Kconfig), `564f2c7df60316db86e36d7267ddadf07bc32b7e` (Makefile). **All five changed Git blobs independently compared to tested `3b02b11...` and match exactly.** `compare_commits` reports five driver-only files, ahead by five/behind by zero, **no shared Boot DTS, firmware, or baseline changes**.
- **Current Boot owner dependency reviewed:** `Drzet/linux razr/boot@df983169abb51a37d2555b3418bec188df049512`; UFS regulator candidate min/max fixed to Motorola source ranges; PMIC GLINK and USB2 HS skeleton remains disabled; no physical parent supply modeled.
- **Project evidence branch:** `Drzet/razr2022_nuc razr/power`, adds [third-round SGM41516D + paired-policy matrix](../power_oneli_charger_policy_third_review_2026-10-11.md) and this handoff. Coordinator controls main STATUS/NEXT_TASKS; neither updated here.
- **Evidence-stage split:** researched implementation/gauge/paired logic from pinned published Motorola-derived source; implemented/tested only the earlier independent signed-temp fix; no new charger driver written, no new build triggered for unchanged source, no native phone or charging test.

## Changes and provenance

### Integration-only repackaging

The corrected signed-temperature implementation has been republished from **upstream baseline** without old Boot ancestry. Same production conversion function `qcom_battmgr_decode_temperature(__le32)` and three `qcom-battmgr-temperature` KUnit cases. All five Git blob SHAs equal the prior test-passing implementation, verified using two exact `fetch_file` reads per file. No rebasing of shared Boot work or cherry-pick has been performed.

### New charger and policy evidence

Primary oneli compatible, DT charger/IRQ/GPIO and paired policy settings from `MotorolaMobilityLLC/kernel-devicetree@90fa7be1db5bd47202673d4431408659149a7359`. A **near-matching Motorola Qualcomm source comparator, not proven identical to oneli installed kernel modules**, exists at `LineageOS/android_kernel_motorola_sm8250@d0c1bd7e2578bba26e5e178702fae09596b11920`:

- `drivers/power/sgm4154x_charger_lite/sgm4154x_charger_lite.{c,h}` explicitly matches `sgm,sgm41516D`, parses `mmi,paired-ichg-table` and `mmi,paired-load-thres`, controls PMIC side load GPIOs and reads SGM ID `0x0b`. SGM41542 and SGM41516D masked ID values both `0x68`; matching ID alone **cannot identify exact variant**. Core register conversions are tabulated in new report. Oneli remains source-disabled while charging safety and aggregation are missing.
- The header hardcodes `SGM4154x_MANUFACTURER="Texas Instruments"`, and `get_property` returns that macro; **[INFERRED]** an explanation for the live stock `charger` supply's `MANUFACTURER=Texas Instruments` while `MODEL_NAME=sgm41516D`. Not evidence of Texas Instruments silicon.
- Motorola comparator `mmi_charger/mmi_charger.c` pairs IDs at opposite 16-bit halves, calculates full-capacity-weighted aggregate SoC, summed current/counter, mean voltage and hottest-pack temp; selects charge/low/high-load states using ESR-adjusted OCV differences and temperature zones. Oneli `mmi,upper-limit-capacity=80` is **not** necessarily an ordinary charge cap: comparator's upper/lower limiter is conditional on `enable_charging_limit && factory_version`.
- `bq27426_fg_mmi.c` resolves oneli `mmi,temp-source=<1>` to `TEMP_SOURCE_EXTERNAL` in its **published comparator enum**, and `mmi,ibat-invert-polority` changes current sign. Actual oneli built binary/profile activation remains unproven.

These are **a concrete plan and gap matrix**, not a direct import of Android charging source or a blanket `sgm41542` alias. The genuine oneli 2025/Android14 driver revision and exact 41516D data-sheet/register discrepancies remain missing for an implementation and safe enablement decision.

### VPU firmware extraction and stock PVT boundaries

Reviewed latest **post-third-review VPU disassembly/inventory**, branch `razr/vpu`, [nested radio manifest](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/vpu/2026-10-11-radio-non-hlos-firmware-manifest.json), and [filesystem scan](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/vpu/2026-10-11-stock-filesystem-firmware-manifest.json). Video `vpu20_4v.mbn` comes from `radio.img` → `SINGLE_N_LONELY` → `NON-HLOS.bin` sparse ext4, not `vendor_a`. SHA-256 `9582ea4c5565408bd3e5ba6f8fffc7881f226cae001b6fcd7a0c868de9add9af`, QC version `video-firmware.2.4-33580ad5a949b4d45b3b008988280e60573cd894`. Separate signed A730 ZAP/SQE there, GMU in `vendor_a`. The source-level ELF PT_LOAD addresses do not establish oneli regulator parent wires, RPMh OPPs or physical runtime; no PAS authentication. **Third coordinator report's pre-discovery 'not located' wording is now superseded.**

The four DTBO roots and `vendor_boot` region are hashed, but a **per-variant stock regulator/consumer phandle matrix has not been delivered**. Power appended [request to shared issue #10](https://github.com/Drzet/razr2022_nuc/issues/10#issuecomment-6114779437), asking VPU to include PM8350/PM8350C grouped input parents, BOB/S12B, UFS/USB2/charger nodes, GLINK and PVT numeric board ID in its **already-planned single shared metadata export**. No additional archive acquisition or guessed parent wire.

## Shared files and integration

- **Boot** owns `sm8475.dtsi` and `sm8475-motorola-oneli.dts`. Its current `df983169...` tree has already incorporated Power's suggested full **allowed voltage ranges** on **disabled** L5B/L7B/L9B/L10C nodes and disabled USB2-first consumer proposals. No action needed to retranscribe those ranges. Topology remains [INFERRED] pending extracted reference and eventual actual board access.
- **Coordinator** chooses ordered kernel commits; recommend the isolated [Power PR #4](https://github.com/Drzet/linux/pull/4) five commits *only*, not merging prior Power branch's inherited Boot ancestry. Combined Image/modules/oneli DTS schema check belongs to coordinator once integrated.
- **USB/DP** own connector/PS5169/AUX, Power only owns source-backed S10B/L2B/L8C regulator contract and charger safety. No duplicate consumer edit.
- **VPU** alone owns firmware archive extraction; Power consumes its metadata. Public reference package is not byte-verified against live handset.

## Validation

- **Verified earlier code source:** [GLINK pinned source CI run 38168888153](https://github.com/Drzet/razr2022_nuc/actions/runs/38168888153) passed 8 shared opcodes, 41 property IDs, 6 synthetic fixtures.
- **Verified production-source build:** [ARM64 object run 38169526109](https://github.com/Drzet/razr2022_nuc/actions/runs/38169526109) compiled `qcom_battmgr.o` and KUnit object under ordinary compiler errors.
- **Verified actual host kernel execution:** [UML KUnit run 38169484188](https://github.com/Drzet/razr2022_nuc/actions/runs/38169484188) passed **3/3** temperature-decoder tests. Also final project-branch [rerun 38169808394](https://github.com/Drzet/razr2022_nuc/actions/runs/38169808394) passed 3/3.
- **New standalone branch `564f2c7...` separately rebuilt:** **NO**, instead all five Git file blobs byte-identical to tested kernel SHA; preserve distinction. No dependency-complete final modpost or charging runtime test.
- **Published charger comparator built under our kernel:** **NO**. Source-only, no SGM current/charge writes; no new charging tests/compatible aliases.
- **Native hardware:** **NO**, unavailable. Android ADB stock measurements are separate from upstream testing.

## Blockers and next test

1. Await VPU/Boot's decoded four-variant PVT regulator and supply phandles; classify absent/unresolved instead of fabricating BOB/S12B/VPH parents. Existing disabled Boot nodes are sufficient for continued source work.
2. Before creating any SGM41516D driver patch, pin a compatible silicon/driver revision or datasheet with register-level divergence from `sgm41542`, verify safe CE/load controls and design main/flip paired policy independently. The Motorola SM8250 comparator does not prove actual oneli installed implementation.
3. Coordinator may review/cherry-pick PR #4 now, and run combined full Image/modules + DT/schema with actual selected SHAs. Need not repeat successful isolated standalone arithmetic tests unchanged.
4. Hardware only later: passive oneli charger chip register/ID read, physical regulator parents, runtime combined capacity/negative temp, charging/thermal fault and suspend/USB dock draw.
