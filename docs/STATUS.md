# Project status

Updated 2026-10-11 with subsequent stock Android ADB capture. Brief physical inspection is recorded; the phone is now disconnected. No native Linux hardware validation. Current instructions and concurrency gates: [NEXT_TASKS.md](NEXT_TASKS.md).

| Workstream | Current evidence | Next gate |
| --- | --- | --- |
| Baseline | [Clean ARM64 Image/dtbs passed](../tests/results/2026-10-11-baseline-ci.md) | Dependency-complete subsystem builds |
| Boot | Kernel `3825dc6afb0f5e102845b32811ce0f518c0b4bbf`: UART fix and disabled UFS rails; [DT run passed](https://github.com/Drzet/linux/actions/runs/38164785277), ARM/TLMM schema scope only | All-applicable oneli schemas; resolved-FDT audit; committed disabled GPU OPP proposal |
| GPU | Kernel `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`; temporary OPP DTB fixture passed; [module build failed](https://github.com/Drzet/razr2022_nuc/actions/runs/38164004265) at modpost, missing Module.symvers | Correct dependency-complete build and Boot OPP integration |
| USB | Kernel `6ab3f710b2c8e9a455bc356673ca67293ad4d322`; [PHY schema run passed](https://github.com/Drzet/linux/actions/runs/38164052929); source audit identifies repeater and PS5169 gaps | USB2-first proposal; attributable driver work; Power/DP contract |
| VPU | Kernel RFC `9bc913217b9051f515970c4b65770efb3374e33a`; [host audit/limited compile/schema passed](https://github.com/Drzet/razr2022_nuc/actions/runs/38165380924), unresolved-symbol warnings permitted | Full module build; schema/resource corrections; hosted stock inventory |
| Power | [Rail report](power_oneli_regulators_2026-10-11.md), [protocol report](power_oneli_charging_protocol_2026-10-11.md), synthetic fixtures; no power-specific kernel patch | Reproduce exact source CLI; assess actual parser defects; rail contract |
| DisplayPort | [Vendor software AUX truth table and graph audit](displayport_oneli_aux_routing_2026-10-11.md); no implementation | Reproducible checks and graph agreement; enablement awaits USB + valid AUX binding |
| Userspace | Project `b15c1dd292fface8928d8b70369472ac637cbe92`; [rootfs built, QEMU startup failed](https://github.com/Drzet/razr2022_nuc/actions/runs/38165284627) on missing ROM | Fix QEMU and tar ownership; add real networking/SSH acceptance |

All seven agents have immediate independent work. Only the integration steps identified in NEXT_TASKS.md must wait on other deliverables. No integration kernel or validated oneli boot-image recipe exists. The capture identifies XT2251-1 PVT (hwrev 0xC000, SKU dn), Android 14 U2SLS34.1-42-14-11, locked/green bootloader and active slot A. Public archive contents, exact loaded DT properties and native image packaging remain unverified.

Historical handoffs retain their original observation times. The completed run outcomes above supersede their pending-job statements. Researched, implemented, compiled, schema-tested, emulated and hardware-tested remain distinct evidence categories.

## Subsequent stock-device evidence

[ADB capture report](oneli_stock_android14_adb_hardware_capture_2026-10-11.md): registered dual-battery/GLINK topology and stock charging observations; configured USB gadget and advertised dual-role combinations; registered but inactive DP connector. No usable DT property export, firmware extraction or native boot was obtained. See the evidence update at the top of NEXT_TASKS.md for owner-specific consequences. The build table above remains the second-review snapshot; this evidence review does not claim a new audit of later subsystem commits.
