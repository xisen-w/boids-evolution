"""Artificial controls for offline measurement; not model research evidence."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from boidsnet.runner import analysis as a, analysis_worker
from boidsnet.runner.env_adapter import MechEnv
from boidsnet.runner.library import Library
from boidsnet.runner.run import DEFAULT_ENV


def traced(value, edges=(), hits=0, complete=True):
    return dict(value=value, edges=list(edges), unsupported=[], ablation_hits=hits, trace_complete=complete)


class MeasurementTests(unittest.TestCase):
    def setUp(self):
        self.env = MechEnv(DEFAULT_ENV)

    def test_probe_seeds_and_parameters_independent_and_deterministic(self):
        sets = [a.ANALYSIS_PROTOCOL[k] for k in ('unparameterized_seeds', 'target_and_ablation_seeds')]
        sets += a.ANALYSIS_PROTOCOL['reliability_seeds']
        self.assertEqual(len(set(s for row in sets for s in row)), sum(map(len, sets)))
        for p in self.env.primitives:
            self.assertEqual(a.parameter_draws(self.env, p), a.parameter_draws(self.env, p))
        self.assertEqual(len(self.env.primitives), 22)

    def test_behavior_errors_and_non_tables_are_not_duplicates(self):
        for y in ({'__error__': 'same'}, 123, [{'x': []}]):
            r = a.pair_behavior(self.env, [traced(y)] * 8, [traced(y)] * 8)
            self.assertFalse(r['comparable'])
            self.assertFalse(r['duplicate'])

    def test_behavior_equal_uses_six_decimal_reference_comparison(self):
        r = a.pair_behavior(self.env, [traced([{'x': 0.12345671}])] * 8,
                            [traced([{'x': 0.12345672}])] * 8)
        self.assertTrue(r['duplicate'])
        r = a.pair_behavior(self.env, [traced([{'x': 1}, {'x': 2}])] * 8,
                            [traced([{'x': 2}, {'x': 1}])] * 8)
        self.assertFalse(r['duplicate'])

    def test_edge_classifications_and_crash_not_functional(self):
        edge = ('a01_r02', 'a00_r01')
        expected = [[{'x': 2}]] * 8
        good = [traced(expected[0], [edge])] * 8
        wrong = [traced([{'x': 1}], [edge], 1)] * 8
        self.assertEqual(a.classify_edge(self.env, good, wrong, expected, edge), 'functional_load_bearing')
        self.assertEqual(a.classify_edge(self.env, good, [traced(expected[0], [edge], 1)] * 8, expected, edge), 'no_observed_effect')
        self.assertEqual(a.classify_edge(self.env, good, [traced({'__error__': 'KeyError'}, [edge], 1)] * 8, expected, edge), 'structural')
        self.assertEqual(a.classify_edge(self.env, good, [traced(expected[0], [edge], 0)] * 8, expected, edge), 'unknown')
        self.assertEqual(a.classify_edge(self.env, [traced(expected[0])] * 8, None, expected, edge), 'unused')
        self.assertEqual(a.classify_edge(self.env, [traced([{'x': 1}])] * 8, None, expected, edge), 'intact_failed')
        self.assertEqual(a.classify_edge(self.env, [traced(expected[0], complete=False)] * 8, None, expected, edge), 'unknown')

    def test_mcross_denominator_unknown_bounds_and_empty(self):
        result = a.m_cross_summary([{'status': 'functional_load_bearing'}, {'status': 'no_valid_target'},
                                    {'status': 'no_observed_functional_dependency'}], [])
        self.assertEqual(result['numerator'], 1)
        self.assertEqual(result['denominator'], 3)
        self.assertEqual(result['lower_bound'], 1/3)
        self.assertEqual(result['upper_bound'], 2/3)
        self.assertIsNone(a.m_cross_summary([], [])['observed_fraction'])

    def test_transitive_edge_not_recounted_for_upstream_root(self):
        index = {'a00_r01': {'author': 0}, 'a01_r02': {'author': 1}, 'a02_r03': {'author': 2}}
        rows = [traced([], [('a02_r03', 'a01_r02'), ('a01_r02', 'a00_r01')])]
        edges = a.direct_cross_edges('a02_r03', index, 'from tools import a01_r02', rows)
        self.assertEqual(edges, {('a02_r03', 'a01_r02')})

    def test_nonfinite_outputs_remain_explicit_in_saved_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'row.json'
            a.write(path, {'value': float('nan')})
            self.assertEqual(a.read(path), {'value': {'__nonfinite_float__': 'nan'}})

    def test_frozen_acl_drift_rejected_before_measurement(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lib = Library(str(root / 'library'))
            lib.add('a00_r01', 0, 1, 'fixture', 'fixture', None, 'def execute(table, lookup):\n    return table\n')
            frozen = root / 'utility_dev/frozen_library'
            shutil.copytree(root / 'library', frozen)
            freeze = {'kept': ['a00_r01'], 'dependency_only': []}
            a.verify_frozen_inputs(root, 'utility_dev', lib.entries, freeze)
            (frozen / 'acl.json').write_text('{"a00_r01":["a01_r01"]}')
            with self.assertRaisesRegex(ValueError, 'ACL mismatch'):
                a.verify_frozen_inputs(root, 'utility_dev', lib.entries, freeze)

    def test_missing_trace_becomes_unknown(self):
        with mock.patch('boidsnet.runner.sandbox.run_tool', return_value=[{'__error__': 'timeout'}]):
            r = analysis_worker.execute('/fixture', 'a00_r01', [{}])[0]
        self.assertFalse(r['trace_complete'])

    def test_paid_analysis_stops_on_critical_probe_errors_in_either_worker(self):
        from boidsnet.runner.smoke_policy import SmokeStop
        envelope = dict(analysis_protocol=1, value=[], edges=[], unsupported=[], ablation_hits=0)
        for error in ('timeout', 'PermissionError: forbidden', 'output size limit', 'MemoryError: allocation'):
            bad = {'__error__': error}
            for responses in ([[bad]], [[dict(envelope, value=bad)]], [[envelope], [bad]]):
                with self.subTest(error=error, ordinary_worker=len(responses) == 2), \
                     mock.patch('boidsnet.runner.sandbox.run_tool', side_effect=responses) as run:
                    with self.assertRaisesRegex(SmokeStop, 'analysis_probe_execution_error'):
                        analysis_worker.execute('/fixture', 'a00_r01', [{}], stop_on_anomaly=True)
                    self.assertEqual(run.call_count, len(responses))

    def test_paid_analysis_keeps_ordinary_model_errors_without_resampling(self):
        for error in ('KeyError: col', 'TypeError: missing argument', 'ValueError: wrong data'):
            bad = {'__error__': error}
            with mock.patch('boidsnet.runner.sandbox.run_tool', return_value=[bad]) as run:
                row = analysis_worker.execute('/fixture', 'a00_r01', [{}], stop_on_anomaly=True)[0]
            self.assertEqual(row['value'], bad)
            self.assertFalse(row['trace_complete'])
            self.assertEqual(run.call_count, 2)  # intact plus ordinary-worker verification only

    def test_infrastructure_error_not_converted_to_model_zero(self):
        from boidsnet.runner.sandbox import SandboxInfrastructureError
        with mock.patch('boidsnet.runner.sandbox.run_tool', side_effect=SandboxInfrastructureError()):
            with self.assertRaises(SandboxInfrastructureError):
                analysis_worker.execute('/fixture', 'a00_r01', [{}])

    def test_refuses_output_inside_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                a.analyze_society(tmp, Path(tmp) / 'analysis', self.env, require_os=False)

    def test_worker_keeps_security_hooks_and_validates_edges(self):
        worker = analysis_worker.worker(('a01_r02', 'a00_r01'))
        self.assertIn('sys.setprofile(_check_call)', worker)
        self.assertIn('sys.addaudithook(_hook)', worker)
        compile(worker, '<fixture>', 'exec')
        with self.assertRaises(ValueError):
            analysis_worker.worker(('../bad', 'a00_r01'))


@unittest.skipUnless(os.environ.get('BOIDS_SANDBOX') == 'docker', 'explicit offline Docker fixtures only')
class AnalysisDockerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.lib = Library(self.tmp.name)
        self.calls = [{'args': [[{'x': 1}], []], 'kwargs': {}}] * 8

    def add(self, tid, code, acl=()):
        self.lib.add(tid, int(tid[1:3]), int(tid[-2:]), 'fixture', 'fixture', None, code, acl=acl)

    def run_source(self, top, edge=None):
        return analysis_worker.execute(self.tmp.name, top, self.calls, ablation=edge)

    def test_importer_specific_alias_and_other_caller_unchanged(self):
        self.add('a00_r01', 'def execute(table, lookup, **params):\n    return [{"x": r["x"] + 1} for r in table]\n')
        self.add('a01_r02', 'from tools.a00_r01 import execute as use\ndef execute(table, lookup, **params):\n    return use(table, lookup)\n', ['a00_r01'])
        self.add('a02_r02', 'from . import a00_r01\ndef execute(table, lookup, **params):\n    return a00_r01.execute(table, lookup)\n', ['a00_r01'])
        self.add('a03_r03', 'from tools import a01_r02, a02_r02\ndef execute(table, lookup, **params):\n    return a02_r02.execute(a01_r02.execute(table, lookup), lookup)\n', ['a01_r02', 'a02_r02'])
        before = a.hashes(Path(self.tmp.name))
        intact = self.run_source('a03_r03')
        changed = self.run_source('a03_r03', ('a01_r02', 'a00_r01'))
        self.assertTrue(all(r['value'] == [{'x': 3}] for r in intact), intact)
        self.assertTrue(all(r['value'] == [{'x': 2}] and r['ablation_hits'] == 1 for r in changed), changed)
        self.assertTrue(all(['a02_r02', 'a00_r01'] in r['edges'] for r in changed))
        self.assertEqual(before, a.hashes(Path(self.tmp.name)))

    def test_dynamic_import_traced_and_ablated(self):
        self.add('a00_r01', 'def execute(table, lookup, **params):\n    return [{"x": 2}]\n')
        self.add('a01_r02', 'import importlib\ndef execute(table, lookup, **params):\n    return importlib.import_module("tools.a00_r01").execute(table, lookup)\n', ['a00_r01'])
        self.assertTrue(all(r['value'] == [{'x': 2}] for r in self.run_source('a01_r02')))
        self.assertTrue(all(r['value'] == [{'x': 1}] for r in self.run_source('a01_r02', ('a01_r02', 'a00_r01'))))

    def test_unsupported_cross_tool_helpers_are_unknown(self):
        self.add('a00_r01', 'def helper(table):\n    return table\ndef execute(table, lookup, **params):\n    return table\n')
        self.add('a01_r02', 'from tools import a00_r01\ndef execute(table, lookup, **params):\n    return a00_r01.helper(table)\n', ['a00_r01'])
        self.assertTrue(all(not r['trace_complete'] for r in self.run_source('a01_r02')))

    def test_ablation_cannot_bypass_acl(self):
        self.add('a00_r01', 'def execute(table, lookup, **params):\n    return table\n')
        self.add('a01_r02', 'from tools import a00_r01\ndef execute(table, lookup, **params):\n    return a00_r01.execute(table, lookup)\n')
        result = self.run_source('a01_r02', ('a01_r02', 'a00_r01'))
        self.assertTrue(all(a.is_error(r['value']) for r in result))

    def test_strict_analysis_stops_real_timeout_and_permission_denial(self):
        from boidsnet.runner.smoke_policy import SmokeStop
        self.add('a00_r01', 'def execute(table, lookup, **params):\n    while True:\n        pass\n')
        self.add('a01_r01', 'def execute(table, lookup, **params):\n    open("/forbidden")\n    return table\n')
        for tid in ('a00_r01', 'a01_r01'):
            with self.subTest(tool=tid), self.assertRaisesRegex(SmokeStop, 'analysis_probe_execution_error'):
                analysis_worker.execute(self.tmp.name, tid, self.calls[:1], timeout_s=0.2, stop_on_anomaly=True)

    def test_instrumented_and_original_values_match(self):
        from boidsnet.runner.sandbox import run_tool
        self.add('a00_r01', 'def execute(table, lookup, **params):\n    return [{"x": r["x"] * 2} for r in table]\n')
        self.assertEqual([r['value'] for r in self.run_source('a00_r01')], run_tool(self.tmp.name, 'a00_r01', self.calls))

    def test_complete_analysis_has_real_functional_edge_and_round_coverage(self):
        import shutil
        from tests.test_parametric_smoke import SOURCE
        env = MechEnv(DEFAULT_ENV)
        # This is an explicitly HAND-WRITTEN fixture, never a model society.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            society = root / 'society'
            society.mkdir()
            lib = Library(str(society / 'library'))
            lib.add('a00_r01', 0, 1, 'unit convert', 'col factor', None, SOURCE, ['unit_convert'])
            target = next(t for t in env.dev_tasks() if t['obj'].steps == [('unit_convert', {'col': 'price_cents', 'factor': 0.01})])
            code = ('from tools import a00_r01\ndef execute(table, lookup, **params):\n'
                    '    return a00_r01.execute(table, lookup, col="price_cents", factor=0.01)\n')
            lib.add('a01_r02', 1, 2, 'cents dollars', 'convert price', target['id'], code, acl=['a00_r01'])
            utility = society / 'utility_dev'
            utility.mkdir()
            shutil.copytree(society / 'library', utility / 'frozen_library')
            a.write(utility / 'frozen_library/freeze.json', {'kept': ['a01_r02'], 'dependency_only': ['a00_r01']})
            a.write(society / 'run_manifest.json', {'arm': '111', 'seed': 1, 'n_agents': 4, 'n_rounds': 2, 'env_sha256': env.file_sha256})
            (society / 'rounds.jsonl').write_text('')
            before = a.hashes(society)
            with mock.patch.object(a, 'depth_summary', return_value={'diagnostic_only': True}):
                report = a.analyze_society(society, root / 'result', env)
            s = report['summary']
            self.assertEqual(s['M_cross']['numerator'], 1)
            self.assertEqual(s['M_cross']['denominator'], 1)  # dependency-only excluded
            self.assertEqual(s['M_cross']['edge_counts'], {'functional_load_bearing': 1})
            self.assertEqual(s['raw_coverage']['reliable_primitives'], ['unit_convert'])
            self.assertEqual([p['reliable_primitive_count'] for p in s['coverage_by_round']], [1, 1])
            self.assertEqual(before, a.hashes(society))
            with self.assertRaises(FileExistsError):
                a.analyze_society(society, root / 'result', env)


if __name__ == '__main__':
    unittest.main()
