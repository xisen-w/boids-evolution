"""One-request diagnostic guards and SDK wire shape, all fully offline."""
import copy
from decimal import Decimal
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import httpx
import openai

from boidsnet.runner.gateway_probe import first_request, resolve_probe, execute_probe
from boidsnet.runner.sac_pilot import approval_template, verify_approval
from boidsnet.runner.local_budget import LocalSmokeBudget
from boidsnet.runner.model import OpenAICompatModel
from boidsnet.runner.failure_diagnostics import failure_diagnostics
from tests.test_failure_diagnostics import bad_request
from tests.test_local_budget import local_config


class OneRequestProbeTests(unittest.TestCase):
    def test_both_prepare_entrypoints_honor_supplied_image_pin(self):
        from boidsnet.runner.gateway_probe import main as probe_main
        from boidsnet.runner.mac_smoke import main as smoke_main
        for main in (probe_main, smoke_main):
            c = local_config()
            def checked():
                self.assertEqual(os.environ['BOIDS_DOCKER_IMAGE'], c['sandbox_image_id'])
                return {'probe': {'image_id': c['sandbox_image_id']}, 'external_model_requests': 0}
            with self.subTest(entry=main.__module__), tempfile.TemporaryDirectory() as tmp, \
                    mock.patch.dict(os.environ, {}, clear=False), \
                    mock.patch('boidsnet.runner.mac_smoke.check', side_effect=checked), \
                    mock.patch('openai.OpenAI', side_effect=AssertionError('no SDK in prepare')):
                config = Path(tmp) / 'config.json'
                config.write_text(json.dumps(c))
                main(['prepare', '--config', str(config), '--out', str(Path(tmp) / 'review'),
                      '--run-out', str(Path(tmp) / 'run')])
                a = json.loads((Path(tmp) / 'review/approval.template.json').read_text())
                self.assertFalse(a['approved'])

    def test_first_request_uses_current_society_prompt_and_never_calls_sdk(self):
        with mock.patch('openai.OpenAI', side_effect=AssertionError('no SDK in prepare')):
            first = first_request(local_config())
            self.assertEqual(first, first_request(local_config()))
        from boidsnet.runner.prompts import SYSTEM
        self.assertEqual(first['system'], SYSTEM)
        self.assertIn('TARGET: NONE', first['system'])
        self.assertLessEqual(len((first['system'] + first['user']).encode()), 16000)
        self.assertEqual((first['temperature'], first['max_tokens']), (0.7, 4000))

    def test_pending_approval_and_changed_prompt_block_before_check_or_sdk(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'NO_CREATE'
            r = resolve_probe(local_config(), out)
            a = approval_template(r)
            with mock.patch('boidsnet.runner.mac_smoke.check') as check, \
                    mock.patch('openai.OpenAI') as sdk:
                with self.assertRaises(PermissionError): execute_probe(r, a, out, True)
                a.update(approved=True, status='APPROVED', reviewed_by='OFFLINE_FIXTURE')
                changed = copy.deepcopy(r); changed['first_request']['user'] += 'changed'
                with self.assertRaises(PermissionError): execute_probe(changed, a, out, True)
                check.assert_not_called(); sdk.assert_not_called()
            self.assertFalse(out.exists())

    def test_probe_approval_cannot_launch_full_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'NO_CREATE'
            r = resolve_probe(local_config(), out)
            a = approval_template(r) | dict(approved=True, status='APPROVED', reviewed_by='OFFLINE_FIXTURE')
            with self.assertRaises(PermissionError): verify_approval(r, a, True, out)

    def test_narrow_caps_are_enforced_and_expansion_is_refused(self):
        for kwargs in ({'request_limit': 97}, {'request_limit': True},
                       {'reserved_cap_cny': 9}, {'reserved_cap_cny': float('nan')},
                       {'reserved_cap_cny': 0}, {'reserved_cap_cny': True}):
            with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
                LocalSmokeBudget(local_config(), Path(tmp) / 'ledger', **kwargs)
        with tempfile.TemporaryDirectory() as tmp:
            b = LocalSmokeBudget(local_config(), Path(tmp) / 'ledger', request_limit=1, reserved_cap_cny=0.10)
            b.before('s', 'u', 4000, 0); b.after(3, 1, None, {})
            with self.assertRaises(PermissionError): b.before('s', 'u', 4000, 0)
            self.assertEqual(b.receipt()['max_http_requests'], 1)
            self.assertEqual(b.receipt()['max_reserved_cny'], 0.10)
            self.assertEqual(b.requests, 1)

    def test_failure_has_one_reservation_and_no_retry_or_reuse(self):
        class RejectedModel:
            calls = 0
            def __init__(self, *args, **kwargs): self.before = kwargs['before_request']
            def complete(self, system, user, temperature, max_tokens):
                self.before(system, user, max_tokens, 0)
                RejectedModel.calls += 1
                raise bad_request({'error': {'code': 'unsupported_parameter', 'param': 'thinking'}})
        c = local_config()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'OFFLINE_PROBE'
            r = resolve_probe(c, out)
            a = approval_template(r) | dict(approved=True, status='APPROVED', reviewed_by='OFFLINE_FIXTURE')
            with mock.patch('boidsnet.runner.mac_smoke.check'), \
                    mock.patch.dict('boidsnet.runner.sandbox.PROBE_REPORT', {'probe': {'image_id': c['sandbox_image_id']}}, clear=True), \
                    mock.patch.dict(os.environ, {'BOIDS_PARTNER_API_KEY': 'OFFLINE_FAKE'}), \
                    mock.patch('boidsnet.runner.model.OpenAICompatModel', RejectedModel):
                with self.assertRaises(RuntimeError): execute_probe(r, a, out, True)
                with self.assertRaises(FileExistsError): execute_probe(r, a, out, True)
            f = json.loads((out / 'FAILED.json').read_text())
            self.assertEqual(f['diagnostic']['provider_params'], ['thinking'])
            self.assertEqual(f['budget']['http_requests'], 1)
            self.assertEqual(RejectedModel.calls, 1)
            request = r['first_request']
            input_bound = len((request['system'] + request['user']).encode()) + 512
            expected = (Decimal(input_bound) * Decimal('3.2') +
                        Decimal(request['max_tokens']) * Decimal('8.4')) / Decimal(1000000)
            self.assertEqual(Decimal(f['budget']['cost_reserved_exact']), expected)
            self.assertFalse((out / 'probe_summary.json').exists())

    def test_actual_sdk_serialization_is_inspected_without_network(self):
        sent = []
        def handler(request):
            sent.append(request)
            return httpx.Response(400, json={'error': {'code': 'unrecognized_request_argument',
                                  'param': 'reasoning_effort', 'message': 'PRIVATE'}},
                                  headers={'x-request-id': '0123456789abcdef0123456789abcdef'})
        offline = openai.OpenAI(api_key='OFFLINE_FAKE', base_url='https://example.invalid/v1',
                               max_retries=0, http_client=httpx.Client(transport=httpx.MockTransport(handler)))
        with mock.patch('boidsnet.runner.sandbox.isolation_level', return_value='os-docker'), \
                mock.patch.dict(os.environ, {'BOIDS_PARTNER_API_KEY': 'OFFLINE_FAKE', 'BOIDS_SANDBOX': 'docker'}), \
                mock.patch('openai.OpenAI', return_value=offline):
            m = OpenAICompatModel('azure:DeepSeek-V4-Flash', 'BOIDS_PARTNER_API_KEY', True,
                base_url='https://agentport.world/v1', thinking='disabled', max_attempts=1,
                accepted_response_models=['DeepSeek-V4-Flash'], request_timeout_s=90)
            with self.assertRaises(openai.BadRequestError) as caught:
                m.complete(**first_request(local_config()))
            self.assertEqual(failure_diagnostics(caught.exception)['provider_params'], ['reasoning_effort'])
            with self.assertRaises(RuntimeError): m.complete('s', 'u', 0.7, 4000)
        self.assertEqual(len(sent), 1)
        request = sent[0]
        payload = json.loads(request.content)
        self.assertEqual(request.url.path, '/v1/chat/completions')
        self.assertFalse(request.url.query)
        self.assertNotIn('thinking', payload)
        self.assertEqual(payload['reasoning_effort'], 'none')
        self.assertNotIn('extra_body', payload)
        self.assertEqual(payload['max_tokens'], 4000)
        self.assertEqual(payload['temperature'], 0.7)
        offline.close()


if __name__ == '__main__':
    unittest.main()
