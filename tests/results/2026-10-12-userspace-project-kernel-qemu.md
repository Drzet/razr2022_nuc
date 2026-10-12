# Combined Drzet/linux kernel in Debian ARM64 QEMU virt: first complete pass

Date: 2026-10-12. Owner: Userspace `Drzet/razr2022_nuc:razr/userspace`.
Scope: **QEMU virt software boot and module compatibility, not Motorola oneli hardware validation.**

## Immutable inputs and interface

- Agreed Boot ↔ Userspace producer layout: [issue #13](https://github.com/Drzet/razr2022_nuc/issues/13), `configs/oneli-combined-artifact-interface-v1.json` on Boot; Userspace `scripts/normalize-boot-combined-bundle.py` adapts the Boot producer to the internal consumer and schema v3 final validator. The QEMU profile has no oneli DT, phone boot.img, or Qualcomm proprietary firmware.
- **Exact kernel**: `Drzet/linux` integration candidate `2b5acf108ae37040ac1e652e029bb37f5609e886`, generated `kernel.release=7.3.0-rc6-g2b5acf108ae3`, Boot build ID `509272edbb90625627a434ef0febc1410b0a896cc2500ffcef82436db32cfe15`.
- Boot full Image/modules/DTB/ordinary modpost and published binaries: [run 38292394177](https://github.com/Drzet/linux/actions/runs/38292394177), producer artifact `11768562884`, `combined-bundle.tar.zst` SHA256 `5338b42efa668b8755c5cff7d12ef9d1ede46106c3abe17cf30118030c009896`. Bundle's own SHA256SUMS verified successfully. Image SHA256 `3a8fa9620e0fc8de68ce8db45dacdfd811a2ba2c9718f9cddee3893ec9af0939`; generated config SHA256 `c86c04cc707889c66f8e4a485d1bff70819c1747150cb211836f07efb9fff90e`; Module.symvers SHA256 `5802d8bb9cb077c61dcf0d7b2bdc8d32793329389156b3b312e7339f9a3d3151`. Full installed matching tree has **1,702 AArch64 modules**; selected guest module `kernel/drivers/net/dummy.ko` (`CONFIG_DUMMY=m`).
- Previously validated Debian trixie ARM64 rootfs `rootfs.tar.zst`, SHA256 `2bdec49277b2ab79ccde1d84d7447c8342bd2e27a5c207468fc381d339825028`, from project [run 38177877133](https://github.com/Drzet/razr2022_nuc/actions/runs/38177877133). Reused unchanged; fresh matching initramfs and disposable 3072 MiB ext4 guest image generated.

## Completed end-to-end evidence

**PASS: [Userspace run 38297826535](https://github.com/Drzet/razr2022_nuc/actions/runs/38297826535), job 114973102362**, checkout `afe416c477069659c7943f7de4b4f2fe9af39fa3`. Evidence artifact `11768979982` (`userspace-project-qemu-38297826535-1`, ZIP SHA256 `6a30943b97da12f3d8a0b6aeb42ff36fa68f2f731ea0a72531d3d2b3b8148b04`).

- Producer archive and rootfs SHA256SUMS verified; Boot v1 adapter reports `BOOT_COMBINED_BUNDLE_NORMALIZED`; real AArch64 ELF/vermagic preflight reports `PROJECT_QEMU_PREFLIGHT_PASS`.
- Staged initramfs is generated **for that exact kernel release**, not reused from Debian's kernel. Final schema v3 validation reports `NATIVE_ARTIFACT_STATIC_PASS` with 1,702 modules, exact Image/config/Module.symvers, initramfs bytes and scoped zero-firmware QEMU profile.
- Actual `qemu-system-aarch64 -machine virt -cpu cortex-a57` uses the **combined Drzet/linux Image**, new initrd, virtio-mmio block/net, QEMU-generated DT (never oneli DT), `console=ttyAMA0`. Serial marker `RAZR_USERSPACE_SMOKE_PASS arch=arm64 init=systemd`.
- Authenticated SSH as disposable `razr` user; `/proc/1/comm=systemd`; assigned IPv4 `eth0 10.0.2.15/24`; remote `RAZR_NETWORK_SSH_PASS`. The observed IPv4 routes contain only the connected `10.0.2.0/24` route; **no external internet connectivity claimed**.
- The project-only guest check verifies `uname -r=7.3.0-rc6-g2b5acf108ae3`, executes `sudo -n /usr/sbin/modprobe dummy`, checks an actual `dummy` entry in `/proc/modules`, then emits `RAZR_PROJECT_MODULE_LOAD_PASS`.
- SSH submits `systemctl poweroff`. A remote system-bus warning appears during shutdown; independently, serial shows full systemd shutdown and `reboot: Power down`. QEMU exit code **0**. Guest boot and SSH status files both `passed`; `project-smoke.log` reports `QEMU_SYSTEMD_NETWORK_SSH_PASS`.

## Harness corrections and scope boundary

Three source test launches used the same immutable Boot binary bundle: [38297069603](https://github.com/Drzet/razr2022_nuc/actions/runs/38297069603) failed from checking `validation/native-v3-validation.json` instead of the actual `evidence/native-v3-validation.json`, **after staging had passed**; [38297375653](https://github.com/Drzet/razr2022_nuc/actions/runs/38297375653) booted and shut down successfully but the CI step was marked failed because a prior `sudo cp -a` changed the evidence directory owner and `tee` could not write `project-smoke.log`. Commits `618d9d4eb447fecebcfda369c7f63cbd9ef89223` and `afe416c477069659c7943f7de4b4f2fe9af39fa3` corrected these CI-only errors, with complete green job 38297826535 and inspected downloadable logs.

The initramfs creator emitted warnings for unrelated built-in hardware drivers' optional firmware files. These are **not** evidence of required Qualcomm firmware on QEMU `virt`, and future enabled consumers must be assessed separately. QEMU does not test Motorola bootloader acceptance, oneli DT selection, native UFS, GPU/VPU firmware authentication, USB-C/DP, real charging or thermals. Boot candidate remains subject to coordinator acceptance/promotion; Userspace made no changes to `Drzet/linux` or coordinator aggregate status.

## Reproduction

Workflow: `.github/workflows/userspace-project-kernel-qemu.yml` on `razr/userspace`, pinned Boot kernel run and archive digest, pinned Debian rootfs and digest. Its sequence: `gh run download` for both source artifacts; archive hashes; `normalize-boot-combined-bundle.py`; `preflight-project-qemu.py`; `sudo bash scripts/prepare-project-qemu.sh <normalized-bundle> <rootfs.tar.zst> <rootfs-sha256> <fresh-workdir>`; `sudo bash scripts/smoke-qemu.sh <workdir> <evidence-dir>` with explicit `RAZR_PROJECT_KERNEL_RELEASE` and `RAZR_PROJECT_QEMU_MODULE=dummy`. The project test does not substitute the Debian distribution kernel.
