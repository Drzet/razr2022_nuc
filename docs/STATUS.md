# Project status

Updated 2026-10-16 after [reviewing completed Boot/research and VPU assignments](COORDINATOR_REVIEW_2026-10-16.md).

**We have a built kernel, Debian/QEMU validation and host-checked diagnostic boot images. Native Linux has not booted on the phone. VPU policy is now accepted for implementation; the bootloader research correction is complete. External-display source work resumes using the identified AUX switch.**

[Assignments](NEXT_TASKS.md) · [Policy](WORKFLOW.md) · [Branch disposition](CLEANUP_2026-10-13.md)

| Owner | Accepted evidence / current state | Next action |
| --- | --- | --- |
| VPU | Policy project 29c59a2; calculator kernel 7ac8d3af. No consumer code delivered yet | Active bounded consumer implementation, candidate remains disabled |
| Boot / research | Boot b2f9aea and research 0acccb3 accepted; 12 synthetic tests independently pass | Paused after completion; handset observations remain |
| DisplayPort | Reference AUX identified as WAS7227Q-10/TR; existing stock GPIO/overlay evidence retained | Active exact-part reuse/binding and graph review |
| USB | PTN3222 kernel 1e526827 / project 481c399 accepted in isolated scope; 44 provider tests reproduced previously | Paused; board integration pending |
| Userspace | Debian/QEMU and diagnostic-v2 accepted | Paused until inputs change |
| GPU / Power | Existing accepted fixes/evidence retained | Paused; specific power-provider work queued |

Accepted integration **2b5acf108ae37040ac1e652e029bb37f5609e886**, [integration record](../configs/accepted-integration-2026-10-12.json) and [diagnostic-v2 record](../configs/accepted-native-console-v2-2026-10-13.json) are unchanged. No new combined kernel or phone-tested ROM. Experimental USB/VPU/DP are not integrated as working hardware.

## What the latest review changes

- **VPU:** explicit reservation, checked admission, independent bandwidth paths, strict clock selection and rollback policy accepted. /3 remains **[INFERRED, USER-ACCEPTED FOR DEVELOPMENT]**. Implement behind the existing disabled gate. Retained 480-fps startup plus the selected clock ceiling rejects even 1080p; this is a deliberate restricted development policy, not a hardware capability claim. A later startup-policy change is required before claiming broad video support.
- **Bootloader:** loading formula and fallback constants are known from reference-firmware analysis. UTF-16 truncation and RVA mapping are repaired and tested. Actual selected RAM/FDT/ramdisk, fallback alignment and accessible early logs remain unobserved. No further identical packaging or firmware extraction is needed.
- **USB:** unknown readable chip IDs no longer reject the oneli profile. Read errors remain fatal. Driver acceptance does not establish powered link/enumeration/wake behavior.
- **DisplayPort:** exact reference part removes the old unknown-AUX identity hold. Existing GPIO mux reuse and binding/graph decision is now assigned. USB-C video is not yet working.

## Remaining route to hardware

The next native milestone is an observable controlled boot on the handset with a supported image/DT/ramdisk composition and recovery arrangement. UART pads/voltage or another early-output route remain unidentified. We must check the bootloader's actual placement against full Image allocation/alignment and its populated memory tree when observable; no guessed addresses.

Separately, USB/DP need board supply/provider and graph integration. VPU needs the selected consumer implementation and an independent resolution of inherited IOVA reservation failures before active DMA. PAS/HFI/decode and physical cache/clock behavior remain hardware outcomes. These subsystem tasks do not block an otherwise ready minimal UART boot.

## Preserved schematic findings

[Canonical schematic record](oneli_schematic_evidence_2026-10-15.md) is auditor/user-transcribed reference-design evidence; installed-PVT correspondence remains [INFERRED].

- PTN3222BUK: I2C 0x4f; S10B/L2B; PM8350C GPIO7 active-low reset.
- WAS7227Q-10/TR AUX: TLMM2/71 software control; FSA4480 remains disabled.
- PM8350/PM8350C parent groups and variable B_PLUS/BOB topology recorded.
- CHG_EN → PM8350C GPIO2 pin134; balance → PM8350BH GPIO1 pin114; bridge → PM8350BH GPIO3 pin139; R909 470 kΩ.
- UART TX → SM8475 GPIO26/D24; RX → GPIO27/C24. Both pads use the accepted qup7 mux; source label names alone do not show a functional mismatch.
