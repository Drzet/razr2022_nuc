# Build record: PTN3222 core/SNPS lifecycle correction

- Date: 2026-10-14; assignment/review from coordinator main `9c77e4f928e7332d8ecc1a5b12fa34bcf18ca0c4`, [review](https://github.com/Drzet/razr2022_nuc/blob/9c77e4f928e7332d8ecc1a5b12fa34bcf18ca0c4/docs/USB_REVIEW_2026-10-14.md).
- Project repository base: `razr/usb@2b64829bd78478a89e18d5bd50952f7a72e3f0c5`; updated production tests and this record are included in the delivery identified by the canonical handoff. Test script/dependency hashes are in the result JSONs.
- Kernel repository / branch / exact commit: published **`Drzet/linux:razr/usb-ptn3222@61202a82ad004302fcc04e321075e190f00b29ed`**, parent **`d513929e8c1ef2ea7f5158ebfb57fda99ff531e9`**. Tested local commit **`c071561e5fbdf01e757e58935ef43df8d47a480e`** has the exact same full tree **`d8151528d81c04e4fdd0a139d78a62322fcb9852`**. Publication reused the established GitHub connector fallback, with expected-head non-force update; no repeated SSH probes or historical author reconstruction. Native local authorship/history and original source attribution remain preserved.
- Upstream baseline: `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.
- Board-support/subsystem changes: only PTN3222 and the demonstrated adjacent SNPS common lifecycle path. No generic PHY core, DWC3, binding, Kconfig, board/SoC DTS, PS5169 or accepted integration change.
- External patches/reuse: retain the existing reviewed adaptation. Execute unchanged production generic PHY core dispatch/count bodies from the pinned source; no new identity/datasheet/reuse survey or external patch import. Original driver/source authorship retained.
- Host/build environment: Ubuntu 26.04.1 amd64; Python 3.14.4; distribution GCC and ARM64 cross GCC 15.2.0 (`Ubuntu 15.2.0-16ubuntu1`). Four compile jobs. Cross compilation and host mock execution, not ARM64/handset execution.
- Architecture/configuration: **existing reduced ARM64 configuration**, [kernel.config](2026-10-14-usb-ptn3222-offline/kernel.config), SHA256 **`789bbe87f9479e856cd8303545d28126dba0d0c0d77f20658039b05b8de940ef`**; no fragments or configuration change. Original tinyconfig options and initial Image/modules build are retained in the [prior build record](https://github.com/Drzet/razr2022_nuc/blob/2b64829bd78478a89e18d5bd50952f7a72e3f0c5/tests/results/2026-10-14-usb-ptn3222-offline.md).
- Firmware: none included or executed.

## Commands and results

```sh
python3 tests/usb/ptn3222/test_lifecycle.py /tmp/razr-usb-ptn3222 \
  /tmp/razr-ptn3222-lifecycle-before \
  --revision d513929e8c1ef2ea7f5158ebfb57fda99ff531e9 --expect-failure
python3 tests/usb/ptn3222/test_lifecycle.py /tmp/razr-usb-ptn3222 \
  /tmp/razr-ptn3222-lifecycle-after
python3 tests/usb/ptn3222/test_driver.py /tmp/razr-usb-ptn3222 \
  /tmp/razr-ptn3222-host-closure
make -C /tmp/razr-usb-ptn3222 O=/tmp/razr-ptn3222-build \
  ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j4 modules
```

**Failing-before evidence:** [before results](2026-10-14-usb-ptn3222-offline/lifecycle/before/lifecycle-result.json), [init retry](2026-10-14-usb-ptn3222-offline/lifecycle/before/init-retry.log), [reconnect](2026-10-14-usb-ptn3222-offline/lifecycle/before/reconnect.log). The exact published candidate is read from existing Git objects, without changing checkout/branches. Both executable cases return **1** for a violated recovery assertion; the `--expect-failure` runner returns 0 only after confirming those failures.

| Actual production-dispatched case | Before at d513929 | After correction |
| --- | --- | --- |
| Init write error plus transient provider cleanup failure; normal repeated core init | First `-EIO`; outer/inner counts 0/0, reset asserted, both repeater votes retained. Retry `-EBUSY`, no recovery. | First error remains `-EIO`. Retry safely finishes cleanup then initializes: counts 1/1, one vote per rail, reset released; final exit balances all counts/votes. |
| Successful init, repeater cleanup failure on exit, consumer reconnect | Consumer exit 0, outer/inner counts 0/1, reset asserted. Reconnect falsely returns 0 with counts 1/2 and faulted/reset provider. | Consumer's own teardown completes; its repeater reference is retained. Reconnect drains pending exit then genuinely initializes: counts 1/1, reset released; final exit balances all counts/votes. |

**Production core/consumer-dispatched execution PASS:** [after results](2026-10-14-usb-ptn3222-offline/lifecycle/after/lifecycle-result.json): **12 cases**. The harness compiles exact production `phy_init`, `phy_exit`, `phy_set_mode_ext`, SNPS common init/exit/set-mode and cleanup helper, plus the production PTN3222 code. It does not hand-copy or simulate dispatch/count arithmetic. PHY/device structs, PM/locking, regulators, clocks, resets, delays, regmap and the SoC-specific PHY init hook are scoped host mocks. The generic core source hash remains **`2535dc20688c48082b30f2498a05931897dc7b5db902bb02c5f5322d31c80117`** before and after.

Cases cover both regressions; persistent disable errors returning `-EAGAIN` without successful init or duplicate votes; a voltage-vote cleanup failure; later clock/reset-assert/reset-deassert/SoC-init failure with failed repeater unwind while preserving original `-ETIMEDOUT`; legacy profile-absent behavior; optional absent repeater; two nested outer references with one owned inner reference; and host/device replay through actual core/SNPS mode dispatch. Successful cleanup follows transient failures without unbind, direct provider exit or generic core changes. ASan/UBSan and leak detection passed outside the sandbox with approved process metadata access.

**Direct-provider unit execution PASS:** [direct result](2026-10-14-usb-ptn3222-offline/lifecycle/direct-result.json), **37 scenarios**. The earlier direct callback recovery assertion was corrected for init-driven cleanup retry. These tests remain provider-level tests; they are not evidence of consumer-reachable recovery by themselves.

**Focused ARM64 compilation/linkage PASS:** [modules.log](2026-10-14-usb-ptn3222-offline/lifecycle/modules.log) contains both changed module compiles, **MODPOST**, and both `.ko` links. No configuration/dependency change required a new Image, full defconfig/combined build, or PS5169 build. Compilation ran before creating local c071561e; committed file bytes match executed/compiled inputs, so no unchanged rebuild followed commit/publication.

**Schema reused:** binding byte-for-byte unchanged from d513929, SHA256 **`a663388f2104a9da9cf02038255f8cb7c4b2043ea3d244ea04df6d51037666db`**. Reuse the existing dtschema 2026.6 [2-valid / 7-invalid result](2026-10-14-usb-ptn3222-offline/schema-result.json); no schema rerun/tool installation. `git diff --check` and strict checkpatch on the kernel patch passed with 0 errors/warnings/checks.

## Recovery contract and returned errors

PTN3222 retries recorded cleanup at init when faulted, before any new voltage/enable vote. A persistent cleanup failure preserves the fault and returns that actual provider error; the first initiating init/tuning error remains intact. Its exit still returns cleanup errors and PHY core retains the inner count accordingly.

SNPS explicitly records its outstanding repeater init reference, retains it after failed exit/unwind and retries that exit **before** acquiring its own resources or calling repeater init. Its completed own-resource teardown continues to return 0 while logging deferred repeater cleanup. Returning a negative outer exit error would pin outer `init_count` at 1 and cause the next core init to bypass SNPS too. Pending cleanup errors propagate on the next initialization, with outer count remaining 0. This is intentional deferred cleanup, not a claim that every electrical resource switched off successfully.

## Image preparation

Not applicable. No new Image, ramdisk, DTB selection, boot package or handset parameters. The prior Image remains an initial compile artifact, not an image of this correction.

## Artifacts

[Manifest](2026-10-14-usb-ptn3222-offline/lifecycle/manifest.json) and [SHA256SUMS](2026-10-14-usb-ptn3222-offline/lifecycle/SHA256SUMS) record locally computed metadata/log hashes. Changed outputs:

| Artifact | Locally computed SHA256 |
| --- | --- |
| phy-nxp-ptn3222.ko | `6f50cbfb8d65c8c6aef2ed880991f29f14784b28a7a1ddc8f00e25e0bbdaaaa7` |
| phy-snps-eusb2.ko | `213f78c708673c2186315c0fa756af43705d9f22436fc1cde54c4417d6af02c0` |
| Module.symvers | `23e17467b4dc6e379c2b4bf698d912a6d947f65d7b830f07482d53755eb0a605` (unchanged exports) |
| Local closure archive | `da77931115fe15998aff1ca83538b14c3d451303ac169deb1de3bda201b94b2b` |

Local archive `/tmp/razr-ptn3222-lifecycle-2026-10-14.tar.xz` is 85,072 bytes and includes generated before/after harnesses, logs, changed modules and a native local-commit Git bundle requiring d513929 as prerequisite. Native commit metadata is also recorded in [local-commit.txt](2026-10-14-usb-ptn3222-offline/lifecycle/local-commit.txt). No binary payload or generated kernel source/harness is committed to this evidence repository; no hosted CI/binary-store claim is made. Initial compile/schema evidence remains linked above rather than duplicated.

## Device validation and exact limits

**Not tested on hardware.** This executes the specified source control flow under host mocks; it does not execute kernel PM/mutex/regulator internals, SoC MMIO, clock/reset electrical behavior, or concurrent independent consumers of a repeater. Nested references of one SNPS consumer are tested. Unchanged SNPS own-rail disable-error handling and SNPS/DWC3 role-error/caching behavior beyond this cleanup boundary are not repaired or claimed verified. Persistent physical cleanup failure remains a logged, retained fault with failed reconnect until cleanup can succeed.

Experimental profile ABI and board graph remain unselected; populated part remains [INFERRED]. Hardware identity, GPIO7 polarity/function, rail parents/physical transitions, enumeration and wake await the phone. Accepted integration is unchanged. This is the bounded lifecycle correction deliverable for coordinator review, with no further task activated.
