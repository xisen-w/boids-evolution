"""Versioned AgentPort smoke policies: verified billing or explicit local allowances."""
import math
import re
from decimal import Decimal

VERSION = 'sac-agentport-smoke-v1'
LOCAL_VERSION = 'sac-agentport-local-smoke-v2'
STAGE_B_VERSION = 'sac-agentport-stage-b-v1'
AGENTPORT_BASE_URL = 'https://agentport.world/v1'
# Explicit provider pins returned by the gateway catalog. Bare aliases and
# moving "latest" routes are not interchangeable with a reproducible model.
AGENTPORT_FLASH_MODELS = frozenset({
    'azure:DeepSeek-V4-Flash',
    'azure:DeepSeek-V4-Flash-0731',
    'openrouter:deepseek/deepseek-v4-flash',
    'openrouter:deepseek/deepseek-v4-flash-0731',
})
EXTRA_KEYS = {'max_reserved_cny', 'input_cny_per_million', 'output_cny_per_million',
              'pricing_confirmed', 'pricing_reference', 'provider_spend_cap_cny',
              'accepted_response_models', 'sandbox_image_id', 'request_timeout_s'}
USD_KEYS = {'max_reserved_usd', 'input_usd_per_million', 'output_usd_per_million'}
LOCAL_EXTRA_KEYS = {'max_reserved_cny', 'reservation_input_cny_per_million',
                    'reservation_output_cny_per_million', 'reservation_basis',
                    'max_reserved_per_request_cny', 'accepted_response_models',
                    'sandbox_image_id', 'request_timeout_s'}


def is_agentport(config):
    return config.get('version') in (VERSION, LOCAL_VERSION, STAGE_B_VERSION)


def is_local_budget(config):
    return config.get('version') in (LOCAL_VERSION, STAGE_B_VERSION)


def is_stage_b(config):
    return config.get('version') == STAGE_B_VERSION


def extra_keys(config):
    keys = LOCAL_EXTRA_KEYS if is_local_budget(config) else EXTRA_KEYS
    return keys | {'arm_order'} if is_stage_b(config) else keys


def thinking_request_body(model, base_url, thinking):
    """Separate experimental intent from provider-specific wire parameters.

    Azure Foundry rejects the DeepSeek-native `thinking` object. Request off
    via OpenAI-style reasoning_effort instead; do not silently drop the intent
    or retry with a different setting if the deployment rejects it.
    """
    if thinking is None:
        return {}
    if base_url == AGENTPORT_BASE_URL and model.startswith('azure:'):
        if thinking != 'disabled':
            raise ValueError('the Azure smoke mapping only supports requested-off reasoning')
        return {'reasoning_effort': 'none'}
    return {'thinking': {'type': thinking}}


def blockers(config):
    if is_local_budget(config):
        return local_blockers(config)
    missing = []
    if config['pricing_confirmed'] is not True or not config['pricing_reference'].strip():
        missing.append('gateway pricing not confirmed')
    for key in ('input_cny_per_million', 'output_cny_per_million'):
        n = config[key]
        if type(n) not in (int, float) or not math.isfinite(n) or n <= 0:
            missing.append(key + ' must be a verified positive CNY rate')
    n = config['provider_spend_cap_cny']
    if type(n) not in (int, float) or not math.isfinite(n) or not 0 < n <= config['max_reserved_cny']:
        missing.append('a separate provider-side key cap no greater than the smoke budget is unconfirmed')
    if not config['accepted_response_models']:
        missing.append('accepted response model IDs not confirmed')
    if not config['sandbox_image_id']:
        missing.append('Docker image ID not pinned')
    if not missing:
        # Reserve for the reviewed input ceiling on every call; never launch a
        # schedule whose declared worst case is already outside either cap.
        bound = worst_case_cost(config)
        if bound > min(Decimal(str(config['max_reserved_cny'])), Decimal(str(config['provider_spend_cap_cny']))):
            missing.append('96-call worst-case reserve exceeds the client or provider cap')
    return missing


def worst_case_cost(config):
    keys = ('reservation_input_cny_per_million', 'reservation_output_cny_per_million') if is_local_budget(config) else ('input_cny_per_million', 'output_cny_per_million')
    rate_in, rate_out = (Decimal(str(config[k])) for k in keys)
    build = len(config['arms']) * len(config['seeds']) * config['n_agents'] * config['n_rounds']
    solve = len(config['arms']) * len(config['seeds']) * 3 * config['eval_tasks_per_depth'] * config['solver_attempts']
    extra = max(0, config['max_http_requests'] - build - solve)
    return ((build + solve + extra) * (config['max_input_bytes'] + 512) * rate_in
            + ((build + extra) * config['builder_max_tokens'] + solve * config['solver_max_tokens']) * rate_out) / Decimal(1000000)


def local_blockers(config):
    missing = []
    for key in ('reservation_input_cny_per_million', 'reservation_output_cny_per_million'):
        value = config[key]
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            missing.append(key + ' must be a positive local accounting allowance')
    if not isinstance(config['reservation_basis'], str) or not config['reservation_basis'].strip():
        missing.append('local allowance basis must be disclosed')
    if not config['accepted_response_models']:
        missing.append('expected response model allowlist is empty')
    if not config['sandbox_image_id']:
        missing.append('Docker image ID not pinned')
    if not missing:
        if worst_case_cost(config) > Decimal(str(config['max_reserved_cny'])):
            missing.append(('full-schedule' if is_stage_b(config) else '96-call') + ' local reservation exceeds the local cap')
        per_call = ((config['max_input_bytes'] + 512) * Decimal(str(config['reservation_input_cny_per_million']))
                    + config['builder_max_tokens'] * Decimal(str(config['reservation_output_cny_per_million']))) / Decimal(1000000)
        if per_call > Decimal(str(config['max_reserved_per_request_cny'])):
            missing.append('builder local reservation exceeds the per-request cap')
    return missing


def validate(config):
    stage = is_stage_b(config)
    for key, want in {'base_url': AGENTPORT_BASE_URL, 'thinking': 'disabled',
                     'n_agents': 8 if stage else 4, 'n_rounds': 12 if stage else 3, 'eval_tasks_per_depth': 2,
                     'solver_attempts': 2, 'max_http_attempts_per_call': 1,
                     'max_http_requests': 432 if stage else 96, 'builder_max_tokens': 4000,
                     'solver_max_tokens': 1500, 'max_input_bytes': 32768 if stage else 16000}.items():
        if config[key] != want:
            raise ValueError(key + ' differs from the fixed ' + ('stage B' if stage else 'smoke') + ' contract')
    if stage and (config['arms'] != ['000', '100', '011', '111'] or config['seeds'] != [2001]
                  or config['arm_order'] != ['011', '100', '111', '000']):
        raise ValueError('stage B requires the reviewed four arms, order and seed 2001')
    if not isinstance(config['model'], str) or config['model'] not in AGENTPORT_FLASH_MODELS:
        raise ValueError('explicit catalog-listed AgentPort DeepSeek Flash provider pin required')
    limit = 60 if stage else 8
    if type(config['max_reserved_cny']) not in (int, float) or not 0 < config['max_reserved_cny'] <= limit:
        raise ValueError('this launcher allows at most CNY ' + str(limit))
    if type(config['request_timeout_s']) not in (int, float) or not 1 <= config['request_timeout_s'] <= 90:
        raise ValueError('request deadline must be at most 90 seconds')
    ids = config['accepted_response_models']
    if not isinstance(ids, list) or any(not isinstance(s, str) or not s.strip() for s in ids):
        raise ValueError('accepted_response_models must be a list of nonempty IDs')
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate response model ID')
    if is_local_budget(config):
        # These are reviewed LOCAL allowances, not a claimed provider quote or
        # an exchange rate. Pin this small engineering launch to the checked route.
        if config['model'] != 'azure:DeepSeek-V4-Flash':
            raise ValueError('local allowance smoke is pinned to azure:DeepSeek-V4-Flash')
        for key, want in {'reservation_input_cny_per_million': 3.2,
                          'reservation_output_cny_per_million': 8.4,
                          'max_reserved_per_request_cny': 0.15 if stage else 0.10}.items():
            if type(config[key]) not in (int, float) or config[key] != want:
                raise ValueError(key + ' differs from the local allowance contract')
        if set(ids) != {'azure:DeepSeek-V4-Flash', 'DeepSeek-V4-Flash'}:
            raise ValueError('local smoke requires the two explicitly expected response IDs')
    elif type(config['pricing_confirmed']) is not bool or not isinstance(config['pricing_reference'], str):
        raise ValueError('invalid pricing confirmation')
    pin = config['sandbox_image_id']
    if pin is not None and (not isinstance(pin, str) or not re.fullmatch(r'sha256:[0-9a-f]{64}', pin)):
        raise ValueError('sandbox image must be an immutable image ID')
