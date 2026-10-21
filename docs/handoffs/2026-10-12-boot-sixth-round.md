# Boot sixth-round handoff: delegated combined ARM64 candidate and Userspace interface

Date: 2026-10-12. Boot owner. Coordinator source: `Drzet/razr2022_nuc` main `docs/NEXT_TASKS.md` blob `d10cffa04f333ee456ef29501921aa4cbb323ae9`, `docs/FIFTH_REVIEW.md` blob `2926da8ee4709e434f78a0d038b95ecee9c586ff`, `AGENTS.md` blob `b3f8041c0541ae3994354ddf9e588f253c2ce3ef`. Delegated Boot candidate creation/build; coordinator retains promotion and aggregate status.

## Source / integration revisions

- Baseline untouched: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- Boot parent unchanged: `525b504b82dbca593a9a697af9be63f53915e0a3`.
- New isolated branch: `Drzet/linux:razr/integration-candidate`. Source replay end `5e647126da5cd0379b061789b1148107bbc7fda3`, candidate workflow commit **`2b5acf108ae37040ac1e652e029bb37f5609e886`**. This is a candidate, not a coordinator-approved `razr/integration` or a native phone image.
- Seven replayed commits, each old/new file conflict-checked against predecessor blob and target blob copied from exact original:

| Owner / subject | Source SHA | Replayed SHA |
| --- | --- | --- |
| GPU chip ID A730 rev 2 | `4955f07a94ea3c51e423e34d819ac3f76f1c9d37` | `eaf8c3dd0d3395bd8915e16c6bd352a4c46f9e2c` |
| GPU GMU pwrlevels return/unwind | `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3` | `f00db9a6d593c03ecf469bcb1d1394d67e604924` |
| Power signed-temp fix | `add9522b3a7ba4ae9d34ee670577c1a0f742585e` | `77969dce2ee39fe362cfeafbc62a8a200f903cf0` |
| Power shared decoder | `a645ca00d80c8def170878e2283975ccacc209a8` | `d371fed6414882b5aedc6e17e16c8d73241c30fd` |
| Power KUnit tests | `b08688eb8f8905da4a37a7644c381f0d579b7ff8` | `75a6e39788ad6884314fdac5f8232b199a6cd545` |
| Power KUnit Kconfig | `0a7af7aeb9aa843547aa3bddc6b326fb04c49808` | `b274ea4f23b5bc3c813546a48595a75f2fe3050a` |
| Power test Makefile | `564f2c7df60316db86e36d7267ddadf07bc32b7e` | `5e647126da5cd0379b061789b1148107bbc7fda3` |

`compare_commits` Boot parent→candidate reported **8 commits, seven changed source files plus the new workflow**; no other subsystem history or branch-mutating workflow imported. Optional UBWC `7f1d729...` withheld, Iris and PS5169 experiments excluded, GPU/USB/VPU/DP/charging peripherals still disabled. Boot includes the USB PHY binding already; no duplicate application.

## The frozen Boot ↔ Userspace v1 artifact contract

- [Machine-readable Boot producer contract](../configs/oneli-combined-artifact-interface-v1.json) committed at `18b68b8babf48a67b518ab410f08390d401de9b4`, [coordination issue #13](https://github.com/Drzet/razr2022_nuc/issues/13). Userspace acknowledgement and its code changes are independent and may follow the producer artifact.
- QEMU virt uses generated virtual DT, `-machine virt -cpu cortex-a57`, built-in PL011, virtio-mmio / block / net, ext4, initrd/devtmpfs and `CONFIG_DUMMY=m` as real modprobe target. Exact config fragment [`configs/oneli-combined-qemu-virt.config`](../configs/oneli-combined-qemu-virt.config) at project commit `6a80ab302e9e2cf5aaf3ca0187baec106e985ade`. Config defaults originate `arch/arm64/configs/defconfig`; olddefconfig and explicit value check must pass. The module is `modules/<release>/kernel/drivers/net/dummy.ko` with matching ELF `vermagic`.
- Complete downloadable archive expected: `combined-bundle.tar.zst`, with `Image`, `kernel.config` + original `.config`, `Module.symvers`, `kernel.release`, `sm8475-motorola-oneli.dtb`, `modules/<release>/` including depmod indexes and all .ko with no dangling source/build symlinks, zero-Qualcomm-firmware QEMU-scoped firmware schema v2, `module-sha256.json`, `build-manifest.json`, `qemu-native-inputs.v3.preflight.json`, `SHA256SUMS`, evidence logs/toolchain. Additional ZIP artifact and archive SHA256 published by GitHub Actions.
- The producer manifest matches Userspace's schema v3, `qemu_virt`, `dtb_path=null`, `boot_packaging_manifest_path=null`, `modules_sha256` exhaustive and `same_build` tied to kernel/image/config/Module.symvers SHA. **`initramfs_path` and its SHA are intentionally null in the producer preflight manifest**, awaiting Userspace's new same-build initramfs. Userspace must fix pathname-only oneli rejection, install mount cleanup before the first mount, and test actual staging/failure paths.
- Native oneli packaging v2 remains structurally referenced only, independent of QEMU. No phone initramfs, root storage address, bootloader placement or flash operation inferred.

## CI / acceptance

[Combined kernel Image/modules/DT/schema/FDT/artifact workflow](https://github.com/Drzet/linux/actions/runs/38292394177) at exact kernel commit `2b5acf108ae37040ac1e652e029bb37f5609e886`. **As of this handoff draft, this run began and toolchain and QEMU-virt configuration steps passed; full Image/modules build and downloadable artifact are NOT YET accepted.** Do not promote until final run status, specific artifact ID/digest, actual installed files and module verification have been inspected. Kernel branch has not been hardware tested. No new firmware download performed.

Once a complete artifact exists, hand exact immutable references to Userspace on [issue #13](https://github.com/Drzet/razr2022_nuc/issues/13); coordinator reviews candidate code/artifacts before accepting or promoting. Userspace executes distinct QEMU virt Project Image/modprobe/systemd/SSH/clean-shutdown smoke; that cannot substantiate native Motorola boot.

## Post-review correction (2026-10-12, sixth coordinator review)

The earlier **pending-build / candidate-not-accepted** paragraph above is a historical in-flight observation and is **superseded**. Coordinator independently inspected [run 38292394177](https://github.com/Drzet/linux/actions/runs/38292394177), all 1,735 bundle checksums and the full ARM64 Image/1,702 modules, then [real combined-kernel Debian QEMU run 38297826535](https://github.com/Drzet/razr2022_nuc/actions/runs/38297826535). Exact tested kernel commit `2b5acf108ae37040ac1e652e029bb37f5609e886` is now **accepted on `Drzet/linux:razr/integration`** for source/build/QEMU only. SHA256 of verified combined ZIP: `bc9ae13983e7aa3161df1cade037929ebd71144e27f4d19204dd0bf50c88f06e`, internal archive `5338b42efa668b8755c5cff7d12ef9d1ede46106c3abe17cf30118030c009896`. Canonical acceptance: coordinator [`docs/SIXTH_REVIEW.md`](https://github.com/Drzet/razr2022_nuc/blob/main/docs/SIXTH_REVIEW.md), [accepted integration manifest](https://github.com/Drzet/razr2022_nuc/blob/main/configs/accepted-integration-2026-10-12.json). **Do not repeat this build or Debian QEMU smoke.** Device execution remains untested.

The subsequent Boot assignment is the **separate native diagnostic initramfs interface**, proposed in `configs/oneli-native-early-initramfs-interface-v1.json` and `docs/oneli-native-early-initramfs-interface-v1.md` on `razr/boot`. Userspace acknowledgement and a new minimal diagnostic payload are outstanding. No native phone image has been produced or approved.
