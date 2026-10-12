> **Superseded firmware-location status (2026-10-12):** SQE, GMU and oneli split ZAP are now **located and SHA256-inventoried**. This 2026-10-11 record is historical. See the [current GPU six-FDT + firmware audit](gpu_stock_fdt_firmware_vote_review_2026-10-12.md) and VPU's radio/vendor source manifests. Do **not** use its 'ZAP unknown' statement as a current blocker.

# GPU consumption of the shared oneli Android 14 firmware manifest

Recorded 2026-10-11; input from the **VPU-owned** stock extraction workflow, not a second GPU-side download. Target physical stock observation: XT2251-1 PVT, SKU dn, hwrev 0xC000, `motorola/oneli_ge/oneli:14/U2SLS34.1-42-14-11/e37c37-31202:user/release-keys`. No new physical test and no verified installed partition contents.

## Exact public reference input

- VPU [acquired archive manifest](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/vpu/2026-10-11-public-stock-reference-manifest.md): ZIP `XT2251-1_ONELI_RETEU_14_U2SLS34.1-42-14-11_subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.xml.zip`, **4,353,164,507 bytes**, SHA256 **`620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`**; original public URL at [Lolinet](https://mirrors-obs-1.lolinet.com/firmware/lenomola/2022/oneli/official/RETGB/XT2251-1_ONELI_RETEU_14_U2SLS34.1-42-14-11_subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.xml.zip).
- VPU acquisition [run 38169190369](https://github.com/Drzet/razr2022_nuc/actions/runs/38169190369); [range-verified metadata run 38170215643](https://github.com/Drzet/razr2022_nuc/actions/runs/38170215643). Outer ZIP has 35 entries, including 16 `super.img_sparsechunk.*` members, `radio.img`, `boot.img`, `vendor_boot.img`, `dtbo.img`. These describe **container names**, not an inspected mounted firmware filesystem.
- The public reference matches the phone's observed **build label**, but its exact retail region, partition bytes, active slot content and ZAP secure-world key acceptance remain unverified. The archive was deleted after the Actions job; not a retained binary workspace. VPU owns controlled reacquisition and image-format-aware extraction.

## Required native-GPU firmware comparison matrix

| GPU subsystem | Generic mainline expected path / source-reported version | Motorola source reference | Current **public reference** observation | Next evidence |
|---|---|---|---|---|
| SQE microcode | `qcom/a730_sqe.fw`, linux-firmware WHENCE reports **v1.81** (pinned WHENCE revision `81a99dba039a21fd83d37a67a7de0fb80152e065`) | Motorola Gen7-4-0 catalog names `a730_sqe.fw` | Not found as a direct outer ZIP member; inner filesystems not yet inspected. No stock version or SHA256 known | Exact inner image, file path, size, SHA256, optional firmware-embedded version/ELF note; compare **bytes/version** with independently pinned linux-firmware asset |
| GMU firmware | `qcom/gmu_gen70000.bin`, pinned WHENCE reports **v4.00.07** | Motorola catalog names `gmu_gen70000.bin` and alternate `c500_gmu.bin` | No actual oneli GMU binary or QC version inspected; no direct outer ZIP match is insufficient for negative claim | Full image/member provenance, SHA256, firmware version; determine whether the normal GMU path or vendor fallback is used on stock. Never silently substitute `c500_gmu.bin` |
| Device-signed ZAP shader | Generic A730 catalog fallback `qcom/a730_zap.mdt` (can be overridden with DT `zap-shader/firmware-name`) | Vendor base `a730_zap`; image may use split MDT + numbered Bxx payloads, MBN or another signed format | No oneli-specific signed image, segment list, signature metadata, path or SHA256 located | Scan **all actual** partition/image formats, including radio and unpacked logical/vendor/odm filesystems, for matching names and split companions; preserve exact signed container bytes, metadata, load ranges and role |
| On-device firmware authorization | SCM secure loader + GMU HFI interface | Vendor device boot and firmware supply chain | No native GPU, firmware load, SCM authorization or Mesa work performed | Unlocked oneli tests only after signed-image identity and kernel DT/GMU power contract established |

Generic firmware names and generic linux-firmware versions are **not evidence** that the public stock archive or connected handset contain identical binaries. A signed ZAP's file existence and signature parsing cannot prove its authentication on locked/secured retail hardware.

## Ownership and acceptance handoff

GPU requests in the shared [inventory issue #10](https://github.com/Drzet/razr2022_nuc/issues/10): for SQE, GMU and ZAP record **source archive SHA, partition container/member, extracted path, exact size, SHA256, format, signature/MDT segment metadata (if parsable), firmware version string and extraction tool versions**; publish negative filesystem search coverage if absent. Do not reconstruct Android sparse chunks by concatenating byte streams and do not infer location in super before inspecting format. VPU controls any new download; GPU consumes the machine-readable manifest.

**Current result:** the generic SQE/GMU filenames agree between mainline and Motorola source; versions can only be compared on the **generic** side. Public stock versions and secure ZAP location remain unknown; therefore no binary equivalence, HFI compatibility or signed ZAP acceptance is claimed. Keep GPU disabled.
