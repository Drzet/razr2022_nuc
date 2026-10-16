# Power fourth-review handoff: PVT NXP/PS5169 stock supply and input-parent audit

- **Date/origin:** 2026-10-12, Power fourth-coordinator assignment, supply audit requested directly by user.
- **Project repo/branch:** `Drzet/razr2022_nuc` / `razr/power`. New [source/metadata report](../power_oneli_pvt_usb_supply_audit_2026-10-12.md) committed **`26f1f09b0cdbcf010473c7eacb757c85e6fc96bb`**. This handoff follows in a second documentation commit.
- **Kernel repo/Power revision:** `Drzet/linux@razr/power` **`3b02b11bc5abdc5c453fa4af16b71bd8e44c2056`**, unchanged. Separate coordinator-transplanted [standalone signed-temp PR #4](https://github.com/Drzet/linux/pull/4) `564f2c7df60316db86e36d7267ddadf07bc32b7e`, source-blob-identical to prior Power original; new combined kernel link still coordinator-owned and not claimed.
- **Baseline:** `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. **Boot dependency audited:** `525b504b82dbca593a9a697af9be63f53915e0a3`, plus Boot's subsequent own changes if integrated. Shared DTS solely Boot-owned.
- **Stage:** stock reference metadata independently inspected, reported as RESEARCHED; original signed-temperature code IMPLEMENTED and ARM64-object and UML KUnit 3/3 previously BUILD-TESTED; no **native mainline** battery/USB/power/thermal validation. Physical stock ADB confirms PVT hwrev `0xC000`, but no active FDT bytes.

## Source audit and results

Source: [VPU's six-FDT successful export](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125), [artifact 11734430639](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125/artifacts/11734430639). Downloaded exact approved artifact and independently computed **SHA-256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`** on **15,862,099-byte** `stock-per-fdt-property-export.json`. JSON source PVT reference `per_fdt[3]` DTBO SHA `4fd14c771ecf9f6eadd8e9e56215bcb2858beda6808ce107ae45a9ce18173aad`, board-id `<0x45 0xc000>`. Base FDT0 `MSM530` SHA `8e269672cd9d77da8575bf201c646c966219064cc0f9001bf512e7bf47455652`; base FDT1 `MSM540` SHA `b8a243a0ae0569e64dfc85bc5ee15e2eeddf65aa2f4df406c24a8467e739c843`. **Both stock bases agree on named output phandles and voltage values**. This is source-only symbolic resolution; no libfdt-applied active stock FDT claimed.

| PVT reference consumer | Overlay fixup | Base provider | Stock allowed µV | Downstream init µV |
|---|---|---|---|---|
| NXP eUSB `@4f` `vdd18` | `S10B` | PM8350 S10B | 1800000..1800000 | 1800000 |
| NXP eUSB `@4f` `vdd3` | `L2B` | PM8350 L2B | 2700000..3300000 | 3072000 |
| PS5169 `@30` `vcc` | `S10B` | PM8350 S10B | 1800000..1800000 | 1800000 |
| PS5169 `@30` `vio` | `L8C` | PM8350C L8C | 1800000..2000000 | 1800000 |

Stock base output regulator nodes have **no local disabled status**; that does not prove hardware rail on. Mainline Boot staged providers remain **disabled**. A100-only PM8010 rails specifically excluded from PVT.

**Electrical upstream parent audit:** correct mainline PMIC group property **names** from pinned `qcom,rpmh-regulator.yaml`: S10B `vdd-s10-supply` (PM8350), L2B `vdd-l2-l7-supply` (PM8350), L8C `vdd-l2-l8-supply` (PM8350C), and `vdd-bob-supply` for BOB input. The SM8450 HDK uses **[INFERRED as oneli]** `vph_pwr` for S10B and BOB, and PM8350C BOB for L2B/L8C. In actual both stock base FDTs the BOB regulator itself exists with **3008000..3960000 µV, init 3296000 µV**, and S12B with **1224000..2040000 µV, init 1256000 µV**. **No verified physical parent wiring can be derived from the filtered selected stock FDT properties or referenced overlay**. HDK includes artificial fixed 3.7V `vph_pwr`: **do not copy that into oneli**. No assumed input-phandle patch proposed.

## Integration and inter-agent boundaries

- **Boot:** Can stage (disabled) source-backed PM8350 S10B `smps10`, L2B `ldo2`, PM8350C L8C `ldo8` labels with documented voltage ranges, but must not enable consumers, copy donor-HDk BOB/VPH parent group wiring or treat `qcom,init-voltage` as a mainline property. Choose output constraints deliberately; only Boot changes board DTS and reruns schema/FDT.
- **USB:** NXP requires both S10B and L2B for first USB2 experiments; PS5169 needs S10B + L8C for later SS/DP. Confirm local reset/enable separately; supply resolution does not solve sequencing or prove actual chip.
- **Power:** Read-only Qualcomm GLINK main battery and BQ27426 flip gauge require separate probe/write audit, while Motorola SGM41516D CE/load switches and paired charging manager remain held. Previous signed-temperature standalone driver is ready for combined dependency-complete linking. **No changes to source/kernel shared tree this round.**
- **Coordinator:** Selected integration and normal modpost with Boot/GPU/Power remains outstanding at snapshot. No repeated unchanged ARM64/KUnit workflow requested. Workflows on Power project branch already restrict push triggers to workflow/scripts, avoiding documentation-triggered object rebuilds.

## Validation

**PASS:** original extracted JSON checksum; exact source-scope `__fixups__` fields against `__symbols__` in both bases; signed integer voltage parsing and source `qcom,init-voltage`/min/max; independent pinned RPMh binding group names, SM8450 HDK comparator, and Boot current DTS inspection. **NOT RUN:** libfdt composed overlay (Boot owns), firmware/binary re-extraction, new kernel build, active VBUS/USB/charging/electrical tests. Source export includes selected properties, not lossless full DTBs.

## Blockers and next test

1. Boot's full *effective* PVT composition once selection rules are grounded; verify voltage and status after any regulator-targeting fragments (notably `L8C` via PVT `fragment@48`).
2. Physical supply parents demand an attributable oneli board netlist/schematic, source-verified PMIC input graph or later electrical probing. Without that, hold `vdd-s10-supply`, `vdd-l2-l7-supply`, `vdd-l2-l8-supply`, `vdd-bob-supply` **values**, even though their mainline *property names* are known.
3. Coordinator combined full dependency-linked Image/modules + oneli schema/FDT at pinned SHA for stand-alone battmgr temperature fix; native GLINK and charger tests remain hardware only.
