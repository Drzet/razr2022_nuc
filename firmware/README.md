# Firmware inventory

Track firmware filenames, SHA-256 hashes, source device/package, package build ID, extraction procedure, intended driver and validation outcome. Keep binary blobs out of Git.

The [VPU investigation](../docs/razr2022_vpu_investigation_2026-10-11.md) records a downstream `vpu20_4v` firmware name. No matching oneli binary or hash has been inspected in the committed evidence. A downstream name alone does not establish the upstream loading path or compatibility.

Use `inventory.template.json` for a verified extraction inventory. Its empty entries do not claim that no firmware is needed. Pin package/source revisions; distinguish an available package from the firmware installed on the actual device.
