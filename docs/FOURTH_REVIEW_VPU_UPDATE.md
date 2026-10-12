# Fourth-review update after VPU extraction — 2026-10-12

This is an amendment to the fourth assignment, not another completed subsystem round. Only VPU advanced. Reviewed project `1a59d79fda42a977956de8e06c3a60d44b2971f4`; kernel `869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf` changes comments only relative to the previously compiled RFC. Other fourth-round tasks remain outstanding.

## Accepted evidence

Coordinator independently inspected the successful [run 38220276125](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125), actual checkout `3dfc56966217dbcadb7107d4df5c913a043b996a`, downloaded [artifact 11734430639](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125/artifacts/11734430639), and verified both SHA256 digests:

- Artifact ZIP: `485ff37b87cff2e6432928cfd4c0d4168bb3c10af163f6e68b6adfba35a528ae`.
- `stock-per-fdt-property-export.json`: 15,862,099 bytes, `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`.

Selected raw properties and fixup-to-symbol mappings were inspected independently. The coordinator did not re-download original stock images or independently reparse their binary FDTs. Source/package provenance is recorded by the SHA-checked extraction job. Full export means every node is indexed and requested properties/fixups exported, not a lossless copy of every property suitable for reconstructing original DTB hashes.

Pinned consumer sources:

- [Compact six-FDT summary](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-12-oneli-stock-fdt-properties.json).
- [Consumer report](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-12-stock-fdt-consumer-report.md).
- [Iris resource/loader contract](https://github.com/Drzet/razr2022_nuc/blob/1a59d79fda42a977956de8e06c3a60d44b2971f4/docs/vpu/2026-10-12-iris-resource-loader-contract.md).

## What is now resolved

| Evidence | Consequence |
| --- | --- |
| Overlay indices 0–3 have board IDs `0x45/b1b0`, `0x45/b2a0`, `0x45/a100`, `0x45/c000` | Index 3 is the PVT reference candidate matching observed hwrev. Actual bootloader selection remains unknown. |
| Two Cape base FDTs, MSM IDs 530 and 540, each 479481 bytes; second begins at byte 479481 | Boot must handle unpadded concatenation. Its current parser aligns to four bytes and would miss the second FDT. |
| Header addresses, legacy-LZ4 ramdisk magic, fragment descriptor now published | These are no longer missing reference fields; native placement and decompression/packer validation remain separate. |
| All overlays: NXP @0x4f has absent local status in an `ok` overlay; Diodes @0x6c explicitly disabled | Reference configuration favors NXP. Stop treating both as equally unknown candidates; composition and exact physical part/driver compatibility still need review. |
| PS5169 @0x30 is `ok`, property named `redriver,enable-gpio` references GPIO19, orientation GPIO91 | Stock DT corroborates enable semantics; USB must trace vendor GPIO operations rather than translate the property blindly into upstream reset pulses. |
| All overlays disable FSA4480-targeted fragments; separate AUX GPIO2/71 properties present | DP can finish its pending variant matrix now. Base FSA4480 presence is not justification to enable it. Actual independent AUX part remains unknown. |
| VPU has two nonsecure context SIDs and three vendor interconnect paths | Resource evidence is available; translating downstream DMA and vote semantics remains substantive driver work. |

## Additional coordinator fixup inspection

In PVT overlay index 3, the exported `__fixups__` entries and base `__symbols__` map these references without guessing numeric phandles:

| Overlay reference | Symbol | Base target |
| --- | --- | --- |
| NXP `vdd18-supply`; PS5169 `vcc-supply` | S10B | `/soc/rsc@17a00000/rpmh-regulator-smpb10/regulator-pm8350-s10` |
| NXP `vdd3-supply` | L2B | `/soc/rsc@17a00000/rpmh-regulator-ldob2/regulator-pm8350-l2` |
| PS5169 `vio-supply` | L8C | `/soc/rsc@17a00000/rpmh-regulator-ldoc8/regulator-pm8350c-l8` |
| GPIO19/91 and AUX GPIO2/71 | tlmm | `/soc/pinctrl@f000000` |
| USB repeater fragment target | qupv3_se5_i2c | `/soc/i2c@994000` |
| PS5169 fragment target | qupv3_se18_i2c | `/soc/i2c@88c000` |
| Disabled FSA fragments 76 and 89 | fsa4480 | `/soc/i2c@994000/fsa4480@42` |

This establishes symbolic reference relationships, not a fully applied overlay or physical parent supply wiring. Numeric `0xffffffff` placeholders remain unrelocated in standalone overlays; that is expected. Power/Boot should resolve symbols rather than label every such reference permanently unknown.

The export's `candidate_phandle_edges` is heuristic: for example it proposes links from `#gpio-cells` numeric values. Do not treat these as typed edges. Use property schemas, provider cell counts, raw property bytes, `__fixups__`, `__local_fixups__` and base symbols. Array cells that happen to equal phandle integers are not necessarily references.

## Changed work order

**Start all other agents now.** Their extraction wait is closed. Boot owns composition; USB/Power/DP can interpret raw properties and symbolic relationships concurrently, then reconcile final effective paths with Boot. GPU firmware comparison and USB failure handling were already independent. Userspace contract work is also independent; project-kernel execution still needs coordinator artifacts.

Boot should first fix unpadded FDT iteration, then compare the PVT candidate with both matching base candidates and produce a typed resolved property matrix. Do not reconstruct and label a filtered JSON projection as the original stock DTB. Actual libfdt application requires retained original bytes; if unavailable, document symbolic resolution separately and coordinate only a bounded existing-member retrieval if essential. No repeat full ROM acquisition is warranted.

VPU may proceed to focused DMA/OPP/ICC/loader work; its extraction milestone is accepted. For ICC, establish whether upstream path aggregation covers the vendor LLCC vote before deciding a third handle is required. Downstream SMMU second-cell semantics must be translated, not copied as presumed upstream flags. Neither discovery alone approves active VPU support.

DP's wait for properties is removed. Its later hold for unresolved part/binding identity remains valid after one updated disposition. The GCC PHY reclassification remains unchanged: it does not block serial/initramfs integration.
