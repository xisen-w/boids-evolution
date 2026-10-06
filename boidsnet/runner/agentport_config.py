"""Explicit AgentPort smoke contract. Unknown billing always blocks spending."""
import math
import re
from decimal import Decimal

VERSION = 'sac-agentport-smoke-v1'
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


def is_agentport(config):
    return config.get('version') == VERSION


def blockers(config):
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
    rate_in, rate_out = (Decimal(str(config[k])) for k in ('input_cny_per_million', 'output_cny_per_million'))
    return (96 * (config['max_input_bytes'] + 512) * rate_in
            + 48 * (config['builder_max_tokens'] + config['solver_max_tokens']) * rate_out) / Decimal(1000000)


def validate(config):
    for key, want in {'base_url': AGENTPORT_BASE_URL, 'thinking': 'disabled',
                     'n_agents': 4, 'n_rounds': 3, 'eval_tasks_per_depth': 2,
                     'solver_attempts': 2, 'max_http_attempts_per_call': 1,
                     'max_http_requests': 96, 'builder_max_tokens': 4000,
                     'solver_max_tokens': 1500, 'max_input_bytes': 16000}.items():
        if config[key] != want:
            raise ValueError(key + ' differs from the fixed smoke contract')
    if not isinstance(config['model'], str) or config['model'] not in AGENTPORT_FLASH_MODELS:
        raise ValueError('explicit catalog-listed AgentPort DeepSeek Flash provider pin required')
    if type(config['max_reserved_cny']) not in (int, float) or not 0 < config['max_reserved_cny'] <= 8:
        raise ValueError('this smoke launcher allows at most CNY 8')
    if type(config['request_timeout_s']) not in (int, float) or not 1 <= config['request_timeout_s'] <= 90:
        raise ValueError('request deadline must be at most 90 seconds')
    ids = config['accepted_response_models']
    if not isinstance(ids, list) or any(not isinstance(s, str) or not s.strip() for s in ids):
        raise ValueError('accepted_response_models must be a list of nonempty IDs')
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate response model ID')
    if type(config['pricing_confirmed']) is not bool or not isinstance(config['pricing_reference'], str):
        raise ValueError('invalid pricing confirmation')
    pin = config['sandbox_image_id']
    if pin is not None and (not isinstance(pin, str) or not re.fullmatch(r'sha256:[0-9a-f]{64}', pin)):
        raise ValueError('sandbox image must be an immutable image ID')
