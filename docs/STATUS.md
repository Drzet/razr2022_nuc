# Project status

Updated 2026-10-11, third coordinator review. Latest ADB attempt unsuccessful; work continues without hardware access. Earlier stock inspection identifies XT2251-1 PVT, hwrev 0xC000, SKU dn, Android 14 U2SLS34.1-42-14-11. No native Linux hardware test. Read [NEXT_TASKS.md](NEXT_TASKS.md) for assignments, exact revisions and dependency gates.

| Workstream | Accepted evidence | Next milestone |
| --- | --- | --- |
| Boot | `6eec6ddd7`: [oneli DTB and all-applicable schema pass](https://github.com/Drzet/linux/actions/runs/38175014232); no overlaps in 39 reservations; 13 committed GPU OPPs; 35 dependency warnings retained | Packaging/DT variant audit, warning classification, disabled USB2 staging |
| GPU | `4955f07a9`: [complete Image/modules pass](https://github.com/Drzet/razr2022_nuc/actions/runs/38174090675); committed OPP check passes | GMU error-path fix, CX/bandwidth/UBWC disposition, stock firmware comparison |
| VPU | `7f1d729b6`: [complete Image/modules and binding pass](https://github.com/Drzet/razr2022_nuc/actions/runs/38170604512); host ABI checks; stock archive acquired and hashed | Locate/extract actual VPU/GPU firmware; resolve resource assumptions |
| USB | `87d7277ce`: PHY binding pass; [temporary PS5169 x86 object/binding pass](https://github.com/Drzet/linux/actions/runs/38170306651); agreed Type-C graph | Durable attributable driver series and full ARM64 link; reference variant audit |
| Power | `3b02b11bc`: signed-temperature fix, [UML KUnit 3/3 pass](https://github.com/Drzet/razr2022_nuc/actions/runs/38169484188), ARM64 objects and pinned source audit pass | Charger/policy audit and integration-ready fix |
| DisplayPort | [23-check reproducible source audit passes](https://github.com/Drzet/razr2022_nuc/actions/runs/38174309894); graph agreement | Bounded stock AUX audit, then hold if identity/binding remains unresolved |
| Userspace | `ce17ea82`: ownership/network/SSH code implemented; replacement runs cancelled; [latest run](https://github.com/Drzet/razr2022_nuc/actions/runs/38177877133) at handoff `f785ae4` in progress at review | Complete QEMU boot/SSH pass; strengthen native module/artifact contract |

## Shared reference and remaining gates

[Verified public stock manifest](https://github.com/Drzet/razr2022_nuc/blob/810be63/docs/vpu/2026-10-11-public-stock-reference-manifest.md): 4,353,164,507 bytes, SHA-256 `620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c`. Boot/vendor_boot v4 headers and four DTBO entries parsed. Signed VPU/ZAP files have **not** been located/extracted. Do not assume they reside in super/vendor; inspect actual image formats/mount layout. Matching build label does not prove exact installed contents or active overlay.

No combined integration kernel, validated phone boot recipe, native boot, rendering, decode, USB/DP or electrical power result exists. Independent build success is substantial progress but not combined or hardware validation. Locked bootloader is a future device-test prerequisite; user plans to unlock when the phone is fully in their possession.

Current handoffs remain on subsystem branches, linked through NEXT_TASKS.md and their PRs. Prior review queue preserved in [SECOND_REVIEW.md](SECOND_REVIEW.md); older records are historical snapshots, not current blockers.
