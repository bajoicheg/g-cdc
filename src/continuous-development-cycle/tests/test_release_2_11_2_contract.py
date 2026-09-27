import unittest
from pathlib import Path


class Release2112ContractTests(unittest.TestCase):
    def test_root_version_is_2112(self):
        version = Path("VERSION").read_text().strip()
        self.assertEqual(version, "2.11.2")

    def test_snapshot_validator_exists(self):
        validator = Path(
            "src/continuous-development-cycle/scripts/validate_snapshot_diagnostics.py"
        )
        self.assertTrue(validator.exists())


if __name__ == "__main__":
    unittest.main()
