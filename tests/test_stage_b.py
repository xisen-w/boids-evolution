"""Stage B config/capacity tests. No credentials or real SDK clients."""
import copy
from decimal import Decimal
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

from boidsnet.runner.agentport_config import worst_case_cost, validate
from boidsnet.runner.config import RunConfig, SAC_ARMS
from boidsnet.runner.env_adapter import MechEnv
from boidsnet.runner.local_budget import LocalSmokeBudget
from boidsnet.runner.prompts import SYSTEM
from boidsnet.runner.run import DEFAULT_ENV
from boidsnet.runner.sac_pilot import ROOT, resolve, read_json, verify_approval, approval_template
from boidsnet.runner.society import Society
from boidsnet.runner.utility import solver_prompt, SOLVER_SYSTEM


class Capture(Exception):
    pass


class CaptureModel:
    def complete(self, system, user, *args):
        self.system, self.user = system, user
        raise Capture()


class StageBTests(unittest.TestCase):
    def setUp(self):
        self.c = read_json(ROOT / 'configs/agentport_flash_stage_b.json')
        self.env = MechEnv(DEFAULT_ENV)

    def test_stage_prepare_no_model_and_correct_schedule(self):
        with mock.patch('openai.OpenAI', side_effect=AssertionError('no provider')):
            r = resolve(self.c)
        self.assertEqual((r['builder_calls'], r['solver_calls'], r['nominal_model_calls']), (384, 48, 432))
        self.assertEqual(r['arm_order'], ['011', '100', '111', '000'])
        self.assertEqual(r['local_budget_policy']['full_schedule_reservation_cny'], '59.513472')
        self.assertEqual(r['spend_blockers'], [])
        self.assertFalse(r['test_unsealed'])
        self.assertIn('mechanism_analysis', r)

    def test_budget_derived_from_calls_not_96(self):
        r = worst_case_cost(self.c)
        changed = dict(self.c, n_rounds=13, max_http_requests=464)
        self.assertGreater(worst_case_cost(changed), r)
        self.assertTrue(resolve(dict(self.c, max_reserved_cny=35))['spend_blockers'])

    def test_old_smoke_cannot_silently_scale(self):
        c = read_json(ROOT / 'configs/agentport_flash_local_smoke.json')
        for k, value in (('n_agents', 8), ('n_rounds', 12), ('max_input_bytes', 32768)):
            with self.assertRaises(ValueError):
                resolve(dict(c, **{k: value}))

    def test_stage_rejects_wrong_seed_order_retries_or_oversized_cap(self):
        for k, value in (('seeds', [1001]), ('arm_order', ['000', '111', '100', '011']),
                         ('max_http_attempts_per_call', 2), ('max_reserved_cny', 61),
                         ('max_reserved_cny', float('nan')), ('max_http_requests', 433)):
            with self.assertRaises(ValueError):
                resolve(dict(self.c, **{k: value}))

    def test_pending_or_stale_approval_cannot_construct_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'run'
            r = resolve(self.c, out)
            with self.assertRaises(PermissionError):
                verify_approval(r, approval_template(r), True, out)
            approved = dict(approval_template(r), approved=True, status='APPROVED', reviewed_by='FIXTURE_NOT_AUTHORIZATION')
            with mock.patch('boidsnet.runner.sac_pilot.code_hash', return_value='changed'):
                with self.assertRaises(PermissionError):
                    verify_approval(r, approved, True, out)

    def test_stage_budget_stops_before_excess(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = LocalSmokeBudget(self.c, Path(tmp) / 'ledger', request_limit=1)
            b.before('s', 'u', 4000, 0)
            b.after(1, 1, None, {'model': 'DeepSeek-V4-Flash', 'finish_reason': 'stop'})
            with self.assertRaises(PermissionError):
                b.before('s', 'u', 4000, 0)
            self.assertEqual(b.requests, 1)

    def history(self):
        return [dict(id=f'a{i % 8:02d}_r{i // 8 + 1:02d}', author=i % 8, round=i // 8 + 1,
                     label='unit conversion', description='Multiply a numeric column by a factor. ' * 12,
                     implements=['unit_convert'], target=None, harness=None, tci=1.0, static_imports=[])
                for i in range(96)]

    def test_all_arms_round12_fit_without_dropping_tools_or_tasks(self):
        source = 'def execute(table, lookup, **params):\n    return table\n'
        snapshot = self.history()[:88]
        for arm in SAC_ARMS:
            with self.subTest(arm=arm), tempfile.TemporaryDirectory() as tmp:
                model = CaptureModel()
                s = Society(RunConfig(arm=arm, seed=2001, n_agents=8, n_rounds=12,
                                      extra={'max_input_bytes': 32768}), self.env, model, tmp)
                s._source = lambda _: source
                try:
                    with self.assertRaises(Capture):
                        s._agent_turn(0, 12, snapshot)
                finally:
                    s.log.close()
                self.assertLessEqual(len((model.system + model.user).encode()), 32768)
                for e in snapshot:
                    self.assertIn('- ' + e['id'], model.user)
                self.assertEqual(model.user.count('TASK dev-'), 8)
                for name in ('S', 'A', 'C'):
                    self.assertIn('[' + name + ' evidence]', model.user)

    def test_solver_all96_interfaces_remain_after_compression(self):
        source = 'def execute(table, lookup, **params):\n    """' + 'Long documentation. ' * 100 + '"""\n    return table\n'
        task = self.env.dev_tasks()[0]['obj']
        prompt = solver_prompt(task, self.history(), lambda _: source, max_input_bytes=32768)
        self.assertLessEqual(len((SOLVER_SYSTEM + prompt).encode()), 32768)
        for e in self.history():
            self.assertIn('--- ' + e['id'], prompt)
            self.assertIn(e['id'] + '.execute(table, lookup, col=<col>, factor=<factor>)', prompt)
        self.assertIn(task.spec, prompt)
        self.assertEqual(prompt.count('execute(table, lookup, **params)'), 97)  # 96 signatures + format
        with self.assertRaises(ValueError):
            solver_prompt(task, self.history(), lambda _: source, max_input_bytes=1000)

    def test_execution_uses_reviewed_seed_order_sizes_and_analysis(self):
        from boidsnet.runner.sac_pilot import execute
        from tests.test_agentport_smoke import OfflineFixtureModel
        observed = []
        class FakeSociety:
            def __init__(self, cfg, env, model, out):
                self.cfg, self.model = cfg, model
                observed.append((cfg.arm, cfg.seed, cfg.n_agents, cfg.n_rounds, Path(out).name))
            def run(self):
                for _ in range(self.cfg.n_agents * self.cfg.n_rounds):
                    self.model.complete('fixture', 'fixture', 0.7, 4000)
                return {'truncated': False, 'records': self.cfg.n_agents * self.cfg.n_rounds}
        def fake_score(soc, env, model, **kwargs):
            self.assertEqual(kwargs['max_input_bytes'], 32768)
            for _ in range(12):
                model.complete('fixture', 'fixture', 0.7, 1500)
            return {'_dev_task_scores': [0.0] * 6}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'run'
            resolved = resolve(self.c, out)
            approval = dict(approval_template(resolved), approved=True, status='APPROVED', reviewed_by='OFFLINE_FIXTURE_NOT_AUTHORIZATION')
            with mock.patch('boidsnet.runner.sandbox.isolation_level', return_value='os-docker'), \
                 mock.patch.dict('boidsnet.runner.sandbox.PROBE_REPORT', {'probe': {'image_id': self.c['sandbox_image_id']}}), \
                 mock.patch('boidsnet.runner.model.OpenAICompatModel', OfflineFixtureModel), \
                 mock.patch('openai.OpenAI', side_effect=AssertionError('NO_PROVIDER')), \
                 mock.patch('boidsnet.runner.society.Society', FakeSociety), \
                 mock.patch('boidsnet.runner.utility.score_society', side_effect=fake_score), \
                 mock.patch('boidsnet.runner.analysis.analyze_society', return_value={'summary': {'fixture': True}}) as analyzed, \
                 mock.patch('boidsnet.runner.analysis.aggregate_analyses', return_value={'fixture': True}):
                report = execute(resolved, approval, out, True)
            self.assertEqual(report['http_requests'], 432)  # simulated, NO HTTP
            self.assertEqual(analyzed.call_count, 4)
            self.assertTrue(all(call.kwargs['stop_on_smoke_anomaly'] for call in analyzed.call_args_list))
            self.assertEqual([r[0] for r in observed], self.c['arm_order'])
            self.assertTrue(all(r[1:4] == (2001, 8, 12) and r[4].endswith('_s2001') for r in observed))

    def test_analysis_anomaly_stops_before_next_arm_and_is_not_complete(self):
        from boidsnet.runner.sac_pilot import execute
        from boidsnet.runner.smoke_policy import SmokeStop
        from tests.test_agentport_smoke import OfflineFixtureModel
        c = read_json(ROOT / 'configs/agentport_flash_local_smoke.json')
        c['sandbox_image_id'] = self.c['sandbox_image_id']
        class FakeSociety:
            def __init__(self, cfg, env, model, out):
                self.model = model
            def run(self):
                for _ in range(12):
                    self.model.complete('fixture', 'fixture', 0.7, 4000)
                return {'truncated': False, 'records': 12}
        def fake_score(soc, env, model, **kwargs):
            for _ in range(12):
                model.complete('fixture', 'fixture', 0.7, 1500)
            return {'_dev_task_scores': [0.0] * 6}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'run'
            resolved = resolve(c, out)
            approval = dict(approval_template(resolved), approved=True, status='APPROVED', reviewed_by='OFFLINE_FIXTURE_NOT_AUTHORIZATION')
            with mock.patch('boidsnet.runner.sandbox.isolation_level', return_value='os-docker'), \
                 mock.patch.dict('boidsnet.runner.sandbox.PROBE_REPORT', {'probe': {'image_id': c['sandbox_image_id']}}), \
                 mock.patch('boidsnet.runner.model.OpenAICompatModel', OfflineFixtureModel), \
                 mock.patch('openai.OpenAI', side_effect=AssertionError('NO_PROVIDER')), \
                 mock.patch('boidsnet.runner.society.Society', FakeSociety), \
                 mock.patch('boidsnet.runner.utility.score_society', side_effect=fake_score), \
                 mock.patch('boidsnet.runner.analysis.analyze_society', side_effect=SmokeStop('analysis_probe_execution_error')):
                with self.assertRaisesRegex(RuntimeError, 'pilot stopped'):
                    execute(resolved, approval, out, True)
            failed = read_json(out / 'FAILED.json')
            self.assertEqual(failed['http_requests'], 24)  # local fixture, not actual requests
            self.assertEqual(failed['completed_arms'], [])
            self.assertTrue(failed['budget']['circuit_open'])
            self.assertEqual(failed['stop_reason'], 'analysis_probe_execution_error')
            self.assertEqual(len(list(out.glob('ENG_*'))), 1)
            self.assertFalse((out / 'pilot_summary.json').exists())


if __name__ == '__main__':
    unittest.main()
