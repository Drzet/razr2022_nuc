# USB/Type-C PVT reference: NXP selected, PS5169 enable and 27-triplet register profile

**2026-10-12, USB fourth assignment.** Source reference is the verified public Motorola `U2SLS34.1-42-14-11` archive, NOT verified on-phone effective DT. Latest coordinator task queue main blob `9a9b9b1f9a06c4f1998677871b9d25bee496d5e5`. Read [VPU's six-FDT consumer report](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-12-stock-fdt-consumer-report.md), [full metadata-only artifact 11734430639](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125/artifacts/11734430639), verified inner JSON SHA256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`. These lines were extracted by USB from **the actual downloaded 15,862,099-byte VPU JSON** at `stock-per-fdt-property-export.json`, not extrapolated from compatibility names. Vendor source comparator: [Motorola `ssusb-redriver-ps5169.c`, pinned blob `01ca89030bfd830c777d96efe67e8d0889235e5c`](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/0450c5076a8ec9415a10888c8c183ef6ff5f91b8/drivers/usb/misc/ssusb-redriver-ps5169.c), particularly `ssusb_redriver_enable_chip`, `ps5169_config_seqs_init`, work-mode handling, suspend/resume and probe.

## Four board overlays and precise status

| Index | Numeric board ID | Standalone FDT SHA-256 | NXP 0x4f | Diodes 0x6c | PS5169 0x30 |
| --- | --- | --- | --- | --- | --- |
| 0 | `<0x45 0xb1b0>` | `10c199f0176717d93eb2e99ae7a19e2fcaf3669d96655a0b31a8feff6e4a0f19` | no local status, parent overlay `ok` | `disabled` | `ok` |
| 1 | `<0x45 0xb2a0>` | `1adcb600d11d3d2b1e25a75fc16e8b754439f279acea2dcecf97dec7d488752b` | same | `disabled` | `ok` |
| 2 | `<0x45 0xa100>` | `bdfc575aa20f2ccb00e9a2414119b03ac6229af531c906ff3f3068fc995cdf28` | same | `disabled` | `ok` |
| 3 | `<0x45 0xc000>` | `4fd14c771ecf9f6eadd8e9e56215bcb2858beda6808ce107ae45a9ce18173aad` | same | `disabled` | `ok` |

**Correction:** the earlier USB second/third report's “both repeater compatibles are present, status unknown” is superseded: this reference **selects NXP at `/fragment@21/__overlay__/eusb2_repeater@4f`** and explicitly disables Diodes `eusb2_repeater@6c` under the same `ok` overlay. Oneli stock ADB read PVT hwrev `0xc000`, so index 3 is the **best matching reference candidate**, not a proven bootloader-selected overlay or physical soldered SKU. Both vendor_boot Cape bases are still separate: MSM530 FDT SHA256 `8e269672...`, MSM540 `b8a243a0...`, uncomposed, and both have matching USB resource topology. No source-only file proves electrical NXP identity.

### NXP repeater, I²C and supplies

- Node `/fragment@21/__overlay__/eusb2_repeater@4f`, downstream `nxp,eusb2-repeater`; value/register tuning `<0x40 0x06 0x22 0x07 0x64 0x08>`, **host** override `<0x40 0x06 0x22 0x07 0x24 0x08>`. These differ at register `0x08`: normal `0x64`, host `0x24`. Do not discard host-mode override when preparing future native PHY.
- `reset-gpio` cells `<7 7 0>`: local overlay GPIO provider phandle 7, pin 7, flag 0; Motorola source binds this to PM8350C GPIO7, **not TLMM19**. Reset output electrical polarity/settle time remains unresolved. `vdd18-supply` and `vdd3-supply` external overlay fixups resolve by base `__symbols__` to PM8350 S10B and L2B, respectively. S10B nominal 1.8 V; L2B vendor init setting 3.072 V in 2.7–3.3 V permitted source range. Exact upstream input parents still need Power/Boot confirmation.
- Diodes `diodes,eusb2-repeater` at 0x6c is disabled in all four standalone overlays. Do not stage it as active or assume PTN3222 exact compatible from the generic NXP string. No new NXP driver was bound on USB candidate.

### Parade PS5169: GPIO19 really is an enable

- All four overlay nodes `/fragment@49/__overlay__/redriver@30` declare `compatible="parade,ps5169-redriver"`, `reg=<0x30>`, `status="ok"`, `redriver,enable-gpio=<0xffffffff 19 0>`, `redriver,orientation-gpio=<0xffffffff 91 0>` (external `tlmm` fixup). Upstream in-tree driver matches `parade,ps5169`; **do not copy the vendor-only compatible verbatim into mainline**. USB-owned binding candidate now explicitly allows a mutually exclusive `enable-gpios` interface or original `reset-gpios` interface.
- Actual Motorola driver function `ssusb_redriver_enable_chip(ps5169,en)` directly calls `gpio_set_value(enable_gpio,en)`; if `en`, it waits **10 ms**. The same GPIO is driven low on disconnect, conditional USB-only suspend and shutdown; there is **no upstream-style 1 ms reset pulse in its normal initial enable sequence**. Local source-backed translation: `enable-gpios = <&tlmm 19 GPIO_ACTIVE_HIGH>`, regulator power then high enable + 10ms; **not** `reset-gpios`. GPIO91 is an **input read** for CC1/CC2 in vendor code; to avoid duplicate owners, proposed mainline connector GLINK remains sole GPIO91 owner.
- VCC external fixup resolves to PM8350 S10B; VIO to PM8350C L8C. Both source ranges are necessary; upstream parent routing and retained/boot-on state need Power sign-off. `enable-gpios` path is currently experimental: no oneli active node in Boot DTS.
- Vendor PM: if USB-only / USB+DP mode, suspend sets enable low and resume sets enable high then replays **the complete config-seq** followed by work mode. If DP-only/NONE/default it does not change enable. This is a software policy from downstream; it is not proof mainline should copy conditional low-power behavior while DP/GLINK events may arrive. The candidate currently holds regulators/enable across system sleep, with no `dev_pm_ops`. **PM policy is held pending upstream Type-C wake and profile replay design**. Turning off enable without reinitializing on resume would lose board configuration.

## Exact vendor config-seq from actual six-FDT export

**Important correction to coordinator wording:** **27 triplets, not 29.** Full raw `config-seq` consists of **81 big-endian u32 cells**, verified across overlay indices **0,1,2,3** with exact identical register/value/delay values. Third cell is `struct reg_sequence.delay_us` in Motorola's `ps5169_config_seqs_init` implementation, interpreted as microseconds. This is source-backed, not a proposed upstream raw-register binding.

| # | Register | Value | Delay µs |
|---:|---:|---:|---:|
|1|`0x9d`|`0x80`|10000|
|2|`0x9d`|`0x00`|0|
|3|`0x40`|`0x80`|0|
|4|`0x8d`|`0x01`|0|
|5|`0x90`|`0x01`|0|
|6|`0x51`|`0x87`|0|
|7|`0x50`|`0x20`|0|
|8|`0x54`|`0x11`|0|
|9|`0x5d`|`0x66`|0|
|10|`0x52`|`0x50`|0|
|11|`0x55`|`0x00`|0|
|12|`0x56`|`0x00`|0|
|13|`0x57`|`0x00`|0|
|14|`0x58`|`0x00`|0|
|15|`0x59`|`0x00`|0|
|16|`0x5a`|`0x00`|0|
|17|`0x5b`|`0x00`|0|
|18|`0x5e`|`0x07`|0|
|19|`0x5f`|`0x00`|0|
|20|`0x60`|`0x00`|0|
|21|`0x61`|`0x03`|0|
|22|`0x65`|`0x40`|0|
|23|`0x66`|`0x00`|0|
|24|`0x67`|`0x03`|0|
|25|`0x75`|`0x0c`|0|
|26|`0x77`|`0x00`|0|
|27|`0x78`|`0x7c`|0|

Register `0x9d` is toggled with a 10-ms delay *inside the register patch*, independently of GPIO19 enable. **[INFERRED]** a chip-internal reset/enable function; do not assert its electrical meaning without data-sheet support. The candidate's `ps5169_init` only programs selected generic EQ/gain masks, and `ps5169_set` programs work mode, AUX monitoring, HPD and optional LFPS. It **does not replay this 27-entry OEM register baseline**, including 0x9d, 0x61/0x65/0x67 and numerous zero clears. Worse, some board raw values are not losslessly expressible as candidate `parade,*-eq-db` pairs. Simply setting three generic EQ properties cannot be claimed to reproduce Motorola's register setup. Dedicated profile implementation requires a separate, source-reviewed patch, with return checking, and should not introduce `config-seq` as an opaque generic mainline ABI without binding review.

## Implementation handoff

The experimental [PS5169 kernel PR #5](https://github.com/Drzet/linux/pull/5) remains separate from minimal USB2. Fourth-round code now returns regmap errors, aborts EQ/initial-safe-mode probe on failure, avoids caching failed mode/orientation and detects changed SVID, plus LE-safe chip ID. The new `enable-gpios` vs `reset-gpios` mutually exclusive binding represents actual wiring rather than guessing a pulse. [Fault-injection CI](https://github.com/Drzet/linux/actions/runs/38242832686) exercises extracted actual production helpers and reported all injected positions and retries passed in its host job. Recheck completed ARM64 modpost and binding outcome for **final changed source SHA** before accepting its new build; earlier passing run 38181747728 covers only the prior source.

USB requests that Boot/Power retain disabled consumers pending effective PVT composition, oneli pinctrl details, upstream parent regulator constraints and vendor config-profile mapping. No hardware PS5169/NXP I²C probe, suspend, Type-C flipped cable or DP test was performed.
