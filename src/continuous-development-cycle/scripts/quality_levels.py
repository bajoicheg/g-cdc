#!/usr/bin/env python3
"""Risk-based validation policy; evidence only, never execution authority."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

LEVELS = {'FAST': 0, 'MEDIUM': 1, 'FULL': 2}
RISK_FLOORS = {c: 'FULL' for c in ('cdc_core', 'executor_authority',
    'authentication', 'ad_write', 'dangerous_migration')}
RISK_FLOORS.update(ordinary_feature='MEDIUM', local_reversible='FAST',
                   documentation='FAST', presentation='FAST')

def fields(data, expected, name):
    if not isinstance(data, dict) or set(data) != set(expected):
        raise ValueError(name + ' fields mismatch')

def text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + ' must be nonempty text')

def texts(value, name, allow_empty=False):
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValueError(name + ' must be a list')
    for item in value: text(item, name)
    if len(value) != len(set(value)): raise ValueError(name + ' contains duplicates')

def level(value):
    if not isinstance(value, str) or value not in LEVELS: raise ValueError('invalid quality level')

def validate_policy(data: dict) -> dict:
    fields(data, ('default_level', 'max_validation_cycles'), 'quality policy')
    level(data['default_level'])
    if type(data['max_validation_cycles']) is not int or data['max_validation_cycles'] < 1:
        raise ValueError('max_validation_cycles must be positive integer')
    return data

def evaluate(data: dict) -> dict:
    fields(data, ('schema', 'project_level', 'risk_level', 'risk_categories',
                  'risk_reason', 'mandatory_check_ids'), 'quality assessment')
    if data['schema'] != 'quality-assessment/v1': raise ValueError('quality assessment schema mismatch')
    level(data['project_level']); level(data['risk_level'])
    texts(data['risk_categories'], 'risk_categories')
    if any(c not in RISK_FLOORS for c in data['risk_categories']): raise ValueError('unknown risk category')
    texts(data['mandatory_check_ids'], 'mandatory_check_ids', allow_empty=True)
    if not isinstance(data['risk_reason'], str): raise ValueError('risk_reason must be text')
    effective = max([data['project_level'], data['risk_level']] +
                    [RISK_FLOORS[c] for c in data['risk_categories']], key=LEVELS.get)
    raised = LEVELS[effective] > LEVELS[data['project_level']]
    if raised: text(data['risk_reason'], 'risk_reason for escalation')
    return {'schema': 'quality-assessment-result/v1', 'effective_level': effective,
            'escalated': raised, 'risk_reason': data['risk_reason'],
            'mandatory_check_ids': list(data['mandatory_check_ids']),
            'authorizes_product_write': False, 'authorizes_release': False,
            'authorizes_external_start': False}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('input')
    args=parser.parse_args(argv)
    try: result=evaluate(json.loads(Path(args.input).read_text()))
    except (OSError,ValueError) as exc:
        print('FAIL: '+str(exc),file=sys.stderr); return 2
    print(json.dumps(result,sort_keys=True)); return 0

if __name__=='__main__':raise SystemExit(main())
