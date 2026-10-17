# Boot minimal dependency audit, third coordinator review

**Evidence:** Compiled FDT on exact Boot kernel revision. Baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`, Boot DTS at `6eec6ddd7842622668c937a466a8db47d20517b1` initially. Present staging head `525b504b82dbca593a9a697af9be63f53915e0a3`. This is **static phandle-graph evidence**, not an observed clock/probe/boot trace.

## Exact source of the 35 original warnings

Compiled FDT gate originally reported `nodes=893 reserved=39 overlaps=0 phandle_refs=888 decode_errors=0 active_to_disabled=35 GPU_OPPs=13` on [run 38175014232](https://github.com/Drzet/linux/actions/runs/38175014232). Unreviewed warnings were **not** treated as automatically harmless. Pinned underlying inherited `sm8450.dtsi` references are in `arch/arm64/boot/dts/qcom/sm8450.dtsi` at baseline.

| Classification | Count in original 35 | Exact source of active→disabled references | Boot disposition |
| --- | ---: | --- | --- |
| Nonessential LPASS codec macro children | 20 | 4 inherited enabled `codec@31e0000` (WSA2), `codec@3200000` (RX), `codec@3220000` (TX), `codec@3240000` (WSA), each references disabled Q6PRMCC clock provider and `vamacro` | Disabled all four board-side at kernel `28a10d03001acdfced14d4fcdf72c3794d1d684c`. Audio policy still unknown; no first-boot requirement. |
| LPASS LPI TLMM | 2 | `pinctrl@3440000` core/audio votes from disabled Q6PRMCC ADSP provider | Disabled `&lpass_tlmm` at `1bb36a60a3cf2e16fd219ce8e2fc0ace4671a755`. |
| Display clock PLL parents | 6 | Enabled DISPCC `clock-controller@af00000` references disabled DSI0 PHY `phy@ae94400` (2), DSI1 PHY `phy@ae96400` (2), QMP USB3/DP `phy@88e8000` (2) | Disabled `&dispcc` at `389439901ec2fa20c9b1e933625020ac4836d0e4`; display/DP remains deferred, not a minimal UART boot gate. |
| GCC clock parents | **7 remaining** | Enabled GCC `clock-controller@100000` references `phy@1c06000` PCIe0 (1), `phy@1c0e000` PCIe1 (2), `phy@1d80000` UFS PHY (3), and `phy@88e8000` QMP USB3/DP (1) | **Retain as unresolved boot-critical provider dependency risk**: GCC itself is needed for UART/system clocks; these are disabled PHY-sourced *input* clocks. Not an excuse to disable GCC, invent stub clocks or assume parent registration succeeds. Check GCC probe/clock orphan handling on actual first boot, and reconcile from source before enabling individual consumers. |

The four categories sum to **35**. The first audio cleanup reduced 35→15 ([run 38181866803](https://github.com/Drzet/linux/actions/runs/38181866803)); LPASS pinctrl cleanup reduced 15→13 ([run 38182047362](https://github.com/Drzet/linux/actions/runs/38182047362)); DISPCC deferral reduced 13→7 ([run 38182198571](https://github.com/Drzet/linux/actions/runs/38182198571)). The latest exact compiled-FDT gate with categorization [run 38182283694](https://github.com/Drzet/linux/actions/runs/38182283694) **passed** and retained `nodes=898 reserved=39 overlaps=0 phandle_refs=889 decode_errors=0 active_to_disabled=7 GPU_OPPs=13`. The increase of five nodes is source-only disabled USB PHY/GLINK graph staging, not hardware enumeration.

## Essential first-boot inventory and regression gate

The minimal source tree enables the QUP0 ancestor `/soc@0/geniqup@9c0000` and UART7 `serial@99c000`; its direct clock/interconnect provider references must not point to disabled devices. Root memory sizing, CPU/timer/interrupt/early firmware handoff remain reliant on bootloader-supplied FDT/memory data and do not have an oneli hardware runtime check.

Revised checker [`tests/scripts/check-oneli-dtb.py`](../tests/scripts/check-oneli-dtb.py), project commit `c35c4249bdd6b6353446f12505a4d2c7e693a5a8`, pins mandatory:
- correct SM8475 eUSB2 PHY compatible and **disabled** eUSB2, DWC3, PMIC GLINK;
- all four LPASS macro consumers, LPASS LPI TLMM and DISPCC **disabled**;
- GPU disabled and exactly thirteen OPP/corner pairs verified;
- UART7 and enabled QUP parent, no enabled UART path to disabled providers;
- all nonzero relevant phandle references parse, zero reserved-memory overlaps, and correct oneli ADSP/video memory entries.
- Each remaining enabled→disabled provider reference is classified; only GCC's seven **expected, still unproven** PHY-parent references are nonfatal. Any new unclassified or active audio/console missing dependency fails CI and requires human review.

**The GCC seven are a documented hold for physical boot probe evidence**, not whitelisted as benign runtime. No fake regulator parent or PHY clocks are introduced. No display, UFS, USB, GPU or VPU consumer enabled to clear a warning.

## Boundary

The checker validates static DTB references, not that RPMh/GCC clock registration/SoC boot succeeds. The compiled oneli DTB schema test (full applicable schema inventory) is separate from this FDT audit and must be read at the exact latest kernel SHA before considering source validation complete. No `Image`, modules, native kernel, or UFS/USB/DP hardware path was booted/tested by this Boot round.
