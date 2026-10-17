# Boot v4 reference layout and bounded image-repack contract

Date: 2026-10-11. Boot owner. **Reference extraction, not an installed handset flash dump.** Input is the source-hashed public Motorola Android 14 stock package for XT2251-1 `U2SLS34.1-42-14-11`. VPU verified the archive/package members, while Boot interprets their AOSP v4 layout. No native boot or flashed image in this work.

## Provenance and source contract

Public archive SHA256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`, 4,353,164,507 bytes. VPU controlled extraction: [fourth-round handoff](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/handoffs/2026-10-11-vpu-fourth-round.md), [machine-readable super/vb metadata](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/vpu/2026-10-11-stock-filesystem-firmware-manifest.json), [radio manifest](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/vpu/2026-10-11-radio-non-hlos-firmware-manifest.json). Source boot structure definitions: Android Open Source Project `system/tools/mkbootimg/include/bootimg/bootimg.h` (Android boot/vendor_boot v4). Motorola source tree: `MotorolaMobilityLLC/kernel-devicetree@90fa7be1db5bd47202673d4431408659149a7359`.

- `boot.img` SHA256 `287b3b5e3c61dec6a40f2b9203942b57533df206b0ed2ef16ecdb6bbe01e305d`, partition-member bytes 100,663,296, magic `ANDROID!`, v4 header **1584 bytes** and fixed **4096-byte** flash-section alignment; kernel payload **46,854,172** bytes, ramdisk **1,380,093** bytes. Header starts offset 0; kernel starts offset **4096**. `boot.img` signature size, payload compression, selected ramdisk contents/command line, OS version raw field, and real bootloader validation remain unparsed/unproven here.
- `vendor_boot.img` SHA256 `1c27e22565f6f50919812bfcb5254cea2f3b629d98f5c26a7b54f5ece452036e`, 100,663,296 bytes, magic `VNDRBOOT`, header **v4 / 2128 bytes**, page size **4096**. Section positions derived by AOSP `align(size, page)`, independently supported by VPU's metadata:
  
  | Section | Byte offset | Exact payload bytes | Provenance |
  | --- | ---: | ---: | --- |
  | Header | 0 | 2128 | v4 header metadata |
  | Vendor ramdisk | 4096 | 13,335,589 | VPU extracted header |
  | DTB region | 13,340,672 | 958,962 | SHA256 `88b605e746f829545f3a5ceabc8ac669eee803db1397d32cc7f49ec91fbba71e` |
  | Vendor ramdisk table | 14,303,232 | 108 | **one** entry, 108 bytes |
  | Bootconfig | 14,307,328 | 85 | three reported keys |

  Vendor ramdisk table type **1** (platform), all sixteen `board_id` words **zero** in the identified record. Fields `kernel_addr`, `ramdisk_addr`, `dtb_addr`, `tags_addr`, ramdisk fragment name, compression magic and DTB-region concatenation count not yet published. Bootconfig reported *keys*, not values: `androidboot.hardware`, `androidboot.memcg`, `androidboot.usbcontroller`.
- `dtbo.img` SHA256 `daf02eb24af55cf4c20569db51b5bca70f0550d035846672ef3054f0c0484bd0`, Android DT table v0. Four FDT hashes in index order:
  0. `10c199f0176717d93eb2e99ae7a19e2fcaf3669d96655a0b31a8feff6e4a0f19`
  1. `1adcb600d11d3d2b1e25a75fc16e8b754439f279acea2dcecf97dec7d488752b`
  2. `bdfc575aa20f2ccb00e9a2414119b03ac6229af531c906ff3f3068fc995cdf28`
  3. `4fd14c771ecf9f6eadd8e9e56215bcb2858beda6808ce107ae45a9ce18173aad`

  Every *table entry* reports `id=rev=custom=0`, root model `oneli`, compatible `qcom,cape-mtp/qcom,cape/qcom,mtp/moto,oneli`. **Not available yet:** numeric root `qcom,board-id`, `qcom,msm-id` for all four, variant property diff, embedded vendor_boot base DTBs and Qualcomm bootloader's effective chosen overlay. Motorola source oneli PVT overlay `<0x45 0xC000>` agrees with actual stock ADB hwrev `0xC000`, but is not evidence that any one of the table entries was applied. [Targeted shared request](https://github.com/Drzet/razr2022_nuc/issues/10) asks VPU to export source-hashed data in its controlled extraction job. **Effective DT composition is held** until base/overlay inputs and selection facts are available.

## Signed firmware observation and scope

VPU located `image/vpu20_4v.mbn` and `.mdt/.bXX` split segments in the public `radio.img → SINGLE_N_LONELY → NON-HLOS.bin → Android sparse ext4` chain. The `vpu20_4v.mbn` SHA256 is `9582ea4c5565408bd3e5ba6f8fffc7881f226cae001b6fcd7a0c868de9add9af`, video-firmware version `video-firmware.2.4-33580ad5a949b4d45b3b008988280e60573cd894`, 18 ELF32 PT_LOAD descriptions spanning declared physical load addresses `0x0f500000..0x0fbff020`. **Those ELF virtual/physical link addresses are neither a Linux memory-reservation prescription nor host IOMMU range**. Source proves a signed-image candidate exists; PAS9 authentication and HFI remain untested, so Boot is explicitly **not** adding an enabled VPU node.

## Reproducible no-flash prototype and Userspace interface

Source script [`scripts/oneli_boot_v4_layout.py`](../scripts/oneli_boot_v4_layout.py), machine-readable [`configs/oneli-boot-packaging-v1.json`](../configs/oneli-boot-packaging-v1.json), tests [`tests/test_oneli_boot_v4_layout.py`](../tests/test_oneli_boot_v4_layout.py).

```bash
# Inspect actual stock reference members *only when VPU supplies them*:
python3 scripts/oneli_boot_v4_layout.py inspect boot.img vendor_boot.img
python3 scripts/oneli_boot_v4_layout.py roundtrip boot.img vendor_boot.img

# No stock Android ramdisk/bootconfig is reused without deliberate selection.
# An UNSIGNED candidate needs fresh explicit inputs and a reviewed ramdisk
# descriptor containing {name, type, board_id:[16 explicit unsigned words]}:
python3 scripts/oneli_boot_v4_layout.py prototype boot.img vendor_boot.img \
  --kernel Image --initramfs initramfs.img --dtb sm8475-motorola-oneli.dtb \
  --vendor-ramdisk purpose-built-vendor-ramdisk.cpio.gz \
  --bootconfig native-bootconfig.txt --ramdisk-descriptor ramdisk-entry.json \
  --cmdline 'console=ttyMSM0' --vendor-cmdline 'reviewed-vendor-args' \
  --vendor-name 'oneli' --out-dir candidate-layout
```

**The command above is interface syntax only; its example arguments are not justified bootloader command-line values.** The prototype retains selected template header addresses and outputs `boot-candidate.UNSIGNED.img`, `vendor_boot-candidate.UNSIGNED.img` and parsed layout JSON. No AVB signing, bootloader validation, hardware-specific memory loading policy or flash operation exists in the tool. Userspace must supply the new initramfs and exact matching kernel/modules/firmware hashes, and Boot must approve the actual board DTB/selection. Never silently substitute stock vendor ramdisk/bootconfig.

The synthetic v4 fixture test covers successful **byte-identical structural identity** repack, correct v4 section offsets, generated *new* unsigned candidate sections, validation failure for corrupted ramdisk-table entry size and the actual VPU-report `vendor_boot` offset equations. This demonstrates code behavior **on synthetic inputs only**. A structural roundtrip of the *actual 100MB public stock boot/vendor_boot binaries* is not claimed: VPU's extraction and source-hashed firmware inventory are complete, but the public metadata-only artifacts do not contain those two member payloads. No re-download or repeat firmware extraction is required for this layout/contract audit; this particular byte-level test can only be marked unverified without input bytes.

## Outstanding boot prerequisites

1. Decode/publish the four DTBOs' numeric root board/MSM IDs, per-variant resource differences and embedded vendor_boot DTB FDT inventory **if derivable from existing extracted metadata**; they are not provided in the durable published manifests. No offline effective FDT composition before evidence.
2. Actual image header strings, compression signatures and binary image identity roundtrip require the respective stock image payload bytes, **not another general VPU extraction**. Current metadata-level assessment and synthetic roundtrip are complete; the real byte-level test is explicitly unverified.
3. Select a correct oneli first-stage DT/kernel placement, explicit initramfs/bootconfig, non-Android Userspace contract and AVB/unlocked-bootloader test path; these are **not** inferred from knowing v4 header version.
4. Physical device once available: validate bootloader acceptance and UART, UFS and other bring-up independently.

Do not publish extracted signed blobs or image binaries into Git.
