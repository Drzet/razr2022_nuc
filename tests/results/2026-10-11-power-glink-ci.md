# Power: pinned Motorola/mainline PMIC GLINK protocol CLI CI

- Date: 2026-10-11.
- **Validated GitHub Actions run:** [38168888153](https://github.com/Drzet/razr2022_nuc/actions/runs/38168888153), job `114557114053`; conclusion **success**, steps source download, source/fixture checks and artifact upload all passed. Run is a **pull-request event**, with actual Actions checkout/test-merge SHA **`58514dd3e4d81ed8fcca2ae9cc30c31016ebe9ca`**, rather than the source feature-branch SHA.
- Workflow original triggering branch commit: `f69ef3a07c65720dc3d486b08ae31f86525e2bdf`. Python **3.12.3**.
- Exact command from run:
  ```sh
  python3 tools/power/glink_protocol_audit.py \
    --vendor evidence/input/vendor.c \
    --upstream evidence/input/upstream.c
  ```
- Input source identities from Actions checkout, at fixed SHAs:
  - `MotorolaMobilityLLC/kernel-msm@9511d6b2dc469e5bd836992e3bdd6d19ace112e0` `drivers/power/supply/qti_battery_charger.c`
  - `Drzet/linux@a5ebb76233b79db01e82e061173cb73c6d2b5c6b` `drivers/power/supply/qcom_battmgr.c`
- GitHub job log **actual SHA-256**:
  ```text
  054b43468479d69f0dbfe0e5effa3751b30e19497056aabade3a28c0c2ed0618  evidence/input/vendor.c
  9591a420f5af384d37bf96dfe95b6a92a2e983dec15fe79ecb9731272ab69ea8  evidence/input/upstream.c
  247e4228593930b4691002b5f9f708e5b37057bb73574d2d717ade63f1bb37ec  tools/power/glink_protocol_audit.py
  ```
- Actual result: **6/6 synthetic unit fixtures pass**, `OK`; **8/8 common opcode values match**, **41/41 common property ID values match**, `PASS`, process exit 0. Artifact `power-glink-audit` uploaded (original C source files are **not** included in saved artifact; full input source content remains retrievable from fixed GitHub commit URLs).
- CI workflow: [`.github/workflows/power-glink-audit.yml`](../../.github/workflows/power-glink-audit.yml); reproducible source/fixture script [`tools/power/glink_protocol_audit.py`](../../tools/power/glink_protocol_audit.py).
- Strict scope: source-level compatibility and synthetic message fixtures. This does **not** establish real PMIC firmware negotiation, GLINK battery reporting, oneli sensor units or native driver runtime. No phone available.
