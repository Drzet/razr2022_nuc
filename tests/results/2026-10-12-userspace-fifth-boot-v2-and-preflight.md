# Fifth review: Userspace Boot v2 alignment, combined-build wire handshake and executed preflight

Date: 2026-10-12. Owner: Userspace, \`Drzet/razr2022_nuc:razr/userspace\`.

## Coordinator inputs (read in full)

Coordinator \`docs/STATUS.md\` blob \`abf01c457c601bebce714d4d4eb0a83800953bc6\`; \`docs/NEXT_TASKS.md\` blob \`d10cffa04f333ee456ef29501921aa4cbb323ae9\`; fifth review \`docs/FIFTH_REVIEW.md\` blob \`2926da8ee4709e434f78a0d038b95ecee9c586ff\`. Boot project source \`cfdecbf41a329bcc0fa3074f8de708e95ef698b1\`, Boot v2 blob \`a53a7b8eb994ffb75fb153d4aa5aea1b5d0c38ef\`. Boot kernel remains \`525b504b82dbca593a9a697af9be63f53915e0a3\`; no accepted combined kernel artifacts as of this review. Boot has explicit fifth-review authority to prepare \`razr/integration-candidate\`; coordinator controls acceptance/promotion.

## Boot wire-format handshake, not yet signed off by Boot

Userspace published [the exact producer/consumer contract](../../docs/userspace_combined_kernel_handoff_v1.md) at \`1f9325002e2b4ae65258b8cc1352f3ac2909d445\`, and [requested explicit Boot ACK/corrections on PR #12](https://github.com/Drzet/razr2022_nuc/pull/12#issuecomment-6130270675). **Boot has not explicitly acknowledged the proposal in the checked comments.** Proposed producer: immutable ZIP with generated Image/config/Module.symvers/kernel.release/oneli DTB/fully installed matching module tree, exhaustive SHA256, \`modules.dep\`, Kconfig, compiler/source commit order, selected loadable \`dummy\` module and the \`oneli-combined-kernel-build-v1\` manifest. Userspace constructs and hashes the fresh initramfs **after** receipt; QEMU \`virt\` must use QEMU-generated DT and no phone package.

QEMU required builtins: \`CONFIG_ARM64\`, PL011 console, GIC, virtio-MMIO/BLK/NET, EXT4, DEVTMPFS, INITRD/gzip, INET/UNIX/PACKET, TMPFS, BINFMT_ELF; \`CONFIG_MODULES=y\`, recommended \`CONFIG_DUMMY=m\`. Values checked against the actual generated config, not a claimed fragment. If Boot changes selected module or layout, version the agreed contract and preflight first.

## Boot packaging v2 bridge

- \`userspace/boot-reference-metadata-v2.json\`, \`ab650df9ad8a1b360b62bfc6716f408109509e1c\`: pins Boot v2 and VPU's six-FDT export; retains structural-only, native-not-ready, hardware-not-accepted fields. Source reference load addresses and two unpadded base DTBs remain facts, not approved boot placements.
- \`scripts/audit-boot-reference-consumer.py\`, \`c03c2cc02c846824e390eb93ba93afd997f01674\` and \`7d2ea756b866044df80f3470449ca32e587f2a5d\`: cross-check Boot v2 source fields and reference VPU typed offsets, OS-version null, explicit required header inputs and disabled native readiness.
- \`scripts/validate-native-kernel-inputs.py\`, \`93bc0b33df2d5fa2c06e63ea528c520f25fb24ac\`: native \`oneli_native\` now requires Boot v2 and a separate \`native_header_inputs_path\`. Every header field must have an explicit bounded unsigned integer, including \`os_version_raw\`; \`phone_boot_validated=false\`, recognized purpose. Empty/missing/null values rejected. Passing checks **never** sets native-ready or phone-accepted. \`qemu_virt\` prohibits this file and the oneli DT/packaging.
- \`tests/userspace/test_native_contract.py\`, \`b23c0c8fb0420ff765f1b54f29ea5906c62c4390\`: **14** tests including Boot v1 rejection and missing/null v2 header inputs.

## Actual code exercised (not only shell syntax)

- \`scripts/preflight-project-qemu.py\` implements direct non-root consumption of the Boot bundle: SHA256 paths, kernel.release, full provenance, generated Kconfig builtins, module tree and exhaustive hashes, real compressed/uncompressed AArch64 ELF \`modinfo vermagic\`, chosen module, and unsafe/dangling module symlinks. Latest correctness fix \`1d598f557b7af1a63000e82c2db46e110f623bf4\` gives clear errors for missing files.
- \`scripts/prepare-project-qemu.sh\` changed to **4 arguments**: bundle directory, verified Debian rootfs archive, archive SHA256, new workdir. It invokes the **same** actual non-root preflight before any write, removes the old pathname-based \`oneli\` Image exclusion, installs mount cleanup before its first mount, then builds matching native initramfs in a temporary AArch64 Debian chroot. No actual combined build was available to execute the chroot/disk creation stage.
- \`scripts/finalize-project-qemu-manifest.py\` creates post-initramfs Userspace schema v3 with actual new initramfs hash and reviewed \`qemu_virt\` zero-firmware scope; \`prepare\` invokes the real full validator before marking disk ready. Boot is not asked to supply the not-yet-existing userspace initramfs.
- \`scripts/smoke-qemu.sh\` requires exact project release, selected module, actual in-guest \`modprobe\`/\`/proc/modules\` whenever the staged project context exists; generic Debian-kernel mode remains distinct.
- \`tests/userspace/test_project_qemu_preflight.py\` executes **13** synthetic positive/negative preflight checks, including wrong-release module despite recomputed SHA, \`CONFIG_VIRTIO_BLK=m\` rejection, \`CONFIG_DUMMY=y\` rejection, missing artifacts, mismatched release, and **actual shell invocation before rootfs access or workdir creation**. These tests run the implementation used by staging, unlike previous syntax-only review.

## Independently checked CI conclusions

**PASS** [run 38292951263](https://github.com/Drzet/razr2022_nuc/actions/runs/38292951263), source SHA \`517a72e3e41547b6362709d2a67b3652b94350ac\`, job \`114957144515\`. Python native validator: **14/14 passed**. Direct preflight + shell entry tests: **13/13 passed**. \`BOOT_REFERENCE_METADATA_PASS\` cross-checked immutably pinned Boot v2 and VPU JSON. \`bash -n\` passed. Earlier during this round, failures occurred from still-pinned Boot v1 CLI and fixture error-string mismatches; subsequent runs correctly enforce pipefail. Do not mislabel those earlier red jobs as accepted. Some later code/documentation edits did not change this acceptance's verified fixture inputs.

**PASS** existing independent Debian-distro QEMU replay [38292682678](https://github.com/Drzet/razr2022_nuc/actions/runs/38292682678): \`QEMU_SYSTEMD_NETWORK_SSH_PASS\`. It uses a **Debian** kernel, not \`Drzet/linux\`. Previous full Debian creation run 38180519542 also passed; no unchanged rootfs rebuild performed.

## Explicit stop condition

**Project-kernel chroot/initramfs/disk staging and QEMU guest runtime are not tested** because no coordinator-accepted combined Image/config/Module.symvers/modules release and immutable artifacts exist. Boot acknowledgement to the manifest/config proposal is separately pending. No oneli boot/AVB/console/flash/firmware authentication or physical peripheral validation occurred. Boot may build after acknowledging or amending the wire contract while Userspace fixes targeted execution problems concurrently. There is no need for another stock firmware scan.

## Final agreement update (later on 2026-10-12)

The earlier "awaiting Boot ACK" note is now superseded. Boot declared [authoritative portable combined artifact v1](https://github.com/Drzet/razr2022_nuc/blob/razr/boot/configs/oneli-combined-artifact-interface-v1.json) in [issue #13](https://github.com/Drzet/razr2022_nuc/issues/13); Userspace **explicitly ACKed** its \`artifact-root/\` \`combined-bundle.tar.zst\` producer layout and withdrew its competing ZIP proposal. The [Boot PR comment](https://github.com/Drzet/razr2022_nuc/pull/12#issuecomment-6130612887) redirects all producers to issue #13. Boot has started kernel candidate \`2b5acf108ae37040ac1e652e029bb37f5609e886\`, [build 38292394177](https://github.com/Drzet/linux/actions/runs/38292394177); completion still requires exact downloadable artifacts and hashes.

Added \`scripts/normalize-boot-combined-bundle.py\`, a verified adapter from **actual Boot-specified** Image/config/Module.symvers/modules-released tree, QEMU preflight null-initramfs state, build manifest, sha records, firmware-v2 record and toolchain evidence into the existing Userspace internal staging layout. Boot does **not** need to alter its artifact tree. Synthetic tests exercise the real adapter plus existing direct module/Kconfig preflight, including corrupted Image, hidden config drift and bogus producer initramfs. **Latest accepted [run 38293908746](https://github.com/Drzet/razr2022_nuc/actions/runs/38293908746), commit \`77bdef876fbbf129be369da151dca3557ba0a8a4\`**: 14/14 native fixtures, **17/17** producer-adapter/preflight fixtures and pinned Boot-v2 metadata audit passed. This supersedes the prior 14+13 fixture report. No combined Image has yet booted QEMU in this Userspace evidence.

