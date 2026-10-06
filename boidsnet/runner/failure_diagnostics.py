"""Allowlisted provider diagnostics; never persist raw messages or headers.

Gateway errors can wrap upstream JSON inside a message string. Inspect that
bounded structure in memory, but emit only controlled codes/parameter names
and well-formed request IDs. Unknown prose is deliberately not logged.
"""
import json
import os
import re


_CODES = frozenset({
    'invalid_request_error', 'invalid_request', 'bad_request', 'badrequest',
    'unsupported_parameter', 'unsupported_value', 'invalid_parameter',
    'invalid_value', 'unrecognized_request_argument', 'unknown_parameter',
    'model_not_found', 'deploymentnotfound', 'deployment_not_found',
    'permission_denied', 'authentication_error', 'invalid_api_key',
    'insufficient_quota', 'rate_limit_exceeded', 'rate_limit_error',
    'content_filter', 'content_policy_violation', 'context_length_exceeded',
    'upstream_error', 'provider_error', 'routing_error', 'no_available_provider',
    'unsupported_model', 'model_not_allowed', 'invalid_model',
})
_PARAMS = frozenset({
    'model', 'messages', 'temperature', 'top_p', 'max_tokens',
    'max_completion_tokens', 'thinking', 'thinking.type', 'reasoning_effort',
    'stream', 'response_format', 'tools', 'tool_choice', 'seed', 'stop', 'n',
    'frequency_penalty', 'presence_penalty', 'extra_body',
})
_HINTS = (
    (r'unrecognized request argument|unknown (?:request )?(?:argument|parameter|field)|'
     r'extra (?:inputs|fields) are not permitted', 'unknown_request_parameter'),
    (r'unsupported (?:parameter|argument)|(?:parameter|argument).*?not supported|'
     r'does not support', 'unsupported_parameter_or_value'),
    (r'invalid (?:parameter|argument|value)|not a valid|must be (?:one of|between|greater|less)',
     'invalid_parameter_or_value'),
    (r'model.*?not (?:found|available|allowed)|deployment.*?not (?:found|exist)',
     'model_or_deployment_unavailable'),
    (r'context (?:length|window)|maximum context', 'context_limit'),
    (r'content (?:filter|policy)', 'content_policy'),
    (r'insufficient (?:quota|balance)|budget.*?exceed', 'quota_or_budget'),
)
_REQUEST_ID = re.compile(
    r'(?:[0-9a-fA-F]{32}|[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}'
    r'|req_[A-Za-z0-9_-]{8,96})\Z')


def _safe_request_id(value):
    if not isinstance(value, str) or not _REQUEST_ID.fullmatch(value):
        return None
    low = value.lower()
    secret = os.environ.get('BOIDS_PARTNER_API_KEY')
    if 'sk_' in low or 'sk-' in low or 'bearer' in low or (secret and secret in value):
        return None
    return value


def failure_diagnostics(exc):
    """Best-effort, bounded, non-throwing metadata extraction from an SDK error.

    A message mentioning a parameter is NOT proof that parameter caused the
    failure: keep message mentions separate from the provider's `param` field.
    """
    result = {'schema': 'safe-provider-error-v1', 'raw_error_retained': False}
    try:
        status = getattr(exc, 'status_code', None)
        if type(status) is int and 100 <= status <= 599:
            result['http_status'] = status
        codes, params, mentioned, hints = set(), set(), set(), set()
        request_ids = set()
        unknown_code = False
        pending = [(getattr(exc, 'body', None), 0)]
        for attr in ('code', 'type', 'param'):
            value = getattr(exc, attr, None)
            if value is not None:
                pending.append(({attr: value}, 0))
        response = getattr(exc, 'response', None)
        if response is not None:
            headers = getattr(response, 'headers', {})
            # Read only these correlation headers, never serialize the mapping.
            for name in ('x-request-id', 'apim-request-id', 'x-ms-request-id'):
                value = _safe_request_id(headers.get(name))
                if value:
                    request_ids.add(value)
        value = _safe_request_id(getattr(exc, 'request_id', None))
        if value:
            request_ids.add(value)
        inspected = 0
        while pending and inspected < 32:
            node, depth = pending.pop()
            inspected += 1
            if depth > 6:
                continue
            if isinstance(node, dict):
                for key in ('code', 'type'):
                    value = node.get(key)
                    if isinstance(value, str):
                        if value.lower() in _CODES:
                            codes.add(value.lower())
                        else:
                            unknown_code = True
                if isinstance(node.get('param'), str) and node['param'] in _PARAMS:
                    params.add(node['param'])
                for key in ('error', 'message', 'detail', 'innererror', 'inner_error'):
                    if key in node:
                        pending.append((node[key], depth + 1))
            elif isinstance(node, str):
                if len(node) > 16384:
                    result['oversize_error_omitted'] = True
                    continue
                try:
                    decoded = json.loads(node)
                except (ValueError, RecursionError):
                    decoded = None
                if isinstance(decoded, dict):
                    pending.append((decoded, depth + 1))
                else:
                    # Fixed hints and exact known parameter names, no snippets.
                    low = node.lower()
                    for pattern, label in _HINTS:
                        if re.search(pattern, low):
                            hints.add(label)
                    for param in _PARAMS:
                        if re.search(r'(?<![a-z0-9_.])' + re.escape(param) + r'(?![a-z0-9_.])', low):
                            mentioned.add(param)
        result.update(provider_codes=sorted(codes), provider_params=sorted(params),
                      message_parameter_mentions=sorted(mentioned), message_hints=sorted(hints),
                      request_ids=sorted(request_ids), unknown_code_omitted=unknown_code)
        result['classification'] = 'provider_error_metadata' if codes or params or hints else 'unclassified_error'
    except Exception:
        # Diagnostics must never mask the original failure or cause a retry.
        result['diagnostic_extraction_failed'] = True
    return result
