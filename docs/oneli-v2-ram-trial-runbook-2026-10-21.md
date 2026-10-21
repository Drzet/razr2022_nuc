# Oneli self-contained Android v2 RAM-boot experiment: proposed one-shot runbook

Date: 2026-10-21. Owner: BOOT. **Status: OFFLINE-VALIDATED ONLY. FUTURE EXPERIMENT NEEDS SEPARATE COORDINATOR AND DEVICE-OWNER APPROVAL. NO PHONE COMMANDS WERE RUN.**

## Exact immutable candidate

- [Packaging run 39642219570, job 119368408037, PASS](https://github.com/Drzet/razr2022_nuc/actions/runs/39642219570); tested project commit `a9b5b0288341820e29772ae96f7f6805c4b2b9fe`.
- [Download artifact 12365726243](https://github.com/Drzet/razr2022_nuc/actions/runs/39642219570/artifacts/12365726243), `oneli-v2-self-contained-ram-trial-39642219570-1`, ZIP **13,752,547 bytes**, independently verified SHA256 **`bac6e9660592d24ed58969538612e7b029ff74f8e403c5bc53f710de40383990`**.
- Unzip one `oneli-reduced-radio-diag-boot-v2.RAM-TRIAL.UNSIGNED.img`, **37,572,608 bytes**, SHA256 **`5176f3d442fc7c307d80ac23c2e87659d6d5975a594a6ee8388331046f4a8e31`**.
- Embedded immutable inputs: raw reduced Image SHA256 `279431f997fc2334d92760d47c01aec2b8e12cf47e6d149d6a078f2347c330e8`; native gzip diskless `radio-early.cpio.gz` `875eb0a1b0f63dbecaefb5160775da01bd8a3bc445ca1eb016effe3717875b7c`; unmodified oneli DTB `70d5c7b08ddda1c0974ac85e95bb1328528bb533c344a0681b5e95b88cd17435`.
- This is **not** the v4 boot image and does **not** consume/replace stock `vendor_boot`. No separately supplied ramdisk or DTB should be added at the fastboot CLI. It is **unsigned**. Neither downloaded-buffer selection nor Motorola native boot success has been proved.

## Offline host acceptance (already COMPLETE)

Pinned AOSP `ntherning/mkbootimg@7209a7164f1772db43f92928012c86a00f6202ff` produced the image; a separate strict byte parser validated header v2, OS raw 0, board `oneli`, 4,096-byte pages, 1,660-byte header, command line and bounded sections. AOSP `unpack_bootimg.py` independently extracted and rehashed kernel, ramdisk and DTB. A second AOSP repack was **byte-for-byte identical**. Optional second-stage and recovery-DTBO sizes/offsets are zero; no stock overlays, proprietary vendor ramdisk or bootconfig. Every header pad and section pad was zero. The legacy image SHA-1 ID is verified. Image `image_size=37,158,912` and kernel start 2 MiB alignment are separate physical-runtime constraints; header address template values **0x8000/0x1000000/0x100/0x1f00000** are not observed runtime addresses. Early gzip contains executable resident `/init` and matching `pci-pwrctrl-pwrseq.ko`. Six output members rehashed from the downloaded ZIP manifest. **No hardware validation has occurred.**

## Prerequisites for any future authorized phone session

1. Positively identify the phone as `oneli`; connect the host using a stable USB port, with an independently verified way into and out of its bootloader. Confirm original stock Android still boots and that recovery is possible *without* the candidate kernel. Record current slot and bootloader fastboot's read-only state. This runbook does not authorize changes to slots, unlocking, AVB, userdata or any partition.
2. Prepare UART7 TX/ground probing with *measured* logic reference; ensure logs can be independently timestamped. UART7 is the primary output; an actual display console is not implemented. Capture known-good stock bootloader serial activity first where possible. Silence with no independently working UART reference is not interpretable.
3. Verify the downloaded image SHA256 exactly **`5176f3d442fc7c307d80ac23c2e87659d6d5975a594a6ee8388331046f4a8e31`** and the archive ZIP SHA256 above. Extract the exact image unmodified; do not regenerate it with a local fastboot `--header-version` or supply extra ramdisk/DTB arguments.
4. Verify the device bootloader's `max-download-size` is at least **37,572,608 bytes** (if reported) and `is-userspace=no` where supported. If identity, capacity, transport, recovery or verification fails, **stop without running `boot`**. An unreported/unknown value requires explicit reviewer decision rather than assuming support.
5. Obtain explicit approval for **one** temporary trial. AOSP's documented fastboot protocol `boot` command boots a previously downloaded `boot.img`; AOSP client supports a preassembled image passed to `fastboot boot FILE`. This is a *standard host-command syntax*, **not proof the Motorola AVB callback uses the downloaded bytes**. Sources: https://android.googlesource.com/platform/system/core/+/4997e024e/fastboot and https://chromium.googlesource.com/aosp/platform/system/core/+/master/fastboot/fastboot.cpp .

## Future read-only preflight and one RAM-only command (DO NOT EXECUTE UNTIL AUTHORIZED)

After recovering a verified `fastboot` binary and confirming that the handset is in **bootloader fastboot**, not `fastbootd`, an operator may use:

```sh
sha256sum ./oneli-reduced-radio-diag-boot-v2.RAM-TRIAL.UNSIGNED.img
fastboot devices
fastboot getvar product
fastboot getvar current-slot
fastboot getvar is-userspace
fastboot getvar max-download-size
```

Some OEM variables may reply FAIL or be unsupported; preserve their raw output and do not mistake that for boot acceptance. **Only after all preflight and stock-return prerequisites have been reviewed and authorized**, initiate **exactly one** bounded RAM request:

```sh
fastboot boot ./oneli-reduced-radio-diag-boot-v2.RAM-TRIAL.UNSIGNED.img
```

That exact syntax is supported by AOSP fastboot client/protocol, but Motorola's device-specific complete image-load path is still **[INFERRED]**. **Do not** run `fastboot flash`, `set_active`, `flashing unlock`, `oem`, `erase`, `-w` or vendor_boot/DTBO/vbmeta writes as part of this test.

## Observation and stock return

Capture exact host response and duration plus bootloader/UART7 logs. Distinguish stages:

- **Host download refused / FAIL**: transport, size, authorization or ABL rejection. Not evidence the Linux Image is defective.
- **Download accepted, ABL rejected v2/DTB/verification**: preserve literal error code, stage and source context; inspect whether `AvbOps` used downloaded `boot` rather than installed `boot`, and which DTB/DTBO path was selected.
- **Bootloader hands control to ARM64**: look for early kernel UART, effective bootargs, 2 MiB Image start alignment, FDT selected and corrected `/memory`; do not assume image header load addresses were followed.
- **Early init `RADIO_EARLY_INSMOD_OK` and `RADIO_EARLY_READY_V1` / `RADIO_EARLY_HOLD`**: indicates `/init` and matching module attempt occurred. It does **not** establish radio binding/association or complete Debian boot. This diskless payload intentionally holds resident.
- **No UART output / apparent hang**: **INCONCLUSIVE** without a validated serial reference. Could be OEM download selection, signature, wrong DTB, RAM overlap, early kernel, power state or disconnected UART; it is not proof of Linux failure or of a successful boot.

For a one-shot trial, use the **pre-verified independent bootloader/stock-reboot procedure appropriate to this exact handset** on any timeout/hang. If still in a working fastboot interface, standard `fastboot reboot` is the non-flashing command to resume stock. If fastboot is no longer responsive, use only a pre-demonstrated hardware entry/recovery sequence; do not improvise physical-key combinations or substitute a flash command. Verify the original installed Android boots and that original slot/partition/AVB state is intact; an attempted RAM boot is *intended* to avoid partition writes but does not guarantee every OEM boot-control side effect. If stock return cannot be established **before** the first test, do not launch.

## Scope and decisions left open

Unverified: `AvbOps` callback mapping of the downloaded v2 buffer vs installed storage, EFI mode value, Motorola DT board/PMIC compatibility without downstream `qcom,board-id`, DTBO selection, memory-map fixups, actual Image/DTB relocation and UART physical access. These are first-trial observations wherever not decidable offline. Existing [split-v4 offline artifact 12338654148](https://github.com/Drzet/razr2022_nuc/actions/runs/39585458990/artifacts/12338654148) remains unchanged and **is not chosen for installation**. An inactive-slot writing/restore plan is only **[INFERRED] fallback** and has no established independent recovery guarantee.
