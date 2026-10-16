# VB2 ownership and file-release regressions

The correction is kernel `905d2403c451838a408f6bb44e80a7cf9aa6ed10`, following rejected delivery `3086118adc521943bd533f98d53b136cf4694bc2`. Coordinator assignment: `432f2f84f6350f0c1b7670b751bf41fd349048ce`.

Run the actual framework/driver control-flow suite:

```sh
python3 tests/vpu/consumer-policy.py --framework --kernel-dir /path/to/linux --json-out /tmp/cleanup-after.json
```

For each regression, select `failed-start`, `nonstreaming-cancel` or `successful-close`:

```sh
python3 tests/vpu/consumer-policy.py --framework --kernel-dir /path/to/linux --kernel-ref 3086118adc521943bd533f98d53b136cf4694bc2 --case failed-start --expect-failure --json-out /tmp/cleanup-before.json
```

`--expect-failure` requires the specific regression assertion; an unrelated failure does not count. `--kernel-ref` retrieves pinned source bytes with `git show`, preserving the checkout. Both revisions use identical unchanged calculator bytes. The runner masks comments while locating definitions and retains complete multiline return types; hashes identify each unchanged extracted function body. Generated sources/binaries remain outside the repository.

The framework suite executes production VB2 `vb2_start_streaming`, `vb2_buffer_done`, enqueue, queue cancellation, streamon/off and queue release; production V4L2-M2M stream ioctl/context release functions; and Iris start/stop callbacks, decoder start, completion wait, stream guards, resource release, file close and buffer-return helpers. It retains their actual control flow, including VB2's forced reclamation after a callback failure. Framework states and the public resource layout come from the selected kernel. The external mocks represent types, ready-list storage, allocators, scheduler/spinlocks, provider calls and firmware responses. Real Linux IRQ scheduling, DMA/provider buses and firmware are not executed.

Six targeted cases pass **645 assertions**, including mock reference/lock checks:

| Case | Boundary exercised |
| --- | --- |
| Partial submission / failed start | Second deferred submit fails, CLOSE times out through the production wait helper. VB2 remains streaming with both buffers ACTIVE and driver-owned. STREAMOFF/REQBUFS/repeated STREAMON cannot reclaim or redispatch them. A successful CLOSE response later permits cancellation and exactly one completion per buffer. |
| Nonstreaming cancellation | A reserved uncertain/unclosed instance with streaming=false is rejected before actual VB2 cancellation. It retains mappings and firmware ownership. |
| Successful file release | Real stream ioctls and driver callbacks start both queues, then actual `iris_close` releases demand and the M2M/VB2 context. CLOSE survives every callback, no STOP is emitted for the removed session, all three mappings are freed once, and a survivor's reservations/PM reference remain intact. |
| Quarantined file close / late CLOSE | Timeout retains the context, mappings, PM and module/device references. A late successful CLOSE is consumed without callbacks to the detached handle or unassigned reclamation. |
| Admission rejection | 1080p startup rejection submits no firmware buffer; subsequent streamoff/close succeeds without unsafe completion. |
| Legacy platform | The original VB2-callback start/stop path remains selected and balances ownership without adopting SM8475 reservations. |

The first three assertions fail on the published old kernel and pass with the same framework control flow on the correction. [Before/after evidence](../results/2026-10-16-vpu-cleanup/) records source/test hashes, exact revisions, commands and diagnostics. The original 52 consumer scenarios also pass after the change (2325 assertions; the additional guard locking changes the precondition count). Their unchanged arithmetic vectors and binding/schema evidence are reused.

SM8475's post-VB2 firmware start can return STREAMON errno while VB2 remains streaming and buffers remain ACTIVE. This is deliberate: error flags stop new work, and guarded streamoff/confirmed close establishes quiescence before cancellation. The implementation does not promise that a failed ioctl made firmware-owned memory reusable. Minimum queued-buffer count remains zero for this profile so VB2 commits during STREAMON; no delayed QBUF start path is introduced. The existing M2M device_run callback is empty, so its scheduling step does not submit Iris firmware work between the framework commit and checked start.

This supplies host control-flow evidence, not a Linux runtime/concurrency or physical DMA result. Supported STOP/CLOSE and existing Linux frameworks are reused; no reset, fake CLOSE success, generic VB2/IOMMU rewrite or new reclamation operation is introduced.
