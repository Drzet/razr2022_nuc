# GCC PHY clock warnings: source-based reclassification

2026-10-12 coordinator correction, after independently re-examining the user's proposed interpretation. Supersedes the earlier Boot report's “unresolved boot-critical provider dependency risk” and any aggregate wording implying seven missing hardware dependencies.

**Disposition:** identifiable deferred PHY clock inputs, handled by the clock framework's unresolved-parent mechanism. No demonstrated blocker to the minimal UART/initramfs milestone. Runtime registration and peripheral operation remain untested. No firmware recovery is required merely to identify these seven inputs.

## Source verified

Inspected these files at pinned baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`; local copies compared equal to the pinned Git objects:

- [GCC driver](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/clk/qcom/gcc-sm8450.c): named PHY parents, muxes, UART source and SM8475 probe adjustments.
- [CCF](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/clk/clk.c): `clk_core_fill_parent_index`, `clk_core_get_parent_by_index`, `__clk_init_parent`, `__clk_core_init`, `clk_core_reparent_orphans_nolock`.
- [Qualcomm registration](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/clk/qcom/common.c): `qcom_cc_really_probe` registers individual clocks, rather than unconditionally acquiring all GCC DT input clocks as mandatory consumer handles.
- [Register mux](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/clk/qcom/clk-regmap-mux.c) and [PHY mux](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/clk/qcom/clk-regmap-phy-mux.c).
- [Inherited DT](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/arch/arm64/boot/dts/qcom/sm8450.dtsi): GCC clock names and UART7's `GCC_QUPV3_WRAP0_S7_CLK` reference.

A failed parent lookup is not cached as a valid parent. CCF initialization places a clock with declared but unresolved selected parent on its orphan list; it does not reject registration solely for that missing parent. Orphan reparenting retries resolution as providers become available. This is a source fact, not a measured oneli probe trace.

## Per-input feature disposition

| GCC input | Registration model | Feature needing PHY clock operational |
| --- | --- | --- |
| `pcie_0_pipe_clk` | Single CCF parent; unresolved provider makes this source orphaned. PHY mux enable selects PHY, disable selects reference in hardware. | PCIe0 link |
| `pcie_1_pipe_clk` | Same single-parent PHY-mux model | PCIe1 link |
| `pcie_1_phy_aux_clk` | Two-parent mux: PHY AUX or `bi_tcxo`; current selection read from register | PCIe1 PHY AUX path when selected |
| `ufs_phy_rx_symbol_0_clk` | Two-parent mux: PHY symbol clock or `bi_tcxo`; current selection read from register | UFS receive path |
| `ufs_phy_rx_symbol_1_clk` | Same model | Additional UFS receive lane/path when used |
| `ufs_phy_tx_symbol_0_clk` | Same model | UFS transmit path |
| `usb3_phy_wrapper_gcc_usb30_pipe_clk` | Two-parent mux: PHY PIPE or `bi_tcxo`; current selection read from register | USB3 SuperSpeed path |

For the five two-parent muxes, CCF `__clk_init_parent()` calls `get_parent()` to interpret the hardware-selected source. It does not force selection of every PHY reference during registration. With a resolvable XO selection the source need not be orphaned; with an unresolved selected PHY it can be orphaned. The actual register selections on this phone are unknown. Do not equate seven static DT references with seven observed orphan clocks.

The PCIe PIPE implementation exposes only the PHY parent to CCF even though its enable/disable callbacks switch the hardware between PHY and reference. CCF topology and hardware mux state must be distinguished.

UART7 uses `gcc_qupv3_wrap0_s7_clk` → `gcc_qupv3_wrap0_s7_clk_src` → `gcc_parent_data_0`: `bi_tcxo`, GPLL0 main or GPLL0 even. None is one of the seven PHY inputs. QUP0 AHB branches do not declare those PHY parents either. This establishes independence of the examined console clock path, not proof that the complete phone boot succeeds.

## Milestones and remaining work

- Minimal serial/initramfs: these seven inputs are **not an identified prerequisite**. Keep nonessential PHY consumers disabled and proceed with combined build and diagnostic-image preparation.
- Internal-storage Debian: UFS controller/PHY/rails and the selected symbol-clock paths must operate before mounting a root filesystem on UFS. An initramfs-only milestone does not require that storage path.
- USB3: PIPE clock operation is a later SuperSpeed requirement, not an early serial-console or USB2 prerequisite.
- PCIe: defer until a project feature actually requires the corresponding link.

**[INFERRED]** The source mechanisms make these warnings manageable for initial bring-up; runtime must still confirm GCC probe, clock parents/rates and the UART path. CCF orphan handling alone is not a complete proof about all device-link ordering, GDSC registration or bootloader-selected mux states.

Boot's remaining task is a bounded source review of any separate device-link/probe-order constraint and a future runtime observation checklist, followed by feature-specific validation when enabling UFS/USB3/PCIe. Do not invent stub clocks, force XO selection, enable unused PHYs, remove legitimate references or block initial integration merely to clear this static warning count. Keep the checker warnings classified and visible; downgrade severity rather than suppressing evidence.
