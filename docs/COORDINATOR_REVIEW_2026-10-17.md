# Coordinator delivery review — 2026-10-17 morning

## Disposition

| Owner | Reviewed delivery | Decision |
| --- | --- | --- |
| DP | Kernel d28598f544682eed5997ac9d57d423e9a5031624; project 60fbc3a3dbc28d173cc67e632f57f25d99a3e58e | AUX driver/binding accepted for isolated source/build scope; ARM64 gate closed. Project handoff needs final CI result. |
| Boot | Project 638a9d7989617783e2d2112847ca293cf08773a4; kernel 7d30153d3b2d890a42b48b6b12bcc8e9fcc7810e | Observability review and CI consolidation accepted. |
| Wireless | Project af57d1a8dc626992843079d987d49ac5338d780f; kernel unchanged at 2b5acf1 | Source transport/config contract accepted with qualifications below. |
| Power | Project b8e85bbe4936814d29ac1db770e2b286c69e9dca | Wireless supply proposal and identified L7E consumer gap accepted for development. |
| USB | Project 3c949fed4e79c8aea081a193b6fa6b9d89dbaed5; kernel PS5169 57d4d32b614cf23c2d9f60cdb06daa30870d7b61 and USB 305bc34cac710adc9fe7c4794a6e909abdf83ee0 | Scoped CI maintenance accepted; previous functional acceptance unchanged. |
| VPU | Project ac293ee4c22e4407d53f03ed55809da1b3eeddf4; kernel c31880525671f65c2d10d8d60d2ab9475c0797e4 | Scoped CI maintenance accepted; production source remains accepted 905d2403. |

Accepted integration remains **2b5acf108ae37040ac1e652e029bb37f5609e886**. No handset boot, radio operation, DP output or new integrated artifact is claimed. GPU/Userspace had no new assigned implementation delivery to accept.

## DP: previously missing build evidence now present

Coordinator inspected exact current workflow, final correction diff, Actions job results and actual host/schema/ARM64 logs for [run 38987006218](https://github.com/Drzet/linux/actions/runs/38987006218), SHA d28598f. Cheap job **117260700595** passes 11 cases / 237 assertions, binding examples and all four exact submitted schema fixtures. ARM64 job **117261174622** runs only after that gate and passes matching vmlinux provider exports, ordinary modules MODPOST/link, AArch64 module identification, vermagic and unchanged config comparison. Previous failed run 38985439713 is superseded, not erased.

The final correction checks vmlinux.symvers immediately after vmlinux and Module.symvers after modules. This closes the earlier source-traced dependency gap; no fake symvers or unresolved-symbol suppression found in the inspected workflow.

CI-reported hashes, read from the actual log:
- gpio-sbu-mux.ko: **6717c84e3d4f8f2d93a54666471181702fdd7d2f6bed32777873babe2d7b7c05**
- Module.symvers: **f46edb2a83b837e02e790a25c54ddf1fb8d46fb9eb492f28ff73617cf275e124**
- Config: **0bedc70610221d4995877520dfc57f23bec865cb7cd4696f29eaa0883970ebd3**
- Module/log artifact: **12084757955**, run 38987006218.

Coordinator did not independently rebuild or download/hash the binary. This accepts isolated software/build scope, not board power, Type-C/DP runtime or suspend. Current project handoff still ends at the obsolete Actions hold; owner must append the successful final evidence and current acceptance without another build.

## CI maintenance

Reviewed VPU and USB maintenance diffs, Boot consolidation/removal diffs and retained workflow, plus live job status:
- Boot run **38985421619**, job 117256042049: success. One compiled DTB serves preserved schema and FDT checks. Actual log inspected; no relevant schema/compiler failure observed. Prior run 38985414833 cancelled as superseded.
- VPU run **38985925553**: source detector and consolidated host job succeed; ARM64 correctly skipped for workflow-only change. Production files unchanged from 905d2403. Before/after push comparison replaces HEAD-only selection.
- USB run **38986262436**: cheap checks succeed; ARM64 correctly skipped. SNPS schema runs also succeed. Before/head detector replaces unreliable event-commit text inspection. Necessary conditional/probe assertions retained; retired import/prototype definitions do not change accepted driver code.

Existing owner local-test/hash and workflow-disable receipts remain attributed owner evidence; coordinator did not repeat unchanged suites or independently reread administrative workflow states. Automatic relevant-change builds, cheap gates and scoped cancellation remain policy. CI cleanup assignments close; do not keep expanding workflow work after its deliverable.

## Boot observability

Accept the source and metadata review. Owner reused archived stock FDT metadata and accepted compiled DTB/config, with recorded hashes; coordinator read the canonical evidence/limitations, not a fresh extraction or independent repeat of the binary parser.

Stock-reference ramoops 0xae000000 + 0x60000 and splash 0xb8000000 + 0x2b00000 are reservations, not proof of usable runtime logging or active framebuffer. Owner reports no overlap with the 39 static native reserved ranges; final RAM, runtime reservations and retention remain unknown. Accepted config has PSTORE_RAM=m, PSTORE_CONSOLE=n and no ramoops node. No usable simple-framebuffer handoff was established.

UART7 is the best evidenced first output route, conditional on accessible TX/ground and measured logic level. Physical pads remain unknown. Another demonstrated output route is acceptable. No more broad source investigation, repeated packing or blind ramoops/simplefb enablement is selected. Native entry/logs are future test outcomes, not evidence required before planning a controlled trial.

## Wireless / Power

Coordinator reviewed both current handoffs. Wireless now uses existing stock FDT metadata to corroborate transport/pins, removes the physical-ID-before-staging gate and specifies normal driver-selected firmware deployment. Stock-export inspection and Debian package inventory are owner evidence; installed hardware remains **[INFERRED]**.

Independently re-read accepted-kernel pwrseq-qcom-wcn.c and qcom,qca6390-pmu.yaml: WCN6855 uses a fixed ten-supply list, common bulk enable/disable and no explicit voltage request; optional vddasd is schema-permitted but absent from that list. Power's L7E vendor-consumer finding is consistent with the Motorola cape source previously independently inspected. A declared supply alone would not add its active management. Select a narrow existing-driver extension, subject to a focused maintained-upstream/pending-series reuse check.

Two qualifications:
1. **Voltage:** 0.500V provider initial value versus a radio request above 1V is not a hardware contradiction. The integration must encode the required active constraints/votes. Use reviewed consumer ranges and supported regulator selectors, accounting for shared consumers; do not reopen this as an identity/research blocker or blindly copy initial values. S12B common range must respect BT's 2.024V maximum as well as WLAN's range.
2. **SWCTRL GPIO82:** reserve its intended radio ownership, but do not claim the current upstream PMU actively requests/drives it. It does not. Binding describes clock-supply state and vendor behavior is input/state. No invented GPIO82 output operation.

Ten-input mapping and PMR735A parent topology remain source-supported proposals **[INFERRED]** for installed oneli. Disabled staging can record them without requiring new physical identity proof. L7E common lifetime and explicit voltage configuration precede enabled radio integration.

## Next selection

Wireless owns the sole generic driver implementation: optional property-present WCN6855 vddasd shared supply, existing common sequence, strict lookup/unwind and focused tests. Boot independently stages disabled board topology and deliberate regulator constraints using fixed Wireless/Power contracts. This bounded second implementation uses separate files and a fixed existing binding interface; enabled consumption waits for reviewed producer code.

Power pauses after accepted contract and answers only a concrete Boot/Wireless dependency. VPU RESUME remains queued behind this immediate radio integration prerequisite; its prior acceptance and user-accepted /3 assumption remain intact. DP performs only final evidence documentation. USB, GPU and Userspace pause. Full assignments: [NEXT_TASKS](NEXT_TASKS.md).


## Wireless/Boot follow-up review — 2026-10-17 afternoon

This section supersedes the morning delivery states and implementation selection above.

### Boot: accept disabled staging

Reviewed project **37dba10d18516e5f4295e637013d529314a2caa4**, kernel **5d261b415a494621c276f8a680286c66971dc57b**, canonical handoff, staging changes/checker and actual automatic [run 39026414041](https://github.com/Drzet/linux/actions/runs/39026414041), job **117378234746**. Accept disabled board/configuration scope.

The final checker confirms 20 resolved Kconfig requirements (the earlier handoff count of 19 is stale), eleven PMU supplies including ASD, regulator selector intersections, five grouped parent edges, disabled ancestry and preserved UART7. Actual FDT result: 924 nodes, 39 reserved ranges, zero overlaps, 928 phandle references, zero decode errors; seven inherited active-to-disabled references remain disclosed. No new radio enablement or native execution is established.

CI-reported DTB SHA256: **f38d0a88b2416e267fd6fa5d26b405ca5e9a0a00082586c24db7dfe8e800448c**. Artifact **12098329381**, ZIP SHA256 **a751503225d17fc65f89cda9e493ef55e957d4d452e156e6b7371e26c38e3be7**. Config hash **2b8f7de18c8142a361751652e131b46236308eb668ca7185fc33b0bc00183fdb** and 17/17 artifact-file verification are owner-reported evidence, not a coordinator rehash. Coordinator read actual CI logs and source; did not rebuild.

The corrected GPIO82 state does not invent output control. Active regulator ranges are deliberate consumer envelopes, not measured outputs. PMR735A parent mapping remains [INFERRED]; B_PLUS is not replaced with a fictional fixed supply. Before enabled integration, review GPIO80's output-low pinctrl against the existing sequencer's GPIOD_ASIS initialization and shared provider activation. This does not block acceptance of inactive staging.

### Wireless: source reviewed; CI correction required

Reviewed project **e5176e18199377d51e6782915dc27c3018ec9257**, kernel **3b674aa5c15e9334878b0241a4664f4fe88d413d**, functional delta and final workflow. Optional vddasd is WCN6855-only, appended to the per-instance bulk list when declared, acquired through existing regulator lookup and managed in the existing common sequence. Property-absent and other-variant behavior is retained. No blocking source defect identified in this delta.

Cheap job **117348778996** in [run 39016225711](https://github.com/Drzet/linux/actions/runs/39016225711) passed. The production-source harness reports 17 scenarios / 326 assertions, with regulator behavior and shared-consumer accounting mocked. It does not execute real pwrseq core lifetime accounting; this boundary is explicitly disclosed and allowed by the assignment.

**Final ARM64 job 117348898289 FAILED**, superseding the handoff's “running” status. Actual log shows successful AArch64 vmlinux, then `Missing actual built-in provider: of_parse_phandle`. The subsequent modules step did not run. Independently inspected exact source: include/linux/of.h defines of_parse_phandle as an inline wrapper calling __of_parse_phandle_with_args; drivers/of/base.c exports the latter. The workflow requires the wrong symbol. This is a CI assertion defect, not evidence of missing kernel OF support.

Assign the bounded workflow correction and completed real module/MODPOST result to Wireless. Keep production code unless a real build defect appears. No full acceptance or integrated radio artifact yet.

### Project position and next sequence

Boot staging is complete and paused. Wireless owns the sole active implementation/correction stream. Once its final link passes and is reviewed, select immutable producer/staging commits for Boot's combined enabled candidate; then provide the accepted kernel/config/modules contract to Userspace for normal Linux firmware packaging and NetworkManager/BlueZ integration. Physical radio revision is a runtime observation, not a new development gate.

DP's prior source/build acceptance, USB and VPU acceptance remain intact; DP still owes documentation closure. VPU RESUME remains queued, with the user-accepted /3 assumption preserved. Accepted integration stays **2b5acf108ae37040ac1e652e029bb37f5609e886**. No new Image/rootfs, handset boot, Wi-Fi association, Bluetooth pairing or display output is claimed. No handset operation assigned.


## Wireless final acceptance — 2026-10-17, after completed replacement build

Supersedes the earlier pending ARM64 decision. Kernel **5d191e2dd449cb226eecd7086f76fc202a6f2257** is accepted for isolated source/build scope. Coordinator inspected the exact commit diff: only the workflow provider assertion changes from inline of_parse_phandle to exported __of_parse_phandle_with_args, with explanation. Production driver and harness are unchanged from the reviewed implementation.

Independently retrieved [run 39037486109](https://github.com/Drzet/linux/actions/runs/39037486109) job results: cheap **117410138942** PASS and ARM64 **117410265783** PASS, completed 14:15:49 UTC. Actual ARM64 log contains matching vmlinux exports, ordinary modules MODPOST, linked AArch64 pwrseq-qcom-wcn.ko, successful vermagic/config checks and WCN6855_ARM64_MODPOST_PASS. No unresolved-symbol suppression or fabricated exports added.

CI-reported hashes (log inspected; coordinator did not independently rebuild/download/rehash):
- Module: **2dda988c8026ddcc58bf297020391e4444f78f8487af47b9e5bd5253d573204c**
- Module.symvers: **5802d8bb9cb077c61dcf0d7b2bdc8d32793329389156b3b312e7339f9a3d3151**
- Resolved config: **e26d4a5759494cbb51e9322c49e66bbbe7a34cf803c5137cc2845dc631cc22c1**
- Artifact: **12103078488**, wireless-arm64-39037486109.

Project head **44f57b4bed055a843e0f829bea79353ca548360b** correctly pins the new kernel and accepted Boot staging, but its final result still says pending. This is documentation closure, not a reason to repeat the passing build or block integration. Wireless updates that canonical result and pauses.

Select Boot as sole implementation owner for a combined radio development candidate from accepted Boot **5d261b415a494621c276f8a680286c66971dc57b** plus accepted Wireless **5d191e2dd449cb226eecd7086f76fc202a6f2257**, under the detailed NEXT_TASKS assignment. Review shared provider activation and GPIO startup, resolve actual module/pre-power dependencies, then one cheap-gated combined build. Userspace consumes its exact accepted artifacts afterward. No new DP/VPU/GPU integration is bundled into this task.

Accepted integration and diagnostic-v2 manifests remain unchanged until candidate review. Mocked host lifetime tests and successful compilation do not establish native kernel lifetime, firmware loading or hardware operation.


## Boot combined radio acceptance — 2026-10-17 evening

**Accept kernel 7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce for combined radio development source/build scope and Userspace consumption.** Existing packaged diagnostic-v2 release and legacy integration manifest remain unchanged.

Coordinator inspected source integration/corrections, final workflow diff, both final job logs and source PCI power-control path. [Run 39050113058](https://github.com/Drzet/linux/actions/runs/39050113058): DT/schema/config/host job **117446794445 PASS** (16:36:03–16:38:53 UTC); combined job **117447403567 PASS** (16:38:55–17:26:37 UTC). Final release **7.3.0-rc6-g7f3865ee17c3**.

Enabled radio PMU/PCIe0/PHY/UART20 paths consume the accepted optional ASD producer. GPIO80 no longer forces output-low before GPIOD_ASIS. Unrelated UFS-only L7B/L9B outputs remain disabled; shared required PHY supplies remain registered. PMR735A parent topology/installed radio identity retain [INFERRED] qualifications. UART7 preserved. The final cheap job verifies 21 config requirements, 11 PMU inputs, six grouped parent edges and host harness 17 cases/326 mocked assertions.

Actual combined log proves Image/modules ordinary MODPOST/link, vmlinux-owned exports from Module.symvers, modules_install/DEPMOD, dependency lists for pci-pwrctrl-pwrseq, ath11k_pci and hci_uart, compressed matching module archive and all 11 release manifest entries passing SHA256 verification. This closes the earlier post-build failure. Host dependency records are not kernel module execution.

CI-reported artifacts/hashes, independently read from logs but not downloaded/rehashed by coordinator:
- Combined artifact **12109240146**, ZIP SHA256 **d5ad99f03097655f03bc25b243ef2c1758b183bb49963167437750a3781a9de1**, 38,392,709 bytes.
- DT evidence artifact **12107262705**.
- Image **0a28060210e747f8c63755142935feda101df4f5d9759f4e876bc2bb1373fb2e**.
- DTB **70d5c7b08ddda1c0974ac85e95bb1328528bb533c344a0681b5e95b88cd17435**.
- Config **e10f77e9c982a4c3c81c94e69922ad8ae623b71e99df88e40c415e5a6fc0b273**.
- Module.symvers **5802d8bb9cb077c61dcf0d7b2bdc8d32793329389156b3b312e7339f9a3d3151**.
- Per-module and compressed archive digests are in the artifact manifest; Userspace must verify them on consumption.

### Why the attempts were slow

The actual workflow starts from broad ARM64 defconfig and runs make -j4 Image modules, including unrelated drivers. Final expensive job took 47m42s. This is not a narrowly selected oneli-only build.

Five integration runs are recorded: 39044250747 failed cheap Kconfig expectation (hidden PCI pre-power resolved m, not y); 39044700866 failed config equality before compilation (pahole installed in only one job); 39045013110 cancelled as superseded; 39045171934 compiled but failed an incorrect vmlinux.symvers assertion, before module packaging; 39050113058 succeeded after checking vmlinux-owned exports in actual Module.symvers. The first two mistakes were cheap-gated, but the third wasted a completed compilation. Repeating the cheap DT gate followed the workflow dependency structure; identical final-source DTB/config hashes show that final correction did not need fresh DT evidence. No additional verification run is selected.

These were validation/workflow mistakes, not demonstrated radio-source compilation defects. Future tasks must validate output contracts and tool parity before expensive jobs, reuse immutable evidence, and retain useful post-build outputs for packaging recovery where practical. Configuration reduction is a future bounded task before another necessary full kernel build, not justification to rebuild this successful release.

### Next owner and limits

Userspace is now the sole implementation stream: consume the exact build, package matching modules and standard Debian firmware/services, supply the early PCI pre-power module, validate archive/load contract and relevant QEMU userspace behavior. Native UFS/USB remain disabled; no root-device assumption or phone boot claim. No kernel rebuild.

Boot handoff at project **372fabd6a0688e2bbe08a2bb6e80bb4deb122fc2** remains stale at failed 8603c55; only documentation/readiness closure is assigned. Wireless final handoff now records its successful build and is closed. Other acceptance remains unchanged.


## Userspace radio packaging review — 2026-10-17

**Accept source 8f54a679c2aa285398e4b12a5f370b5fb7f16201 / delivery 8aedb729895bfd47f19507d9b54e43c3bae8e73e for package/archive and diskless early-module execution scope.** Coordinator read both packaging scripts and workflow, final handoff, completed job statuses and actual CI log. No blocking defect identified in this scope. No kernel was rebuilt.

[Run 39056127007](https://github.com/Drzet/razr2022_nuc/actions/runs/39056127007): cheap job **117464347990** and development job **117464371671** PASS. Exact accepted radio Image/config/module tree reused; verifier pins source/release and critical file digests, checks all 1,699 module hashes and dependency closure, and checks radio entry-point ELF/vermagic. Early initramfs contains the pre-power module and explicitly inserts it before READY. QEMU tests require actual insertion success, matching release, PID1, controlled shutdown or resident HOLD. The positive test rejects an insertion-failure marker. The HOLD test checks READY/HOLD and timeout but does not itself assert insertion success; owner reports inspecting actual HOLD log. READY alone is not proof that every mount/module succeeded.

Debian staging uses the signed existing snapshot, installs normal firmware-atheros, NetworkManager, BlueZ and diagnostics, retains full matching modules/depmod, and removes temporary interpreter/resolver/host SSH keys. Installed package versions were independently visible in CI: firmware-atheros 20250410-2, network-manager 1.52.1-1, bluez 5.82-1.1. The temporary resolver is removed; the rootfs's boot-time resolver behavior has not been tested. This is a targeted next-test item, not an asserted DNS defect.

CI upload hashes independently read from log:
- Evidence/early loader artifact **12110065036**, ZIP **1210294bd8fe51e43e88b2f2d12be44cda333b2adf092cf1a8c725327f98d72b**.
- Rootfs artifact **12109815613**, ZIP **74d4948115beff682e38b918854ab62cce756358998839cf63ecc6b5a83b3306**.

Owner independently downloaded/verified those outputs, reports 32/32 evidence hashes, 1,699 module entries, expected firmware/service files and no embedded test credentials. Coordinator did not repeat archive downloads. Owner-reported inner hashes: rootfs tar **1cfb7b29b6502c08fc5e9d1139c98c8ef78012c5a46d5c24962646045372865b**; early cpio **42d46ffc90a8566fad1ecf9ec0a28c6befe51b158ef01100362c2015e9040e1c**; compressed early cpio **797bd16b74f195a0ed07305f88213cd41e4e5393a36dcdaeb374ba75aed0c990**.

### Scope and next decision

The successful guest runs are diskless BusyBox early-loader tests. They do not boot the newly staged Debian rootfs or exercise its systemd/NetworkManager/D-Bus/BlueZ environment. The handoff states this accurately. Select one existing-rootfs QEMU runtime smoke to close that distinct software integration gap, reusing both accepted kernel and rootfs without rebuilding either. Prior generic Debian tests used a different rootfs and do not replace this check.

This milestone supplies kernel + matching modules + signed firmware/services + an early module loader. It does not supply a demonstrated native storage path, new accepted phone boot package, phone console or working radios. UFS/USB/native root selection and physical early output remain separate. Diagnostic-v2 artifacts and accepted legacy integration remain unchanged; hardware assumptions retain [INFERRED] qualification.
