# Motorola oneli Android 14 public reference: acquired archive and member manifest

Date 2026-10-11. **Actual hosted acquisition succeeded** in [GitHub Actions run 38169190369](https://github.com/Drzet/razr2022_nuc/actions/runs/38169190369), coordinator project PR revision `bc866d33eabb8cc82d1e9f575907536e1ed9e34d`. Download input was the previously identified public RETGB/RETEU package, **not the inaccessible handset's installed ROM**.

Reference URL: https://mirrors-obs-1.lolinet.com/firmware/lenomola/2022/oneli/official/RETGB/XT2251-1_ONELI_RETEU_14_U2SLS34.1-42-14-11_subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.xml.zip

| Evidence | Verified value |
| --- | --- |
| Reference package | XT2251-1_ONELI_RETEU_14_U2SLS34.1-42-14-11_subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.xml.zip |
| Android build identifier | U2SLS34.1-42-14-11 |
| Exact bytes | 4,353,164,507 |
| Full ZIP SHA-256 | `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c` |
| HTTP | 200, application/zip, server IP 178.63.27.77 |
| Curl version | 8.5.0 |
| Download duration | 106.684601 s |
| Stock DTBO SHA-256 | `daf02eb24af55cf4c20569db51b5bca70f0550d035846672ef3054f0c0484bd0` |
| DTBO length | 24,117,248 bytes (Android DT table header declares 913,898 bytes) |
| DTBO candidate count | 4; table version 0; entry size 32; page size 4096 |

## Android DTBO candidate table, without interpretation

| Index | DT size | DT offset | ID | Revision |
| --- | ---: | ---: | ---: | ---: |
| 0 | 227,694 | 160 | 0 | 0 |
| 1 | 227,761 | 227,854 | 0 | 0 |
| 2 | 230,522 | 455,615 | 0 | 0 |
| 3 | 227,761 | 686,137 | 0 | 0 |

The table's custom fields are all zero, too. **These generic IDs do not identify which overlay the retail oneli bootloader selects.** Actual FDT contents and effective on-device overlay still need inspection. The hardened metadata parser validates that all entries fit in the declared table.

## Container names and ZIP evidence

- Direct files: recovery.img, vendor_boot.img, vbmeta_system.img, gpt.bin, boot.img, dspso.bin, BTFM.bin, vbmeta.img, radio.img, dtbo.img, logo.bin, bootloader.img.
- Logical partition container: sixteen members `super.img_sparsechunk.0` through `super.img_sparsechunk.15`, with per-entry CRC32, compressed/uncompressed sizes and exact names stored in the JSON inventory.
- Flash scripts/identification: flashfile.xml, servicefile.xml, signing-info.txt, ONELI_G_U2SLS34.1-42-14-11_subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.info.txt, cid_template.dat and two empty ancillary entries.
- Crucial boundary: the ZIP contains no direct `vpu20_4v*` or signed A730 ZAP binary. They **may** reside inside the sparse super partitions. Their presence and hashes are not established by the outer ZIP manifest.
- [Metadata-only archived manifest](https://github.com/Drzet/razr2022_nuc/actions/runs/38169190369/artifacts/11713052615): archived artifact SHA-256 `9a3c10f5fe004530852e6db27c0a3b3bf5a86b456c89eba4cfd182f7c6fe9f3c`. This 4-KiB ZIP contains approximately 12-KiB plain-text metadata, **no proprietary firmware**.

## Shared downstream consumers

- **Boot:** use the exact candidate package hash and DTBO table for a subsequent DTB/overlay selection audit. The boot and vendor_boot images are definitely present, but their headers have not yet been parsed.
- **GPU:** use this *same* acquired ZIP reference to inspect SQE/GMU/ZAP metadata from the vendor image, rather than a separate multi-GB download. No ZAP hash yet.
- **Power:** board-revision/PMIC and rail metadata can only be inferred from public overlays until source-specific DTBO contents and actual hardware revision are verified.
- **VPU:** Motorola firmware version and VPU Gen2 binary compatibility are still unknown until the vendor partition's exact signed `vpu20_4v` image is identified.

[Cross-subsystem issue #10](https://github.com/Drzet/razr2022_nuc/issues/10) provides durable notification to all owners.

The downloaded 4.35-GB archive was deleted on the CI runner before the job finished. No stock binaries were committed or published.
