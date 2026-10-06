"""Offline task-contract regressions. All generated responses here are fixtures."""
import json
import os
from pathlib import Path
import random
import tempfile
import unittest
from unittest import mock

from boidsnet.runner import analysis
from boidsnet.runner.agentport_config import target_contract
from boidsnet.runner.config import RunConfig, SAC_ARMS
from boidsnet.runner.env_adapter import MechEnv
from boidsnet.runner.gateway_probe import resolve_probe
from boidsnet.runner.library import Library
from boidsnet.runner.prompts import parse_response, PARAM_SYSTEM
from boidsnet.runner.run import DEFAULT_ENV
from boidsnet.runner.sac_pilot import ROOT, resolve, read_json, approval_template, verify_approval
from boidsnet.runner.sandbox import SandboxedTool
from boidsnet.runner.society import Society
from boidsnet.runner.target_contract import VERSION, LEGACY, kwargs_for, parse_params
from boidsnet.runner.utility import freeze_library, score_society, solver_prompt, SOLVER_SYSTEM
from tests import test_stage_b
from tests.test_parametric_smoke import SOURCE


def response(target='dev-example', params='{"col":"price_cents","factor":0.01}', source=SOURCE, implements='unit_convert'):
    return (f'TOOL_LABEL: unit conversion\nTARGET: {target}\nTARGET_PARAMS: {params}\n'
            f'IMPLEMENTS: {implements}\nDESCRIPTION: Convert a numeric column by a factor.\n```python\n{source}```')


def contract(entry, params=None):
    entry.update(target_contract_version=VERSION, target_contract_error=None,
                 target_params={'col': 'price_cents', 'factor': 0.01} if params is None else params)
    return entry


class TargetContractTests(unittest.TestCase):
    def test_valid_json_and_legacy_not_reinterpreted(self):
        parsed = parse_response(response(), ['unit_convert'], target_contract=VERSION)
        self.assertEqual(kwargs_for(parsed), {'col': 'price_cents', 'factor': .01})
        old = parse_response(response(), ['unit_convert'])
        self.assertNotIn('target_params', old)
        self.assertEqual(kwargs_for(old), {})
        self.assertIsNone(kwargs_for({'target': None}))
        self.assertIsNone(kwargs_for({'target': 'dev-x', 'target_params': {'col': 'x'}}))

    def test_bad_json_is_not_eval_and_not_silently_empty_kwargs(self):
        for raw in ('[]', 'null', '{"x":NaN}', '{"x":Infinity}', '{"x":1e999}',
                    '{"x":1,"x":2}', '{"x":{"a":1,"a":2}}', '{"table":[]}',
                    '{"lookup":[]}', '__import__("os")', ''):
            with self.subTest(raw=raw):
                p = parse_response(response(params=raw), target_contract=VERSION)
                self.assertTrue(p['parse_ok'])  # still a tool; target claim invalid
                self.assertIsNotNone(p['target_contract_error'])
                self.assertIsNone(kwargs_for(p))

    def test_missing_duplicate_or_embedded_metadata_rejected(self):
        candidates = [response().replace('TARGET_PARAMS: {"col":"price_cents","factor":0.01}\n', ''),
                      response().replace('TARGET_PARAMS:', 'TARGET_PARAMS: {}\nTARGET_PARAMS:'),
                      response().replace('TARGET:', 'TARGET: NONE\nTARGET:'),
                      response().replace('TARGET: dev-example\n', ''),
                      response().replace('TARGET: dev-example', 'TARGET:')]
        for text in candidates:
            self.assertIsNone(kwargs_for(parse_response(text, target_contract=VERSION)))
        hidden = response().replace('TARGET: dev-example\n', '').replace('    col,', '    # TARGET: dev-example\n    col,')
        self.assertIsNone(kwargs_for(parse_response(hidden, target_contract=VERSION)))

    def test_none_does_not_force_target_or_collaboration(self):
        p = parse_response(response('NONE', '{}'), target_contract=VERSION)
        self.assertIsNone(p['target_contract_error'])
        self.assertIsNone(kwargs_for(p))
        self.assertIsNotNone(parse_response(response('NONE'), target_contract=VERSION)['target_contract_error'])
        self.assertIn('Reuse is permitted but not required', PARAM_SYSTEM)

    def test_crlf_header_is_valid_and_none_still_requires_params_field(self):
        p = parse_response(response().replace('\n', '\r\n'), target_contract=VERSION)
        self.assertIsNone(p['target_contract_error'])
        self.assertEqual(kwargs_for(p), {'col': 'price_cents', 'factor': .01})
        missing = response('NONE', '{}').replace('TARGET_PARAMS: {}\n', '')
        self.assertEqual(parse_response(missing, target_contract=VERSION)['target_contract_error'],
                         'missing_or_duplicate_target_params')

    def test_params_copied_no_shared_mutation(self):
        e = contract({'target': 'dev-x'}, {'options': [1, 2]})
        kwargs_for(e)['options'].append(3)
        self.assertEqual(e['target_params'], {'options': [1, 2]})

    def test_new_configs_are_explicit_unapproved_and_same_budget(self):
        for filename, calls, reserve in [('agentport_flash_contract_smoke.json', 96, '7.2900864'),
                                         ('agentport_flash_stage_b_v2.json', 432, '59.513472')]:
            c = read_json(ROOT / 'configs' / filename)
            with mock.patch('openai.OpenAI', side_effect=AssertionError('NO_PROVIDER')):
                r = resolve(c)
            self.assertEqual(r['target_contract'], VERSION)
            self.assertEqual(r['nominal_model_calls'], calls)
            self.assertEqual(r['local_budget_policy']['full_schedule_reservation_cny'], reserve)
            self.assertFalse(r['test_unsealed'])
            self.assertFalse(approval_template(r)['approved'])
            with self.assertRaises(PermissionError):
                verify_approval(r, approval_template(r), True)
        self.assertEqual(target_contract(read_json(ROOT / 'configs/agentport_flash_stage_b.json')), LEGACY)

    def test_gateway_one_request_cannot_silently_be_stage_b(self):
        for filename in ('agentport_flash_stage_b.json', 'agentport_flash_stage_b_v2.json'):
            with self.assertRaisesRegex(ValueError, 'not a stage B'):
                resolve_probe(read_json(ROOT / 'configs' / filename), '/unused')
        c = read_json(ROOT / 'configs/agentport_flash_contract_smoke.json')
        r = resolve_probe(c, '/unused')
        self.assertEqual(r['first_request']['system'], PARAM_SYSTEM)

    def test_small_pilot_cli_no_implicit_execute_or_key(self):
        from boidsnet.runner.small_pilot import main
        with mock.patch('boidsnet.runner.small_pilot.mac_main') as inner:
            main([])
            self.assertIn('--help', inner.call_args[0][0])
            main(['prepare', '--out', 'review/x', '--run-out', 'runs/x'])
            args = inner.call_args[0][0]
            self.assertEqual(args[0], 'prepare')
            self.assertTrue(args[-1].endswith('agentport_flash_stage_b_v2.json'))
            self.assertNotIn('--allow-spend', args)

    def test_menu_boundary_and_contract_recorded_before_execution(self):
        env = MechEnv(DEFAULT_ENV)
        class Model:
            def complete(self, *args):
                return response('test-not-allowed'), 1, 1
        with tempfile.TemporaryDirectory() as tmp:
            soc = Society(RunConfig(arm='000', seed=1001, n_agents=4, n_rounds=3,
                                   extra={'target_contract': VERSION}), env, Model(), tmp)
            try:
                rec, entry = soc._agent_turn(0, 1, [])
                self.assertEqual(rec['target_contract_error'], 'target_not_in_shown_dev_menu')
                self.assertIsNone(kwargs_for(entry))
            finally:
                soc.log.close()

    def test_invalid_contract_logged_even_without_parsed_code(self):
        class Model:
            def complete(self, *args):
                return 'TARGET: NONE\nTARGET_PARAMS: NaN\nNo Python block.', 1, 1
        with tempfile.TemporaryDirectory() as tmp:
            soc = Society(RunConfig(arm='000', seed=1001, n_agents=4, n_rounds=3,
                                   extra={'target_contract': VERSION}), MechEnv(DEFAULT_ENV), Model(), tmp)
            try:
                rec, entry = soc._agent_turn(0, 1, [])
                self.assertIsNone(entry)
                self.assertTrue(rec['model_parse_failure'])
                self.assertEqual(rec['target_contract_error'], 'invalid_target_params')
                self.assertEqual(rec['target_contract_version'], VERSION)
            finally:
                soc.log.close()

    def test_protocol_mismatch_rejected_before_tool_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'society'
            lib = Library(str(root / 'library'))
            lib.add('a00_r01', 0, 1, 'legacy fixture', 'fixture', None, SOURCE)
            analysis.write(root / 'run_manifest.json', {'extra': {'target_contract': VERSION}})
            with mock.patch('boidsnet.runner.analysis_worker.execute', side_effect=AssertionError('NO_EXECUTION')):
                with self.assertRaisesRegex(ValueError, 'target contract differs'):
                    analysis.analyze_society(root, Path(tmp) / 'out', require_os=False)
            self.assertFalse((Path(tmp) / 'out').exists())

    def test_readiness_preserves_unknown_and_never_authorizes_repeat(self):
        from boidsnet.runner.pilot_readiness import summarize
        s = {'mechanism_delivery': {'declared_target_passes': 0, 'A_nonfallback_opportunities': 0,
                                    'S_opportunities': 0, 'invalid_target_contracts': 2},
             'M_cross': {'unknown_tools': 3, 'lower_bound': 0, 'upper_bound': 1},
             'depth_utility': {'pooled_U_dev': 0}, 'dependency_edges': []}
        result = summarize({'results': [{'arm': '111', 'mechanism_analysis': s}, {'arm': '000'}]})
        warnings = result['arms'][0]['warnings']
        for flag in ('utility_floor', 'no_passing_declared_targets', 'alignment_only_fallback_or_no_evidence',
                     'no_separation_opportunity', 'M_cross_partially_identified', 'invalid_declared_target_contracts'):
            self.assertIn(flag, warnings)
        self.assertEqual(result['arms'][0]['M_cross'], s['M_cross'])
        self.assertEqual(result['arms'][1]['warnings'], ['measurement_summary_missing'])
        self.assertFalse(result['paper_ready'])
        self.assertFalse(result['automatic_next_run'])

    def test_solver_96_declared_interfaces_fit_reviewed_input_cap(self):
        env = MechEnv(DEFAULT_ENV)
        history = test_stage_b.StageBTests().history()
        target = env.dev_tasks()[0]
        for e in history:
            contract(e)
            e['target'] = target['id']
        prompt = solver_prompt(target['obj'], history, lambda _: SOURCE, max_input_bytes=32768)
        self.assertLessEqual(len((SOLVER_SYSTEM + prompt).encode()), 32768)
        for e in history:
            self.assertIn('--- ' + e['id'], prompt)
        self.assertEqual(prompt.count('Declared DEV target invocation'), 96)

    def test_new_contract_capacity_all_arms_full_horizon(self):
        from tests.test_stage_b import StageBTests, Capture, CaptureModel
        env = MechEnv(DEFAULT_ENV)
        snapshot = StageBTests().history()[:88]
        for e in snapshot:
            contract(e, {})
        for arm in SAC_ARMS:
            with tempfile.TemporaryDirectory() as tmp:
                model = CaptureModel()
                soc = Society(RunConfig(arm=arm, seed=2001, n_agents=8, n_rounds=12,
                                        extra={'target_contract': VERSION, 'max_input_bytes': 32768}), env, model, tmp)
                soc._source = lambda _: SOURCE
                try:
                    with self.assertRaises(Capture):
                        soc._agent_turn(0, 12, snapshot)
                    self.assertLessEqual(len((model.system + model.user).encode()), 32768)
                    self.assertEqual(model.system, PARAM_SYSTEM)
                    for e in snapshot:
                        self.assertIn('- ' + e['id'], model.user)
                finally:
                    soc.log.close()

    def test_parameterized_targets_not_collapsed_by_noargs_identity(self):
        # Artificial oracle isolates freezing's choice of comparison condition.
        env = mock.Mock()
        env.verify_primitive.return_value = {'passed': True}
        for target in ('dev-x', None):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                lib = Library(str(root / 'library'))
                for i, primitive in enumerate(('unit_convert', 'normalize_str')):
                    e = lib.add(f'a0{i}_r01', i, 1, 'fixture', 'fixture', target, SOURCE, [primitive])
                    contract(e, {} if target is None else None)
                    e['signature_signal'] = ['same_noargs_identity'] * 8
                lib.save()
                kept, _, _ = freeze_library(tmp, str(root / 'frozen'), env)
                self.assertEqual(len(kept), 2)

    def test_432_request_v2_budget_gate_without_network(self):
        from boidsnet.runner.local_budget import LocalSmokeBudget
        c = read_json(ROOT / 'configs/agentport_flash_stage_b_v2.json')
        with tempfile.TemporaryDirectory() as tmp:
            b = LocalSmokeBudget(c, Path(tmp) / 'ledger')
            for cap in [4000] * 384 + [1500] * 48:
                b.before('', 'x' * 32768, cap, 0)
                b.after(1, 1, None, {'model': 'DeepSeek-V4-Flash', 'finish_reason': 'stop'})
            self.assertEqual(b.receipt()['cost_reserved_exact'], '59.513472')
            with self.assertRaises(PermissionError):
                b.before('', 'x', 1500, 0)
            self.assertEqual(b.requests, 432)

    def test_failed_primitive_claim_preserves_callable_noargs_fallback(self):
        env = mock.Mock()
        env.verify_primitive.return_value = {'passed': False}
        for target in (None, 'dev-x'):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                lib = Library(str(Path(tmp) / 'library'))
                e = lib.add('a00_r01', 0, 1, 'fixture', 'fixture', target, SOURCE, ['unit_convert'])
                contract(e, {})
                e['signature_signal'] = ['valid_noargs_output'] * 8
                lib.save()
                kept, _, meta = freeze_library(tmp, str(Path(tmp) / 'frozen'), env)
                self.assertEqual(len(kept), 1)
                self.assertEqual(meta['kept_parametric'], [])
                env.harness.assert_not_called()


class StageBV2ExecutionTests(test_stage_b.StageBTests):
    """Apply the existing full launcher/approval/failure checks to the v2 config."""
    def setUp(self):
        super().setUp()
        self.c = read_json(ROOT / 'configs/agentport_flash_stage_b_v2.json')


@unittest.skipUnless(os.environ.get('BOIDS_SANDBOX') == 'docker', 'explicit offline Docker fixtures only')
class TargetContractDockerTests(unittest.TestCase):
    def setUp(self):
        self.env = MechEnv(DEFAULT_ENV)
        self.task = next(t for t in self.env.dev_tasks()
                         if t['obj'].steps == [('unit_convert', {'col': 'price_cents', 'factor': .01})])

    def test_bound_harness_preserves_reference_and_unbound_legacy(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = Library(tmp)
            lib.add('a00_r01', 0, 1, 'fixture', 'fixture', self.task['id'], SOURCE)
            tool = SandboxedTool(tmp, 'a00_r01')
            self.assertTrue(self.env.harness(tool, self.task, {'col': 'price_cents', 'factor': .01})['passed'])
            self.assertFalse(self.env.harness(tool, self.task, {'col': 'price_cents', 'factor': .02})['passed'])
            self.assertFalse(self.env.harness(tool, self.task)['passed'])

    def test_target_only_parameterized_tool_retained_wrong_contract_dropped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lib = Library(str(root / 'library'))
            for i, factor in enumerate((.01, .02)):
                e = lib.add(f'a0{i}_r01', i, 1, 'fixture', 'fixture', self.task['id'], SOURCE)
                contract(e, {'col': 'price_cents', 'factor': factor})
                e['signature_signal'] = ['ERR:KeyError'] * 8
            lib.save()
            _, _, meta = freeze_library(tmp, str(root / 'frozen'), self.env, stop_on_anomaly=True)
            self.assertEqual(meta['kept_target_invocations'], ['a00_r01'])
            self.assertEqual(meta['dropped_all_crash'], ['a01_r01'])

    def test_target_freeze_resource_error_stops(self):
        from boidsnet.runner.smoke_policy import SmokeStop
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lib = Library(str(root / 'library'))
            e = lib.add('a00_r01', 0, 1, 'fixture', 'fixture', self.task['id'],
                        'def execute(table, lookup, **params):\n    open("/forbidden")\n')
            contract(e)
            e['signature_signal'] = ['ERR:PermissionError'] * 8
            lib.save()
            with self.assertRaisesRegex(SmokeStop, 'freeze_verification_execution_error'):
                freeze_library(tmp, str(root / 'frozen'), self.env, stop_on_anomaly=True)

    def test_none_target_optional_primitive_verified_despite_default_identity(self):
        source = SOURCE.replace('    col,', '    if not params:\n        return [dict(row) for row in table]\n    col,')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lib = Library(str(root / 'library'))
            e = lib.add('a00_r01', 0, 1, 'fixture', 'fixture', None, source, ['unit_convert'])
            contract(e, {})
            e['signature_signal'] = self.env.signature(SandboxedTool(lib.root, e['id']))
            self.assertFalse(any(s.startswith('ERR') for s in e['signature_signal']))
            lib.save()
            _, _, meta = freeze_library(tmp, str(root / 'frozen'), self.env, stop_on_anomaly=True)
            self.assertEqual(meta['kept_parametric'], ['a00_r01'])
            self.assertTrue(meta['verified_primitives']['a00_r01']['unit_convert'])

    def test_four_arm_build_freeze_solver_dependency_analysis_end_to_end(self):
        # Hand-written fixtures, fixed tiny menu, no SDK and no empirical claim.
        task, env = self.task, self.env
        class Fixture:
            def __init__(self):
                rng = random.Random('society:1001')
                self.order = []
                for _ in range(2):
                    order = list(range(3)); rng.shuffle(order); self.order.extend(order)
                self.n = 0
            def complete(self, system, user, *args):
                assert system == PARAM_SYSTEM
                agent = self.order[self.n]
                rnd = self.n // 3 + 1
                self.n += 1
                dep = f'a{(agent + 1) % 3:02d}_r01'
                code = SOURCE if rnd == 1 else (f'from tools import {dep}\n'
                    'def execute(table, lookup, **params):\n'
                    f'    return {dep}.execute(table, lookup, **params)\n')
                return response(task['id'], source=code, implements='unit_convert' if rnd == 1 else 'NONE'), 1, 1
            def solve(self, target, kept, k):
                tid = next(e['id'] for e in kept if e['round'] == 2)
                code = f'from tools import {tid}\ndef execute(table, lookup, **params):\n'
                code += f'    return {tid}.execute(table, lookup, col="price_cents", factor=0.01)\n'
                return '```python\n' + code + '```', 1, 1
        with tempfile.TemporaryDirectory() as tmp, mock.patch('openai.OpenAI', side_effect=AssertionError('NO_PROVIDER')):
            for arm in SAC_ARMS:
                root = Path(tmp) / arm
                cfg = RunConfig(arm=arm, seed=1001, n_agents=3, n_rounds=2,
                                extra={'target_contract': VERSION, 'stop_on_smoke_anomaly': True})
                model = Fixture()
                with mock.patch.object(env, 'menu', return_value=[task]):
                    soc = Society(cfg, env, model, str(root))
                    built = soc.run()
                analysis.write(root / 'run_manifest.json', cfg.to_dict() | {'engineering': True, 'env_sha256': env.file_sha256})
                rows = [json.loads(x) for x in (root / 'rounds.jsonl').read_text().splitlines()]
                self.assertEqual(built['records'], 6)
                self.assertTrue(all(r['harness']['passed'] for r in rows))
                second = [r for r in rows if r['round'] == 2]
                self.assertTrue(all(not r['sac_evidence']['A']['fallback'] for r in second))
                self.assertTrue(all(r['sac_fired'] == {n: b == '1' for n, b in zip('SAC', arm)} for r in second))
                score_society(str(root), env, model, attempts=2, split='dev', task_ids=[task['id']], stop_on_smoke_anomaly=True)
                before = analysis.hashes(root)
                report = analysis.analyze_society(root, Path(tmp) / (arm + '-analysis'), env, stop_on_smoke_anomaly=True)
                s = report['summary']
                self.assertEqual(s['depth_utility']['pooled_U_dev'], 1.0)
                self.assertEqual(s['M_cross']['numerator'], 1)
                self.assertEqual(s['M_cross']['denominator'], 2)
                self.assertEqual(s['M_cross']['unknown_tools'], 0)
                self.assertEqual(s['M_cross']['edge_counts'], {'functional_load_bearing': 1})
                self.assertEqual(s['mechanism_delivery']['declared_target_passes'], 6)
                self.assertEqual(before, analysis.hashes(root))


if __name__ == '__main__':
    unittest.main()
