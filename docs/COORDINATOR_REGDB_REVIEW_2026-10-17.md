# Coordinator review — signed regulatory database, 2026-10-17

## Decision

Accept Userspace source **840d53bbceadc4fb33248c2d2487795d35160dd0** and documentation **eff19bcff7d5eb0fc1f181f4c86b9aa32bb18846** for packaging and focused QEMU software scope. Close the assigned regulatory.db correction. No blocking source finding. Activate the previously queued VPU firmware-specific RESUME adaptation; exact instructions are in [NEXT_TASKS](NEXT_TASKS.md). Userspace and GPU pause.

## Review and evidence

Inspected staging, guest preparation and smoke-check scripts. The versioned layer verifies the original tar, installs normal Debian wireless-regdb from the same signed snapshot, selects the upstream-signed database/signature pair compatible with the kernel's existing trusted keys, verifies resolved paths and package integrity, and preserves previous artifacts. Temporary test-helper adaptation replaces one asserted parent-tar hash only; it does not weaken the retained original helper.

Independently checked automatic [run 39061160706](https://github.com/Drzet/razr2022_nuc/actions/runs/39061160706): cheap job **117479241735** and focused guest job **117479264038** succeeded. The job log records **RAZR_REGDB_QEMU_PASS**, evidence checksum validation, and archive digests below. Inspected the guest's positive `iw reg reload` check and exact kernel 7f3865e `reg_reload_regdb()`: the operation requests regulatory.db and returns failure if `valid_regdb()` rejects it. Thus this test does more than grep for absent errors. No coordinator rerun or kernel rebuild was performed. Raw guest details and inner-file hashes below are owner-recorded evidence; the coordinator inspected CI logs/source, not a newly downloaded archive.

| Item | Identity |
| --- | --- |
| Existing kernel | 7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce / 7.3.0-rc6-g7f3865ee17c3 |
| Debian package | wireless-regdb 2026.05.30-1~deb13u1, all; snapshot 20261011T000000Z |
| Rootfs artifact | 12111471711 |
| Rootfs ZIP SHA256 (CI) | ec1d7ea5e9e45cded5cfb801e6e238fcf2adf8e18724080cad0049e371039aa4 |
| Rootfs tar SHA256 (handoff) | 630738c3ac43726199f56d326511fb8a69a443a01eea8e0a234318de5d3e8b38 |
| Evidence artifact | 12111960073 |
| Evidence ZIP SHA256 (CI) | 9c69889bbacf1687e2e5906c46f610cd97c74361a71c30fcb00ae91e50368eb0 |
| Selected DB SHA256 (handoff) | 2fb33ca0074db573e05ef7dd50bb45b63c0ff98b7e852e1105ebad536fae8e6b |
| Selected signature SHA256 (handoff) | c941c08f51c93e46722293b85631604c3740d86c3de0c75f79aef50d2e919179 |

Owner reports world domain 00/DFS-UNSET, successful signed reload and clean guest exit; no country override. Earlier canceled/failed attempts remain historical, superseded by this pass.

## Limits and next work

QEMU validates packaging and the kernel's software database acceptance, not handset Wi-Fi/BT, native root storage or RF operation. Accepted diagnostic-v2 release remains unchanged. No handset test or flash is assigned.

The accepted Xiaomi comparison already identifies one small useful VPU adaptation: payload-free RESUME for both settings-change and drain, limited to the inferred oneli firmware profile. Select that work now, retaining VPU2, conservative startup, disabled integration gate and user-accepted /3. Default encoding for other firmware profiles must remain unchanged. No further broad firmware audit, chip-ID prerequisite or display activation.

Boot and DP retain their existing documentation-only closures if still outstanding; Wireless, Power and USB remain paused. No additional implementation stream or expensive rebuild is selected.
