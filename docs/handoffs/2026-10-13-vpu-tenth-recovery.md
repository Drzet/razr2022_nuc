# VPU canonical handoff — Qualcomm upstream v5 adaptation candidate

**Updated:** 2026-10-14, coordinator review and consolidation. **Status:** bounded offline closure accepted; SM8475 remains disabled and excluded from integration. **Stop:** VPU paused; only coordinator main NEXT_TASKS can assign further work.

## Exact branches and inputs

- **Canonical kernel candidate:** [`Drzet/linux:razr/vpu-provenance-v5@a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac`](https://github.com/Drzet/linux/commit/a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac), based on VPU kernel `869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf`; original baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- **Project evidence/handoff branch:** `Drzet/razr2022_nuc:razr/vpu`; this is the single current VPU handoff. Earlier [upstream reuse audit](../vpu/2026-10-13-tenth-upstream-reuse-prototype-audit.md) remains historical source evidence; it is not the implementation queue.
- **Upstream source:** Vikash Garodia et al., Qualcomm [`[PATCH v5 00/13] media: iris: Migrate iommus to iris sub nodes`](https://lists.openwall.net/linux-kernel/2026/09/26/358), 2026-09-26, Message-ID `20260926-vpu_iommu_iova_handling-v5-0-0322ca5dc10c@oss.qualcomm.com`, series base `f5f84daefcd92d7a630066635ecea1433ed5eac7`. Pinned [dt-schema PR #207](https://github.com/devicetree-org/dt-schema/pull/207) merged dependency revision `840a01d414daf3e8ac0b8a386c36edb68f397189`.
- **Accepted kernel/Boot source dependency:** `Drzet/linux:razr/integration@2b5acf108ae37040ac1e652e029bb37f5609e886` for exact oneli->sm8475->sm8450 bus hierarchy/cell checks, **unchanged**. No shared DTS, accepted diagnostic-v2 manifest, image or userspace input changed.
- **Frozen archive:** `Drzet/linux:razr/vpu@a6327db1c2dbeab9d18ba913c20cb126a3a5a1a1`, preserved at `archive/vpu-peer-prototype-2026-10-13`; old peer DMA-consumer compatible/phandle/IOVA-only reserved-memory ABI is superseded and must not be merged.

## Implementation and provenance

Historical tested commits on frozen `razr/vpu-upstream`, in dependency order (corrected mapping below):
1. **Historical upstream-derived backports (original author metadata corrected on the new branch below):** `7d7038b2` Qualcomm v5 common Venus binding context nodes; `b8d974e5` v5 `iommu-ranges` OF reservation support; `6619b5ec` v5 Iris `non-pixel`/`pixel` child DMA-device creation; `3e4c8aae` v5 VB2/internal/HFI buffer ownership routing; `48606cc3` v5 parent DMA-mask handling. Original tested commits are preserved but had incorrect Git authorship; a separate corrected series is documented below. Not claimed upstream merged into Linux mainline.
2. **Local VPU2/SM8475 adaptations:** `15aba70e` adds disabled/fail-closed SM8475 context contract, `93ed9eb2` restricts experimental binding to nonsecure contexts. Stock reference SID/mask pairs nonpixel `0x2180/0x400`, pixel `0x2187/0x400`; windows `[0x25800000,0xe0000000)` and `[0x00100000,0xe0000000)`. Pixel low floor is **[INFERRED]** conservative stock-policy retention rather than proven silicon requirement. Upper bound enforced with device-local IOMMU ranges, not invalid holey DMA mask. Firmware PAS physical carveout remains distinct. Existing HFI Gen2/VPU2 code reused, no new driver architecture. SM8475 probe explicitly returns `-EOPNOTSUPP` **before** V4L2 while firmware/PAS, MXC/MMCX and ICC policy are unresolved.
3. **Fixtures/CI and corrections:** `4cefd67d` production-route/DT fixture checks, `dc244b1b` CI setup, `fa899044` schema cleanup, `89884d53` skip redundant full builds on fixture-only commits, `f9c74e06` and `ec9a8949` correct DT property ordering. Tests use enabled copies of disabled fixtures and include deliberately invalid instances. No Boot shared DTS edit.

## Verified results, exact evidence

- **PASS full ARM64 dependency-complete build including `Image`, `modules`, modpost and `qcom-iris.ko`:** [workflow 38431204894, job 115413530352](https://github.com/Drzet/linux/actions/runs/38431204894), kernel `fa89904487d4a465eb6df3f14db123d553be9502`. Build log explicitly records `MODPOST Module.symvers`, `OBJCOPY arch/arm64/boot/Image`, `LD [M] .../qcom-iris.ko`. The **overall workflow was FAILURE because its separate host/schema job failed**, not because the ARM64 build failed. Artifact `iris-v5-arm64-build-evidence`, id `11833993049`, CI-reported ZIP SHA256 `8c23a989342978b1a0c1b0ec88086656e27f337e369e0b075098837cd23c12b3`; not independently downloaded/rehashed.
- **PASS final focused schema/host CI:** [workflow 38431847444](https://github.com/Drzet/linux/actions/runs/38431847444), exact head `ec9a8949cfbd1b05cf01553bffc39719ee1a16a7`, job `115415753529`. Enabled positive fixture, **eight expected-invalid schema cases**, pinned SoC hierarchy, fixture-constant IOVA-bound assertions (not parser execution), **53 checks against extracted production routing functions**, plus source assertions for HFI/internal allocation/free symmetry, VB2 role routing, child lifecycle and fail-closed SM8475 gate. Pinned merged dt-schema commit `840a01d414daf3e8ac0b8a386c36edb68f397189`. CI-reported host artifact ZIP SHA256 `e5952ea677dfced77e34b5bfc195b458b596d33c8c8b6dc8abcd4388435e8cdb`; not independently rehashed.
- **Why final ARM64 job was skipped:** last commits `f9c74e06`/`ec9a8949` change fixture/test only; CI `source_changes` gate skips identical driver build inputs. The earlier successful full build is applicable to unchanged C/IOMMU driver source. Schema-only `fa899044` was included in full build's kernel head. This is **not** a full build at final head.
- **NOT TESTED:** physical IOMMU/SMMU allocation, runtime child-device creation on oneli, firmware PAS9 signature/ACK, HFI exchange, decoding, hardware clocks/power/ICC, actual phone, final active board DTS. Host extraction/shims and source assertions cannot establish runtime behavior.

## Remaining boundaries and stop condition

This satisfies the assigned **disabled upstream-derived candidate**, not a working decoder. Preserve existing supported platforms and upstream attribution; no bespoke peer bindings, secure sessions, OPP/ICC expansion, or Boot-owned shared DTS. Coordinator accepted the bounded offline closure below. This does not authorize integration or another VPU task. Follow only current coordinator main NEXT_TASKS. No new firmware extraction, repeat generic reuse audit, or duplicate full build for identical driver inputs.

## Coordinator-required closure, 2026-10-14: completed offline deliverables

**Authoritative result:** original candidate `Drzet/linux:razr/vpu-upstream@ec9a8949cfbd1b05cf01553bffc39719ee1a16a7` is preserved. New **provenance-corrected implementation branch** [`razr/vpu-provenance-v5@f8d742ff240f44ea150a90b24002d41703c66948`](https://github.com/Drzet/linux/tree/razr/vpu-provenance-v5) starts at required `869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf` and replays thirteen historical source trees onto a new commit chain without changing kernel source. No separate driver, accepted integration, board DTS, resource policy, firmware or hardware state was changed.

### Source provenance and reconstruction

- **Exact upstream series:** Qualcomm v5 `20260926-vpu_iommu_iova_handling-v5-0-0322ca5dc10c@oss.qualcomm.com`. Fetched thread mbox URL: `https://lore.kernel.org/all/20260926-vpu_iommu_iova_handling-v5-0-0322ca5dc10c@oss.qualcomm.com/t.mbox.gz`. **Compressed downloaded mbox SHA256:** `5e882d398deb2ab99423190e14a00fcef623d68790ae757ab6c8f5432a8173f7`. **Decompressed mbox SHA256:** `ea89d5bc0b6f58f3d24e856928e88c4512defd8256bf8aa20616e9fbf35644a2`. Digest and original Message-IDs obtained by [successful provenance GitHub Actions run 38486727933](https://github.com/Drzet/linux/actions/runs/38486727933), job `115602051003`, executable script `tests/vpu_provenance_rebuild.py` on test branch.
- Five upstream patches restored **original Git author Vikash Garodia `vikash.garodia@oss.qualcomm.com`**, dated 2026-09-26, original patch subject and body, legitimate upstream source trailers and exact Message-ID, with a clearly labelled backport note. Each extracted upstream diff and its corresponding historical backport has **identical `git patch-id --stable`**. No new local signature was manufactured; no upstream review trailer was added to the separate local adaptation commits. Import identities and old/new SHAs:

| Original v5 patch | Old Drzet-author SHA | New attributed SHA | Stable patch-id |
| --- | --- | --- | --- |
| 01/13 common context binding | `7d7038b2fdbc8b3f514849288231dcc56bad631d` | `284faea8e13ae48a98f950faa314788d6d7fe409` | `e1330b5a848460d14cd6574877fcf607d269d9a1` |
| 04/13 OF `iommu-ranges` | `b8d974e54e99d23f168d676863865257ec505a6f` | `1660c0069f473c7a7c64723e80af3e2953b55b24` | `eecfd66a55b8f2b7b2fc7d76d815facca0489d00` |
| 05/13 context child devices | `6619b5ec1c7d88b14d480f7831e9c7b8332a6cd8` | `a1db34f4dd6eace8479d1ab8bced0b271ecf5a5c` | `bb9ca73889bfca249029efb854fb1634a4360b5c` |
| 06/13 DMA buffer routing | `3e4c8aaed251afa734b1a4d88f85cd546b11acde` | `daa8690d7feb584548f936cc5ba527bbd336abc1` | `9e71460e2d5f1e4e2993819f4d9fa27c076946f1` |
| 07/13 parent DMA-mask handling | `48606cc39c15c5f2860c355e6150c5e392e5bda9` | `ae0e9e35728990ed01d129760093be4178c62514` | `a2b127d41c7133ea30721a72eca01333334844f7` |

Upstream patch Message-IDs follow `20260926-vpu_iommu_iova_handling-v5-{1,4,5,6,7}-0322ca5dc10c@oss.qualcomm.com`. **Imported patch delta:** stable patch-IDs match for all five; dependency/base and commit metadata differ, but the imported patches themselves are not modified. Separate **local adaptations and test/CI history** were replayed without changing source trees:

| Original local commit | Replayed local commit |
| --- | --- |
| `15aba70eea178a43bb1fbfaa71752931b9eecd0e` | `8277dd0d08803ae4094ddf189accd4c4387046ce` |
| `93ed9eb2121aea871eee01f91a3d2f891968a3ba` | `d2985559f1845c90aa95b2014668c41f317ceb6a` |
| `4cefd67d32950408f88835325a0c9215427169ea` | `a236abbdef3d3ef72caf4ca9f219711755c05707` |
| `dc244b1bd2c6f98b4eb4282b9c342ac992e906a3` | `eeb2728256fd60a051ae10be6683740d33b99350` |
| `fa89904487d4a465eb6df3f14db123d553be9502` | `951f4e546aeef6324cc4ab920cc7c59afa53ac34` |
| `89884d534f0c2429f6880153856aa19c09f7cce0` | `fd2f8dd371dbf7486cbdac4d940b6f9b179df693` |
| `f9c74e06d86672f9b85086f711702966f68d730d` | `e5990904a249b9088c0e3458b21faf131c92f3c3` |
| `ec9a8949cfbd1b05cf01553bffc39719ee1a16a7` | `f8d742ff240f44ea150a90b24002d41703c66948` |

**Exact final Git tree SHA on both branches:** `e311baf147a4d7e28dbb1075773ef20ab9441d59`. This was checked in the reconstruction job and independently confirmed using the two GitHub Git-commit tree objects. Since **kernel source is tree-identical**, reuse the earlier complete ARM64 Image/modules/modpost Iris module build at `fa899044` without rerunning it for metadata-only history changes. The build did *not* execute on the corrected history itself.

### Executed production-function validation

Test-only branch [`razr/vpu-closure-tests@816b6e07e3dc66d164d271ee20f385bd3fb1bd58`](https://github.com/Drzet/linux/tree/razr/vpu-closure-tests) adds narrowly scoped C host harnesses under `tests/` and GitHub workflows; it does **not** modify the production driver or IOMMU helper. [Successful production-path CI run 38486683289](https://github.com/Drzet/linux/actions/runs/38486683289), job `115601903926`, logged:

- `Iris production context-child tests: PASS`: extracted production `iris_create_cb_dev()`, `iris_init_cb_devs()`, `iris_deinit_cb_devs()`; absent legacy child nodes, individual/two child registration, failure of first or second child, reference put and unregister accounting.
- `IOMMU extracted production reservation tests: 12 cases, PASS`: compiled `of_iommu_derive_resv_regions()` unchanged under explicit OF translation and allocator mocks; nonpixel/pixel complements, optional coherent flag, zero-length, overflow, failed translation, failed range allocation, failed reservation allocation, partial valid input and overlapping/out-of-order ranges.
- `Iris production probe/unwind: 10 scenarios, PASS`: extracted actual `iris_probe()` and `iris_remove()` with mocked external acquisition and V4L2 interfaces, covering child registration and later V4L2, DMA-mask and PM failure cleanup. **These are host-mock execution tests, not native oneli or complete kernel probing.**

**Inherited upstream limitations observed, not repaired:** failure to translate or parse a range can terminate parsing after partially collecting valid entries; zero-length, overflow and allocation failures can be silently skipped; when no ranges survive, the function may emit **no reserved regions**. Missing reservations on error are not equivalent to rejecting a malformed DT and cannot establish fail-closed DMA. Host translation mocks do not validate all real OF cell/parent translations, bus notifier setup, physical SMMU allocator or runtime platform_device semantics. The production Iris SM8475 probe remains explicitly disabled with `-EOPNOTSUPP`, so these host paths cannot imply hardware VPU2 decode works.

**Coordinator-accepted scoped offline deliverable:** source attribution, exact mbox pin, complete old/new SHA map, identical final source tree, and executable error-path tests are available for coordinator review. No accepted integration, Boot-owned board/SoC DTS, userspace or hardware behavior has been changed. Coordinator must decide if the **upstream-inherited malformed-range/allocation limitations** warrant a separate reviewed task before integration. Do not autonomously enable SM8475, modify resource policy or open new implementation streams.

## Coordinator consolidation and branch disposition — 2026-10-14

Coordinator independently inspected the successful jobs 115601903926 and 115602051003, checked original author/trailers in the reconstructed commits, and compared all thirteen old/new Git trees locally: every pair matches. The three unchanged host harnesses were executed locally against corrected f8d742ff: child lifecycle PASS, 12 range cases PASS, 10 probe/unwind scenarios PASS. Source mbox hashes remain CI-reported; no independent mbox download is claimed.

Canonical candidate is now `a1f0288d7c3d8d51fc53398d0ffe6bcdff8a54ac` on `razr/vpu-provenance-v5`: three existing test scripts and their read-only host workflow were consolidated from 816b6e07; validation branch filters now follow this candidate. Production drivers/bindings are unchanged from f8d742ff/ec9a8949. No reconstruction script or write-enabled history-generation workflow was imported. Commit skips duplicate CI because the unchanged tests were just executed locally and existing schema/full-build inputs are unchanged.

| Kernel branch | Role after review |
| --- | --- |
| `razr/vpu-provenance-v5` | Sole canonical disabled candidate; includes reviewed host tests; paused |
| `razr/vpu-upstream` at ec9a8949 | Frozen original build/schema evidence; incorrect historical authorship superseded |
| `razr/vpu-closure-tests` at 816b6e07 | Historical execution/reconstruction evidence; do not develop or rerun provenance publishing |
| `razr/vpu-provenance-closure` at 228e7406 | Historical metadata-capture scaffold based on 869cf4; not a complete driver candidate |
| `razr/vpu` / prototype archive at a6327db1 | Superseded bespoke prototype; frozen |

No branch reset or force-push was needed. Earlier CI failures were followed by passing closure runs; they do not establish branch corruption or concurrent writers. Accepted integration remains 2b5acf10. Original records remain in Git history; duplicated closure prose was removed from this handoff.
