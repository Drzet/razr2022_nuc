# VPU to Boot: disabled-node evidence contract, not an enablement patch

2026-10-11. Kernel baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`; provisional VPU kernel `7f1d729b6f458f1e76efe2894eb3c544bc9db856`. Boot sole owner of shared SoC/board DTS. **No VPU node is requested for integration or runtime enablement yet.**

## Evidence that can be copied into a *disabled, incomplete design* only

| Field | Evidence | Scope |
| --- | --- | --- |
| Controller MMIO | Motorola `kernel-video-devicetree` `56e3632e15ab870f76920f80f19929addf48088b`, `waipio-vidc.dtsi`: address `0x0aa00000`, length `0xf0000` | Motorola Waipio family, not direct chip register read |
| IRQ | Same Motorola video source: GIC SPI 174 high level | Source-defined |
| Reserved video memory | Motorola oneli board `kernel-devicetree` `90fa7be1db5bd47202673d4431408659149a7359`: `0x9fd00000` + `0x700000`, no-map | Strongest board-specific source, not the effective runtime FDT |
| Firmware secure processor | Same Motorola video overlay PAS ID 9; existing mainline Iris firmware loader uses PAS 9 | Mainline interface match; signed firmware authentication **not checked** |
| Video GDSCs | Motorola controller source references `video_cc_mvs0c_gdsc` and `video_cc_mvs0_gdsc` | Source-backed *providers*, not final four-domain OPP map |
| Clocks | Motorola GCC VIDEO_AXI0, VIDEOCC MVS0C, MVS0 and source clock. Mainline Iris profile requests `iface/core/vcodec0_core` | Names translation review, clocks frequencies and OPP selection unresolved |
| Resets | GCC VIDEO_AXI0_CLK_ARES, VIDEOCC MVS0C_CLK_ARES | Controller source; kernel reset-controller compatibility needs checking |
| Oneli stock DTBO variants | Four publicly downloaded Android 14 DTBO root fragments: `model=oneli`, compatible `moto,oneli`, `qcom,cape-mtp`, `qcom,cape`, `qcom,mtp` | **Not** an effective selected VPU/controller FDT; no VPU properties observed in those fragments |

Verified public reference: [stock manifest](2026-10-11-public-stock-reference-manifest.md), [four DTBO/boot header report](2026-10-11-public-stock-boot-dtbo.md), exact ZIP SHA256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`. The handset stock ADB report records XT2251-1 PVT, hwrev 0xC000 and Android 14 U2SLS34.1-42-14-11. Matching build label is not proof of binary identity.

## Mandatory blockers before even a complete *disabled* schema-valid node

The provisional `qcom,sm8475-iris.yaml` and Iris probe require: four correctly named domains `venus,vcodec0,mxc,mmcx`, `operating-points-v2` and justified `required-opps`, three controller clocks, two resets, two ICC paths, at least one suitable upstream IOMMU endpoint, `dma-coherent`, and a verified `firmware-name`. The verified Motorola source **does not yet establish** exact RPMh corner votes, two upstream IOMMU specifier mapping, full nonsecure DMA address aperture, or an actual Linux firmware install path. Candidate `sm8475_data` currently borrows a [INFERRED] SM8250 bandwidth table and VPU2 sizing/capacity policy. **Do not fill these using guessed values just to make the schema pass.** The oneli-specific video controller may be supplied by a video DTB separate from the board DTBO.

**Update: source-backed signed-firmware candidates now LOCATED, not authenticated.** The [public reference radio manifest](2026-10-11-radio-non-hlos-firmware-manifest.json) documents `radio.img` → Motorola `SINGLE_N_LONELY` → `NON-HLOS.bin` → Android sparse → ext4 `image/vpu20_4v.mbn` (SHA-256 `9582ea4c5565408bd3e5ba6f8fffc7881f226cae001b6fcd7a0c868de9add9af`), `vpu20_4v.mdt` and 12 split `.bXX` files. The MBN's `QC_IMAGE_VERSION_STRING` is `video-firmware.2.4-33580ad5a949b4d45b3b008988280e60573cd894`; its ELF32 18 PT_LOAD sections cover *declared* physical addresses from `0x0f500000` to `0x0fbff020` exclusive. These are firmware image link/load descriptors, **not proof** of video controller DMA IOVA aperture or upstream IOMMU stream-ID mapping. The Linux `firmware-name` property must name an installed request_firmware-readable signed image whose packaging path is established; presence in Android ext4 alone does not establish that install path, selected radio partition, secure PAS 9 acceptance, or HFI protocol compatibility. [Hosted range/extraction run 38180934057](https://github.com/Drzet/razr2022_nuc/actions/runs/38180934057) passed and retained metadata only. The four-domain RPMh required-opps map, interconnect DDR lookup bandwidth, and upstream SMMU consumer entries **remain [INFERRED]** and were not resolved by ELF fields. The shared UBWC SM8475 LPDDR5 match has been sent to GPU for independent review via [issue #10](https://github.com/Drzet/razr2022_nuc/issues/10).

**Requested Boot action:** retain this as an evidence contract, not a board patch. When verified firmware names and provider mapping exist, Boot alone proposes a `status = "disabled"` node and runs the full oneli schema/FDT check against its own committed DTB. A disabled but missing-required-properties node is not a valid permanent solution. The handset is needed later for actual PAS 9/HFI/decode validation.
