import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import project_lanes as lanes
import project_lane_runtime as runtime

SHA = "a" * 40


def claim(name, writes=(), kind=lanes.LaneKind.WORKER, branch=None, worktree=None, invocation=None):
    return lanes.LaneClaim(
        lane_id=name, invocation_id=invocation or name, kind=kind, source_head=SHA,
        worktree=worktree or f"/tmp/{name}", branch=branch or f"cdc/{name}",
        write_paths=frozenset(writes), executor_id=name, role="writer"
    )


class MemoryStore:
    ref = "refs/heads/cdc/project-lanes"
    store_id = "sha256:" + "c" * 64

    def __init__(self):
        self.rev = 0
        self.value = None

    def read(self):
        return self.rev, copy.deepcopy(self.value)

    def compare_and_swap(self, expected, value):
        if expected != self.rev:
            raise ValueError("stale")
        self.rev += 1
        self.value = copy.deepcopy(value)
        return str(self.rev)


class CooperativeLaneExtendedTests(unittest.TestCase):
    def test_integrator_is_singleton_but_does_not_block_isolated_writer(self):
        integrator = claim("i", (), lanes.LaneKind.INTEGRATOR)
        self.assertTrue(lanes.admit_writer([integrator], claim("w", {"src/a"})))
        self.assertFalse(lanes.admit_writer([integrator], claim("i2", (), lanes.LaneKind.INTEGRATOR)))

    def test_duplicate_branch_or_worktree_blocks_writer_even_when_paths_are_disjoint(self):
        a = claim("a", {"src/a"}, branch="cdc/shared", worktree="/tmp/a")
        self.assertFalse(lanes.admit_writer([a], claim("b", {"src/b"}, branch="cdc/shared", worktree="/tmp/b")))
        self.assertFalse(lanes.admit_writer([a], claim("b", {"src/b"}, branch="cdc/b", worktree="/tmp/a")))

    def test_unsafe_or_nonportable_claim_paths_fail_closed(self):
        for path in ("../escape", "/absolute", "src//double", "src/../escape", "CON/file"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                lanes.validate_claim(claim("bad", {path}))

    def test_result_touched_paths_must_stay_within_original_write_claim(self):
        c = claim("a", {"src/a", "docs/readme.md"})
        self.assertTrue(lanes.result_within_claim(c, {"src/a/x.py", "docs/readme.md"}))
        self.assertFalse(lanes.result_within_claim(c, {"src/a/x.py", "src/b/y.py"}))

    def test_project_completion_aggregates_lanes_queue_results_and_unknown_effects(self):
        self.assertTrue(lanes.project_can_finalize(
            active_lane_count=0, runnable_task_count=0, pending_result_count=0, unknown_effect_count=0))
        for kwargs in (
            {"active_lane_count": 1, "runnable_task_count": 0, "pending_result_count": 0, "unknown_effect_count": 0},
            {"active_lane_count": 0, "runnable_task_count": 1, "pending_result_count": 0, "unknown_effect_count": 0},
            {"active_lane_count": 0, "runnable_task_count": 0, "pending_result_count": 1, "unknown_effect_count": 0},
            {"active_lane_count": 0, "runnable_task_count": 0, "pending_result_count": 0, "unknown_effect_count": 1},
        ):
            with self.subTest(kwargs=kwargs):
                self.assertFalse(lanes.project_can_finalize(**kwargs))

    def test_durable_coordinator_admits_disjoint_foreground_and_watchdog_lanes(self):
        c = runtime.ProjectLaneCoordinator(MemoryStore())
        foreground = claim("fg", {"src/ui"}, lanes.LaneKind.FOREGROUND)
        watchdog = claim("wd", {"src/backend"}, lanes.LaneKind.WATCHDOG)
        self.assertTrue(c.admit(foreground, generation=1)["admitted"])
        self.assertTrue(c.admit(watchdog, generation=1)["admitted"])
        snap = c.snapshot()
        self.assertEqual({v["state"] for v in snap["lanes"].values()}, {"running"})
        self.assertEqual(len(snap["lanes"]), 2)

    def test_coordinator_blocks_overlap_before_mutation_and_release_is_identity_bound(self):
        c = runtime.ProjectLaneCoordinator(MemoryStore())
        a = claim("a", {"src"})
        b = claim("b", {"src/b"})
        c.admit(a, generation=1)
        blocked = c.admit(b, generation=1)
        self.assertFalse(blocked["admitted"])
        self.assertEqual(blocked["reason"], "write_claim_conflict")
        with self.assertRaises(ValueError):
            c.release("a", invocation_id="other", generation=1)
        c.release("a", invocation_id="a", generation=1)
        self.assertEqual(c.snapshot()["lanes"]["a"]["state"], "released")

    def test_handoff_requires_checkpoint_and_quiescence_not_ttl(self):
        c = runtime.ProjectLaneCoordinator(MemoryStore())
        c.admit(claim("a", {"src/a"}), generation=1)
        with self.assertRaises(ValueError):
            c.handoff("a", invocation_id="a", generation=1, checkpoint_ref=None, executor_quiescent=False)
        with self.assertRaises(ValueError):
            c.handoff("a", invocation_id="a", generation=1, checkpoint_ref="cp-1", executor_quiescent=False)
        c.handoff("a", invocation_id="a", generation=1, checkpoint_ref="cp-1", executor_quiescent=True)
        self.assertEqual(c.snapshot()["lanes"]["a"]["state"], "handoff_ready")

    def test_successful_writer_result_survives_lane_release_until_integrated(self):
        c = runtime.ProjectLaneCoordinator(MemoryStore())
        a = claim("a", {"src/a"})
        c.admit(a, generation=1)
        c.record_result(
            "a", invocation_id="a", generation=1, result_commit="b" * 40,
            observed_base=SHA, base_ancestor=True, touched_paths={"src/a/x.py"}, evidence_refs=["test:green"])
        c.release("a", invocation_id="a", generation=1)
        snap = c.snapshot()
        self.assertEqual(len(snap["integration_queue"]), 1)
        self.assertFalse(c.can_finalize(runnable_task_count=0, unknown_effect_count=0))
        c.mark_integrated("a", result_commit="b" * 40, integrator_lane_id="integrator")
        self.assertTrue(c.can_finalize(runnable_task_count=0, unknown_effect_count=0))

    def test_result_rejects_stale_base_unverified_ancestry_or_path_escape(self):
        for observed_base, ancestor, touched in (
            ("c" * 40, True, {"src/a/x.py"}),
            (SHA, False, {"src/a/x.py"}),
            (SHA, True, {"src/b/x.py"}),
        ):
            c = runtime.ProjectLaneCoordinator(MemoryStore())
            c.admit(claim("a", {"src/a"}), generation=1)
            with self.subTest(observed_base=observed_base, ancestor=ancestor, touched=touched), self.assertRaises(ValueError):
                c.record_result(
                    "a", invocation_id="a", generation=1, result_commit="b" * 40,
                    observed_base=observed_base, base_ancestor=ancestor,
                    touched_paths=touched, evidence_refs=["test:green"])


if __name__ == "__main__":
    unittest.main()
