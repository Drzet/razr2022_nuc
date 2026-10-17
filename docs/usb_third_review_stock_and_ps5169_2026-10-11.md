# USB third coordinator review: stock evidence and durable PS5169

2026-10-11. Owner USB. Checked coordinator main AGENTS, STATUS, WORKFLOW and NEXT_TASKS (third review blob fd33173324a2a97befcd87238271b36fa949ac74). Kernel baseline a5ebb76233b79db01e82e061173cb73c6d2b5c6b unchanged. No phone runtime validation.

## What changed from the third coordinator report

VPU has now **found** the previously missing signed firmware and GPU binaries, superseding the third review's earlier limited firmware-location status. Public Motorola Android 14 archive is 4,353,164,507 bytes, SHA256 620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c. [Shared VPU inventory and CI](https://github.com/Drzet/razr2022_nuc/issues/10#issuecomment-6114680664): radio.img → Motorola SINGLE_N_LONELY → NON-HLOS.bin → typed Android sparse → ext4 → firmware files. Found image/vpu20_4v.mbn + MDT/Bxx splits (version video-firmware.2.4), image/a730_sqe.fw, a730_zap.mdt/Bxx, with gmu_gen70000.bin from super:vendor_a. These are measured source file hashes, not firmware authentication or native video/rendering tests.

[Filesystem/DTBO manifest](https://github.com/Drzet/razr2022_nuc/blob/razr/vpu/docs/vpu/2026-10-11-stock-filesystem-firmware-manifest.json): vendor_boot v4 includes embedded DTB region of 958,962 bytes SHA256 88b605e746f829545f3a5ceabc8ac669eee803db1397d32cc7f49ec91fbba71e. All four DTBO roots identify oneli and contain BOTH compatible strings nxp,eusb2-repeater and diodes,eusb2-repeater. The table ID/revision is zero in each. This is string-presence evidence, NOT evidence of active repeater part or actual handset overlay selection.

Read-only stock ADB identified XT2251-1 PVT, hwrev 0xC000, SKU dn, Android 14 U2SLS34.1-42-14-11. Firmware build label matches the public archive but exact installed bytes remain unverified. Device USB HAL observed dual Type-C roles on Android, not working native USB or a dock.

## Explicit per-variant USB evidence matrix

| DTBO index | Extracted reference DTB SHA256 | NXP and Diodes string evidence | Actual enabled repeater | PS5169 per-variant status/EQ/reset | Live selection |
| --- | --- | --- | --- | --- | --- |
| 0 | 10c199f0176717d93eb2e99ae7a19e2fcaf3669d96655a0b31a8feff6e4a0f19 | both present | unknown | unknown | unknown |
| 1 | 1adcb600d11d3d2b1e25a75fc16e8b754439f279acea2dcecf97dec7d488752b | both present | unknown | unknown | unknown |
| 2 | bdfc575aa20f2ccb00e9a2414119b03ac6229af531c906ff3f3068fc995cdf28 | both present | unknown | unknown | unknown |
| 3 | 4fd14c771ecf9f6eadd8e9e56215bcb2858beda6808ce107ae45a9ce18173aad | both present | unknown | unknown | unknown |

The VPU source manifest does not yet include per-node property values, statuses or a resolved base + overlay composition. USB requested a tightly scoped per-variant JSON property export in [VPU shared issue #10](https://github.com/Drzet/razr2022_nuc/issues/10#issuecomment-6114753777): NXP/Diodes node statuses, reset GPIO and supply phandles, register tuning, PS5169 I2C 0x30, VCC/VIO, GPIO19/91, EQ/config-seq, connector/GLINK endpoints and numeric board IDs. No separate 4.35-GB ROM download was started. The matrix above is intentionally a **partial stock variant report**, not a fabricated comparison.

## Durable attributed PS5169 implementation

Kernel **razr/usb-ps5169**, forked from USB baseline branch commit **87d7277ced4c562e2379ee58aaed5c5fd7db4f32**. It contains permanently committed source:
- 068af1339724278235fa0880f565c47c344b3f7b: automated attributed import and complete ARM64 CI workflow.
- 3212e1d8a836f3dbbd0a258410b18683a38207ad: Esteban Urrutia original binding v3, preserving author/sign-off.
- 551c094e0ce5e7f492fe21d7e6ab2de815343b6a: Esteban Urrutia original driver v3, preserving author/sign-off.
- cbed833e9d5131fbed49774f385bba38bcd7944f: USB-owned direct Linux header inclusion repair.
- **4cbfc0145d9c837d2ba3fd9050f529a786135403**: USB-owned VCC/VIO bulk regulator support and required vio-supply binding.

Original applied source SHA256: PS5169 C b76465571bc5a7f80a177660e9290115fedcfbccda1fb43c801e25a6f3a521ed; binding 3c9f01f921398edf34e7d3b13439306bd26e8f48a75151294ec529c83b852cc3. The workflow validates both before local changes, then commits them separately. GitHub-hosted [Actions run 38181747728](https://github.com/Drzet/linux/actions/runs/38181747728) covers schema and complete ARM64 Image/modules normal modpost. At writing, its ARM64 job result still needs final conclusion verification; DO NOT claim it passed based only on intermediate stages.

### Source-code-specific review

- Both regulator supplies are requested and bulk-enabled VCC then VIO. Motorola vendor supplies are S10B 1.8V VCC and L8C 1.8–2.0V VIO; vendor L8C is marked boot-on. Correct physical enable sequencing and power-retention behavior remain [INFERRED]. Probe error and remove paths bulk-disable supplies; that is code review only, not testing regulator hardware.
- Original PS5169 code requests a required reset-gpios and pulses logical assert for 1–1.5ms then deasserts with 10–11ms delay. Motorola's **TLMM GPIO19 is source-backed as high-enable/low-disable**, but equivalence to a physical reset pin, reset polarity and pulse tolerance is **[INFERRED]** and NOT a valid oneli DT binding claim. No oneli node is enabled.
- Software-quality gap: ps5169_write() ignores regmap write/update return codes, as does ps5169_init() for EQ registers. Source-backed robustness improvement would propagate errors through probe and Type-C switch/retimer callbacks, with unwind after failed init. Do not confuse successful compilation with tested I2C behavior.
- Driver contains no explicit suspend/resume PM callbacks; supplies are left enabled until removal. Suspend retention requires deliberate design, not assumed from source build.
- Mainline Type-C contracts: GLINK should be **single input owner of GPIO91**, not PS5169; independent AUX SBU node uses GPIO2/71 and belongs to DisplayPort, not nonexistent PS5169 port@2. Existing [versioned graph contract](typec_graph_contract_v1_2026-10-11.md) and [Boot-only disabled USB2-first proposal](usb2_first_boot_contract_v1_2026-10-11.md) remain in effect. NXP repeater identity is still unproven; no guess that it must be PTN3222.

## Follow-ups and integration ownership

**Boot** owns all shared SM8475/oneli DTS changes; can stage disabled USB2-first eUSB PHY/controller/port@0 with Power's rail range contract without PS5169. **USB** now provides exact committed PS5169 driver/binding to be reviewed as an *experimental* candidate, pending ARM64 build outcome and reset contract. **VPU** owns shared stock metadata extraction; **DisplayPort** keeps AUX port@2 disabled until a genuine compatible/part identity is found. Hardware is disconnected; no native enumeration, DP, register reads or firmware secure load has been tested.
