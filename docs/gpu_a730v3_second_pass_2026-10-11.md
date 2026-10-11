# GPU second-pass audit: Adreno 730v3 (oneli)

Date: 2026-10-11. Kernel baseline: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. GPU patch: `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`. Shared DT owner: Boot; pinned reference for compiled proposal: `cbde49d927478decd6d608a309a7d7482992f776`. Hardware/installed firmware are unavailable.

## Revision-specific downstream comparison

Source (pinned): [Motorola KGSL adreno-gpulist.h, lines 1956–2043](https://github.com/MotorolaMobilityLLC/kernel-msm/blob/9511d6b2dc469e5bd836992e3bdd6d19ace112e0/drivers/gpu/msm/adreno-gpulist.h#L1956-L2043), compared to [Motorola Cape GPU description](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-gpu.dtsi#L4-L43) and [pinned mainline GPU catalog](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/gpu/drm/msm/adreno/a6xx_catalog.c#L1480-L1503).

| Field | Motorola Gen7-0-1 | Motorola Gen7-4-0 (oneli's `qcom,adreno-gpu-gen7-4-0`) | Pinned upstream A730 record |
|---|---|---|---|
| Base chip identification | `0x07030001` | `0x07030002` from Cape DT; Gen7-4-0 catalog uses ANY_ID | `0x07030001` before patch; both `0x07030001` and `0x07030002` after patch |
| SQE | `a730_sqe.fw` | Same | Same |
| GMU | `gmu_gen70000.bin` | Same | Same |
| Vendor fallback GMU | `c500_gmu.bin` | Same | No corresponding fallback in A730 profile |
| ZAP base name | `a730_zap` | Same | `a730_zap.mdt` fallback, board `firmware-name` override supported |
| HWCG table | `gen7_0_0_hwcg_regs` | Same | `a730_hwcg`, source-level mapping resembles vendor, exact register-by-register equivalence not yet demonstrated |
| GBIF table | `gen7_0_0_gbif_regs` | Same | `a640_gbif`; must not infer identical data solely from similar names |
| Protected registers | `gen7_0_0_protected_regs` | Same | `a730_protect` |
| GMEM | 2 MiB | 2 MiB | 2 MiB |
| Bus width | 32 | 32 | No explicit `bus_width=32` in A730 catalog entry |
| Features | APRIV, IOCOHERENT, CONTENT_PROTECTION, IFPC, ACD, L3_VOTE, BCL, PREEMPTION | Identical list | cached coherent, APRIV, PREEMPTION only; IFPC and ACD are **not** enabled in A730 quirks |

The vendor's two records share the same fields listed above. This is source evidence supporting reuse of the A730 Gen1 programming profile rather than inventing a new A730v3 driver. It is **not** evidence of equivalent secure firmware acceptance, voltage/clock behaviour, or power management. [INFERRED] Missing optional vendor IFPC/ACD/L3/BCL features can affect power/performance, but the source comparison does not establish a requirement to backport them before initial rendering. Do not add an IFPC quirk or vendor feature flags without an independently reviewed mainline implementation.

The upstream [GMU OPP/RPMh code](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/drivers/gpu/drm/msm/adreno/a6xx_gmu.c#L1693-L1874) constructs ARC votes from `opp-level`, RPMh command DB and device OPP tables, **not** by importing downstream `qcom,cx-level` verbatim. The relevant downstream extra CPU/GMU-facing votes must remain visible in this audit.

## Full Motorola GPU frequency and corner matrix

All frequencies, corners, bus indices and ACD words below are transcribed from pinned [`cape-gpu.dtsi` levels 0–12](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-gpu.dtsi#L67-L245). The corner integer values are from pinned [RPMh DT header](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/include/dt-bindings/power/qcom,rpmhpd.h#L35-L75). Bus values are downstream indices, **not KB/s**.

| MHz | GPU `opp-level` | GPU corner integer | Separate vendor CX corner | Bus freq/min/max | Vendor ACD word |
|---:|---|---:|---|---|---|
| 900 | TURBO_L1 | 416 | TURBO_L1 | 11/11/11 | `0x882b5ffd` |
| 862 | TURBO | 384 | TURBO | 11/11/11 | `0x882b5ffd` |
| 815 | NOM_L1 | 320 | NOM_L1 | 11/10/11 | `0x882b5ffd` |
| 765 | NOM | 256 | NOM | 10/9/11 | `0x882c5ffd` |
| 710 | SVS_L2 | 224 | **NOM** | 10/6/11 | `0x882c5ffd` |
| 645 | SVS_L1 | 192 | SVS_L1 | 8/6/9 | `0x882d5ffd` |
| 580 | SVS_L0 | 144 | **SVS_L1** | 8/6/9 | `0x882e5ffd` |
| 515 | SVS | 128 | SVS | 6/6/8 | `0x882e5ffd` |
| 439 | LOW_SVS_L2 | 96 | **SVS** | 6/3/8 | `0xc0285ffd` |
| 364 | LOW_SVS_L1 | 80 | **SVS** | 3/1/6 | `0xc0285ffd` |
| 324 | LOW_SVS | 64 | LOW_SVS | 2/1/6 | `0xc02a5ffd` |
| 285 | LOW_SVS_D1 | 56 | **LOW_SVS** | 2/1/5 | `0xc02c5ffd` |
| 220 | MIN_SVS | 48 | **LOW_SVS** | 2/1/5 | `0xc8285ffd` |

**Unresolved integration issue:** six of thirteen vendor CX corners differ from GPU corners (710, 580, 439, 364, 285, 220 MHz); the preceding rows document the actual set. Neither simply copying the GPU corner into both ARC tables nor silently discarding the downstream CX votes establishes voltage correctness. Mainline's GMU OPP/ARC model and firmware-dependent vote interpretation require source-level reconciliation plus eventual on-device voltage/thermal tests.

The proposed DTS block in [GPU handoff](handoffs/gpu-2026-10-11.md) removes ten SM8450-only OPP nodes and installs all thirteen supported Cape GPU frequencies/corners. It deliberately does **not** claim to map vendor `qcom,cx-level`, vendor bus-table indices or ACD words. The [compiled fixture validator](../tests/scripts/gpu-opp-fixture.py) extracts that block from the handoff into a **temporary** checkout of an exact Boot commit, builds a DTB and checks each OPP's 64-bit frequency and compiled numeric corner. This is not an edit or integration of `razr/boot` and must not be mistaken for on-device frequency testing.

## Firmware requirements for a shared GPU/VPU public-stock manifest

- `qcom/a730_sqe.fw` (SQE): kernel's expected lookup; linux-firmware WHENCE publishes version v1.81. **Content SHA-256 not yet captured.**
- `qcom/gmu_gen70000.bin` (GMU): kernel's expected lookup; linux-firmware WHENCE publishes version v4.00.07. **Content SHA-256 not yet captured.**
- Device-signed ZAP: vendor base name `a730_zap`, kernel fallback `a730_zap.mdt`. Public firmware source for **Motorola oneli** not yet extracted; signed image, accompanying segmented MDT files, full path and SHA-256 are **unknown**. Neither generic SM8450 nor Nothing Pong ZAP is established as valid for oneli.
- The pinned Motorola KGSL catalog also lists alternate `c500_gmu.bin` for both 7-0-1 and 7-4-0, but mainline's catalog does not request that fallback. Do not silently substitute it.

Candidate **public, not installed** oneli firmware archive: [Lolinet RETGB directory](https://mirrors-obs-1.lolinet.com/firmware/lenomola/2022/oneli/official/RETGB/), listing `XT2251-1_ONELI_RETEU_14_U2SLS34.1-42-14-11_subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.xml.zip` (2025-11-19; about 4.35 GB in directory units). This identifies a **candidate source**, not a downloaded or independently hashed image. The package contents, signed ZAP presence, firmware hashes and extraction results remain unknown. The target phone is currently unavailable and its installed firmware/retail region/board revision cannot be identified. VPU and Boot should share **one** pinned public package manifest when one has been downloaded/verified, keeping extracted binaries out of Git.

Recommended manifest columns: source URI, exact package filename, release/version/region, observed archive SHA256, partition/archive member, exact firmware relative path, size, SHA256, license/provenance, role, status (observed in package vs expected from source) and build/board applicability. Never fill unknown hashes from product listings.

## Build and runtime boundaries

Two GPU-only GitHub Actions workflows were added on coordination branch `razr/gpu`:
- `gpu-arm64.yml`: pins GPU kernel commit `4955f07...`, checks ARM64 resolved `CONFIG_DRM_MSM=m`, builds kernel Image and then `M=drivers/gpu/drm/msm` module, archives logs/config/module SHA when successful.
- `gpu-opp-fixture.yml`: pins Boot `cbde49d...`, injects reviewed OPP snippet only in runner checkout, compiles DTB and runs `fdtget` frequency/corner/compatible assertions.

Successful CI is required before marking these tests passed; a workflow file or in-progress run alone is not a build result. No physical GPU/GMU/rendering test can run without the oneli handset.
