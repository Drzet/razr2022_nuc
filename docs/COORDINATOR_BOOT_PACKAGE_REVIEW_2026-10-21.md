# Coordinator Boot packaging review — 2026-10-21

## Decision

Accept **cddb2bf99f3893865ddbd9498bb35697fa33f45d** for offline packaging delivery; tested code/workflow **31d75a7d784e6ed7d6d107ef2b8d2e808da13a48**. No kernel rebuild or new package is required. This is not hardware acceptance.

Coordinator inspected the packaging script, workflow, canonical handoff, launch decision, successful job **119173118766** logs and artifact metadata for run **39585458990**. Logs show exact input checks, v4 round-trip, separately pinned AOSP unpack/repack component comparisons and nine member checksum passes. Artifact **12338654148** is available, 13,753,327 bytes; GitHub digest matches Boot's reported ZIP SHA256 **ad38b4167b36e7ff73baf5d82efcdd5e5fd9dafe35e8c91787e0d07953afbff8**. Coordinator did not independently download/re-hash the ZIP in this review; Boot reports doing so.

| Output | Bytes | SHA256 |
| --- | ---: | --- |
| boot-v4 | 37,462,016 | f564b46465a654ce5130095ed039f08e1ffcf7659b0d162ddb8e92f203f73d1f |
| vendor_boot-v4 | 122,880 | f866638f2975355ee3a9c415dd8a40b114b3468d0c1528f73b13966f26e28b61 |

[Download bundle](https://github.com/Drzet/razr2022_nuc/actions/runs/39585458990/artifacts/12338654148).
[Boot launch decision](https://github.com/Drzet/razr2022_nuc/blob/cddb2bf99f3893865ddbd9498bb35697fa33f45d/docs/oneli-reduced-native-diag-launch-decision-2026-10-21.md).

## Findings and next decision

The package correctly reuses accepted reduced Image, DTB and diskless early ramdisk. Generated vendor_boot carries the mainline DTB and empty vendor fragment; it is not stock Motorola vendor_boot. The handset command line excludes the QEMU shutdown flag. Image runtime size is larger than file size; the reported nominal budget is a structural constraint, not a physical placement proof.

The launch decision identifies the remaining gap but does not resolve it: existing disassembly proves a fastboot boot handler, not the origins of vendor_boot/DTB/DTBO for downloaded v4 images. The report supplied no new call-path evidence settling this question. This was permitted by the packaging stop condition; it is now the next bounded investigation.

Do not require successful runtime logs as a prerequisite for designing the first experiment that obtains them. Separate loader behavior resolvable from source/binary analysis from observations made during an eventual trial. A RAM-only route is preferred, not assumed to exist or imposed as the only conceivable installation route. A partition-writing alternative may be designed offline with rollback; execution remains separately authorized.

Boot alone is assigned the exact loader-composition investigation in NEXT_TASKS. All other agents remain paused. Prior accepted releases are unchanged.
