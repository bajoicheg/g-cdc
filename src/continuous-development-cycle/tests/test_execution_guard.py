import sys
import unittest
from pathlib import Path

EXECUTION_DIR = Path(__file__).resolve().parents[1] / "execution"
sys.path.insert(0, str(EXECUTION_DIR))

from execution_guard import guard_command


class ExecutionGuardTests(unittest.TestCase):
    def test_f117_plan_loop_rejected(self):
        result = guard_command(
            "продолжай",
            "План: создать fleet supervisor следующим шагом сделаю архитектуру",
        )
        self.assertEqual(result, "REJECT")

    def test_action_result_allowed(self):
        result = guard_command(
            "разрабатывай",
            "Создан execution_guard.py и добавлен тест",
        )
        self.assertEqual(result, "ALLOW")

    def test_f118_false_blocker_requires_marker(self):
        result = guard_command(
            "делай",
            "BLOCKER: GitHub API returned permission denied",
        )
        self.assertEqual(result, "ALLOW")

    def test_non_execution_command_is_not_restricted(self):
        result = guard_command(
            "объясни",
            "План: можно обсудить архитектуру",
        )
        self.assertEqual(result, "ALLOW")


if __name__ == "__main__":
    unittest.main()
