import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from project_lanes import LaneClaim, LaneKind

if importlib.util.find_spec("project_lane_git"):
    import project_lane_git
else:
    project_lane_git = None


def git(repo, *args, input_text=None):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout.strip()


class GitLaneResultVerifierTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(project_lane_git, "Git lane result verifier is not implemented")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "test@example.invalid")
        git(self.repo, "config", "user.name", "Test")
        (self.repo / "src/a").mkdir(parents=True)
        (self.repo / "src/b").mkdir(parents=True)
        (self.repo / "src/a/base.txt").write_text("a\n")
        (self.repo / "src/b/outside.txt").write_text("original\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.primary = git(self.repo, "branch", "--show-current")
        self.claim = LaneClaim(
            "lane", "inv", LaneKind.WORKER, self.base, str(self.repo), "worker",
            write_paths=frozenset({"src/a"}), executor_id="e", role="writer")
        self.verifier = project_lane_git.GitLaneResultVerifier(self.repo)

    def commit(self, path, text, message):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        git(self.repo, "add", str(path))
        git(self.repo, "commit", "-qm", message)
        return git(self.repo, "rev-parse", "HEAD")

    def test_descendant_result_reports_all_touched_paths(self):
        head = self.commit(Path("src/a/new.py"), "print(1)\n", "inside")
        result = self.verifier(self.claim, head)
        self.assertTrue(result["base_ancestor"])
        self.assertEqual(result["observed_base"], self.base)
        self.assertEqual(result["touched_paths"], {"src/a/new.py"})

    def test_non_descendant_result_is_not_accepted_as_ancestry(self):
        git(self.repo, "checkout", "-qb", "other", self.base)
        other = self.commit(Path("src/a/other.py"), "x\n", "other")
        git(self.repo, "checkout", "-q", self.primary)
        master = self.commit(Path("src/a/master.py"), "m\n", "master")
        self.assertTrue(self.verifier(self.claim, master)["base_ancestor"])
        unrelated = LaneClaim(
            "lane2", "inv2", LaneKind.WORKER, other, str(self.repo), "worker2",
            write_paths=frozenset({"src/a"}), executor_id="e", role="writer")
        self.assertFalse(self.verifier(unrelated, master)["base_ancestor"])

    def test_touched_and_restored_escape_is_still_reported(self):
        original = (self.repo / "src/b/outside.txt").read_text()
        self.commit(Path("src/b/outside.txt"), "changed\n", "outside")
        head = self.commit(Path("src/b/outside.txt"), original, "restore")
        self.assertEqual(git(self.repo, "diff", "--name-only", self.base + ".." + head), "")
        result = self.verifier(self.claim, head)
        self.assertIn("src/b/outside.txt", result["touched_paths"])

    def test_invalid_or_missing_commit_fails_closed(self):
        for value in ("main", "f" * 40):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.verifier(self.claim, value)


if __name__ == "__main__":
    unittest.main()
