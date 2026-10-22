# Coordinator review: eqs/oneli reuse audit — 2026-10-22

## Decision

Accept the [audit at 5d229112b6a8d609e38159ebd9800f687974fcda](https://github.com/Drzet/razr2022_nuc/blob/5d229112b6a8d609e38159ebd9800f687974fcda/docs/research/eqs-oneli-linux-reuse-audit-2026-10-22.md) as a qualified source comparator, with the corrections below. It supplies useful Motorola wiring corroboration, not a new working native port or a reason to replace the accepted v2 image. No new build or subsystem implementation selected.

## Independently checked useful findings

The directly inspected LineageOS device-tree snapshot is **4d2ea0ebf7a591e2c98d682a106afe4605616724**.

- [Eqs common overlay](https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/blob/4d2ea0ebf7a591e2c98d682a106afe4605616724/qcom/cape-eqs-common-overlay.dtsi) includes the common PS5169 node under SE5. [Oneli common overlay](https://github.com/LineageOS/android_kernel_motorola_sm8475-devicetrees/blob/4d2ea0ebf7a591e2c98d682a106afe4605616724/qcom/cape-oneli-common-overlay.dtsi) instead includes it under **SE18** and adds **vio-supply = L8C**. This is a concrete guard against copying the wrong board wiring. SE18/L8C were already recorded in oneli's earlier DP contract; the new value is the pinned side-by-side comparator.
- The eqs display file lines 972–998 and oneli lines 778–804 are identical for the inspected block: FSA4480 disabled, AUX GPIO2 enable and GPIO71 select, matching DP clock list. This corroborates vendor software inheritance. It does not establish eqs switch silicon, live oneli wiring or native DP operation.
- The oneli common overlay also corroborates **CHG_EN on PM8350C GPIO2** and paired-load controls on **PM8350B GPIO1/GPIO3**. It declares the SGM41516D flip charger and paired main/flip battery relationships. Keep the schematic PM8350BH identity and named FLIP nets authoritative; vendor node names and logical GPIO flags do not independently prove electrical polarity or safe charging policy.
- This same snapshot makes later targeted Motorola comparisons easier. It is not an upstream DT or an effective retail FDT: full overlay composition and physical population remain unverified.

## Corrections to the audit's actionable recommendations

1. **The WAS7227Q binding and powered GPIO-SBU adaptation already exist.** Direct inspection of accepted kernel **d28598f544682eed5997ac9d57d423e9a5031624** confirms `willsemi,was7227q` plus `gpio-sbu-mux`, a required `vcc-supply` for this part, and the regulator-lifetime implementation. The [current DP handoff](https://github.com/Drzet/razr2022_nuc/blob/2f992d150b5c13b5f98c59e4b7fb9ee802ed918d/docs/handoffs/2026-10-11-displayport-oneli.md) records accepted host/schema and ARM64 module/MODPOST run **38987006218**. Audit sections 5/9 draw partly on the historical October 11 report: do not commission another binding/driver or repeat those tests. The remaining work is **selected integration of accepted code and the full board graph**, then hardware testing.
2. **PTN3222 BUK identity is not a renewed development gate.** The [USB review](USB_REVIEW_2026-10-14.md) already accepts **1e5268277f6d4c25cde2f3e2b3f00439107e087a**: unknown readable IDs warn and continue for the oneli profile; identity-read failures remain fatal. Physical applicability remains untested.
3. Keep **GPIO91 as the agreed sole GLINK input** when composing the USB/DP graph; the audit's brief “orientation” description must not be interpreted as permission to drive it or give it a second consumer.
4. Eqs SE5 versus oneli SE18 is a routing difference. Merely sharing an I2C controller with a repeater at a different address does not prove an address collision; avoid that interpretation of the audit's “collide” wording.
5. Eqs Android header-v4 packaging supplies no new proof about oneli temporary boot or Motorola vendor_boot callbacks. Keep the accepted v2 candidate and stock vendor_boot write policy. No new UART test pad, voltage measurement, framebuffer handoff or native panel implementation was established.
6. The reported negative search for a native eqs port remains the audit author's bounded search result, not an independently exhaustive coordinator search. Floating Android product refs must be pinned before future code consumption. The vendor-only `qcom,dp-downgrade` remains a conditional research lead, not a native setting to add.

## Owner disposition and next steps

- **Boot:** retain ownership of the next separately authorized observed RAM trial using the existing image. Physical UART access/level or another useful observation route and independent stock return remain unresolved device-session preparation. No rebuild or renewed broad loader research.
- **Boot, later with USB and DP:** if USB/DP integration is selected, consume accepted PS5169/PTN/SBU candidates, preserve SE18/L8C and single GPIO91 ownership, compose connector ports and supplies, then validate the changed integrated DT/kernel once. DP's implementation is complete for its accepted isolated scope; board integration is still outstanding. This is queued conditional work, not a new active assignment.
- **Wireless, Power, GPU/display, VPU and Userspace:** remain paused. The audit supplies no demonstrated code defect or new native implementation requiring them to restart.

## Review scope

Read the complete audit, current AGENTS/STATUS/NEXT_TASKS/WORKFLOW, current DP handoff, USB review, the two pinned vendor board overlays, the matching display blocks and accepted SBU driver/binding. Source review only; no new compilation, CI, firmware extraction, overlay merge or handset operation. Prior accepted test results are reused, not represented as rerun.
