# Coordinator wireless feasibility review — 2026-10-17

## Decision

Accept [wireless handoff b0b6360e6c995671457e734a8e36b81d055b3036](https://github.com/Drzet/razr2022_nuc/blob/b0b6360e6c995671457e734a8e36b81d055b3036/docs/handoffs/2026-10-16-wireless-oneli.md) as source research with the qualification below. Integration using existing drivers is feasible **[INFERRED]**; installed oneli compatibility and operation are not yet demonstrated. No new radio driver is justified by the reviewed evidence.

Kernel razr/wireless remains exactly accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886**: no wireless kernel implementation has been delivered. Primary work is board power/transport configuration, firmware deployment and runtime validation.

## Independently checked evidence

At the accepted kernel, coordinator inspected:
- ath11k/pci.c: Qualcomm WCN6855 PCI device 0x1103 match and hardware-revision selection.
- hci_qca.c: qcom,wcn6855-bt support and power-sequencer consumer; lookup failure can fall back to legacy behavior, so successful probe alone does not establish correct shared power ownership.
- pci-pwrctrl-pwrseq.c: pci17cb,1103 pre-enumeration power support, vddaon supply lookup and wlan target.
- pwrseq-qcom-wcn.c: qcom,wcn6855-pmu, ten input supplies and shared WLAN/Bluetooth sequencing.
- sm8450-hdk.dts: matching PMU topology and GPIO80/81/82/204 reference configuration.
- Current oneli DTS lacks the corresponding wireless board nodes.
- Motorola kernel-devicetree@90fa7be1db5bd47202673d4431408659149a7359 qcom/cape.dtsi: QCA6490 WLAN/BT declarations, RC0 selection, supply references, shared control GPIOs and L7E antenna-switch/ASD supply.

Inherited Cape declarations support an oneli candidate; physical population, precise IDs and applicability remain **[INFERRED]**. Vendor WLAN S2E “AON” and BT S11B “AON” labels cannot be translated into upstream PMU inputs by name alone.

Read the metadata-only wireless manifest at b0b6360, including oneli-named board-data candidates and BT patch/NVM inventory. Extraction/hash verification and Xiaomi's zero generic-driver delta remain attributed Wireless/CI evidence; coordinator did not re-extract firmware, independently repeat that complete donor diff, compile wireless changes or execute hardware tests.

## Required qualification

Section 7 of the handoff makes staging conditional on physically verified PCI identity, while its conclusion permits runtime discovery. Physical IDs, HCI revision and firmware keys are **not prerequisites for preparing a source-supported development candidate**. Mark proposed hardware compatibility [INFERRED], validate power wiring first, and let normal PCI/HCI enumeration confirm identity during controlled testing. Do not fabricate IDs or force a driver to accept a mismatch.

Start with standard Linux firmware and normal automatic filename/revision selection. Motorola paths are provenance, not Linux deployment requirements. Use the already inventoried Motorola firmware/board data only for a demonstrated missing or incompatible entry; do not require manual revision selection, a custom board-2.bin or another extraction before an initial controlled attempt.

## Next steps and owners

1. **Wireless:** targeted transport, pin ownership, binding/config and firmware deployment contract from existing evidence; correct the physical-ID staging restriction in its canonical handoff. No generic driver edits.
2. **Power:** own the ten-input PMU supply map, actual provider/voltage constraints, shared sequencing and L7E antenna-switch ownership decision. Distinguish proven wiring from reference-design inference; report exact remaining evidence if unresolved.
3. **Boot, queued after coordinator acceptance of those contracts:** stage shared PMU, PCIe Wi-Fi and UART Bluetooth nodes/config with focused DT/schema and ARM64 module/dependency validation. Preserve diagnostic UART. No activation from this review alone.
4. **Userspace, queued after a selected kernel/config contract:** standard firmware/module packaging, NetworkManager/BlueZ and device-specific address handling. Do not copy Xiaomi calibration/MAC data or assume its persist layout.
5. **Later hardware validation:** enumeration, scan/association, pairing, simultaneous operation, rfkill and suspend/resume. No phone operation assigned now.

DP validation and Boot observability continue. Wireless and Power perform separate source-only contracts using fixed inputs; Power owns rail conclusions, Wireless references them rather than duplicating them. [NEXT_TASKS](NEXT_TASKS.md) is the assignment authority.
