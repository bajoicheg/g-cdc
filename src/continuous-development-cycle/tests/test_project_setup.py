"""User-visible planner contracts; changing platform/authority/preservation breaks these."""
import copy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from contracts import load_yaml
from validate_adapter import validate_adapter
from validate_checkpoint_24 import validate_checkpoint_24


def init_request(preset='portable'):
    return dict(schema='cdc-init-request/v1', repository='owner/project',
                branch='feature/setup', source_head='a' * 40, preset=preset,
                validation=dict(quick='python -B quick.py', full='python -B full.py',
                                release='python -B release.py'), cloud_profile_json=None)


def invoke(command, request):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'request.json'
        path.write_text(json.dumps(request))
        before = set(Path(directory).iterdir())
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/cdc.py'),
                                 command, str(path)], cwd=directory,
                                capture_output=True, text=True)
        if set(Path(directory).iterdir()) != before:
            raise AssertionError('planner wrote files in caller workspace')
        return result


class InitCLITests(unittest.TestCase):
    def initialize(self, request):
        result = invoke('init', request)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_each_preset_generates_valid_adapter_and_checkpoint(self):
        for preset, quality, platform in [('portable', 'MEDIUM', 'any'),
                                          ('windows', 'MEDIUM', 'windows'),
                                          ('android', 'MEDIUM', 'android'),
                                          ('critical', 'FULL', 'any')]:
            with self.subTest(preset=preset):
                value = self.initialize(init_request(preset))
                files = {item['path']: item['content'] for item in value['files']}
                with tempfile.TemporaryDirectory() as directory:
                    adapter_file = Path(directory) / 'adapter.yaml'
                    checkpoint_file = Path(directory) / 'checkpoint.md'
                    adapter_file.write_text(files['docs/development-cycle.yaml'])
                    checkpoint_file.write_text(files['docs/work-status/current.md'])
                    adapter = load_yaml(adapter_file)
                    checkpoint = load_yaml(checkpoint_file, frontmatter=True)
                    binding = validate_adapter(adapter)
                    validate_checkpoint_24(checkpoint, adapter)
                self.assertEqual(adapter['quality']['default_level'], quality)
                self.assertEqual(adapter['validation']['final_platform'], platform)
                self.assertEqual(checkpoint['repository'], 'owner/project')
                self.assertEqual(checkpoint['branch'], 'feature/setup')
                self.assertEqual(checkpoint['candidate_sha'], 'a' * 40)
                self.assertEqual(checkpoint['policy_digest'], binding['policy_digest'])
                self.assertEqual(checkpoint['phase'], 'recovery')
                self.assertEqual(checkpoint['lease_state'], 'released')
                self.assertIsNone(checkpoint['operation_key'])
                self.assertEqual(checkpoint['last_green_evidence'], '')
                self.assertFalse(adapter['watchdog']['enabled'])
                self.assertEqual(adapter['ci']['actions_budget'], 'conserve')
                self.assertFalse(any(v for k, v in value.items() if k.startswith('authorizes_')))

    def test_validation_commands_are_literal_unexecuted_data(self):
        request = init_request()
        request['validation']['full'] = 'touch SENTINEL; $(touch OTHER); `touch THIRD`'
        result = self.initialize(request)
        self.assertIn(request['validation']['full'], str(result['files']))

    def test_invalid_preset_identity_or_missing_full_command_is_rejected(self):
        for field, bad in [('repository', '../project'), ('branch', '../main'),
                            ('source_head', 'abcd'), ('preset', 'unknown')]:
            with self.subTest(field=field):
                request = init_request(); request[field] = bad
                self.assertNotEqual(invoke('init', request).returncode, 0)
        request = init_request(); request['validation']['full'] = ''
        self.assertNotEqual(invoke('init', request).returncode, 0)

    def test_duplicate_json_keys_are_rejected_before_planning(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.json'
            path.write_text('{"schema":"cdc-init-request/v1","schema":"other"}')
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/cdc.py'),
                                     'init', str(path)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('duplicate JSON field', result.stderr)


if __name__ == '__main__':
    unittest.main()
