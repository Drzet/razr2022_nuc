# Current assignments — 2026-10-16 latest delivery review

Supersedes previous queues. [Review](COORDINATOR_REVIEW_2026-10-16.md#latest-vpu--dp-delivery-review--2026-10-16-current) · [Status](STATUS.md) · [Policy](WORKFLOW.md).

## Active: DisplayPort — validation closure

Project **razr/displayport@eb01acfb7dd1e177735de7a30151197a0b2647fb**; kernel **razr/displayport@5499623959199a0fc5a8c76398e1708107fefc3a**. Preserve these commits and append any required workflow correction. Source/lifetime direction and Xiaomi comparison accepted; implementation acceptance awaits complete ARM64 build evidence.

1. Correct .github/workflows/razr-gpio-sbu.yml so the selected ARM64 configuration explicitly produces matching built-in provider symbols before ordinary module modpost/link. Fresh defconfig plus make modules alone does not guarantee vmlinux.o/Module.symvers. Use vmlinux or a demonstrated equivalent matching build dependency; real regulator/Type-C/GPIO providers, no fake symvers or unresolved-symbol suppression.
2. Pin dtschema (coordinator used 2026.9) and record actual compiler/tool versions, exact kernel SHA and config hash. Execute changed ARM64 object/module/modpost/link and preserve logs, resulting module hash and dependency evidence. No full Image packaging or shared-DTS change.
3. Run binding examples and the submitted exact dtc fixture runner in a working environment. Coordinator already passed binding document/schema validation and four equivalent libfdt-generated instances; these are not a claim that the exact runner ran.
4. Reuse unchanged production host evidence: independent 11 cases / 237 assertions PASS. Repeat only if relevant driver/test bytes change. No broad source research, replacement driver or DRM/QMP/GLINK patch.
5. Update existing canonical DP handoff with exact project/kernel commits and evidence; post to issue #11 and stop for coordinator acceptance.

WAS7227Q-10/TR reference identity and installed-board [INFERRED] qualification remain. willsemi prefix already exists. Preserve property-absent legacy behavior and shared L2B contract. Board enablement, parent rails and system-sleep behavior are separate.

## Active independent review: Boot — early-output observability

Project **razr/boot@b2f9aea38b5581781e8b07aa98a85dbbeddaa237**; accepted MBM research **0acccb329521d91b84fdcfb4bf9d7dcc25f44a25**. Accepted integration and diagnostic-v2 manifests remain inputs, not new build assignments.

1. Inspect existing stock exports/manifests and accepted source evidence for framebuffer/splash and ramoops. Record proven address/size/format/stride, reserved-memory ownership and handoff/retention/readback properties where present; explicitly mark absent or runtime-dependent fields. Never guess addresses or copy Xiaomi layout.
2. Check only relevant existing final-FDT/stock-DTBO symbol and reserved-memory requirements. Reuse corrected MBM results; no repeated disassembly, firmware retrieval/extraction or repackaging.
3. Recommend the best evidenced early-output route and smallest missing device observation. UART TX GPIO26 ball D24 and RX GPIO27 ball C24 are recorded; physical pads/connector and electrical access remain unidentified. An evidenced equivalent output route is acceptable; UART wiring is not a mandatory gate.
4. Update existing docs/oneli_native_loader_output_decision_2026-10-12.md, configs/oneli-native-loader-readiness-v1.json and canonical Boot handoff. Distinguish source inspection from runtime verification. Post exact project commit to issue #12 and stop.
5. No shared-DTS enablement, new kernel/boot artifact, flashing or phone operation.

Concurrency is bounded: DP repairs validation tooling; Boot reviews independent existing evidence to advance first-boot logging. Their files and interfaces are independent.

## Complete / paused / queued

- **VPU:** project adc83dc27be82d940df56317af3c1812e51f22fa source comparison accepted; kernel 905d2403c451838a408f6bb44e80a7cf9aa6ed10 cleanup acceptance retained. Paused. After DP closure, coordinator may select the narrow firmware/profile-scoped payload-free RESUME quirk. Preserve default encoding for other profiles; cover DRC/drain, ports/states, 64/68-byte serialization and queue errors. Motorola compatibility remains [INFERRED]. No VPU3/static-bandwidth transplant, silent startup reduction, probe enablement or repeated /3 proof.
- **Power:** b7d80a25a19b1a581880062463f468f1ce19f9ab accepted and paused. PTN 3.075–3.300V request selects 3.080V; 8mV difference is non-blocking. No renewed BUK identity gate. B_PLUS is variable.
- **USB:** isolated PTN3222/PS5169 acceptance retained; paused. Unknown readable chip IDs diagnostic, failed reads abort.
- **GPU / Userspace:** paused; accepted inputs unchanged.
- **Battery/charging:** no implementation selected.

## Integration

Accepted kernel **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. DP closure precedes selection of its integration. Boot alone owns shared DTS and specifically commissioned combined artifacts. VPU and external display are not prerequisites for an observable native boot. No handset Linux execution has occurred.

Preserve GLINK-only GPIO91, PS5169 enable GPIO19 and AUX GPIO2/71. Corrected Xiaomi audit is a qualified research input, not permission to import board layout, firmware or charging behavior.
