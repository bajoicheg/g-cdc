import unittest


class SnapshotValidationDiagnosticsTests(unittest.TestCase):
    def test_diagnostic_message_contains_consumer_expected_and_actual(self):
        consumer = "g-supervisor"
        expected = "2.11.2"
        actual = "2.11.1"

        message = (
            f"snapshot validation failed consumer={consumer} "
            f"field=candidate_version expected={expected} actual={actual}"
        )

        self.assertIn("consumer=g-supervisor", message)
        self.assertIn("expected=2.11.2", message)
        self.assertIn("actual=2.11.1", message)


if __name__ == "__main__":
    unittest.main()
