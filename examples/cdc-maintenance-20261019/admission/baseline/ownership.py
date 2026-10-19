"""Transactional coordination state. Only the trusted broker may use this store.

VerifiedTarget is the broker's assertion, not an authentication protocol. The
bridge must verify principal, grant, account and session before constructing it.
"""
import contextlib
from dataclasses import dataclass, asdict
import json
import math
import os
import re
import sqlite3
import time

from .handover import decode_handover


class Conflict(ValueError):
    pass


class PendingEffect(ValueError):
    pass


@dataclass(frozen=True)
class VerifiedTarget:
    provider: str
    account_id: str
    profile_id: str
    session_id: str
    observed_at: float
    proof_sha256: str


def _identity(value):
    fields = {'provider', 'account_id', 'profile_id', 'session_id'}
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError('incomplete identity')
    if value['provider'] not in ('codex', 'kimi'):
        raise ValueError('unsupported provider')
    if any(not isinstance(v, str) or not v.strip() or len(v.encode()) > 1024
           for v in value.values()):
        raise ValueError('invalid identity binding')
    return dict(value)


def _target(value):
    if not isinstance(value, VerifiedTarget):
        raise ValueError('broker verification required')
    if (type(value.observed_at) not in (int, float)
            or not math.isfinite(value.observed_at)
            or not 0 <= time.time() - value.observed_at <= 90
            or not isinstance(value.proof_sha256, str)
            or not re.fullmatch(r'[0-9a-f]{64}', value.proof_sha256)):
        raise ValueError('invalid or stale verification')
    return _identity({k: v for k, v in asdict(value).items()
                      if k not in ('observed_at', 'proof_sha256')})


class OwnershipStore:
    def __init__(self, path):
        self.path = os.fspath(path)
        # Storage path and parent are provisioned privately by the broker.
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        os.close(fd)
        with self._transaction() as db:
            db.execute('CREATE TABLE IF NOT EXISTS ownership '
                       '(singleton INTEGER PRIMARY KEY CHECK(singleton=1), body TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS history '
                       '(generation INTEGER PRIMARY KEY, body TEXT NOT NULL)')

    @contextlib.contextmanager
    def _transaction(self):
        db = sqlite3.connect(self.path, timeout=5)
        try:
            db.execute('PRAGMA synchronous=FULL')
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _read(db):
        row = db.execute('SELECT body FROM ownership WHERE singleton=1').fetchone()
        if row is None:
            raise Conflict('ownership not initialized')
        return json.loads(row[0])

    @staticmethod
    def _write(db, row):
        body = json.dumps(row, allow_nan=False, separators=(',', ':'))
        db.execute('INSERT INTO history VALUES (?, ?)', (row['generation'], body))
        db.execute('INSERT OR REPLACE INTO ownership VALUES (1, ?)', (body,))

    @staticmethod
    def _expected(row, generation):
        if type(generation) is not int or row['generation'] != generation:
            raise Conflict('stale ownership generation')

    def create(self, owner):
        owner = _identity(owner)
        with self._transaction() as db:
            if db.execute('SELECT 1 FROM ownership').fetchone():
                raise Conflict('ownership already exists')
            row = dict(generation=0, phase='RUNNING', owner=owner,
                       handover=None, target=None, pending_effect=None)
            self._write(db, row)
            return row

    def read(self):
        with self._transaction() as db:
            return self._read(db)

    def advance(self, expected_generation, phase, *, handover=None, target=None):
        transitions = {'RUNNING': 'DRAINING', 'DRAINING': 'HANDOVER_SAVED',
                       'HANDOVER_SAVED': 'TARGET_VERIFIED', 'TARGET_VERIFIED': 'RUNNING'}
        with self._transaction() as db:
            row = self._read(db)
            self._expected(row, expected_generation)
            if row['pending_effect'] is not None:
                raise PendingEffect('reconcile original effect before ownership transfer')
            if transitions[row['phase']] != phase:
                raise ValueError('invalid ownership transition')
            if handover is not None and phase != 'HANDOVER_SAVED':
                raise ValueError('handover supplied in wrong phase')
            if target is not None and phase != 'TARGET_VERIFIED':
                raise ValueError('target supplied in wrong phase')
            if phase == 'HANDOVER_SAVED':
                decode_handover(handover)
                row['handover'] = handover.decode('utf-8')
                row['target'] = None
            elif phase == 'TARGET_VERIFIED':
                _target(target)
                row['target'] = asdict(target)
            elif phase == 'RUNNING':
                row['owner'] = _target(VerifiedTarget(**row['target']))
                row['target'] = None
            row['phase'] = phase
            row['generation'] += 1
            self._write(db, row)
            return row

    def record_unknown(self, expected_generation, operation):
        if (not isinstance(operation, dict)
                or set(operation) != {'operation_id', 'task_id', 'attempt_id'}
                or any(not isinstance(v, str) or not v or len(v.encode()) > 1024
                       for v in operation.values())):
            raise ValueError('original operation identity required')
        with self._transaction() as db:
            row = self._read(db)
            self._expected(row, expected_generation)
            if row['pending_effect'] is not None:
                raise PendingEffect('original unknown must not be overwritten')
            row['pending_effect'] = dict(operation)
            row['generation'] += 1
            self._write(db, row)
            return row


def may_cancel(turn_id, lease, *, now):
    if not isinstance(lease, dict) or not isinstance(turn_id, str) or not turn_id:
        return False
    expiry = lease.get('expires_at')
    return (lease.get('turn_id') == turn_id
            and type(expiry) in (int, float) and math.isfinite(expiry)
            and type(now) in (int, float) and math.isfinite(now) and now >= expiry)
