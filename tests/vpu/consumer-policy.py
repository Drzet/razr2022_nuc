#!/usr/bin/env python3
"""Execute extracted production SM8475 consumer functions under host mocks.

No hardware, Linux PM concurrency, firmware or real provider execution is implied.
The accepted calculator/reference evidence is reused, not rerun here.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def function(code, name):
    masked = re.sub(r'/\*.*?\*/|//[^\n]*', lambda m: ''.join('\n' if c == '\n' else ' ' for c in m.group()), code, flags=re.S)
    match = re.search(r'\b' + re.escape(name) + r'\s*\([^;]*?\)\s*\{', masked, re.S)
    if not match:
        raise ValueError(name)
    start = code.rfind('\n', 0, match.start()) + 1
    if not masked[start:match.start()].strip():
        start = code.rfind('\n', 0, start - 1) + 1
    depth = 0
    for i in range(match.end() - 1, len(code)):
        depth += (masked[i] == '{') - (masked[i] == '}')
        if depth == 0:
            return code[start:i + 1]
    raise ValueError('unbalanced function: ' + name)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kernel-dir', type=Path, required=True)
    ap.add_argument('--json-out', type=Path, required=True)
    ap.add_argument('--framework', action='store_true')
    ap.add_argument('--kernel-ref', help='Read pinned kernel sources with git show')
    ap.add_argument('--case', default='all', help='Framework case or all')
    ap.add_argument('--expect-failure', action='store_true')
    args = ap.parse_args()
    sys.dont_write_bytecode = True
    root = args.kernel_dir.resolve()
    iris = root / 'drivers/media/platform/qcom/iris'
    sources = {}
    extracted = {}

    def read(name):
        sources[name] = (subprocess.check_output(['git', '-C', str(root), 'show', args.kernel_ref + ':drivers/media/platform/qcom/iris/' + name]) if args.kernel_ref else (iris / name).read_bytes())
        return sources[name].decode()

    def take(name, functions):
        code = read(name)
        result = []
        for func in functions.split():
            text = function(code, func)
            extracted[func] = hashlib.sha256(text.encode()).hexdigest()
            result.append(text)
        return '\n'.join(result)

    power_header = re.sub(r'^#include.*$', '', read('iris_power.h'), flags=re.M)
    # Actual enum values/fourcc constants and public packet layout, no magic casts.
    packet = read('iris_hfi_gen2_packet.h')
    packet_types = packet[packet.index('struct iris_hfi_header {'):packet.index('/**\n * struct iris_hfi_buffer')]
    defines = read('iris_hfi_gen2_defines.h')
    hfi = '\n'.join(line for line in defines.splitlines() if re.match(r'#define HFI_CMD_(BUFFER|START|STOP|CLOSE|RESUME)\s', line))
    hfi += '\n#define HFI_FW_FLAGS_SUCCESS ' + re.search(r'HFI_FW_FLAGS_SUCCESS\s*=\s*(0x[0-9a-fA-F]+)', defines).group(1)
    v4l2 = (root / 'include/uapi/linux/videodev2.h').read_text()
    formats = '\n'.join(line for line in v4l2.splitlines() if re.match(r'#define V4L2_PIX_FMT_(H264|HEVC|VP9|NV12|P010|QC08C|QC10C)\s', line))
    rpmh = (root / 'include/dt-bindings/power/qcom,rpmhpd.h').read_text()
    rpmh = '\n'.join(line for line in rpmh.splitlines() if line.startswith('#define RPMH_REGULATOR_LEVEL_'))
    resources = read('iris_resources.c')
    rows = resources[resources.index('static const struct {'):resources.index('static struct icc_bulk_data *iris_sm8475_path')]
    platform = read('iris_platform_common.h')
    depth_constants = '\n'.join(line for line in platform.splitlines()
                                  if re.match(r'#define (REGISTER_BIT_DEPTH|BIT_DEPTH_8|BIT_DEPTH_10)\b', line))
    buffer_header = read('iris_buffer.h')
    attrs = re.search(r'enum iris_buffer_attributes \{.*?\};', buffer_header, re.S).group()
    for name in ['iris_vpu2_bw.c', 'iris_vpu2_bw.h', 'iris_vpu2_bw_math.h']:
        read(name)
    setup = (HERE / 'consumer-policy-mocks.h').read_text()
    setup = setup.replace('/* PUBLIC_POWER_HEADER */', power_header)
    setup = setup.replace('/* SOURCE_CONSTANTS */', hfi + '\n' + formats + '\n' + rpmh + '\n' + packet_types + '\n' + depth_constants + '\n' + attrs)
    slices = [
        take('iris_resources.c', 'iris_get_clk_by_type iris_sm8475_path iris_sm8475_icc'),
        rows,
        take('iris_resources.c', 'iris_sm8475_check_opp iris_sm8475_select_opp iris_sm8475_clock_tree iris_sm8475_clock iris_sm8475_restore iris_sm8475_apply iris_sm8475_unvote iris_sm8475_config_vote'),
        take('iris_vpu2.c', 'iris_sm8475_frequency'),
        take('iris_power.c', 'iris_sm8475_policy iris_sm8475_workload iris_sm8475_configure iris_sm8475_adapt iris_sm8475_fault iris_sm8475_aggregate iris_sm8475_admit iris_sm8475_release iris_sm8475_suspend iris_sm8475_resume iris_sm8475_recover_idle'),
        take('iris_common.c', 'iris_vb2_buffer_to_driver iris_sm8475_close_session'),
        take('iris_power.c', 'iris_calc_bw iris_set_interconnects iris_vote_interconnects iris_set_clocks iris_scale_clocks iris_scale_power'),
        take('iris_common.c', 'iris_process_streamon_input iris_process_streamon_output iris_flush_deferred_buffers iris_kill_session iris_session_streamoff'),
        take('iris_vdec.c', 'iris_vdec_qbuf'),
        take('iris_buffer.c', 'iris_queue_deferred_buffers'),
        take('iris_hfi_queue.c', 'iris_sm8475_hfi_allowed'),
        take('iris_hfi_gen2_response.c', 'iris_sm8475_quarantined_response'),
        take('iris_vb2.c', 'iris_vb2_buf_queue'),
        take('iris_vidc.c', 'iris_policy_streamoff iris_policy_reqbufs'),
    ]
    if args.framework:
        import importlib.util
        spec = importlib.util.spec_from_file_location('cleanup_framework', HERE / 'cleanup-framework.py')
        extension = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(extension)
        setup, slices = extension.extend(root, args.kernel_ref, setup, slices, sources, extracted, read, take, function)
    with tempfile.TemporaryDirectory(prefix='vpu-consumer-test-') as directory:
        build = Path(directory)
        (build / 'linux').mkdir()
        for name, text in {
            'types.h': '#include <stdint.h>\n#include <stdbool.h>\ntypedef uint64_t u64; typedef uint32_t u32;\n',
            'errno.h': '#define EINVAL 22\n#define ERANGE 34\n#define ENOMEM 12\n#define ENODEV 19\n#define EIO 5\n#define EBUSY 16\n#define ETIMEDOUT 110\n',
            'limits.h': '#define U64_MAX UINT64_MAX\n',
            'math64.h': '',
            'overflow.h': '#define check_add_overflow(a,b,p) __builtin_add_overflow(a,b,p)\n#define check_mul_overflow(a,b,p) __builtin_mul_overflow(a,b,p)\n',
        }.items():
            (build / 'linux' / name).write_text(text)
        source = setup + '\n#include "iris_vpu2_bw.c"\n' + '\n'.join(slices)
        source += '\n' + (HERE / ('cleanup-framework-cases.c' if args.framework else 'consumer-policy-cases.c')).read_text()
        (build / 'consumer.c').write_text(source)
        cmd = ['gcc', '-std=gnu11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
               '-Wno-unused-function', '-Wno-unused-but-set-variable', '-Wno-sign-compare', '-fsanitize=undefined',
               '-fno-sanitize-recover=all', '-fno-omit-frame-pointer', '-I', str(build),
               '-I', str(iris), str(build / 'consumer.c'), '-o', str(build / 'consumer')]
        if args.framework:
            cmd.insert(8, '-Wno-unused-parameter')
        compile_run = subprocess.run(cmd, capture_output=True, text=True)
        if compile_run.returncode:
            # Keep only external temporary debug artifacts on failure.
            Path('/tmp/vpu-consumer-failed.c').write_text(source)
            raise RuntimeError(compile_run.stdout + compile_run.stderr)
        run = subprocess.run([str(build / 'consumer'), *([args.case] if args.framework else [])], capture_output=True, text=True)
        if run.returncode and not args.expect_failure:
            raise RuntimeError(run.stdout + run.stderr)
        if args.expect_failure:
            if run.returncode == 0:
                raise RuntimeError('Regression unexpectedly passed on the rejected candidate')
            predicates = {
                'failed-start': 'contexts[0].sq.owned_by_drv_count==2 && contexts[0].sq.streaming',
                'nonstreaming-cancel': 'iris_policy_streamoff(&files[0],NULL,10)==-EIO',
                'successful-close': 'q->inst->reservation.closed',
            }
            if predicates.get(args.case, '<no expected regression>') not in run.stdout + run.stderr:
                raise RuntimeError('Failed for a different reason: ' + run.stdout + run.stderr)
            output = {'expected_failure': True, 'returncode': run.returncode, 'diagnostic': run.stdout + run.stderr}
        else:
            output = json.loads(run.stdout)
        report = dict(assignment='432f2f84f6350f0c1b7670b751bf41fd349048ce',
                      kernel_revision=subprocess.check_output(['git', '-C', str(root), 'rev-parse', args.kernel_ref or 'HEAD'], text=True).strip(),
                      kernel_dirty=False if args.kernel_ref else bool(subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True)),
                      evidence='Host extraction with mocked providers; not kernel or hardware execution',
                      production_sources={k: hashlib.sha256(v).hexdigest() for k, v in sources.items()},
                      extracted_functions=extracted,
                      tests={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__), HERE / 'consumer-policy-mocks.h', HERE / 'consumer-policy-cases.c', *([HERE / 'cleanup-framework.py', HERE / 'cleanup-framework-mocks.h', HERE / 'cleanup-framework-cases.c'] if args.framework else [])]},
                      compiler=subprocess.check_output(['gcc', '--version'], text=True).splitlines()[0],
                      compile_command=[arg.replace(directory, '$BUILD') for arg in cmd],
                      result=output)
        args.json_out.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(output))


if __name__ == '__main__':
    main()
