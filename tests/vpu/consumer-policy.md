# SM8475 consumer production-path host tests

Run from the project root:

```sh
python3 tests/vpu/consumer-policy.py --kernel-dir /path/to/Drzet-linux --json-out /tmp/vpu-consumer.json
```

Use corrected kernel `905d2403c451838a408f6bb44e80a7cf9aa6ed10`, following consumer/quarantine delivery `3086118adc521943bd533f98d53b136cf4694bc2`, following implementation `18f326a67deb0df2ff873cb62ebae9d81c60a3b0`, binding/fixture commit `afd1712af59341447876df649ae670c046d84658` and accepted calculator `7ac8d3afedfde74286b52e11aaa1eca42a1329a5`. The checked calculator C, public header and math header are byte-identical to the accepted calculator evidence. The unchanged 1362-vector reference/differential suite is reused, not replayed.

The runner extracts actual production functions without rewriting their bodies, includes the actual public resource structures and checked calculator, and executes them against the separate host mocks. Source hashes, extracted-function hashes, compiler, command, test hashes and results are in [the result record](../results/2026-10-16-vpu-consumer.json). Kernel source/generated programs are not copied into this repository. Linux error/overflow arithmetic shims and an abstract one-element capability array are host scaffolding; actual fourcc, packed bit-depth constants, buffer attribute enum, HFI packet layout/constants and RPMh levels come from the selected kernel. Minimal type/state/list/locking representations and external provider operations are mocks.

Coverage includes:

- Explicit codec/depth/linear-output mapping, model validation, validated payload subtraction, zero-byte activity, effective operating rate, checked frequency overflow, 1080p startup clock rejection, 4K startup MB/s rejection, and distinct 409-fps route-cap versus 410-fps model errors.
- Configured-instance candidate admission, independent D/L aggregation, equality versus cap+1, u64 aggregation overflow, u32 conversion, multiple sessions, empty ready queues, high-water retention, survivor cleanup, PM-get failure, reference ownership and close-confirmed idle recovery.
- Exact supported OPP rows and asymmetric MXC/MMCX order, missing paths/domains/OPPs, negative/zero/under/over rounding, higher-row promotion, provider readback and coupled-clock mismatches. ARM64's unsigned-long boundary is covered by the u64 demand/444 MHz check; this harness does not claim 32-bit execution.
- Every position in the eight-operation bridge/final update, seven-position repair and four-operation unvote sequence. Failures can change mocked hardware before returning errors. OPP failures remain uncertain because cached same-OPP success cannot certify repaired required domains; a dedicated cached-OPP mock exercises correct clock readback with unresolved dependencies. Idle recovery cannot clear that uncertainty.
- Actual enqueue/deferred submission, input/output stream-on and DRC resume consumers, asynchronous rejected-buffer unlink/completion exactly once, sampling from 480 to 30 without dropping retained demand, final serialized HFI fault guard, STREAMOFF preflight and REQBUFS refusal on unconfirmed cleanup. Existing table/frequency behavior is exercised with the policy disabled.

The reported assertion count includes mock lock/reference/provider precondition checks. These tests execute production C under a sequential host model and UBSan, with explicit checked arithmetic. They do not execute Linux VB2 cancellation, IRQ concurrency, actual PM/provider buses, real required-OPP transitions, clock hardware, firmware or DMA. File-close quarantine and broader driver caller integration also receive ARM64 compilation/link checks; compilation is not an execution test of file release or native locking. The build has a separate [record](../results/2026-10-16-vpu-consumer-build.md).

The coordinator-requested VB2 cleanup correction adds [actual framework regressions](cleanup-framework.md), with fail-before/pass-after evidence and its own build record. The old result file remains the pinned earlier delivery; corrected consumer results are in [consumer-after.json](../results/2026-10-16-vpu-cleanup/consumer-after.json).
