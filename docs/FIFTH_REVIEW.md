> Historical review. Current STATUS.md and NEXT_TASKS.md supersede all work instructions below.

# Fifth coordinator review — 2026-10-12

The largest implementation progress this round is USB's PS5169 failure handling and Boot's packaging tools. GPU, Power and DisplayPort improved the evidence and correctly retained unsupported hardware holds. Userspace has a prepared project-kernel consumer, but it has not executed that path. **There is still no accepted combined kernel build.** That is an integration deliverable, not a dependency on phone access or further VPU extraction.

## Reviewed project heads

All heads below are in Drzet/razr2022_nuc. The review starts from coordinator main `5261a8cb15e93d406bc58d711c224d53104c129c`; subsystem branches have not been merged wholesale.

| Owner | Reviewed project commit | Result |
| --- | --- | --- |
| Boot | `cfdecbf41a329bcc0fa3074f8de708e95ef698b1` | Unpadded FDT parsing, explicit packaging v2, independent synthetic pack/unpack, typed symbolic PVT matrix |
| USB | `5e0556fe95fb8b1ba0b1a92a980d6640cb3d318d` | PS5169 register-error propagation, retry/rollback, endian handling, enable/reset binding distinction |
| GPU | `874fe6d5243806a9c46b7a84b421167a0509c7c8` | Stock/generic firmware differences and GX/CX/ICC evidence; missing export fields identified |
| Power | `9a163f0cea7e93af6823b6e2581b7f1db775e782` | Symbolic USB supply providers and base voltage ranges; electrical parents unresolved |
| DisplayPort | `d5b45132914f075c784c6bbb2ca2e604cd262f86` | All four AUX/FSA variant dispositions complete; no defensible AUX IC compatible |
| Userspace | `9c7150def328c4180ed995c11e5bcbd6d1f471ad` | Artifact v3 checks, Boot-v1 bridge, matching-module/initramfs preparation and guest module-load checks |
| VPU | `1a59d79fda42a977956de8e06c3a60d44b2971f4` | Unchanged since accepted extraction; no new DMA/OPP/ICC result claimed |

Kernel Boot remains `525b504b82dbca593a9a697af9be63f53915e0a3`, GPU remains `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`, and standalone Power remains `564f2c7df60316db86e36d7267ddadf07bc32b7e`. New USB candidate is `Drzet/linux:razr/usb-ps5169` at `2875777fef3496f33ad6862678251d1de00ee7f6`. DP has no kernel patch. These are separate candidates, not an integrated phone image.

## Independently checked validation

The coordinator inspected GitHub job status and logs, not just handoff assertions.

| Evidence | Exact tested source | Accepted scope |
| --- | --- | --- |
| [Boot 38281131338](https://github.com/Drzet/razr2022_nuc/actions/runs/38281131338), job 114918410787 | Project `b16bd7b0d488a20105dc8abba582f800a4be6cd8` | 9/9 tests: changed-size synthetic pack/unpack against pinned independent AOSP-derived tools and symbolic metadata checks. No actual stock libfdt composition or phone boot |
| [USB 38243032057](https://github.com/Drzet/linux/actions/runs/38243032057), jobs 114790073872 / 114790074074 | Kernel `2875777fef3496f33ad6862678251d1de00ee7f6` | Host fault-injection job, binding checks and full ARM64 Image/modules all completed successfully; ordinary MODPOST visible. Full build is no longer pending |
| [Userspace 38245293728](https://github.com/Drzet/razr2022_nuc/actions/runs/38245293728), job 114797531172 | Project `9b168c89f5d0328fd0c9a690ffd6808ffb73333d` | Latest 11/11 fixtures and BOOT_REFERENCE_METADATA_PASS. Supersedes report's older latest-pass reference 38244943279; no combined-project-kernel guest run |

USB build-record artifact 11746724447 has ZIP SHA256 `7d91c163921fab411be7da6925a4ed1a8d54f4abd4bea8ae28f814c0f0c4d17c`. Logs hash Image `0423d8145649ce6ed3e809ce13d9c2de75a0d9bb73ffe03d290a4e92d123b018`, Module.symvers `ad4f64708b64e132fea71feb4602c437831a2ba1c4f267708f2f8cfcf63725d9`, and ps5169.ko `ad4652c9582c1f455fdcc32e287427c8c2f598f5564eec3d399737de0c6f88e3`. This small record artifact is not the complete installed-module delivery needed by Userspace.

Userspace run 38244458164 was a false green: tee masked a failed negative fixture without pipefail. The defect is documented and fixed; do not cite that run as acceptance. Latest checks propagate failure. The earlier complete Debian-distro-kernel QEMU pass remains valid for its own scope. Host-extracted PS5169 helper tests do not execute the real kernel probe/lifecycle.

## Evidence corrections and remaining gaps

- **27 PS5169 triplets, not 29.** Coordinator reparsed the previously hash-verified full FDT export: PVT config-seq is 324 bytes / 81 u32 cells / 27 triplets. First operations are `(0x9d,0x80,10000)`, `(0x9d,0,0)`, `(0x40,0x80,0)`. This corrects the previous assignment/amendment count. Vendor GPIO19 enable is not evidence for an arbitrary reset pulse. Generic EQ controls do not implement the entire board sequence.
- **Export filtering is consequential.** Both bases contain 13 GPU power-level nodes, but the exported child properties only include reg; frequency, CX and bus-vote fields were filtered out. Their absence from this JSON does not prove absence from stock DT. Coordinator independently confirmed this. Preserve the distinction between pinned Motorola source OPP data and compiled reference values.
- **Power providers are symbolically resolved; electrical parents are not.** S10B is 1.8 V fixed; base L2B is 2.7–3.3 V and L8C 1.8–2.0 V. PVT fragment48 targets L8C but its exported property dictionary is empty. That does not establish the fragment's complete content or effective constraints. A bounded unfiltered export is needed before claiming the effective PVT values. Do not substitute donor-board VPH/BOB wiring.
- **Boot-v2/Userspace-v1 interface drift remains.** Boot now requires explicit header inputs; Userspace's pinned bridge still consumes v1. Its successful fixtures do not establish v2 compatibility. Symbolic resolution is useful, but is not libfdt apply or proof of bootloader selection.
- **Userspace prep needs direct execution coverage.** Current fixtures test the validator; prepare-project-qemu.sh was syntax-checked. Its rejection of an Image based on an `oneli` pathname is not a valid compatibility test: one suitably configured ARM64 Image can serve multiple boards. Verify config/provenance and QEMU's generated DT instead. Also install cleanup before the first mount so a partially failed mount setup is unwound. These are concrete follow-ups, not claims of observed guest failures.
- **DisplayPort's current task is finished.** All reference overlays disable FSA4480 and retain separate GPIO2/71 AUX controls. Neither this nor PS5169 identifies the independent AUX switch. No more generic source audits are useful without new part evidence.
- **Seven GCC PHY references retain the downgraded severity.** UART/initramfs does not need PCIe/USB3/UFS. UFS is needed for internal-storage rootfs. Remaining source probe-order checks and eventual runtime checks do not justify enabling unused PHYs or blocking a minimal combined compile.

## Decision

The next milestone is one combined, disabled-peripheral kernel build followed by its real QEMU virt smoke run. The coordinator has not delivered that build yet. To remove this repeated scheduling gap, [NEXT_TASKS.md](NEXT_TASKS.md) explicitly assigns Boot execution of an isolated integration candidate; coordinator retains selection, review and promotion ownership. This is a new narrow delegation, superseding earlier instructions that Boot must not prepare any combined candidate.

VPU/USB source work and Power's read-only audit can proceed concurrently. GPU waits only for the missing exported fields needed for its final vote decision. DisplayPort should wait for attributable AUX identity. Native boot/console, firmware authentication, DMA/HFI, rendering/decode, USB/DP link behavior and electrical/charging safety remain untested hardware gates. QEMU cannot close them.
