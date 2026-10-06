"""Public schema must describe every primitive without exposing hidden examples."""
import inspect
import random
import unittest
from unittest import mock

from boidsnet.runner.env_adapter import MechEnv
from boidsnet.runner.run import DEFAULT_ENV
from boidsnet.runner.primitive_contract import PUBLIC_PRIMITIVES, render_public_contract
from boidsnet.runner.prompts import SYSTEM
from boidsnet.runner.gateway_probe import first_request
from tests.test_local_budget import local_config


class PublicContractTests(unittest.TestCase):
    def test_solver_sees_public_parameter_names_without_physical_line_cap(self):
        from types import SimpleNamespace
        from boidsnet.runner.utility import SOLVER_FORMAT, solver_prompt, glue_gate
        entry = {'id': 'a00_r01', 'author': 0, 'implements': ['filter'],
                 'description': 'Keep matching rows.'}
        source = 'def execute(table, lookup, **params):\n    return table\n'
        prompt = solver_prompt(SimpleNamespace(spec='Public task'), [entry], lambda _: source)
        self.assertIn('Declared filter call: a00_r01.execute(table, lookup, col=<col>, op=<op>, value=<value>)', prompt)
        self.assertNotIn('15 lines', SOLVER_FORMAT)
        self.assertNotIn('12 one-line call assignments', SOLVER_FORMAT)
        self.assertNotIn('probe_seeds', prompt)
        base = 'from tools import a00_r01\ndef execute(table, lookup, **params):\n'
        # Physical formatting and chain length do not create a gate failure.
        call = '    t = a00_r01.execute(table, lookup)\n'
        self.assertTrue(glue_gate(base + call * 12 + '    return t\n', {'a00_r01'})[0])
        self.assertTrue(glue_gate(base + call * 30 + '    return t\n', {'a00_r01'})[0])
        multiline = ('from tools import a00_r01\ndef execute(table, lookup, **params):\n'
                     '    return a00_r01.execute(\n        table,\n        lookup,\n'
                     '        col="units",\n        op=">",\n        value=0,\n    )\n')
        self.assertTrue(glue_gate(multiline, {'a00_r01'})[0])

    def test_solver_inability_still_requires_legal_tool_calls_without_scoring_change(self):
        from boidsnet.runner.utility import SOLVER_SYSTEM, SOLVER_FORMAT, glue_gate
        self.assertIn('library may be insufficient', SOLVER_SYSTEM)
        self.assertIn('incorrect result is scored as failure', SOLVER_SYSTEM)
        self.assertIn('returning the original input table without', SOLVER_FORMAT)
        invalid = 'from tools import a00_r01\ndef execute(table, lookup, **params):\n    return table\n'
        self.assertFalse(glue_gate(invalid, {'a00_r01'})[0])
        valid = 'from tools import a00_r01\ndef execute(table, lookup, **params):\n    return a00_r01.execute(table, lookup, col="units", factor=1.0)\n'
        self.assertTrue(glue_gate(valid, {'a00_r01'})[0])

    def test_all_primitive_argument_names_match_the_public_call_interface(self):
        env = MechEnv(DEFAULT_ENV)
        self.assertEqual(set(PUBLIC_PRIMITIVES), set(env.m.PRIMITIVES))
        for name, (ref, sample, _) in env.m.PRIMITIVES.items():
            declared = PUBLIC_PRIMITIVES[name][0].split(',')
            self.assertEqual(declared, list(inspect.signature(ref).parameters)[2:], name)
            for seed in range(20):
                self.assertEqual(set(sample(random.Random(seed))), set(declared), name)

    def test_all_filter_and_aggregate_modes_are_specified(self):
        self.assertIn('>, <, or ==', PUBLIC_PRIMITIVES['filter'][1])
        self.assertIn('zero, mean, or median', PUBLIC_PRIMITIVES['fill_missing'][1])
        self.assertIn('sum, mean, count, or max', PUBLIC_PRIMITIVES['group_agg'][1])
        self.assertIn('sum, count, or mean', PUBLIC_PRIMITIVES['multi_group_agg'][1])
        self.assertIn('*, -, or +', PUBLIC_PRIMITIVES['derive'][1])

    def test_contract_is_static_and_has_no_probe_values_or_reference_code(self):
        text = render_public_contract()
        for forbidden in ('def p_', 'SEED_RANGES', 'probe_seeds', '30000', '36190', 'n_param_draws'):
            self.assertNotIn(forbidden, text)
        self.assertIn(text, SYSTEM)
        with mock.patch('openai.OpenAI', side_effect=AssertionError('offline only')):
            request = first_request(local_config())
        self.assertEqual(request['system'], SYSTEM)
        self.assertIn('TARGET: <NONE if any keyword parameter is required', request['user'])
        self.assertIn('even when a menu task uses that primitive', request['user'])
        self.assertLess(len((request['system'] + request['user']).encode()), 16000)


if __name__ == '__main__':
    unittest.main()
