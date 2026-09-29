import unittest

from scripts.project_lanes import LaneClaim, LaneKind, admit_writer, paths_overlap
from scripts.project_lane_runtime import LaneRuntime, LaneState


class CooperativeLaneTests(unittest.TestCase):
    def claim(self, name, writes, kind=LaneKind.WORKER):
        return LaneClaim(
            lane_id=name,
            invocation_id=name,
            kind=kind,
            source_head="a" * 40,
            worktree=name,
            branch=name,
            write_paths=frozenset(writes),
        )

    def test_disjoint_writers_can_coexist(self):
        self.assertTrue(admit_writer([self.claim("a", {"src/a"})], self.claim("b", {"src/b"})))

    def test_parent_child_paths_overlap(self):
        self.assertTrue(paths_overlap(self.claim("a", {"src"}), self.claim("b", {"src/a"})))
        self.assertFalse(admit_writer([self.claim("a", {"src"})], self.claim("b", {"src/a"})))

    def test_portable_case_and_unicode_variants_overlap(self):
        self.assertTrue(paths_overlap(self.claim("a", {"SRC/Feature"}), self.claim("b", {"src/feature"})))
        self.assertTrue(paths_overlap(self.claim("a", {"docs/café"}), self.claim("b", {"docs/cafe\u0301"})))

    def test_read_only_lane_does_not_block_writer(self):
        self.assertTrue(admit_writer([self.claim("review", set(), LaneKind.REVIEW)], self.claim("worker", {"src/a"})))

    def test_integrator_is_singleton(self):
        existing = self.claim("i1", set(), LaneKind.INTEGRATOR)
        candidate = self.claim("i2", set(), LaneKind.INTEGRATOR)
        self.assertFalse(admit_writer([existing], candidate))

    def test_runtime_requires_fresh_heartbeat_and_drained_effects(self):
        runtime = LaneRuntime("lane", 1)
        runtime.heartbeat("activity-1")
        self.assertEqual(runtime.state, LaneState.RUNNING)
        runtime.pending_effects = True
        with self.assertRaises(ValueError):
            runtime.release()


if __name__ == "__main__":
    unittest.main()
