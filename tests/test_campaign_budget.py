"""Offline cross-run cap, lock, provenance, and fail-closed integration checks."""
import copy
from decimal import Decimal
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from boidsnet.runner.campaign_budget import CampaignBudget, digest
from boidsnet.runner.local_budget import LocalSmokeBudget
from boidsnet.runner.sac_pilot import resolve, approval_template, execute
from tests.test_local_budget import local_config
from tests.test_agentport_smoke import OfflineFixtureModel


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'campaign'
        self.config = local_config()
        self.config['max_reserved_cny'] = 7.5
        self.auth = {'status': 'USER_AUTHORIZED_BOUNDED_REPAIR_CAMPAIGN',
                     'max_reserved_cny': 7.5, 'individually_confirm_each_run': False,
                     'user_confirmation': 'OFFLINE_FIXTURE_NOT_AUTHORIZATION',
                     'root': str(self.root), 'config': self.config}
        CampaignBudget.initialize(self.root, self.auth)

    def bound(self, name):
        b = CampaignBudget(self.root, self.auth)
        b.bind_run(resolve(self.config, self.root / name))
        return b

    def amendment(self, b, cap=30):
        return {'status': 'USER_AUTHORIZED_CUMULATIVE_BUDGET_INCREASE',
                'user_confirmation': 'OFFLINE_FIXTURE_EXPLICIT_NEW_CAP',
                'root': str(b.root), 'base_authorization_sha256': digest(self.auth),
                'prior_ledger_sha256': b.rows[-1]['sha256'],
                'previous_cap_cny': str(b.cap), 'prior_reserved_cny': str(b.reserved),
                'max_reserved_cny': cap}

    def test_explicit_extension_preserves_spending_history_and_reopens_only_budget_stop(self):
        with self.bound('first') as b:
            for _ in range(75): b.reserve('0.10')
            with self.assertRaises(PermissionError): b.reserve('0.01')
        before = (self.root / 'ledger.jsonl').read_bytes()
        with CampaignBudget(self.root, self.auth) as b:
            a = self.amendment(b)
            b.extend_budget(a)
            self.assertEqual(b.reserved, Decimal('7.50'))
            self.assertEqual(b.requests, 75)
            self.assertEqual(b.cap, Decimal('30'))
            self.assertFalse(b.closed)
            with self.assertRaises(PermissionError): b.extend_budget(a)
        self.assertTrue((self.root / 'ledger.jsonl').read_bytes().startswith(before))
        with self.bound('second') as b:
            for _ in range(225): b.reserve('0.10')
            self.assertEqual(b.reserved, Decimal('30.00'))
            with self.assertRaises(PermissionError): b.reserve('0.01')
        with CampaignBudget(self.root, self.auth) as b:
            self.assertTrue(b.closed)
            self.assertEqual(b.requests, 300)
            self.assertEqual(b.receipt()['remaining_cny'], '0.00')

    def test_amendment_requires_pinned_confirmation_and_finite_larger_cap(self):
        with CampaignBudget(self.root, self.auth) as b:
            original = self.amendment(b)
            for key, value in [('status', ''), ('user_confirmation', ''),
                               ('root', '/wrong'), ('prior_ledger_sha256', 'wrong'),
                               ('previous_cap_cny', '1'), ('prior_reserved_cny', '1'),
                               ('base_authorization_sha256', 'wrong'),
                               ('max_reserved_cny', 'NaN'), ('max_reserved_cny', 'Infinity'),
                               ('max_reserved_cny', 'invalid'), ('max_reserved_cny', True),
                               ('max_reserved_cny', 7.5), ('max_reserved_cny', 0)]:
                with self.subTest(key=key, value=value), self.assertRaises(PermissionError):
                    b.extend_budget(dict(original, **{key: value}))
            self.assertEqual(len(b.rows), 1)

    def test_active_or_successfully_finished_run_cannot_be_extended(self):
        with self.bound('first') as b:
            b.reserve('0.05')
            with self.assertRaises(PermissionError): b.extend_budget(self.amendment(b))
            b.finish()
            with self.assertRaises(PermissionError): b.reserve('0.01')
        with CampaignBudget(self.root, self.auth) as b:
            self.assertTrue(b.closed)
            self.assertEqual(b.closed_reason, 'smoke_complete')
            with self.assertRaises(PermissionError): b.extend_budget(self.amendment(b))
            with self.assertRaises(PermissionError): b.bind_run(resolve(self.config, self.root / 'second'))

    def test_reopen_accumulates_and_exact_ceiling_sticks(self):
        with self.bound('first') as b:
            for _ in range(40):
                b.reserve(Decimal('0.10'))
        with self.bound('second') as b:
            self.assertEqual(b.receipt()['reserved_cny'], '4.00')
            for _ in range(35):
                b.reserve(Decimal('0.10'))
            self.assertEqual(b.receipt()['remaining_cny'], '0.00')
            with self.assertRaises(PermissionError):
                b.reserve(Decimal('0.001'))
            self.assertEqual(b.closed_reason, 'budget_limit')
        with CampaignBudget(self.root, self.auth) as b:
            self.assertTrue(b.closed)
            with self.assertRaises(PermissionError):
                b.bind_run(resolve(self.config, self.root / 'third'))
            self.assertEqual(b.requests, 75)

    def test_nonconcurrent_exclusive_lock(self):
        with self.bound('first'):
            with self.assertRaises(BlockingIOError):
                CampaignBudget(self.root, self.auth)

    def test_failed_amendment_write_cannot_be_mistaken_for_budget_stop(self):
        with CampaignBudget(self.root, self.auth) as b:
            amendment = self.amendment(b)
            with mock.patch('boidsnet.runner.campaign_budget.os.fsync', side_effect=OSError('fixture fsync')):
                with self.assertRaises(OSError): b.extend_budget(amendment)
            self.assertTrue(b.closed)
            self.assertEqual(b.closed_reason, 'ledger_failure')
            self.assertEqual(b.cap, Decimal('7.5'))
            with self.assertRaises(PermissionError): b.extend_budget(amendment)

    def test_deleted_or_corrupt_ledger_never_resets(self):
        ledger = self.root / 'ledger.jsonl'
        ledger.write_text(ledger.read_text() + '{partial')
        with self.assertRaises(ValueError): CampaignBudget(self.root, self.auth)
        ledger.unlink()
        with self.assertRaises(FileNotFoundError): CampaignBudget(self.root, self.auth)
        with self.assertRaises(FileExistsError): CampaignBudget.initialize(self.root, self.auth)

    def test_authorization_config_and_output_scope_are_pinned(self):
        auth = copy.deepcopy(self.auth)
        auth['config']['model'] = 'unauthorized-model'
        with self.assertRaises((PermissionError, ValueError)): CampaignBudget(self.root, auth)
        with CampaignBudget(self.root, self.auth) as b:
            changed = resolve(self.config, self.root / 'first')
            changed['config']['n_rounds'] = 2
            with self.assertRaises(PermissionError): b.bind_run(changed)
            with self.assertRaises(PermissionError): b.bind_run(resolve(self.config, self.root.parent / 'outside'))

    def test_sticky_local_failure_does_not_refund_campaign(self):
        with self.bound('first') as b:
            local = LocalSmokeBudget(self.config, self.root / 'local.jsonl', campaign=b)
            with mock.patch.object(local, '_append', side_effect=OSError('OFFLINE_DISK_FAILURE')):
                with self.assertRaises(PermissionError): local.before('s', 'u', 4000, 0)
            self.assertEqual(b.requests, 1)
            amount = b.reserved
            self.assertGreater(amount, 0)
        with self.bound('second') as b:
            self.assertEqual(b.reserved, amount)

    def test_campaign_refusal_prevents_local_reservation(self):
        with self.bound('first') as b:
            for _ in range(75): b.reserve(Decimal('0.10'))
            local = LocalSmokeBudget(self.config, self.root / 'local.jsonl', campaign=b)
            with self.assertRaises(PermissionError): local.before('s', 'u', 4000, 0)
            self.assertEqual(local.requests, 0)
            self.assertEqual(local.receipt()['stop_reason'], 'campaign_refusal')

    def test_rebinding_same_run_and_corrupt_hash_denied(self):
        resolved = resolve(self.config, self.root / 'first')
        with CampaignBudget(self.root, self.auth) as b: b.bind_run(resolved)
        with CampaignBudget(self.root, self.auth) as b:
            with self.assertRaises(PermissionError): b.bind_run(resolved)
        ledger = self.root / 'ledger.jsonl'
        rows = [json.loads(line) for line in ledger.read_text().splitlines()]
        rows[0]['max_reserved_cny'] = '9'
        ledger.write_text('\n'.join(json.dumps(row) for row in rows) + '\n')
        with self.assertRaises(PermissionError): CampaignBudget(self.root, self.auth)


@unittest.skipUnless(os.environ.get('BOIDS_SANDBOX') == 'docker', 'explicit Docker offline validation only')
class CampaignDockerTests(unittest.TestCase):
    def test_four_arms_share_global_and_local_reservations(self):
        from boidsnet.runner.sandbox import isolation_level, PROBE_REPORT
        self.assertEqual(isolation_level(), 'os-docker')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'campaign'
            config = local_config()
            config.update(max_reserved_cny=7.5, sandbox_image_id=PROBE_REPORT['probe']['image_id'])
            auth = {'status': 'USER_AUTHORIZED_BOUNDED_REPAIR_CAMPAIGN',
                    'max_reserved_cny': 7.5, 'individually_confirm_each_run': False,
                    'user_confirmation': 'OFFLINE_FIXTURE_NOT_AUTHORIZATION',
                    'root': str(root), 'config': config}
            CampaignBudget.initialize(root, auth)
            out = root / 'OFFLINE_RUN'
            resolved = resolve(config, out)
            approval = approval_template(resolved) | dict(approved=True, status='APPROVED', reviewed_by='OFFLINE_FIXTURE')
            with CampaignBudget(root, auth) as campaign, \
                    mock.patch('boidsnet.runner.model.OpenAICompatModel', OfflineFixtureModel), \
                    mock.patch('openai.OpenAI', side_effect=AssertionError('NO_EXTERNAL_PROVIDER')):
                report = execute(resolved, approval, out, True, campaign=campaign)
                self.assertEqual(report['status'], 'COMPLETE_DEV_DIAGNOSTIC')
                self.assertEqual(campaign.requests, 96)
                self.assertEqual(Decimal(report['budget']['cost_reserved_exact']), campaign.reserved)
                self.assertEqual(report['budget']['campaign'], campaign.receipt())
            with CampaignBudget(root, auth) as reopened:
                self.assertEqual(reopened.requests, 96)


if __name__ == '__main__':
    unittest.main()
