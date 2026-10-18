# Coordinator reduced configuration review — 2026-10-18

## Decision

Accept Boot configuration preparation **a0726ef69177c21755bc28b60de244681bf80f40**, final handoff **0e6728c8336dc6dd9b6c4dc6a46d99fe99d6a2cd**, for source and resolved-Kconfig scope. Select one full build/package assignment for the exact reduced configuration; no release promotion or hardware claim.

## Verification

Inspected the 62-platform exclusion fragment, contract checker and config-only workflow. Kernel source remains **7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce**. The recipe verifies the accepted config hash, uses upstream merge_config.sh and real olddefconfig, and retains QCOM/VEXPRESS. No kernel, DTB or QEMU build occurred.

Read successful job **117712429303**, [run 39139991644](https://github.com/Drzet/razr2022_nuc/actions/runs/39139991644). Downloaded artifact **12141466452** and independently verified ZIP SHA256 **afa33a29a23cd6741655d081d57906f108361d1c56b1a363e8c1bc7748bcf4e3** and every internal SHA256SUMS entry. Inspected resolved configs, removed-symbol list, full diff and the recorded y/m change. Independently reran the submitted checker against the downloaded config bytes and pinned fragments: PASS. This reruns the contract checker, not Kconfig resolution or compilation.

| Config | y | m | Enabled total |
| --- | ---: | ---: | ---: |
| Accepted broad | 3301 | 1536 | 4837 |
| Reduced candidate | 2246 | 1034 | 3280 |

Candidate SHA256 **97ee634780847771163608e353e0086eceee6347ccd42a4d9d87d04f967981be**. Removed 1557 enabled symbols (32.2%); no newly enabled symbols. The checker verifies 85 explicit requirements, 26 radio selections, 16 QEMU built-ins and preservation of 253 accepted consumer symbols; these sets overlap and are not additive test counts.

The sole retained y/m change is **GPIO_REGMAP y → m**. Pinned GPIO Kconfig identifies it as a hidden tristate helper; the removed Realtek GPIO_RTD1625 built-in selected it. Reviewed config retains the helper as a module and preserves SM8450 pinctrl, ARM SMMU and all asserted functional dependencies. This is not a required oneli consumer transition and is not a blocker to compilation validation. The explicit checker is not exhaustive hardware dependency proof. Non-boolean removals in the inspected diff belong to removed Apple/Samsung/SH/HDA/FSL options.

## Build decision and remaining limits

No blocking source/config finding. Full compilation/link and QEMU have not exercised the reduced selection. Select Boot's first build using the reviewed config, unchanged kernel and reused verified DTB; do not repeat unchanged DT/schema tests. Require a distinct kernel release identity so new configuration modules cannot silently mix with the accepted broad-build modules. Check tool/config identity before expensive work.

The config-only workflow uses versioned distro packages and records tool versions, rather than an immutable package environment; future reproducibility therefore requires verifying resolved config/tool identities. The checker records additions/y-m changes rather than universally rejecting them; the reviewed exact artifact has zero additions and the one explained transition above. Changed inputs require fresh review, not automatic acceptance from a green result alone.

Record actual compilation time and output sizes; 32.2% fewer enabled symbols does not prove a corresponding speedup. Deliver complete matching modules and manifests for coordinator review, then assign Userspace compatibility checks against the fixed producer. Preserve accepted radio/diagnostic artifacts throughout. [NEXT_TASKS](NEXT_TASKS.md) activates Boot only; other agents remain paused.
