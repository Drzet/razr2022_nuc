# VPU fourth-round handoff: verified Motorola reference firmware

Date: 2026-10-11, VPU subsystem agent. Assignment: coordinator main docs/NEXT_TASKS.md (third review, file SHA fd33173324a2a97befcd87238271b36fa949ac74).
Kernel: Drzet/linux branch razr/vpu, **7f1d729b6f458f1e76efe2894eb3c544bc9db856** (RFC, unchanged); baseline **a5ebb76233b79db01e82e061173cb73c6d2b5c6b** unchanged. Project: Drzet/razr2022_nuc branch razr/vpu; branch SHA should be read from [draft PR #1](https://github.com/Drzet/razr2022_nuc/pull/1) since committing this handoff advances it. Boot board reference reviewed at kernel 6eec6ddd7842622668c937a466a8db47d20517b1, not combined. Research: yes; implemented extraction scripts: yes; verified host extraction: yes; full ARM64 compilation: prior run 38170604512 pass; device PAS, HFI and decode: **not tested**.

## Source/provenance

Public Motorola U2SLS34.1-42-14-11 Android 14 stock archive [original reference](https://mirrors-obs-1.lolinet.com/firmware/lenomola/2022/oneli/official/RETGB/XT2251-1_ONELI_RETEU_14_U2SLS34.1-42-14-11_subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.xml.zip) is 4,353,164,507 bytes, SHA-256 **620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c**. Previously captured XT2251-1 PVT Android build label matches, but installed signed bytes and chosen overlay were not read: this is **reference firmware, not installed firmware attestation**.

Formats identified by signatures and parsers, never raw concatenation: sixteen individual Android sparse v1 super chunks reconstructed into a 11,811,160,064-byte logical partition super image; Android LP geometry verified; six ext4 logical filesystem instances and external dspso.bin ext4 scanned. Separate radio.img (203,319,040 bytes, SHA-256 **bcaac550d908ea72f08e9a1782714a46f52d26f20ec11c7e32f97140677769ca**) is Motorola SINGLE_N_LONELY, containing NON-HLOS.bin (178,827,436 bytes, SHA-256 **03d37634aa39ff9af06d3b583267e6d166996c22e7b4f06b0bcb7d7b4031a1d9**) as Android sparse v1 with twelve typed chunks. NON-HLOS expands to 414,187,520 bytes of ext4 (SHA-256 **2ea61a0b5d31b626358f0b72c102131535f08ae3fb279b1857e646b0675416c6**), with 639 file paths examined. The packed fsg.mbn member is separate ext4, 840 file paths examined and no firmware-name matches.

Exact scripts and metadata:
- [Format-aware sparse super reconstruction](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/scripts/reconstruct-oneli-super.py) parses RAW/FILL/DONT_CARE/CRC and checks bounds.
- [Partition and firmware inventory](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/scripts/inspect-oneli-lp-firmware.py) uses upstream Python lpunpack pinned to commit c59b8f3b069c5a8aa438a049fa4a091177172434, blob 9671d1d731d28f04f0d65dad0dacb2110da87029, read-only ext4 scanning, SHA256, ELF/MBN/QC markers.
- [Bounded radio-only HTTP-range/Motorola container/nested sparse parser](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/scripts/inspect-oneli-moto-radio.py).
- [Machine-readable detailed NON-HLOS manifest](../vpu/2026-10-11-radio-non-hlos-firmware-manifest.json) gives all 28 matching files, paths, sizes, SHA256 and parsed ELF data; [super/vendor JSON](../vpu/2026-10-11-stock-filesystem-firmware-manifest.json) covers searched partitions, failures/negative coverage and vendor_boot metadata.
- Neither binary payloads nor proprietary partition images were committed or uploaded. Expensive CI runs have been returned to manually dispatched only.

## Actual firmware

VPU: NON-HLOS ext4 image/vpu20_4v.mbn **2,024,040 bytes** SHA-256 **9582ea4c5565408bd3e5ba6f8fffc7881f226cae001b6fcd7a0c868de9add9af**; sibling image/vpu20_4v.mdt **5,404 bytes** SHA-256 **a276e19d4ba6f4b4b42bec7ee4497e1002582a357454d56e5e050d5f969c64b6**, and twelve source-hashed .b00..b09, .b18, .b19 split segments. QC_IMAGE_VERSION_STRING is **video-firmware.2.4-33580ad5a949b4d45b3b008988280e60573cd894**. MBN and MDT parse as ELF32 18 PT_LOAD with declared physical load addresses from **0x0f500000** through end-exclusive **0x0fbff020**; this is firmware link metadata, NOT host video IOMMU aperture.

GPU: same NON-HLOS image/a730_sqe.fw **74,676 bytes**, SHA256 **e67d1829f57fc8326d806234b932dc3b78e28a9940df34c70752f17d5f38b7aa**; image/a730_zap.mdt **4,044 bytes**, SHA256 **f5d8a41c1380ba2b42cd742538083306d245471ac5d51139e3bc8a6168ce84d2**, plus three separately hashed .b00/.b01/.b02; ZAP ELF32 advertises one PT_LOAD 0x1000..0x18bc and Qualcomm-specific flags. Separately, super:vendor_a/firmware/gmu_gen70000.bin **57,272 bytes**, SHA256 **b2d3f0e2a98fd6259ab9ffef16df63265542e6cc9a970d53d476e823d432042a**. No c500_gmu name seen in all successfully scanned reference ext4 instances, not a guarantee across unexamined firmware/partitions.

Other vendor_a Venus ELF32 variants have distinct video-firmware.2.6-466e8c... version: **do not equate these with the actual Motorola VPU20_4V 2.4 candidate**. Split MDT/Bxx file presence, ELF flags or QC version strings do not validate signed PAS9 authentication or HFI Gen2 acceptance.

## Validation and tested SHAs

**PASS** complete controlled ROM LP scan [run 38180072535](https://github.com/Drzet/razr2022_nuc/actions/runs/38180072535), GitHub head e7e2c9c06f20f8844cf04e37767369d2fed23ce2 and actual PR checkout 433a8cd23fbc0ac205baab448cd142efeec20eae. [Artifact 11717379423](https://github.com/Drzet/razr2022_nuc/actions/runs/38180072535/artifacts/11717379423), SHA256 e151032c53111a9a54efc8b7c4e933ad7e5aeaacb00852774febf598b0b8140a.

**PASS** bounded radio/SINGLE_N_LONELY/NON-HLOS nested ext4 scan [run 38180934057](https://github.com/Drzet/razr2022_nuc/actions/runs/38180934057), source branch commit 16e6e620064a3baacf05b9362e79404004fe5f6a and tested PR checkout c4be91a4613192f7d0526c95dac32544a63601ce. [Artifact 11718485158](https://github.com/Drzet/razr2022_nuc/actions/runs/38180934057/artifacts/11718485158), SHA256 6d189e7b663788a9e6c18d49d9025c0420106737cd0e05d56027490943bc3b47. Metadata only, no signed binaries. CI retained Python/tool/package versions and logs.

Prior host strict ARM64 Image/modules build and new binding schema **PASS** [38170604512](https://github.com/Drzet/razr2022_nuc/actions/runs/38170604512), no unchanged rebuild needed. Earlier 38179038843 LP parser failure (different JSON partition-list key) fixed; earlier 38178912619 duplicate CI canceled before extraction.

## Shared derived DT/boot facts

[Source-hashed boot and four-DTBO-variant report](../vpu/2026-10-11-public-stock-boot-dtbo.md): boot.img and vendor_boot.img both v4; vendor_boot header 2,128 bytes, page 4096, ramdisk size 13,335,589, embedded DTB region size **958,962** at offset **13,340,672**, DTB region SHA-256 **88b605e746f829545f3a5ceabc8ac669eee803db1397d32cc7f49ec91fbba71e**. Ramdisk table contains one 108-byte entry with zero board IDs; bootconfig 85 bytes with three reported androidboot keys. Four public DTBO root candidates all model oneli, matching qcom,cape-mtp/qcom,cape/qcom,mtp/moto,oneli; selected physical overlay remains unknown. Boot/USB/Power/DP may inspect exact metadata through [shared issue #10](https://github.com/Drzet/razr2022_nuc/issues/10) without downloading stock ROM again.

## Shared DT and unresolved resource contract

No Boot/shared DTS, other subsystem branches, defconfig, or upstream kernel baseline modified. Reference Motorola video DT supports MMIO 0x0aa00000 size 0xf0000, IRQ GIC SPI174, PAS9, two video GDSCs/resets, board video carveout 0x9fd00000+0x700000. Firmware source now supports **basename vpu20_4v**, but the Linux request_firmware install path/packaging and installed exact binary hash remain unverified.

**[INFERRED], not resolved by the recovered firmware:** upstream IOMMU stream IDs and DMA IOVA aperture; MXC/MMCX OPP frequencies/corner mapping; DDR interconnect topology and SM8250-derived bandwidth lookup in the provisional Iris profile; exact VPP capacity and secure buffer mapping. ELF physical PT_LOAD ranges are *not* host DMA/IOMMU evidence. SM8475 UBWC HBB16/v4 match was inferred from separate Waipio LPDDR5 source and is awaiting the GPU owner's independent review. Do not enable a VPU node on the strength of recovered binaries; retain the evidence-only [Boot-facing disabled-node contract](../vpu/2026-10-11-boot-disabled-node-contract.md) without guessed phandles or filename.

## Blockers, consumers and next test

GPU should compare measured SQE/GMU/ZAP hashes to its generic firmware, review shared UBWC profile; Boot owns shared DT and packaging, consumes v4 embedded DTB region and four candidate DTBO roots; USB/Power/DP consume per-variant metadata. All dependencies and file hashes have been posted to [issue #10](https://github.com/Drzet/razr2022_nuc/issues/10). Further offline source audit can focus on justified clock/IOMMU/ICC mapping; hold unresolved fields rather than invent a runnable profile.

Runtime authentication, firmware selection by phone, HFI negotiation, DMA setup, V4L2 registration and decode remain **phone-only tests, not performed**. Firmware-location and bounded source verification accepted; actual operational VPU support not claimed.
