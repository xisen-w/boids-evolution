"""Serial, durable, non-resumable local smoke circuit; NOT a provider bill cap."""
import json
import os
from decimal import Decimal
from pathlib import Path
import threading
from types import MappingProxyType

from .agentport_config import is_local_budget, validate, blockers
from .model import validate_usage


class LocalSmokeBudget:
    """Reserve before send; retain uncertain requests; never refund or resume.

    Monetary values are local allowances, not measured gateway charges. A
    server can bill a sent request after cancellation; this cannot undo it.
    """

    def __init__(self, config, ledger, *, request_limit=None, reserved_cap_cny=None, campaign=None):
        if not is_local_budget(config):
            raise ValueError('local circuit needs the explicit v2 budget policy')
        validate(config)
        if blockers(config):
            raise PermissionError('local budget configuration has unresolved blockers')
        self.config = MappingProxyType(dict(config))
        self.campaign = campaign
        self.ledger = Path(ledger)
        self.currency = 'CNY'
        self._rate_in = Decimal(str(config['reservation_input_cny_per_million']))
        self._rate_out = Decimal(str(config['reservation_output_cny_per_million']))
        self._cap = Decimal(str(config['max_reserved_cny']))
        # A separately approved one-request diagnostic may only NARROW the
        # smoke limits, never expand them. Validate before creating a ledger.
        self._request_limit = config['max_http_requests']
        if request_limit is not None:
            if type(request_limit) is not int or not 1 <= request_limit <= self._request_limit:
                raise ValueError('diagnostic request limit must narrow the smoke limit')
            self._request_limit = request_limit
        if reserved_cap_cny is not None:
            if type(reserved_cap_cny) not in (int, float):
                raise ValueError('diagnostic cap must be a finite positive number')
            narrowed = Decimal(str(reserved_cap_cny))
            if not narrowed.is_finite() or not 0 < narrowed <= self._cap:
                raise ValueError('diagnostic cap must narrow the smoke cap')
            self._cap = narrowed
        self._per_request_cap = Decimal(str(config['max_reserved_per_request_cny']))
        self._reserved = self._accounted = Decimal(0)
        self.requests = self.reported_responses = 0
        self._pending = None
        self._stopped = False
        self._stop_reason = None
        self._ledger_healthy = True
        self._lock = threading.RLock()
        # A second process or restart must not silently start a fresh counter
        # on an existing run's ledger, even when that ledger is empty.
        fd = os.open(self.ledger, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    @property
    def reserved(self):
        return float(self._reserved)

    def _append(self, row):
        with self.ledger.open('a', encoding='utf-8') as f:
            f.write(json.dumps(row, sort_keys=True, allow_nan=False) + '\n')
            f.flush()
            os.fsync(f.fileno())

    def stop(self, reason):
        # Only caller-controlled reason codes, never raw exception messages.
        allowed = {'run_failure', 'unsettled_request', 'invalid_request',
                   'request_limit', 'money_limit', 'invalid_usage', 'usage_over_reserve',
                   'ledger_failure', 'diagnostic_complete', 'campaign_refusal'}
        if reason not in allowed:
            reason = 'run_failure'
        with self._lock:
            if self._stopped:
                return
            self._stopped, self._stop_reason = True, reason
            try:
                self._append({'event': 'circuit_open', 'reason': reason,
                              'request': self.requests, 'reserved_cost_exact': str(self._reserved)})
            except Exception:
                self._ledger_healthy = False

    def _deny(self, reason):
        self.stop(reason)
        raise PermissionError('local smoke circuit open: ' + reason)

    def before(self, system, user, max_tokens, attempt):
        with self._lock:
            if self._stopped:
                raise PermissionError('local smoke circuit already open; new review required')
            if self._pending is not None:
                self._deny('unsettled_request')
            if (type(attempt) is not int or attempt != 0
                    or not isinstance(system, str) or not isinstance(user, str)
                    or type(max_tokens) is not int or not 0 < max_tokens <= self.config['builder_max_tokens']):
                self._deny('invalid_request')
            size = len((system + user).encode('utf-8'))
            if size > self.config['max_input_bytes']:
                self._deny('invalid_request')
            amount = ((size + 512) * self._rate_in + max_tokens * self._rate_out) / Decimal(1000000)
            if self.requests >= self._request_limit:
                self._deny('request_limit')
            if amount > self._per_request_cap or self._reserved + amount > self._cap:
                self._deny('money_limit')
            # The campaign reservation is durable before the local reservation
            # and before transport. Failure later never refunds this amount.
            if self.campaign is not None:
                try:
                    self.campaign.reserve(amount)
                except Exception:
                    self._deny('campaign_refusal')
            # Hold the lock across the durable reservation. No request may
            # leave until this function returns successfully.
            self.requests += 1
            self._reserved += amount
            self._pending = (size + 512, max_tokens, amount)
            try:
                self._append({'event': 'request_reserved', 'request': self.requests,
                              'input_bytes': size, 'output_token_cap': max_tokens,
                              'currency': self.currency, 'accounting_basis': 'local_allowance',
                              'reserved_cost_exact': str(self._reserved),
                              'request_reserved_cost_exact': str(amount)})
            except Exception:
                self._ledger_healthy = False
                self._deny('ledger_failure')

    def after(self, tin, tout, cached, metadata):
        with self._lock:
            try:
                validate_usage(tin, tout, cached)
            except RuntimeError:
                self._deny('invalid_usage')
            if self._pending is None:
                self._deny('invalid_usage')
            input_cap, output_cap, reservation = self._pending
            amount = (tin * self._rate_in + tout * self._rate_out) / Decimal(1000000)
            # Persist valid usage even when it reveals an overrun. Never label
            # usage multiplied by local allowances as a provider invoice.
            self._accounted += amount
            self.reported_responses += 1
            self._pending = None
            try:
                self._append({'event': 'response_usage', 'request': self.requests,
                              'tokens_in': tin, 'tokens_out': tout, 'cached_tokens': cached,
                              'metadata': metadata, 'currency': self.currency,
                              'accounting_basis': 'local_allowance',
                              'usage_cost_at_allowance_exact': str(amount)})
            except Exception:
                self._ledger_healthy = False
                self._deny('ledger_failure')
            if tin > input_cap or tout > output_cap or amount > reservation or self._accounted > self._cap:
                self._deny('usage_over_reserve')

    def receipt(self):
        with self._lock:
            receipt = {'currency': self.currency, 'accounting_basis': 'local_allowance_not_provider_invoice',
                    'provider_bill_guaranteed': False,
                    'cost_reserved': float(self._reserved), 'cost_reserved_exact': str(self._reserved),
                    'usage_cost_at_allowance': float(self._accounted),
                    'max_reserved_cny': float(self._cap),
                    'max_reserved_per_request_cny': float(self._per_request_cap),
                    'max_http_requests': self._request_limit,
                    'http_requests': self.requests, 'reported_responses': self.reported_responses,
                    'unreported_requests': self.requests - self.reported_responses,
                    'circuit_open': self._stopped, 'stop_reason': self._stop_reason,
                    'ledger_healthy': self._ledger_healthy}
            if self.campaign is not None:
                receipt['campaign'] = self.campaign.receipt()
            return receipt
