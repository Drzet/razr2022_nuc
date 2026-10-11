# USB PS5169 candidate: source-object and binding schema test

Date: 2026-10-11. **PASS** on independently compiled candidate and candidate YAML example, NOT oneli hardware validation or full kernel module integration.

## Source and exact tested commit

Kernel branch Drzet/linux razr/usb at **87d7277ced4c562e2379ee58aaed5c5fd7db4f32**. GitHub Actions [run 38170306651](https://github.com/Drzet/linux/actions/runs/38170306651), job **114561359738**, concluded **success**. [Artifact 11713402217](https://github.com/Drzet/linux/actions/runs/38170306651/artifacts/11713402217) contains original source hashes, local candidate diffs, schema and object compile logs, full resolved kernel configuration, tool versions and object checksum.

External original unmerged v3: [Esteban Urrutia's August 2026 PS5169 series](https://patchew.org/linux/20260810-ps5169-bup-v3-0-a2178b2834d7@proton.me/), applied using git am --3way in a temporary CI checkout retaining patch authorship. Patchew regenerates the mbox envelope timestamp on each download, so the workflow verifies the *applied unmodified source files*, before any local edits, by fixed SHA-256:

- Original drivers/usb/typec/mux/ps5169.c: b76465571bc5a7f80a177660e9290115fedcfbccda1fb43c801e25a6f3a521ed
- Original Documentation/devicetree/bindings/usb/parade,ps5169.yaml: 3c9f01f921398edf34e7d3b13439306bd26e8f48a75151294ec529c83b852cc3

The two narrow committed scripts scripts/razr/ps5169-candidate-headers.py and scripts/razr/ps5169-candidate-power.py add missing direct header includes, then replace the VCC-only supply logic with bulk-managed **VCC and VIO** regulators, and add a required **vio-supply** to the binding. Motorola oneli identifies VCC as PM8350 S10B and VIO as PM8350C L8C. No GPIO19 reset/pulse changes were made. Both candidate diffs are in the artifact.

## Actual commands and evidence

On ubuntu-24.04 x86-64 runner, with build-essential, bc, bison, flex, libelf-dev, libssl-dev, libncurses-dev, dwarves, curl and an isolated Python dtschema virtual environment, after git am and scripts:

- PATH="$PWD/.schema-venv/bin:$PATH" make DT_SCHEMA_FILES=Documentation/devicetree/bindings/usb/parade,ps5169.yaml dt_binding_check
- make x86_64_defconfig
- scripts/config --enable I2C --enable REGMAP_I2C --enable DRM --enable DRM_BRIDGE --enable TYPEC --enable TYPEC_MUX_PS5169
- make olddefconfig
- grep -qx 'CONFIG_TYPEC_MUX_PS5169=y' .config
- make -j2 V=1 drivers/usb/typec/mux/ps5169.o

The Actions shell used set -euo pipefail, confirmed schema SCHEMA/LINT/STYLE/DTEX/DTC example, a resolved CONFIG_TYPEC_MUX_PS5169=y, and compiler CC of ps5169.o. SHA256 object e7bcd730b97e1053b7398b79d74e204f1cf1e2396b2dbb38fdfb16faebc0eec2.

Earlier [header-only compile run 38169662388](https://github.com/Drzet/linux/actions/runs/38169662388) and [VIO+schema run 38170118109](https://github.com/Drzet/linux/actions/runs/38170118109) passed. An intermediate [run 38169898682](https://github.com/Drzet/linux/actions/runs/38169898682) failed only at its temporary mbox checksum before applying patches, and was corrected with source-level hashing. This is not a kernel C compilation failure.

## Scope boundary

The candidate original driver and YAML are created **ephemerally in the CI checkout**. Kernel branch contains the scripts and workflow, **not a permanently added PS5169 driver**. No full dependency-resolved modpost/module, ARM64 target kernel, Boot oneli DTB/graph, driver reset timings, GPIO91 firmware, actual I2C probing, USB3 signaling, DP, or hardware test performed. Motorola GPIO19 is source-backed as high-enable/low-disable but physical reset equivalence to the proposed upstream reset-gpios pulse remains unconfirmed. Actual Type-C connector contract is documented separately. The phone is unavailable.

Next step: source-prove GPIO19 enable/reset role and power sequencing before permanently integrating the candidate driver and binding; leave PS5169 disabled. Consumer: USB, Boot and DisplayPort.
