"""No provider calls or real keys. Prices below are ARTIFICIAL test values."""
import copy
import json
import os
from pathlib import Path
import re
import tempfile
import types
import unittest
from unittest import mock

from boidsnet.runner.sac_pilot import (ROOT, Budget, resolve, read_json, approval_template,
                                     verify_approval, execute)
from boidsnet.runner.smoke_policy import SmokeStop, verdict_has_execution_error
from boidsnet.runner.config import RunConfig
from boidsnet.runner.society import Society
from boidsnet.runner.env_adapter import MechEnv
from boidsnet.runner.run import DEFAULT_ENV
from boidsnet.runner.model import OpenAICompatModel
from boidsnet.runner.agentport_config import AGENTPORT_FLASH_MODELS
from boidsnet.runner.utility import score_society
from tests.test_model import make

TEMPLATE = ROOT / 'configs/agentport_flash_smoke.json'
IDENT = 'def execute(table, lookup, **params):\n    return table\n'
BUILDER = 'TOOL_LABEL: identity\nTARGET: NONE\nIMPLEMENTS: NONE\nDESCRIPTION: identity fixture\n```python\n' + IDENT + '```'


def ready_config():
    c = read_json(TEMPLATE)
    c.update(input_cny_per_million=1.0, output_cny_per_million=1.0,
             pricing_confirmed=True, pricing_reference='OFFLINE FIXTURE, NOT A PROVIDER QUOTE',
             provider_spend_cap_cny=8, accepted_response_models=[c['model']],
             sandbox_image_id='sha256:' + '0' * 64)
    return c


class ConfigAndBudgetTests(unittest.TestCase):
    def test_template_never_authorizes_spend(self):
        r = resolve(read_json(TEMPLATE))
        self.assertEqual(r['nominal_model_calls'], 96)
        self.assertTrue(r['spend_blockers'])
        approval = approval_template(r) | dict(approved=True, status='APPROVED', reviewed_by='TEST_FIXTURE')
        with mock.patch('boidsnet.runner.model.OpenAICompatModel') as model, \
                mock.patch('boidsnet.runner.sandbox.isolation_level') as iso:
            with self.assertRaises(PermissionError):
                execute(r, approval, '/never-created', True)
            model.assert_not_called(); iso.assert_not_called()

    def test_unknown_prices_or_provider_cap_block(self):
        for key, bad in [('input_cny_per_million', None), ('output_cny_per_million', -1),
                         ('output_cny_per_million', float('nan')), ('pricing_confirmed', False),
                         ('provider_spend_cap_cny', None), ('provider_spend_cap_cny', 9),
                         ('accepted_response_models', [])]:
            c = ready_config(); c[key] = bad
            with self.subTest(key=key, bad=bad):
                self.assertTrue(resolve(c)['spend_blockers'])
                with tempfile.TemporaryDirectory() as tmp, self.assertRaises(PermissionError):
                    Budget(c, Path(tmp) / 'ledger')

    def test_no_route_retry_size_or_budget_expansion(self):
        for key, value in [('base_url', 'https://unapproved.invalid/v1'), ('max_http_requests', 97),
                           ('max_http_attempts_per_call', 2), ('max_reserved_cny', 9),
                           ('n_rounds', 4), ('n_agents', 8), ('request_timeout_s', 181)]:
            c = ready_config(); c[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                resolve(c)

    def test_gateway_model_ids_are_explicit_catalog_pins(self):
        for model in AGENTPORT_FLASH_MODELS:
            c = ready_config(); c['model'] = model
            self.assertFalse(resolve(c)['spend_blockers'])
        for model in ('deepseek-flash', 'deepseek-v4-flash', 'tier:cheap',
                      'openrouter:~deepseek/deepseek-flash-latest', 'azure:DeepSeek-V4-Pro'):
            c = ready_config(); c['model'] = model
            with self.subTest(model=model), self.assertRaises(ValueError):
                resolve(c)

    def test_exact_money_boundary_and_sticky_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = ready_config()
            b = Budget(c, Path(tmp) / 'ledger')
            # Exercise the low-level boundary after constructing a valid plan.
            b.config['max_reserved_cny'] = 0.000524
            b.before('s', 'u', 10, 0)  # (2 + 512 + 10) * 1 / 1e6, exactly
            self.assertEqual(b.reserved, 0.000524)
            b.after(3, 1, None, {})
            with self.assertRaises(PermissionError):
                b.before('s', 'u', 10, 0)
            b.config['max_reserved_cny'] = 8
            with self.assertRaises(PermissionError):
                b.before('s', 'u', 10, 0)
            self.assertEqual(b.requests, 1)
            self.assertEqual(b.receipt()['currency'], 'CNY')

    def test_unaffordable_schedule_blocked_before_first_request(self):
        c = ready_config(); c['output_cny_per_million'] = 1000
        self.assertIn('96-call worst-case reserve exceeds the client or provider cap', resolve(c)['spend_blockers'])

    def test_request_cap_counts_every_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = Budget(ready_config(), Path(tmp) / 'ledger')
            for _ in range(96):
                b.before('s', 'u', 10, 0)
                b.after(3, 1, None, {})
            with self.assertRaises(PermissionError):
                b.before('s', 'u', 10, 0)
            self.assertEqual(b.requests, 96)

    def test_currency_fields_preserve_legacy_usd_without_mislabeling_cny(self):
        from boidsnet.runner.sac_pilot import DEFAULT_CONFIG
        for c in (read_json(DEFAULT_CONFIG), ready_config()):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'ledger'
                b = Budget(c, path)
                b.before('s', 'u', 10, 0)
                self.assertEqual(b.receipt()['unreported_requests'], 1)
                b.after(3, 1, None, {})
                self.assertEqual(b.receipt()['unreported_requests'], 0)
                rows = [json.loads(line) for line in path.read_text().splitlines()]
                self.assertEqual('reserved_usd_cumulative' in rows[0], b.currency == 'USD')
                self.assertEqual('usage_cost_at_uncached_rate_usd' in rows[1], b.currency == 'USD')

    def test_approval_covers_price_and_image(self):
        r = resolve(ready_config())
        a = approval_template(r) | dict(approved=True, status='APPROVED', reviewed_by='TEST_FIXTURE')
        verify_approval(r, a, True)
        for key, value in [('input_cny_per_million', 2), ('sandbox_image_id', 'sha256:' + '1' * 64)]:
            changed = copy.deepcopy(r); changed['config'][key] = value
            with self.assertRaises(PermissionError):
                verify_approval(changed, a, True)


class ResponseContractTests(unittest.TestCase):
    def test_azure_and_native_thinking_wire_formats_are_distinct(self):
        from boidsnet.runner.agentport_config import thinking_request_body
        self.assertEqual(thinking_request_body('azure:DeepSeek-V4-Flash',
                         'https://agentport.world/v1', 'disabled'), {'reasoning_effort': 'none'})
        self.assertEqual(thinking_request_body('deepseek-flash', 'https://api.deepseek.com', 'disabled'),
                         {'thinking': {'type': 'disabled'}})
        r = resolve(ready_config())
        self.assertEqual(r['provider_request_body'], {'reasoning_effort': 'none'})

    def test_reasoning_aliases_tokens_and_inline_blocks_stop_after_accounting(self):
        variants = [({'reasoning': 'secret reasoning fixture'}, None),
                    ({'reasoning_details': [{'text': 'fixture'}]}, None),
                    ({'content': '<think>fixture</think>answer'}, None),
                    ({}, 3), ({}, -1), ({}, True), ({}, '0')]
        for message_change, tokens in variants:
            m = make([]); m.accepted_response_models = ['fixture']
            m.before_request, m.after_response = mock.Mock(), mock.Mock()
            message = {'content': 'answer'} | message_change
            m.client.chat.completions.create = mock.Mock(return_value=types.SimpleNamespace(
                usage=types.SimpleNamespace(prompt_tokens=3, completion_tokens=5,
                                            completion_tokens_details=types.SimpleNamespace(reasoning_tokens=tokens)),
                model='fixture', choices=[types.SimpleNamespace(finish_reason='stop',
                                                                message=types.SimpleNamespace(**message))]))
            with self.subTest(message=message_change, tokens=tokens), self.assertRaises(SmokeStop):
                m.complete('s', 'u', 0.7, 10)
            m.after_response.assert_called_once()
            with self.assertRaises(RuntimeError): m.complete('s', 'u', 0.7, 10)
            self.assertEqual(m.before_request.call_count, 1)

    def test_gateway_transport_requires_no_retry_and_explicit_models(self):
        with mock.patch('boidsnet.runner.sandbox.isolation_level', return_value='os-docker'), \
                mock.patch.dict(os.environ, {'BOIDS_PARTNER_API_KEY': 'OFFLINE_FAKE', 'BOIDS_SANDBOX': 'docker'}), \
                mock.patch('openai.OpenAI') as client:
            for model in AGENTPORT_FLASH_MODELS:
                m = OpenAICompatModel(model, 'BOIDS_PARTNER_API_KEY', True,
                    base_url='https://agentport.world/v1', thinking='disabled', max_attempts=1,
                    accepted_response_models=[model], request_timeout_s=90)
                self.assertFalse(client.call_args.kwargs['http_client'].follow_redirects)
                client.call_args.kwargs['http_client'].close()
                self.assertFalse(m.transport_policy()['follow_redirects'])
                self.assertEqual((m.MAX_ATTEMPTS, m.REQUEST_TIMEOUT_S), (1, 90))
            with self.assertRaises(ValueError):
                OpenAICompatModel('azure:DeepSeek-V4-Flash', 'BOIDS_PARTNER_API_KEY', True,
                    base_url='https://agentport.world/v1', thinking='disabled', max_attempts=2,
                    accepted_response_models=['DeepSeek-V4-Flash'])

    def test_gateway_pins_cannot_bypass_deepseek_guards(self):
        baseline = dict(model='azure:DeepSeek-V4-Flash', key_env='BOIDS_PARTNER_API_KEY',
                        allow_spend=True, base_url='https://agentport.world/v1',
                        thinking='disabled', max_attempts=1,
                        accepted_response_models=['DeepSeek-V4-Flash'])
        for change in ({'model': 'deepseek-flash'}, {'model': 'gpt-5.4-mini'},
                       {'thinking': None}, {'thinking': 'enabled'}, {'param_mode': 'auto'},
                       {'send_temperature': False}, {'token_param': 'max_completion_tokens'},
                       {'accepted_response_models': []}, {'max_attempts': 2},
                       {'azure_endpoint': 'https://unapproved.invalid'},
                       {'key_env': 'UNAPPROVED_KEY_ENV'}):
            with self.subTest(change=change), mock.patch('openai.OpenAI') as client, \
                    self.assertRaises((ValueError, PermissionError)):
                OpenAICompatModel(**(baseline | change))
            client.assert_not_called()

    def test_anomalies_account_then_stop_and_refuse_reuse(self):
        for finish, model, text, reasoning in [('length', 'deepseek-flash', 'x', None),
                ('stop', 'wrong-model', 'x', None), ('stop', 'deepseek-flash', '', None),
                ('stop', 'deepseek-flash', 'x', 'unexpected reasoning'),
                ('content_filter', 'deepseek-flash', 'x', None)]:
            m = make([]); m.accepted_response_models = ['deepseek-flash']
            m.before_request, m.after_response = mock.Mock(), mock.Mock()
            m.client.chat.completions.create = mock.Mock(return_value=types.SimpleNamespace(
                usage=types.SimpleNamespace(prompt_tokens=3, completion_tokens=1), model=model,
                choices=[types.SimpleNamespace(finish_reason=finish, message=types.SimpleNamespace(
                    content=text, reasoning_content=reasoning))]))
            with self.subTest(finish=finish, model=model), self.assertRaises(SmokeStop):
                m.complete('s', 'u', 0.7, 10)
            m.after_response.assert_called_once()
            with self.assertRaises(RuntimeError):
                m.complete('s', 'u', 0.7, 10)
            self.assertEqual(m.before_request.call_count, 1)


class StopSemanticsTests(unittest.TestCase):
    def society(self, tmp, model, env):
        return Society(RunConfig(arm='000', seed=1001, n_agents=4, n_rounds=3,
                                 extra={'stop_on_smoke_anomaly': True}), env, model, tmp)

    def test_bad_builder_is_recorded_without_regeneration_or_fake_tool(self):
        model = types.SimpleNamespace(complete=mock.Mock(return_value=('bad fixture', 3, 1)))
        with tempfile.TemporaryDirectory() as tmp:
            result = self.society(tmp, model, MechEnv(DEFAULT_ENV)).run()
            self.assertEqual(model.complete.call_count, 12)
            self.assertEqual(result['records'], 12)
            self.assertEqual(result['tools_built'], 0)
            self.assertEqual(result['model_parse_failures'], 12)
            self.assertEqual(result['harness_passed'], 0)

    def test_execution_error_stops_before_next_agent(self):
        for error in ('fixture failure', 'timeout', 'PermissionError: forbidden file'):
            model = types.SimpleNamespace(complete=mock.Mock(return_value=(BUILDER, 3, 1)))
            env = MechEnv(DEFAULT_ENV)
            with self.subTest(error=error), tempfile.TemporaryDirectory() as tmp, \
                    mock.patch.object(env, 'exec_feedback', return_value='raised ' + error):
                with self.assertRaisesRegex(SmokeStop, 'builder_public_execution_error'):
                    self.society(tmp, model, env).run()
                self.assertEqual(model.complete.call_count, 1)

    def test_wrong_answer_not_misclassified_as_execution_failure(self):
        self.assertFalse(verdict_has_execution_error({'passed': False, 'crashed': 0}))
        self.assertTrue(verdict_has_execution_error({'passed': False, 'crashed': 1}))

    def test_empty_library_stops_before_solver_request(self):
        from boidsnet.runner.library import Library
        model = types.SimpleNamespace(solve=mock.Mock(), complete=mock.Mock())
        with tempfile.TemporaryDirectory() as tmp:
            Library(str(Path(tmp) / 'library'))
            with self.assertRaisesRegex(SmokeStop, 'empty_frozen_library'):
                score_society(tmp, MechEnv(DEFAULT_ENV), model, split='dev', stop_on_smoke_anomaly=True)
            model.solve.assert_not_called(); model.complete.assert_not_called()

    def test_strict_stopping_cannot_change_confirmatory_scoring(self):
        with self.assertRaises(ValueError):
            score_society('never-created', None, None, split='test', stop_on_smoke_anomaly=True)

    def test_bad_solver_attempt_is_zero_without_dropping_other_attempts(self):
        from boidsnet.runner.library import Library
        good = '```python\nfrom tools import a00_r01\ndef execute(table, lookup, **params):\n    return a00_r01.execute(table, lookup)\n```'
        model = types.SimpleNamespace(solve=mock.Mock(side_effect=[('bad fixture', 3, 1), (good, 3, 1)]))
        with tempfile.TemporaryDirectory() as tmp:
            lib = Library(str(Path(tmp) / 'library'))
            entry = lib.add('a00_r01', 0, 1, 'fixture', 'identity', None, IDENT)
            entry.update(signature_signal=['fixture'] * 8, harness={'passed': False})
            lib.save()
            env = MechEnv(DEFAULT_ENV)
            task = env.dev_tasks()[0]['id']
            verdict = {'passed': True, 'crashed': 0, 'n_pass': 8, 'n_total': 8, 'details': []}
            with mock.patch.object(env, 'harness', return_value=verdict):
                result = score_society(tmp, env, model, split='dev', stop_on_smoke_anomaly=True,
                                       task_ids=[task], attempts=2)
            self.assertEqual(model.solve.call_count, 2)
            self.assertEqual(result['_dev_task_scores'], [0.5])
            self.assertEqual(result['gate_fail_rate'], 0.5)
            audit = json.loads((Path(tmp) / 'utility_dev/private_audit/task_000_attempt_0.json').read_text())
            self.assertFalse(audit['passed'])
            self.assertIsNone(audit['verdict'])

    def test_solver_python_mistakes_are_not_timeouts_or_infrastructure_errors(self):
        from boidsnet.runner.smoke_policy import ordinary_solver_code_error
        for text, expected in [("KeyError: 'col'", True), ('TypeError: bad call', True),
                               ('timeout', False), ('PermissionError: denied', False),
                               ('tool corrupted its result channel', False)]:
            v = {'passed': False, 'crashed': 1, 'details': ['seed 1: crash RuntimeError: ' + text]}
            self.assertEqual(ordinary_solver_code_error(v), expected)
        self.assertFalse(ordinary_solver_code_error({'crashed': 1, 'details': []}))

    def test_solver_error_scoring_and_infrastructure_stop_are_separate(self):
        from boidsnet.runner.library import Library
        from boidsnet.runner.sandbox import SandboxInfrastructureError
        good = '```python\nfrom tools import a00_r01\ndef execute(table, lookup, **params):\n    return a00_r01.execute(table, lookup)\n```'
        crash = {'passed': False, 'crashed': 8, 'n_pass': 0, 'n_total': 8,
                 'details': [f"seed {i}: crash RuntimeError: KeyError: 'col'" for i in range(8)]}
        passed = {'passed': True, 'crashed': 0, 'n_pass': 8, 'n_total': 8, 'details': []}
        for error in (crash, SandboxInfrastructureError('fixture infrastructure')):
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as tmp:
                lib = Library(str(Path(tmp) / 'library'))
                entry = lib.add('a00_r01', 0, 1, 'fixture', 'identity', None, IDENT)
                entry.update(signature_signal=['fixture'] * 8, harness={'passed': False})
                lib.save()
                model = types.SimpleNamespace(solve=mock.Mock(return_value=(good, 3, 1)))
                env = MechEnv(DEFAULT_ENV)
                with mock.patch.object(env, 'harness', side_effect=[error, passed]):
                    args = dict(split='dev', stop_on_smoke_anomaly=True,
                                task_ids=[env.dev_tasks()[0]['id']], attempts=2)
                    if isinstance(error, Exception):
                        with self.assertRaises(SandboxInfrastructureError):
                            score_society(tmp, env, model, **args)
                        self.assertEqual(model.solve.call_count, 1)
                    else:
                        result = score_society(tmp, env, model, **args)
                        self.assertEqual(model.solve.call_count, 2)
                        self.assertEqual(result['_dev_task_scores'], [0.5])
                        self.assertEqual(result['model_execution_failure_attempts'], 1)


class DockerCommandTests(unittest.TestCase):
    def test_flags_have_no_privilege_socket_network_or_writable_root(self):
        from boidsnet.runner.docker_sandbox import options
        args = options('boids-tool-offline-fixture')
        for required in ('--network=none', '--read-only', '--cap-drop=ALL',
                         '--security-opt=no-new-privileges', '--user=65534:65534',
                         '--pids-limit=64', '--memory=256m', '--cpus=1', '--pull=never'):
            self.assertIn(required, args)
        self.assertNotIn('--privileged', args)
        self.assertFalse(any('docker.sock' in a for a in args))

    def test_timeout_removes_only_its_own_container(self):
        import subprocess
        from boidsnet.runner import docker_sandbox as d
        calls = []
        def fixture(args, **kw):
            calls.append(args)
            if args[0] == 'run':
                raise subprocess.TimeoutExpired('OFFLINE_FIXTURE', 1)
            return types.SimpleNamespace(returncode=0, stderr='')
        with mock.patch.object(d, 'cli', side_effect=fixture):
            with self.assertRaises(subprocess.TimeoutExpired):
                d.invoke(['OFFLINE_IMAGE'], timeout=1)
        name = calls[0][calls[0].index('--name') + 1]
        self.assertEqual(calls[1], ['rm', '--force', name])
        self.assertRegex(name, '^boids-tool-[0-9a-f]{32}$')


class OfflineFixtureModel:
    """Exercises real build/freeze/score/accounting, but never instantiates an SDK."""
    def __init__(self, name, key_env, allow_spend, **kw):
        self.name, self.base_url, self.thinking = name, kw['base_url'], kw['thinking']
        self.send_temperature, self.token_param, self.param_mode = True, 'max_tokens', 'strict'
        self.before, self.after = kw['before_request'], kw['after_response']
        self.last_retries, self.last_cached_tokens = 0, None
        self.last_response_metadata = {'model': name, 'finish_reason': 'stop', 'response_id': 'OFFLINE_FIXTURE'}

    def sampling(self):
        return dict(temperature_sent=True, token_param='max_tokens', thinking=self.thinking, base_url=self.base_url)

    def transport_policy(self):
        return {'offline_fixture': True, 'external_requests': 0}

    def complete(self, system, user, temperature, max_tokens):
        self.before(system, user, max_tokens, 0)
        if 'composing tools from a fixed library' in system:
            tid = re.search(r'a\d{2}_r\d{2}', user).group()
            text = '```python\nfrom tools import ' + tid + '\ndef execute(table, lookup, **params):\n    return ' + tid + '.execute(table, lookup)\n```'
        else:
            text = BUILDER
        self.after(7, 10, None, self.last_response_metadata)
        return text, 7, 10


@unittest.skipUnless(os.environ.get('BOIDS_SANDBOX') == 'docker', 'explicit Docker offline validation only')
class DockerEndToEndTests(unittest.TestCase):
    def test_four_arm_build_freeze_score_and_ledger(self):
        from boidsnet.runner.sandbox import isolation_level, PROBE_REPORT
        self.assertEqual(isolation_level(), 'os-docker')
        c = ready_config(); c['sandbox_image_id'] = PROBE_REPORT['probe']['image_id']
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'OFFLINE_FIXTURE'
            r = resolve(c, out)
            a = approval_template(r) | dict(approved=True, status='APPROVED', reviewed_by='OFFLINE_TEST_FIXTURE')
            with mock.patch('boidsnet.runner.model.OpenAICompatModel', OfflineFixtureModel), \
                    mock.patch('openai.OpenAI', side_effect=AssertionError('no external SDK allowed')):
                report = execute(r, a, out, True)
            self.assertEqual(report['status'], 'COMPLETE_DEV_DIAGNOSTIC')
            self.assertEqual(report['http_requests'], 96)  # simulated calls, NOT HTTP
            self.assertEqual(report['budget']['reported_responses'], 96)
            self.assertEqual(len(report['results']), 4)
            for arm in report['results']:
                self.assertEqual(arm['build']['records'], 12)
                self.assertEqual(arm['solver']['solver_calls'], 12)
                self.assertEqual(arm['solver']['gate_fail_rate'], 0)
            self.assertFalse((out / 'FAILED.json').exists())
            rows = [json.loads(line) for line in (out / 'request_ledger.jsonl').read_text().splitlines()]
            self.assertEqual(len(rows), 192)
