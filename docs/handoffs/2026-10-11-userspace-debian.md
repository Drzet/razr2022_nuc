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
