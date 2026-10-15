"""Partition regressions use real unittest objects and tiny isolated suites."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_candidate_tests as candidate


class CandidatePartitionTests(unittest.TestCase):
    def case(self, name, module, method=None):
        def passing(test):
            test.assertEqual(2 + 2, 4)
        cls = type(name, (unittest.TestCase,), {
            '__module__': module, 'test_probe': method or passing})
        return cls('test_probe')

    def inventory(self):
        heavy = self.case('Heavy', 'test_managed_host_bridge')
        other = self.case('Other', 'test_other')
        # A similarly named module must remain in the exact complement.
        similar = self.case('Similar', 'test_managed_host_bridge_extra')
        suite = unittest.TestSuite([unittest.TestSuite([heavy, other]), similar])
        return (heavy, other, similar), candidate.index_tests(suite)

    def test_partition_union_preserves_every_original_object_without_overlap(self):
        original, inventory = self.inventory()
        parts = candidate.partition_tests(inventory)
        candidate.validate_partition_coverage(inventory, parts)
        self.assertEqual(parts['host-bridge'], [original[0]])
        self.assertEqual(parts['remaining'], [original[1], original[2]])
        selected = [case for cases in parts.values() for case in cases]
        self.assertEqual({case.id() for case in selected}, set(inventory))
        self.assertEqual(len(selected), 3)
        self.assertTrue(all(any(case is source for source in original) for case in selected))

    def test_duplicate_or_unstable_test_ids_cannot_be_silently_dropped(self):
        case = self.case('Heavy', 'test_managed_host_bridge')
        with self.assertRaises(ValueError):
            candidate.index_tests(unittest.TestSuite([case, case]))
        class Unstable(unittest.TestCase):
            calls = 0
            def runTest(self):
                pass
            def id(self):
                self.calls += 1
                return 'test_unstable.Case.test_' + str(self.calls)
        with self.assertRaises(ValueError):
            candidate.index_tests(unittest.TestSuite([Unstable()]))

    def test_empty_missing_duplicated_and_unassigned_partitions_fail_closed(self):
        _, inventory = self.inventory()
        parts = candidate.partition_tests(inventory)
        invalid = [
            {},
            {'host-bridge': parts['remaining'], 'remaining': parts['host-bridge']},
            {'host-bridge': [], 'remaining': list(inventory.values())},
            {'host-bridge': parts['host-bridge'], 'remaining': []},
            {'host-bridge': parts['host-bridge'], 'remaining': parts['remaining'][:1]},
            {'host-bridge': parts['host-bridge'], 'remaining': list(inventory.values())},
            {'host-bridge': parts['host-bridge'], 'remaining': [*parts['remaining'], parts['remaining'][0]]},
            {'host-bridge': parts['host-bridge'], 'remaining': [*parts['remaining'], self.case('Unknown', 'test_new')]},
        ]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                candidate.validate_partition_coverage(inventory, value)
        with self.assertRaises(ValueError):
            candidate.index_tests(unittest.TestSuite())
        with self.assertRaises(ValueError):
            candidate.partition_tests({'test_other.Other.test_probe': self.case('Other', 'test_other')})
        with self.assertRaises(ValueError):
            candidate.index_tests(unittest.TestSuite([unittest.TestSuite([lambda: None])]))

    def test_decorated_method_and_class_skips_are_rejected_before_execution(self):
        @unittest.skip('synthetic excluded coverage')
        def skipped(test):
            test.fail('must never run')
        method = self.case('MethodSkip', 'test_other', skipped)
        cls = unittest.skip('synthetic class exclusion')(type('ClassSkip', (unittest.TestCase,), {
            '__module__': 'test_other', 'test_probe': lambda test: None}))
        for case in (method, cls('test_probe')):
            with self.subTest(case=case), self.assertRaises(ValueError):
                candidate.index_tests(unittest.TestSuite([case]))

    def fixture(self, body):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        tests = root / 'tests'; tests.mkdir()
        (tests / 'test_managed_host_bridge.py').write_text(
            'import unittest\nclass Heavy(unittest.TestCase):\n def test_ok(self):\n  self.assertTrue(True)\n')
        (tests / 'test_other.py').write_text(
            'import unittest\nclass Other(unittest.TestCase):\n def test_probe(self):\n  ' + body + '\n')
        return root, tests

    def run_fixture(self, body, partition='remaining'):
        root, tests = self.fixture(body)
        output = root / 'github-output'
        environment = os.environ.copy(); environment['GITHUB_OUTPUT'] = str(output)
        proc = subprocess.run([sys.executable, '-B', str(candidate.__file__),
            '--tests-root', str(tests), '--partition', partition],
            cwd=root, env=environment, capture_output=True, text=True, timeout=20)
        return proc, output

    def test_successful_cli_executes_exact_selected_count_and_publishes_inventory(self):
        proc, output = self.run_fixture('self.assertEqual(7, 7)')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads(proc.stdout.splitlines()[-1])
        self.assertEqual((report['total_tests'], report['selected_tests'], report['executed_tests']), (2, 1, 1))
        self.assertEqual(report['skipped_tests'], 0)
        values = dict(line.split('=', 1) for line in output.read_text().splitlines())
        self.assertEqual(values['inventory_sha256'], report['inventory_sha256'])
        self.assertEqual(values['selected_tests'], '1')

    def test_runtime_skip_assertion_failure_and_error_return_nonzero_without_success_outputs(self):
        for body in ("self.skipTest('runtime exclusion')", 'self.fail("synthetic failure")',
                     'raise RuntimeError("synthetic error")'):
            with self.subTest(body=body):
                proc, output = self.run_fixture(body)
                self.assertNotEqual(proc.returncode, 0)
                self.assertFalse(output.exists())

    def test_test_object_that_does_not_execute_cannot_report_partition_success(self):
        root, tests = self.fixture('self.assertTrue(True)')
        (tests / 'test_other.py').write_text(
            'import unittest\nclass Other(unittest.TestCase):\n'
            ' def test_probe(self): pass\n def run(self, result=None): return result\n')
        environment = os.environ.copy(); environment.pop('GITHUB_OUTPUT', None)
        proc = subprocess.run([sys.executable, '-B', str(candidate.__file__),
            '--tests-root', str(tests), '--partition', 'remaining'],
            cwd=root, env=environment, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(proc.returncode, 0)
        report = json.loads(proc.stdout.splitlines()[-1])
        self.assertEqual(report['selected_tests'], 1)
        self.assertEqual(report['executed_tests'], 0)

    def test_discovery_error_is_nonzero_instead_of_omitting_broken_module(self):
        root, tests = self.fixture('self.assertTrue(True)')
        (tests / 'test_broken.py').write_text('raise RuntimeError("synthetic import failure")\n')
        proc = subprocess.run([sys.executable, '-B', str(candidate.__file__),
            '--tests-root', str(tests), '--partition', 'host-bridge'],
            cwd=root, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('discovery', proc.stderr)


if __name__ == '__main__':
    unittest.main()
