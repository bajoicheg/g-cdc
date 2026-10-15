#!/usr/bin/env python3
"""Run an exhaustive partition of the original packaged unittest discovery.

This is test execution only: no scheduling, Source publication or budget changes.
Both jobs discover the same inventory; the required workflow gate compares its
fingerprint and counts before accepting their combined result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PARTITIONS = ('host-bridge', 'remaining')
HEAVY_MODULE = 'test_managed_host_bridge'


def _test_id(case):
    if not isinstance(case, unittest.TestCase):
        raise ValueError('unassigned discovery object is not a unittest TestCase')
    identifier = case.id()
    if (not isinstance(identifier, str) or not identifier or identifier != identifier.strip()
            or '.' not in identifier or any(ord(char) < 32 or ord(char) == 127 for char in identifier)
            or case.id() != identifier):
        raise ValueError('test requires a unique stable qualified id')
    return identifier


def _declared_skip(case):
    method = getattr(case, getattr(case, '_testMethodName', ''), None)
    return bool(getattr(case, '__unittest_skip__', False)
                or getattr(method, '__unittest_skip__', False))


def index_tests(suite):
    """Flatten once, retaining the actual original objects and discovery order."""
    inventory = {}
    def visit(item):
        if isinstance(item, unittest.TestSuite):
            for child in item:
                visit(child)
            return
        identifier = _test_id(item)
        if identifier in inventory:
            raise ValueError('duplicate discovered test id: ' + identifier)
        if _declared_skip(item):
            raise ValueError('declared test skip is forbidden: ' + identifier)
        inventory[identifier] = item
    visit(suite)
    if not inventory:
        raise ValueError('empty candidate test inventory')
    return inventory


def validate_partition_coverage(inventory, partitions):
    if not inventory or set(partitions) != set(PARTITIONS):
        raise ValueError('complete nonempty candidate partition inventory required')
    assigned = set()
    for name in PARTITIONS:
        cases = partitions[name]
        if not cases:
            raise ValueError('empty candidate partition: ' + name)
        for case in cases:
            identifier = _test_id(case)
            if identifier not in inventory or inventory[identifier] is not case:
                raise ValueError('unassigned or replaced candidate test object')
            if identifier in assigned:
                raise ValueError('duplicated or overlapping partition test id')
            expected = 'host-bridge' if identifier.split('.', 1)[0] == HEAVY_MODULE else 'remaining'
            if name != expected:
                raise ValueError('candidate test assigned to the wrong partition')
            assigned.add(identifier)
    if assigned != set(inventory):
        raise ValueError('candidate partition union loses discovered tests')


def partition_tests(inventory):
    partitions = {name: [] for name in PARTITIONS}
    for identifier, case in inventory.items():
        selected = 'host-bridge' if identifier.split('.', 1)[0] == HEAVY_MODULE else 'remaining'
        partitions[selected].append(case)
    validate_partition_coverage(inventory, partitions)
    return partitions


def run_partition(tests_root, partition, *, stream=None):
    if partition not in PARTITIONS:
        raise ValueError('unsupported candidate test partition')
    loader = unittest.TestLoader()
    # Same default pattern/top-level semantics as the original `unittest discover`.
    discovered = loader.discover(str(Path(tests_root).resolve()))
    if loader.errors:
        raise ValueError('candidate unittest discovery failed; no partition may omit its errors')
    inventory = index_tests(discovered)
    partitions = partition_tests(inventory)
    selected = partitions[partition]
    inventory_sha256 = hashlib.sha256(json.dumps(sorted(inventory), separators=(',', ':')).encode()).hexdigest()
    result = unittest.TextTestRunner(stream=stream or sys.stderr, verbosity=2).run(unittest.TestSuite(selected))
    report = {'partition': partition, 'inventory_sha256': inventory_sha256,
              'total_tests': len(inventory), 'selected_tests': len(selected),
              'executed_tests': result.testsRun, 'skipped_tests': len(result.skipped)}
    passed = result.wasSuccessful() and not result.skipped and result.testsRun == len(selected)
    return (0 if passed else 1), report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--partition', required=True, choices=PARTITIONS)
    parser.add_argument('--tests-root', type=Path, default=ROOT / 'src/continuous-development-cycle/tests')
    args = parser.parse_args(argv)
    try:
        status, report = run_partition(args.tests_root, args.partition)
        print(json.dumps(report, sort_keys=True))
        if status == 0 and os.environ.get('GITHUB_OUTPUT'):
            # Actions supplies this path; values are derived counters/fingerprint,
            # never test output or candidate-controlled multiline strings.
            with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='ascii') as output:
                for key in ('inventory_sha256', 'total_tests', 'selected_tests'):
                    output.write(key + '=' + str(report[key]) + '\n')
        return status
    except (OSError, ValueError, TypeError) as error:
        print('CANDIDATE_PARTITION_RED: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
