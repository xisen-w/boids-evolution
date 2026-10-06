"""Same-Mac smoke entrypoint: check -> prepare -> explicit approved execute.

No automatic spend, no credential files, no .env fallback. The check command
executes only a hand-written identity tool, not a model or research experiment.
"""
import argparse
import getpass
import json
import os
from pathlib import Path
import tempfile

from .sac_pilot import ROOT, read_json, write_json, resolve, approval_template, execute, verify_approval
from .agentport_config import is_agentport


def check():
    from .sandbox import isolation_level, PROBE_REPORT, run_tool
    from .library import Library
    if isolation_level() != 'os-docker':
        raise RuntimeError('Docker isolation not verified; no model requests allowed')
    with tempfile.TemporaryDirectory(prefix='boids_mac_preflight_') as tmp:
        lib = Library(tmp)
        lib.add('a00_r01', 0, 1, 'identity fixture', 'offline check', None,
                'def execute(table, lookup):\n    return table\n')
        call = {'args': [[{'units': 1.0}], []], 'kwargs': {}}
        if run_tool(tmp, 'a00_r01', [call, call]) != [call['args'][0]] * 2:
            raise RuntimeError('Docker tool protocol check failed')
    return dict(PROBE_REPORT, external_model_requests=0)


def main(argv=None, *, campaign=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('check', 'prepare', 'execute'))
    p.add_argument('--config', default=str(ROOT / 'configs/agentport_flash_local_smoke.json'))
    p.add_argument('--out')
    p.add_argument('--run-out')
    p.add_argument('--review')
    p.add_argument('--approval')
    p.add_argument('--allow-spend', action='store_true')
    args = p.parse_args(argv)
    os.environ['BOIDS_SANDBOX'] = 'docker'
    if args.action == 'check':
        if args.allow_spend:
            p.error('check never accepts spend permission')
        print(json.dumps(check(), indent=2))
        return
    config = read_json(args.config)
    if not is_agentport(config):
        p.error('this entrypoint accepts only the AgentPort smoke contract')
    if args.action == 'prepare':
        if not args.out or not args.run_out or args.allow_spend or args.approval or args.review:
            p.error('prepare needs --out and --run-out; spending/approval flags are forbidden')
        if config.get('sandbox_image_id'):
            os.environ['BOIDS_DOCKER_IMAGE'] = config['sandbox_image_id']
        receipt = check()
        if config.get('sandbox_image_id') and receipt['probe']['image_id'] != config['sandbox_image_id']:
            raise PermissionError('prepared Docker image differs from the supplied pin')
        config['sandbox_image_id'] = receipt['probe']['image_id']
        resolved = resolve(config, args.run_out)
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=False)
        write_json(out / 'config.json', config)
        write_json(out / 'resolved_config.json', resolved)
        write_json(out / 'approval.template.json', approval_template(resolved))
        write_json(out / 'sandbox_receipt.json', receipt)
        print(json.dumps({'status': 'PREPARED_NOT_APPROVED', 'model_requests': 0,
                          'nominal_calls': resolved['nominal_model_calls'],
                          'spend_blockers': resolved['spend_blockers'], 'out': str(out)}, indent=2))
        return
    if not args.out or not args.review or not args.approval or args.run_out:
        p.error('execute needs --out, --review, --approval, --allow-spend; no --run-out')
    resolved, approval = read_json(args.review), read_json(args.approval)
    if config != resolved['config']:
        p.error('config differs from reviewed config')
    verify_approval(resolved, approval, args.allow_spend, args.out)
    # Check/pin the reviewed sandbox BEFORE prompting for a credential.
    os.environ['BOIDS_DOCKER_IMAGE'] = config['sandbox_image_id']
    check()
    # Hidden terminal input is optional; no key is ever accepted as a CLI arg.
    supplied = config['key_env'] not in os.environ
    try:
        if supplied:
            import sys
            if not sys.stdin.isatty():
                raise PermissionError('key absent: use an interactive hidden prompt or runtime environment')
            os.environ[config['key_env']] = getpass.getpass('AgentPort key (hidden, not saved): ')
        report = execute(resolved, approval, args.out, args.allow_spend, campaign=campaign)
        print(json.dumps({'status': report['status'], 'budget': report['budget'], 'out': args.out}))
    finally:
        if supplied:
            os.environ.pop(config['key_env'], None)


if __name__ == '__main__':
    main()
