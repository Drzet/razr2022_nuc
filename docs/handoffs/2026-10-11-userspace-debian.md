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
