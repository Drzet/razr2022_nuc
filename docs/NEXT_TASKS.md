# Second review: next assignments and concurrency

Reviewed 2026-10-11 after the second subsystem round. This supersedes the task queue in [the first review](FIRST_REVIEW.md). The phone is unavailable. No hardware success is claimed. Read this file from coordinator **main**, even when working on an older subsystem branch.

## Independently checked outcomes

The coordinator inspected branch source/diffs and completed GitHub run/job records. Boot, GPU and Userspace job logs were also inspected to establish scope/failure causes. Reports of source-level hardware findings remain qualified as in the originating handoffs.

| Owner | Reviewed kernel / project head | Outcome and limitation |
| --- | --- | --- |
| Boot | kernel `3825dc6afb0f5e102845b32811ce0f518c0b4bbf`; coordinator main `7bdf284` | UART QUP parent and interconnect fix committed; disabled UFS rail candidates staged. [Run 38164785277](https://github.com/Drzet/linux/actions/runs/38164785277) completed successfully, including oneli DTB compilation. Schema checks select **only ARM/qcom and SM8450 TLMM**; they do not establish correctness of the new regulator, UFS or other nodes. |
| GPU | kernel `4955f07a94ea3c51e423e34d819ac3f76f1c9d37`; project `c066afb` | Compiled temporary OPP fixture passed per [record](https://github.com/Drzet/razr2022_nuc/blob/c066afb/tests/results/2026-10-11-gpu-opp-fixture.md). Actual Boot tree does not yet contain it. [Module run 38164004265](https://github.com/Drzet/razr2022_nuc/actions/runs/38164004265) **failed**: missing Module.symvers and unresolved DRM/kernel symbols in isolated M= build. This is not evidence that the chip-ID edit is incorrect. |
| USB | kernel `6ab3f710b2c8e9a455bc356673ca67293ad4d322`; project `17e97a7` | PHY binding CI passed. Repeater tuning, enable/reset and rail gaps documented. No USB driver or board enablement yet. |
| VPU | kernel `9bc913217b9051f515970c4b65770efb3374e33a`; project `056f2a459bf1505e08be12ccf9a5ae0d23a1698e` | Five-commit RFC profile/binding exists. [Run 38165380924](https://github.com/Drzet/razr2022_nuc/actions/runs/38165380924) passed host audit and candidate compile/schema jobs. Isolated module build uses KBUILD_MODPOST_WARN=1, so full dependency-resolved module validation is still absent. No firmware downloaded. |
| Power | kernel remains `cb9105e`; reports/script in coordinator main | Rail and protocol audit delivered; Boot has staged disabled rail subset. Six synthetic tests are not execution of the real kernel parser. Full checked-in source-comparison CLI run is not recorded. |
| DisplayPort | kernel remains baseline `a5ebb7623`; report in coordinator main | Vendor software AUX truth table identified; physical part identity remains unresolved. No DP driver/board implementation. Source graph assertions are not DT schema tests. |
| Userspace | project `b15c1dd292fface8928d8b70369472ac637cbe92` | [Run 38165284627](https://github.com/Drzet/razr2022_nuc/actions/runs/38165284627) built the Debian ARM64 rootfs successfully, then QEMU failed immediately: `failed to find romfile "efi-virtio.rom"`. No guest boot yet. Current package list/harness does not implement SSH/network acceptance. |

Handoff statements that these completed jobs are still pending are now stale. Keep historical handoffs intact; append exact new run results.

## Work allocation: no whole agent needs to wait

| Agent | Work that starts immediately | Gate only for the dependent step |
| --- | --- | --- |
| Boot | Broader oneli schema checks, flattened-memory audit, adoption of reviewed disabled GPU OPP proposal | Power evidence before active rail enablement; VPU firmware inventory before stock-specific boot packaging; USB/DP driver/binding contract before their board enablement |
| GPU | Repair module CI; close profile/CX-vote audit | Boot's committed OPP change before validating integrated board; VPU inventory for stock ZAP hashes |
| USB | Compile/repair PS5169 candidate, investigate repeater support, define USB2-first DT contract | Power rail contract and repeater evidence before active board enablement; Boot for shared DT commit |
| VPU | Full module build, schema/driver contract audit, hosted firmware acquisition | Boot only for combined disabled-node DT validation; hardware only for runtime firmware/decode |
| Power | Reproduce source comparison, assess concrete GLINK code defects, rail-parent audit | Firmware/board evidence for unresolved physical mapping; device only for electrical/charging validation |
| DisplayPort | Reproducible routing checks, narrow AUX binding investigation, agreement on graph contract | USB connector/PS5169 implementation and valid AUX compatible before final board graph enablement |
| Userspace | Fix QEMU startup and tar ownership; add networking/SSH smoke test | Exact Boot kernel/modules/boot contract only for native oneli image integration |

**Critical dependency chains:** Power/USB proposals → Boot shared DT; GPU OPP proposal → Boot committed DT → integrated GPU check; USB Type-C/PS5169 + AUX binding → Boot DP graph. VPU and Userspace build work run alongside these. A draft contract can be agreed before another agent's implementation is complete.

## Boot — current priority

1. Broaden validation of the **oneli DTB** to all applicable schemas, particularly RPMh regulator providers and UFS PHY/host. Current workflow runs broad dtbs_check over the tree but filters schemas to ARM/TLMM; optimize it to validate the actual target without losing schema coverage. Inspect diagnostics, not only the make exit status; separate inherited baseline issues from newly introduced ones.
2. Extract reserved-memory and supply/clock/power-domain phandles from the compiled FDT. Turn the textual zero-overlap result into a reproducible check of the actual artifact, including enabled ancestors and disabled consumers.
3. Review and apply the GPU OPP replacement from [GPU issue #4](https://github.com/Drzet/razr2022_nuc/issues/4) and [pinned GPU handoff](https://github.com/Drzet/razr2022_nuc/blob/c066afb/docs/handoffs/gpu-2026-10-11.md), keeping GPU disabled. Run the GPU owner's check against the **committed** DTB. Module compilation and OPP static integration need not wait on one another; successful OPP transcription does not resolve CX-vote or runtime correctness.
4. Request a concrete USB2-first node proposal and updated Power rail contract. Keep source-uncertain consumers disabled. Do not duplicate firmware downloading: consume the VPU-owned manifest. Boot owns stock boot/vendor_boot/DTBO analysis and image-packaging parameters once supplied.

Acceptance: exact new SHA, all-applicable target schema report, flattened-memory/phandle report, committed disabled OPP candidate with thirteen-entry check. Do not enable UFS from vendor initial voltages alone.

## GPU — current priority

1. Fix module CI using a dependency-complete in-tree kernel/modules build with normal modpost errors. Retain .config, Module.symvers, module output, commands and hashes. Do not copy VPU's unresolved-symbol warning workaround as an acceptance gate. Correct artifact paths to match the selected build mode.
2. Supply Boot an exact reviewable OPP change and run the existing checker against Boot's resulting SHA. Keep this distinct from the already-passed disposable fixture.
3. Close the source-level CX/GMU/RPMh vote mapping and revision-quirk comparison. Identify concrete remaining unsupported operations rather than repeating the broad profile-reuse hypothesis. Read the shared VPU firmware manifest when available; avoid a second multi-GB download.

Acceptance: full dependency-resolved MSM module pass and source disposition of corner/profile gaps. Hardware rendering and signed ZAP acceptance remain deferred.

## USB — current priority

1. Split USB2 debugging from USB3/DP. Deliver a Boot-ready, source-cited USB2/eUSB PHY, controller, I2C and supply proposal with unresolved repeater elements explicitly disabled. USB2 planning must not wait on PS5169 or the AUX mux.
2. Investigate the PS5169 series beyond the reported broken v3: find a corrected revision, or fix its compile failures locally while preserving attribution. Compile the candidate independently of oneli. Resolve binding representation of enable versus reset and both VCC/VIO supplies; no guessed GPIO semantics. A maintainer-corrected release is not required before doing our own attributable compile fixes.
3. Separate repeater identity from missing tuning support. Trace the three source-backed register overrides, reset sequencing and any chip-ID checks into a narrowly scoped driver/binding proposal. No PTN3222-family compatible may be asserted solely from the matching address/register map.
4. Agree with DP and Power on connector ports and GPIO91 ownership, referring to [issue #3](https://github.com/Drzet/razr2022_nuc/issues/3). Publish one versioned graph contract for Boot, not competing board edits.

Acceptance: independently compilable candidate where supportable, USB2-first proposal, and precise disposition of remaining repeater/PS5169 gaps. Actual identity reads and enumeration stay deferred.

## VPU — current priority

1. Replace the warning-tolerant isolated module gate with a complete in-tree Image/modules build. Retain full .config and populated Module.symvers; fail unresolved symbols normally. Host ABI fixtures remain useful but separate.
2. Audit the RFC schema against what the driver actually requires. It currently permits only two power domains while sm8475_data requests additional `mxc`/`mmcx` OPP domains, and operating-points-v2 is optional although the probe calls dev_pm_opp_of_add_table. Reconcile those contracts before asking Boot for a candidate node. Also justify the mandatory two-IOMMU mapping: two vendor context-bank nodes do not by themselves establish a correct single-device mainline mapping.
3. Replace or explicitly isolate SM8250-derived bandwidth, DMA, capacity and corner assumptions. Resolve UBWC initialization semantics using the actual provider path. Keep the RFC unenabled; it is not ready to represent operational VPU support.
4. **Own one shared firmware acquisition job.** Try the already identified public archive from a GitHub-hosted runner, record HTTP/DNS outcome, enforce bounded transfer/time and generate a package/member hash manifest. The chat container's DNS or binary-fetch limitation is an environment blocker, not proof the archive is unavailable from Actions. Inspect the inventory utility's DTBO bounds before treating malformed tables as valid. Supply Boot DTB/DTBO/boot metadata, GPU SQE/GMU/ZAP inventory and Power relevant source/overlay evidence. Keep binaries out of Git and do not publish proprietary firmware artifacts automatically.

Acceptance: clean dependency-resolved build, corrected schema/resource contract, and real firmware manifest or an exact hosted-download failure. Secure firmware acceptance and decode remain phone-only.

## Power — current priority

1. Execute the exact committed tools/power/glink_protocol_audit.py against both pinned original source files and retain inputs' hashes plus output. Add a small independent CI job; report source comparison and synthetic fixtures separately.
2. Investigate the reported signed-temperature conversion and header-only notification ACK differences in the real qcom_battmgr code. If a defect is established independently of an unobserved firmware assumption, prepare a narrow patch and tests that exercise the real parser/conversion behavior. The current fixtures merely pack/unpack synthetic structures; they do not demonstrate the kernel accepts them. A Motorola-specific behavior assumption stays labelled [INFERRED].
3. Give Boot a reviewed parent/consumer/voltage contract for staged UFS and proposed USB rails. Do not equate vendor initial voltage with the full allowable range. Resolve what sources establish and list the exact missing physical connections; keep charging control disabled while unsupported.

Acceptance: reproducible pinned-source pass, justified parser-fix disposition, and updated rail contract. No need to wait for Boot to perform these tasks.

## DisplayPort — bounded independent work, then a specific hold

1. Commit the 23 reported source assertions as a reproducible script/test with pinned inputs. This supplies durable evidence rather than prose counts alone.
2. Agree the connector/retimer/AUX graph and GPIO ownership with USB now. Preserve the newly found vendor software truth table; do not re-open software polarity as unknown. Physical switch identity/wiring remains separate.
3. Investigate a valid binding path for the independent AUX switch: source/BOM/stock-DT identification first; assess whether the existing generic GPIO-controlled driver/binding can support a justified extension without inventing a part. If no evidence closes this, publish a bounded blocker and stop speculative node implementation.

Acceptance: reproducible routing evidence and agreed graph contract. **Hold actual board DP enablement** until USB supplies its connector/PS5169 implementation and AUX binding identity is supportable. This hold does not require waiting to finish steps 1–3.

## Userspace — current priority

1. Fix the observed QEMU startup error (`efi-virtio.rom`). Make the emulated device/network configuration explicit and ensure required host resources exist. First obtain a real guest boot/systemd pass; the rootfs build already passed, so do not report the whole build as unstarted.
2. Fix a source-reviewed archive defect: build-userspace.sh uses tar `--owner=0 --group=0`, changing **all** rootfs archive ownership to root. Preserve original numeric UID/GID values. The ext4 image is populated directly from the source tree, so testing only that image would miss corruption of the separately exported tar. Verify ownership of representative non-root-owned files after tar extraction and compare with the source rootfs.
3. Add user provisioning, SSH server, explicit virtual-network configuration and a host-to-guest SSH command acceptance test using an ephemeral CI key. Current packages contain no SSH server and the smoke service powers off immediately after its serial sentinel; revise lifecycle so networking/SSH can actually be tested before shutdown. Record a failed boot separately from a failed SSH check.
4. Update the Boot contract with machine-readable native kernel release, matching module directory, initramfs and firmware inputs. Test generic userspace now; wait for an exact native kernel/modules artifact only for oneli integration. Keep desktop/Docker expansion behind the base boot/network/SSH milestone.

Acceptance: preserved rootfs ownership plus a completed QEMU boot/systemd/network/SSH run with artifact hashes. No dependency on phone access or completed native boot support.

## Coordination and integration gates

Work on assigned branches. Boot alone commits shared SoC/board DT. Agents update their own handoffs/result files and propose main changes; the coordinator owns aggregate STATUS/NEXT_TASKS to avoid concurrent overwrites. Never copy a stale branch-wide STATUS over main.

Kernel integration remains a separate explicit step: exact selected commits, dependency-complete build, target DT/schema results and ordered provenance. The VPU RFC is excluded from operational claims. Userspace workflow repair is independent of kernel integration. Mainline baseline remains unchanged.

Each next handoff must list: exact head, completed run conclusion, actual tested SHA (including PR test-merge SHA if applicable), artifacts/config, remaining bounded blocker, and who consumes the deliverable. Do not stop with a job still running and call the assignment validated.

Physical validation is deferred for all agents: bootloader/console, firmware authorization, rendering/decode, USB/DP signaling, charging and thermal behavior. Archive acquisition, build failures, schema coverage and graph agreement are **not** physical-hardware blockers.
