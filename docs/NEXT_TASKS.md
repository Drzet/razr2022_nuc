# Current assignments — 2026-10-17 wireless and CI maintenance

Supersedes previous queues. [Review](COORDINATOR_REVIEW_2026-10-16.md#latest-vpu--dp-delivery-review--2026-10-16-current) · [Status](STATUS.md) · [Policy](WORKFLOW.md).

## Active CI maintenance — all workflow owners

User reports Actions re-enabled on 2026-10-17. Automatic builds remain authorized for assigned work; the earlier temporary hold is superseded. Apply [automatic CI policy](WORKFLOW.md#automatic-ci-policy--user-decision-2026-10-17). No manual-only conversion or central dispatcher migration.

- **DisplayPort:** on current razr/displayport head, make expensive ARM64 validation depend on successful cheap production-host/schema checks; preserve automatic relevant-change triggers. Add workflow/branch-scoped supersession cancellation. Continue the existing dependency-complete build assignment. Diagnose any scheduling failure from repository/event evidence before changing triggers.
- **Boot:** consolidate razr-oneli-dt.yml and razr-oneli-fdt.yml so identical oneli DTB compilation is performed once and reused for schema/FDT checks. Preserve distinct assertions, pinned provenance and automatic relevant-change triggers. Retire the redundant workflow only after its checks are covered. Add scoped supersession cancellation. This workflow-only maintenance is independent of the active observability review; it does not select a new combined Image.
- **USB:** limited workflow-maintenance exception to paused status: inspect current owned workflow definitions, retire superseded candidate/durable prototype automation where current PS5169/PTN checks replace it, and combine duplicate checks for identical inputs. Cheap host/schema checks must gate expensive builds. Preserve automatic relevant-change triggers and add scoped supersession cancellation. Do not rebuild accepted unchanged drivers merely to reproduce old evidence or change driver/DTS code.
- **VPU:** limited workflow-maintenance exception to paused status: on the canonical razr/vpu-provenance-v5 branch, ensure cheap host/schema jobs gate expensive builds and avoid duplicate lifecycle checks. Add scoped supersession cancellation; retire superseded prototype automation without modifying frozen historical branches. Preserve all necessary checks and automatic relevant-change triggers. No RESUME implementation is activated.
- **Power / Wireless / GPU / Userspace:** apply this policy to workflows you own when needed for an assigned change; do not launch new extraction/build work solely for cleanup. Do not edit another owner's workflow.

Each maintenance owner inspects actual branch heads before editing, preserves intervening work, updates its existing handoff with retired/replacement workflows and exact commits, and stops after delivery. Evidence retention and acceptance criteria remain unchanged. Automated checks caused by these scoped maintenance changes are authorized; avoid redundant reruns. No repository-wide settings changes or cancellation of unrelated runs.

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

## Active independent review: Wireless — board integration contract

Project **razr/wireless@b0b6360e6c995671457e734a8e36b81d055b3036**; kernel **razr/wireless@2b5acf108ae37040ac1e652e029bb37f5609e886**. [Coordinator assessment](COORDINATOR_WIRELESS_REVIEW_2026-10-17.md). Existing source audit and firmware inventory accepted within their stated limits.

1. Update docs/handoffs/2026-10-16-wireless-oneli.md to remove physical PCI/HCI identity as a prerequisite for preparing a source-supported candidate. Mark compatibility [INFERRED]; runtime enumeration confirms or rejects it. No fabricated IDs or binding override.
2. Use existing six-FDT exports/oneli overlays and pinned Motorola source to refine PCIe0/UART20 routing, pin ownership, reset/wake and wrapper requirements. Check GPIO76–82/94/96/204 against existing oneli ownership. Report source-backed versus unresolved facts; no duplicate stock extraction.
3. Specify the minimal board-node and resolved-Kconfig requirements against the accepted kernel/bindings, including pre-enumeration power and shared PMU ownership. Power owns supply mapping and L7E conclusions; reference that delivery instead of independently deriving a competing rail contract.
4. Record standard Linux firmware deployment paths and runtime diagnostic collection. Let drivers select revision/filenames; Motorola inventory is fallback evidence for concrete failures. No custom board-data generation or further firmware download/disassembly.
5. Deliver one updated canonical handoff with exact commit, remaining dependencies and Boot/Userspace requests. Stop for coordinator review. No kernel/shared-DTS edits or build of unchanged drivers.

## Active independent review: Power — wireless PMU and antenna supply contract

Project **razr/power@b7d80a25a19b1a581880062463f468f1ce19f9ab**. Inputs: wireless b0b6360 handoff/manifest, accepted kernel 2b5acf108ae37040ac1e652e029bb37f5609e886, existing stock exports and Motorola kernel-devicetree@90fa7be1db5bd47202673d4431408659149a7359. Reuse existing Power provider work.

1. Map each of the upstream WCN6855 PMU's ten supply inputs to the source-supported oneli provider and parent; record voltage constraints and existing shared consumers. Resolve downstream S2E/S11B naming by topology/evidence, not spelling. Mark reference-board extrapolation [INFERRED].
2. Determine the source-supported function and ownership of L7E, named WLAN antenna-switch and BT ASD downstream. Establish how it should be supplied with existing Linux interfaces, or report the exact missing evidence/interface. Do not silently drop it, invent a PMU property or impose an unexplained always-on setting.
3. Review shared WLAN/BT power lifetime against existing pwrseq and hci_qca fallback behavior, including one radio remaining active when the other stops. Separate source guarantees from untested sleep/coexistence.
4. Update the existing canonical Power handoff with one supply/interface table and a definite ready-for-staging or named-gap conclusion. Post exact project commit to issue #9; stop for coordinator review. No driver/DTS implementation or hardware operation.
5. Prior USB/DP supply acceptance remains closed: no renewed BUK chip-ID or 8mV research; B_PLUS remains variable.

These reviews are source-only and use separate owner files. DP remains the sole implementation/validation stream; Boot's active observability work continues. This prepares wireless interfaces without starting dependent board implementation.

## Queued wireless consumers — not active yet

- **Boot:** after coordinator accepts Wireless/Power contracts and selects integration, apply shared PMU, PCIe Wi-Fi and UART Bluetooth board nodes/config on the Boot-owned DTS. Preserve UART7 diagnostics and existing rail consumers. Validate applicable bindings/DTB, pin ownership and dependency-complete ARM64 modules/modpost; record exact candidate/config/artifact identities. No physical-ID-before-staging gate; unresolved power connections remain explicit dependencies. Current active task is still observability.
- **Userspace:** after a selected kernel/config/firmware contract, package matching modules and ordinary Linux firmware with NetworkManager/BlueZ. Preserve per-device address provenance; no Xiaomi MAC/calibration or assumed persist layout. No rootfs rebuild now.

## Complete / paused / queued

- **VPU:** project adc83dc27be82d940df56317af3c1812e51f22fa source comparison accepted; kernel 905d2403c451838a408f6bb44e80a7cf9aa6ed10 cleanup acceptance retained. Paused. After DP closure, coordinator may select the narrow firmware/profile-scoped payload-free RESUME quirk. Preserve default encoding for other profiles; cover DRC/drain, ports/states, 64/68-byte serialization and queue errors. Motorola compatibility remains [INFERRED]. No VPU3/static-bandwidth transplant, silent startup reduction, probe enablement or repeated /3 proof.
- **Power USB/DP scope:** b7d80a25a19b1a581880062463f468f1ce19f9ab accepted; closed. New wireless source review is assigned above.
- **USB:** isolated PTN3222/PS5169 acceptance retained; paused. Unknown readable chip IDs diagnostic, failed reads abort.
- **GPU / Userspace:** paused; accepted inputs unchanged.
- **Battery/charging:** no implementation selected.

## Integration

Accepted kernel **2b5acf108ae37040ac1e652e029bb37f5609e886** and diagnostic-v2 artifacts unchanged. DP closure precedes selection of its integration. Boot alone owns shared DTS and specifically commissioned combined artifacts. VPU and external display are not prerequisites for an observable native boot. No handset Linux execution has occurred.

Preserve GLINK-only GPIO91, PS5169 enable GPIO19 and AUX GPIO2/71. Corrected Xiaomi audit is a qualified research input, not permission to import board layout, firmware or charging behavior.
