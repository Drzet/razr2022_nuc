# GPU GMU probe power-level failure handling: validation record

Date 2026-10-11. Kernel branch `Drzet/linux:razr/gpu`. Independently confirmed defect in pinned source: [`a6xx_gmu_init` `a6xx_gmu_pwrlevels_probe(gmu)`](https://github.com/Drzet/linux/blob/4955f07a94ea3c51e423e34d819ac3f76f1c9d37/drivers/gpu/drm/msm/adreno/a6xx_gmu.c#L2448-L2463) discarded the helper's returned errors and proceeded to build HFI tables with possibly incomplete GMU/GPU frequencies, RPMh votes and bandwidth configuration.

## Patch and cleanup validation

**Kernel commit** `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`: [independent GMU change](https://github.com/Drzet/linux/commit/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3), strictly following existing [A730v3 chip-ID commit](https://github.com/Drzet/linux/commit/4955f07a94ea3c51e423e34d819ac3f76f1c9d37). One file modified: `drivers/gpu/drm/msm/adreno/a6xx_gmu.c`, with two narrow effects:

```c
ret = a6xx_gmu_pwrlevels_probe(gmu);
if (ret)
    goto detach_gxpd;
```

And `pm_runtime_disable(gmu->dev)` added in `err_put_device`, balancing the existing `pm_runtime_enable(gmu->dev)` for all initialization failure paths after enable. This does not adjust any GPIO, OPP, HFI, clock frequency, register value or GPU firmware assumption.

The failed power-level setup now uses the **already existing** ACD-error path: if valid detach GX PD, put QMP, delete device link, detach CX PD, unmap MMIO, free registered GMU/HFI IRQs, free GMU allocations, disable runtime PM and release the `of_find_device_by_node` reference. The pre-existing ACD error path uses the same corrected PM balance. [`a6xx_gpu_init` caller](https://github.com/Drzet/linux/blob/3baaec593ae7c701e95e0c3df2d56c33d3aed4f3/drivers/gpu/drm/msm/adreno/a6xx_gpu.c#L2765-L2775) already checks GMU init errors and returns `ERR_PTR(ret)`.

**Cleanup scope:** the shared unwind still has pre-existing complexities outside this two-hunk patch: `devm_pm_opp_of_add_table(gmu->dev)` is tied to the GMU device's devres lifetime, and unrelated earlier setup may have resource-lifetime issues. The structural test checks ordering and guards; it does **not** simulate every kernel error injection or prove all such unrelated paths are leak-free.

## Tests performed

1. Prior original chip-ID GPU kernel `4955f07...`: [normal ARM64 full `Image modules` run 38174090675](https://github.com/Drzet/razr2022_nuc/actions/runs/38174090675) **PASS**. Exact project input `d0fc7d7bba683719e852311f5f2d0e3fd95a1fbe`, artifact [`gpu-msm-module-38174090675-1`](https://github.com/Drzet/razr2022_nuc/actions/runs/38174090675/artifacts/11716182125), contains `Module.symvers`, `msm.ko`, `.config`, logs, hashes and tool versions. Uploaded ZIP SHA256 `07c828f16d82f93760ad003cb716d59562ee53bbd54be7e0a35d6bd8da8c5061`. **This pass predates the GMU error-handling patch.**
2. Modified kernel `3baaec...`: [static control-flow check 38179317499](https://github.com/Drzet/razr2022_nuc/actions/runs/38179317499) **PASS**, project revision `68f17e289b8f3d4e21d8700a8662ec1e51d31e64`. It asserts checked return code, existing ACD cleanup branch, GX/QMP null/error guards, ordered link/CX/MMIO/IRQ/memory/runtime-PM/reference unwinding. Negative mutations deliberately delete the checked return, skip shared cleanup, remove PM disable or remove GX detach; **all four mutations were rejected**. Evidence [artifact 11716729054](https://github.com/Drzet/razr2022_nuc/actions/runs/38179317499/artifacts/11716729054), uploaded ZIP SHA256 `1336e6ca73690da58b1cd84be383a9c1a92267a1f9c10c9c1db97cc30543f490`.
3. An earlier static-test run [38179175912](https://github.com/Drzet/razr2022_nuc/actions/runs/38179175912) **FAILED due to a test harness defect**: one mutation changed the first global occurrence of GX detach outside the target `a6xx_gmu_init` function, creating a false negative. Script fixed in project revision `68f17e...` by restricting mutations to the specific function; the corrected test passed.
4. Modified kernel AArch64 **targeted object compile PASSED**, [run 38179435399](https://github.com/Drzet/razr2022_nuc/actions/runs/38179435399), tested project SHA `aea7f092d7f6e3eb01401062fbca86b622497da4`, kernel `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`. Real Kbuild emitted `CC [M] drivers/gpu/drm/msm/adreno/a6xx_gmu.o`; resulting AArch64 ELF object verified and hashed. [Evidence artifact 11717267945](https://github.com/Drzet/razr2022_nuc/actions/runs/38179435399/artifacts/11717267945) contains resolved `.config`, tool/compiler versions, command log, ELF header and SHA256SUMS. Uploaded ZIP SHA256 `88ea06798465b80f50bbfac6834ecd67f3877fae91b04ab89bec3fd8fa3c4a57`. This validates compilation of the **changed source**, not complete module linking/modpost.
5. New kernel full strict ARM64 `Image modules` run [38178986611](https://github.com/Drzet/razr2022_nuc/actions/runs/38178986611), input project `649aafdf4b00766c2c22cae34f2212b7c71c94d5` pinned kernel `3baaec593ae7c701e95e0c3df2d56c33d3aed4f3`, was still **in progress** at this record update; its conclusion must be inspected before claiming dependency-complete new module linking.

**Hardware validation:** none; stock phone disconnected. Deliberately no firmware or CX power profile change. The board GPU remains disabled.
