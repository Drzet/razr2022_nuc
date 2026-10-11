# Oneli inherited reserved-memory audit (source-level)

Date: 2026-10-11. Boot branch inspected: `Drzet/linux` at `e664c44e48f1011b0705f42fdd63b61e69f90b9d` (source audit), upstream parent `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.

**Scope and limitations:** This compares `reserved-memory` `reg` cells from three pinned plain-text sources, stripping comments and checking static intervals. It is **not** a compiled/resolved DTB/DTBO audit, does not include possible DT header `/memreserve/`, runtime bootloader fixups, dynamic `size` allocations, other included Motorola overlays, or physical RAM boundaries. Public stock image extraction and real device overlay selection remain outstanding.

Sources:
- [Upstream `sm8450.dtsi`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/arch/arm64/boot/dts/qcom/sm8450.dtsi) for inherited regions.
- [Motorola Cape `cape-reserved-memory.dtsi`](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-reserved-memory.dtsi) for downstream active `reg` intervals.
- [Motorola oneli base `cape-moto-oneli-base.dts`](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-oneli-base.dts), also `cape-v2-moto-oneli-base.dts`, for ADSP and video relocation.
- [Boot board DTS](https://github.com/Drzet/linux/blob/e664c44e48f1011b0705f42fdd63b61e69f90b9d/arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dts).

## Explicit results

- Upstream baseline has **40** statically addressed reserved-memory nodes; Motorola's `cape-reserved-memory.dtsi` has **32** active statically addressed nodes after comment removal; oneli base replaces two regions.
- The boot branch deletes inherited `video_mem`, `adsp_mem` and `rmtfs_mem` and adds two oneli-specific regions. Effective projected static count: **39**; detected pairwise interval overlaps: **0**.
- Motorola oneli places ADSP at `0x85700000 + 0x02800000` and video at `0x9fd00000 + 0x00700000`. Inherited upstream `rmtfs_mem` at `0x9fd00000 + 0x00280000` would overlap video, so deleting it avoids that conflict; do not invent an RMTFS relocation.
- Mainline reserves XBL ramdump `0x80640000 + 0x00180000` and an adjacent `xbl_sc_mem` `0x807c0000 + 0x00040000`. Motorola instead reserves the combined `0x80640000 + 0x001c0000` as XBL ramdump. The total covered interval is the same, but purpose/ownership of the final 256 KiB differs.
- Mainline includes additional effective `oem_vm_mem` at `0xbb000000 + 0x05000000` and several virtual-machine/trusted-UI reservations with no active matching `reg` in the pinned Motorola `cape-reserved-memory.dtsi`. Some Motorola definitions have their `reg` properties commented out. They are **not verified on oneli**, but have not been removed without a live or public stock FDT audit. [INFERRED] Conservative reservation may prevent accidental use of secure memory at the expense of usable RAM.
- Mainline `memory-region` consumers found by text scan reference `slpi_mem`, `adsp_mem` and `cdsp_mem`; renamed oneli `adsp_mem` retains the label. No reference to `rmtfs_mem` was found within the examined upstream `sm8450.dtsi`. This does not establish that firmware or external drivers do not require RMTFS.
- Boot still does not enable UFS, GPU or VPU. No secure firmware startup or reserved-memory use was exercised.

## Inherited region inventory

| Mainline node/label | Base address | Size | Motorola comparison / boot disposition |
| --- | --- | --- | --- |
| `hyp_mem` | `0x80000000` | `0x600000` | Same address and size in Motorola Cape |
| `xbl_dt_log_mem` | `0x80600000` | `0x40000` | Same address and size in Motorola Cape |
| `xbl_ramdump_mem` | `0x80640000` | `0x180000` | Motorola size `0x1c0000`; mainline splits this interval |
| `xbl_sc_mem` | `0x807c0000` | `0x40000` | Not separate in Motorola; part of larger XBL ramdump interval |
| `aop_image_mem` | `0x80800000` | `0x60000` | Same address and size in Motorola Cape |
| `aop_cmd_db_mem` | `0x80860000` | `0x20000` | Same address and size in Motorola Cape |
| `aop_config_mem` | `0x80880000` | `0x20000` | Same address and size in Motorola Cape |
| `tme_crash_dump_mem` | `0x808a0000` | `0x40000` | Same address and size in Motorola Cape |
| `tme_log_mem` | `0x808e0000` | `0x4000` | Same address and size in Motorola Cape |
| `uefi_log_mem` | `0x808e4000` | `0x10000` | Same address and size in Motorola Cape |
| `smem` | `0x80900000` | `0x200000` | Same address and size in Motorola Cape |
| `cpucp_fw_mem` | `0x80b00000` | `0x100000` | Same address and size in Motorola Cape |
| `cdsp_secure_heap` | `0x80c00000` | `0x4600000` | Same address and size in Motorola Cape |
| `video_mem` | `0x85700000` | `0x700000` | Removed; oneli ADSP occupies old video region |
| `adsp_mem` | `0x85e00000` | `0x2100000` | Replaced by oneli ADSP at `0x85700000`, size `0x2800000` |
| `slpi_mem` | `0x88000000` | `0x1900000` | Same address and size in Motorola Cape |
| `cdsp_mem` | `0x89900000` | `0x2000000` | Same address and size in Motorola Cape |
| `ipa_fw_mem` | `0x8b900000` | `0x10000` | Same address and size in Motorola Cape |
| `ipa_gsi_mem` | `0x8b910000` | `0xa000` | Same address and size in Motorola Cape |
| `gpu_micro_code_mem` | `0x8b91a000` | `0x2000` | Same address and size in Motorola Cape |
| `spss_region_mem` | `0x8ba00000` | `0x180000` | Same address and size in Motorola Cape |
| `spu_tz_shared_mem` | `0x8bb80000` | `0x60000` | Same address and size in Motorola Cape |
| `spu_modem_shared_mem` | `0x8bbe0000` | `0x20000` | Same address and size in Motorola Cape |
| `mpss_mem` | `0x8bc00000` | `0x13200000` | Same address and size in Motorola Cape |
| `cvp_mem` | `0x9ee00000` | `0x700000` | Same address and size in Motorola Cape |
| `camera_mem` | `0x9f500000` | `0x800000` | Same address and size in Motorola Cape |
| `rmtfs_mem` | `0x9fd00000` | `0x280000` | Removed; conflicts with oneli video. RMTFS address unknown |
| `xbl_sc_mem2` | `0xa6e00000` | `0x40000` | Same address and size in Motorola Cape |
| `global_sync_mem` | `0xa6f00000` | `0x100000` | Same address and size in Motorola Cape |
| `oem_vm_mem` | `0xbb000000` | `0x5000000` | No active matching Motorola Cape reservation; **unverified** |
| `qheebsp_reserved_mem` | `0xe0000000` | `0x600000` | No active matching Motorola Cape reservation; **unverified** |
| `cpusys_vm_mem` | `0xe0600000` | `0x400000` | Same address and size in Motorola Cape |
| `hyp_reserved_mem` | `0xe0a00000` | `0x100000` | Same address and size in Motorola Cape |
| `trust_ui_vm_mem` | `0xe0b00000` | `0x4af3000` | No active matching Motorola Cape reservation; **unverified** |
| `trust_ui_vm_qrtr` | `0xe55f3000` | `0x9000` | No active matching Motorola Cape reservation; **unverified** |
| `trust_ui_vm_vblk0_ring` | `0xe55fc000` | `0x4000` | No active matching Motorola Cape reservation; **unverified** |
| `trust_ui_vm_swiotlb` | `0xe5600000` | `0x100000` | No active matching Motorola Cape reservation; **unverified** |
| `tz_stat_mem` | `0xe8800000` | `0x100000` | Same address and size in Motorola Cape |
| `tags_mem` | `0xe8900000` | `0x1200000` | Same address and size in Motorola Cape |
| `qtee_mem` | `0xe9b00000` | `0x500000` | Same address and size in Motorola Cape |

## Public stock-image candidate and packaging boundary

A public oneli firmware directory lists `XT2251-1_ONELI_RETEU_12_S3SLS32.16-72-14-8_subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.xml.zip` (about 3.57 GB) at [lolinet oneli RETGB firmware archive](https://mirrors-obs-1.lolinet.com/firmware/lenomola/2022/oneli/official/RETGB/). **Only the directory listing is verified**. The archive has not been downloaded, hashed or opened; its `boot.img`, `vendor_boot.img` and `dtbo.img` filenames, image-header versions, partition addresses, signatures, kernel load address and DT selection have **not** been verified. Its Android 12 branch name resembles the pinned vendor source family but does not prove binary correspondence. It is not identified as firmware installed on the unavailable handset.

When archive bytes become available, preserve the download URL, exact size and SHA-256, obtain boot partition and DTB/DTBO inventory through offline unpack tools and record their header fields, overlays and memory maps. Before packing/booting a kernel, reconcile all reserved regions and exact board revision. Do not assume an AOSP generic-boot layout for a particular phone.

## Next acceptance checks

1. Compile the oneli DTB at an exact kernel SHA and run binding validation; inspect its flattened `reserved-memory` against the above static projection, scan node references and confirm no new reservation overlap. Report inherited DT warnings separately.
2. Extract at least one **named, hashed** public stock image to compare its DTB/DTBO regions and boot headers. Any mismatch must be resolved before choosing the image format and carveouts.
3. After physical handset access is restored, inspect actual firmware ID, selected board overlay, RAM bank and bootloader memory handoff non-destructively. **No hardware or boot success claimed.**
