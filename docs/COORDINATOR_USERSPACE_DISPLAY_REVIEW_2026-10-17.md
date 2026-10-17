# Userspace and earlycon review — 2026-10-17

## Decisions

- Accept Userspace tested source **e5de7e3961bf16fe65fd599514a6804316ef5a49**, handoff **f84d71e5e126d9f74a43b555a3062a3c3c153767**, for actual prepared-Debian QEMU runtime scope. Assign the concrete reported regulatory database gap.
- Accept GPU/display kernel **5d9e2e7b5461ad421ad74fe2b0b1f79ca05f1fdf**, handoff **401d2d8006707a4f7c2ebb11d03ac2b465916d3f**, for isolated default-disabled source/predicate/object scope. Pause; no integration or hardware activation.
- Accepted radio kernel **7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce**, original radio rootfs and diagnostic-v2 remain immutable. No handset result is established.

## Userspace evidence and assessment

Coordinator read preparation/guest assertion scripts, canonical handoff and actual job log for [run 39058718000](https://github.com/Drzet/razr2022_nuc/actions/runs/39058718000), runtime job **117472034308**. Actual log ends RADIO_ROOTFS_QEMU_SMOKE_PASS and successful upload. The host verifier requires guest systemd PID1, exact release, early pre-power presence, actual hci_uart module presence, D-Bus, NetworkManager, address/default route/resolver and successful DNS lookup, zero reported failures and clean poweroff. Test-only changes are confined to the disposable disk/initramfs. No kernel compilation or Debian reinstall occurs.

Owner independently inspected the serial artifact and reports DHCP 10.0.2.15/24, default gateway 10.0.2.2, NetworkManager-created resolv.conf with 10.0.2.3, successful DNS, and BlueZ unit present but inactive without a virtual BT controller. Coordinator inspected enforcing code and CI result, not a fresh artifact extraction. Earlier failures were root-owned disk permission and reuse of unavailable dummy-module fixture; correction to existing hci_uart tests actual selected ABI without modifying the kernel.

Artifact **12110358882**, ZIP **c8e72dd6576ad18fd19e66da8c7c7379f387fcfb0e8d4dcad9e9ea4f91c98382**: upload digest independently read from CI; 14/14 internal verification is owner evidence. QEMU does not test oneli radio or storage.

The handoff explicitly records cfg80211 failing to find regulatory.db (-2). Firmware-atheros staging alone does not close this reported request. Assign confirmation from existing serial and signed Debian regulatory database packaging; do not label it hardware failure or silently omit it from readiness. One focused acceptance check follows the changed package; no unchanged broad smoke round.

## Early framebuffer console evidence and assessment

Coordinator read full production source/shared predicate header, Kconfig/Makefile/workflow delta and actual [run 39058524964](https://github.com/Drzet/linux/actions/runs/39058524964), job **117471377860** log. Previously identified width arithmetic and format/status handling are corrected. Geometry uses widened multiplication, span/end bounds and glyph-fit checks; only one enabled framebuffer is selected. Mapping failure prevents later init-only calls. Source includes no board geometry, DTS enablement or panel initialization. Option has no default y.

Actual host result: **34+ checks on production predicates**, with DT enumeration mocked. Object target compiled as ARM64; object SHA256 **8403e4333918b01486d13262c22d368d486f54020602350f19eec26744c99554** recorded by owner/CI. Artifact **12110496278**, upload ZIP **2a96fbd7273e2d7e9b45e7c5e6efaeb80a5f9fa3840e0ef87539b66d8bc7aafa** independently read from CI. No full image/link, real libfdt traversal, framebuffer rendering execution or physical scanout test.

Evidence limitation: upload names out/.config without include-hidden-files; default uploader behavior omits hidden files. The 494-byte ZIP must not be presented as a full resolved-config archive. Config assertions and object build exist in the job log. Also missing workflow concurrency cancellation; address both in next source-task workflow maintenance, without another build now. Retained WC mapping after later console unregister is a disclosed experimental lifetime limitation, not hidden qualification.

Before actual integration/enablement, test production parser fixtures and reconcile memory ownership, bootloader framebuffer geometry/format and continued scanout. These facts cannot be inferred from a shared splash address. Only one earlycon singleton is selected; UART fallback means a separate configuration, not two simultaneous earlycon arguments.

## Next work

Userspace owns the sole new implementation task: signed regulatory database correction. GPU/display pauses with the disabled prototype. Boot has no new build/packaging task. VPU RESUME and configuration reduction remain queued; no new full kernel build is justified by this review.
