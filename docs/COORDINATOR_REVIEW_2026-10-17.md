# Coordinator delivery review — 2026-10-17 morning

## Disposition

| Owner | Reviewed delivery | Decision |
| --- | --- | --- |
| DP | Kernel d28598f544682eed5997ac9d57d423e9a5031624; project 60fbc3a3dbc28d173cc67e632f57f25d99a3e58e | AUX driver/binding accepted for isolated source/build scope; ARM64 gate closed. Project handoff needs final CI result. |
| Boot | Project 638a9d7989617783e2d2112847ca293cf08773a4; kernel 7d30153d3b2d890a42b48b6b12bcc8e9fcc7810e | Observability review and CI consolidation accepted. |
| Wireless | Project af57d1a8dc626992843079d987d49ac5338d780f; kernel unchanged at 2b5acf1 | Source transport/config contract accepted with qualifications below. |
| Power | Project b8e85bbe4936814d29ac1db770e2b286c69e9dca | Wireless supply proposal and identified L7E consumer gap accepted for development. |
| USB | Project 3c949fed4e79c8aea081a193b6fa6b9d89dbaed5; kernel PS5169 57d4d32b614cf23c2d9f60cdb06daa30870d7b61 and USB 305bc34cac710adc9fe7c4794a6e909abdf83ee0 | Scoped CI maintenance accepted; previous functional acceptance unchanged. |
| VPU | Project ac293ee4c22e4407d53f03ed55809da1b3eeddf4; kernel c31880525671f65c2d10d8d60d2ab9475c0797e4 | Scoped CI maintenance accepted; production source remains accepted 905d2403. |

Accepted integration remains **2b5acf108ae37040ac1e652e029bb37f5609e886**. No handset boot, radio operation, DP output or new integrated artifact is claimed. GPU/Userspace had no new assigned implementation delivery to accept.

## DP: previously missing build evidence now present

Coordinator inspected exact current workflow, final correction diff, Actions job results and actual host/schema/ARM64 logs for [run 38987006218](https://github.com/Drzet/linux/actions/runs/38987006218), SHA d28598f. Cheap job **117260700595** passes 11 cases / 237 assertions, binding examples and all four exact submitted schema fixtures. ARM64 job **117261174622** runs only after that gate and passes matching vmlinux provider exports, ordinary modules MODPOST/link, AArch64 module identification, vermagic and unchanged config comparison. Previous failed run 38985439713 is superseded, not erased.

The final correction checks vmlinux.symvers immediately after vmlinux and Module.symvers after modules. This closes the earlier source-traced dependency gap; no fake symvers or unresolved-symbol suppression found in the inspected workflow.

CI-reported hashes, read from the actual log:
- gpio-sbu-mux.ko: **6717c84e3d4f8f2d93a54666471181702fdd7d2f6bed32777873babe2d7b7c05**
- Module.symvers: **f46edb2a83b837e02e790a25c54ddf1fb8d46fb9eb492f28ff73617cf275e124**
- Config: **0bedc70610221d4995877520dfc57f23bec865cb7cd4696f29eaa0883970ebd3**
- Module/log artifact: **12084757955**, run 38987006218.

Coordinator did not independently rebuild or download/hash the binary. This accepts isolated software/build scope, not board power, Type-C/DP runtime or suspend. Current project handoff still ends at the obsolete Actions hold; owner must append the successful final evidence and current acceptance without another build.

## CI maintenance

Reviewed VPU and USB maintenance diffs, Boot consolidation/removal diffs and retained workflow, plus live job status:
- Boot run **38985421619**, job 117256042049: success. One compiled DTB serves preserved schema and FDT checks. Actual log inspected; no relevant schema/compiler failure observed. Prior run 38985414833 cancelled as superseded.
- VPU run **38985925553**: source detector and consolidated host job succeed; ARM64 correctly skipped for workflow-only change. Production files unchanged from 905d2403. Before/after push comparison replaces HEAD-only selection.
- USB run **38986262436**: cheap checks succeed; ARM64 correctly skipped. SNPS schema runs also succeed. Before/head detector replaces unreliable event-commit text inspection. Necessary conditional/probe assertions retained; retired import/prototype definitions do not change accepted driver code.

Existing owner local-test/hash and workflow-disable receipts remain attributed owner evidence; coordinator did not repeat unchanged suites or independently reread administrative workflow states. Automatic relevant-change builds, cheap gates and scoped cancellation remain policy. CI cleanup assignments close; do not keep expanding workflow work after its deliverable.

## Boot observability

Accept the source and metadata review. Owner reused archived stock FDT metadata and accepted compiled DTB/config, with recorded hashes; coordinator read the canonical evidence/limitations, not a fresh extraction or independent repeat of the binary parser.

Stock-reference ramoops 0xae000000 + 0x60000 and splash 0xb8000000 + 0x2b00000 are reservations, not proof of usable runtime logging or active framebuffer. Owner reports no overlap with the 39 static native reserved ranges; final RAM, runtime reservations and retention remain unknown. Accepted config has PSTORE_RAM=m, PSTORE_CONSOLE=n and no ramoops node. No usable simple-framebuffer handoff was established.

UART7 is the best evidenced first output route, conditional on accessible TX/ground and measured logic level. Physical pads remain unknown. Another demonstrated output route is acceptable. No more broad source investigation, repeated packing or blind ramoops/simplefb enablement is selected. Native entry/logs are future test outcomes, not evidence required before planning a controlled trial.

## Wireless / Power

Coordinator reviewed both current handoffs. Wireless now uses existing stock FDT metadata to corroborate transport/pins, removes the physical-ID-before-staging gate and specifies normal driver-selected firmware deployment. Stock-export inspection and Debian package inventory are owner evidence; installed hardware remains **[INFERRED]**.

Independently re-read accepted-kernel pwrseq-qcom-wcn.c and qcom,qca6390-pmu.yaml: WCN6855 uses a fixed ten-supply list, common bulk enable/disable and no explicit voltage request; optional vddasd is schema-permitted but absent from that list. Power's L7E vendor-consumer finding is consistent with the Motorola cape source previously independently inspected. A declared supply alone would not add its active management. Select a narrow existing-driver extension, subject to a focused maintained-upstream/pending-series reuse check.

Two qualifications:
1. **Voltage:** 0.500V provider initial value versus a radio request above 1V is not a hardware contradiction. The integration must encode the required active constraints/votes. Use reviewed consumer ranges and supported regulator selectors, accounting for shared consumers; do not reopen this as an identity/research blocker or blindly copy initial values. S12B common range must respect BT's 2.024V maximum as well as WLAN's range.
2. **SWCTRL GPIO82:** reserve its intended radio ownership, but do not claim the current upstream PMU actively requests/drives it. It does not. Binding describes clock-supply state and vendor behavior is input/state. No invented GPIO82 output operation.

Ten-input mapping and PMR735A parent topology remain source-supported proposals **[INFERRED]** for installed oneli. Disabled staging can record them without requiring new physical identity proof. L7E common lifetime and explicit voltage configuration precede enabled radio integration.

## Next selection

Wireless owns the sole generic driver implementation: optional property-present WCN6855 vddasd shared supply, existing common sequence, strict lookup/unwind and focused tests. Boot independently stages disabled board topology and deliberate regulator constraints using fixed Wireless/Power contracts. This bounded second implementation uses separate files and a fixed existing binding interface; enabled consumption waits for reviewed producer code.

Power pauses after accepted contract and answers only a concrete Boot/Wireless dependency. VPU RESUME remains queued behind this immediate radio integration prerequisite; its prior acceptance and user-accepted /3 assumption remain intact. DP performs only final evidence documentation. USB, GPU and Userspace pause. Full assignments: [NEXT_TASKS](NEXT_TASKS.md).
