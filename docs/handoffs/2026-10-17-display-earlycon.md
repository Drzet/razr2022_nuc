# Display earlycon: isolated default-disabled port handoff

- **Date / agent:** 2026-10-17, GPU/display agent, coordinator assignment [`65ced806f29c3bf6ce661398b58504ccfdc0d174`](https://github.com/Drzet/razr2022_nuc/commit/65ced806f29c3bf6ce661398b58504ccfdc0d174).
- **Kernel:** [`Drzet/linux:razr/display-earlycon@5d9e2e7b5461ad421ad74fe2b0b1f79ca05f1fdf`](https://github.com/Drzet/linux/commit/5d9e2e7b5461ad421ad74fe2b0b1f79ca05f1fdf), isolated direct child of the specifically assigned accepted radio kernel **`7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce`**. No GPU or combined branch was advanced. Project branch `razr/display-earlycon` starts from coordinator `65ced...`; this is its one current handoff.
- **Evidence stages:** source-researched and implemented **yes**; exact production-predicate host tests **PASS**; targeted ARM64 kernel object compile **PASS**; full Image/modules **NOT RUN** (not assigned); native phone display/secure scanout **NOT TESTED**, QEMU framebuffer **NOT TESTED**.
- **Stop condition:** deliver generic port + focused evidence and halt before any board activation. Achieved.

## Scope, reuse and provenance

Closest source is Xiaomi Pad 6 Pro (liuqin), `yzddmr6/linux-sm8450-liuqin` revision [`fe81794b5e1b8a3f11a165f3acbfdb8fa671dbb3`](https://github.com/yzddmr6/linux-sm8450-liuqin/blob/fe81794b5e1b8a3f11a165f3acbfdb8fa671dbb3/drivers/tty/serial/earlycon-simplefb.c), original blob **`0a69b695c93c89421c99427a31af85ae98e5db58`**, GPL-2.0. Source Kconfig blob `e6b07f6c83f3d2415380dbac55f23874c8396046`, source Makefile blob `5239ff135932351b4eefa452644fe074a71e14fa`. It itself adapts the kernel's EFI framebuffer earlycon. The original's author identity was not asserted beyond the pinned repository; GPL SPDX and source provenance are retained.

Narrow alternatives reviewed: existing kernel `drivers/firmware/efi/earlycon.c` uses EFI `screen_info`, unlike the relevant flat-DT handoff; `drivers/video/fbdev/simplefb.c` and simpledrm/fbcon start later and do not replace this early-parameter console; archived generic framebuffer earlycon patch proposals exist (2022 Markuss Broks), not accepted as a current kernel option in our pinned tree. No blanket upstream/panel audit. No evidence that oneli firmware supplies a valid live `/chosen/framebuffer@` node. The mere reference splash carveout `0xb8000000/0x02b00000` does **not** establish scanout or safe framebuffer RAM ownership.

## Minimal kernel delta

All changes in [kernel commit `5d9e2e7`](https://github.com/Drzet/linux/commit/5d9e2e7b5461ad421ad74fe2b0b1f79ca05f1fdf):

1. `drivers/tty/serial/earlycon-simplefb.c`: GPL-2.0 port of Xiaomi's early `/chosen` simplefb driver, retained 32-bit `a8r8g8b8`/`x8r8g8b8` rendering and early WC/permanent WC mapping. Single enabled matching framebuffer is mandatory: skip `status=disabled` or malformed status and return `-EEXIST` on multiple enabled compatible nodes. Validate precisely one `reg` address/size tuple, inherit missing chosen cell counts from its root parent, translate address, reject malformed geometry/format before registering write, and avoid any deliberate splash-wide clear. No copied display geometry.
2. `drivers/tty/serial/earlycon-simplefb-check.h`: production predicates for exact NUL-terminated format/status lengths, nonzero 32-bit-aligned pixel geometry with **64-bit width×4 and stride×height**, reg and physical address overflow/size_t bounds, per-glyph offset and line/wrap fit. Exact predicates are shared with host tests; this is **not a separate unrelated test implementation**.
3. `drivers/tty/serial/Kconfig` and `Makefile`: new `CONFIG_SERIAL_EARLYCON_SIMPLEFB` opt-in ARM64 option with **no default y**. Build only if explicitly enabled and with `ARCH_USE_MEMREMAP_PROT`, font and serial dependencies. `earlycon=simplefb` and `keep_bootcon` would also be needed in a *separately approved* experimental boot. Kernel's `earlycon.c::setup_earlycon` has one `early_con` singleton, returning `-EALREADY` when registered; two `earlycon=` arguments are **not** simultaneous UART+framebuffer logging.
4. `tools/testing/selftests/simplefb-earlycon/geometry-test.c`: host tests compiled against **the exact production header**, including forbidden string truncation/non-NUL format, mock disabled status and multiple eligible nodes, oversized stride/width, insufficient span, base+span overflow, misalignment, glyph offsets and narrow-height wrap. Mock DT node enumeration **does not** run production libfdt traversal, and tests do not touch physical framebuffer memory.
5. `.github/workflows/display-earlycon-object.yml`: branch/path-filtered cheap host tests **before** installing ARM64 cross compiler, then default-off check, explicit configuration enablement and **only** `drivers/tty/serial/earlycon-simplefb.o` compilation. No Image/modules/dtbs rebuild.

**Lifetime review:** early scanout access uses `early_memremap_prot`; `early_initcall` transitions active bootconsole to `memremap(..., MEMREMAP_WC)`. A failed remap marks the console dead so late writes cannot invoke freed `.init` mapping functions. At `late_initcall`, a mapping is freed only if the console already unregistered; if `keep_bootcon` remains active, the WC mapping deliberately persists for its lifetime (and may leak after a later unregister, since this experimental console has no safe unregister callback). Font indices bound against `charcount`; glyph width/height verified before rendering; newline consumes input; impossible progress terminates rather than spinning in printk. No autonomous power/clock/DSI/display initialization.

## Validation: exact successful source, job and hashes

[GitHub Actions run **39058524964**](https://github.com/Drzet/linux/actions/runs/39058524964), job **117471377860**: **COMPLETED SUCCESS** on kernel **`5d9e2e7b5461ad421ad74fe2b0b1f79ca05f1fdf`**.

- Host GCC `-std=gnu11 -O2 -Wall -Wextra -Werror`, source-linked checker: **PASS: 34+ checks**. Invalid-DT entries are *mocked* buffers/statuses; no libfdt parsing execution claimed.
- ARM64 `defconfig` verified `CONFIG_SERIAL_EARLYCON_SIMPLEFB` **not enabled**. Explicitly enabled Kconfig, ran `olddefconfig`, checked both `CONFIG_SERIAL_EARLYCON_SIMPLEFB=y` and `CONFIG_ARCH_USE_MEMREMAP_PROT=y`, prepared kernel scripts and built only target object.
- `CC drivers/tty/serial/earlycon-simplefb.o` **PASS**. `readelf` confirms `Machine: AArch64`. Object SHA256 **`8403e4333918b01486d13262c22d368d486f54020602350f19eec26744c99554`**. No compiler warnings/errors in recorded job log.
- [Immutable run artifact 12110496278](https://github.com/Drzet/linux/actions/runs/39058524964/artifacts/12110496278): generated `.config`, object identity/hash evidence. Artifact ZIP SHA256 **`2a96fbd7273e2d7e9b45e7c5e6efaeb80a5f9fa3840e0ef87539b66d8bc7aafa`**.

## Shared files/integration and remaining gates

**No board DTS**, `sm8475.dtsi`, regulator, reserved-memory, bootargs, MDSS/DPU/DSI/panel, GPU enablement or Userspace artifact has been changed. The new kernel branch is a prototype only; Boot retains any future board enablement, cmdline and display handoff ownership, coordinator alone accepts integration.

Physical evidence needed **before** trying `earlycon=simplefb`: (a) active oneli bootloader framebuffer *physical base and ownership/reservation*, (b) verified width, height, stride, one supported pixel format and actual live scanout across Linux entry, (c) verified no overlapping allocations/overwrite, (d) observed earlycon lifetime with UART or other independent logging, and (e) actual on-device bootconsole/console handoff. [INFERRED] Even a valid stock splash buffer may cease scanning on kernel entry; no code can cure that without operating panel/display hardware, which is explicitly outside scope.

**Hold:** no phone access. Kconfig default disabled, no oneli DT node or bootargs, and no panel driver. Additional source validation desirable before hardware enablement is an actual production libfdt fixture test and physical WC mapping behavior; these were not claimed by the host check or object compilation. Stop for coordinator review.
