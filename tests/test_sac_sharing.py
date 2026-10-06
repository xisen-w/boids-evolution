"""Offline contracts for common evidence and executable tool sharing."""
import json
import os
import tempfile
import unittest

from boidsnet.runner.config import RunConfig, SAC_ARMS
from boidsnet.runner.library import Library
from boidsnet.runner.mechanisms import build_evidence, render_evidence
from boidsnet.runner.sandbox import TOOL_ID, run_tool, is_error
from boidsnet.runner.society import Society


def fixture():
    rows = []
    for tool_id, author, rnd, imports, acl in (
        ('a01_r01', 1, 1, [], []),
        ('a03_r01', 3, 1, ['a01_r01'], ['a01_r01']),
        ('a01_r02', 1, 2, ['a01_r01'], []),
        ('a02_r02', 2, 2, ['a01_r01'], ['a01_r01']),
        ('a02_r01', 2, 1, ['a01_r02'], ['a01_r02']),
    ):
        rows.append(dict(id=tool_id, author=author, round=rnd,
                         static_imports=imports, build_acl=acl,
                         label='table cleaner', description='clean table rows',
                         target='dev_fixture', implements=['clean'],
                         harness={'passed': True}))
    return rows


class EvidenceTests(unittest.TestCase):
    def test_nonempty_matched_evidence_all_toggles(self):
        snapshot = fixture()
        source = lambda _: 'def execute(table, lookup, **params):\n    return table\n'
        baseline = None
        for arm in SAC_ARMS:
            bundle = build_evidence(snapshot, [1, 3], 3, source)
            self.assertEqual(bundle['fired'], dict(S=True, A=True, C=True))
            if baseline is None:
                baseline = bundle
            self.assertEqual(bundle, baseline)
            before = json.dumps(bundle, sort_keys=True)
            toggles = RunConfig(arm=arm, seed=1).mechanism_toggles
            rendered = render_evidence(bundle, toggles)
            neutral = render_evidence(bundle, dict(S=False, A=False, C=False))
            for rule in 'SAC':
                name = dict(S='SEPARATION', A='ALIGNMENT', C='COHESION')[rule]
                self.assertEqual(name + ' GUIDANCE:' in rendered, toggles[rule])
            # All descriptive evidence is present verbatim, in order.
            cursor = 0
            for line in neutral.splitlines():
                cursor = rendered.index(line, cursor) + len(line)
            self.assertEqual(json.dumps(bundle, sort_keys=True), before)

    def test_adoption_requires_prior_round_and_recorded_acl(self):
        bundle = build_evidence(fixture(), [1, 3], 3,
                                lambda _: 'def execute(x):\n    return x\n')
        leader = bundle['A']['adoption']
        self.assertEqual(leader['id'], 'a01_r01')
        self.assertEqual(leader['adopted_by'], ['a02_r02'])
        self.assertEqual(leader['adoption_count'], 1)


class SharingTests(unittest.TestCase):
    def test_transitive_cross_agent_execute_and_denied_guesses(self):
        with tempfile.TemporaryDirectory() as root:
            lib = Library(root)
            base = lib.add('a100_r100', 100, 100, 'base', '', None,
                           'def execute(x):\n    return x + 1\n')
            middle = lib.add('a01_r101', 1, 101, 'middle', '', None,
                             'from tools import a100_r100\ndef execute(x):\n'
                             '    return a100_r100.execute(x) * 2\n', acl=[base['id']])
            top = lib.add('a02_r102', 2, 102, 'top', '', None,
                          'from tools import a01_r101\ndef execute(x):\n'
                          '    return a01_r101.execute(x) + 3\n', acl=[middle['id']])
            self.assertEqual(run_tool(root, top['id'], [{'args': [4]}]), [13])
            for tid in (base['id'], middle['id'], top['id']):
                self.assertIsNotNone(TOOL_ID.fullmatch(tid))
            guessed = lib.add('a03_r102', 3, 102, 'guess', '', None,
                              'from tools import a100_r100\ndef execute(x):\n'
                              '    return a100_r100.execute(x)\n', acl=[])
            self.assertTrue(is_error(run_tool(root, guessed['id'], [{'args': [4]}])[0]))

    def test_same_round_absent_and_previous_round_visible_in_all_arms(self):
        class Env:
            primitives = []
            def dev_tasks(self): return []
            def menu(self, *args): return []
        class Model:
            def complete(self, *args):
                return ('TOOL_LABEL: table cleaner\nTARGET: NONE\nIMPLEMENTS: NONE\n'
                        'DESCRIPTION: clean table rows\n```python\n'
                        'def execute(table, lookup, **params):\n    return table\n```', 1, 1)
        with tempfile.TemporaryDirectory() as root:
            for arm in SAC_ARMS:
                society = Society(RunConfig(arm=arm, seed=1), Env(), Model(),
                                  os.path.join(root, arm))
                try:
                    _, first = society._agent_turn(0, 1, [])
                    _, second = society._agent_turn(1, 1, [])
                    self.assertEqual(second['build_acl'], [])
                    snapshot = list(society.lib.entries.values())
                    _, next_round = society._agent_turn(2, 2, snapshot)
                    self.assertEqual(next_round['build_acl'], sorted(e['id'] for e in snapshot))
                    with open(os.path.join(society.out, 'prompts', next_round['id'] + '.json')) as f:
                        prompt = json.load(f)['user']
                    self.assertIn('- ' + first['id'] + ' ', prompt)
                    self.assertIn('- ' + second['id'] + ' ', prompt)
                finally:
                    society.log.close()
