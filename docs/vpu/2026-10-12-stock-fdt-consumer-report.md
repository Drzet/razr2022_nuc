# Shared oneli stock FDT property export for Boot, USB, Power, DP, GPU and VPU

**2026-10-12, source-only reference; not an observed live FDT.** This replaces the earlier incomplete four-DTBO hash/root-string list and zero-content live-DT archive attempts. Exactly **six** standalone FDTs were extracted with a Python FDT token parser from the verified public Motorola U2SLS34.1-42-14-11 ZIP, using only two bounded HTTP ZIP64 member requests (`dtbo.img` and `vendor_boot.img`) and per-member SHA-256 validation. **No 4.35GB repeat, raw FDT or proprietary images published.**

**Authoritative source and reproducibility:**
- [Compact machine-readable consumer JSON](2026-10-12-oneli-stock-fdt-properties.json): original table offsets, root numeric IDs, six hashes, VPU streams/paths/votes, AUX/USB/PS5169/PMIC and header metadata.
- **[Full 15,862,099-byte raw-property JSON artifact](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125/artifacts/11734430639)**: SHA-256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465` of `stock-per-fdt-property-export.json`; zip artifact SHA-256 `485ff37b87cff2e6432928cfd4c0d4168bb3c10af163f6e68b6adfba35a528ae`. **PASS** [workflow run 38220276125](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125), branch input `2fe785c0d3712128d58443792afd7f77794461d9`, actual tested PR checkout `3dfc56966217dbcadb7107d4df5c913a043b996a`. Pinned Python 3.12.3, parser Git blob `273517eeb62f7333f678b2722d4389743757982e`, HTTP ZIP64 reader blob `3ca9cacaaf441b8563839b6de971c95c10fe0430`.
- Full JSON includes all 6 FDTs' `node_index` with **each** node's path, local status, compatible/phandle and short reg; selected 900-1700 requested/raw hardware-prop records per FDT, phandle candidate edges, explicit ancestor statuses, full overlay `__fixups__`, `__local_fixups__`, `__symbols__`, selected exact `raw_hex`, `cells_be_u32` and source hashes, FDT reservation lists. Sensitive identifier property names deliberately redacted. **External fixup `0xffffffff` is unresolved, not a valid phandle value in the base tree.**
- Verified original ZIP SHA-256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`; `dtbo.img` SHA-256 `daf02eb24af55cf4c20569db51b5bca70f0550d035846672ef3054f0c0484bd0`; `vendor_boot.img` SHA-256 `1c27e22565f6f50919812bfcb5254cea2f3b629d98f5c26a7b54f5ece452036e`.

## Six reference FDT identities, all UNCOMPOSED

| Source | Index / offset within DTB region | Size, bytes | Numeric root ID | SHA-256 |
| --- | --- | ---: | --- | --- |
| DTBO | 0 / 160 | 227694 | `qcom,board-id=<0x45 0xb1b0>` | `10c199f0176717d93eb2e99ae7a19e2fcaf3669d96655a0b31a8feff6e4a0f19` |
| DTBO | 1 / 227854 | 227761 | `<0x45 0xb2a0>` | `1adcb600d11d3d2b1e25a75fc16e8b754439f279acea2dcecf97dec7d488752b` |
| DTBO | 2 / 455615 | 230522 | `<0x45 0xa100>` | `bdfc575aa20f2ccb00e9a2414119b03ac6229af531c906ff3f3068fc995cdf28` |
| DTBO | 3 / 686137 | 227761 | `<0x45 0xc000>` | `4fd14c771ecf9f6eadd8e9e56215bcb2858beda6808ce107ae45a9ce18173aad` |
| vendor_boot base | 0 / 0 | 479481 | `qcom,msm-id=<530 65536>` | `8e269672cd9d77da8575bf201c646c966219064cc0f9001bf512e7bf47455652` |
| vendor_boot base | 1 / 479481 | 479481 | `qcom,msm-id=<540 65536>` | `b8a243a0ae0569e64dfc85bc5ee15e2eeddf65aa2f4df406c24a8467e739c843` |

Both base root board IDs are `<0 0>`, both root compatible `qcom,cape`, model Qualcomm Cape SoC; both 3027 nodes and same VPU/USB/DP resource topology. The 4 DTBO roots share compatible `qcom,cape-mtp,qcom,cape,qcom,mtp,moto,oneli` and `qcom,msm-id` triple `<531 65536>,<540 65536>,<530 65536>`. The **physical stock ADB hwrev 0xc000** makes DTBO index 3 a *plausible reference candidate*, not proven selected. Neither base+overlay matching rules nor active bootloader FDT identity were captured. Vendor_boot FDTs are **not padded to 4 bytes** between images; offset 479481 must be accepted.

## Boot: exact vendor_boot v4 layout

`VNDRBOOT`, v4, page 4096, header 2128; `kernel_addr=0x8000`, `ramdisk_addr=0x1000000`, `tags_addr=0x100`, `dtb_addr=0x1f00000`. Vendor ramdisk offset 4096, size 13335589 and SHA-256 `5309c9a46937648872e84b94c2cbd592ad41c0fe2efc6be0319d497056f8986e`, **legacy LZ4** magic `02214c18` (from magic, not successful decompression test). Embedded DTB region starts offset 13340672, size **958962**, SHA-256 `88b605e746f829545f3a5ceabc8ac669eee803db1397d32cc7f49ec91fbba71e`, two FDTs verified as above. Ramdisk fragment table at 14303232 has one 108-byte entry, type 1, size13335589, fragment offset0, 16 board-ID cells zero; bootconfig offset14307328, 85 bytes, keys `androidboot.hardware`, `androidboot.memcg`, `androidboot.usbcontroller`. Do not copy stock loading addresses as silently accepted mainline packaging inputs or infer bootloader image choice. Boot retains packing/composition authority.

## USB: reference board-specific controller and retimer details

All four DTBOs contain **NXP eUSB2 repeater** `/fragment@21/__overlay__/eusb2_repeater@4f`, compatible `nxp,eusb2-repeater`, `reg=<0x4f>`; its local `status` property is **absent** under `/fragment@21/__overlay__` with status `ok`. `reset-gpio=<7 7 0>` references a local GPIO provider. Its `vdd18-supply`/`vdd3-supply` are unresolved external overlay fixups. Exact vendor tune `qcom,param-override-seq=<0x40 6 0x22 7 0x64 8>` and host sequence `<0x40 6 0x22 7 0x24 8>`. Alternate **Diodes** `eusb2_repeater@6c`, compatible `diodes,eusb2-repeater`, reg0x6c is **explicitly disabled** in all four. These prove source candidate statuses but not the chip physically soldered to oneli.

All four also contain `/fragment@49/__overlay__/redriver@30`, compatible `parade,ps5169-redriver`, `reg=<0x30>`, **status `ok`** with an `ok` parent. `redriver,enable-gpio=<0xffffffff 19 0>`, `redriver,orientation-gpio=<0xffffffff 91 0>`; unresolved external supplier fixups `vcc-supply`, `vio-supply`. `config-seq` 29 three-cell triplets, supplied as complete `raw_hex` and cells in full artifact; no generated supply identity/voltage. Mainline GPIO/regulator representation and reset semantics remain USB's responsibility. PMIC GLINK/connector references and QMP USB3-DP graph node paths/properties are in full JSON with explicit provider edges and fixup status.

## DP/AUX: definitive overlay status override

Both base FDTs contain `/soc/qcom,dp_display@ae90000` with `qcom,dp-aux-switch=<855>` referencing **`/soc/i2c@994000/fsa4480@42`**, compatible `qcom,fsa4480-i2c`, reg0x42, base status absent, I²C parent status `ok`. Yet **all FOUR board overlay `__fixups__` include TWO references to symbol `fsa4480`** whose target `__overlay__` fragments each have **explicit `status="disabled"`**:
- DTBO0: `/fragment@75/__overlay__`, `/fragment@88/__overlay__`
- DTBO1 and 3: `/fragment@76/__overlay__`, `/fragment@89/__overlay__`
- DTBO2: `/fragment@79/__overlay__`, `/fragment@97/__overlay__`

Therefore base presence does **not** justify enabling an FSA4480 AUX route; effective stock composition is still Boot-owned. Each oneli overlay also exports **two Motorola AUX GPIOs** `mmi,aux-switch-enable-gpio=<0xffffffff 2 0>` and `mmi,aux-switch-flip-gpio=<0xffffffff 71 0>` (fragment 76,77,80,77 for variants 0-3). These raw cells corroborate GPIO2/GPIO71 source software truth table but **do not identify actual discrete AUX switch part** or what the uncomposed external TLMM phandle resolves to. PS5169 is a retimer, not the stand-alone AUX mux. DP can now complete its source-bound variant matrix without inventing a new compatible.

## Power/GPU/VPU consumers

- **Power:** All FDTs' regulator/PMIC and parent/supply property paths/raw values, status and ancestor chains are available in the full JSON. Variant **2** adds `qcom,pmic-id` root data `<47 0 0 0 0 0 0 0 65 65>` and extra PM8010 i/j regulator and `gpio-regulator@0` fragments, which must not be transferred to PVT c000 without identity evidence. Exact rpmh regulators and external phandle supplier fixups remain *standalone overlay evidence*, not reconciled live parent wiring.
- **GPU:** SM8475 UBWC provider `qcom,sm8475 -> ubwc_4_0_hbb16` has already received GPU's source-level [cross-consumer approval](https://github.com/Drzet/razr2022_nuc/blob/razr/gpu/docs/gpu_ubwc_cross_subsystem_review_2026-10-11.md). Static HBB16 is still [INFERRED] and may be overridden by SMEM; this is not rendering/physical DRAM validation.
- **VPU:** Both base FDTs publish exactly matched `/soc/qcom,vidc@aa00000` node, two nonsecure SMMU context SIDs `0x2180`/`0x2187`, clock levels, 7MiB reserved region, PAS ID9 and *three*, not two, interconnect votes. Full [Iris resource and loader reconciliation](2026-10-12-iris-resource-loader-contract.md) records source-supported vs unimplemented translations and proposed Linux signed firmware path. No enabled board node or claimed decode.

## Scope and action for consumers

**This is the accepted missing-property publication, not an accepted composed DT.** The full JSON retains `raw_hex`, lengths and SHA256 for selected individual properties, and node path/status for every parsed node; all external `0xffffffff` overlay fixups are explicitly unresolved until Boot applies a verified base+overlay using symbol relocation. Please consume the [single shared export artifact](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125/artifacts/11734430639) and [persistent compact JSON](2026-10-12-oneli-stock-fdt-properties.json), not another stock ZIP. The export workflow has been returned to manual-only. No phone hardware state, AUX identity, VPU PAS loading, powered USB dock or DP link training was tested.
