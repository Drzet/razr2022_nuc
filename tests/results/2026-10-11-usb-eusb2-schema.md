# USB eUSB2 PHY binding schema result, 2026-10-11

**Outcome: PASSED, binding-only CI.** Does not validate the Motorola oneli device-tree node or a kernel driver/module.

- GitHub Actions workflow: [Razr USB eUSB2 binding schema, run 38164052929](https://github.com/Drzet/linux/actions/runs/38164052929) / job `114542804907`.
- Repository: `Drzet/linux`; PR #1 with head branch `razr/usb` and base `razr/boot`. Workflow test **PR merge tree** `32156ad974d0d22282d1beabb9aee8385ca11bfc`; source USB commit carrying workflow `6ab3f710b2c8e9a455bc356673ca67293ad4d322` and schema binding change `0119d73b40bed1041278cf9307bdec9c17880618`.
- Runner: `ubuntu-24.04`, reported Linux `6.17.0-1022-azure`; DTC `1.7.0`, `dtschema 2026.9`, `pylibfdt 1.7.2.post2`, Python 3.12 venv (runner wheel ABI).
- Exact executed command (from job log; shell `set -euo pipefail`):

```sh
PATH="$PWD/.venv/bin:$PATH" \
  make DT_SCHEMA_FILES=Documentation/devicetree/bindings/phy/qcom,snps-eusb2-phy.yaml dt_binding_check \
  2>&1 | tee usb-ci-record/dt_binding_check.log
```

- Job log shows `SCHEMA`, `LINT`, `STYLE`, `DTEX` and `DTC [C]` completed with successful job outcome. [Preserved logs and full tool versions, artifact 11710884372](https://github.com/Drzet/linux/actions/runs/38164052929/artifacts/11710884372). The artifact is 845 bytes zipped and was published successfully by the job.

**Not executed:** `dtbs_check` against USB-enabled `sm8475-motorola-oneli.dts` (the Boot board tree does not yet describe USB), affected driver build, runtime USB enumeration or any hardware test. The owner does not currently have the phone.

Next schema milestone requires Boot's **pinned SHA** containing the justified eUSB2/repeater/GLINK nodes; then compile oneli DTB and run filtered `dtbs_check`, record warnings and compare to baseline.
