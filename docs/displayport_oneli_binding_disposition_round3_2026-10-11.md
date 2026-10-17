# Oneli DisplayPort AUX binding disposition and USB/Boot contract, round 3

- **Date:** 2026-10-11.
- **Owner:** DisplayPort, project branch `razr/displayport`.
- **State:** pinned source checks implemented/passed in CI; **no AUX binding or board enablement patch**; hardware testing deferred.
- **Mainline/kernel baseline:** `Drzet/linux@a5ebb76233b79db01e82e061173cb73c6d2b5c6b`, kernel `razr/displayport` unchanged at baseline.
- **Oneli physical stock evidence:** [Android 14 ADB capture](oneli_stock_android14_adb_hardware_capture_2026-10-11.md), XT2251-1 PVT, hwrev `0xC000`, SKU `dn`, fingerprint `motorola/oneli_ge/oneli:14/U2SLS34.1-42-14-11/e37c37-31202:user/release-keys`; session ended after capture.

## 1. Reproducible pinned routing assertions: **passed**

- Source: [`tests/displayport/oneli_dp_source_audit.py`](../tests/displayport/oneli_dp_source_audit.py), project commit `8ee6b67de1e5ed733924e0221ab3479ed5bac67c`.
- CI: [`razr-displayport-source.yml`](../.github/workflows/razr-displayport-source.yml), project/tested SHA **`fc5f56328b3cf2569705c8ebd56f280be90b2960`**.
- **Run:** [38174309894](https://github.com/Drzet/razr2022_nuc/actions/runs/38174309894), job ID `114573300965`, **completed / success**; Python **3.12.3** on `ubuntu-24.04`. CI printed `Project SHA: fc5f56328b3cf2569705c8ebd56f280be90b2960`, `Source assertions: 23/23 passed` twice (network and offline replay), `VERIFIED: 23/23 pinned-source assertions`.
- Integrity test deliberately appended text to cached `vendor_aux` source: expected Git blob SHA `633e1324ca2447635dfd829fd823e24b98fc46ac`, actual `fbe73e5bffdde1cf54bd24ddf610ff5ed7a03461`; audit rejected input with `SOURCE_ERROR` and CI integrity step passed.
- Artifact: **`oneli-displayport-source-audit`**, GitHub artifact ID `11715520550`, 3,784 bytes, workflow-reported digest `sha256:66d5cddba12bb9c4b794b2b4e0067a5e3d4c9eedaa94c2ab9fa07435055e43fd`. Two JSON reports retain pinned source repository/revision/path, Git blob and SHA-256, assertion labels and line evidence.
- To rerun (Python standard library only; network for the initial download):

```sh
python3 tests/displayport/oneli_dp_source_audit.py \
  --cache /tmp/oneli-dp-pinned --output /tmp/oneli-dp-report.json
python3 tests/displayport/oneli_dp_source_audit.py \
  --cache /tmp/oneli-dp-pinned --offline --output /tmp/oneli-dp-offline.json
```

The 23 checks comprise **13 vendor AUX GPIO/generic SBU checks** and **10 existing reciprocal mainline source/HDK-comparator graph checks**. The HDK is only a *comparator*. Verified Git objects are from Motorola display driver `701a48c1db80eda2ff17154a9017783230cc22aa`, Motorola display DT `80b207bf35be5da38375e755506f136558ad24b5`, and selected mainline baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b`.

**Validation boundaries:** This is source-text pattern checking with immutable file identity, **not** a semantic C execution test, resolved-FDT check, schema pass, compiled kernel or proof of oneli physical operation. The 23/23 status must not be misreported as kernel/display validation.

## 2. USB graph agreement recorded; no duplicate ownership

The USB owner **acknowledged issue #3** in [comment 6113097851](https://github.com/Drzet/razr2022_nuc/issues/3#issuecomment-6113097851), naming a versioned [USB graph contract v1](https://github.com/Drzet/razr2022_nuc/blob/razr/usb/docs/typec_graph_contract_v1_2026-10-11.md), originating project commit **`9bb9721bf3546669273c55c328c3099ceb59e8f0`**. Power independently [confirmed rail/ownership boundaries](https://github.com/Drzet/razr2022_nuc/issues/3#issuecomment-6113030907). This is **explicit agreement** with USB and Power at the source/contract level; Boot's implementation/acceptance is not thereby implied.

| Graph / GPIO | Contract owner | Exact mapping or hold |
| --- | --- | --- |
| `connector@0/port@0` | USB proposes, Boot edits DTS | Reciprocal `usb_1_dwc3_hs`, USB2/role path; staged independently of DP and PS5169 |
| `connector@0/port@1` | USB proposes, Boot edits DTS | PS5169 `port@0` (connector facing) ↔ PS5169 `port@1` (QMP facing) ↔ `usb_1_qmpphy_out`; **do not create PS5169 AUX port@2** |
| QMP `port@1` and `port@2` | Baseline link, Boot preserves | DWC3 SuperSpeed and DRM DP0 input; existing reciprocal link checks passed |
| `connector@0/port@2` | DisplayPort proposes, Boot edits DTS | **Independent AUX/SBU switch only**; node and phandle withheld pending compatible |
| TLMM91 | **PMIC GLINK sole input owner**, USB | `orientation-gpios` active-high (software CC2). PS5169 cannot request GPIO91 separately |
| TLMM19 | USB / PS5169 | Vendor high=enable, low=disable. The upstream candidate `reset-gpios` pulse is **not proven equivalent** |
| TLMM2 | DisplayPort AUX switch | Vendor writes 1=disable, 0=enable; logical active-low mapping **[INFERRED]** if IC driver is appropriate |
| TLMM71 | DisplayPort AUX switch | Vendor writes 0=CC1, 1=CC2; logical active-high mapping **[INFERRED]** if IC driver is appropriate |
| Rails S10B/L8C etc. | Power contract, Boot supplies | PS5169 VCC S10B/VIO L8C; full regulator parent/enable proof still pending |

Upstream Qualcomm PMIC GLINK and QMP PHY provide the architecture for orientation/mode/HPD, but firmware message compatibility on the installed Android 14 build and real electrical behaviour are untested. **Boot alone** edits `sm8475.dtsi` / `sm8475-motorola-oneli.dts`. The above is a contract, **not** permission to enable DP.

## 3. GPIO-SBU binding investigation and bounded blocker

Existing Linux binding [`gpio-sbu-mux.yaml`](https://github.com/Drzet/linux/blob/a5ebb76233b79db01e82e061173cb73c6d2b5c6b/Documentation/devicetree/bindings/usb/gpio-sbu-mux.yaml) requires a *specific part-compatible* followed by `"gpio-sbu-mux"`, and `select-gpios`, `orientation-switch`, a Type-C `port`, plus `enable-gpios` when `mode-switch` is set. Its allowed part compatibles in the pinned kernel are:

- `nxp,cbdtu02043`
- `onnn,fsusb42`
- `onnn,fsusb43l10x`
- `pericom,pi3usb102`
- `ti,tmuxhs4212`

**No oneli source or accessible stock DT property establishes any of these five part identities.** Vendor `mmi,aux-switch-*` properties prove the GPIO IDs and software levels, not the switch manufacturer/part or physical wiring. The Android 14 ADB capture could list DT *directories*, but extracted **zero property files**, so it cannot identify the IC or an active node. Motorola's `fsa4480` DT node is **explicitly disabled** on oneli and the inspected driver has its FSA notifier/event calls commented out. Its inherited phandle only serves a vendor initialization guard. The PS5169 is the high-speed redriver **without integrated AUX switching**.

**Existing driver fit, carefully bounded:** `gpio-sbu-mux.c` uses `enable-gpios` logically asserted for DP states C/D/E, disabled for safe/USB states, and `select-gpios` according to Type-C orientation. **[INFERRED]** If the real mux is a supported GPIO-SBU part, a GPIO2 `GPIO_ACTIVE_LOW` and GPIO71 `GPIO_ACTIVE_HIGH` mapping reproduces Motorola's connected software levels. It is not proven by matching this truth table that an allowed first compatible is electrically or semantically valid.

**One subtle source-level difference:** Motorola's disconnect path explicitly writes **GPIO71=0** along with GPIO2=1, whereas the generic `gpio_sbu_switch_set(TYPEC_ORIENTATION_NONE)` sets `enabled=false` but **does not reset the stored `swapped` value**; after a CC2 detach, select can remain logically true while the switch is disabled. The next NORMAL orientation call resets select. This difference is not a demonstrated failure and does **not** justify changing generic behaviour for all users without further review; note it in runtime validation and potential narrowly scoped compatibility review.

**Valid routes after new evidence:**

1. Identify the **physical AUX/SBU IC** from Motorola's PVT board BOM/schematic, board marking, precise vendor/reference stock DT property (not a directory name), or another attributable source.
2. If it is one of the five listed parts, reuse that binding/driver with properly reviewed GPIO polarity, supplies, Type-C graph, and disabled staging followed by `dt_binding_check`/`dtbs_check`.
3. If it is a different part but truly has identical GPIO switching, propose a **part-specific, evidenced** extension to the existing binding, and driver adjustment only if required; validate the actual compatible. If behaviour differs, investigate a new narrow driver/binding **after** evidence.
4. **Present status:** *identity unknown; binding blocked*. Do not add bare `"gpio-sbu-mux"`, falsely claim one of the five, assume FSA4480, or add a speculative board node.

No credible additional part identification was obtained from the checked Motorola source, stock capture or targeted public lookup. No DP kernel patch was produced, no oneli DTB/graph/schema validation of an implemented node exists.

## 4. Stock Android evidence and next physical test

The now recorded **physical** XT2251-1 PVT / Android 14 capture enumerated `card0-DP-1`, but `/sys/class/drm/card0-DP-1/enabled` returned `disabled`; `status` and `modes` returned permission denied. Therefore the *stock Android DRM connector is registered*, not tested with a DP monitor or known-working AUX/PS5169. Neither installed DTB/DTBO identity nor chosen overlays were captured.

The next physical opportunity should record, **on stock Android without modifying firmware**, a known DP-Alt-Mode-capable powered dock and monitor in both plug orientations, DP connector enabled/status/mode (where permitted), video actually visible, USB sink-power + host-data capability and `dumpsys usb`; these measurements still would **not** constitute native Linux DP success.

The native acceptance remains the [dock procedure](../tests/procedures/2026-10-11-displayport-dock.md): logged HPD, AUX/DPCD/EDID, KMS, retimer/USB3/PD and repeated plug orientation **only after** authorized boot, valid board graph, and complete driver/power dependencies.

## 5. Integration and handoff

| Stage | Evidence |
| --- | --- |
| Research/source-audited | **Yes**, immutable Motorola/mainline inputs and explicit USB/Power contract |
| Source-check implementation | **Yes**, project branch `razr/displayport`, tested SHA `fc5f56328b3cf2569705c8ebd56f280be90b2960` |
| Automated host/source validation | **Passed**, 23/23, offline replay and tamper rejection, run `38174309894` |
| Kernel `razr/displayport` implementation | **None**; at baseline `a5ebb76233b79db01e82e061173cb73c6d2b5c6b` |
| Binding / compiled oneli DP DT / schema | **No candidate**; AUX identity and USB/PS5169 prerequisites unresolved |
| Native hardware DP | **Deferred**; device unavailable after stock ADB capture |

**Consumers:** Coordinator to review documentation/CI and consider merging scoped project changes; USB to maintain graph contract, PS5169 candidate, GPIO91 and `port@1`; Boot to accept connector graph only after reviewed dependencies, keeping DP0 and GPIO-SBU held; Power owns rail constraints; DisplayPort resumes driver/DT work after attributable mux identity, then physical DP once handset returns.

**No merge/cherry-pick into kernel branches, no baseline change, and no coordinator-owned aggregate STATUS/NEXT_TASKS modification.**
