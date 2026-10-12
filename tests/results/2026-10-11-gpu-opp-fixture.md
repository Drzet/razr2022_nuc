# GPU: compiled SM8475 OPP fixture result

- Date: 2026-10-11
- Evidence type: **build-tested temporary DTS proposal**, **not** an integrated Boot commit, hardware result or working GPU.
- Workflow: [GPU OPP compiled-DT fixture](https://github.com/Drzet/razr2022_nuc/actions/runs/38164310160), run ID `38164310160`, attempt 1; **completed success**.
- Project revision executed: `7e606e2f6c8e2fa54ba94386fd2776c6208c2f97`.
- Kernel checkout: `Drzet/linux` Boot revision `cbde49d927478decd6d608a309a7d7482992f776`, pinned by immutable SHA.
- External inputs: proposed GPU OPP snippet from [handoff](../../docs/handoffs/gpu-2026-10-11.md); no external kernel patchset; independent driver patch `4955f07a94ea3c51e423e34d819ac3f76f1c9d37` **not included in this DT-only build**.
- Host: GitHub Actions `ubuntu-24.04`, compiler `gcc-aarch64-linux-gnu` and `dtc/fdtget` versions preserved in the run artifact's `environment.txt`. Other installed packages captured in `apt-install.log`; exact versions are not reproduced here.
- Source fixture: [`tests/scripts/gpu-opp-fixture.py`](../../tests/scripts/gpu-opp-fixture.py).
- Build configuration: ARM64 `defconfig` generated via `make -C kernel O=<temporary output> defconfig`. Generated `.config` preserved as `kernel.config` in artifact.
- Firmware: none extracted or loaded. No initramfs, image packaging, actual device revision, or actual installed firmware is known.

## Commands and results

Commands from the pinned [workflow](../../.github/workflows/gpu-opp-fixture.yml):

```sh
python3 -m py_compile tests/scripts/gpu-opp-fixture.py
python3 tests/scripts/gpu-opp-fixture.py --apply kernel docs/handoffs/gpu-2026-10-11.md
make -C kernel O=<temporary output> ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
make -C kernel O=<temporary output> ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j"$(nproc)" dtbs
python3 tests/scripts/gpu-opp-fixture.py --check <temporary output>/arch/arm64/boot/dts/qcom/sm8475-motorola-oneli.dtb
```

The proposal is appended **only to the runner's ephemeral copy** of `sm8475.dtsi`; no shared-DT commit was made. Actions completed all phases successfully.

Validated from the compiled DTB's `opp-hz` 64-bit cells and numeric `opp-level`:

| GPU MHz | RPMh numeric corner |
|---:|---:|
| 900 | 416 |
| 862 | 384 |
| 815 | 320 |
| 765 | 256 |
| 710 | 224 |
| 645 | 192 |
| 580 | 144 |
| 515 | 128 |
| 439 | 96 |
| 364 | 80 |
| 324 | 64 |
| 285 | 56 |
| 220 | 48 |

The check also verified exactly 13 entries, no old SM8450-only nodes, GPU `qcom,adreno-730.2` plus fallback and `qcom,sm8475-gpucc`. Job log explicitly printed `PASS: compiled DTB contains exactly 13 SM8475 GPU OPPs with expected RPMh corners`.

Artifacts: [`gpu-opp-fixture-38164310160-1`](https://github.com/Drzet/razr2022_nuc/actions/runs/38164310160/artifacts/11710889692), artifact ID `11710889692`, containing DTB, resolved `.config`, execution logs, proposal, fixture, tool versions and in-artifact `SHA256SUMS`. Reported upload ZIP digest SHA256: `4c992255217654cab5c32ebf0c5042642612ef2f8db1c0066047a251a0ddfcad`.

## Limitations and next action

- The successful DTB contains the review **fixture**, not a merged Boot implementation. Boot must apply the proposal and rerun build/schema checks on its own named commit.
- Mainline `opp-level` validation does not establish correct independent vendor CX votes, ACD, DDR bandwidth indices, thermal throttling or GMU firmware power behaviour.
- GPU device remains disabled in the actual pinned Boot board DT. No hardware exists for runtime validation.
- GPU kernel module build is a **separate** run; this record does not imply it succeeded.
