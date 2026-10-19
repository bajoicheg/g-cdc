"""Bounded, structured nonsecret handover; never imports model transcripts."""
import json
import re

MAX_BYTES = 1048576
MAX_NOTE_BYTES = 65536
_FIELDS = {'schema', 'goal', 'source_shas', 'tasks', 'active_operations',
           'checks', 'next_action', 'notes'}
_FORBIDDEN = {'access_token', 'refresh_token', 'password', 'raw_session',
              'reasoning', 'auth', 'credentials', 'secret', 'api_key'}


def _scan(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str) or key.lower() in _FORBIDDEN:
                raise ValueError('secret or unsupported key')
            _scan(child)
    elif isinstance(value, list):
        for child in value:
            _scan(child)


def _validate(value):
    if not isinstance(value, dict) or set(value) != _FIELDS:
        raise ValueError('incomplete or unsupported handover')
    if value['schema'] != 'cdc-operator-handover/v1':
        raise ValueError('unsupported schema')
    for field in ('goal', 'next_action'):
        if not isinstance(value[field], str) or not value[field].strip():
            raise ValueError('missing handover text')
    for field in ('source_shas', 'tasks', 'active_operations', 'checks', 'notes'):
        if not isinstance(value[field], list):
            raise ValueError('expected handover list')
    for sha in value['source_shas']:
        if not isinstance(sha, str) or not re.fullmatch(r'[0-9a-f]{40}', sha):
            raise ValueError('invalid source SHA')
    for task in value['tasks']:
        if not isinstance(task, dict) or not {'id', 'attempt_id', 'budget', 'status'} <= task.keys():
            raise ValueError('incomplete original task')
        for field in ('id', 'attempt_id', 'status'):
            if not isinstance(task[field], str) or not task[field]:
                raise ValueError('missing original task identity/status')
        if not isinstance(task['budget'], dict):
            raise ValueError('missing original budget')
    for operation in value['active_operations']:
        if not isinstance(operation, dict) or not operation.get('operation_id'):
            raise ValueError('missing original operation')
    for note in value['notes']:
        if not isinstance(note, str) or len(note.encode('utf-8')) > MAX_NOTE_BYTES:
            raise ValueError('source note bound')
    if not all(isinstance(check, str) for check in value['checks']):
        raise ValueError('invalid checks')
    _scan(value)


def encode_handover(value):
    try:
        _validate(value)
        raw = json.dumps(value, ensure_ascii=False, allow_nan=False,
                         separators=(',', ':')).encode('utf-8')
    except (TypeError, OverflowError, RecursionError, UnicodeError) as exc:
        raise ValueError('invalid handover') from exc
    if len(raw) > MAX_BYTES:
        raise ValueError('aggregate handover bound')
    return raw


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('duplicate handover key')
        result[key] = value
    return result


def decode_handover(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ValueError('aggregate handover bound')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs)
        encode_handover(value)
        return value
    except (UnicodeError, RecursionError) as exc:
        raise ValueError('invalid handover') from exc
