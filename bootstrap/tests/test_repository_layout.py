"""Regressions for a GREEN workflow that skipped PR #69's root-level code."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

BOOTSTRAP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOTSTRAP))
layout = __import__('repository_layout') if importlib.util.find_spec('repository_layout') else None


class RepositoryLayoutTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(layout, 'repository-wide layout gate is missing')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)

    def add(self, name, content=''):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        subprocess.run(['git', '-C', str(self.root), 'add', name], check=True)

    def test_root_runtime_and_test_are_rejected_together(self):
        for path in ('scripts/project_lanes.py', 'scripts/project_lane_runtime.py', 'tests/test_project_lanes.py'):
            self.add(path)
        with self.assertRaises(ValueError) as caught:
            layout.validate(self.root)
        for path in ('scripts/project_lanes.py', 'scripts/project_lane_runtime.py', 'tests/test_project_lanes.py'):
            self.assertIn(path, str(caught.exception))

    def test_canonical_sources_and_discovered_tests_are_allowed(self):
        for path in ('bootstrap/validate_release.py', 'bootstrap/tests/test_gate.py',
                     'src/cdc27/release_contract.py',
                     'src/continuous-development-cycle/scripts/project_lanes.py',
                     'src/continuous-development-cycle/tests/test_project_lanes.py'):
            self.add(path)
        layout.validate(self.root)

    def test_test_in_source_directory_is_not_discovered(self):
        self.add('src/continuous-development-cycle/scripts/test_hidden.py')
        with self.assertRaisesRegex(ValueError, 'test_hidden'):
            layout.validate(self.root)

    def test_nested_test_requires_tracked_package_markers(self):
        base = 'src/continuous-development-cycle/tests/nested/'
        self.add(base + 'test_hidden.py')
        with self.assertRaisesRegex(ValueError, '__init__'):
            layout.validate(self.root)
        (self.root / base / '__init__.py').write_text('')
        with self.assertRaisesRegex(ValueError, '__init__'):
            layout.validate(self.root)
        self.add(base + '__init__.py')
        layout.validate(self.root)

    def test_same_discovery_rule_applies_to_bootstrap_tests(self):
        self.add('bootstrap/tests/nested/testcase.py')
        with self.assertRaisesRegex(ValueError, '__init__'):
            layout.validate(self.root)

    def test_undiscoverable_test_module_names_are_rejected(self):
        for name in ('test-hidden.py', 'test.hidden.py'):
            self.add('bootstrap/tests/' + name)
        with self.assertRaises(ValueError) as caught:
            layout.validate(self.root)
        self.assertIn('test-hidden.py', str(caught.exception))
        self.assertIn('test.hidden.py', str(caught.exception))

    def test_symlink_marker_does_not_prove_nested_discovery(self):
        base = 'bootstrap/tests/nested/'
        self.add(base + 'test_hidden.py')
        marker = self.root / base / '__init__.py'
        marker.symlink_to('missing.py')
        subprocess.run(['git', '-C', str(self.root), 'add', str(marker)], check=True)
        with self.assertRaisesRegex(ValueError, '__init__'):
            layout.validate(self.root)

    def test_symlink_test_is_not_a_regular_discoverable_module(self):
        path = self.root / 'bootstrap/tests/test_hidden.py'
        path.parent.mkdir(parents=True)
        path.symlink_to('missing.py')
        subprocess.run(['git', '-C', str(self.root), 'add', str(path)], check=True)
        with self.assertRaisesRegex(ValueError, 'test_hidden.py'):
            layout.validate(self.root)

    def test_cli_fails_before_candidate_import(self):
        self.add('scripts/project_lanes.py', "raise RuntimeError('must not import')")
        result = subprocess.run([sys.executable, '-B', str(BOOTSTRAP / 'repository_layout.py'),
                                 '--root', str(self.root)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('LAYOUT_RED', result.stdout)
        self.assertNotIn('must not import', result.stderr)
