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
from src.cdc27.release_contract import validate_candidate
from src.cdc27.compatibility import validate_matrix
import validate_release


class MajorTransitionTests(unittest.TestCase):
    def test_major_compatibility_transition_preserves_schemas_and_history(self):
        data = json.loads((ROOT / 'compatibility/matrix.json').read_text())
        data.update(target_version='3.0.0', developed_under_version='2.12.1')
        validate_matrix(data)
        for version in ('3.0.1', '3.1.0', '4.0.0'):
            with self.subTest(version=version):
                invalid = copy.deepcopy(data); invalid['target_version'] = version
                with self.assertRaises(ValueError):
                    validate_matrix(invalid)
        invalid = copy.deepcopy(data); invalid['migration']['preserve_budget_history'] = False
        with self.assertRaises(ValueError):
            validate_matrix(invalid)

    def test_major_candidate_uses_the_same_strict_stable_transition(self):
        data = json.loads((ROOT / 'release/candidate.template.json').read_text())
        data.update(version='3.0.0', developed_under_version='2.12.1')
        validate_candidate(data)
        for version in ('3.0.1', '3.1.0', '4.0.0'):
            with self.subTest(version=version):
                invalid = copy.deepcopy(data); invalid['version'] = version
                with self.assertRaises(ValueError):
                    validate_candidate(invalid)

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
