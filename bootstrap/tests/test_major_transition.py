"""A new stable major candidate retains an independent stable driver and gates."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'bootstrap'))
from src.cdc27.canonical_source import validate_source_lock
import validate_release


class MajorTransitionTests(unittest.TestCase):
    def lock(self):
        data = json.loads((ROOT / 'release/source.lock.json').read_text())
        data['development_driver_version'] = '2.12.1'
        data['target_version'] = '3.0.0'
        return data

    def test_next_major_zero_minor_and_patch_is_structurally_supported(self):
        for validator in (validate_source_lock, validate_release.source_lock):
            with self.subTest(validator=validator.__name__):
                validator(self.lock())

    def test_major_skip_nonzero_components_or_same_driver_are_rejected(self):
        for target in ('4.0.0', '3.1.0', '3.0.1', '2.12.1', '3.0.0-rc1'):
            for validator in (validate_source_lock, validate_release.source_lock):
                with self.subTest(target=target, validator=validator.__name__):
                    data = self.lock(); data['target_version'] = target
                    with self.assertRaises(ValueError):
                        validator(data)

    def test_major_transition_preserves_independent_base_and_canonical_gates(self):
        for key, value in [('development_driver_version', '3.0.0'),
                           ('development_driver_version', '2.5.0'),
                           ('base_package_tree', 'missing'),
                           ('base_validation_commit', 'missing'),
                           ('direct_product_repo_development', True)]:
            for validator in (validate_source_lock, validate_release.source_lock):
                with self.subTest(field=key, validator=validator.__name__):
                    data = self.lock(); data[key] = value
                    with self.assertRaises(ValueError):
                        validator(data)


if __name__ == '__main__':
    unittest.main()
