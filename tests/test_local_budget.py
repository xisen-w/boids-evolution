"""Offline-only circuit-breaker checks; no credentials or provider traffic."""
import copy
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
import json
import os
from pathlib import Path
import tempfile
import threading
import types
import unittest
from unittest import mock

from boidsnet.runner.local_budget import LocalSmokeBudget
from boidsnet.runner.sac_pilot import ROOT, resolve, read_json, approval_template, execute, verify_approval
from boidsnet.runner.agentport_config import worst_case_cost
from tests.test_agentport_smoke import OfflineFixtureModel
from tests.test_model import make

TEMPLATE = ROOT / 'configs/agentport_flash_local_smoke.json'


def local_config():
    config = read_json(TEMPLATE)
    config['sandbox_image_id'] = 'sha256:' + '0' * 64
    return config


class LocalPolicyTests(unittest.TestCase):
    def test_local_policy_does_not_require_or_claim_provider_cap(self):
        c = local_config(); r = resolve(c)
        self.assertEqual(r['spend_blockers'], [])
        self.assertNotIn('provider_spend_cap_cny', c)
        self.assertNotIn('pricing_confirmed', c)
        self.assertFalse(r['local_budget_policy']['provider_bill_guaranteed'])
        self.assertEqual(worst_case_cost(c), Decimal('7.2900864'))
        self.assertFalse(approval_template(r)['approved'])

    def test_local_allowances_do_not_silently_transfer_to_another_route(self):
        for key, value in [('model', 'openrouter:deepseek/deepseek-v4-flash'),
                           ('reservation_input_cny_per_million', 0.19),
                           ('max_reserved_per_request_cny', 0.11),
                           ('reservation_output_cny_per_million', float('nan')),
                           ('accepted_response_models', ['anything'])]:
            c = local_config(); c[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                resolve(c)

    def test_all_allowances_are_review_bound(self):
        r = resolve(local_config())
        a = approval_template(r) | dict(approved=True, status='APPROVED', reviewed_by='OFFLINE')
        verify_approval(r, a, True)
        changed = copy.deepcopy(r); changed['config']['max_reserved_cny'] = 7.9
        with self.assertRaises(PermissionError):
            verify_approval(changed, a, True)

    def test_too_small_total_cap_blocks_entire_schedule(self):
        c = local_config(); c['max_reserved_cny'] = 7
        self.assertIn('96-call local reservation exceeds the local cap', resolve(c)['spend_blockers'])
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(PermissionError):
            LocalSmokeBudget(c, Path(tmp) / 'ledger')


class LocalCircuitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'ledger.jsonl'
        self.c = local_config()
        self.b = LocalSmokeBudget(self.c, self.path)

    def rows(self):
        return [json.loads(line) for line in self.path.read_text().splitlines()]

    def test_exact_boundary_retains_reserve_and_stays_open(self):
        amount = (Decimal(514) * Decimal('3.2') + 10 * Decimal('8.4')) / 1000000
        self.b._reserved = Decimal(8) - amount  # low-level boundary fixture
        self.b.before('s', 'u', 10, 0)
        self.assertEqual(self.b.reserved, 8)
        self.b.after(3, 1, None, {})
        self.assertEqual(self.b.reserved, 8)  # no refund for cheap actual usage
        with self.assertRaises(PermissionError): self.b.before('s', 'u', 10, 0)
        self.b._reserved = Decimal(0)
        with self.assertRaises(PermissionError): self.b.before('s', 'u', 10, 0)
        self.assertEqual(self.b.requests, 1)
        self.assertEqual(self.b.receipt()['stop_reason'], 'money_limit')

    def test_per_request_limit_is_independent_of_total(self):
        self.b._per_request_cap = Decimal('0.001')  # exercise independent guard
        with self.assertRaises(PermissionError): self.b.before('s', 'u', 10, 0)
        self.assertEqual(self.b.requests, 0)

    def test_missing_usage_prevents_any_second_request(self):
        self.b.before('s', 'u', 10, 0)
        with self.assertRaises(PermissionError): self.b.before('s', 'u', 10, 0)
        self.assertEqual(self.b.requests, 1)
        self.assertEqual(self.b.receipt()['unreported_requests'], 1)
        self.assertEqual(self.b.receipt()['stop_reason'], 'unsettled_request')

    def test_cap_96_and_no_refund(self):
        for _ in range(96):
            self.b.before('s', 'u', 10, 0)
            self.b.after(3, 1, None, {})
        with self.assertRaises(PermissionError): self.b.before('s', 'u', 10, 0)
        self.assertEqual(self.b.requests, 96)
        self.assertEqual(len(self.rows()), 193)  # reserve+usage and circuit event

    def test_config_snapshot_cannot_be_raised_by_caller(self):
        self.c['max_reserved_cny'] = 999
        self.assertEqual(self.b.receipt()['max_reserved_cny'], 8)
        with self.assertRaises(TypeError): self.b.config['max_reserved_cny'] = 999

    def test_existing_ledger_blocks_restart_even_when_empty(self):
        with self.assertRaises(FileExistsError): LocalSmokeBudget(local_config(), self.path)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_invalid_request_and_retry_are_terminal(self):
        for args in [('s', 'u', 10, 1), ('s', 'x' * 16001, 10, 0), ('s', 'u', 4001, 0)]:
            with self.subTest(args=args[2:]), tempfile.TemporaryDirectory() as tmp:
                b = LocalSmokeBudget(local_config(), Path(tmp) / 'ledger')
                with self.assertRaises(PermissionError): b.before(*args)
                with self.assertRaises(PermissionError): b.before('s', 'u', 10, 0)
                self.assertEqual(b.requests, 0)

    def test_usage_exceeding_reserve_is_recorded_then_stops(self):
        self.b.before('s', 'u', 10, 0)
        with self.assertRaises(PermissionError): self.b.after(1000000, 10, None, {})
        with self.assertRaises(PermissionError): self.b.before('s', 'u', 10, 0)
        self.assertEqual(self.b.reported_responses, 1)
        self.assertEqual(self.rows()[-2]['event'], 'response_usage')
        self.assertEqual(self.b.receipt()['stop_reason'], 'usage_over_reserve')

    def test_invalid_or_duplicate_usage_cannot_reduce_or_double_account(self):
        self.b.before('s', 'u', 10, 0)
        self.b.after(3, 1, None, {})
        amount = self.b.receipt()['usage_cost_at_allowance']
        with self.assertRaises(PermissionError): self.b.after(3, 1, None, {})
        with self.assertRaises(PermissionError): self.b.after(-1, 1, None, {})
        self.assertEqual(self.b.receipt()['usage_cost_at_allowance'], amount)
        self.assertEqual(self.b.reported_responses, 1)

    def test_durable_write_failure_prevents_send_and_reuse(self):
        m = make([]); m.before_request = self.b.before
        m.client.chat.completions.create = mock.Mock()
        with mock.patch('boidsnet.runner.local_budget.os.fsync', side_effect=OSError('OFFLINE_DISK_FAILURE')):
            with self.assertRaises(PermissionError): m.complete('s', 'u', 0.7, 10)
        with self.assertRaises(PermissionError): m.complete('s', 'u', 0.7, 10)
        m.client.chat.completions.create.assert_not_called()
        self.assertFalse(self.b.receipt()['ledger_healthy'])

    def test_response_write_failure_opens_circuit(self):
        self.b.before('s', 'u', 10, 0)
        with mock.patch.object(self.b, '_append', side_effect=OSError('OFFLINE_DISK_FAILURE')):
            with self.assertRaises(PermissionError): self.b.after(3, 1, None, {})
        with self.assertRaises(PermissionError): self.b.before('s', 'u', 10, 0)
        self.assertFalse(self.b.receipt()['ledger_healthy'])

    def test_two_threads_cannot_reserve_concurrent_requests(self):
        barrier = threading.Barrier(2)
        def reserve():
            barrier.wait()
            try: self.b.before('s', 'u', 10, 0); return 'reserved'
            except PermissionError: return 'denied'
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: reserve(), range(2)))
        self.assertCountEqual(results, ['reserved', 'denied'])
        self.assertEqual(self.b.requests, 1)
        self.assertTrue(self.b.receipt()['circuit_open'])

    def test_reports_do_not_claim_measured_invoice_costs(self):
        self.b.before('s', 'u', 10, 0); self.b.after(3, 1, None, {})
        self.assertFalse(self.b.receipt()['provider_bill_guaranteed'])
        self.assertNotIn('cost_reported_at_uncached_rate', self.b.receipt())
        self.assertNotIn('usage_cost_at_uncached_rate', self.rows()[1])


class LocalModelStopTests(unittest.TestCase):
    def test_execute_persists_circuit_after_ambiguous_model_failure(self):
        class AmbiguousModel(OfflineFixtureModel):
            def complete(self, system, user, temperature, max_tokens):
                self.before(system, user, max_tokens, 0)
                raise TimeoutError('PRIVATE_ERROR_CANARY_MUST_NOT_BE_LOGGED')
        c = local_config()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'OFFLINE_FAILURE'
            r = resolve(c, out)
            a = approval_template(r) | dict(approved=True, status='APPROVED', reviewed_by='OFFLINE_TEST_FIXTURE')
            with mock.patch('boidsnet.runner.sandbox.isolation_level', return_value='os-docker'), \
                    mock.patch.dict('boidsnet.runner.sandbox.PROBE_REPORT', {'probe': {'image_id': c['sandbox_image_id']}}, clear=True), \
                    mock.patch('boidsnet.runner.model.OpenAICompatModel', AmbiguousModel), \
                    mock.patch('openai.OpenAI', side_effect=AssertionError('no provider SDK allowed')):
                with self.assertRaises(RuntimeError): execute(r, a, out, True)
            failed = json.loads((out / 'FAILED.json').read_text())
            self.assertTrue(failed['budget']['circuit_open'])
            self.assertEqual(failed['budget']['unreported_requests'], 1)
            self.assertEqual(failed['completed_arms'], [])
            self.assertFalse((out / 'pilot_summary.json').exists())
            self.assertNotIn('PRIVATE_ERROR_CANARY', (out / 'FAILED.json').read_text())
            ledger = [json.loads(s) for s in (out / 'request_ledger.jsonl').read_text().splitlines()]
            self.assertEqual([row['event'] for row in ledger], ['request_reserved', 'circuit_open'])

    def test_transport_failure_stops_client_without_resampling(self):
        m = make([ConnectionError('OFFLINE_FAILURE')]); m.accepted_response_models = ['fixture']
        m.MAX_ATTEMPTS = 1
        with self.assertRaises(ConnectionError): m.complete('s', 'u', 0.7, 10)
        with self.assertRaises(RuntimeError): m.complete('s', 'u', 0.7, 10)

    def test_accounting_hook_failure_stops_client(self):
        m = make([])
        m.after_response = mock.Mock(side_effect=PermissionError('OFFLINE_BUDGET_FAILURE'))
        m.client.chat.completions.create = mock.Mock(return_value=types.SimpleNamespace(
            usage=types.SimpleNamespace(prompt_tokens=3, completion_tokens=1),
            choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='fixture'))]))
        with self.assertRaises(PermissionError): m.complete('s', 'u', 0.7, 10)
        with self.assertRaises(RuntimeError): m.complete('s', 'u', 0.7, 10)
        self.assertEqual(m.client.chat.completions.create.call_count, 1)


@unittest.skipUnless(os.environ.get('BOIDS_SANDBOX') == 'docker', 'explicit offline Docker validation only')
class LocalDockerIntegrationTests(unittest.TestCase):
    def test_four_arms_under_local_only_budget(self):
        from boidsnet.runner.sandbox import isolation_level, PROBE_REPORT
        self.assertEqual(isolation_level(), 'os-docker')
        c = local_config(); c['sandbox_image_id'] = PROBE_REPORT['probe']['image_id']
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'LOCAL_OFFLINE_FIXTURE'
            r = resolve(c, out)
            a = approval_template(r) | dict(approved=True, status='APPROVED', reviewed_by='OFFLINE_TEST_FIXTURE')
            with mock.patch('boidsnet.runner.model.OpenAICompatModel', OfflineFixtureModel), \
                    mock.patch('openai.OpenAI', side_effect=AssertionError('no provider SDK allowed')):
                report = execute(r, a, out, True)
            self.assertEqual(report['status'], 'COMPLETE_DEV_DIAGNOSTIC')
            self.assertEqual(report['http_requests'], 96)  # simulated model calls
            self.assertEqual(len(report['results']), 4)
            self.assertFalse(report['budget']['circuit_open'])
            self.assertLessEqual(report['budget']['cost_reserved'], 8)
            self.assertEqual(len((out / 'request_ledger.jsonl').read_text().splitlines()), 192)
