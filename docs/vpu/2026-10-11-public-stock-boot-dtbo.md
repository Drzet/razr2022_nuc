# Oneli Android 14 public stock boot headers and DTBO candidate identities

Recorded 2026-10-11. **Public reference evidence only; not the installed handset firmware or a bootloader-selected effective FDT.** Kernel baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.

A single full download was first verified in [hosted ZIP manifest run 38169190369](https://github.com/Drzet/razr2022_nuc/actions/runs/38169190369), followed by a second **bounded HTTP ZIP64 range verification** in [run 38170215643](https://github.com/Drzet/razr2022_nuc/actions/runs/38170215643). The latter read only required central-directory ranges and selected compressed members and reported verified individual CRC32 and SHA-256. The corrected workflow uses shell `pipefail`, avoiding the false-positive success of the initial failed ZIP64 parser run 38169976751. Exact project/source revision for the successful range check: `45244112c4a5b752d444f980bac4b02cc91b749e` (pull-request run may use an automatically created merge commit; inspect project-tested-sha.txt for actual checkout). Script `scripts/inspect-oneli-stock-ranges.py`; 26 MiB upper bound per ranged fetch, 128 MiB per expanded member.

## Verified package and selected members

- ZIP: `XT2251-1_ONELI_RETEU_14_U2SLS34.1-42-14-11_subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.xml.zip`. URL and complete reference inventory: [public stock manifest](2026-10-11-public-stock-reference-manifest.md).
- Outer ZIP size **4,353,164,507 bytes**, SHA-256 **`620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`**. Central directory: offset `4353161182`, size `3227`, **35** entries.
- `boot.img`: 100,663,296 bytes, SHA-256 `287b3b5e3c61dec6a40f2b9203942b57533df206b0ed2ef16ecdb6bbe01e305d`. Header magic `ANDROID!`, version **4**, header size **1584**, kernel size **46,854,172**, ramdisk size **1,380,093**.
- `vendor_boot.img`: 100,663,296 bytes, SHA-256 `1c27e22565f6f50919812bfcb5254cea2f3b629d98f5c26a7b54f5ece452036e`. Header magic `VNDRBOOT`, version **4**, page size **4096**.
- `dtbo.img`: 24,117,248 bytes, SHA-256 `daf02eb24af55cf4c20569db51b5bca70f0550d035846672ef3054f0c0484bd0`. DT table has 4 validated entries.
- `flashfile.xml`: 4,629 bytes, SHA-256 `052aa0ad1bbd772ef203c57fdc22bdb1e4494d8a0b4e79a234f161632745a318`; raw XML intentionally not uploaded.
- `servicefile.xml`: 4,318 bytes, SHA-256 `cf2e39f6c85ce2ae26fb7dd94c58a8287e5c05f7b793d9a48a639fb6e2980085`; raw XML intentionally not uploaded.

## Four compiled stock DTBO candidate descriptions

All four compiled DTBs passed `dtc -I dtb -O dts` return code 0 when extracted from the reference `dtbo.img`. In every case root model is **`oneli`**, root compatible list **`qcom,cape-mtp`, `qcom,cape`, `qcom,mtp`, `moto,oneli`**.

| Table index | DTB SHA-256 | Root model/compatible | eUSB compatible evidence |
| --- | --- | --- | --- |
| 0 | `10c199f0176717d93eb2e99ae7a19e2fcaf3669d96655a0b31a8feff6e4a0f19` | oneli / qcom,cape-mtp ... moto,oneli | `diodes,eusb2-repeater`, `nxp,eusb2-repeater` |
| 1 | `1adcb600d11d3d2b1e25a75fc16e8b754439f279acea2dcecf97dec7d488752b` | same | same |
| 2 | `bdfc575aa20f2ccb00e9a2414119b03ac6229af531c906ff3f3068fc995cdf28` | same | same |
| 3 | `4fd14c771ecf9f6eadd8e9e56215bcb2858beda6808ce107ae45a9ce18173aad` | same | same |

The 4 DTBO table IDs, revisions and custom fields are all zero. No `vpu20_4v` string or video firmware name was observed in the decompiled *board* DTBO candidates; the video-controller overlay may be delivered separately and/or later in the DT assembly. Absence of the string in these four DTBO fragments **does not prove absence of a VPU** or firmware in the final stock effective device tree.

**Practical implications:**
- **Boot:** strong independent stock-board evidence for `moto,oneli` root, published header v4 images and actual four public FDT variants. Need actual bootloader selection and proper Qualcomm overlay composition; do not invent live boot image arguments.
- **USB:** the vendor-repeater compatible strings are actually present in the referenced stock DTBO source, reinforcing a concrete software contract. No physical part/chip ID or oneli repeater electrical identity established.
- **GPU and Power:** FDT candidates can be analyzed for further SoC rail/OPP/GPU evidence, but this metadata tool did not extract those phandles.
- **VPU:** all signed `vpu20_4v` bytes remain inside the unextracted super/vendor image; source-level HFI hypothesis and 4-rail probe schema changes stand separately.

Evidence: [ZIP range metadata artifact](https://github.com/Drzet/razr2022_nuc/actions/runs/38170215643/artifacts/11713258439), artifact SHA-256 `9ec33e7bfa01dee313a7e8e22ee08ad62b7da0f58ad2be67cc52c76f96fb1531`. Artifact contains JSON/tool-version/log metadata only, no firmware images. Target project SHA may be a PR test-merge SHA, captured in artifact `project-tested-sha.txt` instead of assuming its PR head equals checkout commit. **Phone tests deferred.**
