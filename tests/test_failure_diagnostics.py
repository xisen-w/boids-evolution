"""Offline diagnostic regressions. No provider requests or real credentials."""
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

import httpx
import openai

from boidsnet.runner.failure_diagnostics import failure_diagnostics
from boidsnet.runner.sac_pilot import resolve, approval_template, execute
from boidsnet.runner.society import Society
from boidsnet.runner.config import RunConfig
from boidsnet.runner.env_adapter import MechEnv
from boidsnet.runner.run import DEFAULT_ENV
from tests.test_local_budget import local_config
from tests.test_agentport_smoke import OfflineFixtureModel
from tests.test_model import make


def bad_request(body, request_id='01234567-89ab-cdef-0123-456789abcdef'):
    response = httpx.Response(400, request=httpx.Request('POST', 'https://example.invalid/v1/chat/completions'),
                              headers={'x-request-id': request_id}, json=body)
    return openai.BadRequestError('PRIVATE_EXCEPTION_TEXT_NOT_FOR_LOGS', response=response, body=body)


class SafeFailureTests(unittest.TestCase):
    def test_nested_gateway_json_yields_code_parameter_and_request_id(self):
        exc = bad_request({'error': {'message': json.dumps({'error': {
            'code': 'unrecognized_request_argument', 'param': 'thinking',
            'message': 'Unrecognized request argument supplied: thinking'}})}})
        d = failure_diagnostics(exc)
        self.assertEqual(d['provider_codes'], ['unrecognized_request_argument'])
        self.assertEqual(d['provider_params'], ['thinking'])
        self.assertIn('thinking', d['message_parameter_mentions'])
        self.assertEqual(d['message_hints'], ['unknown_request_parameter'])
        self.assertEqual(d['request_ids'], ['01234567-89ab-cdef-0123-456789abcdef'])
        self.assertFalse(d['raw_error_retained'])

    def test_secret_and_arbitrary_prose_are_not_persisted(self):
        canary = 'sk_sm_OFFLINE_CREDENTIAL_CANARY'
        body = {'error': {'code': canary, 'param': canary,
                         'message': 'PRIVATE_PROMPT_CANARY Bearer ' + canary},
                'headers': {'Authorization': canary}}
        with mock.patch.dict(os.environ, {'BOIDS_PARTNER_API_KEY': canary}):
            d = failure_diagnostics(bad_request(body, 'req_' + canary))
        text = json.dumps(d)
        for forbidden in (canary, 'PRIVATE_PROMPT', 'Bearer', 'PRIVATE_EXCEPTION', 'Authorization'):
            self.assertNotIn(forbidden, text)
        self.assertEqual(d['request_ids'], [])
        self.assertTrue(d['unknown_code_omitted'])

    def test_known_secret_echo_as_uuid_id_is_rejected(self):
        secret = '0123456789abcdef0123456789abcdef'
        with mock.patch.dict(os.environ, {'BOIDS_PARTNER_API_KEY': secret}):
            self.assertEqual(failure_diagnostics(bad_request({}, secret))['request_ids'], [])

    def test_unknown_and_oversize_errors_fail_closed(self):
        for body in (None, ['arbitrary'], {'message': 'x' * 16385}, {'message': 'PRIVATE'}):
            with self.subTest(body_type=type(body).__name__):
                d = failure_diagnostics(bad_request(body))
                self.assertEqual(d['classification'], 'unclassified_error')
                self.assertNotIn('PRIVATE', json.dumps(d))

    def test_diagnostic_attribute_error_cannot_mask_original_exception(self):
        class Hostile(Exception):
            @property
            def body(self):
                raise ValueError('SECRET')
        d = failure_diagnostics(Hostile())
        self.assertTrue(d['diagnostic_extraction_failed'])

    def test_parameter_mention_is_not_promoted_to_causal_param(self):
        d = failure_diagnostics(bad_request({'message': 'The model supports thinking but temperature is invalid.'}))
        self.assertEqual(d['provider_params'], [])
        self.assertEqual(d['message_parameter_mentions'], ['model', 'temperature', 'thinking'])

    def test_error_and_ledger_survive_real_sdk_exception_without_network(self):
        class RejectedModel(OfflineFixtureModel):
            def complete(self, system, user, temperature, max_tokens):
                self.before(system, user, max_tokens, 0)
                raise bad_request({'error': {'code': 'unsupported_parameter', 'param': 'thinking',
                                            'message': 'PRIVATE_ERROR_CANARY'}})
        c = local_config()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'OFFLINE_DIAGNOSTIC'
            r = resolve(c, out)
            a = approval_template(r) | dict(approved=True, status='APPROVED', reviewed_by='OFFLINE_TEST_FIXTURE')
            with mock.patch('boidsnet.runner.sandbox.isolation_level', return_value='os-docker'), \
                    mock.patch.dict('boidsnet.runner.sandbox.PROBE_REPORT', {'probe': {'image_id': c['sandbox_image_id']}}, clear=True), \
                    mock.patch('boidsnet.runner.model.OpenAICompatModel', RejectedModel), \
                    mock.patch('openai.OpenAI', side_effect=AssertionError('no provider SDK allowed')):
                with self.assertRaises(RuntimeError):
                    execute(r, a, out, True)
            raw = (out / 'FAILED.json').read_text()
            failed = json.loads(raw)
            self.assertEqual(failed['diagnostic']['provider_params'], ['thinking'])
            self.assertEqual(failed['http_requests'], 1)
            self.assertTrue(failed['budget']['circuit_open'])
            self.assertNotIn('PRIVATE', raw)
            prompts = list((out / 'ENG_000_s1001/prompts').glob('*.json'))
            self.assertEqual(len(prompts), 1)
            prompt = json.loads(prompts[0].read_text())
            self.assertEqual(prompt['status'], 'REQUEST_PREPARED')
            self.assertIsNone(prompt['response'])
            self.assertTrue(prompt['system'] and prompt['user'])

    def test_missing_usage_attribute_stops_before_second_reservation(self):
        m = make([])
        m.before_request = mock.Mock()
        m.client.chat.completions.create = mock.Mock(return_value=types.SimpleNamespace())
        for _ in range(2):
            with self.assertRaises(RuntimeError):
                m.complete('s', 'u', 0.7, 10)
        self.assertEqual(m.before_request.call_count, 1)


if __name__ == '__main__':
    unittest.main()
