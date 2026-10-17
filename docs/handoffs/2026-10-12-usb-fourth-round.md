# Subsystem handoff: USB fourth assignment, PS5169 failure semantics and stock PVT
- **Date / owner:** 2026-10-12, Motorola oneli native USB/Type-C.
- **Kernel repo / branch / head:** `Drzet/linux` `razr/usb-ps5169` **`2875777fef3496f33ad6862678251d1de00ee7f6`**, based on accepted attributable PS5169 `4cbfc0145d9c837d2ba3fd9050f529a786135403`, which branched from USB PHY+schema head `87d7277ced4c562e2379ee58aaed5c5fd7db4f32`. Upstream baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` unchanged.
- **Project repo / branch:** `Drzet/razr2022_nuc:razr/usb`, detailed source-backed [stock variant/configuration report](../usb_stock_pvt_variant_ps5169_2026-10-12.md) commit `2a9d03b06ffd98a5c1e46f1a0b1db2e46c723fe8`.
- **Primary dependencies:** Boot shared DTS staging at `525b504b82dbca593a9a697af9be63f53915e0a3`, eUSB2 PHY binding already included in Boot branch; Power's RPMh S10B/L2B/L8C contract, DisplayPort's GPIO2/71 independent AUX routing; VPU six-FDT reference export project `1a59d79fda42a977956de8e06c3a60d44b2971f4`, source ZIP SHA256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`, exported JSON SHA256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`.
- **Stages:** source inspected and implementation committed; injected host tests **passed** on latest exact code; schema **passed** at latest prebuild job; dependency-complete ARM64 Image/modules linking initiated on exact `2875777...` but check final completed run conclusion before asserting pass. Phone hardware validation **NO**.

## Changes and original authorship

Keep Esteban Urrutia's original v3 binding `3212e1d8a836f3dbbd0a258410b18683a38207ad` and driver `551c094e0ce5e7f492fe21d7e6ab2de815343b6a` intact as attributable ancestors. Earlier local headers `cbed833e9d5131fbed49774f385bba38bcd7944f` and VCC/VIO `4cbfc0145d9c837d2ba3fd9050f529a786135403` are separate source commits. New fourth-round USB commits:
- `bd5f6168529f156e812ed7ac95d863f8d408da46`: source `ps5169_write` returns I²C error from configuration, AUX/HPD, LFPS writes; `ps5169_init` propagates every EQ/gain failure; probe unwinds registered retimer/switch, enable and supplies; retimer/switch cache `mode/orientation/svid` rolls back on errors with dirty/invalid hardware state so same request retries; downstream mux failure triggers best-effort hardware rollback; independent changed SVID handled. Adds optional active-high `enable-gpios` alternative and fixes little-endian chip ID/revision via `le16_to_cpu`.
- `10634b58d676d8e98e25319e14b614bd7b759006`: documented mutually exclusive `reset-gpios` vs `enable-gpios`; examples include both S10B VCC and L8C VIO (the example itself selects only enable).
- `45743756e7078e8aee2754039aee2523910149ea`: include actual `linux/byteorder/generic.h`.
- `18da60d5358e32ced74f3e18f927fecac514acb7`: host executable test extracts **actual static PS5169 C production functions** and runs fake I²C/downstream errors; following `c6d1515c5a993dd3587642a86edd2ef65b76434c` fixes an unused-metadata warning in extraction-only mock.
- `5f81cf06788c739faed869edff122498f634a2e5`: hosted host-injection and ARM64 kernel/binding workflow.
- `2875777fef3496f33ad6862678251d1de00ee7f6`: probe programs initial safe mode before declaring `hw_valid`; failure unwinds. Earlier `ps5169_init` only wrote EQ/gain and did not actually establish safe Type-C work mode.

**Kernel PR #5 remains draft**: https://github.com/Drzet/linux/pull/5. Do not merge into minimal USB2 nor enable untested board consumers.

## Stock variant disposition and bound GPIO contract

[VPU full six-FDT artifact](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125/artifacts/11734430639) checked by USB: four standalone overlay roots index 0 `0x45/b1b0`, 1 `0x45/b2a0`, 2 `0x45/a100`, 3 `0x45/c000`; only index3 matches read-only PVT hwrev, not confirmed bootloader selected. All NXP 0x4f have absent local status under `ok` overlay while Diodes 0x6c are explicitly `disabled`. All PS5169 @0x30 are `ok`, `parade,ps5169-redriver` (vendor string), GPIO19 output `redriver,enable-gpio` with flag zero (active-high), GPIO91 vendor orientation input. External supplier fixups symbolically resolve NXP S10B/L2B and PS5169 S10B/L8C, not upstream electrical parent wires. Both Cape base FDTs MSM530/540 have matching symbol providers and regulator min/max: S10B **1.8–1.8V**, L2B **2.7–3.3V**, L8C **1.8–2.0V**. No demonstrated upstream `vin-supply` parent property in these exact regulator nodes.

Pinned vendor driver `MotorolaMobilityLLC/kernel-msm@0450c5076a8ec9415a10888c8c183ef6ff5f91b8` `drivers/usb/misc/ssusb-redriver-ps5169.c`: GPIO19 `gpio_set_value(en)` followed by 10ms delay when high; no GPIO reset pulse on enable. For USB/combined modes, downstream suspend deasserts enable; resume reasserts and replays entire register config. DP-only retains enable; alternative upstream PM wake path remains held.

**Exact correction to NEXT_TASKS:** raw `config-seq` has **27** `(register,value,delay_us)` triplets (**81 cells**), not 29, identical across all four overlays. First entries `(0x9d,0x80,10000)`, `(0x9d,0x00,0)`, `(0x40,0x80,0)`; complete verified table in linked report. Generic `parade,*-eq-db` knobs cannot reproduce this raw baseline. `0x9d` electrical meaning **[INFERRED]**; do not mislabel it a GPIO19 reset pulse. Neither generic upstream raw `config-seq` binding nor new board-specific profile committed; acceptance requires source review and hardware-safe restore contract.

NXP `qcom,param-override-seq` (value/register) normal `0x40/0x06,0x22/0x07,0x64/0x08`; host differs `0x24/0x08`. PM8350C GPIO7 local reset is **not** TLMM19 enable. Generic NXP model does not prove `nxp,ptn3222` exact SKU; no driver or enabled DT built.

## Shared files and integration

USB-owned candidate changes: `drivers/usb/typec/mux/ps5169.c`, `Documentation/devicetree/bindings/usb/parade,ps5169.yaml`, test script and CI workflow. **No edits** to shared `sm8475.dtsi`, `sm8475-motorola-oneli.dts`, Boot configuration or physical rail policies. Boot owns integration; GLINK remains single orientation GPIO91 owner; DisplayPort owns GPIO2/71 AUX. Correct connector work is independent and future.

## Validation

- Accepted previous full ARM64 Image/modules and binding at `4cbfc014...`: [run 38181747728](https://github.com/Drzet/linux/actions/runs/38181747728), module SHA256 `fd9b63ca50dd45d50e3a69b281ba1148673c39a33e359a03228a49846d05dea5`. **This is historical, not testing new source**.
- New host fault test [run 38242832686](https://github.com/Drzet/linux/actions/runs/38242832686) completed **PASS** on source `c6d1515...`: mode 5 injected I²C failure points all return -EIO and retry successfully, EQ/gain init 12 points all fail/retry, retimer mode failure retry, downstream mux failure, changed SVID with unchanged mode, switch I²C failure with downstream rollback, downstream switch failure. First run [38242557727](https://github.com/Drzet/linux/actions/runs/38242557727) failed **only harness compiler -Werror unused EQ metadata**; fixed in `c6d1515...`, not a production driver compiler error.
- Latest actual candidate `2875777...`: [new run 38243032057](https://github.com/Drzet/linux/actions/runs/38243032057) has **host fault test and DT-binding check PASSED**, full ARM64 Image/modules + ordinary modpost **running at handoff creation**. Accept only after completed job and linked `ps5169.ko` ELF SHA and exact config record.
- Test boundary: injected test compiles **actual extracted helper bodies** in userspace mocks; it verifies inits and transitions but **does not instantiate an I²C device or execute actual `ps5169_probe`**. Probe's fail/unwind labels are checked structurally. Thus real regulator enable/disable, GPIO timing, I²C bus readiness, and system suspend are untested. The next meaningful kernel failure suite should exercise probe under KUnit's fake regmap/regulator or a target harness rather than calling these hardware-tested.

## Remaining gates

1. Finalize exact-SHA ARM64 pass with module checksum or fix compiler/schema failure.
2. Hardware-independent focused review: decide whether and how to add a **board-specific typed PS5169 register profile** faithfully translating 27 stock entries, including 0x9d delay and retry/error propagation. Do NOT silently copy opaque `config-seq` vendor property into generic upstream schema. All raw profile assumptions remain held.
3. Resolve host regulator parent/voltage sequencing with Power/Boot and active-high enable ownership; no physical I2C chip identity, NXP reset/polarity and USB2/USB3 link evidence. Do not claim S10B/L2B wiring beyond stock symbolic regulator references.
4. PM: source-supported USB-only suspend deasserts enable and must replay profile on resume; mainline candidate keeps chip powered and so does not implement this policy. Preserve Type-C / DP connections until a safe wake/restore sequence is proven; no unreviewed suspend-on changes.
5. First phone tests when available: read-only NXP 0x13..0x16 ID (with safe power), PS5169 ID and GPIO19, role/orientation, USB2 enumeration, SuperSpeed and DP. Separate from boot kernel acceptance.

No merge, no native operation claims.
