from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from project_lanes import LaneClaim, LaneKind, admit_writer, paths_overlap


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

    def test_unsafe_git_branch_names_are_rejected(self):
        for branch_name in ("--force", "refs/tags/not-a-lane", "refs/heads/bad ref",
                            "refs/heads/a..b", "refs/heads/.hidden"):
            value = self.claim("unsafe", {"src/a"})
            value = LaneClaim(
                lane_id=value.lane_id, invocation_id=value.invocation_id,
                kind=value.kind, source_head=value.source_head,
                worktree=value.worktree, branch=branch_name,
                write_paths=value.write_paths)
            with self.subTest(branch=branch_name), self.assertRaises(ValueError):
                admit_writer([], value)

    def test_integrator_is_singleton(self):
        existing = self.claim("i1", set(), LaneKind.INTEGRATOR)
        candidate = self.claim("i2", set(), LaneKind.INTEGRATOR)
        self.assertFalse(admit_writer([existing], candidate))


if __name__ == "__main__":
    unittest.main()
