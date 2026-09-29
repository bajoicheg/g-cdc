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
        write_paths=frozenset(writes), executor_id=name, role="writer")


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


def registry_config(store):
    return runtime.LaneRegistryConfig(
        canonical_repository="example/g-cdc",
        product_source_ref="refs/heads/main",
        coordination_ref=store.ref,
        coordination_store_id=store.store_id,
        policy_authority="sha256:" + "d" * 64,
    )


def coordinator(store=None, **kwargs):
    store = store or MemoryStore()
    return runtime.ProjectLaneCoordinator(store, registry_config(store), **kwargs)


def quiescent(lane, checkpoint):
    return {"quiescent": True, "evidence_ref": "process:stopped:" + checkpoint}


def verifier(observed_base=SHA, ancestor=True, touched=None):
    return lambda claim_value, result: {
        "observed_base": observed_base,
        "base_ancestor": ancestor,
        "touched_paths": set(touched if touched is not None else {"src/a/x.py"}),
    }


def activity_verifier(lane, activity_ref):
    return {"observed": True, "activity_ref": activity_ref,
            "evidence_ref": "process:activity:" + activity_ref}


def integration_verifier(item, integrator):
    return {
        "integrated": True,
        "result_commit": item["result_commit"],
        "observed_shared_head": "c" * 40,
        "integrated_head": "d" * 40,
        "force_push": False,
        "evidence_ref": "git:conditional-integration",
    }


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
        lane = claim("a", {"src/a", "docs/readme.md"})
        self.assertTrue(lanes.result_within_claim(lane, {"src/a/x.py", "docs/readme.md"}))
        self.assertFalse(lanes.result_within_claim(lane, {"src/a/x.py", "src/b/y.py"}))

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
        coord = coordinator()
        self.assertTrue(coord.admit(
            claim("fg", {"src/ui"}, lanes.LaneKind.FOREGROUND), generation=1)["admitted"])
        self.assertTrue(coord.admit(
            claim("wd", {"src/backend"}, lanes.LaneKind.WATCHDOG), generation=1)["admitted"])
        self.assertEqual(len(coord.snapshot()["lanes"]), 2)

    def test_coordinator_blocks_overlap_before_mutation_and_release_is_identity_bound(self):
        coord = coordinator()
        coord.admit(claim("a", {"src"}), generation=1)
        blocked = coord.admit(claim("b", {"src/b"}), generation=1)
        self.assertFalse(blocked["admitted"])
        self.assertEqual(blocked["reason"], "write_claim_conflict")
        with self.assertRaises(ValueError):
            coord.release("a", invocation_id="other", generation=1, executor_id="a", checkpoint_ref="cp-a")
        coord.release("a", invocation_id="a", generation=1, executor_id="a", checkpoint_ref="cp-a")
        self.assertEqual(coord.snapshot()["lanes"]["a"]["state"], "released")

    def test_handoff_requires_checkpoint_and_independent_quiescence(self):
        store = MemoryStore()
        coordinator = globals()["coordinator"](store)
        coordinator.admit(claim("a", {"src/a"}), generation=1)
        with self.assertRaises(ValueError):
            coordinator.handoff("a", invocation_id="a", generation=1, executor_id="a", checkpoint_ref=None)
        with self.assertRaises(ValueError):
            coordinator.handoff("a", invocation_id="a", generation=1, executor_id="a", checkpoint_ref="cp-1")
        coordinator = globals()["coordinator"](store, quiescence_verifier=quiescent)
        coordinator.handoff("a", invocation_id="a", generation=1, executor_id="a", checkpoint_ref="cp-1")
        self.assertEqual(coordinator.snapshot()["lanes"]["a"]["state"], "handoff_ready")

    def test_heartbeat_requires_independent_observable_activity(self):
        coord = coordinator()
        coord.admit(claim("a", {"src/a"}), generation=1)
        with self.assertRaisesRegex(ValueError, "activity verifier"):
            coord.heartbeat("a", invocation_id="a", generation=1, executor_id="a", activity_ref="commit:a")
        coord = coordinator(activity_verifier=activity_verifier)
        coord.admit(claim("a", {"src/a"}), generation=1)
        coord.heartbeat("a", invocation_id="a", generation=1, executor_id="a", activity_ref="commit:a")
        with self.assertRaises(ValueError):
            coord.heartbeat("a", invocation_id="a", generation=1, executor_id="a", activity_ref="commit:a")

    def test_release_requires_bound_executor_and_checkpoint(self):
        coord = coordinator()
        coord.admit(claim("a", {"src/a"}), generation=1)
        with self.assertRaises(ValueError):
            coord.release("a", invocation_id="a", generation=1, executor_id="other", checkpoint_ref="cp-a")
        with self.assertRaises(ValueError):
            coord.release("a", invocation_id="a", generation=1, executor_id="a", checkpoint_ref=None)

    def test_successful_writer_result_survives_lane_release_until_integrated(self):
        coord = coordinator(result_verifier=verifier(), integration_verifier=integration_verifier)
        coord.admit(claim("a", {"src/a"}), generation=1)
        coord.record_result(
            "a", invocation_id="a", generation=1, executor_id="a", result_commit="b" * 40,
            evidence_refs=["test:green"])
        coord.release("a", invocation_id="a", generation=1, executor_id="a", checkpoint_ref="cp-a")
        self.assertEqual(len(coord.snapshot()["integration_queue"]), 1)
        self.assertFalse(coord.can_finalize(runnable_task_count=0, unknown_effect_count=0))
        coord.admit(claim("integrator", (), lanes.LaneKind.INTEGRATOR), generation=1)
        coord.mark_integrated(
            "a", result_commit="b" * 40, integrator_lane_id="integrator",
            integrator_invocation_id="integrator", integrator_generation=1, integrator_executor_id="integrator")
        coord.release("integrator", invocation_id="integrator", generation=1, executor_id="integrator", checkpoint_ref="cp-integrator")
        self.assertTrue(coord.can_finalize(runnable_task_count=0, unknown_effect_count=0))

    def test_result_rejects_stale_base_unverified_ancestry_or_path_escape(self):
        for check in (
            verifier("c" * 40, True, {"src/a/x.py"}),
            verifier(SHA, False, {"src/a/x.py"}),
            verifier(SHA, True, {"src/b/x.py"}),
        ):
            coord = coordinator(result_verifier=check)
            coord.admit(claim("a", {"src/a"}), generation=1)
            with self.assertRaises(ValueError):
                coord.record_result(
                    "a", invocation_id="a", generation=1, executor_id="a", result_commit="b" * 40,
                    evidence_refs=["test:green"])


if __name__ == "__main__":
    unittest.main()
