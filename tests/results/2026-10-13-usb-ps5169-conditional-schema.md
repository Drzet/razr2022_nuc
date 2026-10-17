# PS5169 oneli conditional schema and production-probe rejection: tenth review closure

**2026-10-13, USB agent.** This is a source/schema result only. The experimental kernel series remains board-disabled, outside accepted `razr/integration`. Execution authorized by [tenth coordinator tasks](https://github.com/Drzet/razr2022_nuc/blob/main/docs/NEXT_TASKS.md); the prior accepted full ARM64 compilation was **not repeated** for fixture-only tests.

## Frozen input revisions and accepted earlier kernel build

- Kernel: `Drzet/linux:razr/usb-ps5169`, final fixture/binding head **`4dcbc7ba1c04afea37ab0b0caf6b4c16bfcc3dfe`**. This includes the earlier production source `8356706a0e58916bd6149da085db6072b8feeee8` unchanged, newly corrected PS5169 binding and fixture-only checks. Compare source-code diff against `8356706`: no `drivers/usb/typec/mux/ps5169.c` edit.
- Accepted full ARM64 source/binding job **115057293411**, [run 38323664587](https://github.com/Drzet/linux/actions/runs/38323664587), completed 2026-10-13 00:27:35 UTC, normal `Image modules` modpost, linked AArch64 `ps5169.ko`. This tests **kernel head `8356706`**, before current YAML correction. Historical build-record [artifact 11781795488](https://github.com/Drzet/linux/actions/runs/38323664587/artifacts/11781795488), GitHub-reported ZIP SHA256 `996acbe635a6c33240ccc04f83e4f727af56a320fec94cce02f570427dcabb65`. It contains build logs/config and metadata, NOT deployable kernel/modules. CI-reported Image SHA256 `c437c7e71743e21cbfa1d00c6ec24468f9ffee4fc4bf1c7757c393c11e0759ea`, Module.symvers `ad4f64708b64e132fea71feb4602c437831a2c4f267708f2f8cfcf63725d9`, and PS5169 module `4d141eb37d3a1fc090aafacf182fc99c9ec77d6da45a4c84dbad9edc8fd473e2`. These binary digests are **CI-produced/recorded**, not independently downloaded and hashed by USB.
- Source producer still [VPU's accepted four-overlay PS5169 record](../usb_stock_pvt_variant_ps5169_2026-10-12.md): `motorola,oneli-ps5169` is a proposed driver-specific ABI for reference stock PVT, not confirmed bootloader-selected live compatible.

## Actual validation defect fixed

The fifth-round PS5169 binding expressed seven prohibitions using YAML flow sequences of the form:

`required: [parade,dp-eq-db]`

**This is parsed as TWO required property names, `parade` and `dp-eq-db`, not the property `parade,dp-eq-db`.** Schema compilation and generic examples still passed, but the oneli conditional silently allowed each forbidden property. The first new [test run 38383360656](https://github.com/Drzet/linux/actions/runs/38383360656) successfully compiled the positive oneli fixture and then **correctly failed its negative-test assertion** on this exact bug. No such negative acceptance is now described as a PASS.

A separate kernel binding commit **`fe1d09829d1cf0f2e42dc8826a54d2c354bc1f96`** corrects all seven to:

`required: ['parade,dp-eq-db']`

with matching quoting for USB RX EQ, USB TX EQ, DP gain, USB RX gain, USB TX gain and fine-tune LFPS. Existing `enable-gpios` versus `reset-gpios` exclusive choice remains unchanged.

## Positive and negative fixture evidence

New source files:
- `tests/usb/ps5169/oneli-valid.dts` at commit `a67b0bd0874e1ed62fae2189bcafecf61c858761`: standalone fixture, mock regulators and GPIO provider, `compatible = "motorola,oneli-ps5169", "parade,ps5169"`, `enable-gpios = <&tlmm 19 0>` (active-high), both required supplies, graph ports, switch and retimer flags, **none** of the generic tuning overrides. Not a proposed shared oneli DTS.
- `scripts/razr/ps5169-conditional-validation.py` commit `67580ee17db0ec21f735251a95a9c5a3503e3f6f`: builds actual full processed PS5169 + USB-switch schemas, compiles valid and **eight** derivative negative `*.dts` fixtures to actual `*.dtb` using `dtc`, checks the real `fdtget` cell triplet `<phandle 19 0>`, then executes `dt-validate -s processed-schema.json -l parade,ps5169`. Seven forbidden overrides are each tested separately, plus both enable and reset GPIOs specified together. It asserts precise retimer diagnostic/schema identity and `not:anyOf` rejection rather than accepting arbitrary warnings or command exit codes.
- The same script augments the existing, previously tested `scripts/razr/ps5169-probe-fault-injection.py` **in memory** with presence of each named forbidden property, then recompiles and calls actual production `ps5169_probe` and `ps5169_remove` extracted from unchanged kernel C. All seven cases return `-EINVAL` before any register writes, release supplies and acquired dependencies and allow successful reprobe. Host services remain mocks, not actual Linux devres/electrical behavior.
- `.github/workflows/razr-ps5169-conditional-schema.yml` [separate fixture-only Actions job](https://github.com/Drzet/linux/actions/workflows/razr-ps5169-conditional-schema.yml), pinned `dtschema==2026.6`. Old `.github/workflows/razr-ps5169-fault-ci.yml` job gate was updated at `fc1954a9715e5822ed6e7cd07f054d70cc355a61` so binding-only/fixture-only commits no longer trigger an unchanged ARM64 `Image modules` job; driver-source changes still trigger full linking.

**Accepted PASS:** [run 38383690974](https://github.com/Drzet/linux/actions/runs/38383690974), job **115250104673**, source checkout **`4dcbc7ba1c04afea37ab0b0caf6b4c16bfcc3dfe`**. Executed **1 valid, 7 forbidden-override negatives, 1 mutually-exclusive GPIO negative, and 7 production probe override rejection/cleanup/reprobe tests.** Every negative produces the named PS5169 schema diagnostic, and positive has no validator output. In both valid and invalid fixtures, `fdtget -t x` confirms the compiled enable GPIO cell triplet phandle (fixture local) / pin 19 / flags 0.

`dt-validate` (dtschema 2026.6) returns **exit code zero even on these emitted schema errors**; test program deliberately requires matching nonempty diagnostics for each rejected case. This avoids a dangerous false-green test outcome.

[Artifact 11804747283](https://github.com/Drzet/linux/actions/runs/38383690974/artifacts/11804747283) contains actual compiled fixture DTBs/DTSs, processed JSON schema, per-fixture schema diagnostics, generated runtime host harness, executable output, hashes, and machine-readable results. ZIP SHA256 **`207750bb561ee49fa977705489edd3f94d7a5f66ad0bcd239d16eb590b3112b7`** was **independently recomputed by USB** from the downloaded artifact ZIP and agrees with GitHub's artifact digest. Contents were opened and checked; compiled `enable-gpios` cell arrays show `[3,19,0]` in fixtures. Fixture source SHA256 `b397c8bfdd09ce0e3fb05c87b770d79b01baf494d726bda5ecbdb1278df5610b`; checked binding SHA256 `f29cf0c237b386dc82257ebf91171f0409cdd200dc81c4dcbbab7c49931cc399`; unchanged driver source SHA256 `238cb7343c30003da59a24b875b3cdecedcc9198fa74762235e05fdec33aabd3`.

## Boundary and final disposition

- **USB tenth-round closure accepted by owning agent:** conditional schema positive/negative coverage, runtime override rejection in actual probe C with mocked providers, and exact prior full-build record are complete.
- **Still held:** reference NXP exact hardware identity, actual PS5169 register semantics, S10B/L8C electrical parents, Type-C/DP wake/replay and any physical native link behavior. Source-only USB evidence cannot establish those.
- **No board enablement, shared Boot DTS edits, PM power cycling, new ARM64 kernel binary or integration promotion.** Accepted `razr/integration` remains `2b5acf108ae37040ac1e652e029bb37f5609e886`; PS5169 PR stays draft and experimental.
- Additional work should start only for a concrete review defect, new attributable hardware evidence or selected future device session. Pause USB as assigned.
