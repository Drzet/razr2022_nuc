# Coordinator VPU review — 2026-10-18

## Decision

Accept kernel **daf47c502fe9c959d49fb37f10f79d5f7d037d8f**, direct child of c3188052, and project **c0a2ae91156f14d9000c9a159cd3178fd31fbb0b** for the assigned firmware-specific RESUME adaptation. No blocking finding in the reviewed delta. Acceptance covers source, host packet serialization and ARM64 compilation/link; it does not establish Motorola firmware interoperability.

## Independently reviewed evidence

Reviewed all five changed files: firmware descriptor declaration/selection, shared RESUME helper and wrappers, production-extraction host test and consolidated CI invocation. Inspected production packet builders. The oneli descriptor alone opts in; static zero defaults retain U32 reasons elsewhere. Both DRC/settings-change and drain forward their original reason to the helper. With the option enabled, the builder receives NONE/NULL/0 and emits 64 bytes; default remains 68 bytes. Flags, ports, session/packet IDs and queue errors retain their existing behavior. Stack-local reason is copied synchronously by the unchanged serializer. Attribution identifies the pinned Xiaomi adaptation.

The host test extracts actual production initializers/functions and compares serialized bytes against explicit expected fields. It covers seven Gen2 descriptors, option toggles, both reasons/port mappings, queue errors and header-ID wrap. Queue/OS storage are mocked: it does not validate caller scheduling or firmware responses.

Independently read [run 39074972666](https://github.com/Drzet/linux/actions/runs/39074972666) jobs and logs. Host **117520119072**, source selection **117520119269** and ARM64 **117520358477** all succeeded. Host log records **216 cases / 61034 assertions**. ARM64 log shows both changed production objects, normal MODPOST, Image creation and qcom-iris.ko link. No coordinator rebuild or redundant test campaign.

| Evidence | CI identity |
| --- | --- |
| Host artifact | 12115998426; ZIP SHA256 837606677f2b4152638a861f285c070a61cc4f60f3568d11dcb3329d058433c0 |
| Build evidence artifact | 12117494506; ZIP SHA256 0995b792952bc2a7c2c19116e010559a3681ab51fd3ee0b7ffabbdc02faf7f58 |

Archive digests were read from CI logs, not independently rehashed here. The owner's canonical handoff contains config/output hashes and distinguishes downloaded config verification from CI-produced binary records. Build evidence does not include the Image/module payloads. Existing source acceptance needs no repeated build to manufacture another archive.

## Boundaries and follow-up

SM8475 remains disabled and unintegrated. Motorola applicability is [INFERRED]; /3 remains [INFERRED, USER-ACCEPTED FOR DEVELOPMENT]. VPU2, conservative 480-fps startup, admission/resource policy and previously disclosed recovery limitations are unchanged. No physical chip-ID gate or new broad firmware investigation is imposed. On-device testing must eventually exercise PAS/init/version and successful DRC plus drain/restart with verified frames.

Also inspected Boot documentation at **53c1b7a58099c9ad0fb111edf9f62cad8cc9797a** and DP closure at **2f992d150b5c13b5f98c59e4b7fb9ee802ed918d**. Both prior documentation assignments are complete. Boot's historical owner-state prose is superseded by current NEXT_TASKS; no standalone documentation round is needed.

Select **Boot** as the sole active owner to prepare a reduced, reproducible configuration against accepted kernel **7f3865e**, retaining diagnostics, radio and QEMU/Userspace dependency contracts. Deliver resolved config and cheap checks before a later full build. This addresses the observed cost of broad defconfig builds without claiming unmeasured savings. Do not yet merge DP/VPU/earlycon or replace accepted release artifacts. VPU, Userspace, GPU, DP, Wireless, USB and Power pause. Exact assignment: [NEXT_TASKS](NEXT_TASKS.md).
