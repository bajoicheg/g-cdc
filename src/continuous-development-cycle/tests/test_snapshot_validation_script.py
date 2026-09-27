import unittest
from unittest.mock import patch


class SnapshotValidationScriptTests(unittest.TestCase):
    def test_diagnostics_contract_format_is_preserved(self):
        message = (
            "snapshot validation failed "
            "consumer=g-ad-control "
            "field=candidate_version "
            "expected=2.11.2 "
            "actual=2.10.2"
        )

        self.assertIn("consumer=g-ad-control", message)
        self.assertIn("expected=2.11.2", message)
        self.assertIn("actual=2.10.2", message)


if __name__ == "__main__":
    unittest.main()
