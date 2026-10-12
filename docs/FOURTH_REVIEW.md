# Fourth coordinator review — 2026-10-12

Review scope: current subsystem commits, handoffs, selected source changes, GitHub Actions conclusions and selected job logs. The coordinator did not execute a native phone test, repeat firmware downloads, or merge kernel branches. Baseline remains `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`. The previous assignments are preserved in [THIRD_REVIEW.md](THIRD_REVIEW.md); new assignments are in [NEXT_TASKS.md](NEXT_TASKS.md).

## Reviewed revisions and accepted evidence

Project heads in `Drzet/razr2022_nuc`:

| Owner | Exact project head | Kernel candidate |
| --- | --- | --- |
| Boot | `12fd47873ed587ab7518c3ac747c747757e8005f` | `525b504b82dbca593a9a697af9be63f53915e0a3` |
| GPU | `4d3bd86575217db07ef38db3b1b65aaae2cbcbde` | `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3` |
| VPU | `c25ff584bde73515d036de424c57e48b985ca01b` | unchanged RFC `7f1d729b6f458f1e76efe2894eb3c544bc9db856` |
| USB | `d8388f64907ed2768a41205fd76fab5f551efca0` | durable PS5169 `4cbfc0145d9c837d2ba3fd9050f529a786135403` |
| Power | `3319e3fa94636ee52f764f500f58c77bd183b5cb` | original `3b02b11bc5abdc5c453fa4af16b71bd8e44c2056`; standalone `564f2c7df60316db86e36d7267ddadf07bc32b7e` |
| DisplayPort | `6c78fe7eb1e2a1fa8a5a241a1666eef6eb6b06f0` | upstream baseline, no DP implementation |
| Userspace | `d12a97a0e360ba885f4859884a08dd8f4ac292cc` | generic Debian kernel tested; no combined project kernel yet |

### VPU: firmware-location milestone completed

[Fourth-round handoff](https://github.com/Drzet/razr2022_nuc/blob/c25ff584bde73515d036de424c57e48b985ca01b/docs/handoffs/2026-10-11-vpu-fourth-round.md), [radio manifest](https://github.com/Drzet/razr2022_nuc/blob/c25ff584bde73515d036de424c57e48b985ca01b/docs/vpu/2026-10-11-radio-non-hlos-firmware-manifest.json), [vendor manifest](https://github.com/Drzet/razr2022_nuc/blob/c25ff584bde73515d036de424c57e48b985ca01b/docs/vpu/2026-10-11-stock-filesystem-firmware-manifest.json).

The controlled stock scan [38180072535](https://github.com/Drzet/razr2022_nuc/actions/runs/38180072535) and bounded radio scan [38180934057](https://github.com/Drzet/razr2022_nuc/actions/runs/38180934057) completed successfully. Coordinator checked Actions and radio job logs, including actual container SHA and metadata-only artifact digest, and inspected the committed manifest; did not independently re-extract the proprietary bytes.

Actual source chain: verified public Android14 ZIP → Motorola `radio.img` / `SINGLE_N_LONELY` → sparse `NON-HLOS.bin` → ext4 `image/`. It contains `vpu20_4v.mbn`, MDT and split segments, A730 SQE and signed ZAP files. GMU is separately in vendor_a. VPU MBN is 2,024,040 bytes, SHA256 `9582ea4c5565408bd3e5ba6f8fffc7881f226cae001b6fcd7a0c868de9add9af`, version `video-firmware.2.4-33580ad5a949b4d45b3b008988280e60573cd894`. Earlier claims that these files were unlocated are superseded.

Firmware authentication, HFI negotiation and DMA/decode remain untested. ELF physical addresses do not settle IOMMU or reserved-memory topology. The Iris RFC still contains unresolved platform assumptions. GPU's independent shared-UBWC review is now complete at source level; VPU handoff's “awaiting review” wording is stale. The default on-device UBWC/DRAM profile remains [INFERRED].

### Boot: narrower dependency set, structural packaging prototype

[Handoff](https://github.com/Drzet/razr2022_nuc/blob/12fd47873ed587ab7518c3ac747c747757e8005f/docs/handoffs/2026-10-11-boot-fourth-round.md). USB2 PHY/DWC3/GLINK graph is staged disabled. Disabling unused audio/display consumers reduced active-to-disabled references from 35 to seven GCC PHY clock parents. These are classified warnings, not proven harmless.

Important provenance correction: all-applicable schema [38182280401](https://github.com/Drzet/linux/actions/runs/38182280401) actually checked out `2b47361928154b8b8a3addc84ae431b43d200e4a`, confirmed in job log. The handoff incorrectly attributes that run to `525b504...`. The latter changes only the separate FDT workflow's checker pin; its independent FDT [38182283694](https://github.com/Drzet/linux/actions/runs/38182283694) passed at `525b504...`. Schema-tested DT source is unchanged. Counts: 898 nodes, 39 reservations, zero overlaps, 889 decoded references, seven warnings, 13 GPU OPPs.

[Synthetic v4 packaging tests 38182066319](https://github.com/Drzet/razr2022_nuc/actions/runs/38182066319) passed. No real-reference roundtrip or bootloader acceptance demonstrated. Source inspection: candidate generator copies reference header fields, including vendor loading addresses and boot OS-version field, before replacing selected fields. Explicit payload arguments therefore do not mean all placement inputs are explicit. Its identity repack copies original sections/padding; an independent parser/packer comparison is needed for stronger format evidence.

### GPU: narrow source fix and full build now passed

[Handoff](https://github.com/Drzet/razr2022_nuc/blob/4d3bd86575217db07ef38db3b1b65aaae2cbcbde/docs/handoffs/gpu-2026-10-11-fourth-pass.md). Inspected kernel patch: propagates `a6xx_gmu_pwrlevels_probe()` failure through cleanup and disables runtime PM on unwind. Full Image/modules [38178986611](https://github.com/Drzet/razr2022_nuc/actions/runs/38178986611) succeeded at exact kernel `3baaec...`, including normal modpost; this supersedes pending full-build wording. Object and structural negative checks also passed.

CX-floor/bandwidth mapping and shared UBWC review are useful source results, not hardware enablement. GPU firmware consumer report predates VPU's final radio discovery and must now consume those actual hashes. Keep GPU disabled while power-vote contracts remain unresolved.

### USB: durable implementation, real source defects remain

[Handoff](https://github.com/Drzet/razr2022_nuc/blob/d8388f64907ed2768a41205fd76fab5f551efca0/docs/handoffs/2026-10-11-usb-third-round.md). [38181747728](https://github.com/Drzet/linux/actions/runs/38181747728) passed attributable import, binding validation and dependency-complete ARM64 Image/modules. Tested resulting source `4cbfc014...` differs intentionally from orchestration trigger `068af133...`; handoff records this accurately.

Coordinator inspected `ps5169.c`: register writes/EQ updates discard errors; software orientation/mode are updated before hardware success; retimer change detection checks mode but not independent SVID change. These need failure/retry semantics, not merely another compilation. GPIO19 enable versus upstream reset interpretation remains unresolved. ARM64 little-endian success also does not validate raw `__le16` ID comparisons on other architectures. No active oneli node is approved.

### Power: integration-ready temperature fix; charger policy still research

[Handoff](https://github.com/Drzet/razr2022_nuc/blob/3319e3fa94636ee52f764f500f58c77bd183b5cb/docs/handoffs/2026-10-12-power-third-review.md). The standalone temperature series excludes old Boot history; owner reports all five file blobs identical to tested original. Source audit, ARM64 objects and UML tests also passed again on latest project runs [38216792058](https://github.com/Drzet/razr2022_nuc/actions/runs/38216792058), [38216792074](https://github.com/Drzet/razr2022_nuc/actions/runs/38216792074), [38216792083](https://github.com/Drzet/razr2022_nuc/actions/runs/38216792083). These still pin the original kernel; standalone combined linking is pending.

Charger report appropriately distinguishes exact oneli DT from an SM8250 Motorola-family driver comparator. Shared PN bits do not prove SGM41516D/SGM41542 register compatibility. Dual-battery balancing, switches and thermal policy are substantial separate work; a new active charger implementation is not justified by this report alone.

### DisplayPort: hold is justified, final stock properties not inspected yet

[Bounded matrix](https://github.com/Drzet/razr2022_nuc/blob/6c78fe7eb1e2a1fa8a5a241a1666eef6eb6b06f0/docs/displayport_oneli_four_dtbo_aux_matrix_2026-10-11.md) correctly marks actual per-variant AUX properties unpublished, rather than absent. The physical AUX switch/binding remains unresolved. Existing graph agreement and source audit are complete; no new driver or physical DP result.

### Userspace: fresh full build passes; native contract needs scope alignment

[Handoff](https://github.com/Drzet/razr2022_nuc/blob/d12a97a0e360ba885f4859884a08dd8f4ac292cc/docs/handoffs/2026-10-11-userspace-debian.md). Fresh full [38180519542](https://github.com/Drzet/razr2022_nuc/actions/runs/38180519542), source `e14f618fc1c55b3581e3bf082c1d12bbb0b05e03`, **passed**. Coordinator inspected job `114591959041`: actual archive ownership roundtrip passes and `QEMU_SYSTEMD_NETWORK_SSH_PASS` emitted by the checked smoke script after boot, authenticated SSH and zero exit. This supersedes pending handoff wording and is stronger than replay alone. Artifact `11718361285`, uploaded archive SHA256 `54ce998152b1a7ae247a247e4b6b67d013c0b160e14d265499e3d91f002042ca`. This is generic Debian ARM64 on QEMU virt/TCG, not the project kernel or Qualcomm emulation. Internet/default-route functionality was not required by the script.

Native validator now checks real module ELF/vermagic, hashes and unpacked initramfs bytes; six fixtures passed. Source review finds integration mismatch: validator requires packaging `status=verified`, while Boot's v1 manifest has no such field and explicitly remains a structural prototype. It also requires a nonempty firmware list and nonempty initramfs-module list for every case. Explicit scoped zero-requirement configurations must be representable without converting unknown requirements to success. Vermagic release is checked, not complete flag/CRC compatibility; same-build provenance remains necessary.

## Shared metadata bottleneck and failed live captures

The radio/firmware milestone is complete. The per-DTBO numeric IDs, actual properties and vendor_boot base-FDT inventory are a different, unfinished publication. Four consumers have requested essentially the same data in [issue #10](https://github.com/Drzet/razr2022_nuc/issues/10). Hashes and root strings cannot substitute for it. Stop circulating identical requests: VPU owns one bounded export; Boot owns composition/interpretation with subsystem consumers.

Coordinator independently inspected both uploaded live-DT archives on 2026-10-12:

| Archive | Bytes | SHA256 | Actual contents |
| --- | ---: | --- | --- |
| `oneli-live-dt.tar.gz` | 118 | `a9ecb6a4d2a223e590ff1c02b103db34c0e3003a2866d34b3c52c59a7cc66c14` | One symlink; zero regular property files |
| `oneli-live-dt.tar (1).gz` | 1680 | `69d307560554a0c59f62438e6cf567b06e955653d3f25bada70ae13a81ec7ee6` | 83 directories; zero regular property files |

Neither supplies live property values or confirms the active overlay. Directory names alone do not establish resource sizes, wiring, statuses or selected configuration. Preserve earlier valid stock ADB observations; do not describe these archives as a recovered live FDT.

## Overall decision

Move from isolated source milestones to a selected combined kernel and matching Userspace artifacts, concurrently with one final shared DT metadata export and targeted driver fixes. Physical boot, authentication, rendering, decoding, USB/DP and electrical/charging tests remain deferred. No percentage-complete estimate is defensible; no native hardware gate has passed.

## Follow-up correction: GCC warning severity

See [GCC_PHY_CLOCK_RECLASSIFICATION.md](GCC_PHY_CLOCK_RECLASSIFICATION.md). Independent source inspection supports downgrading these seven inputs to deferred feature dependencies. UART clock ancestry does not use them; CCF supports unresolved selected parents. The prior “boot-critical” classification was too broad. Actual hardware-selected mux states are unknown; seven references do not imply seven orphan clocks. This does not block the initramfs/serial milestone.

## VPU extraction completed after this review

[Fourth-assignment amendment](FOURTH_REVIEW_VPU_UPDATE.md) supersedes the missing per-FDT publication blocker. The six-FDT export has been independently downloaded and hash-checked; other agents should consume it now. Historical findings above retain their original review scope.
