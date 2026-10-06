"""Durable cross-run reservation ceiling for an explicitly delegated repair campaign.

Local allowances only, never a claim about the provider invoice. The lifetime
file lock permits one runner at a time. No run can refund/reset the campaign.
"""
import fcntl
import hashlib
import json
import os
from decimal import Decimal
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


class CampaignBudget:
    def __init__(self, root, authorization):
        self.root = Path(root).resolve()
        self.authorization = json.loads(json.dumps(authorization))
        self._validate_authorization()
        self.cap = Decimal(str(authorization['max_reserved_cny']))
        self._lock = (self.root / 'campaign.lock').open('a')
        try:
            fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.rows = [json.loads(line) for line in (self.root / 'ledger.jsonl').read_text().splitlines()]
            self._validate_ledger()
        except BaseException:
            self._lock.close()
            raise
        self.bound_run = None

    def _validate_authorization(self):
        a = self.authorization
        if (a.get('status') != 'USER_AUTHORIZED_BOUNDED_REPAIR_CAMPAIGN'
                or a.get('max_reserved_cny') != 7.5
                or a.get('individually_confirm_each_run') is not False
                or not a.get('user_confirmation')
                or not a.get('root') or Path(a['root']).resolve() != self.root
                or a.get('config', {}).get('max_reserved_cny') != 7.5):
            raise PermissionError('invalid bounded campaign authorization')
        from .agentport_config import validate, is_local_budget
        if not is_local_budget(a['config']):
            raise PermissionError('campaign only supports local smoke policy')
        validate(a['config'])

    @classmethod
    def initialize(cls, root, authorization):
        root = Path(root).resolve()
        # An exclusive directory is the one-time creation claim. Deleted or
        # corrupt ledgers are never silently recreated on a subsequent launch.
        root.mkdir(parents=True, exist_ok=False)
        obj = cls.__new__(cls)
        obj.root, obj.authorization = root, authorization
        obj._validate_authorization()
        header = {'event': 'campaign_initialized', 'authorization_sha256': digest(authorization),
                  'max_reserved_cny': '7.5', 'sequence': 0, 'previous_sha256': None}
        header['sha256'] = digest(header)
        fd = os.open(root / 'ledger.jsonl', os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, 'w') as f:
            f.write(json.dumps(header, sort_keys=True) + '\n')
            f.flush()
            os.fsync(f.fileno())

    def _validate_ledger(self):
        if not self.rows:
            raise PermissionError('empty campaign ledger')
        self.reserved = Decimal(0)
        self.requests = 0
        self.closed = False
        self.closed_reason = None
        previous = None
        runs = set()
        for i, row in enumerate(self.rows):
            payload = {k: v for k, v in row.items() if k != 'sha256'}
            if (row.get('sha256') != digest(payload) or row.get('sequence') != i
                    or row.get('previous_sha256') != previous):
                raise PermissionError('corrupt campaign ledger')
            prior_hash = previous
            previous = row['sha256']
            if i == 0:
                if (row.get('event') != 'campaign_initialized'
                        or row.get('authorization_sha256') != digest(self.authorization)
                        or row.get('max_reserved_cny') != '7.5'):
                    raise PermissionError('campaign authorization differs')
                continue
            event = row.get('event')
            if event == 'budget_extended':
                amendment = row.get('amendment', {})
                if row.get('amendment_sha256') != digest(amendment):
                    raise PermissionError('budget amendment digest differs')
                self.cap = self._extension_cap(amendment, prior_hash)
                self.closed, self.closed_reason = False, None
                continue
            if self.closed:
                raise PermissionError('event after campaign closure')
            if event == 'run_bound':
                if row['run_id'] in runs:
                    raise PermissionError('campaign run cannot be rebound')
                runs.add(row['run_id'])
            elif event == 'request_reserved':
                amount = Decimal(row['amount_cny'])
                if (not amount.is_finite() or not 0 < amount <= Decimal('0.10')
                        or row['run_id'] not in runs):
                    raise PermissionError('invalid campaign reservation')
                self.reserved += amount
                self.requests += 1
                if (self.reserved > self.cap or str(self.reserved) != row['reserved_cny']
                        or row['request'] != self.requests):
                    raise PermissionError('campaign accounting mismatch')
            elif event == 'campaign_stopped':
                if (row.get('reason') not in ('budget_limit', 'smoke_complete')
                        or row.get('reserved_cny') != str(self.reserved)):
                    raise PermissionError('invalid campaign closure')
                self.closed = True
                self.closed_reason = row['reason']
            else:
                raise PermissionError('unknown campaign event')

    def _extension_cap(self, amendment, prior_hash):
        """An explicit, append-only user amendment; never reset old spending."""
        if (amendment.get('status') != 'USER_AUTHORIZED_CUMULATIVE_BUDGET_INCREASE'
                or not isinstance(amendment.get('user_confirmation'), str)
                or not amendment['user_confirmation'].strip()
                or amendment.get('base_authorization_sha256') != digest(self.authorization)
                or amendment.get('prior_ledger_sha256') != prior_hash
                or amendment.get('previous_cap_cny') != str(self.cap)
                or amendment.get('prior_reserved_cny') != str(self.reserved)
                or amendment.get('root') != str(self.root)
                or self.closed_reason not in (None, 'budget_limit')):
            raise PermissionError('invalid or stale user budget amendment')
        value = amendment.get('max_reserved_cny')
        if type(value) not in (int, float, str):
            raise PermissionError('invalid extended cap')
        try:
            cap = Decimal(str(value))
        except Exception as exc:
            raise PermissionError('invalid extended cap') from exc
        if not cap.is_finite() or cap <= self.cap:
            raise PermissionError('budget amendment must increase the finite cumulative cap')
        return cap

    def extend_budget(self, amendment):
        if self.bound_run is not None:
            raise PermissionError('cannot change budget within an active run')
        amendment = json.loads(json.dumps(amendment))
        cap = self._extension_cap(amendment, self.rows[-1]['sha256'])
        self._append({'event': 'budget_extended', 'amendment': amendment,
                      'amendment_sha256': digest(amendment)})
        self.cap = cap
        self.closed, self.closed_reason = False, None

    def finish(self):
        """Caller invokes only after the complete smoke has returned successfully."""
        if self.closed or self.bound_run is None:
            raise PermissionError('no active campaign run to finish')
        self._append({'event': 'campaign_stopped', 'reason': 'smoke_complete',
                      'run_id': self.bound_run, 'reserved_cny': str(self.reserved)})
        self.closed, self.closed_reason = True, 'smoke_complete'

    def _append(self, payload):
        row = dict(payload, sequence=len(self.rows), previous_sha256=self.rows[-1]['sha256'])
        row['sha256'] = digest(row)
        try:
            with (self.root / 'ledger.jsonl').open('a') as f:
                f.write(json.dumps(row, sort_keys=True, allow_nan=False) + '\n')
                f.flush()
                os.fsync(f.fileno())
        except BaseException:
            self.closed = True
            self.closed_reason = 'ledger_failure'
            raise
        self.rows.append(row)

    def bind_run(self, resolved):
        if self.closed or self.bound_run is not None:
            raise PermissionError('campaign is closed or already bound')
        if resolved['config'] != self.authorization['config']:
            raise PermissionError('run expands or changes authorized campaign configuration')
        scope = resolved.get('run_scope') or {}
        out = Path(scope.get('output_dir', '')).resolve()
        if out.parent != self.root or not scope.get('run_id'):
            raise PermissionError('run output must be a fresh direct child of campaign')
        if any(row.get('run_id') == scope['run_id'] for row in self.rows):
            raise PermissionError('campaign run already used')
        self.bound_run = scope['run_id']
        self._append({'event': 'run_bound', 'run_id': self.bound_run,
                      'review_sha256': digest(resolved), 'code_sha256': resolved['code_sha256'],
                      'output_dir': str(out)})

    def reserve(self, amount):
        amount = Decimal(str(amount))
        if (self.closed or self.bound_run is None or not amount.is_finite()
                or not 0 < amount <= Decimal('0.10')):
            raise PermissionError('campaign cannot reserve this request')
        if self.reserved + amount > self.cap:
            self._append({'event': 'campaign_stopped', 'reason': 'budget_limit',
                          'reserved_cny': str(self.reserved)})
            self.closed = True
            self.closed_reason = 'budget_limit'
            raise PermissionError('cumulative campaign budget exhausted')
        self.reserved += amount
        self.requests += 1
        self._append({'event': 'request_reserved', 'run_id': self.bound_run,
                      'request': self.requests, 'amount_cny': str(amount),
                      'reserved_cny': str(self.reserved)})

    def receipt(self):
        return {'max_reserved_cny': str(self.cap), 'reserved_cny': str(self.reserved),
                'remaining_cny': str(self.cap - self.reserved), 'requests': self.requests,
                'closed': self.closed, 'accounting_basis': 'local_allowance_not_provider_invoice'}

    def close(self):
        self._lock.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
