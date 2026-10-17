#!/usr/bin/env python3
"""Validate maintained USB workflow wiring and execute its real push selector.

Run with the existing dtschema environment (ruamel.yaml dependency). This
executes automation in temporary Git fixtures, never kernel compilation.
"""
import argparse
import ast
import fnmatch
import json
import os
from pathlib import Path
import subprocess
import tempfile

from ruamel.yaml import YAML


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ps5169', type=Path)
    parser.add_argument('legacy', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    yaml = YAML(typ='safe')
    wfpath = '.github/workflows/razr-ps5169-fault-ci.yml'
    workflow = yaml.load((args.ps5169 / wfpath).read_text())
    jobs = workflow['jobs']
    checks = jobs['checks']
    build = jobs['arm64-and-binding']
    assert build['needs'] == 'checks'
    assert build['if'] == "needs.checks.outputs.build == 'true'"
    assert 'always()' not in build['if']
    assert 'steps.changes.outputs.build' in checks['outputs']['build']
    assert workflow['on']['push']['branches'] == ['razr/usb-ps5169']
    assert 'workflow_dispatch' in workflow['on']
    assert workflow['permissions'] == {'contents': 'read'}
    assert workflow['concurrency'] == {
        'group': '${{ github.workflow }}-${{ github.ref }}', 'cancel-in-progress': True}
    commands = '\n'.join(s.get('run', '') for s in checks['steps'])
    assert "'dtschema==2026.6'" in commands
    assert 'dt_binding_check' in commands
    assert commands.count('python3 scripts/razr/ps5169-fault-injection.py') == 1
    assert commands.count('python scripts/razr/ps5169-conditional-validation.py') == 1
    assert 'python3 scripts/razr/ps5169-probe-fault-injection.py' not in commands
    build_commands = '\n'.join(s.get('run', '') for s in build['steps'])
    assert 'Image modules' in build_commands
    assert 'test -s Module.symvers' in build_commands
    assert 'ps5169.ko' in build_commands and 'readelf' in build_commands
    assert 'resolved-arm64.config' in build_commands
    assert 'dt_binding_check' not in build_commands
    assert all(j['timeout-minutes'] > 0 for j in jobs.values())
    for root in (args.ps5169, args.legacy):
        assert not (root / '.github/workflows/razr-ps5169-candidate.yml').exists()
        schema = yaml.load((root / '.github/workflows/razr-usb-schema.yml').read_text())
        assert schema['concurrency'] == workflow['concurrency']
        assert schema['permissions'] == {'contents': 'read'}
        assert {'razr/usb', 'razr/usb-ps5169'} <= set(schema['on']['push']['branches'])
        assert 'pull_request' in schema['on'] and 'workflow_dispatch' in schema['on']
        assert 'dtschema==2026.6' in str(schema)
    assert not (args.ps5169 / '.github/workflows/razr-ps5169-durable.yml').exists()
    assert not (args.ps5169 / '.github/workflows/razr-ps5169-conditional-schema.yml').exists()

    # Extract the actual workflow step, rather than a copy of its selector.
    step = next(s for s in checks['steps'] if s.get('id') == 'changes')
    run = step['run']
    bash_syntax = subprocess.run(['bash', '-n'], input=run, text=True, capture_output=True)
    assert bash_syntax.returncode == 0, bash_syntax.stderr
    for job in jobs.values():
        for s in job['steps']:
            if 'run' in s:
                subprocess.run(['bash', '-n'], input=s['run'], text=True, check=True)
    code = run.split("python3 - <<'PY'\n", 1)[1].rsplit('\nPY', 1)[0]
    patterns = next(ast.literal_eval(node.value) for node in ast.walk(ast.parse(code))
                    if isinstance(node, ast.Assign) and any(
                        isinstance(t, ast.Name) and t.id == 'patterns' for t in node.targets))
    results = []
    with tempfile.TemporaryDirectory(prefix='usb-ci-selector-') as tmp:
        root = Path(tmp)
        git(root, 'init', '-q')
        git(root, 'config', 'user.name', 'CI selector fixture')
        git(root, 'config', 'user.email', 'fixture@example.invalid')
        driver = 'drivers/usb/typec/mux/ps5169.c'
        fixture = root / driver
        fixture.parent.mkdir(parents=True)
        fixture.write_text('synthetic baseline\n')
        git(root, 'add', '.')
        git(root, 'commit', '-qm', 'baseline')
        baseline = git(root, 'rev-parse', 'HEAD')

        def commit(path, text='synthetic change\n'):
            p = root / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
            git(root, 'add', '--', path)
            git(root, 'commit', '-qm', 'fixture change')
            return git(root, 'rev-parse', 'HEAD')

        def verify(name, before, head, expected, event='push', cwd=None):
            target = cwd or root
            output = target / 'outputs'
            output.write_text('')
            env = {**os.environ, 'EVENT_NAME': event, 'BEFORE_SHA': before,
                   'GITHUB_SHA': head, 'GITHUB_OUTPUT': str(output)}
            r = subprocess.run(['bash', '-euo', 'pipefail', '-c', run], cwd=target,
                               env=env, text=True, capture_output=True)
            assert r.returncode == 0, (name, r.stderr)
            value = output.read_text().strip()
            assert value == 'build=' + str(expected).lower(), (name, value, r.stdout)
            results.append({'case': name, 'build': expected})

        cheap = [wfpath, 'docs/usb.md',
                 'Documentation/devicetree/bindings/usb/parade,ps5169.yaml',
                 'tests/usb/ps5169/oneli-valid.dts',
                 'scripts/razr/ps5169-fault-injection.py',
                 'scripts/razr/ps5169-probe-fault-injection.py',
                 'scripts/razr/ps5169-conditional-validation.py']
        for path in cheap:
            triggered = any(fnmatch.fnmatchcase(path, p) for p in workflow['on']['push']['paths'])
            assert triggered == (not path.startswith('docs/'))
            before = git(root, 'rev-parse', 'HEAD')
            head = commit(path)
            verify(path, before, head, False)
        sources = [driver, 'drivers/usb/typec/mux/Kconfig',
                   'drivers/usb/typec/mux/Makefile', 'include/linux/usb/typec_mux.h',
                   'include/linux/regulator/consumer.h', 'include/linux/gpio/consumer.h',
                   'include/linux/regmap.h', 'include/drm/bridge/aux-bridge.h',
                   'arch/arm64/configs/defconfig']
        for path in sources:
            assert any(fnmatch.fnmatchcase(path, p) for p in workflow['on']['push']['paths'])
            assert any(fnmatch.fnmatchcase(path, p) for p in patterns)
            before = git(root, 'rev-parse', 'HEAD')
            head = commit(path)
            verify(path, before, head, True)
        before = git(root, 'rev-parse', 'HEAD')
        commit(driver, 'first commit changes source\n')
        head = commit(wfpath, 'second commit changes workflow\n')
        verify('multi-commit push', before, head, True)
        verify('new branch', '0' * 40, head, True)
        verify('missing before', '', head, True)
        verify('invalid before', '--bad-option', head, True)
        verify('unavailable before (fetch failure)', '1' * 40, head, True)
        verify('explicit dispatch', before, head, True, 'workflow_dispatch')
        before = git(root, 'rev-parse', 'HEAD')
        git(root, 'mv', driver, 'renamed-source.c')
        git(root, 'commit', '-qm', 'rename source')
        verify('rename source', before, git(root, 'rev-parse', 'HEAD'), True)
        verify('empty effective diff', baseline, baseline, False)
        shallow = root / 'shallow'
        subprocess.run(['git', 'clone', '-q', '--depth=2', root.as_uri(), str(shallow)], check=True)
        verify('shallow clone fetches older push base', baseline,
               git(root, 'rev-parse', 'HEAD'), True, cwd=shallow)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'result': 'PASS', 'selector_cases': results,
        'scope': 'real workflow step with local Git fixtures; workflow graph/assertion checks; no Actions scheduler or kernel build'}, indent=2) + '\n')
    print(f'PASS: workflow wiring, bash syntax and {len(results)} real Git selector cases')


if __name__ == '__main__':
    main()
