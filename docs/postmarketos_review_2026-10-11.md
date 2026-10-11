# postmarketOS source review
Date: 2026-10-11. Source review only; no packages built or device tests performed.

## Previous findings
The existing hardware database links the postmarketOS SM8450/SM8475/SM7475 wiki in the CPU driver record and open question C15 (firmware licensing/reproducibility). It contains no selected postmarketOS package, build workflow or verified oneli port. The current wiki URL redirects to Nura and direct access was blocked; indexed wiki content is older and is used only to discover source repositories.

## Repositories inspected

| Source | Exact revision | Scope |
| --- | --- | --- |
| [Official pmaports](https://gitlab.postmarketos.org/postmarketOS/pmaports/-/tree/0c45e6bc8007746f18fc608ae2f0cc40e9dd380e) | `0c45e6bc8007746f18fc608ae2f0cc40e9dd380e` | Current checkout, device package recipes and tooling packages |
| [pmbootstrap](https://gitlab.postmarketos.org/postmarketOS/pmbootstrap/-/tree/200f5123615808326ac796f66b02fdc6cebbcbf1) | `200f5123615808326ac796f66b02fdc6cebbcbf1` | Usage docs, argument parser and local-kernel packaging implementation |
| [SM8450 community pmaports](https://github.com/sm8450-mainline/pmaports/tree/057851da99cfbf63b44beefc0282a8603fec306a) | `057851da99cfbf63b44beefc0282a8603fec306a` | SM8450 kernel package and Nothing Phone 2 device package |
| [SM8450 community kernel](https://github.com/sm8450-mainline/linux/tree/bf1d29fced6e156dd6090a9b6600a8c44259c114) | `bf1d29fced6e156dd6090a9b6600a8c44259c114` | `next-new` head, Makefile, Qualcomm DT directory and SM8475 include |

## Concrete findings

1. **No ready oneli package located.** The official pmaports checkout contains no `oneli`, `sm8450`, `sm8475` or `waipio` references in device APKBUILD/deviceinfo files. Broader non-config searches did not locate such a port. The inspected community pmaports checkout also has no oneli match. This is scoped to these checkouts, not proof that no private branch, merge request or independent port exists.

2. **There is a reusable community SoC reference.** The community kernel contains [sm8475.dtsi](https://github.com/sm8450-mainline/linux/blob/bf1d29fced6e156dd6090a9b6600a8c44259c114/arch/arm64/boot/dts/qcom/sm8475.dtsi), layered on sm8450.dtsi. It changes USB HS PHY and UFS PHY nodes, controller compatibles, GPU OPPs and UFS clock tables. Its directory also contains `sm8475-nothing-pong.dts` and `sm8475-xiaomi-diting.dts`. These are source references, not verified Razr settings. The selected branch's Makefile reports 6.13-rc3; its head is dated 2025-01-11. It is not a replacement for our proposed 7.3-era baseline.

3. **Community packaging exists outside the official checkout.** [linux-postmarketos-qcom-sm8450/APKBUILD](https://github.com/sm8450-mainline/pmaports/blob/057851da99cfbf63b44beefc0282a8603fec306a/device/testing/linux-postmarketos-qcom-sm8450/APKBUILD) pins kernel commit `6a206d940546d791db1f98a63618f57ea5b10c00` and declares version 6.5.0. It builds an ARM64 kernel and installs modules and DTBs. This package does not use the community kernel's current next-new head.

4. **Nothing Phone 2 is a useful packaging example, not an oneli definition.** Its [deviceinfo](https://github.com/sm8450-mainline/pmaports/blob/057851da99cfbf63b44beefc0282a8603fec306a/device/testing/device-nothing-pong/deviceinfo) selects `qcom/sm8475-nothing-pong` and Android boot-image generation; its APKBUILD depends on the community kernel, mkbootimg, Mesa, dynamic-partition mapping and qbootctl. Its modules-initfs file is only template comments. Do not copy its offsets, partition paths, boot header or module list into a Razr package.

5. **pmbootstrap accommodates our separate kernel repository.** At the pinned revision, `pmb/parse/arguments.py` exposes `--aports` for a local package tree and `build --envkernel` for packaging a locally built kernel. `pmb/build/envkernel.py` explicitly handles kernels cross-compiled on the host and expects the appropriate build output directory. This permits kernel development in Drzet/linux with packaging maintained separately; no second kernel source copy is needed.

6. **Initramfs/image tooling already exists.** The official `main/postmarketos-mkinitfs/APKBUILD` packages version 2.11.1 and depends on boot-deploy >=0.23.0. pmbootstrap's usage documentation covers installation-image generation and export. Reusing this tooling is preferable to immediately writing a custom equivalent, subject to verifying oneli boot inputs. Tooling availability does not establish a working Razr boot path.

## Recommendation
Keep Drzet/linux as the kernel source of truth. First compare the community SM8475 device-tree and supporting changes against the proposed upstream baseline, preserving only still-needed changes as attributable commits. This comparison is outstanding; this review did not audit the whole community kernel delta.

Evaluate a small local pmaports package set for oneli and our kernel, driven by pinned pmbootstrap/pmaports revisions. Track local package definitions under a future `packaging/postmarketos/` directory in the coordination repository, and use a separate generated pmaports checkout for builds. No extra fork is required unless ongoing package maintenance makes it useful.

Keep oneli-specific image parameters unresolved until verified from Motorola boot artifacts. Boot tooling and initial userspace can be reused without choosing Alpine as the permanent desktop distribution.

## Next work
- Boot workstream: compare community sm8475.dtsi and its dependencies against the selected upstream commit.
- USB/GPU workstreams: review relevant community changes for missing functionality and obsolete workarounds.
- Packaging: validate a minimal local device/kernel package against current pmbootstrap; then decide adoption.
- VPU: this review supplies no new confirmed decode implementation.
- ThinkPhone/bronco is listed in the indexed wiki as another SM8475 device, but no bronco source was inspected here; treat it as a follow-up lead.

No kernel baseline selection, kernel changes, packages or boot images were created by this review.
