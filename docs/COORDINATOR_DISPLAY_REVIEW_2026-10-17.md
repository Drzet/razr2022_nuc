# Internal-display audit: coordinator decision — 2026-10-17

Input: full feasibility audit supplied by the user in the coordinator conversation on 2026-10-17. Accept its separation between firmware framebuffer reuse, late native DRM console and unproven oneli display continuity. A reference splash reservation is not a usable framebuffer contract. Native panel implementation is not selected.

Coordinator independently read Xiaomi earlycon-simplefb.c at **fe81794b5e1b8a3f11a165f3acbfdb8fa671dbb3** through the GitHub connector. This confirms flat-DT chosen-node parsing, 32-bit pixel rendering, early mapping then WC remap, and no panel initialization. ThinkPhone/Edge panel and upstream-status assertions in the supplied audit were not independently re-audited here and are not implementation inputs for this task.

Concrete source review findings:
- Stride validation compares against **fb_width * 4** in u32 arithmetic, permitting overflow before comparison. This needs checked/widened arithmetic and downstream bounds review.
- Format comparison uses strcmp on the DT property without validating a terminating NUL within the supplied length.
- First compatible framebuffer child is selected without checking status; a disabled placeholder must not activate writes.
- Address/span and offset arithmetic, multiple-node selection, early/permanent mapping lifecycle, font bounds and console coexistence require focused review. DT reg describes an extent; it does not establish physical ownership/reservation or continued scanout.

Decision: offline review and a default-disabled generic port may proceed now. Hardware handoff evidence gates adding an oneli framebuffer node/bootargs and executing writes, not code inspection or a disabled compile. Use a separate branch and preserve UART-first baseline. No copied Xiaomi geometry, display clocks, DSI panel or GPU enablement.

Assign GPU/display agent (not DisplayPort) the bounded task in NEXT_TASKS. Its implementation is independent of Userspace's frozen-artifact QEMU test. Boot retains shared board DTS and eventual experimental boot configuration ownership. First panel trial remains conditional on measured/recovered oneli geometry, format, stride, valid reserved RAM and active scanout across entry. Native DRM/panel support remains a later decision.
