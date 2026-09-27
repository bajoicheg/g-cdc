import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import execution_lease_v2 as lease


class ExecutionRequiredLeaseTests(unittest.TestCase):

    def setUp(self):
        self.record = lease.initialize(
            "example/project",
            "refs/heads/main"
        )

        self.record = lease.acquire(
            self.record,
            "11111111-1111-4111-8111-111111111111",
            "2026-09-27T20:00:00Z",
            invocation={
                "invocation_id": "test-execution-required",
                "automation_id": None,
                "conversation_id": None,
                "execution_surface": "chat",
                "execution_required": True,
                "started_at_utc": "2026-09-27T20:00:00Z",
            },
        )


    def test_execution_required_cannot_finalize_plan_only(self):
        broken = copy.deepcopy(self.record)

        broken["finalization"]["state"] = "plan_only"

        with self.assertRaises(ValueError):
            lease.validate(broken)


    def test_execution_required_allows_real_execution_state(self):
        valid = copy.deepcopy(self.record)

        valid["finalization"]["state"] = "checkpointed"
        valid["finalization"]["checkpoint_ref"] = "checkpoint-1"

        self.assertEqual(
            lease.validate(valid),
            valid
        )


if __name__ == "__main__":
    unittest.main()
