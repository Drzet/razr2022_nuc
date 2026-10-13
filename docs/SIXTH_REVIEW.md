> Historical review. Current STATUS.md and NEXT_TASKS.md supersede all work instructions below.

# Sixth coordinator review — 2026-10-12

**Accepted milestone: the combined project kernel builds, and that exact Image boots Debian ARM64 under QEMU virt with a real matching module load.** Coordinator promoted the unchanged tested commit `2b5acf108ae37040ac1e652e029bb37f5609e886` to `Drzet/linux:razr/integration`. This is build/QEMU acceptance, not native phone acceptance. Upstream baseline and subsystem branches remain unchanged.

## Reviewed heads and results

Project revisions below are immutable Drzet/razr2022_nuc commits. [NEXT_TASKS.md](NEXT_TASKS.md) replaces the previous queue with staged work.

| Owner | Project head | Result |
| --- | --- | --- |
| Boot | `8f1ed3dac1315852eaba95d3b855000130adb909` | Combined source replay, configuration and complete binary/module producer contract |
| Userspace | `cdd1659ce1d2704fe04d8fb26474fbb463bd4c90` | Boot-v2 alignment, actual adapter/preflight, matching initramfs and complete project-kernel QEMU pass |
| VPU | `dadd330c3f09f715372da94091f04166f9f0c141` | Durable derived evidence, omitted fields closed, qualified loader bounds; remaining DMA/OPP/ICC design holds identified |
| GPU | `dd0eabe4864b657963def1ba3086d473e9bfcc5e` | Compiled stock power data and exact 12-row HFI table correspondence; combined source/build checked |
| Power | `1013ef56961716e6afb93321036c300a9f62cbf9` | PVT fragment48 closure and concrete GLINK/BQ write-path audit; integrated source identity checked |

USB and DisplayPort have no new submissions in this round; their fifth-review results stand.

## Combined build: independently accepted

[Kernel run 38292394177](https://github.com/Drzet/linux/actions/runs/38292394177), job **114955339003**, tested `2b5acf108ae37040ac1e652e029bb37f5609e886`, completed successfully. Coordinator inspected the source compare, workflow failure propagation, logs and downloaded artifact, rather than relying on the handoff. Boot's handoff's pending-build paragraph and Power's unaccepted-build statement are now superseded.

The diff from Boot `525b504b82dbca593a9a697af9be63f53915e0a3` is eight commits: two GPU patches, five isolated Power commits and the combined workflow. Only the intended seven source files plus that workflow changed. No Iris/PS5169/optional UBWC series was imported. The original→replayed SHAs are retained in [the accepted manifest](../configs/accepted-integration-2026-10-12.json). Board peripheral enablement was not added.

- Full ARM64 Image/modules and ordinary MODPOST passed. The seven known PHY-reference warnings remain categorized as deferred feature inputs, not demonstrated UART/initramfs blockers.
- Direct applicable DT validation emitted no diagnostics. Independent compiled-FDT audit: 898 nodes, 39 reserved regions, zero overlaps, 889 decoded references, zero decode errors, 13 GPU OPPs and seven already-reviewed active-to-disabled clock references.
- Kernel release: **7.3.0-rc6-g2b5acf108ae3**. **1,702 installed modules**, no archive symlinks. The hidden `.config` is included alongside `kernel.config`.
- Coordinator downloaded artifact **11768562884**, verified ZIP SHA256 `bc9ae13983e7aa3161df1cade037929ebd71144e27f4d19204dd0bf50c88f06e`, then archive SHA256 `5338b42efa668b8755c5cff7d12ef9d1ede46106c3abe17cf30118030c009896`, and **all 1,735 SHA256SUMS entries** after extraction. Actual Image, DTB, Module.symvers, modules and logs are present.

## Project-kernel QEMU: independently accepted

[Userspace run 38297826535](https://github.com/Drzet/razr2022_nuc/actions/runs/38297826535), job **114973102362**, tested project scripts `afe416c477069659c7943f7de4b4f2fe9af39fa3`. Coordinator downloaded evidence artifact **11768979982**, verified ZIP SHA256 `6a30943b97da12f3d8a0b6aeb42ff36fa68f2f731ea0a72531d3d2b3b8148b04`, and inspected the guest logs and validation report.

- The pinned combined Image, verified Debian rootfs and a freshly generated matching initramfs passed real bundle preflight and final static validation of 1,702 module entries.
- Serial identifies Linux **7.3.0-rc6-g2b5acf108ae3**, then the ARM64/systemd success marker. The saved QEMU command uses virt-generated DT and the staged project Image, not oneli DT or a substitute Debian kernel.
- Authenticated SSH records systemd as PID1, IPv4 **10.0.2.15/24** and the network/SSH marker. Only a connected route is shown; external internet is not claimed.
- The source-enforced project check compares `uname -r`, executes `modprobe dummy`, checks `/proc/modules` and produces the recorded **RAZR_PROJECT_MODULE_LOAD_PASS**.
- Guest serial reaches **reboot: Power down**; QEMU exit code is **0** and boot/SSH status files are passed. A shutdown bus warning is visible but does not negate the independently observed orderly poweroff.

Earlier failures 38297069603 and 38297375653 were harness path/ownership errors. They remain failures; corrected run 38297826535 is the accepted complete pass. No unchanged rerun is required.

## Subsystem evidence and remaining blockers

**VPU:** coordinator checked focused export run 38291543595 and corrected loader run 38292192600, verified the committed focused JSON hash `f1bb6f41036aeb2e04ac289cfa803aab686cf92097a77444c9ed50c96397fe48` and decompressed retained JSON hash `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`. Missing GPU/PVT/header fields are no longer extraction tasks. The new boot header provides packed OS version **402653593**, zero reserved words, empty cmdline and a **4096-byte signature section** with a recorded hash; none proves acceptance of a modified image.

The coordinator independently inspected upstream arm-smmu source: the second cell enters the SMR match mask, and a single device's stream matches attach to one context bank. Two SID entries therefore do not themselves recreate the vendor pixel/bitstream domains. This is now an architecture/allocator question, not a request for another firmware search. Clock-parent topology narrows the fourth-clock question; required power corners and DDR/LLCC dynamic policy remain unresolved. Iris stays excluded from integration.

Host loader metadata reports VPU 7 MiB load span and ZAP 4 KiB within the 8 KiB stock carveout. ZAP's pinned host-loader path requires `.mdt` and `.b01`; hash metadata is packed in MDT. Secure authentication/HFI execution remain untested.

**GPU:** coordinator inspected metadata run 38297688741 and independently replayed the checker against local pinned baseline HFI source and hash-verified focused/loader metadata. Both 13×7 property tables, all **12×3 HFI encoded words**, and ZAP split/bounds checks pass. This establishes the numerical correspondence, not correct runtime selection. Dynamic nonzero bandwidth selection and six per-GPU CX floors remain unresolved; no speculative vote patch is accepted. GPU stays disabled.

**Power:** coordinator inspected the raw PVT focused dictionary: fragment48 contains exactly zero-length **regulator-boot-on**. It neither changes voltage nor identifies the physical regulator input parent. S10B/L2B/L8C source ranges and consumer references are no longer waiting for extraction. GLINK's reporting path still sends protocol requests; BQ27426 probe can perform configuration writes with suitable battery metadata, and Motorola family code also writes gauge configuration. Read-only sysfs is not a no-write implementation. Active charging/thermal/dual-pack policy remains excluded. The signed-temperature patch's combined build is now accepted; no new Power driver is needed for the next milestone.

## Next milestone and scheduling decision

**Prepare and host-validate an initramfs-only native early-boot image path using the accepted kernel.** This must establish exact payload/DT/ramdisk/header handling and an explicit diagnostic-output contract. It does not require UFS rootfs, GPU/VPU, USB3, DP or charging enablement.

Run Boot first for the small native payload interface, then Userspace for the diagnostic initramfs; their independent implementation work may overlap after that agreement. A separate bounded VPU DMA design task is optional and must not block them. Pause GPU, Power, USB and DP implementation for this milestone; do not launch another all-agent audit round. Existing USB tasks remain queued, not cancelled.

Hardware-only gates are actual bootloader selection/acceptance, usable phone diagnostics, secure firmware authentication, DMA/HFI/decode/rendering, USB/DP links and electrical/charging behavior. Do not describe the new QEMU pass as solving any of them. Unlock is an owner-managed future step, not an offline coding blocker.
