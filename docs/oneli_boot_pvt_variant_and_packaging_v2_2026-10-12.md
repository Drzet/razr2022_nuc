# Boot fifth-round: PVT reference composition, packaging contract v2

Date: 2026-10-12. Boot owner; fourth coordinator review `docs/NEXT_TASKS.md` blob `9a9b9b1f9a06c4f1998677871b9d25bee496d5e5`, `docs/FOURTH_REVIEW_VPU_UPDATE.md`, `docs/GCC_PHY_CLOCK_RECLASSIFICATION.md`.

Source distinction: **public Android 14 reference, not installed handset DT**. Source archive SHA256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`. VPU's six-FDT JSON source at project `1a59d79fda42a977956de8e06c3a60d44b2971f4`; full metadata export `stock-per-fdt-property-export.json` SHA256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465` from [run 38220276125](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125). Review's independently checked symbol paths are recorded in `FOURTH_REVIEW_VPU_UPDATE.md`. No repeat ROM download was performed. No kernel changes in this round; selected Boot kernel remains `525b504b82dbca593a9a697af9be63f53915e0a3`, baseline unchanged.

## Fixed: two UNPADDED base FDTs

The original `inspect_vendor` advanced FDT position by `align(pos + totalsize, 4)` and skipped FDT #1 at a nonaligned boundary. It now advances exactly by `totalsize`, supports only recognizable optional zero-padded boundaries, rejects nonzero trailers and verifies nonempty DTB regions. Its regression constructs two 479481-byte source-format FDTs, with the second magic at offset **479481** and total region size **958962**. The test also rejects corrupt second magic.

| vendor_boot DTB | Region-relative offset | Size | MSM ID | FDT SHA256 |
| --- | ---: | ---: | --- | --- |
| Base 0 | 0 | 479481 | 530 / 65536 | `8e269672cd9d77da8575bf201c646c966219064cc0f9001bf512e7bf47455652` |
| Base 1 | 479481 | 479481 | 540 / 65536 | `b8a243a0ae0569e64dfc85bc5ee15e2eeddf65aa2f4df406c24a8467e739c843` |

The two share 3027 base nodes, root `qcom,cape`, board-id 0/0. Their compiled source identities and FDT SHA256s are **VPU extraction evidence**, not hashes recomputed by the new synthetic parser test.

## PVT variant versus BOTH base candidates

The overlay candidates have source `qcom,board-id` 0=`0x45/b1b0`, 1=`0x45/b2a0`, 2=`0x45/a100`, 3=`0x45/c000`. Reference index 3 is the **PVT candidate**, agreeing with observed phone hwrev `0xc000`. Its root `qcom,msm-id` triples include 531, 540 and 530 at revision `0x10000`; thus both embedded base IDs **530 and 540** match its declared MSM list. The physical bootloader-selected base and overlay are not known.

The [machine-readable typed symbolic matrix](../configs/oneli-pvt-symbolic-composition-v1.json) lists the same 12 source fixup relationships against **both** base IDs. Coordinator independently checked these symbol-target paths:

| PVT overlay consumer or target | Source selector | Symbolically resolved base path |
| --- | --- | --- |
| NXP @0x4f `vdd18-supply`; PS5169 @0x30 `vcc-supply` | `S10B` | `/soc/rsc@17a00000/rpmh-regulator-smpb10/regulator-pm8350-s10` |
| NXP `vdd3-supply` | `L2B` | `/soc/rsc@17a00000/rpmh-regulator-ldob2/regulator-pm8350-l2` |
| PS5169 `vio-supply` | `L8C` | `/soc/rsc@17a00000/rpmh-regulator-ldoc8/regulator-pm8350c-l8` |
| PS5169 GPIO19 enable, GPIO91 orientation; AUX GPIO2 enable / GPIO71 flip | `tlmm` | `/soc/pinctrl@f000000` |
| NXP repeater I2C overlay target | `qupv3_se5_i2c` | `/soc/i2c@994000` |
| PS5169 retimer I2C overlay target | `qupv3_se18_i2c` | `/soc/i2c@88c000` |
| Two FSA4480-disabling fragments 76 and 89 | `fsa4480` | `/soc/i2c@994000/fsa4480@42` |

In *all four* overlays, NXP @0x4f has **absent local status under an `ok` parent**, Diodes @0x6c is explicitly disabled, PS5169 @0x30 has status `ok`, and two base FSA4480-targeted fragments explicitly disable it. The PVT AUX GPIO2 and GPIO71 remain a distinct circuit from the PS5169 Type-C retimer. The NXP reset-gpio local raw cells `<7 7 0>` are **not** mapped to TLMM without typed local-fixup evidence. PS5169 vendor `redriver,enable-gpio` names GPIO19 but this is **not** a proven upstream reset pulse contract.

**Unique non-PVT data:** overlay index 2 (`0x45/a100`) adds PM8010 i/j and `gpio-regulator@0` fragments. These are NOT transferred to index 3. Symbols establish source dependency destinations; they do not establish parent rail voltage, electrical wiring, active Linux driver support or physical chip identity.

**Exactly what has and has not been applied:** both base candidates and PVT index 3 are **symbolically compatible and their external fixup paths are resolved** in the JSON report. No original FDT binary payload was retained in the shared metadata-only export. Therefore neither `libfdt`/`fdtoverlay` application nor post-relocation numeric phandle/status verification was performed. A filtered property JSON projection cannot reconstruct original source DTB bytes. If exact original source members become available from an already authorized workspace, validate `sha256sum` for each base and overlay, run `fdtoverlay -i base.dtb -o composed.dtb pvt-3.dtbo` separately for both, parse root/probe/supply statuses, record return code and hashes, and compare results to symbolic expectations. Do **not** label the current JSON matrix a physically applied/reference-bootloader selected tree.

## Packaging v2: reference versus chosen native inputs

[Machine-readable contract v2](../configs/oneli-boot-packaging-v2.json) replaces v1 for new Userspace consumers. `vendor_boot` v4 reference: page 4096, header 2128, kernel addr `0x8000`, ramdisk addr `0x1000000`, tags addr `0x100`, DTB addr `0x1f00000`. It embeds the two FDTs above, and legacy-LZ4 vendor ramdisk magic `02214c18`, one type-1 fragment and 85-byte bootconfig. Stock `boot.img` raw OS-version, stock fragment name, native kernel-placement and AVB policy remain **UNRESOLVED**, not filled with copied Android defaults.

The [prototype](../scripts/oneli_boot_v4_layout.py) now requires `--header-inputs explicit-header-values.json`: `os_version_raw`, `kernel_addr`, `ramdisk_addr`, `tags_addr`, `dtb_addr`, `purpose` (structural-only or reviewed-native), and `phone_boot_validated=false`. Missing/null/noninteger values are rejected. It explicitly overwrites these header fields instead of silently copying the stock OS version/addresses from templates. Example structural-only deliberate values (NOT native placement approval):

```json
{"purpose":"structural-only","phone_boot_validated":false,"os_version_raw":0,
 "kernel_addr":32768,"ramdisk_addr":16777216,"tags_addr":256,"dtb_addr":32505856}
```

The caller must also supply fresh Image/initramfs/DTB/vendor ramdisk/bootconfig and explicit name/cmdlines. The output remains `UNSIGNED`. The v2 manifest reports independent structural validation separately from `native_ready=false` and `hardware_accepted=false`, without a misleading generic `verified` flag. Userspace `oneli_native` may consume this as reference-format evidence; QEMU virt must not use the Motorola DTB or Android addresses.

## Completed tests and remaining gates

- `scripts/oneli_boot_v4_layout.py`: parser and explicit-header commit `a64d3489a72b78d053ac174295a5246eecd385c9`; improved regressions `26aae5f979f4a91a62119da3e4ea199213076cad` and `78aa7b8a67aa3d79d3cc027f3eed820e4e9fb114`.
- **Six tests PASS** in [run 38280888156](https://github.com/Drzet/razr2022_nuc/actions/runs/38280888156), exact project checkout `bdf6512626ba261f1e17c546acd864c2a24e973d`, including *independent* AOSP-derived `mkbootimg.py`/`unpack_bootimg.py` at public source commit `ntherning/mkbootimg@7209a7164f1772db43f92928012c86a00f6202ff`. Cross-check unpacks the generated candidates, verifies kernel/initramfs/DTB/vendor ramdisk/bootconfig payload SHA256 identity and compares separately repacked changed-size (+page-boundary) AOSP-v4 image section sizes, hashes and vendor addresses. [Artifact 11760448988](https://github.com/Drzet/razr2022_nuc/actions/runs/38280888156/artifacts/11760448988), ZIP digest `2808667179568e9dc527e0695df57590778970c48cc1d95a48a19b2d1bb5137a`.
- Machine-readable PVT matrix commit `f8fc89a86ba280df09e721613e6cfc820775598b`, packaging v2 commit `518cb6d59abdbd1dcd976ec23b55252504b9db40`. Its metadata-only consistency regression tests are separately added after that pass; consult latest exact CI job for their status.
- Corrected old CI provenance: all-applicable board schema pass [38182280401](https://github.com/Drzet/linux/actions/runs/38182280401) used kernel checkout **`2b473619...`**. Boot head `525b504...` changes only the separate FDT workflow pin, passed [38182283694](https://github.com/Drzet/linux/actions/runs/38182283694). These results are static board compilations, not native boot.
- Seven GCC→disabled PHY parent references were reclassified by coordinator source review: no proven UART7/initramfs blocker. GCC/CCF registration supports unresolved selected parents/orphan retry. UFS symbol clocks are needed later for internal storage; USB3 PIPE for SuperSpeed; PCIe clocks for links. Review device-links when touching these consumers, log selected mux states on hardware later. No need to enable PHYs to silence static warnings.

**Outstanding physical-only:** reference bootloader base/overlay selection, native image load addresses, unlocked hardware boot/UART, GPU/VPU secure firmware authentication, peripheral operation. **Outstanding offline if original bytes obtainable:** real stock image roundtrip and real libfdt composition of each original base+PVT overlay. Neither has been claimed from compact JSON. No firmware downloads, kernel baseline changes or other subsystem branch modifications in this Boot round.
