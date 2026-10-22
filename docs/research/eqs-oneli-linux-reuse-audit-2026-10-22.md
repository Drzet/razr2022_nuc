# Motorola Edge 30 Ultra (eqs) → Razr 2022 (oneli): native-Linux reuse audit

**Date:** 2026-10-22  
**Scope:** Read-only research; no kernel, workflow, build, flash or on-device execution.  
**Coordinator base:** Drzet/razr2022_nuc main at 43a72d27af358243b23c7cb4c0fc93f5bd75dd3e.  
**Primary direct A/B reference:** LineageOS/android_kernel_motorola_sm8475-devicetrees at 4d2ea0ebf7a591e2c98d682a106afe4605616724.  
**Native development comparison:** Drzet/linux at radio build source 7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce; base a5ebb76233b79db01e82e061173cb73c6d2b5c6b.

## 1. Executive decision

**Yes, substantially reusable at the Motorola Cape/SM8475 platform, driver and hardware-description *reference* level; no, not interchangeable at the board-DT, boot-image, display-panel, charger or firmware level.** The most useful new finding is a **single LineageOS Motorola device-tree repository that contains both eqs and oneli descriptions under the same Cape inheritance hierarchy**. It is better than Xiaomi Pad 6 Pro for distinguishing Motorola-specific wiring, PMIC rail names, shared Qualcomm GLINK integration, PS5169 control and the inherited external-display implementation. It is *not* a ready-made upstream/mainline device tree or a proven working native-Linux image.

**DP:** Both eqs and oneli vendor display descriptions select the *same* AUX control TLMM **GPIO2 and GPIO71** and disable the inherited FSA4480 node. Both inherit the same Motorola Cape DP controller and PS5169 register-programming description. Critically, eqs instantiates that PS5169 on QUP I²C **SE5**, while oneli uses **SE18** and explicitly requests the L8C VIO rail. The oneli schematic already identifies its actual standalone SBU/AUX component as **WAS7227Q-10/TR**: no remaining need to guess an AUX chip based on eqs. Eqs also sets vendor-only **qcom,dp-downgrade**, absent from the oneli DP overlay. Its operational semantics and usefulness for upstream DRM are **unverified**. No new DP driver or blind DT copy is justified.

**Boot:** Eqs LineageOS specifies Android **header v4**, A/B boot/DTBO/vendor_boot and modular vendor ramdisk, but this is an **Android ROM packaging recipe**, not evidence that an eqs binary or recipe safely boots Linux on oneli. The oneli coordinator already accepted a standalone **header-v2 RAM-trial** image; the next milestone remains one observed, separately authorized phone trial. Eqs offers **no verified simpler bootloader or UART solution**.

**Power/wireless:** A common Cape hierarchy gives usable source evidence for QCA6490, PCIe0/UART20, GPIO80/81/82/204 and shared regulator families, corroborating rather than replacing native oneli's staged WCN6855/ath11k/hci_qca path. It cannot prove installed PCI/HCI identity, board data or actual RF functionality. Oneli's **dual battery and flip charging path** has no eqs equivalent: do not copy eqs charger policy.

**Native Linux:** The inspected eqs implementation and release procedure are LineageOS **Android**, using Android 5.10 vendor drivers, proprietary service modules and firmware. No independently verifiable eqs-specific mainline/postmarketOS/Ubuntu Touch/Mobian native implementation or successful device boot was identified in the targeted sources. This is a bounded negative search finding, **not proof that no private or unpublished port exists**.

## 2. Evidence and method

1. Read the coordinator's **AGENTS.md**, **docs/STATUS.md**, **docs/NEXT_TASKS.md**, **docs/WORKFLOW.md**, the 2026-10-21 packaging/display reviews, project DP/USB/power investigations and schematic record. The accepted oneli source/build scope is **not hardware acceptance**; its native Linux has **not booted on the handset**.
2. Compared eqs and oneli within the *same immutable snapshot* of LineageOS's split **android_kernel_motorola_sm8475-devicetrees** repository, rather than treating Android device-product makefiles as an SoC/PCB schematic.
3. Compared those definitions with existing **Drzet/linux** oneli DTS/SM8475 include and coordinator subsystem conclusions, without modifying them.
4. Cross-checked eqs LineageOS boot configuration, module load inventory, firmware manifest and installation instructions. Searched for genuine native ports. Source configuration, schematic-reference wiring, successful Android images and tested Linux hardware are distinct evidentiary levels.

**Evidence classification:** **S** = explicit source/DT text; **H** = oneli schematic-derived, physical population of retail PVT still unverified; **P** = upstream/native project source/build status, not observed hardware; **U** = unresolved or [INFERRED]. **Identical** denotes matching inspected source/SoC function, *not* proven bit-identical populated PCB.

Pinned source groups:

- **DTS repository [D]**: https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/tree/4d2ea0ebf7a591e2c98d682a106afe4605616724
- **Android kernel [K]**: https://github.com/LineageOS/android_kernel_motorola_sm8475/tree/0e4b4e9fccd77aa387944368da3949e01e580111
- **Eqs product [E]**: https://github.com/LineageOS/android_device_motorola_eqs
- **Motorola SM8475 product common [C]**: https://github.com/LineageOS/android_device_motorola_sm8475-common
- **Oneli Linux [L]**: https://github.com/Drzet/linux/tree/7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce
- **Oneli coordinator [P]**: https://github.com/Drzet/razr2022_nuc/tree/43a72d27af358243b23c7cb4c0fc93f5bd75dd3e
- **Oneli schematic [H]**: https://github.com/Drzet/razr2022_nuc/blob/43a72d27af358243b23c7cb4c0fc93f5bd75dd3e/docs/oneli_schematic_evidence_2026-10-15.md

## 3. Hardware compatibility matrix

| Area | Eqs vs oneli | Classification | Evidence and adaptation |
| --- | --- | --- | --- |
| SoC and CPU | Both Cape/SM8475, Adreno 730 | **Identical SoC family** (S) | D:qcom/cape.dtsi, eqs/oneli PVT overlay; LineageOS eqs device data. Does **not** establish matching routing |
| Qualcomm peripheral clocks, MDSS DP block | Shared Cape SoC register maps, inherited DP/USB3-QMP/clock descriptions | **Identical source base**, adaptation to upstream (S) | D:qcom/cape.dtsi; D:qcom/display/display/cape-sde.dtsi; L:sm8475.dtsi |
| PMIC core and RPMh | Cape common PM8350/B/C, PM8450, PMR735-family references; variant overlay and PM8010 applicability differ | **Compatible with modification** (S/U) | D:qcom/cape-regulators.dtsi; eqs includes waipio-pm8010-spmi.dtsi in its common overlay, oneli EVT overlay also can include it. Installed variant/rail topology must not be inferred |
| Regulator parents | Shared vendor rail names S10B, L2B, L5B, L8C etc; detailed oneli parent wiring schematic-derived | **Compatible with modification** (H) | H: PM8350 L1/L4 and L3/L5 from S11B, L2/L7 from BOB, L6/L9/L10 from S12B; PM8350C L2/L8 from S1C, L10 from S12B. Do not substitute eqs regulator-tree initialization |
| DWC3, USB3/DP PHY | Shared Cape DWC3/eUSB2/QMP family | **Identical SoC**, board-dependent power (S/P) | D:qcom/cape-moto-common-overlay-base.dtsi and qcom/cape.dtsi; L:sm8475.dtsi |
| NXP eUSB2 repeater | Common @ I²C SE5 / 0x4f, S10B + L2B, PM8350C GPIO7 | **Compatible with modifications** (S/H) | D:qcom/cape-moto-common-overlay-base.dtsi; H identifies oneli **PTN3222BUK**. Exact eqs population not independently measured. Oneli upstream driver BUK ID matching remains a known caveat |
| PS5169 redriver | Shared Parade PS5169, I²C 0x30, TLMM19 enable, TLMM91 orientation; **eqs SE5; oneli SE18** | **Different board I²C path; shared IC driver** (S) | D:qcom/cape-moto-common-redriver.dtsi, cape-eqs-common-overlay.dtsi and cape-oneli-common-overlay.dtsi. Only oneli explicitly supplies VIO from L8C |
| AUX/SBU switch | Both DTs disable FSA4480 and assign TLMM2 enable/TLMM71 select; oneli schematic **WAS7227Q-10/TR** | **Shared control policy; eqs switch silicon unverified** (S/H/U) | D:qcom/display/display/cape-sde-display-{eqs,oneli}-common-base.dtsi; H sheet 8. Vendor qcom,dp-aux-switch FSA4480 phandle is not evidence of hardware |
| Type-C control and DP Alt Mode | Both inherit Qualcomm UCSI/PMIC-GLINK/altmode, same DWC3 controller | **Compatible with modification**, firmware handshake unverified (S/U) | D:qcom/cape.dtsi (qcom,ucsi-glink and qcom,altmode-glink), qcom/cape-moto-common-overlay-base.dtsi; native GLINK+USB-C graph separate |
| DP vendor tuning | eqs has qcom,dp-downgrade; oneli not; both remove qcom,mst-enable | **Different** (S/U) | D:qcom/display/display/cape-sde-eqs.dts vs cape-sde-oneli.dts. Meaning/necessity of eqs flag not established |
| Internal displays | eqs one 1080×2400 display with CSOT/Tianma candidates; oneli main 1080×2400 plus **BOE 800×600 cover DSI** | **Different panel topology** (S) | D:qcom/display/display/cape-sde-display-{eqs,oneli}-common-base.dtsi. Oneli second DSI connector, cover supply, GPIO123/127/128 unique |
| Backlight and reset | Both use MIPI DCS families; oneli cover has independent enable and reset, oneli main GPIO106/107 | **Compatible framework; different sequences** (S) | Same D:display files. **Do not reuse eqs panel init/refresh/power sequences** |
| WLAN/BT | Cape common QCA6490 platform, shared 80/81/82/204 controls and rail families; oneli staged upstream WCN6855 transport | **Compatible with modification** (S/P/U) | D:qcom/cape.dtsi; L:sm8475-motorola-oneli.dts. Firmware board-ID/calibration and runtime identity **unverified** |
| GPU Adreno 730 / GMU | SM8475 family, shared vendor GPU clock/voltage metadata | **Compatible source only** (S/P/U) | D:qcom/cape.dtsi, D:qcom/cape-regulators.dtsi; L:sm8475.dtsi GPU OPP replacement, GPU disabled; secure GMU firmware applicability unverified |
| VPU / SMMU | Qualcomm video/MDSS/SMMU base, downstream Android videocc and video driver stack | **Compatible concepts; native adaptation required** (S/P) | D:qcom/cape.dtsi, qcom/display/display/cape-sde.dtsi; C:modules.load uses msm_video.ko; native Iris experimental RESUME remains disabled |
| ADSP/audio | Both use Qualcomm ADSP and similar WSA883x/LPASS audio routing, common vendor services | **Compatible with modifications** (S/U) | D:qcom/audio/cape-{eqs,oneli}-audio-overlay.dtsi; native oneli audio disabled. Codec population and calibrated topology not proven identical |
| UFS storage | Common Cape UFS host/PHY addresses and regulator references | **Compatible with modifications** (S/P) | D:qcom/cape-moto-common-overlay-base.dtsi; L:sm8475.dtsi PHY moved to 0x01d80000; oneli UFS remains disabled. Eqs UFS size/capacity not a DT compatibility basis |
| Charging and battery | eqs main battery/charger and 125-W vendor limit; oneli **paired main + flip battery**, dedicated flip SGM41516D and load switch | **Different** (S/H) | D:qcom/cape-eqs-charger-overlay.dtsi vs cape-oneli-common-overlay.dtsi/waipio-li-charger-overlay.dtsi; H: SGM41516D, WS4695C-12 and balancing MOSFETs |
| NFC/touch/camera | eqs ST21NFC @0x08; oneli Qualcomm SN-NCI @0x28; touchscreen and camera regulator differences | **Different** (S) | D:qcom/cape-{eqs,oneli}-common-overlay.dtsi; eqs moto-eqs-wl2868c.dtsi; variant display/touch records |
| Console | Cape stdout selects QUP UART7 at 0x99c000, serial0; oneli GPIO26/27 schematic corresponds to debug nets | **Shared software, physical access unverified** (S/H/U) | D:qcom/cape.dtsi; L:sm8475-motorola-oneli.dts; H GPIO26 D24/TX, GPIO27 C24/RX |
| DTBO board identity | eqs PVT board-id 0x41 / 0xC1A0; oneli PVT 0x45 / 0xC000 | **Different** (S) | D:qcom/cape-eqs-pvt1a-overlay.dts vs cape-oneli-pvt-overlay.dts. Never repurpose the eqs DTBO |

**Revision caveat:** Overlay composition varies with EVT/DVT/PVT: table compares the named common and PVT reference files, not a verified complete flattened FDT loaded into either handset. **[INFERRED]** Exact PVT component population needs retail-device confirmation.

## 4. Exact implementation inventory: reuse decisions

| Source / symbol | How to use it | Do not do |
| --- | --- | --- |
| D:qcom/cape.dtsi — reserved memory, PMIC GLINK, QCA6490, shared clocks | Cross-check oneli evidence, reuse common high-level topology and regulator names | Paste downstream DRM/CNSS/GLINK properties into mainline DT |
| D:qcom/cape-moto-common-overlay-base.dtsi — UFS, NXP repeater, ucsi/USB role graph | Validate common host supplies and repeater lines against H and current oneli work | Pretend a legacy nested dwc3 or vendor repeater compatible works upstream |
| D:qcom/cape-moto-common-redriver.dtsi — **parade,ps5169-redriver**, 0x30, GPIO19/91, config-seq | Compare vendor profile/register sequence with existing PS5169 candidate, **target SE18 and L8C** for oneli | Instantiate eqs's SE5 PS5169 on oneli or copy vendor binding |
| K:drivers/usb/misc/ssusb-redriver-ps5169.c — **CONFIG_USB_REDRIVER_PS5169** | Downstream behavior reference only. Native USB owner has existing tested implementation using Linux Type-C mux/retimer APIs | Introduce second competing PS5169 driver |
| D:qcom/display/display/cape-sde.dtsi — **sde_dp**, PHY, altmode, DP clocks/supplies | Audit requirements for upstream **mdss_dp0**, **usb_1_qmpphy**, **pmic_glink_altmode** | Copy old qcom,dp-display DT node, FSA phandle or vendor clock indexing |
| D:qcom/display/display/cape-sde-display-eqs-common-base.dtsi **lines 972–998**, corresponding oneli file **778–804** | Concrete **identical software GPIO2/GPIO71 AUX control**; validate against oneli's WAS7227Q and the current GPIO-SBU binding | Claim the same physical AUX IC on eqs, or that FSA4480 is enabled |
| D:qcom/display/display/cape-sde-eqs.dts — **qcom,dp-downgrade** | Only a lead for targeted driver-symbol review if on-device DP link training identifies a relevant failure | Apply the vendor flag to native MSM DRM without verified matching semantics |
| D:qcom/display/display/cape-sde-display-oneli-common-base.dtsi | Source for *oneli* two DSI connections, cover GPIO123/127/128 and panel candidates | Port eqs panel firmware/init commands |
| D:qcom/cape-regulators.dtsi and H oneli schematic | Reconcile source rails and input-parent groups with upstream **qcom-rpmh-regulator** and native staged parents | Overwrite oneli schematic rails with eqs defaults or fabricate fixed B_PLUS |
| D:qcom/cape.dtsi — QCA6490 transport/rails | Existing kernel WCN6855 PMU, PCIe0, UART20, ath11k and hci_qca candidate already staged; use eqs only to resolve **new discrepancies** | Add unproven PCI ID, hardcode MAC/board data, replace native driver with qcacld |
| D:qcom/audio/cape-{eqs,oneli}-audio-overlay.dtsi | Audit common WSA883x LPASS/ADSP concepts later when audio assigned | Import Android sound machine configuration as working mainline audio |
| C:BoardConfigCommon.mk, modules.load, modules.load.vendor_boot | Understand split-v4/DTB+DTBO and where vendor Android modules reside | Treat this as proof eqs fastboot boot works on oneli |
| E:BoardConfig.mk, proprietary-firmware.txt | Document eqs board selection, eqs-specific vendor modules and firmware provenance | Flash eqs boot, DTBO, modem, Bluetooth or vendor_boot on oneli |

### Linkable source inventory (immutable where available)

- https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/blob/4d2ea0ebf7a591e2c98d682a106afe4605616724/qcom/cape-eqs-common-overlay.dtsi
- https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/blob/4d2ea0ebf7a591e2c98d682a106afe4605616724/qcom/cape-oneli-common-overlay.dtsi
- https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/blob/4d2ea0ebf7a591e2c98d682a106afe4605616724/qcom/cape-moto-common-redriver.dtsi
- https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/blob/4d2ea0ebf7a591e2c98d682a106afe4605616724/qcom/cape-moto-common-overlay-base.dtsi
- https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/blob/4d2ea0ebf7a591e2c98d682a106afe4605616724/qcom/cape-regulators.dtsi
- https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/blob/4d2ea0ebf7a591e2c98d682a106afe4605616724/qcom/display/display/cape-sde.dtsi
- https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/blob/4d2ea0ebf7a591e2c98d682a106afe4605616724/qcom/display/display/cape-sde-eqs.dts
- https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/blob/4d2ea0ebf7a591e2c98d682a106afe4605616724/qcom/display/display/cape-sde-oneli.dts
- https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/blob/4d2ea0ebf7a591e2c98d682a106afe4605616724/qcom/display/display/cape-sde-display-eqs-common-base.dtsi#L972-L998
- https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/blob/4d2ea0ebf7a591e2c98d682a106afe4605616724/qcom/display/display/cape-sde-display-oneli-common-base.dtsi#L778-L804
- https://github.com/LineageOS/android_kernel_motorola_sm8475/blob/0e4b4e9fccd77aa387944368da3949e01e580111/drivers/usb/misc/ssusb-redriver-ps5169.c
- https://github.com/LineageOS/android_device_motorola_sm8475-common/blob/lineage-24.0/BoardConfigCommon.mk
- https://github.com/LineageOS/android_device_motorola_sm8475-common/blob/lineage-24.0/modules.load.vendor_boot
- https://github.com/LineageOS/android_device_motorola_sm8475-common/blob/lineage-24.0/modules.load
- https://github.com/LineageOS/android_device_motorola_eqs/blob/lineage-24.0/BoardConfig.mk
- https://github.com/LineageOS/android_device_motorola_eqs/blob/lineage-24.0/proprietary-firmware.txt
- https://github.com/Drzet/linux/blob/7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce/arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dts
- https://github.com/Drzet/linux/blob/7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce/arch/arm64/boot/dts/qcom/sm8475.dtsi

**Revision qualification:** LineageOS Android *device product* files above are linked at the inspected branch **lineage-24.0**, not an independently recorded full commit SHA; pin their SHA before any future patch integration. This report's direct eqs/oneli DT comparison *is* pinned at **4d2ea0e...**. Existing Motorola stock devicetree provenance: https://github.com/MotorolaMobilityLLC/kernel-devicetree/tree/90fa7be1db5bd47202673d4431408659149a7359/qcom and Motorola display DT: https://github.com/MotorolaMobilityLLC/kernel-display-devicetree/tree/80b207bf35be5da38375e755506f136558ad24b5/display.

## 5. USB-C/DP: concrete oneli gap analysis

**Reference signal chain:** Qualcomm DPU DP0 → QMP USB3/DP PHY → PS5169 (SS/DP high-speed lanes) → USB-C connector; a **separate SBU/AUX switch** routes AUX P/M according to CC orientation. PMIC-GLINK UCSI/altmode provides logical Type-C state and hotplug; this is not an oneli-verified live connection.

1. **Source equivalence established:** Both vendor panel-display trees disable the FSA4480 I²C node and supply **mmi,aux-switch-enable-gpio = TLMM2**, **mmi,aux-switch-flip-gpio = TLMM71** on DP. The existing Motorola DP implementation, https://github.com/MotorolaMobilityLLC/kernel-msm-5.4-techpack-display/blob/701a48c1db80eda2ff17154a9017783230cc22aa/msm/dp/dp_aux.c#L714-L778, gives the functional output states: disabled GPIO2/GPIO71=(1,0), CC1=(0,0), CC2=(0,1). This had already been derived for oneli; eqs **independently corroborates inheritance**, not a new switch-driver solution.
2. **Oneli physical SBU switch already known:** schematic sheet 8 says **WAS7227Q-10/TR**, **OE_N** enabled low, **SEL** sets orientation, powered from **L2B about 3.07 V**. Current oneli research asks for an exact part-compatible Linux gpio-sbu-mux binding and connector port@2 endpoint. Do **not** call this switch AW35615 or FSA4480, and do not infer eqs uses WAS7227Q.
3. **Redriver mapping must be oneli-specific:** vendor common node at **0x30** and **TLMM19/91** can inform the PS5169 mode/EQ profile. The eqs **SE5** declaration is *incorrect on oneli*: oneli is **QUP SE18** and adds **L8C VIO**. A rushed eqs transplant could collide with the shared SE5 eUSB2 repeater and fail I²C probing. Oneli schematic + project USB report own regulator and BUK repeater compatibility decisions.
4. **Type-C contract:** Existing native oneli DTS has a **disabled pmic-glink provider**, **HS-only port@0** and disabled USB/dispcc; no live SS/DP graph or AUX/SBU graph. Existing **Drzet/linux** upstream drivers already implement DWC3, QMP combo PHY, PMIC-GLINK Altmode, MSM DP and a tested candidate PS5169 driver. Boot/USB/DP owners would need to compose correct connector ports, supplies, retimer chain and switch-mode consumer, not introduce another DRM stack.
5. **HPD versus AUX:** downstream cape-sde.dtsi names an **altmode-dev=<&altmode 0>** and legacy **qcom,dp-aux-switch=<&fsa4480>**, even while fsa4480 is disabled. Do not confuse this historical phandle with an active physical switch. Test HPD events and successful AUX/EDID separately once Linux boots; no separate oneli HPD GPIO is established by the inspected eqs files.
6. **qcom,dp-downgrade:** eqs sets it, oneli does not; both delete MST enable. **[UNVERIFIED]** Its precise vendor-driver effect, effective build support and relevance to oneli are not established by these board overlays. It is *not* an immediately actionable mainline setting. Only revisit if the DP owner identifies a matching vendor symbol and observed link-training symptoms.

**DP impact:** Eqs is the strongest *Motorola platform* comparator for **common** AUX GPIO software, controller settings and PS5169 source semantics. Oneli schematic/source remain superior for the **actual oneli IC, bus, power, reset and pin assignments**. Thus this audit supplies a cross-check, not a newly proved fix or reason to restart an accepted/paused DP implementation task.

## 6. Boot infrastructure

| Evidence | Eqs Android implementation | Oneli native state / implication |
| --- | --- | --- |
| Header | C:BOARD_BOOT_HEADER_VERSION **4**, BOARD_MKBOOTIMG_ARGS header_version, GKI Image | Oneli prepared split-v4 only as an offline package; **accepted trial candidate is header-v2**, structure checked, runtime untested |
| DTB | C:BOARD_INCLUDE_DTB_IN_BOOTIMG true, BOARD_USES_QCOM_MERGE_DTBS_SCRIPT true | Native v2 candidate already embeds its own DTB; no proof eqs selection applies to Motorola oneli loader |
| DTBO | C:TARGET_NEEDS_DTBOIMAGE true; A/B dtbo partition | Eqs and oneli board IDs differ. No eqs overlay or merged DTBO should be flashed oneli |
| Vendor ramdisk | C:BOARD_BUILD_VENDOR_RAMDISK_IMAGE true; modules.load.vendor_boot specifies early Android/vendor dependencies | Stock oneli vendor_boot contents and firmware callbacks remain separate; oneli v2 trial does **not replace** stock vendor_boot |
| Partition scheme | C:A/B boot/dtbo/vbmeta/vendor_boot; E super partition and rollback index specific to eqs | Eqs LineageOS install **flashes** boot, dtbo, vbmeta and vendor_boot; not a demonstrated non-destructive oneli RAM boot |
| Command line/bootconfig | C:Android firmware path, logging and androidboot.usbcontroller=a600000.dwc3 | Eqs Android-specific bootconfig and OEM vendor services are not Debian boot prerequisites |
| Console | D:cape.dtsi **serial0=&qupv3_se7_2uart** and stdout **0x99c000/115200** | Existing native oneli **uart7**, GPIO26/27 selected; physical test points and voltage unresolved |
| Firmware | E:proprietary-firmware.txt lists ABL/AOP/QUPFW/DSP/BT/modem etc for eqs | Reuse *roles and filenames*, **not eqs blobs**; use oneli firmware provenance and signed versions |
| Verified boot | E:AVB rollback index 40; eqs installs signed Android images | Do not transplant or touch oneli slot/vbmeta/AVB policy |

Oneli coordinator's **2026-10-21** package review accepts **cc8caae0dd7c7f2bb030cd167e69f366aec876d4** / successful run **39642219570**, artifact **12365726243**, 37,572,608-byte **oneli-reduced-radio-diag-boot-v2.RAM-TRIAL.UNSIGNED.img**, SHA256 **5176f3d442fc7c307d80ac23c2e87659d6d5975a594a6ee8388331046f4a8e31**, for offline structure. Its next milestone is *separately authorized* **fastboot boot** with meaningful UART7/equivalent observation and stock return. It has not been executed on the phone.

**Verdict:** The eqs Android boot-v4 path is a **secondary documentation comparator only**. It is *not* more experimentally verified as a native oneli boot path than the existing selected oneli v2 package. No change to boot strategy, no vendor_boot overwrite and no additional build recommended on this evidence. Source references: https://github.com/Drzet/razr2022_nuc/blob/43a72d27af358243b23c7cb4c0fc93f5bd75dd3e/docs/COORDINATOR_V2_PACKAGE_REVIEW_2026-10-21.md ; https://lineageos.github.io/lineage_wiki/devices/eqs/install/ (Android install, flashing 4 images).

## 7. Wireless, GPU/VPU, reserved memory and audio

**Wireless — qualified high platform reuse, limited new implementation.** Motorola common Cape declares QCA6490 with shared GPIO80 WLAN_EN, GPIO81 BT_EN, GPIO82 switch status, GPIO204 XO and PMIC S10B/S11B/S12B/S1C/L7E rails. Native oneli candidate uses upstream **qcom,wcn6855-pmu**, **ath11k PCI** (source-expected pci17cb,1103), and **hci_qca** on **UART20**, with regulators and source/build-stage support in the existing radio kernel. Thus eqs corroborates Motorola's shared *logical* topology; it does **not** supersede oneli's rail-parent schematic, calibration data or prove installed IDs. Keep the WCN6855 driver and Linux firmware selection. Eqs LineageOS instead loads vendor **qca_cld3_qca6490.ko** and Android Bluetooth services; that is not a native Linux code-port shortcut. Eqs BTFM.bin/BT firmware manifest is **not** permission to deploy eqs-specific firmware to oneli.

**GPU — same SoC, no new native bring-up proof.** Oneli native **sm8475.dtsi** already replaces inherited SM8450 GPU OPPs using Motorola SM8475 frequencies, with GPU/GMU disabled pending CX floor/bandwidth, signed firmware and actual bring-up. Shared eqs Adreno 730 and source clocks corroborate class of hardware but not board OPP power or signed GMU image compatibility; do not revert oneli's corrected table to eqs/SM8450 inheritance. Standard MSM DRM/Adreno/GMU is the relevant Linux stack, whereas eqs Android uses **msm_kgsl.ko**.

**VPU and IOMMU — reference, not a solved gap.** Both derive video/MDSS reserved memory and SMMU from Cape, but vendor downstream Android **msm_video.ko** and Qualcomm IOVA/pool descriptions cannot simply substitute for Linux Iris V4L2, upstream IOMMU domain setup, firmware/HFI version and bounded IOVA reservations. Oneli's separately reviewed **daf47c502fe9c959d49fb37f10f79d5f7d037d8f** remains disabled/unintegrated. Exact usable carveouts differ by composed board firmware: native oneli deletes inherited memory nodes, sets ADSP **0x85700000 + 0x02800000**, VIDEO **0x9fd00000 + 0x00700000**, and drops incompatible inherited RMTFS reservation pending installed mapping. Eqs files do not authorize overriding these known oneli reservations.

**Audio — a later, qualified reuse lead.** Both Motorola audio overlays disable an inherited WCD938x codec and share LPASS/WSA883x configurations, but native audio still requires oneli's actual routing, SoundWire clocks and ADSP firmware. Eqs Android ASoC/Qualcomm PAL configurations are not a drop-in ALSA implementation. No changes assigned.

## 8. Native-port search and reference ranking

- **Motorola eqs:** Official LineageOS wiki and eqs-development repositories contain **Android** kernel 5.10/device blobs/recovery, not an inspected standalone mainline device implementation. Public postmarketOS release list and targeted eqs/postmarketOS/Ubuntu Touch/Mobian searches found **no verifiable eqs-native boot report or working patch series** by the report date. **[UNVERIFIED]** No exhaustive index of all personal Git repos, chat patches or private device trees was possible.
- **Xiaomi Pad 6 Pro / liuqin:** For Linux-native SM8475 SoC adaptation, modern mainline-style DT, Qualcomm DRM/USB/DP and non-Android drivers, the preexisting project Xiaomi/sm8450-mainline audit remains the better *Linux implementation* comparator. Source: https://github.com/sm8450-mainline/linux/blob/bf1d29fced6e156dd6090a9b6600a8c44259c114/arch/arm64/boot/dts/qcom/sm8475.dtsi ; https://github.com/Drzet/razr2022_nuc/blob/43a72d27af358243b23c7cb4c0fc93f5bd75dd3e/docs/postmarketos_review_2026-10-11.md . Xiaomi's DSI panel, connector and rail wiring cannot be used for oneli.
- **ThinkPhone / bronco:** Another Motorola Cape-era comparator: D:qcom/display/display/cape-sde-bronco.dts shares the same display parent and adds qcom,dp-downgrade plus qcom,dsc-continuous-pps. Its board-specific functionality and real native-Linux success are **not verified here**. For Motorola generalities, eqs direct A/B with oneli is more convenient, but no evidence ranks ThinkPhone runtime outcomes below eqs.
- **Motorola stock sources:** https://github.com/MotorolaMobilityLLC/kernel-devicetree/tree/90fa7be1db5bd47202673d4431408659149a7359 and https://github.com/MotorolaMobilityLLC/kernel-msm/tree/9511d6b2dc469e5bd836992e3bdd6d19ace112e0, plus Motorola techpack-display. **Oneli stock source and oneli schematic outrank foreign-board defaults** whenever they conflict.
- **LineageOS live wiki**: https://github.com/LineageOS/lineage_wiki/blob/main/_data/devices/eqs.yml and https://lineageos.github.io/lineage_wiki/devices/eqs/install/ confirm a maintained Android-based eqs release, A/B and its explicit flash procedure; no native-Linux success asserted.

| Problem / decision | Best reference | Why |
| --- | --- | --- |
| Common Motorola Cape PMIC/radio/PS5169 vendor control | **eqs↔oneli LineageOS source comparison** plus oneli stock | Identical source hierarchy, explicit differing buses/variant overlays |
| Actual oneli DP AUX switch and GPIO polarity | **oneli schematic and DP handoff**, eqs cross-check | WAS7227Q identity, active-low OE_N and specific GPIOs are oneli evidence |
| Mainline DRM/USB/GLINK/Type-C DT interfaces | **Xiaomi/mainline + existing Drzet/linux** | Eqs Android vendor APIs are incompatible with mainline bindings |
| Boot loader / image composition | **oneli accepted v2 trial and oneli MBM analysis** | Eqs LineageOS v4 split install not demonstrated as oneli RAM boot |
| Wireless mainline power sequencing | **existing oneli radio branch + schematic**, eqs Cape comparator | Linux WCN6855 APIs already implemented; runtime still unknown |
| GPU/VPU native control | **existing Drzet/linux and sm8450-mainline** | EqS lacks verified native driver/hardware result |
| Two internal displays and dual charging | **oneli stock DTS and schematic only** | Eqs lacks oneli cover panel and flip power path |

## 9. Ranked actionable recommendations and stop conditions

| Rank | Action | Expected benefit | Effort | Confidence | Owner / precondition |
| --- | --- | --- | --- | --- | --- |
| **1** | Preserve accepted **oneli header-v2 temporary RAM trial** as the next project milestone; do **not** switch to eqs v4/install | Highest direct resolution of boot uncertainty | **Device session**, not further offline build | **High** policy/source, **unknown** actual boot | Coordinator/Boot when user authorizes handset experiment |
| **2** | When DP activation is assigned, verify connector SBU **WAS7227Q** exact compatible and bind Type-C **port@2** to GPIO2 active-low enable/GPIO71 select with documented GPIO-SBU mux behavior | Could resolve remaining AUX/EDID path | **Medium** for binding + graph, device test necessary | **High** net/source logic; **medium** driver binding choice | DP+Boot; compare existing disabled PS5169/PMIC-GLINK graph first |
| **3** | In that same scoped USB/DP integration, use **SE18** for PS5169, **L8C VIO**, S10B VCC, TLMM19/91; keep SE5 for eUSB2 repeater; reuse accepted PS5169 implementation | Avoid wrong-bus probe/supply fault in any eqs-derived DTS | **Low** review, **medium** integrated board work | **High** for source assignments | USB+Boot only after explicit new queue assignment |
| **4** | If on-device DP negotiation/link training fails, source-check **qcom,dp-downgrade** semantics before considering a *native equivalent* | Conditional diagnostic clue; no guaranteed improvement | **Low** source review, uncertain code delta | **Low** absent observed failure | DP after hardware evidence; not a speculative preemptive patch |
| **5** | Keep current WCN6855/ath11k/hci_qca staging; use eqs Cape as a diff to reconcile source rail names and check firmware *families* at runtime | Prevents duplicate driver work; may clarify board discrepancies | **Low** now, **medium** runtime | **High** source, **unknown** hardware | Wireless/Power currently paused |
| **6** | Keep oneli's PVT panel/flip-power and corrected SM8475 OPP/IOVA definitions; do not import eqs panel, charger, DTBO or signed blobs | Prevents unsafe cross-board regressions | **No code action** | **High** | All owners |
| **7** | Use the direct A/B DTS pair as an evidence baseline for future targeted oneli regressions; pin Android product-file commit before applying any future patch | More precise reviews; fewer speculative board assumptions | **Low** | **High** | Coordinator research reference only |

**No new immediate subsystem implementation is authorized by this audit.** The coordinator's 2026-10-21 NEXT_TASKS says all existing agents are paused pending a controlled device trial. The recommendation table describes **future conditional work**, not reopened tasks. Evidence required to upgrade findings from source to functioning native device: observed UART/boot handoff; PMIC/USB provider probe; USB orientation and retimer registration; Alt Mode events; actual DP HPD/AUX EDID/video; WLAN PCI/HCI enumeration and association; GPU/GMU init; VPU actual frames. No such on-phone test is claimed.

## 10. Source and commit provenance summary

- Coordinator **main 43a72d27af358243b23c7cb4c0fc93f5bd75dd3e**: https://github.com/Drzet/razr2022_nuc/commit/43a72d27af358243b23c7cb4c0fc93f5bd75dd3e
- Native oneli radio source **7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce**: https://github.com/Drzet/linux/commit/7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce
- LineageOS vendor device trees **4d2ea0ebf7a591e2c98d682a106afe4605616724**: https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/commit/4d2ea0ebf7a591e2c98d682a106afe4605616724
- LineageOS vendor kernel **0e4b4e9fccd77aa387944368da3949e01e580111**: https://github.com/LineageOS/android_kernel_motorola_sm8475/commit/0e4b4e9fccd77aa387944368da3949e01e580111
- Motorola stock DT **90fa7be1db5bd47202673d4431408659149a7359**; display techpack **701a48c1db80eda2ff17154a9017783230cc22aa**; display DT **80b207bf35be5da38375e755506f136558ad24b5**.
- Oneli native **PS5169 and PTN3222** isolated candidate history, integration caution: https://github.com/Drzet/razr2022_nuc/blob/43a72d27af358243b23c7cb4c0fc93f5bd75dd3e/docs/USB_REVIEW_2026-10-14.md ; https://github.com/Drzet/linux/blob/61202a82ad004302fcc04e321075e190f00b29ed/drivers/phy/phy-nxp-ptn3222.c .
- Oneli DP evidence: https://github.com/Drzet/razr2022_nuc/blob/43a72d27af358243b23c7cb4c0fc93f5bd75dd3e/docs/displayport_oneli_aux_routing_2026-10-11.md .
- Accepted package and terminal stop condition: https://github.com/Drzet/razr2022_nuc/blob/43a72d27af358243b23c7cb4c0fc93f5bd75dd3e/docs/COORDINATOR_V2_PACKAGE_REVIEW_2026-10-21.md ; https://github.com/Drzet/razr2022_nuc/blob/43a72d27af358243b23c7cb4c0fc93f5bd75dd3e/docs/NEXT_TASKS.md .

**Tests this audit performed:** Static reading and comparison of referenced GitHub source texts, device/product configs and existing coordinator evidence; targeted public-source search. **Not performed:** full overlay preprocessing/dtbo merge for each SKU, byte-for-byte DTS semantic diff, executable test, schema, build, firmware extraction, on-device or Android-vs-native runtime validation. All undocumented physical/effective-PVT equivalences remain **[INFERRED]**.
