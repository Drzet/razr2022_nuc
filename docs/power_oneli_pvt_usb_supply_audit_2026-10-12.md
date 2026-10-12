# Oneli PVT USB supply audit: resolved stock phandles, voltages, and electrical input-parent limits

**Power owner, 2026-10-12.** Research/metadata validation only. **Target stock candidate:** XT2251-1 PVT observed hwrev `0xC000`; reference DTBO index **3** has board-id `<0x45 0xC000>`. This is not a bootloader-selected effective FDT or a voltage measurement. **Kernel baseline:** `Drzet/linux@a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. **Boot board staging audited:** `Drzet/linux@525b504b82dbca593a9a697af9be63f53915e0a3`. No native hardware tests.

## Input and independently reproduced inspection

- **Actual six-FDT raw-property JSON:** downloaded the single approved [VPU artifact 11734430639](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125/artifacts/11734430639), [passing run 38220276125](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125). Decoded ZIP member `stock-per-fdt-property-export.json`: **15,862,099 bytes**, independently computed SHA-256 **`1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`** matching coordinator's record. Artifact ZIP declared SHA-256 `485ff37b87cff2e6432928cfd4c0d4168bb3c10af163f6e68b6adfba35a528ae`. Original source ZIP previously verified 4,353,164,507 bytes, SHA-256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`; **no re-download of stock firmware**.
- **DTBO 3** SHA-256 `4fd14c771ecf9f6eadd8e9e56215bcb2858beda6808ce107ae45a9ce18173aad`, offset 686137, size 227761. Stock **vendor_boot base FDT #0** `qcom,msm-id=<530 65536>`, SHA-256 `8e269672cd9d77da8575bf201c646c966219064cc0f9001bf512e7bf47455652`. **Base FDT #1** `<540 65536>`, SHA-256 `b8a243a0ae0569e64dfc85bc5ee15e2eeddf65aa2f4df406c24a8467e739c843`. Both base FDTs contain **identical** named PM8350/PM8350C regulator paths and values inspected below; exact bootloader choice unobserved.
- Inspection used the export's **actual** `per_fdt[3].nodes_with_requested_properties`/`/__fixups__` and both `per_fdt[4..5].nodes_with_requested_properties`/`/__symbols__`. Resolved named external `0xffffffff` placeholders **symbolically**; no synthetic numeric phandles, heuristic `candidate_phandle_edges` or unproved libfdt application. The export is a selected-property JSON projection, **not a lossless FDT**.
- Independent source comparator: [Motorola Cape RPMh definitions](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-regulators.dtsi) pinned `90fa7be1db5bd47202673d4431408659149a7359`; [upstream RPMh regulator binding](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml); [SM8450 HDK comparator](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/arch/arm64/boot/dts/qcom/sm8450-hdk.dts). The HDK is **not** the oneli physical wiring diagram.

## Four independently verified consumer-to-provider edges

| Board consumer | PVT stock property and overlay node | Exported `__fixups__` symbol | Exact stock base target | Evidence level |
| --- | --- | --- | --- | --- |
| NXP eUSB2 repeater I²C 0x4f | `/fragment@21/__overlay__/eusb2_repeater@4f:vdd18-supply:0` | `S10B` | `/soc/rsc@17a00000/rpmh-regulator-smpb10/regulator-pm8350-s10` | FIXUP+SYMBOL RESOLVED, not effective runtime |
| NXP eUSB2 repeater I²C 0x4f | `/fragment@21/__overlay__/eusb2_repeater@4f:vdd3-supply:0` | `L2B` | `/soc/rsc@17a00000/rpmh-regulator-ldob2/regulator-pm8350-l2` | FIXUP+SYMBOL RESOLVED |
| Parade PS5169 retimer I²C 0x30 | `/fragment@49/__overlay__/redriver@30:vcc-supply:0` | `S10B` | Same PM8350 S10B target | FIXUP+SYMBOL RESOLVED |
| Parade PS5169 retimer I²C 0x30 | `/fragment@49/__overlay__/redriver@30:vio-supply:0` | `L8C` | `/soc/rsc@17a00000/rpmh-regulator-ldoc8/regulator-pm8350c-l8` | FIXUP+SYMBOL RESOLVED |

All four reference overlays define the same NXP `vdd18/vdd3` and PS5169 `vcc/vio` fixups; index 3 is the **PVT-reference candidate**, not proven applied live. NXP node has no local `status` override inside an `ok` parent fragment; Diodes 0x6c is explicitly disabled. PS5169 node and containing fragment specify `status="ok"`. These are *vendor reference node statuses*, not permission to activate native Linux USB/DP/charging. In PVT `__fixups__`, `L8C` also targets `/fragment@48:target:0`; S10B also serves flip BQ27426 and SGM charger I²C `vdd-i2c-supply`, NFC and audio consumers. **An S10B dependency does not require enabling the charger or battery load switches.**

## Extracted base-provider voltage, initial-vote and status matrix

Numbers are in **µV**, directly from the two stock `vendor_boot` FDTs (530 and 540), which agree. `qcom,init-voltage` is a downstream initial setpoint, **not a physical measurement, or a permitted range by itself**.

| RPMh rail | Stock regulator node | Stock min..max | Stock `qcom,init-voltage` | Local `status` |
| --- | --- | --- | --- | --- |
| **PM8350 S10B** | `rpmh-regulator-smpb10/regulator-pm8350-s10` | **1800000..1800000** | **1800000** | absent (not disabled in stock base) |
| **PM8350 L2B** | `rpmh-regulator-ldob2/regulator-pm8350-l2` | **2700000..3300000** | **3072000** | absent |
| **PM8350C L8C** | `rpmh-regulator-ldoc8/regulator-pm8350c-l8` | **1800000..2000000** | **1800000** | absent |
| **PM8350C BOB**, *not a proven parent* | `rpmh-regulator-bobc1/regulator-pm8350c-bob` | 3008000..3960000 | 3296000 | absent |
| **PM8350 S12B**, *not a proven parent of the four consumers* | `rpmh-regulator-smpb12/regulator-pm8350-s12` | 1224000..2040000 | 1256000 | absent |

Each of S10B/L2B/L8C in the two stock FDTs has `qcom,set=<3>` and, for L2B/L8C, `qcom,init-mode=<4>`. Their provider *registration* and active electrical output are not observed on mainline; base missing `status` means DT default available, **not measured on**. The mainline board candidate currently stages PM8350 and PM8350C regulator providers `status="disabled"`, with only UFS L5B/L7B/L9B/L10C child entries. No native PS5169/NXP or S10B/L2B/L8C node is active.

A100 overlay index 2 has extra PM8010 i/j PMIC data. **Do not import those PVT-unsupported rails**. In PVT overlay index 3, the separate `L8C` `fragment@48` targets the regulator; this export does not prove a novel electrical parent or a measured voltage. Use Boot's composition pass for any further overlays on the target provider.

## Upstream input parents: supported group names, no proven oneli wiring

There are **two different meanings of “parent”**:

1. The consumer's **regulator provider** is fully source-resolved above. There is no longer a missing symbolic label for NXP or PS5169.
2. Each regulator's **electrical upstream input rail** is a PMIC physical connection. Neither the extracted source properties for the five named PMIC regulator outputs **nor** their oneli PVT fragment establish the real upstream electrical input. Stock downstream represents individual `qcom,rpmh-vrm-regulator` resources, not the upstream PMIC-group input phandles required for a definite graph. The exported selected-property records do not provide a `vin-supply`/`vdd-*-supply` link for S10B, L2B or L8C. **Do not read absence in a filtered JSON export as proof no physical input exists**.

The *correct mainline binding property names* for the relevant PMIC input groups are established by upstream source, independently of what oneli connects to them:

| Child/output | Correct mainline group input property | HDK only: example parent connection | Oneli conclusion |
| --- | --- | --- | --- |
| PM8350 S10B | **`vdd-s10-supply`** on PM8350 `regulators-0` | `<&vph_pwr>`, HDK artificial fixed 3.700V source | **[INFERRED]** real phone input unknown; must **not** copy HDK's fixed 3.7V pack rail |
| PM8350 L2B | **`vdd-l2-l7-supply`** on PM8350 `regulators-0` | `<&vreg_bob>`, the PM8350C BOB | **[INFERRED]** BOB is plausible and present in *both* stock base FDTs, but no stock parent phandle confirms its actual oneli wiring |
| PM8350C L8C | **`vdd-l2-l8-supply`** on PM8350C `regulators-1` | `<&vreg_bob>`, PM8350C BOB | **[INFERRED]** same; not established by the consumer's `vio-supply` alone |
| PM8350C BOB (if adopted) | **`vdd-bob-supply`** on PM8350C `regulators-1` | `<&vph_pwr>` | Battery power bus, topology, range and real voltage **not derived** from fixed HDK power source |

**No parent DTS patch is justified now.** The stock BOB's initial vote (3.296V) is source-backed and sufficient to identify that output's default *vote*, but it does not electrically prove that either LDO receives BOB, nor establish actual BOB regulation/voltage during USB operation. Likewise `qcom,init-voltage=<1800000>` on S10B says nothing about the actual incoming VPH voltage.

## Specific Boot/USB staging correction

- **Boot's owned DT at `525b504b82dbca593a9a697af9be63f53915e0a3`:** existing disabled PM8350 `regulators-0` and PM8350C `regulators-1` infrastructure is appropriate. When Boot stages *disabled* USB regulator consumers, it can source-back proposed child labels `oneli_s10b` (PM8350 smps10, 1.8V fixed), `oneli_l2b` (PM8350 ldo2, 2.7..3.3V) and `oneli_l8c` (PM8350C ldo8, 1.8..2.0V). If a driver actually requires a fixed initial setting rather than a range, retain initial vote separately in documentation until the native setting is justified; avoid treating downstream `qcom,init-voltage` as an upstream binding option. Keep RPMh providers/consumer nodes disabled. Do not put unresolved input-supply phandles in the DT.
- **USB:** NXP repeater `vdd18=S10B`, `vdd3=L2B`; PS5169 `vcc=S10B`, `vio=L8C`. The PS5169 regulator supplies are relevant to later USB3/DP, **not minimal USB2 or UART/initramfs bring-up**. NXP's local hardware reset contract and PS5169 GPIO19 enable/driver API remain USB-owned. Do not mislabel enable as reset or conflate controller PHY's 1.2V rail with NXP's 3.072V supply.
- **Power/read-only gating:** Qualcomm PMIC-GLINK main battery supply reporting and separately read-only flip fuel-gauge reporting are candidates for source review; the actual downstream oneli SGM41516D and Motorola paired policy involve PM8350C CE GPIO2 + PM8350B load GPIO1/GPIO3 and remain disabled. No unverified SGM41542 alias, GPIO manipulation, regulator `always-on` guess, firmware charging write or automatic paired balancing is justified.
- **Validation needed to resolve input parents:** an attributable oneli PVT schematic/board netlist; **or** a source-derived effective DT with actual PMIC `vdd-*` input-supply graph; **or** measured input-output relationship during the later physical test. DTBO symbol resolution alone answers consumer *phandles* but cannot substitute for any of these.

## Validation and stage

**PASS (metadata/source audit):** Independently recomputed SHA-256 for 15,862,099-byte JSON; for FDT #3 inspected exact NXP/PS5169 `__fixups__`, for *both* FDT #4/#5 inspected `__symbols__` and exact output regulator `regulator-{min,max}-microvolt`, `qcom,init-voltage` and local statuses. Compared parent property *names* with pinned mainline binding and HDK DTS and reviewed current Boot staging. **Not tested:** overlay application with libfdt; physical parent wiring; regulator voltage measurement; USB enumeration; charging; any mainline native boot. No source code changed and **no new kernel build** was run merely for documentation.
