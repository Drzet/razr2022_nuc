# Subsystem handoff: Debian ARM64 userspace and generic QEMU virt

- Date and originating chat: 2026-10-11, userspace subsystem, Linux on Motorola Razr 2022.
- Repository / branch: Drzet/razr2022_nuc, razr/userspace.
- Origin coordinator main: 77cad2417b4c02082a8d96fd1b55c088973afc4a (read AGENTS.md, docs/STATUS.md, docs/WORKFLOW.md and docs/NEXT_TASKS.md at this revision before edits).
- Upstream native kernel baseline SHA: a5ebb76233b79db01e82e061173cb73c6d2b5c6b, unchanged.
- Required native board support: Boot handoff recorded cb9105ebeb9485e31d044d4fa69396b415523669 at review time; newer reviewed Boot revision and board/boot artifacts are REQUIRED for real phone integration, not this generic QEMU milestone.
- Stage: research reviewed; implementation committed; CI/QEMU emulation pending first completed evidence; **hardware-tested: NO, phone unavailable**.

## Changes and provenance

The userspace branch includes:
- e78a8d824e8167bd3fdfe3986a7c297c2b9d49a6: Debian snapshot manifest and serial-sentinel QEMU smoke script.
- b60716bb03af8b08c07789dbc503d0eb3bfb14e3: cross-debootstrap ARM64 rootfs builder.
- ebc63be45cdacead87c04c5b5576378d6c46d509: dedicated .github/workflows/userspace-qemu.yml, without changing the baseline job.
- adb13940422fd29af8a94639f61812ba4051763d: correct dpkg-query format substitutions in evidence reporting.
- 4f26dfab38106951b8e59d3498de72fcd6c7edcb: docs/userspace_boot_contract.md.
- 273346890968be4c0be9914310b37b460f389d58: userspace/README.md usage and evidence boundaries.

Additional commits: 0db12829933c5a36ab69b5702537a00ee13850d4 pins/verifies Debian 13 archive signing keys; 9cc0857e040b37dc3f2c43ed3d742a058406a1d5 adds explicit GPG and wget host dependencies. The signed Debian public key assets are verified against Debian FTP-master published SHA256 digests (main 6f1d277429dd7ffedcc6f8688a7ad9a458859b1139ffa026d1eeaadcbffb0da7; security 844c07d242db37f283afab9d5531270a0550841e90f9f1a9c3bd599722b808b7) before bootstrap.\n\nPinned distribution inputs: Debian trixie, arm64; signed main and security snapshot repositories at 20261011T000000Z; SOURCE_DATE_EPOCH 1791676800; 3072 MiB disposable ext4 disk. QEMU uses distribution linux-image-arm64 (resolved package version in evidence), *not* Drzet/linux. Installed packages: systemd-sysv, udev, iproute2, kmod, ca-certificates, e2fsprogs, initramfs-tools and linux-image-arm64 plus dependency closure. Debian packages are never committed to source control.

## Shared files and integration

Owned files: userspace/inputs.env; userspace/README.md; scripts/build-userspace.sh; scripts/smoke-qemu.sh; docs/userspace_boot_contract.md; .github/workflows/userspace-qemu.yml; this handoff.

No edit to existing .github/workflows/arm64-baseline.yml, configs/baseline.json, Drzet/linux or any other subsystem branch. Proposed new CI is isolated on userspace branch and intended for coordinator review before merge. Boot retains exclusive ownership of kernel and shared DT.

For physical integration, Boot must provide exact oneli Image + DTB + native modules + initramfs dependencies, proven firmware and root storage plan, diagnostic console and packaging parameters. Do not mix the QEMU Debian test kernel/modules with Drzet/linux; do not assume an Android boot header, partition UUID, UART path or DTBO selection. See docs/userspace_boot_contract.md.

## Reproduction and validation

On an Ubuntu 24.04 host with sudo and signed Debian archive keyring:

~~~bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends debootstrap qemu-user-static binfmt-support qemu-system-arm debian-archive-keyring e2fsprogs zstd xz-utils ca-certificates gnupg wget
mkdir -p evidence
sudo env GITHUB_SHA="$(git rev-parse HEAD)" bash scripts/build-userspace.sh /tmp/razr-userspace-build "$PWD/evidence"
bash scripts/smoke-qemu.sh /tmp/razr-userspace-build "$PWD/evidence"
~~~

Builder captures environment.txt, inputs.env, full package TSV, apt/debootstrap logs, command transcript, QEMU kernel release, compressed rootfs and SHA256SUMS. QEMU test logs serial output and guest exit code. Acceptance requires qemu-serial.log containing literal RAZR_USERSPACE_SMOKE_PASS arch=arm64 init=systemd **and** exit status 0. Debian snapshot repositories retain signature verification.

First workflow run, from ebc63be45cdacead87c04c5b5576378d6c46d509: https://github.com/Drzet/razr2022_nuc/actions/runs/38164653282. This was still in progress when this initial handoff was created; its kernel is Debian generic and success, if obtained, proves only the emulated service. Later exact head must be validated independently.

No claim of successful build or guest boot is made until CI logs and artifact are checked. Reproducibility means pinned Debian archive timestamp plus recorded package/host tool versions, NOT guaranteed byte-for-byte-identical ext4 or initramfs images.

## Blockers and next test

1. Obtain a full successful CI run for the final branch head, record job/run ID, package and image hashes, QEMU serial sentinel and process exit status in tests/results. Investigate failures instead of marking a partial build as pass.
2. Boot must validate native kernel+oneli DTB and document actual flash/boot-image inputs; no board boot command is yet established.
3. Offline native integration later: supply matching native kernel modules, rebuild native initramfs and verify module/firmware closure. This requires an explicit new test, distinct from generic Debian QEMU smoke.
4. Physical hardware acceptance postponed: real boot, console logs, UFS root mounting, firmware startup, USB/DP/GPU/VPU/thermal/power are all untested while the phone is unavailable.

[INFERRED] Debian ARM64 systemd userspace is an appropriate candidate once the native kernel can mount and execute the real oneli root filesystem; hardware boot remains unverified.

## Follow-up assignment: coordinator second review (2026-10-11)

Read coordinator main `docs/NEXT_TASKS.md` at `98f6bd1fd441a2d0bca1596346a9aca3756bd0af`. The assigned gates are the missing QEMU ROM, non-root tar ownership, DHCP/SSH command acceptance, and machine-readable native kernel/module/firmware inputs. No kernel or board DT source was changed.

### Implementation provenance

Implementation commits on `razr/userspace` (in commit order):

- `10b617f90c25cedf1e97829be6d66e3d30ad020f`: verify extracted tar owner/group/mode against the original non-root home directory and an explicit UID 1234/GID 1235 fixture.
- `9e992a85595e14a77d020c968f2055e90f2440aa`: remove tar `--owner=0 --group=0`, add SSH/server/user, virtio_net-only DHCP, unique SSH host keys, and a disposable QEMU-only CI authorized key and shutdown privilege after tar export.
- `ccdc76fd49f79ba38de504f8189e20ea8e822b84`: separate QEMU systemd serial marker from host-guest SSH acceptance, explicit NIC, user networking and clean shutdown.
- `43bbfc2f7eaac8be0af0e926a1b21d6d643ab885`: avoid invoking chroot after removing bootstrap interpreter.
- `a4d23e89afb9fe5c4da1530e6088d60cdc3426dc`: host QEMU/iPXE and SSH dependencies, ownership shell-syntax check.
- `fd53f645b4ba827a8b3a33d9c559a3eea78e1e8b` and `becf007a164f4bebf76e65d8000d0b9e945e7850`: native artifact JSON template and offline validator.
- `cc9d57318e094f0149f7a5c764dc210da81b4c6e`, `c1638cdc11bd8b2b558cb0c287e920d843f19bce`: Boot contract and usage documentation.
- `5b84a259b5b78343da36c379c94b3a49ac37ad81`: explicit Ubuntu Noble iPXE ROM directory `/usr/lib/ipxe/qemu`, derived from Ubuntu `ipxe-qemu` package file list; not an inferred oneli ROM location.
- `85ff1c4f42465e8c139610e98ae2ccec4c994c3c`: QEMU smoke host process runs as root to access the ephemeral private key created by the root-owned builder.
- `ce17ea82c55a453ef593a7d0cbcb4f78520b2e67`: drop erroneous separate Debian trixie `systemd-networkd` package request; the service belongs to the `systemd` package.

**Evidence boundary:** The `razr` user account and SSH server are installed in the transferable rootfs; it contains no authorized key and no shared SSH host private key. The one-time public key and privileged shutdown rule are added only to the disposable QEMU disk after archive construction. This is static design until the next build verifies tarball and guest behavior. Running on the unavailable phone is not claimed.

### Completed CI results and exact scope

- Earlier pre-assignment run `38165284627` at source `b15c1dd292fface8928d8b70369472ac637cbe92`: **failure**, but Debian arm64 rootfs construction **passed**; QEMU exited before boot with `failed to find romfile "efi-virtio.rom"`. Full logs at https://github.com/Drzet/razr2022_nuc/actions/runs/38165284627.
- Follow-up run `38177212005` at source `85ff1c4f42465e8c139610e98ae2ccec4c994c3c`: **failure in rootfs package selection**, `E: Unable to locate package systemd-networkd`; no tar ownership check, guest boot or SSH occurred. Logs and partial artifact at https://github.com/Drzet/razr2022_nuc/actions/runs/38177212005. The Debian package is `systemd`, which contains `systemd-networkd.service`; fixed by commit `ce17ea82c55a453ef593a7d0cbcb4f78520b2e67`.
- New run `38177545171` (push) and `38177548051` (PR) for implementation SHA `ce17ea82c55a453ef593a7d0cbcb4f78520b2e67`: **unresolved at this handoff update**. GitHub reported push in_progress with `steps=null` and PR pending. No emulation pass claimed.

Commands are defined in `userspace/README.md`; QEMU's effective command, rootfs package versions, key SHA256, artifact hashes, owner-roundtrip and SSH/serial logs are emitted into Actions evidence **if the builder reaches those stages**. A failed partial evidence artifact is not proof of success. The hosting kernel is Debian's generic arm64 kernel for QEMU `virt`; native `Drzet/linux` kernel baseline remains `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`, untouched.

### Native Boot contract and blockers

Machine-readable template: `userspace/native-kernel-inputs.example.json`; validator: `scripts/validate-native-kernel-inputs.py`. Required exact `kernel_commit`, `kernel_release`, Image/config/oneli DTB paths, same-release modules directory with modules.dep, native initramfs path, licensed firmware manifest/directory and evidence-backed packaging manifest are intentionally **null** until Boot delivers real artifacts. Source-level schema presence does not make them available. No stock block-device numbers, boot header offsets or DTBO selection were guessed from the limited stock ADB capture.

**Remaining acceptance blocker:** Obtain a completed rootfs ownership roundtrip plus a real systemd boot marker, networkd/DHCP route, ephemeral-key SSH command and guest exit 0 from the *same* tested implementation. Hardware boot, Qualcomm storage, console, firmware acceptance and peripherals remain deferred, and cannot be inferred from `virt`.

## Third coordinator review follow-up — 2026-10-11

Read coordinator **main** `docs/STATUS.md` blob `1f3babd216fdfffd1d30e21bf286ae8838c72454` and full `docs/NEXT_TASKS.md` blob `fd33173324a2a97befcd87238271b36fa949ac74` (also current AGENTS/WORKFLOW). No aggregate main files, kernel baseline, or other subsystem branches changed.

### Independently inspected QEMU evidence

**Completed** run [38177877133](https://github.com/Drzet/razr2022_nuc/actions/runs/38177877133), job `114584033705`, source branch `f785ae444e904fe030baa8d745102d25a1fe2cde`, PR test-merge `1417fedd35f9fe217ad02953321696e8f092acef` (from `environment.txt`), **overall failure at SSH command check**. Downloaded evidence artifact ID `11717192325` and inspected the archive rather than relying on workflow status alone.

- Debian 13 `trixie` ARM64 bootstrap and rootfs tarball: PASS; builder exit code 0. Generic QEMU distribution kernel release `6.12.111+deb13-arm64`. `rootfs.tar.zst` SHA256 `2bdec49277b2ab79ccde1d84d7447c8342bd2e27a5c207468fc381d339825028`; `qemu-vmlinuz` `5028c424ee9fd0f4d18c38269122e30e3d084deb1b13404ab070a3f478ddd30a`; `qemu-initrd.img` `df154b816eef1d7aebdb3b2ef4e3e031074708b33aad48a4fbdc69601ffa6d2d`; `packages.tsv` `076deee0067b4012c4fde96bc6ae3e10fc89a18e80840157f9cf5e761cd9d703`.
- Exact Debian package examples: `linux-image-arm64=6.12.111-1`, `systemd=257.13-1~deb13u1`, `openssh-server=1:10.0p1-7+deb13u4`. Hosted Ubuntu 24.04.5; QEMU `8.2.2`.
- Archive **UID/GID extraction test passed**: `home/razr` source/extracted `1000:1000:700`; `usr/local/share/razr-ownership-fixture` source/extracted `1234:1235:644`.
- Generic QEMU arm64 Debian kernel booted and emitted exact `RAZR_USERSPACE_SMOKE_PASS arch=arm64 init=systemd`; `systemd-networkd.service` and `ssh.service` started, target reached multi-user.
- `ssh-command.log` shows an accepted host SSH key followed by `Failed to connect to system scope bus via local transport: No such file or directory`. **[INFERRED]** This error is produced by the prior `systemctl is-active systemd-networkd` test in the non-root SSH command; the log does not contain a separate explicit key-authentication-success marker, but executing that guest command and returning its error is evidence that SSH authentication and remote command execution worked. The network/SSH combined gate **failed**; no clean-shutdown success was recorded.

Follow-up commit `69d8810398cfa72b7dfa4b2807be7b9d5375aba9` replaces the user-bus-dependent `systemctl` call with PID 1 and IPv4 route checks. The QEMU acceptance step still must prove boot marker + route + remote authenticated command + exit 0 in one run.

### Native artifact gate: meaningful negative fixtures

New native contract validator commits: `a46bb56842eb44737c8363b514c4668e328c3a21` and `c375475d9e69fdd71e6e5663a418a9a3269f765b`, fixtures `04195d8c5c6890cd93edc72d7996400f49e9de71`, contract input template `44b4e1e6d15881cb6e39000ccab41f736d282a3a`. Schema v2 verifies AArch64 ELF + module vermagic, exhaustive compressed/native module SHA256 mappings, modules.dep hash, actual extracted initramfs module and firmware bytes, kernel Image/config/DTB/initrd/packaging manifest hashes, and refuses empty/unknown firmware requirements.

[Completed fast CI run 38179683577](https://github.com/Drzet/razr2022_nuc/actions/runs/38179683577), job `114589402535`, **SUCCESS** (6 tests/6 passing, 4.806 seconds). Branch SHA `ed536a2745286552166fd929018f407ba28ba9ab`; **actual PR merge SHA** `2b623aa24b4469b254ff9ffd2b0900bfc944fe7a`. See `tests/results/2026-10-11-userspace-native-contract.md`. These are synthetic ARM64 ELF module/firmware tests, *not* validation of Drzet/linux modules. Module symbol CRCs, actual firmware requirements and phone secure loading remain unproven.

### CI scheduling and consumers

The original rootfs workflow's duplicate push and PR triggers caused repeated cancellations. Commit `9a3d091f6dcf3d9dc3df7eea26b47bd108444507` removes the push trigger and scopes PR paths to actual generic rootfs/QEMU inputs. A separate lightweight fixture workflow validates native artifact parser changes. A replay workflow `d6d58b8c7ccc377a5fe79ddbe5767f41f6f06721` reuses the fully-hashed prior Debian rootfs tarball while assembling a **disposable** QEMU disk with a unique transient SSH key, avoiding a repeated >200 MB snapshot bootstrap for SSH harness debugging. Replay must record mixed source and harness SHA accurately; it cannot replace a clean full-build test at one final revision.

Boot consumes `docs/userspace_boot_contract.md` and `userspace/native-kernel-inputs.example.json` after the coordinator publishes exact Image/config/modules/DTB/firmware inputs. The **project-kernel QEMU virt** trial is a separate future gate, after the generic Debian-kernel pass, and must use QEMU's DT, never oneli's. No coordinator-selected combined project kernel with fully matching modules is presently supplied or accepted for this task. [INFERRED] Such a build can be used for generic virtual ABI tests once the coordinator identifies it, not as Qualcomm hardware emulation.

### Completed QEMU replay acceptance and CI trigger correction

[Replay run 38180287160](https://github.com/Drzet/razr2022_nuc/actions/runs/38180287160), job `114591200586`, **SUCCESS** at branch code `222720a5eb783750a79e510d2f8a11c666d988c7`, actual PR merge checkout `416657aa25c2167df7a2f45163cdb488d248f417`. The recorded source rootfs SHA256 is `2bdec49277b2ab79ccde1d84d7447c8342bd2e27a5c207468fc381d339825028` from old build `38177877133`; SHA256SUMS verification passed before disposable disk assembly. Guest marker `RAZR_USERSPACE_SMOKE_PASS arch=arm64 init=systemd`; authenticated remote marker `RAZR_NETWORK_SSH_PASS`; guest IPv4 `eth0=10.0.2.15/24`, connected route `10.0.2.0/24`, **no default IPv4 route shown**. Guest systemd poweroff reached `reboot: Power down`, QEMU exit `0`. Ephemeral key/sudo permissions only in disposable ext4, not source tar. Artifact ID `11717344092`. The SSH shutdown transcript contains a system-bus warning, but the independent serial trace conclusively establishes clean actual guest poweroff. See `tests/results/2026-10-11-userspace-qemu-replay.md`.

This is **implemented and emulation-tested for the generic Debian kernel** (QEMU virt), not hardware-tested or project-kernel-tested. Rootfs tar archive ownership was previously validated using actual extraction. The replay is NOT a fresh full rootfs build.

CI cancellation root cause: `pull_request.paths` matches the **cumulative PR diff**, so each documentation change retriggered and cancelled the full multi-minute build despite narrow-looking paths. Fix `e14f618fc1c55b3581e3bf082c1d12bbb0b05e03`: full workflow on explicit `razr/userspace` branch workflow-file push/manual dispatch only. Fast replay and native-contract workflows separately scoped to relevant **push** paths, commits `650459f9f9944d95adb63d5abd07cec29fe7b3bc` and `f6320c81287cfba6f09289b3b874590e1eb6f1bf`. No more documentation PR updates can cancel the expensive workflow.

A fresh full rootfs/QEMU workflow was started at source commit `e14f618fc1c55b3581e3bf082c1d12bbb0b05e03` as [run 38180519542](https://github.com/Drzet/razr2022_nuc/actions/runs/38180519542); conclusion must be inspected independently once complete. The QEMU replay acceptance itself is already complete, and six native artifact fixture tests passed. Project kernel QEMU remains on an explicit hold pending coordinator-selected Image + matching modules. No native oneli boot, actual Qualcomm firmware authentication or real peripheral result is inferred.

## Fifth work package: fourth-review metadata consumption and combined artifact staging (2026-10-12)

Coordinator main reviewed at `5261a8cb15e93d406bc58d711c224d53104c129c`, current `docs/STATUS.md` blob `ba9a17056ea24cc437a9c9496540a992f6e52d97`, `docs/NEXT_TASKS.md` blob `9a9b9b1f9a06c4f1998677871b9d25bee496d5e5`, fourth-review update `97e765f09931337a2a232a7d7d0036a572c099bb`. No physical phone, live DT, selected bootloader overlay or combined native kernel has been validated. The central six-FDT export has already completed: run `38220276125`, source-derived full JSON SHA256 `1a07f09d9ce7c3c4c1bcd4317ef634b28197a93bffe464e1c63f737579063465`.

### Owned commits, decisions and source limits

- `bc99eefbc03722d254aa6003bdeeef5c6724747d`, `7296fefdaa4493a38c1d022a160c9647d12c8751`: upgrade native artifact gate to v3 with explicit `qemu_virt`/ `oneli_native` targets, exact same-build Image/config/Module.symvers provenance, native module ABI/hash/embedded-initramfs checks; permit justified zero required firmware or early modules in a selected target while rejecting unknown requirements. Eleven fixture tests cover positive synthetic AArch64 and mismatches.
- `f5efd0dff0708d9d3558b0f49d001d2cee52b41c`, `f174432fab2d035e663d758ef5bcf3a82aa26475`: consume actual source-pinned Boot v1 and VPU six-FDT header/ramdisk/table export into `userspace/boot-reference-metadata-v1.json` and `scripts/audit-boot-reference-consumer.py`. The metadata bridge verifies published Git blob digests, v4 sizes/alignments, legacy LZ4 and one platform fragment, the two **unpadded** 479481-byte FDTs, PVT reference overlay index 3, and retains unverified OS-version/fragment name/bootconfig values. The stock loading addresses `0x8000`, `0x1000000`, `0x100`, `0x1f00000` are reference facts, **not** native placement approval. Active DT selection unresolved.
- `967e434e91798df9e57855ab0cb7e559f9362ba5`: align `docs/userspace_boot_contract.md` with the actual Boot v1 `oneli-native-boot-packaging-contract-v1`, which has **no** generic `status=verified`. Separate file integrity, reference structure, native composition and hardware acceptance. Current source-only check accepts Boot v1 as `structural_reference_audited=true`, explicitly `native_composition_ready=false`, `hardware_accepted=false`; no simulated flash success.
- `4f3d36890aa97e8803fbfa3e6c20bde897bb8f76`, `dcf72a622481e77c45809d877cfdadd55feeabd3`, `9b168c89f5d0328fd0c9a690ffd6808ffb73333d`, and `f9b5dfbcaa75c014861f966b0b0c8b2db81cf38c`: source-stage, **unexecuted** project-kernel QEMU consumer. Requires one selected exact combined Image/config/Module.symvers/modules/release/build ID and known loadable `virt` test module, hashes/vermagic validation, a fresh matching initramfs built against those modules, and authenticated in-guest `modprobe` plus `/proc/modules` proof. Rejects unknown firmware requirements. QEMU generates the DT, no oneli DT/boot image provided.
- `f1163e849e8301c9771f4573f6faa4aa84fd9279`, `9b58fded85ed73dffcad1ba39c02e28cea9c1ce3`, `ac1f8ab300eee8653cd856f6151ee0840a3a781e`: explicit **null until reviewed** templates for QEMU combined inputs, oneli native Boot inputs and native early-initramfs diagnostic requirements. No guessed `console=`, `root=`, storage, firmware, bootconfig, unsigned flashing parameters or physical bootloader acceptance.
- `eb39a910d0dcbff554d87cc80abd50013dd66bb0`, `fde6eb0fbc2fd06ab2ec9d1ffbdd12c7bc5fe4be`, `6d3f41b7281905ff4c27ca85a61799b32e78a7b6`: CI includes immutable Boot/VPU metadata cross-check and Bash source syntax, and **now propagates negative fixture failures** by `set -Eeuo pipefail`. An earlier purported green job 38244458164 concealed one failing unittest because `tee` was the final pipe command and a fixture expected old wording. That apparent green run was **not** accepted.
- `a122acf9db2bc96a81586d156fea52d15d76e699`: dedicated current [test result report](../../tests/results/2026-10-12-userspace-boot-contract-v3.md) (project-relative path is `tests/results/2026-10-12-userspace-boot-contract-v3.md`); source and emulation results explicitly separated.

### Completed acceptance and who consumes it

- Latest checked [Actions 38245293728](https://github.com/Drzet/razr2022_nuc/actions/runs/38245293728) at exact implementation SHA `9b168c89f5d0328fd0c9a690ffd6808ffb73333d`, job `114797531172`: **SUCCESS**, 11/11 fixture tests, pinned Boot/VPU reference audit `BOOT_REFERENCE_METADATA_PASS`, and source-stage Bash syntax. No project-kernel QEMU run was attempted. Source-only metadata comparison does not prove independently applying FDT overlays or unpacking original stock bytes; test source was pinned Boot and VPU JSON, not executable phone firmware. Previous 38244943279 also passed this test suite, and separately validated the compiler-ABI checks.
- Prior [fresh full Debian rootfs / QEMU 38180519542](https://github.com/Drzet/razr2022_nuc/actions/runs/38180519542) at project `e14f618fc1c55b3581e3bf082c1d12bbb0b05e03`: **SUCCESS**. Archive UID/GID extraction pass, ARM64 Debian systemd guest, configured IPv4 + authenticated SSH, shutdown and QEMU status zero. Generic **Debian kernel**, NOT a Drzet/linux or physical oneli run; external internet not asserted. No unchanged full bootstrap repeated for this documentation/contract work.
- **Boot recipient**: [Userspace native artifact contract](../userspace_boot_contract.md), metadata bridge `userspace/boot-reference-metadata-v1.json`, v3 `userspace/oneli-native-inputs.example.json`. Needs Boot review of staged reference/native-readiness semantics and eventual v2 packaging manifest if native composition becomes demonstrable. Boot is *not* requested to invent a `verified` field.
- **Coordinator recipient**: `scripts/prepare-project-qemu.sh` and `userspace/native-kernel-inputs.example.json`. Exact combined Image, release, generated config, `Module.symvers`, modules/moddep, build toolchain and hash manifest, loadable QEMU-module candidate and virt-capable config must be selected/published **together**. Then use QEMU's virt DT and perform one real load/systemd/SSH/poweroff acceptance test; do **not** choose a preexisting standalone GPU/Boot/Power kernel opportunistically.
- **VPU recipient**: radio-derived `vpu20_4v.mbn` SHA256 `9582ea4c5565408bd3e5ba6f8fffc7881f226cae001b6fcd7a0c868de9add9af`; proposed `qcom/vpu/vpu20_4v.mbn` install path remains experimental for a *future enabled VPU profile*. It is **not** a requirement for generic QEMU or oneli minimal early initramfs. Signed firmware authorization/driver runtime remains hardware-only.
- **Physical native diagnostics**: only an input design `userspace/native-early-diagnostics.example.json` exists. Console/bootloader/storage/firmware cannot be populated from the public reference. No flash, bootloader unlocking, native kernel boot or phone-level UART/USB/GPU/VPU/charging result is claimed.

All source and report edits occurred on `razr/userspace` in `Drzet/razr2022_nuc`. No merge into coordinator main, no edits to `Drzet/linux` or Boot's source manifest, and no kernel baseline change. **Stop condition:** accepted source/fixture work ends here pending exact coordinator combined artifacts; there is no justification for another unchanged Debian rootfs build or repeated stock ROM extraction.
