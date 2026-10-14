# Build record: PTN3222 Motorola profile offline adaptation

- Date: 2026-10-14.
- Project repository commit at execution: `fe6a73f769bb193988ce256066a2168b6940a85d`, with the two new test scripts in the working tree. Their source hashes are preserved in the result records; the canonical handoff identifies the delivery commit.
- Kernel repository / branch / exact commit: `Drzet/linux:razr/usb-ptn3222@f499a099f3d53fae2b1ece4701e4c27f5c71429b`.
- Upstream baseline commit: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- Board-support and subsystem commits: baseline only plus the isolated PTN3222 adaptation. No board node, shared DTS, PS5169, accepted integration or other subsystem changes.
- External patches: no patch applied wholesale. Existing upstream PTN3222 reused; exact Motorola/NXP/community sources and coverage are in the canonical USB handoff. Adaptation is a new local commit, preserving existing authorship/license.
- Host/build environment: Ubuntu 26.04.1 amd64, four build jobs; Python 3.14.4. ARM64 cross compilation, not ARM64 execution.
- Toolchain identity/version/source: distribution `aarch64-linux-gnu-gcc` and host `gcc` 15.2.0 (`Ubuntu 15.2.0-16ubuntu1`), DTC 1.7.2; dtschema 2026.6 with [exact installed packages](2026-10-14-usb-ptn3222-offline/schema-packages.txt).
- Architecture and configuration base: ARM64 `tinyconfig`, then MODULES, OF, I2C, GPIOLIB, REGULATOR, COMPILE_TEST enabled; PHY_NXP_PTN3222 and PHY_SNPS_EUSB2 modules; WERROR disabled. Kconfig selects REGMAP_I2C=m and GENERIC_PHY. This is a reduced linkage configuration, not the handset defconfig or an accepted combined image.
- Configuration fragments: no external fragment; exact script options below and generated configuration preserved.
- Generated configuration artifact: [kernel.config](2026-10-14-usb-ptn3222-offline/kernel.config), SHA256 `789bbe87f9479e856cd8303545d28126dba0d0c0d77f20658039b05b8de940ef`.
- Firmware: none included or executed.

## Commands and results

The build ran with modified source before creating `f499a099...`; its committed driver bytes are identical to the tested bytes (SHA256 `023239da29c269e42bcebd0d97c1a77e7cd934f631ef3fec1429e044a535cf57`). Commit creation does not justify recompiling unchanged source. Reported kernel.release was `7.3.0-rc6+`.

```sh
make -C /tmp/razr-usb-ptn3222 O=/tmp/razr-ptn3222-build \
  ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- tinyconfig
/tmp/razr-usb-ptn3222/scripts/config --file /tmp/razr-ptn3222-build/.config \
  --enable MODULES --enable OF --enable I2C --enable GPIOLIB \
  --enable REGULATOR --enable COMPILE_TEST --module PHY_NXP_PTN3222 \
  --module PHY_SNPS_EUSB2 --disable WERROR
make -C /tmp/razr-usb-ptn3222 O=/tmp/razr-ptn3222-build \
  ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- olddefconfig
make -C /tmp/razr-usb-ptn3222 O=/tmp/razr-ptn3222-build \
  ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j4 Image modules
python3 tests/usb/ptn3222/test_driver.py \
  /tmp/razr-usb-ptn3222 /tmp/razr-ptn3222-host
python3 tests/usb/ptn3222/validate_binding.py \
  /tmp/razr-usb-ptn3222 /tmp/razr-ptn3222-schema \
  --tools /tmp/razr-ptn3222-schema-venv/bin
```

**Compilation/linkage PASS:** [build.log](2026-10-14-usb-ptn3222-offline/build.log) and [configure.log](2026-10-14-usb-ptn3222-offline/configure.log). Actual `Image`, modules, modpost and `.ko` linking completed. PTN3222, SNPS and regmap-I2C are included; no unresolved-symbol or source-compile diagnostic occurred. No defconfig/DTB/boot validation is implied.

**Production-function host execution PASS:** [host-result.json](2026-10-14-usb-ptn3222-offline/host-result.json), **37 scenarios**, GCC ASan/UBSan with leak detection. Actual production C functions/structures are compiled after removing only kernel include directives and module-registration trailer; providers, regulators, GPIO, delays and regmap are explicit host mocks. Covers legacy/no-GPIO behavior, exact normal/host writes and vote ordering, mode before/after init, role replay after exit, OTG/device selection, invalid modes, all four power-on steps, four ID reads, three initial writes, each ID-byte mismatch, three role-write failures with rollback, failed rollback fail-closed recovery, cleanup disable/voltage failures and retries, provider/defer/property errors and devm cleanup. This is not execution of kernel regulator/PHY internals or chip emulation.

**Real binding/instance validation PASS:** dtschema 2026.6, `dt-doc-validate`, `dt-mk-schema`, DTC DTBs and `dt-validate` filtered to the actual binding. [schema-result.json](2026-10-14-usb-ptn3222-offline/schema-result.json): **2 valid / 7 invalid** fixtures. Positive legacy-minimal and synthetic profile instances have no binding diagnostics. Negative instances require the correct diagnostics for absent reset, absent each supply, unknown/wrong-type profile and both raw vendor sequence properties. Validation checks diagnostics, not merely `dt-validate`'s exit status. Fixtures do not describe verified oneli hardware.

**Source/style checks PASS:** `git diff --check`; `scripts/checkpatch.pl --no-tree --strict --file drivers/phy/phy-nxp-ptn3222.c`: zero errors, warnings or checks. No PS5169 tests or source audit rerun.

Initial tool setup failures were environmental: the sandbox prevented LeakSanitizer process inspection, so the successful host run used approved execution outside the sandbox; Python lacked ensurepip/development headers, so pinned tooling and downloaded headers were staged under `/tmp`. No system package was installed. These failures were not driver-test failures.

## Image preparation

Not applicable: no ramdisk, boot package, device-tree selection or handset boot parameters. The reduced build's raw Image is a compile artifact.

## Artifacts

These SHA256 values were computed locally from the actual produced files, not copied from CI:

| Artifact | SHA256 |
| --- | --- |
| ARM64 Image | `fbe3331fbf58fc6d423dbf89d78dce66486908b54fcdda020ceaae7b86299da3` |
| phy-nxp-ptn3222.ko | `c1176abf43926f94c929ae252e5cfab671904685277b87716d677165487944c6` |
| phy-snps-eusb2.ko | `da7c9299c21bd91cea60d895a8de083972940b850c0ac05665662ae24b8eeab0` |
| regmap-i2c.ko | `022feb53f9a32b62d5819ce3285be9dad725ea1d31ca2ffb465ac3c4d679157b` |
| Module.symvers | `23e17467b4dc6e379c2b4bf698d912a6d947f65d7b830f07482d53755eb0a605` |
| Local evidence archive | `479bb5347c6cd5129d201984c6878de190b8a257a95855b66b9762d5e2831996` |

Binary outputs, generated host harness and compiled fixtures are preserved locally in `/tmp/razr-ptn3222-offline-2026-10-14.tar.xz` (837,076 bytes); no binary payload is committed. Text logs/configuration/diagnostics are in [the record directory](2026-10-14-usb-ptn3222-offline), with [SHA256SUMS](2026-10-14-usb-ptn3222-offline/SHA256SUMS). The local archive is not a hosted CI artifact or a permanent remote binary store.

## Device validation

**Not tested.** Phone unavailable. Confirm installed DT and populated identity, GPIO7 polarity/function, board rail parents and physical sequencing/settle, device/host enumeration, reconnect and suspend/wake when hardware is available. Chip-ID checks fail before tuning on unsupported/unreadable identity, but cannot prove the board wiring. The experimental profile ABI needs coordinator/maintainer review. Unchanged SNPS/DWC3 consumers have inherited error-caching/ignored-role-return limitations; provider error returns are tested, not end-to-end controller fault recovery. No accepted integration promotion or board enablement is claimed.
