# VPU sixth-round bounded resource and loader translation decision

**2026-10-12.** Coordinator inputs: main `FIFTH_REVIEW.md` blob `2926da8ee4709e434f78a0d038b95ecee9c586ff`, `NEXT_TASKS.md` blob `d10cffa04f333ee456ef29501921aa4cbb323ae9`. Kernel upstream baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. VPU draft kernel `Drzet/linux:razr/vpu` (functional build-tested source `7f1d729b6f458f1e76efe2894eb3c544bc9db856`; comment-only later head `869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf`). The VPU RFC remains experimental and **excluded from Boot's delegated first minimal integration candidate**.

## Immutable evidence closure, not another full ROM scan

- **Archived full approved six-FDT JSON** [compressed in git](evidence/stock-six-fdt-full-properties.json.gz): gunzip yields **15,862,099 bytes** SHA256 **`1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`**. Preserved from independently reviewed [CI artifact 11734430639](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125/artifacts/11734430639) after verifying original artifact ZIP and uncompressed JSON SHA-256. Contains complete **previously filtered** export, not reconstructable original six DTB binaries. No proprietary DTBs or ROM in repository.
- **Focused missing-property JSON** [in git](evidence/focused-stock-properties.json), **803,197 bytes**, SHA256 **`f1bb6f41036aeb2e04ac289cfa803aab686cf92097a77444c9ed50c96397fe48`**. SHA-checked ZIP64 HTTP Range retrieved **only** `dtbo.img`, `vendor_boot.img`, `boot.img` from the previously full-SHA-verified public Motorola Android14 stock ZIP `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`. [CI 38291543595 PASS](https://github.com/Drzet/razr2022_nuc/actions/runs/38291543595), artifact 11766556493 digest SHA256 `189b13e4ed75d2e1d148017993b48b7334865571f51bd43786b6099a0d3b0e60`, source script [export-oneli-focused-stock-gaps.py](../../scripts/export-oneli-focused-stock-gaps.py). Records exact FDT source offsets/hashes, every property on 156 selected GPU/GMU/video/GDSC/RPMh/interconnect-provider nodes **per base**, complete raw/cells/length/SHA for each requested field, and each DTBO variant's `fragment@48`. 156-node sets for MSM530 and MSM540 are **byte-property identical**, but entire source FDTs differ in other fields.
- **Boot header** from checked `boot.img` SHA256 `287b3b5e3c61dec6a40f2b9203942b57533df206b0ed2ef16ecdb6bbe01e305d`: boot v4, 1,584-byte header, `os_version_packed=402653593`, four reserved header u32 **all zero**, empty v4 cmdline, kernel 46,854,172 bytes SHA256 `70664573fb75d3c57140f58dcf4f2777d5d7f5ca9123ce3e13685bc7df65ea0b`, ramdisk 1,380,093 bytes SHA256 `ad24b08320481911855ce1a0eea5d328763d29054132b62256fa2a2d4db6bc3a`, v4 boot signature 4,096 bytes SHA256 `030600e25f969311812014a82fcb3edf10871be255cb59b74452d1e8926cf869`. The signature hash is a source fact **not** verification, boot addresses are in vendor_boot and require Boot's explicit packaging v2 inputs. Do not interpret these as bootloader acceptance.
- **PVT fragment 48 resolution (Power):** in each of four stock DTBOs, `/fragment@48/__overlay__` has **exactly one source property `regulator-boot-on`**, zero-length Boolean. Its `/fragment@48/target` is unresolved overlay placeholder `<0xffffffff>`; Boot's separately typed symbolic composition resolves target to L8C. **No voltage constraint or electrical parent is specified by this fragment**. Previous export's empty selected dictionary was caused by filtering, not source absence.

## Exact GPU/GMU vote evidence (both base FDTs)

At `/soc/qcom,kgsl-3d0@3d00000`, source `qcom,bus-table-ddr` has **12 u32 numbers**, the indexed stock-table sequence: `[0,781250,1761718,2136718,2660156,3000000,6074218,6671875,8171875,10687500,12484375,13085937]`; `qcom,bus-table-cnoc=[0,100]`. `qcom,ubwc-mode=4`, `qcom,min-access-length=32`, `qcom,initial-pwrlevel=11`, `qcom,chipid=117637122`. These are vendor-formatted table **raw u32 values**, not automatically `icc_set_bw` kB/s or mainline OPP corners. The 13 indexed power levels, each containing real `qcom,gpu-freq`, `qcom,level`, `qcom,cx-level`, `qcom,bus-freq`, `qcom,bus-min`, `qcom,bus-max`, `qcom,acd-level`, are in the full committed focused JSON.

| Vendor level index | GPU MHz | CX level (raw) | GX level (raw) | Bus index (raw) |
| --- | ---: | ---: | ---: | ---: |
| 0 | 900 | 416 | 416 | 11 |
| 1 | 862 | 384 | 384 | 11 |
| 2 | 815 | 320 | 320 | 11 |
| 3 | 765 | 256 | 256 | 10 |
| 4 | 710 | 256 | 224 | 10 |
| 5 | 645 | 192 | 192 | 8 |
| 6 | 580 | 192 | 144 | 8 |
| 7 | 515 | 128 | 128 | 6 |
| 8 | 439 | 128 | 96 | 6 |
| 9 | 364 | 128 | 80 | 3 |
| 10 | 324 | 64 | 64 | 2 |
| 11 | 285 | 64 | 56 | 2 |
| 12 | 220 | 64 | 48 | 2 |

Original per-index bus minima/maxima and ACD IDs are in JSON. `/soc/qcom,gmu@3d69000` has exact `iommus=<546 5 1024>` with mainline-translation caveat, and `qcom,iommu-dma="disabled"`, two IRQs and seven named clocks. This closes GPU's **missing source properties**, but dynamic CX vote/GMU expectation and vendor bus index translation are GPU-owned, and are **not** established by vendor arrays alone. Do not inject these integers into upstream RPMh/ICC tables.

## VPU IOMMU: second-cell semantics decided, two-domain port HELD

Pinned `Drzet/linux:razr/vpu` `drivers/iommu/arm/arm-smmu/arm-smmu.c::arm_smmu_of_xlate`: with `#iommu-cells=2`, first cell is SMR ID, **second is stream-match mask** via `FIELD_PREP(ARM_SMMU_SMR_MASK, args->args[1])`. Therefore stock nonsecure pairs `<93 0x2180 0x400>` and `<93 0x2187 0x400>` have SID 0x2180/0x2187 with a **0x400 SMR mask**, not a vendor security flag, offset, OPP level or IOVA address. A mask bit denotes a don't-care bit for stream matching, **not** `dma_mask`.

Crucial pinned `arm_smmu_attach_dev` calls `arm_smmu_master_install_s2crs(cfg, S2CR_TYPE_TRANS, smmu_domain->cfg.cbndx, fwspec)`, which installs *all* IOMMU specifiers belonging to this Linux device into **the same context-bank/domain**. Thus two upstream `iommus` entries are **expressible as stream-match rules**, but **do not reproduce the vendor's two separate nonsecure bitstream and pixel translation domains**. Stock IOVA pools: bitstream `0x25800000..0xe0000000` and pixel `0x00100000..0xe0000000`. Proposed Iris host `dma_mask=0xdfffffff` is a supported *upper bound only*. **Decision:** no guessed consumer with dual contexts on one upstream device; require source-backed dedicated child devices/aux-domains and matching Iris allocator ownership or proved single-domain equivalence with actual address constraints. This does not block a disabled-peripheral minimal kernel.

## Clocks, GDSCs, OPPs: one clock question narrowed, power mapping HELD

Stock VPU raw four clock handles correspond to GCC VIDEO_AXI0, VIDEOCC MVS0C, MVS0 and `VIDEO_CC_MVS0_CLK_SRC`. Pinned `drivers/clk/qcom/videocc-sm8450.c` proves `video_cc_mvs0_clk` branch -> `video_cc_mvs0_div_clk_src` -> `video_cc_mvs0_clk_src` PLL, with `CLK_SET_RATE_PARENT` on branch/divider/source. **Decision:** fourth clock is an *upstream source/ancestor in the common clock tree* and an explicit fourth consumer clock gate is not intrinsically required by source-level topology. Exact required fourth-vendor-clock sequencing still untested. Compare vendor allowed rates 239,999,999/338,000,000/366,000,000/444,000,000 against source PLL frequencies 720/1014/1098/1332 MHz: dividing by **3** would produce 240/338/366/444 MHz. Divider 3 is **[INFERRED]**, since the RO divider's actual phone register was not read. Do not program or assume fixed divisor by fiat.

GDSC source has `video_cc_mvs0_gdsc` parent `mvs0c_gdsc`, matching two upstream `venus,vcodec0` *roles* but not enough to construct the additional RPMh required-opps `mxc,mmcx` provider/order and corner cells. Vendor `qcom,allowed-clock-rates` only supplies frequencies; it does **not** encode each matched MXC/MMCX vote. **Decision:** keep VPU 4-domain OPP DT and dynamic frequency policy disabled pending a verified regulator/clock/required-OPP translation. Do not manufacture `required-opps` rows from the four rates.

## ICC: three route requirements confirmed; translation HELD

Stock controller has **three interconnect paths**, not the two in provisional `sm8475_data`: `venus-cnoc`, `venus-ddr`, `venus-llcc`. The original arrays and source phandle/provider paths are in the six-FDT manifest and focused JSON. Vendor `qcom,bus-range-kbps=<1000 1000, 1000 15000000, 1000 15000000>` gives CNOC min/max 1000/1000 and DDR and LLCC 1000/15000000. These are **per-vendor-request bounds**, not calibrated real decoder bandwidth.

Pinned `drivers/media/platform/qcom/iris/iris_resources.c::iris_set_icc_bw` clamps/bulk-votes **only** entry named `video-mem`; adding `video-llcc` to `icc_tbl` would only initialize its minimum and leave it **unscaled when video bandwidth changes**. The vendor providers use their own raw endpoint number spaces, not automatically the `include/dt-bindings/interconnect/qcom,sm8450.h` namespace. **Decision:** a three-path DT alone is insufficient. Need typed route mapping against upstream `sm8450.c` provider topology and source-grounded LLCC-vs-DDR average/peak aggregation policy; no guessed third vote or direct reuse of SM8250 decoder BW table. Minimal integration does not depend on Iris.

## Qualified oneli Qualcomm firmware loader replay

Real `NON-HLOS.bin` is preserved as **hash-only source evidence** (see [radio manifest](2026-10-11-radio-non-hlos-firmware-manifest.json)). Controlled `radio.img` HTTP range (not 4.35GB ZIP), exact radio/non-HLOS/ext4 SHA validation, `debugfs` extraction of **only** `vpu20_4v.mbn`, `vpu20_4v.mdt`, `a730_zap.mdt` and the needed load split segments; no published signed payload. [Source checker](../../scripts/check-oneli-mdt-loader-bounds.py) and [machine output](evidence/qualified-mdt-loader-bounds.json); corrected [CI 38292192600 PASS](https://github.com/Drzet/razr2022_nuc/actions/runs/38292192600).

Pinned `drivers/soc/qcom/mdt_loader.c` rules reproduced: all PT_LOAD except QCOM_MDT_TYPE_HASH, ignore memsz=0, align maximum physical segment end to 4KiB, split iff **any nonzero ELF phdr** lies outside firmware file, segment lookup via *original program header index* in `b%02d`. **Important correction of first audit:** the Qualcomm hash program header can be `PT_NULL` carrying `p_flags & TYPE_MASK == TYPE_HASH`; `qcom_mdt_read_metadata` tests flags on *any* phdr after index 0. The corrected check now requires a recognised hash descriptor for each file.

| Source | Actual ELF32 phdrs | Required load segments | Hash metadata | `qcom_mdt_get_size` |
| --- | ---: | --- | --- | ---: |
| `vpu20_4v.mbn` | 20 | 10 load segments **inside MBN**; self-contained | index19, 4712 bytes *in MBN* | **0x700000** |
| `vpu20_4v.mdt` | 20 | `.b01`–`.b09`, `.b18` all exact-sized and source-hashed | index19, 4712 bytes **packed in MDT** | **0x700000** |
| `a730_zap.mdt` | 3 | `.b01` 2236 bytes, exact size/hash | index2, 3896 bytes **packed in MDT** | **0x1000** |

All three have relocatable host ELF flags (BIT27) and fit the **stock** 7MiB VPU / 8KiB ZAP carved regions by size. Split `.b00` and hash companion `.b19` (and ZAP `.b00/.b02`) exist in stock package but are **not additional load-segment file requests by this pinned kernel MDT path**, because metadata resides in MDT. Other Android/vendor secure-loader choices could differ; this is a **host structural finding**, not cryptographic verification. Proposed future Debian single-file firmware path `/lib/firmware/qcom/vpu/vpu20_4v.mbn` plus DT `firmware-name = "qcom/vpu/vpu20_4v.mbn"` remains **packaging proposal only**, not enabled driver contract or secure acceptance. Gen2 packet ABI remains [INFERRED].

## Integration / consumers

Boot owns disabled board DT and the independent combined candidate; do **not** merge any Iris ancestor or block its Image/modules/QEMU contract on the above. GPU consumes recovered vote table and ZAP segment bounds; Power consumes fragment48 exact Boolean and regulator identities; Boot consumes explicit boot header/section hashes. Source property values come from **uncomposed public reference**; not a captured runtime FDT. Both project workflows for bounded previous FDT extraction are manual-only after successful runs. Pending hardware PAS9/HFI/decode, effective DT selection, DRAM HBB and physically correct power/IOVA policy remain separate gates.
