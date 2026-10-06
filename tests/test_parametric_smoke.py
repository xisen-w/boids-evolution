"""Offline contract checks: parametric components are not broken task tools."""
import os
import tempfile
import types
import unittest
from unittest import mock

from boidsnet.runner.config import RunConfig
from boidsnet.runner.env_adapter import MechEnv
from boidsnet.runner.run import DEFAULT_ENV
from boidsnet.runner.smoke_policy import (SmokeStop, missing_parameter,
                                        verified_parametric_component)
from boidsnet.runner.society import Society


SOURCE = '''def execute(table, lookup, **params):
    col, factor = params['col'], params['factor']
    out = [dict(row) for row in table]
    for row in out:
        if row.get(col) is not None:
            row[col] *= factor
    return out
'''
VALUE_SOURCE = SOURCE.replace('def execute(table, lookup, **params):\n    col, factor = params[\'col\'], params[\'factor\']',
                             'def execute(table, lookup, col=None, factor=None):\n'
                             '    if col is None or factor is None:\n'
                             '        raise ValueError("col and factor parameters required")')
TYPE_SOURCE = SOURCE.replace('def execute(table, lookup, **params):\n    col, factor = params[\'col\'], params[\'factor\']',
                            'def execute(table, lookup, col, factor):')


class ParametricPolicyTests(unittest.TestCase):
    def test_shared_prompt_states_lookup_container_and_public_schema(self):
        from boidsnet.runner.prompts import SYSTEM
        self.assertIn('Both table and lookup are lists of dict rows', SYSTEM)
        self.assertIn('not dictionaries keyed by region', SYSTEM)
        self.assertIn('region (str)', SYSTEM)
        self.assertIn('target (float)', SYSTEM)
        self.assertIn('manager (str)', SYSTEM)
        # Public interface only, not a reference implementation or probe values.
        self.assertNotIn('p_lookup_ratio', SYSTEM)
        self.assertNotIn('36190', SYSTEM)

    def test_only_exact_known_missing_parameter_is_classified(self):
        self.assertTrue(missing_parameter("KeyError: 'col'", {'col'}))
        for error in ("KeyError: 'unknown'", 'timeout', "TypeError: wrong input",
                      "KeyError: 'col' additional text", None, 'ERR:RuntimeError'):
            self.assertFalse(missing_parameter(error, {'col'}))

    def test_explicit_keyword_interfaces_use_valueerror_or_typeerror(self):
        names = {'col', 'factor'}
        for error in ('ValueError: col and factor parameters required',
                      'ValueError: Missing col or factor',
                      "TypeError: execute() missing 2 required positional arguments: 'col' and 'factor'",
                      "TypeError: execute() missing 1 required keyword-only argument: 'col'"):
            self.assertTrue(missing_parameter(error, names), error)
        for error in ('ValueError: invalid col value', 'ValueError: missing unknown',
                      'ValueError: database failure', 'PermissionError: col required',
                      "TypeError: execute() missing 1 required positional argument: 'unknown'"):
            self.assertFalse(missing_parameter(error, names), error)

    def test_missing_valueerror_still_requires_noncrashing_primitive_verification(self):
        env = MechEnv(DEFAULT_ENV)
        entry = {'target': None, 'implements': ['unit_convert']}
        error = 'raised ValueError: col and factor parameters required'
        for crashed in (0, 1):
            with mock.patch.object(env, 'verify_primitive', return_value={'passed': not crashed, 'crashed': crashed}) as verify:
                result = verified_parametric_component(env, None, entry, error)
                verify.assert_called_once()
                self.assertEqual(result is not None, not crashed)

    def test_independent_verification_required_no_task_target_or_false_claim(self):
        env = MechEnv(DEFAULT_ENV)
        entry = {'target': None, 'implements': ['unit_convert']}
        with mock.patch.object(env, 'verify_primitive', return_value={'passed': True, 'crashed': 0}) as verify:
            result = verified_parametric_component(env, None, entry, "raised KeyError: 'col'")
            self.assertEqual(result['parameter_names'], ['col', 'factor'])
            verify.assert_called_once()
            verify.reset_mock()
            for changed, feedback in (
                (dict(entry, target='dev-any'), "raised KeyError: 'col'"),
                (dict(entry, implements=[]), "raised KeyError: 'col'"),
                (dict(entry, implements=['made_up']), "raised KeyError: 'col'"),
                (entry, 'raised timeout'),
            ):
                self.assertIsNone(verified_parametric_component(env, None, changed, feedback))
            verify.assert_not_called()
            self.assertIsNone(verified_parametric_component(env, None, entry, "raised KeyError: 'unknown'"))
        with mock.patch.object(env, 'verify_primitive', return_value={'passed': False, 'crashed': 0}):
            classified = verified_parametric_component(env, None, entry, "raised KeyError: 'col'")
            self.assertFalse(classified['semantic_passed'])
            self.assertEqual(classified['verified_primitives'], {})
        for verdict in ({'passed': False, 'crashed': 1},
                        {'passed': True, 'crashed': 1}):
            with mock.patch.object(env, 'verify_primitive', return_value=verdict):
                self.assertIsNone(verified_parametric_component(env, None, entry, "raised KeyError: 'col'"))

    def evaluate_fixture(self, tmp, env, source=SOURCE):
        soc = Society(RunConfig(arm='000', seed=1001, n_agents=4, n_rounds=3,
                               extra={'stop_on_smoke_anomaly': True}), env, None, tmp)
        entry = soc.lib.add('a00_r01', 0, 1, 'unit_convert', 'col, factor', None,
                            source, ['unit_convert'])
        rec = {'round': 1, 'agent': 0, 'tool_id': entry['id']}
        return soc, entry, rec

    def test_signal_errors_inspected_individually_not_ignored_for_verified_tool(self):
        env = MechEnv(DEFAULT_ENV)
        for errors, should_stop in ((["KeyError: 'col'"] * 8, False),
                                    (["KeyError: 'col'"] * 7 + ['timeout'], True),
                                    (["KeyError: 'col'"] * 7 + ["KeyError: 'unknown'"], False)):
            with self.subTest(errors=errors[-1]), tempfile.TemporaryDirectory() as tmp:
                soc, entry, rec = self.evaluate_fixture(tmp, env)
                tool = types.SimpleNamespace(prefetch=lambda calls: [{'__error__': e} for e in errors])
                try:
                    with mock.patch('boidsnet.runner.society.SandboxedTool', return_value=tool), \
                            mock.patch.object(env, 'exec_feedback', return_value="raised KeyError: 'col'"), \
                            mock.patch.object(env, 'verify_primitive', return_value={'passed': True, 'crashed': 0}), \
                            mock.patch.object(env, 'signature', return_value=['ERR:RuntimeError'] * 8):
                        if should_stop:
                            with self.assertRaisesRegex(SmokeStop, 'builder_probe_execution_error'):
                                soc._evaluate(rec, entry)
                        else:
                            soc._evaluate(rec, entry)
                            self.assertEqual(rec['signature_errors'], 8)  # retain raw failures
                            self.assertEqual(rec['parametric_probe_contract']['signal_errors_classified']
                                             + rec.get('model_probe_error_count', 0), 8)
                            self.assertFalse(rec['harness']['passed'])  # no fabricated task pass
                finally:
                    soc.log.close()

    def test_crashing_primitive_verdict_is_retained_and_stops_before_signal(self):
        env = MechEnv(DEFAULT_ENV)
        verdict = {'passed': False, 'n_pass': 0, 'n_total': 12, 'crashed': 12,
                   'details': ['offline fixture: ValueError']}
        with tempfile.TemporaryDirectory() as tmp:
            soc, entry, rec = self.evaluate_fixture(tmp, env)
            try:
                with mock.patch.object(env, 'exec_feedback', return_value="raised KeyError: 'col'"), \
                        mock.patch.object(env, 'verify_primitive', return_value=verdict), \
                        mock.patch.object(env, 'signature') as signature:
                    with self.assertRaisesRegex(SmokeStop, 'builder_parametric_verification_failed'):
                        soc._evaluate(rec, entry)
                    signature.assert_not_called()
                self.assertEqual(rec['parametric_probe_diagnostic']['primitive_verdicts']['unit_convert'], verdict)
                self.assertNotIn('parametric_probe_contract', rec)
                # Failed oracle evidence is internal audit data, never a new
                # public feedback message or library/exemplar metadata.
                self.assertEqual(soc.feedback, {})
                self.assertNotIn('parametric_probe_diagnostic', entry)
            finally:
                soc.log.close()


@unittest.skipUnless(os.environ.get('BOIDS_SANDBOX') == 'docker', 'explicit Docker offline validation only')
class ParametricDockerTests(unittest.TestCase):
    def test_signed_literal_glue_executes_without_solver_arithmetic(self):
        from boidsnet.runner.library import Library
        from boidsnet.runner.sandbox import SandboxedTool
        from boidsnet.runner.utility import glue_gate
        glue = ('from tools import a00_r01\n'
                'def execute(table, lookup, **params):\n'
                '    return a00_r01.execute(table, lookup, col="units", factor=-1)\n')
        self.assertTrue(glue_gate(glue, {'a00_r01'})[0])
        with tempfile.TemporaryDirectory() as tmp:
            lib = Library(tmp)
            lib.add('a00_r01', 0, 1, 'unit_convert', 'Synthetic control', None, SOURCE)
            lib.add('a01_r01', 1, 1, 'signed_glue', 'Synthetic control', None, glue,
                    acl=['a00_r01'])
            self.assertEqual(SandboxedTool(tmp, 'a01_r01')([{'units': 2}], []), [{'units': -2}])

    def test_false_composite_claim_keeps_crashes_failed_and_is_dropped(self):
        from boidsnet.runner.utility import freeze_library
        source = '''def execute(table, lookup, **params):
    key, col = params['key'], params['col']
    op, value = params['op'], params['value']
    seen, out = set(), []
    for row in table:
        if row.get(key) not in seen:
            seen.add(row.get(key))
            if row.get(col) is not None and row[col] > value:
                out.append(dict(row))
    return out
'''
        env = MechEnv(DEFAULT_ENV)
        with tempfile.TemporaryDirectory() as tmp:
            soc, entry, rec = ParametricPolicyTests().evaluate_fixture(tmp, env, source)
            entry['implements'] = ['dedupe', 'filter']
            try:
                soc._evaluate(rec, entry)
                self.assertFalse(rec['harness']['passed'])
                self.assertFalse(rec['parametric_probe_contract']['semantic_passed'])
                for verdict in rec['parametric_probe_diagnostic']['primitive_verdicts'].values():
                    self.assertFalse(verdict['passed'])
                    self.assertEqual((verdict['n_pass'], verdict['n_total'], verdict['crashed']), (0, 12, 12))
                kept, _, frozen = freeze_library(tmp, os.path.join(tmp, 'frozen'), env)
                self.assertEqual(kept, [])
                self.assertIn(entry['id'], frozen['dropped_all_crash'])
            finally:
                soc.log.close()

    def test_explicit_keyword_tools_survive_all_real_probe_and_freeze_paths(self):
        from boidsnet.runner.utility import freeze_library
        env = MechEnv(DEFAULT_ENV)
        for source in (VALUE_SOURCE, TYPE_SOURCE):
            with self.subTest(signature=source.splitlines()[0]), tempfile.TemporaryDirectory() as tmp:
                soc, entry, rec = ParametricPolicyTests().evaluate_fixture(tmp, env, source)
                try:
                    soc._evaluate(rec, entry)
                    self.assertEqual(rec['parametric_probe_contract']['signal_errors_classified'], 8)
                    self.assertFalse(rec['harness']['passed'])
                    verdict = rec['parametric_probe_diagnostic']['primitive_verdicts']['unit_convert']
                    self.assertEqual((verdict['n_pass'], verdict['n_total'], verdict['crashed']), (12, 12, 0))
                    kept, _, freeze = freeze_library(tmp, os.path.join(tmp, 'frozen'), env)
                    self.assertEqual([e['id'] for e in kept], [entry['id']])
                    self.assertTrue(freeze['verified_primitives'][entry['id']]['unit_convert'])
                finally:
                    soc.log.close()

    def test_wrong_parametric_output_stays_failed_and_excluded_from_freeze(self):
        from boidsnet.runner.utility import freeze_library
        env = MechEnv(DEFAULT_ENV)
        wrong_source = SOURCE.replace('row[col] *= factor', 'row[col] += factor')
        with tempfile.TemporaryDirectory() as tmp:
            soc, entry, rec = ParametricPolicyTests().evaluate_fixture(tmp, env, wrong_source)
            try:
                soc._evaluate(rec, entry)
                self.assertFalse(rec['parametric_probe_contract']['semantic_passed'])
                verdict = rec['parametric_probe_diagnostic']['primitive_verdicts']['unit_convert']
                self.assertEqual((verdict['n_pass'], verdict['n_total'], verdict['crashed']), (0, 12, 0))
                self.assertFalse(rec['harness']['passed'])
                kept, _, freeze = freeze_library(tmp, os.path.join(tmp, 'frozen'), env)
                self.assertEqual(kept, [])
                self.assertEqual(freeze['dropped_all_crash'], [entry['id']])
                self.assertFalse(freeze['verified_primitives'][entry['id']]['unit_convert'])
            finally:
                soc.log.close()

    def test_real_parametric_component_survives_freeze_but_wrong_target_is_failed(self):
        from boidsnet.runner.utility import freeze_library
        from boidsnet.runner.sandbox import isolation_level
        self.assertEqual(isolation_level(), 'os-docker')
        env = MechEnv(DEFAULT_ENV)
        with tempfile.TemporaryDirectory() as tmp:
            soc, entry, rec = ParametricPolicyTests().evaluate_fixture(tmp, env)
            try:
                soc._evaluate(rec, entry)
                self.assertEqual(rec['parametric_probe_contract']['signal_errors_classified'], 8)
                kept, _, freeze = freeze_library(tmp, os.path.join(tmp, 'frozen'), env)
                self.assertEqual(freeze['kept_parametric'], [entry['id']])
                self.assertEqual([e['id'] for e in kept], [entry['id']])
                entry['target'] = env.dev_tasks()[0]['id']
                soc._evaluate(rec, entry)
                self.assertFalse(rec['harness']['passed'])
                self.assertEqual(rec['harness']['crashed'], 8)
                self.assertTrue(rec['model_harness_execution_failure'])
            finally:
                soc.log.close()


if __name__ == '__main__':
    unittest.main()
