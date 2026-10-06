"""Review-gated replay of ONLY the first smoke builder request; no retry.

PREPARE is offline except for the local Docker check. EXECUTE makes at most
one model request, reserves at most CNY 0.10, and never runs generated code
or continues into a society. It cannot approve a full smoke run.
"""
import argparse
import getpass
import importlib.metadata
import json
import os
from pathlib import Path
import tempfile

from .sac_pilot import (ROOT, resolve, digest, read_json, write_json,
                        approval_template, verify_approval)
from .config import RunConfig
from .env_adapter import MechEnv
from .run import DEFAULT_ENV
from .society import Society
from .agentport_config import is_local_budget
from .failure_diagnostics import failure_diagnostics


def first_request(config):
    """Use the actual society prompt path; stop before any model or probe."""
    captured = {}

    class Captured(BaseException):
        pass

    class Capture:
        def complete(self, system, user, temperature, max_tokens):
            captured.update(system=system, user=user, temperature=temperature, max_tokens=max_tokens)
            raise Captured()

    cfg = RunConfig(arm='000', seed=1001, n_agents=config['n_agents'], n_rounds=config['n_rounds'],
                    k=config['k'], menu_size=config['menu_size'], model=config['model'],
                    temperature=config['temperature'], max_tokens_per_call=config['builder_max_tokens'],
                    separation_threshold=config['separation_threshold'],
                    alignment_window=config['alignment_window'], tool_timeout_s=config['tool_timeout_s'],
                    extra={'max_input_bytes': config['max_input_bytes'], 'stop_on_smoke_anomaly': True})
    with tempfile.TemporaryDirectory(prefix='boids_request_capture_') as tmp:
        try:
            Society(cfg, MechEnv(DEFAULT_ENV, config['dev_seed']), Capture(), tmp).run()
        except Captured:
            pass
    if not captured:
        raise RuntimeError('first builder request was not captured')
    return captured


def resolve_probe(config, out, run_id=None):
    if not is_local_budget(config):
        raise ValueError('one-request probe requires the local v2 smoke policy')
    r = resolve(config, out, run_id)
    r.update(execution_mode='one_builder_request_only', builder_calls=1, solver_calls=0,
             nominal_model_calls=1, first_request=first_request(config),
             study_status='api_compatibility_diagnostic_not_society_or_scientific_evidence')
    r['local_budget_policy'].update(max_reserved_cny=0.10, max_http_requests=1)
    r['local_budget_policy'].pop('full_schedule_reservation_cny')
    return r


def execute_probe(review, approval, out, allow_spend):
    # Use the common signature/owner checks, then this mode's own exact live
    # resolution. A full-smoke approval cannot authorize this separate run.
    verify_approval(review, approval, allow_spend)
    scope = review.get('run_scope') or {}
    if not scope.get('run_id') or scope.get('output_dir') != str(Path(out).resolve()):
        raise PermissionError('probe approval output scope differs')
    if resolve_probe(review['config'], out, scope['run_id']) != review:
        raise PermissionError('probe source/config/request changed; new review required')
    expected = {'scikit-learn': '1.5.2', 'openai': '1.51.0', 'httpx': '0.27.2',
                'numpy': '2.0.2', 'scipy': '1.13.1'}
    if {name: importlib.metadata.version(name) for name in expected} != expected:
        raise ValueError('install the pinned requirements before execution')
    from .mac_smoke import check
    from .sandbox import PROBE_REPORT
    from .local_budget import LocalSmokeBudget
    from .model import OpenAICompatModel
    from .prompts import parse_response
    c = review['config']
    os.environ['BOIDS_SANDBOX'] = 'docker'
    os.environ['BOIDS_DOCKER_IMAGE'] = c['sandbox_image_id']
    check()
    if PROBE_REPORT.get('probe', {}).get('image_id') != c['sandbox_image_id']:
        raise PermissionError('probe sandbox image differs from review')
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    claim = out.parent / ('.' + out.name + '.' + scope['run_id'] + '.consumed')
    with claim.open('x') as f:
        f.write(digest(review) + '\n')
    out.mkdir(exist_ok=False)
    budget = LocalSmokeBudget(c, out / 'request_ledger.jsonl', request_limit=1, reserved_cap_cny=0.10)
    write_json(out / 'reviewed_config.json', review)
    write_json(out / 'approval.json', {k: approval[k] for k in (
        'status', 'approved', 'reviewed_by', 'credential_owner', 'review_sha256')})
    model = None
    supplied = c['key_env'] not in os.environ
    try:
        if supplied:
            import sys
            if not sys.stdin.isatty():
                raise PermissionError('runtime key missing; no file or other credential fallback')
            os.environ[c['key_env']] = getpass.getpass('AgentPort key (hidden, not saved): ')
        model = OpenAICompatModel(c['model'], c['key_env'], True, base_url=c['base_url'],
                                  thinking=c['thinking'], max_attempts=1,
                                  accepted_response_models=c['accepted_response_models'],
                                  request_timeout_s=c['request_timeout_s'],
                                  before_request=budget.before, after_response=budget.after)
        write_json(out / 'request.json', review['first_request'])
        text, tin, tout = model.complete(**review['first_request'])
        write_json(out / 'response.json', {'content': text, 'tokens_in': tin, 'tokens_out': tout,
                                          'metadata': model.last_response_metadata})
        parsed = parse_response(text, MechEnv(DEFAULT_ENV, c['dev_seed']).primitives)
        budget.stop('diagnostic_complete')
        report = {'status': 'API_RESPONSE_RECEIVED_NOT_END_TO_END', 'budget': budget.receipt(),
                  'builder_parse_ok': parsed['parse_ok'], 'generated_code_executed': False,
                  'scientific_effect': 'unassessable', 'next_request_allowed': False}
        write_json(out / 'probe_summary.json', report)
        return report
    except (Exception, SystemExit, KeyboardInterrupt) as exc:
        budget.stop('run_failure')
        write_json(out / 'FAILED.json', {'status': 'FAILED_API_DIAGNOSTIC_NOT_SCORED',
                                       'error_type': type(exc).__name__,
                                       'diagnostic': failure_diagnostics(exc), 'budget': budget.receipt()})
        raise RuntimeError('one-request diagnostic stopped; inspect sanitized FAILED.json') from None
    finally:
        if supplied:
            os.environ.pop(c['key_env'], None)
        if model is not None:
            client = getattr(model, 'client', None)
            close = getattr(client, 'close', None)
            if callable(close):
                try:
                    close()
                except Exception:
                    # Do not mask the original result or emit raw SDK errors.
                    # This process never sends another request in either case.
                    write_json(out / 'CLIENT_CLOSE_FAILED.json', {'status': 'CLIENT_CLOSE_FAILED'})


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('prepare', 'execute'))
    p.add_argument('--config', default=str(ROOT / 'configs/agentport_flash_local_smoke.json'))
    p.add_argument('--out', required=True)
    p.add_argument('--run-out')
    p.add_argument('--review')
    p.add_argument('--approval')
    p.add_argument('--allow-spend', action='store_true')
    a = p.parse_args(argv)
    os.environ['BOIDS_SANDBOX'] = 'docker'
    if a.action == 'prepare':
        if not a.run_out or a.review or a.approval or a.allow_spend:
            p.error('prepare requires --run-out and forbids execute/approval flags')
        from .mac_smoke import check
        c = read_json(a.config)
        if c.get('sandbox_image_id'):
            os.environ['BOIDS_DOCKER_IMAGE'] = c['sandbox_image_id']
        receipt = check()
        if c.get('sandbox_image_id') and receipt['probe']['image_id'] != c['sandbox_image_id']:
            raise PermissionError('prepared Docker image differs from the supplied pin')
        c['sandbox_image_id'] = receipt['probe']['image_id']
        r = resolve_probe(c, a.run_out)
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=False)
        for name, value in (('resolved_config', r), ('approval.template', approval_template(r)),
                            ('sandbox_receipt', receipt)):
            write_json(out / (name + '.json'), value)
        print(json.dumps({'status': 'PREPARED_NOT_APPROVED', 'model_requests': 0,
                          'planned_requests': 1, 'local_cap_cny': 0.10, 'out': a.out}))
    else:
        if not a.review or not a.approval or a.run_out:
            p.error('execute requires --review and --approval; --run-out is forbidden')
        r = execute_probe(read_json(a.review), read_json(a.approval), a.out, a.allow_spend)
        print(json.dumps(r))


if __name__ == '__main__':
    main()
