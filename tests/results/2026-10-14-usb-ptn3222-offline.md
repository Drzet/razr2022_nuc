# Build record: PTN3222 informational identity policy (2026-10-15)

- **Authorization:** user explicitly authorized keeping undocumented BUK identity informational, validating offline, publishing and updating the handoff. This supersedes the earlier source-only assignment for this bounded change; coordinator acceptance/integration remains separate.
- **Project branch/base:** `razr/usb@5a9e2c5f4fa743fd79580eac44ccd00379f0ed17`. Updated `tests/usb/ptn3222/test_driver.py`, this existing record, its scoped `identity/` evidence and the canonical USB handoff.
- **Kernel:** `Drzet/linux:razr/usb-ptn3222@1e5268277f6d4c25cde2f3e2b3f00439107e087a`, tree `a4ea7bfa43182f6fddcae88601ee2be7b32c3923`. Direct history: accepted isolated base `61202a82ad004302fcc04e321075e190f00b29ed` → driver policy `d87632e89fbbfe090afa841796ef67bed5eea449` → separate binding-description correction `1e5268277f6d4c25cde2f3e2b3f00439107e087a`. Native commits pushed over SSH; no publication remapping or force update.
- **Changed kernel files:** `drivers/phy/phy-nxp-ptn3222.c`; `Documentation/devicetree/bindings/phy/nxp,ptn3222.yaml` (description only). Generic PHY core, SNPS consumer, tuning values, sequencing, cleanup, Kconfig and shared DTS are unchanged.
- **Fixed dependencies:** baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`; accepted integration `2b5acf108ae37040ac1e652e029bb37f5609e886`; PS5169 `4dcbc7ba1c04afea37ab0b0caf6b4c16bfcc3dfe`. No integration/image change.
- **Environment:** Python3.14.4; host GCC and ARM64 cross GCC15.2.0 (`Ubuntu 15.2.0-16ubuntu1`); four build jobs. Same reduced ARM64 [kernel.config](2026-10-14-usb-ptn3222-offline/kernel.config), SHA256 `789bbe87f9479e856cd8303545d28126dba0d0c0d77f20658039b05b8de940ef`. No fragments, dependency changes or tool installation.
- **Reuse/provenance:** existing upstream-derived PTN3222 adaptation and Motorola source remain attributed in the [canonical handoff](../../docs/handoffs/2026-10-13-usb-tenth-round.md). No new imported driver, proprietary firmware or generated kernel source is committed here.

## Policy and focused execution

The schematic names BUK, while the added numerical allowlist was supported only by CUK/GM and HUK documentation. `ptn3222_read_id()` now warns on readable IDs outside those documented values and continues the explicitly selected oneli profile. The diagnostic includes the assembled ID and revision; it does not identify the package or qualify the silicon. Each of the four identity-read errors still propagates and aborts before tuning. Write errors, rollback, cleanup/retry and profile-absent legacy behavior remain unchanged.

Commands (run before committing; hashes below establish identical committed source):

```sh
ASAN_OPTIONS=detect_leaks=0 GIT_NO_LAZY_FETCH=1 \
  python3 tests/usb/ptn3222/test_driver.py /tmp/razr-usb-ptn3222 \
  /tmp/razr-ptn3222-identity-before \
  --revision 61202a82ad004302fcc04e321075e190f00b29ed --identity-only
ASAN_OPTIONS=detect_leaks=0 \
  python3 tests/usb/ptn3222/test_driver.py /tmp/razr-usb-ptn3222 \
  /tmp/razr-ptn3222-identity-after
make -C /tmp/razr-usb-ptn3222 O=/tmp/razr-ptn3222-build \
  ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j4 modules
```

- **Before:** the new unknown-ID continuation assertion fails on exact61202a82. The runner returns250 from the C assertion abort, as expected; this is executed behavior, not a compilation failure. [Log](2026-10-14-usb-ptn3222-offline/identity/before.log), [result](2026-10-14-usb-ptn3222-offline/identity/before-result.json).
- **After:** **44 production-provider scenarios PASS**, with ASan/UBSan and leak detection explicitly disabled. [Result](2026-10-14-usb-ptn3222-offline/identity/after-result.json). Five synthetic unknown IDs (including a changed byte at each ID position, all-zero and all-one tuples) continue, log raw ID/revision, apply device tuning and balance teardown. No synthetic tuple is claimed to be BUK's ID. A documented ID with another revision continues without an unknown-ID warning. All four injected identity-read errors still abort before writes. The remaining cases cover documented CUK/HUK values, role replay, regulator/write failures, cleanup retries, missing providers and profile-absent legacy operation.
- **ARM64:** changed PTN3222 object compiled, **MODPOST and `.ko` link PASS**. [Module log](2026-10-14-usb-ptn3222-offline/identity/modules.log). The unchanged SNPS object/module is reused. No Image/full defconfig/combined build.
- **Patch style:** separate driver and binding patches each pass strict checkpatch with zero errors/warnings/checks: [driver](2026-10-14-usb-ptn3222-offline/identity/driver-checkpatch.log), [binding](2026-10-14-usb-ptn3222-offline/identity/binding-checkpatch.log). An initial combined diff elicited the binding-separate-patch warning; the delivered commits are separate. Whitespace checks clean.
- **Binding:** [comparison](2026-10-14-usb-ptn3222-offline/identity/binding-constraints.log) confirms every byte outside the profile description remains identical. Reuse existing dtschema2026.6 [2-positive/7-negative evidence](2026-10-14-usb-ptn3222-offline/schema-result.json); no schema/test replay. This comparison is not a fresh schema-validation result.

## Artifacts and limits

[Manifest](2026-10-14-usb-ptn3222-offline/identity/manifest.json) and [SHA256SUMS](2026-10-14-usb-ptn3222-offline/identity/SHA256SUMS) record source, tooling, config and log hashes. Locally computed hashes:

| Artifact | SHA256 |
| --- | --- |
| PTN3222 source | `2130a965f1f31d340e8279d64515979c8813664e906f77a92730487b4cb5827f` |
| Binding with updated prose | `f1c7bd0f17ea10b33de3ce6b217afb504e8160c0c88e9e5370de1adf96ebd611` |
| Changed PTN3222 module | `b490b1c51511a9bd0796f9c8b33f7319dc957aaf821e7bd3cd32cd11b58e9160` |
| Module.symvers (unchanged exports) | `23e17467b4dc6e379c2b4bf698d912a6d947f65d7b830f07482d53755eb0a605` |

Generated host harnesses/binaries remain in `/tmp/razr-ptn3222-identity-before` and `/tmp/razr-ptn3222-identity-after`; changed module remains under `/tmp/razr-ptn3222-build`. No hosted binary-store or artifact-download verification is claimed. No source changed after successful tests/build; commit messages and description-only binding update do not require an unchanged rebuild.

This executes actual production provider C with explicit host mocks for providers, GPIOs, regulators, regmap and delays. It is **host source execution and ARM64 cross compilation**, not kernel runtime, chip emulation or hardware. The full real regulator/GPIO internals, timing, electrical identity, enumeration and wake remain untested. No new BUK ID/compatible is invented. Read-only identity capture remains useful future evidence, not a numeric allowlist prerequisite under the authorized policy.

The accepted lifecycle dispatch tests, exact historical module results and local/published mappings remain in the [previous build record at5a9e2c5](https://github.com/Drzet/razr2022_nuc/blob/5a9e2c5f4fa743fd79580eac44ccd00379f0ed17/tests/results/2026-10-14-usb-ptn3222-offline.md). Those unchanged core/SNPS lifecycle tests and PS5169 tests were not rerun. No firmware execution, ramdisk/DTB/boot packaging, shared board changes or handset parameters are involved. Stop after publishing the bounded change and handoff for coordinator review.
