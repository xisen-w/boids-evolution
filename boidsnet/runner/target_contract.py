"""Versioned, declared DEV task invocation; never infer targets from outcomes.

The default remains the historical no-kwargs contract. New runs explicitly
opt in, and generated JSON parameters are data, never evaluated Python.
"""
import copy
import json
import math

VERSION = 'declared-task-params-v1'
LEGACY = 'declared-task-noargs-v1'


def valid_params(value):
    def valid(x):
        if x is None or type(x) in (str, bool, int):
            return True
        if type(x) is float:
            return math.isfinite(x)
        if type(x) is list:
            return all(valid(v) for v in x)
        if type(x) is dict:
            return all(type(k) is str and valid(v) for k, v in x.items())
        return False
    try:
        return (type(value) is dict and not {'table', 'lookup'} & set(value)
                and valid(value))
    except RecursionError:
        return False


def parse_params(text):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError('duplicate JSON key')
            out[k] = v
        return out
    try:
        value = json.loads(text, object_pairs_hook=pairs)
        if not valid_params(value):
            raise ValueError('expected finite JSON kwargs without table/lookup')
    except (ValueError, TypeError, RecursionError):
        return {}, 'invalid_target_params'
    return value, None


def kwargs_for(entry):
    """None means no valid invocation, not an executable empty dict."""
    if not entry.get('target') or entry.get('target_contract_error'):
        return None
    version = entry.get('target_contract_version', LEGACY)
    if version == LEGACY:
        # Never give historical artifacts a new interpretation.
        return {} if not entry.get('target_params') else None
    value = entry.get('target_params')
    if version != VERSION or not valid_params(value):
        return None
    return copy.deepcopy(value)


def scope_key(entry):
    return json.dumps([entry['target'], kwargs_for(entry)], sort_keys=True,
                      ensure_ascii=False, allow_nan=False)
