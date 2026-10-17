# BOOT handoff: seventh-round console-summary v2 one-time host refresh

## 2026-10-17 active BOOT delivery: disabled radio board/config staging

**Assignment:** [coordinator eb4444d](https://github.com/Drzet/razr2022_nuc/commit/eb4444d63fc185f7a8b23c4ba6aa8ff2e0cc90eb), `docs/NEXT_TASKS.md`. Starting project BOOT `638a9d7989617783e2d2112847ca293cf08773a4`, kernel BOOT `7d30153d3b2d890a42b48b6b12bcc8e9fcc7810e`. Accepted tested functional integration remains **`2b5acf108ae37040ac1e652e029bb37f5609e886` unchanged**. Producer inputs pinned: [Wireless source contract af57d1a](https://github.com/Drzet/razr2022_nuc/commit/af57d1a8dc626992843079d987d49ac5338d780f), [Power supply contract b8e85bb](https://github.com/Drzet/razr2022_nuc/commit/b8e85bbe4936814d29ac1db770e2b286c69e9dca). Wireless subsequently completed its *driver implementation candidate* [`3b674aa`](https://github.com/Drzet/linux/commit/3b674aa5c15e9334878b0241a4664f4fe88d413d), which is separate from this disabled-source DTS staging and **not merged into BOOT**. Wireless CI outcome/acceptance are independently gated.

### Changes and unchanged hardware state

**Kernel `Drzet/linux:razr/boot`:**

- `9d8d27bfb90a35ad593103c60a210ad7aa921a83`, formatting/description correction `d2f8f002278fe8f3999af7dc4165608277d5427f` and TLMM GPIO82 binding correction `83bade370babeda6608af5a5c29b608c547c817a`: only `arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dts`. Extend *already disabled* PM8350/C RPMh providers with S10B, S11B, S12B, S1C and variable-B_PLUS-fed BOB-C; add **disabled** PMR735A provider S2E/L7E. Connect reviewed grouped parents. Add root `qcom,wcn6855-pmu` with **ten** bulk input supplies, one **`vddasd-supply` → L7E** and ten upstream internal LDO outputs. Both PCIe0 host/PHY and WCN-compatible `wifi@0` endpoint are disabled; QUP2 wrapper, UART20 and `qcom,wcn6855-bt` are disabled. No stock GPIOs are driven and no module probes. The hypothetical `pci17cb,1103` and BT WCN compatible are **[INFERRED]**, not real oneli hardware IDs.
- `0ce8f5aba5ff233e2dacd6fe09cfc48b3f037458`, modular QMP-PHY parent correction `80af4b591bd5b251978b6e781461c05480986043`: development-only `arch/arm64/configs/razr-oneli-wireless.config`; requests PCIe/QMP, WCN pwrseq, ath11k PCI/MHI/QRTR, Bluetooth HCI UART/QCA and **BT_LE=y**. No actual Image/rootfs rebuilt. `CONFIG_PCI_PWRCTRL_PWRSEQ=m` must be **verified in resolved Kconfig**, not presumed from merely listing a hidden Kconfig symbol.
- `51b1bc2bb80be8cff1846eef24258ffca4fe7c09`, resolved PHY checker correction `1f0056f5bbaa9db93fd12e40c52ab14396d44a0e`: `scripts/razr/check-oneli-wireless-staging.py` reads the **actual compiled DTB**, checks phandle equality and all eleven WCN supply slots, five parent edges, six regulator selector envelopes, disabled ancestry (including PCIe PHY and QUP wrapper), selected radio GPIOs and unchanged UART7; also checks 19 **resolved** Kconfig symbols.
- `6b40ea433e8b8aedbfab5bf93fc9c6c8fbf21985` plus pinned-schema correction `5d261b415a494621c276f8a680286c66971dc57b`: extend already consolidated, automatically triggered `razr-oneli-dt.yml` to merge the source fragment then `olddefconfig`, compile the DTB **once**, validate all binding schemas/FDT, and run the focused stage/selector/config checker. Keep workflow/ref-scoped supersession cancellation; no duplicate FDT workflow, driver/module/Image build or firmware download.

**Proposed requested vs actually selectable voltage envelopes (µV, *not* measured outputs):**

| RPMh output | Source-supported board constraints (µV) | Pinned driver's selector intersection (µV) | Other consumers |
| --- | --- | --- | --- |
| PM8350 S10B | 1800000..1800000 | 1800000 | WLAN/BT IO, PTN3222, PS5169 |
| PM8350 S11B | 966000..1170000 | 968000..1168000 (8mV step) | shared digital/AON, L5B parent |
| PM8350 S12B | **1350000..2024000** | 1352000..2024000 (8mV step) | WLAN/BT RF and L9B/L10B parent, BT's 2.024V max honoured |
| PM8350C S1C | 1900000..2024000 | 1904000..2016000 (16mV step) | WLAN/BT RF, L8C parent shared with PS5169 |
| PMR735A S2E | **1012000..1040000** | 1012000..1040000 (4mV step) | WLAN PMU MX. **Vendor 0.500V initial is NOT an active consumer vote** |
| PMR735A L7E | 2800000..2800000 | 2800000 (8mV step) | shared Wi-Fi antenna switch / Bluetooth ASD; optional FM [INFERRED] |

Per pinned `drivers/regulator/of_regulator.c`, populated min/max DT fields set `constraints->apply_uV`; these are *deliberate regulator-core startup requests when providers eventually probe*, rather than copying ineffective vendor initial values. No board runtime voltage has been measured. The existing RPMh driver has appropriate selector intersections; the board's **disabled** providers cannot apply these requests now. Later enabled integration must still validate actual votes, shared consumers, provider dependencies, PMIC headroom and runtime sleep policy.

**Source/caveat ledger:** PM8350 L2/L7←PM8350C BOB, L3/L5←PM8350 S11B (not HDK BOB), L6/L9/L10←PM8350 S12B, PM8350C L2/L8←PM8350C S1C are from inspected Motorola oneli rev03 schematic evidence; **PMR735A L7E←PM8350C BOB is [INFERRED] from SM8450 HDK**. Motorola reference PMR735A buck inputs were not physically verified; PM8350/8350C buck and BOB high-side source is **variable B_PLUS**, deliberately left without an invented fixed-voltage regulator or fabricated phandle. Existing L5B/L7B/L9B/L10C UFS nodes remain disabled and preserve consumers. PCIe0 upstream host already owns PERST94/CLKREQ95/WAKE96, and UART20 uses inherited QUP20 TLMM76–79 mux. One PMU node owns GPIO80 WLAN_EN, 81 BT_EN, 204 XO, with SWCTRL82 *status/input* only; no separate second owner or invented output. Existing UART7/`serial0:115200n8`, GLINK GPIO91, USB/DP GPIO19/2/71 are unchanged.

**Validation:** automatic oneli schema/FDT/config workflow still compiles DTB **once**. First complete run [39025973401](https://github.com/Drzet/linux/actions/runs/39025973401) verified all six selector grids and supply/phandle/FDT assertions, but failed two focused checks: Qualcomm TLMM schema disallows generic `input-enable` on GPIO82, and built-in PCIe PHY was requested under modular `PHY_QCOM_QMP`; both diagnosed from actual run logs/config, not hypothetical. Corrected source: remove the disallowed property without adding GPIO82 output control; explicitly retain `PHY_QCOM_QMP=m` and `PHY_QCOM_QMP_PCIE=m` and assert both. [Final automatic CI run 39026414041](https://github.com/Drzet/linux/actions/runs/39026414041) at exact BOOT kernel `5d261b415a494621c276f8a680286c66971dc57b` is **pending**, using pinned dtschema `2026.9`; older runs cancelled as superseded. No pass claimed until complete. Previous run's exact config, tool versions and logs are retained in artifact `12098413685`. No ARM64 module or phone validation commissioned until Wireless optional-vddasd producer is accepted for integration.

**Stop condition:** after CI result, correct only attributable compiler/schema/config issues, write final hashes/toolchain/result here and in [machine readiness](../../configs/oneli-native-loader-readiness-v1.json), then post the exact project/kernel commit and run to [BOOT issue #12](https://github.com/Drzet/razr2022_nuc/issues/12). No radio enable, merged producer, Userspace packaging, boot candidate, broad radio research or device operation without coordinator's next decision.

---


## 2026-10-17 scoped CI consolidation (coordinator latest NEXT_TASKS)

**Kernel workflow-only change**, on `Drzet/linux:razr/boot` starting at `525b504b82dbca593a9a697af9be63f53915e0a3`:

- `30caad671e46c04613283884858183e559153662`: [`razr-oneli-dt.yml`](https://github.com/Drzet/linux/blob/razr/boot/.github/workflows/razr-oneli-dt.yml) now has workflow/ref-scoped `cancel-in-progress`, retains automatic push paths and manual dispatch, and uses **one** `CHECK_DTBS=y` make invocation to compile the exact oneli DTB and check applicable schemas. Direct `dt-validate`, pinned `check-oneli-dtb.py`, resolved DTS decompile, explicit binding docs, version evidence and SHA256SUMS still consume that same DTB. Original pinned project audit commit `c35c4249bdd6b6353446f12505a4d2c7e693a5a8` is unchanged.
- `7d30153d3b2d890a42b48b6b12bcc8e9fcc7810e`: retired duplicate [`razr-oneli-fdt.yml`](https://github.com/Drzet/linux/blob/525b504b82dbca593a9a697af9be63f53915e0a3/.github/workflows/razr-oneli-fdt.yml). Its compiled-FDT audit, kernel/config and version evidence, DTB export and 30-day artifact retention are all represented by the retained `razr-oneli-dt.yml`. The retired workflow previously duplicated the exact oneli DTB compilation, so the change reduces CI cost without removing FDT checks.
- [Automatic validation run 38985414833](https://github.com/Drzet/linux/actions/runs/38985414833) at `30caad6` was **cancelled as superseded** after the retirement commit, as intended by scoped concurrency. Its automatic successor [run 38985421619](https://github.com/Drzet/linux/actions/runs/38985421619) at exact kernel workflow-only HEAD `7d30153d3b2d890a42b48b6b12bcc8e9fcc7810e` **PASSED**, job `117256042049`. All steps succeeded: schema docs, **one** `CHECK_DTBS=y` oneli DTB compilation, direct all-applicable `dt-validate`, FDT reservations/phandle audit, DTB decompile, provenance and 30-day artifact. Artifact `12082891581`, `oneli-dt-38985421619-1` (118,634-byte GitHub-reported artifact size). This is source+compiled-DTB CI, **not** physical native boot or combined Image. No unchanged kernel Image, modules or diagnostic payload rebuilt. No manual dispatch or rerun requested.

**Project documentation-only handoff** follows the already completed [2026-10-17 early-output observability review](../oneli_native_loader_output_decision_2026-10-12.md) and does not alter its findings or the machine-readable readiness record. Original host evidence and MBM formulas are unchanged. No shared DTS edits. Boot wireless node staging is still **queued** until Wireless and Power source contracts are accepted and coordinator selects integration.

**Stop:** report this workflow maintenance to Boot issue #12; await automatic CI outcome and coordinator acceptance. No unrelated workflow changes or device operations.

---


## Latest BOOT handoff: 2026-10-17 early-output observability

**Assigned source-only task:** [coordinator `87f26ca6821b417272588901e53547e8f8ddf372`](https://github.com/Drzet/razr2022_nuc/commit/87f26ca6821b417272588901e53547e8f8ddf372) and current `NEXT_TASKS.md`, plus [Boot issue #12](https://github.com/Drzet/razr2022_nuc/issues/12). Starting source project `razr/boot@b2f9aea38b5581781e8b07aa98a85dbbeddaa237`; Motorola research `0acccb329521d91b84fdcfb4bf9d7dcc25f44a25`. **Accepted kernel is unchanged**: `Drzet/linux@2b5acf108ae37040ac1e652e029bb37f5609e886`; no added DTS, driver, config, initramfs or image. Wireless/Power source-only contracts are independent and wireless Boot integration remains queued.

**Deliverable commits/files:**
- `bd3e352b4628aa15ad9aa5980850aba491c44ac1`: [current loader/output decision](../oneli_native_loader_output_decision_2026-10-12.md), new `2026-10-17` section documenting framebuffer/splash/ramoops candidate, alternative early logs, final-FDT symbol and memory requirements, and recommendation.
- `f0b5903af62c44144cc161c6eabc7f89041c1c60`: [readiness record](../../configs/oneli-native-loader-readiness-v1.json), `early_output_observability_2026_10_17` evidence/provenance, all required qualified regions and readiness gates, preserving original accepted image/config identities and ABL placement decision.
- This canonical handoff records the completed review and stops for coordinator approval. No parallel new report or schema.

### Reused evidence; tested vs source vs unknown

**Independent extraction of existing METADATA, not stock firmware:** downloaded original VPU [six-FDT artifact 11734430639](https://github.com/Drzet/razr2022_nuc/actions/runs/38220276125/artifacts/11734430639), independently SHA256-checked `15,862,099` bytes of JSON = `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`. All **four** separate stock DTBO node indexes show `/fragment@28/__overlay__/ramoops_mem` at **`0xae000000` size `0x60000` (384KiB)** and one `splash_region` at **`0xb8000000` size `0x2b00000` (43MiB)**, with `/__fixups__/reserved_memory` targets. PVT candidate overlay index **3** SHA256 `4fd14c771ecf9f6eadd8e9e56215bcb2858beda6808ce107ae45a9ce18173aad` uses `fragment@71` for splash. Both MSM530/MSM540 stock bases export `/__symbols__/reserved_memory="/reserved-memory"` and contain firmware logs `xbl_dtlog` 0x80600000 + 0x40000 / `uefi_log` 0x808e4000 + 0x10000. Each of six standalone `/memreserve/` lists is empty. All six full node indexes have **zero simple-framebuffer nodes**. Base `/memory` remains zero-size before runtime fixup. No original FDT bytes or final composed selected board were claimed.

**Independent accepted compiled-DTB cross-check:** retrieved the unchanged compiled native oneli DTB from artifact `11768562884`, verified SHA256 `d3c9abcea9950200babbcf6c979073dc94c6af5cac68578540ad570db4a14a03`, and parsed its actual FDT token structure: **898 nodes, 39 direct statically located `/reserved-memory` ranges, zero overlaps with the stock ramoops/splash candidate intervals, zero ramoops/simple-framebuffer nodes**. No recompilation, overlay apply or device test. Nearest existing static reservations are `[0xa6f00000,0xa7000000)` and `[0xbb000000,0xc0000000)`. This does not verify usable DRAM, runtime-reserved regions or the chosen FDT.

**Pinned Motorola source corroboration:** [`cape-moto-common-overlay.dtsi`](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-common-overlay.dtsi) uses fixed **384KiB no-map ramoops with console-size 256KiB and record-size 128KiB**, plus a separate 4KiB annotation immediately below at 0xadfff000. [`cape-moto-common-base.dtsi`](https://github.com/MotorolaMobilityLLC/kernel-devicetree/blob/90fa7be1db5bd47202673d4431408659149a7359/qcom/cape-moto-common-base.dtsi) deletes the original dynamic 2MiB Cape `ramoops_region` with pmsg, so do not transfer its old `mem-type`/pmsg policy. Output format `width/height/stride/pixel format`, actual scanout buffer and handoff, ramoops power-cycle retention, PVT overlay choice and working `/sys/fs/pstore` readback are **not** supplied by these source/JSON records. Stock splash is a **reservation**, not `simplefb`. XBL/UEFI buffers and RTB are **firmware/vendor storage**, not evidenced as reusable Linux log consoles. Memory locations are exact *reference overlay* addresses but not approved RAM on the installed device. Mainline has 39 statically audited reservations and no static overlap with candidates; dynamic/running memory/ABL allocations remain untested.

**Independently inspected accepted generated `kernel.config`** from immutable kernel bundle artifact **11768562884**, SHA256 `c86c04cc707889c66f8e4a485d1bff70819c1747150cb211836f07efb9fff90e`:
- **UART:** `CONFIG_SERIAL_EARLYCON=y`, `CONFIG_SERIAL_QCOM_GENI=y`, `CONFIG_SERIAL_QCOM_GENI_CONSOLE=y`, `/chosen/stdout-path=serial0:115200n8` and configured QUP0/UART7 on the accepted oneli DTS.
- **Pstore:** `CONFIG_PSTORE=y` but **`CONFIG_PSTORE_RAM=m`** and **`CONFIG_PSTORE_CONSOLE=n`** (also `PSTORE_PMSG=n`). There is **no fixed ramoops node in the accepted native DTB**. Thus no immediately usable early or persistent console recorder, notwithstanding stock address evidence and `CONFIG_EFI_VARS_PSTORE=y`.
- **Display:** `CONFIG_FB_EFI=y` and `CONFIG_FRAMEBUFFER_CONSOLE=y` but `CONFIG_SYSFB_SIMPLEFB=n`, `CONFIG_FB_SIMPLE=n`, `CONFIG_DRM_SIMPLEDRM=n`; no attributable GOP handoff, display scanout register state or `/chosen/framebuffer@...`/format/stride. DISPCC and panels are intentionally disabled for minimal boot.

**Recommendation:** **UART7 first**, if GPIO26 (reference TX/ball D24) plus ground and measured logic level are physically reachable and source bytes can be observed. GPIO27 ball C24 is RX, not proof of connector access. **Smallest useful device action is a read-only pad/access/logic-level observation during stock/MBM**, not a successful Linux boot. Alternate evidenced early output is acceptable if UART inaccessible. If no physical UART route, consider **future reviewed** in-kernel ramoops console + exact retained safe memory and later `/sys/fs/pstore` readback, after validating live selected FDT/`/reserved-memory`, RAM/carveouts, warm reset preservation and logging policy. Do **not** treat `0xb8000000` reserved splash as an active screen.

**Stop and handoff:** BOOT early-output research complete, static inputs and missing device evidence explicit. Full ABL address contract remains resolved for planning; runtime K/E/RAM/FDT/vendor-ramdisk/AVB/recovery remain unmeasured. No on-device test/flash, new firmware acquisition, disassembly, DTS/config/driver/boot candidate edits or CI build. This documentation-only task needs **no repeated build**. Post exact project head and evidence to issue #12, then stop.

---


## Current BOOT completion: 2026-10-16 ABL placement and decoder correction

**Coordinator input:** [current review `99b37f464fedca0caacc47b59fa3b2fa525ccacf`](https://github.com/Drzet/razr2022_nuc/blob/99b37f464fedca0caacc47b59fa3b2fa525ccacf/docs/COORDINATOR_REVIEW_2026-10-15.md) and current `docs/NEXT_TASKS.md`. Original BOOT head read first: `812172869a8c9665c6a39004aad9b1c52cf036bf`. Accepted kernel remains `Drzet/linux:razr/integration@2b5acf108ae37040ac1e652e029bb37f5609e886`. **This current update supersedes seventh-round statements that the actual Motorola placement algorithm was completely unknown.** Previous accepted host images and schematic evidence remain intact.

### Accepted source-backed MBM placement contract

Reference branch `research/oneli-mbm-readonly-20261015@5a8d6ab606c825dbe776db43955c44214f7c64e3`, [source-backed address report](https://github.com/Drzet/razr2022_nuc/blob/5a8d6ab606c825dbe776db43955c44214f7c64e3/docs/oneli_mbm_kernel_load_address_contract_2026-10-15.md), public bootloader member SHA256 `bcb596054b276aa3e314412e32b274be8c33b4d93dde9550f55f9a7376496ab3`, LinuxLoader PE SHA256 `5e6db9577a35ec5a5e9c848e271e13048b9ba71a47311d64f0a29b78500eb3ca`. Motorola ABL AArch64 code analysed in [run 38808611568](https://github.com/Drzet/razr2022_nuc/actions/runs/38808611568); numeric constants evidenced in [run 38809199858](https://github.com/Drzet/razr2022_nuc/actions/runs/38809199858). These are **reference-firmware static results**, not observed selected runtime values.

- Define `B=KernelBaseAddr`, `Z=KernelSize`, `M=BaseMemory`, `O=FDT base-memory offset`, `E=reserved kernel end`, `K=kernel Image start`. For accepted nonzero-size uncompressed Image, successful UEFI GetVariable pair yields `K=B+text_offset+O` and `E=B+Z+O`. Accepted Image `text_offset=0`.
- 64-bit fallback on unsuccessful UEFI query: `K=(M|0x80000)+O` (**OR**, not add); `E=M+0x06400000+O`.
- With `P=boot page size`, `R=selected total ramdisk bytes` and `S=FDT devicetree_space_size` (default 2MiB), `initrd=E-align_up(R,P)-P`, `dtb=initrd-S-P`. ABL's check `dtb>K` is weaker than the necessary Linux nonoverlap `dtb>=K+Image.image_size`.
- With our Image `image_size=0x32c0000` and default `P=4096`, `S=2MiB`, verify `E-K >= 0x34c2000+align_up(R,4096)`. If `M` were 2MiB aligned and `O=0`, fallback has 99.5MiB capacity but `K=M|0x80000` is **not** a valid 2MiB-aligned Image entry. Do not infer a real collision, success or chosen branch.
- Reference code includes unlocked-guarded downloaded `fastboot boot` handling and unlocked AVB continuation; actual temporary boot/vendor_boot/FDT composition has **not** been tested. Literal public v4 header addresses no longer define the loader's computed physical positions. Runtime B/Z/M/O, memory fixup, selected FDT/DTBO, ramdisk/bootargs, output and recovery remain unobserved.

### Repaired research evidence tool and focused validation

**Research branch correction commits:**
- `10d18f1c51d56c70b7b081ef738cdff2f506fa53`: fix aligned UTF-16LE terminator scanning and section-validated PE RVA→raw-offset mapping in `scripts/analyze-oneli-mbm-placement-constants.py`.
- `59c9c875ef809c2659ab9d4c292573fc44c084f2`: `tests/test_oneli_mbm_placement_constants.py`, 12 synthetic checks, including both full UEFI strings, nonidentity RVAs and bounds failures.
- `0acccb329521d91b84fdcfb4bf9d7dcc25f44a25`: lightweight isolated CI workflow, **without** a stock firmware download/disassembly. [Run 38830120757](https://github.com/Drzet/razr2022_nuc/actions/runs/38830120757), job 116746730360 **PASS: 12/12** and Python compilation.

Independent offline re-read of [existing PE metadata artifact 12007666834](https://github.com/Drzet/razr2022_nuc/actions/runs/38808611568) verified sections `.text` RVA `0x1000` / file offset `0x1000`, raw span to `0xf0000`; `.data` 0xf0000..0x109000; `.reloc` 0x109000..0x10a000. All 11 referenced metadata RVAs (four numeric fallback values, six strings and one GUID) fall inside identity-mapped, raw-backed `.text`. Numeric values remain unchanged. Previously printed `KernelBaseAdd`/`KernelSiz` are an extractor defect; correct decoder tests `KernelBaseAddr`/`KernelSize` on **synthetic** UTF-16LE, not fresh proprietary bytes. Source recompile/synthetic pass does not constitute independent rerun of the binary extractor. Existing firmware acquisition is not repeated.

**Updated BOOT records:** [loader/output decision](../oneli_native_loader_output_decision_2026-10-12.md), doc commit `f2dd8bbba75fc292ea27c9de7f57651825bb013a`; [machine readiness](../../configs/oneli-native-loader-readiness-v1.json), current data commit `45f1129c9ffc9713ec9e335f10c80db22a5bf3e7`. Both preserve the kernel Image/DTB and diagnostic-v2 artifact hashes; the old speculative header-address overlap is retained *only* as a rejected historical hypothetical.

### Read-only physical observations and bounded conditional experiment

Before any phone operation, verify actual bootloader/version/lock state, both-slot flags and source-matched original per-slot image hashes, credible independent recovery, physical UART GPIO26 TX pad+ground+voltage or alternate observable early output. Obtain whichever selected UEFI/fallback memory inputs are visible; a native test may be required to observe the rest. For any selected address set, check 2MiB Image alignment, **full 53,215,232-byte** reservation, downstream DTB/ramdisk allocations, real physical RAM/carveouts, FDT memory and initrd window. The oneli mainline DTB still starts with RAM size zero.

Only if a coherent restore/output route and actual unlocked temporary boot contract are established, coordinator may authorize a *separate* non-flashing RAM-only trial. Before claiming valid replacement, determine whether Motorola ABL retains original vendor_boot/DTB/DTBO and how generic/vendor ramdisk and bootargs are combined. **Actual kernel entry and diagnostic bytes are measured results**, not mandatory prior achievements. No `fastboot` command is provided or executed, no flash, unlock, modem, kernel, DTS, combined build or boot image altered here.

**BOOT stop:** source placement contract incorporated; static literal-tool regression closed; runtime-selected values and safe observer/recovery path remain device tests. Submit exact research and BOOT commits to issue #13 and **pause** for coordinator acceptance. VPU's policy task is separate.

---


- **Date / chat:** 2026-10-12, BOOT continuation of seventh coordinator review.
- **Source branch:** `Drzet/razr2022_nuc:razr/boot`.
- **Exact tested packaging source:** `0b2ee0709987831ede07a1494117c7abd3485075`.
- **Accepted kernel and DT unchanged:** `Drzet/linux:razr/integration@2b5acf108ae37040ac1e652e029bb37f5609e886`, `Image` SHA256 `3a8fa9620e0fc8de68ce8db45dacdfd811a2ba2c9718f9cddee3893ec9af0939`, mainline oneli DTB SHA256 `d3c9abcea9950200babbcf6c979073dc94c6af5cac68578540ad570db4a14a03`.
- **Upstream baseline:** `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- **Evidence levels:** v2 Userspace diagnostic output tested in QEMU; BOOT unsigned AOSP v4 image **host-tested**; Motorola phone hardware **not tested**.

## Changed input and source provenance

Userspace completed the independent seventh-review console-summary fix: actual diskless test [run 38317559417](https://github.com/Drzet/razr2022_nuc/actions/runs/38317559417) at exact Userspace commit `64b7a3358d3250dbe92518e548517ddfd038b149`. Its 15/15 artifact checksums pass. Downloaded Userspace v2 artifact **11777077254**: ZIP SHA256 `3625ebfdaf83edd4628791f8a818ecaea357aeabcb354b062e00911124f4ed76`. The raw cpio SHA256 `cf00eb88014e177a48164f5d70ee8ee277ebe5936a8808bf80885ae8818a408e`; gzip cpio SHA256 `ccd4c96b2cb05ff695175af8625dbbf8fe2f822d32fafaa5ae930e7796b7a93b`; embedded `/init` SHA256 `d23e8bd9662a91d9cd1b6edaa1db49ed5ec8ea6aec70f9763cddab4a6e8989e9`. Both positive and negative QEMU console logs include **one nonempty summary line between PROBE_ERRORS_BEGIN/END**. The marker `RAZR_NATIVE_PROBE_ERROR_FIXTURE_CI_ONLY` is supplied through QEMU's test command line and is **not evidence of an actual oneli probe failure**.

For this *single* changed-payload-only repackaging, BOOT added [input lock](../../configs/oneli-native-host-console-v2-input-lock.json), [bounded wrapper](../../scripts/repackage_oneli_native_console_v2.py) and [isolated CI](../../.github/workflows/boot-native-console-v2.yml). Original BOOT v1 packer blob `8221b23255489f7e94d3b267106c36db02c31df5` and accepted vendor_boot v1 remain pinned. This workflow **does not regenerate or publish vendor_boot**; the v1 file is consumed and independently SHA verified byte-for-byte against a recomputed identical vendor layout. The new generic v2 gzip only replaces the boot-v4 ramdisk section.

## Validation / exact artifact

First new run [38318193635](https://github.com/Drzet/razr2022_nuc/actions/runs/38318193635) **failed** after successful input downloads/checksums due to a wrapper bug passing a filesystem Path instead of bytes to SHA256. Corrected at BOOT commit `0b2ee0709987831ede07a1494117c7abd3485075`. Retain this failed test in history.

**Successful [BOOT run 38318260840](https://github.com/Drzet/razr2022_nuc/actions/runs/38318260840)**, job **115039980166**, checked source commit `0b2ee0709987831ede07a1494117c7abd3485075`. All CI jobs passed: pin accepted kernel+v2 payload+v1 vendor inputs; verify their hashes; check v2 `/init`, actual QEMU probe fixture and hold logs; pack only a changed boot image; inspect with BOOT parser; independently unpack/repack with pinned AOSP tools and compare section sizes/hashes, command line and signature policy. No kernel or Debian rebuild.

- Artifact **11777433748**, `oneli-native-boot-console-v2`, independently downloaded ZIP SHA256 **`c2f7353a652d60c4d3e0282dfa101ab421d1dfd605c571c509194f25b26cb00b`**, **5/5 internal SHA256SUMS passed**.
- `boot-console-v2.UNSIGNED.img`, 53,395,456 bytes, SHA256 **`1e00e4f998f5001bc08d9e0d4e4465664100194ce211cd9eb8b329612b5563bb`**. Embedded kernel identical; generic gzip changed to v2 sha `ccd4c96b2cb05ff695175af8625dbbf8fe2f822d32fafaa5ae930e7796b7a93b`. OS version field 0; no boot-v4 signature; empty cmdline; Android image structure only.
- Previous v1 `boot-candidate.UNSIGNED.img` remains accepted for its former payload and untouched: SHA256 `f47686e4cff28d9491ece814dd6c91c6f22eab32b3061a46f9bb935ae1fcda74`.
- **No new vendor_boot output.** The exact existing v1 vendor image SHA256 `1b4f6379b41e22735176bf63c725d3455d47c7b510f29d0de62b408da5f47572` remains the paired *structural* host reference. Neither v1 nor v2 is native-phone accepted or AVB signed.
- Machine output artifact includes `boot-console-v2-inspection.json`; durable [result record](../../tests/results/2026-10-12-oneli-native-console-v2-repackage.json) with all identities and distinct historical failure.

## Shared files, dependencies and next action

Only BOOT-owned project files are touched, no kernel/DT/schema/baseline edits, no `razr/integration` movement, no coordinator STATUS/NEXT_TASKS changes. Separate seventh BOOT decision report [native loader/output decision](../oneli_native_loader_output_decision_2026-10-12.md), machine [readiness record](../../configs/oneli-native-loader-readiness-v1.json) and [handoff](2026-10-12-boot-seventh-loader-output.md) establish the actual remaining oneli unknowns.

**Phone readiness remains BLOCKED:** actual Motorola bootloader Image base/relocation, bootloader-supplied RAM, DT/DTBO selection, generic/vendor ramdisk and cmdline priority, observed physical UART/early diagnostic route, AVB/rollback and independently verified reversible restoration. The *only* next physical acceptance path requires evidenced loader placement and a safe observable recovery-capable experiment; no flash command is supplied or approved. Do not repeat unchanged host image builds or generic ROM scans. Coordinator reviews these BOOT artifacts and is sole owner of any aggregate readiness change.


## Current BOOT assignment: 2026-10-15 schematic-to-board review

**Assignment:** current main `docs/NEXT_TASKS.md` at coordinator main revision `b525b6ab2bd399810d70365d048bc46cfda5f98e`. Independent source-only review while USB reviews PTN3222BUK. **No DTS, driver, kernel or artifact change**. Accepted kernel remains `Drzet/linux@2b5acf108ae37040ac1e652e029bb37f5609e886`. Reviewed exact Boot project head before this update: `3462c5e61c0defde33c49eee647064894dc5b24b`.

**Pinned, reviewable contract:** [configs/oneli-schematic-board-contract-v1.json](../../configs/oneli-schematic-board-contract-v1.json), creation commit `e7747622c90a2dce689bcb553bf258f10a7069df`. Derived input: [coordinator's schematic evidence](https://github.com/Drzet/razr2022_nuc/blob/d84b05099dd9f01e11b744503a3728ae71e70ee4/docs/oneli_schematic_evidence_2026-10-15.md), from user/auditor inspected `Schematics_256_MP_0616.pdf`, Motorola `maven.cpm` rev03. Drawing not redistributed. **Schematic-derived reference design only, exact installed PVT population and runtime unverified**. For Linux comparison: [pinned SoC DTS](https://github.com/Drzet/linux/blob/2b5acf108ae37040ac1e652e029bb37f5609e886/arch/arm64/boot/dts/qcom/sm8450.dtsi), [accepted oneli DTS](https://github.com/Drzet/linux/blob/2b5acf108ae37040ac1e652e029bb37f5609e886/arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dts), [RPMh binding](https://github.com/Drzet/linux/blob/2b5acf108ae37040ac1e652e029bb37f5609e886/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml), [driver per-rail supply names](https://github.com/Drzet/linux/blob/2b5acf108ae37040ac1e652e029bb37f5609e886/drivers/regulator/qcom-rpmh-regulator.c) and [HDK comparator](https://github.com/Drzet/linux/blob/2b5acf108ae37040ac1e652e029bb37f5609e886/arch/arm64/boot/dts/qcom/sm8450-hdk.dts).

### UART7 verdict: GPIO mux matches; source labels conflict with schematic directions

| Source | TX | RX | Functional evidence |
| --- | --- | --- | --- |
| User-transcribed reference schematic | AP **GPIO26**, ball **D24**, net `SDM_DBG_UART_TX` | AP **GPIO27**, ball **C24**, net `SDM_DBG_UART_RX` | Physical-net direction in reference drawing, not a confirmed solder-accessible pad |
| Inherited `sm8450.dtsi` pinctrl labels | `qup_uart7_tx` **gpio27** | `qup_uart7_rx` **gpio26** | **Names opposite** those signal directions |
| Accepted `uart7` / SoC TLMM | `qup7` alternate function, drive 2, bias disable **on both** pads | Same | Both GPIO26/27 are enabled for `qup7`; the group names don't program TX/RX direction, which is determined by silicon's mux role |
| Pinned Motorola `cape-pinctrl.dtsi` | `qupv3_se7_2uart`: **GPIO26/27 together**, `qup7` | No labelled pin direction | Confirms the same two-pad function, not which physical pad is a usable console receiver |

Mainline `drivers/pinctrl/qcom/pinctrl-sm8450.c` advertises `qup7` for GPIO24–27, including both reported pins. `uart7 = serial@99c000` is `qcom,geni-debug-uart`, parent QUP0 enabled, corrected QUP0 ICC links, `serial0` alias and `stdout-path=serial0:115200n8`, with built-in `CONFIG_SERIAL_QCOM_GENI=y` and `CONFIG_SERIAL_QCOM_GENI_CONSOLE=y`. **No currently demonstrated functional pinmux error.** Minimal *future* optional source clean-up: use a single oneli-local `qup7` two-pad default pinctrl state for GPIO26+27, or relabel inherited references without changing electrical configuration. Do **not** silently swap the actual pin group contents or claim UART operation. **Required device observation:** identify a real ground/pad, voltage domain and accessible UART TX receiver path; capture bytes from the controlled handoff. UART voltage/test pads remain UNKNOWN.

### RPMh regulator parent reconciliation: proposed, not applied

The driver and binding explicitly support the grouped property names below. `PM8350` means RPMh `qcom,pm8350-rpmh-regulators`, `qcom,pmic-id="b"` in accepted **disabled** `regulators-0`; `PM8350C` means `qcom,pm8350c-rpmh-regulators`, ID **c** in disabled `regulators-1`. Neither provider has parent `vdd-*-supply` inputs staged in accepted oneli DTS.

| Provider | Mainline binding property | Schematic input rail | HDK input | Decision |
| --- | --- | --- | --- | --- |
| PM8350 | `vdd-l1-l4-supply` | **S11B** | S11B | Same |
| PM8350 | `vdd-l3-l5-supply` | **S11B** | BOB | **Change source assumption** |
| PM8350 | `vdd-l2-l7-supply` | **BOB (PM8350C)** | BOB | Same |
| PM8350 | `vdd-l6-l9-l10-supply` | **S12B** | S12B | Same |
| PM8350 | `vdd-l8-supply` | **S2H** (PM8450; **not PM8350BH**) | S2H | Same |
| PM8350C | `vdd-l1-l12-supply` | **S1C** | BOB | **Change source assumption** |
| PM8350C | `vdd-l2-l8-supply` | **S1C** | BOB | **Change source assumption; L8C→S1C** |
| PM8350C | `vdd-l3-l4-l5-l7-l13-supply` | **BOB (PM8350C)** | BOB | Same |
| PM8350C | `vdd-l6-l9-l11-supply` | **BOB (PM8350C)** | BOB | Same |
| PM8350C | `vdd-l10-supply` | **S12B** | S12B | Same |
| PM8350C | `vdd-bob-supply` | **B_PLUS** | HDK `vph_pwr` (fixed 3.7V) | **Variable physical power-path; NO HDK fixed-supply copy** |

**Additional physical feeds:** PM8350 S1–S12 buck inputs and PM8350C S1–S10 buck inputs derive from `B_PLUS` in the reference drawing. Mapping requires actual regulator supply-provider ownership and cannot be replaced with `regulator-fixed` at an invented 3.7V. The BOB output `VREG_BOB` is generated by **PM8350C** and shares its variable `B_PLUS` input. The accepted oneli DTS lacks instantiated `S11B`, `S12B`, `S1C`, `S2H`, `BOB` and high-level `B_PLUS` provider phandles; **do not paste a table into DTS as if these phandles exist**.

**Consumer implications:** UFS PHY VDDA-PHY←PM8350 **L5B** now traces to **S11B** rather than HDK BOB; UFS host VCC←**L7B** traces to BOB; UFS VCCQ←**L9B** traces to S12B; PHY VDDA-PLL←PM8350C **L10C** traces to S12B. For USB and DP, the identified `PTN3222BUK` repeater gets S10B and L2B; PS5169 VCC=S10B and VIO=**L8C fed by S1C**; AUX `WAS7227Q-10/TR` VCC=L2B. Actual supply constraints and pin control belong to the separately queued USB/DP/Power agreements. **All current regulators and consumers remain disabled**.

**Battery provider/name boundary:** `PM8350BH` is the schematic main charge/bridge power-controller designation, distinct from the PM8350 (RPMh ID **b**) and PM8350C (**c**) regulator inputs, and not interchangeable with the upstream `qcom,pm8350b-rpmh-regulators` name without a part/provider audit. The user-corrected `CHG_EN` belongs to **PM8350C GPIO2 pin134**, `FLIP_BALANCE_EN_N` to **PM8350BH GPIO1 pin114**, and `FLIP_BATTPLUS_EN` to **PM8350BH GPIO3 pin139**, with R909 470kΩ pull-down and U900 WS4695C-12 bridge. **Power owner** has the queued polarity/provider/paired-pack policy task; BOOT makes no GPIO or charger DTS proposal in this round.

### Concrete next observations and stop

- **Offline source, owner Boot/Power (future assigned integration only):** decide how actual `B_PLUS` is represented without HDK's fixed `vph_pwr`, instantiate correct *disabled* PM8350/PM8350C/PM8450 RPMh producer phandles for S11B/S12B/S1C/S2H/BOB, and review cross-provider dependencies before any proposed `vdd-*-supply` patch. Check binding/schema and regulator parent/provider readiness then, not now.
- **On device, Boot/owner:** actual MBM-selected RAM map/Image load and relocation, DT/DTBO treatment (the accepted compiled DT memory remains size zero), ramdisk/command-line selection; separately physical GPIO26/27 UART output pad, voltage, accessible receiver and logs. Stock Android PVT `0xc000` plus reference schematic alone does not prove installed PCB variant or voltage/readout.
- **Test gate, Boot/device owner:** read-only bootloader capabilities and original per-slot data, credible restoration and observable diagnostic method before a separately reviewed native trial. Successful kernel entry and logs are *test outcomes*, **not pre-existing proof required to plan the trial**.

**Validation:** read-only comparison of the exact accepted SoC DTS, oneli board, pinctrl driver, RPMh binding/driver, SM8450 HDK and pinned Motorola pinmux source; grouped property names and differences checked. No changed kernel/DTS/schema source, no CI/build/QEMU replay, no physical test and no charging/power state change. Stop BOOT work here and post the exact document commit to issues #13 and #9 for coordinator review; USB's independent BUK/reset task remains active.
