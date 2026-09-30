import copy
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


class MemoryAttemptStore:
    def __init__(self, store_id):
        self.ref = "refs/heads/cdc/integration-publication-attempts"
        self.store_id = store_id
        self.rev = 0
        self.value = None

    def read(self):
        return self.rev, copy.deepcopy(self.value)

    def compare_and_swap(self, expected, value):
        if expected != self.rev:
            raise ValueError("stale publication attempt state")
        self.rev += 1
        self.value = copy.deepcopy(value)
        return str(self.rev)


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

    def test_integration_verifier_proves_result_and_observed_head_ancestry(self):
        git(self.repo, "checkout", "-qb", "worker-result", self.base)
        result_commit = self.commit(Path("src/a/integrated.py"), "ok\n", "worker result")
        git(self.repo, "checkout", "-q", self.primary)
        git(self.repo, "merge", "--ff-only", "worker-result")
        integrator = LaneClaim(
            "integrator", "integrator-inv", LaneKind.INTEGRATOR, self.base,
            str(self.repo), self.primary, executor_id="integrator", role="integrator")
        verifier = project_lane_git.GitLaneIntegrationVerifier(
            self.repo, "refs/heads/" + self.primary)
        evidence = verifier(
            {"lane_id": "lane", "result_commit": result_commit},
            integrator,
            {"lane_id": "lane", "result_commit": result_commit,
             "observed_shared_head": self.base,
             "intended_integrated_head": result_commit,
             "operation_id": "op-1"})
        self.assertTrue(evidence["integrated"])
        self.assertEqual(evidence["integrated_head"], result_commit)
        self.assertFalse(evidence["conditional_update"])
        self.assertFalse(evidence["force_push"])

    def test_integration_verifier_rejects_result_not_present_on_shared_head(self):
        git(self.repo, "checkout", "-qb", "worker-result", self.base)
        result_commit = self.commit(Path("src/a/not-integrated.py"), "no\n", "worker result")
        git(self.repo, "checkout", "-q", self.primary)
        integrator = LaneClaim(
            "integrator", "integrator-inv", LaneKind.INTEGRATOR, self.base,
            str(self.repo), self.primary, executor_id="integrator", role="integrator")
        verifier = project_lane_git.GitLaneIntegrationVerifier(
            self.repo, "refs/heads/" + self.primary)
        with self.assertRaisesRegex(ValueError, "ancestry"):
            verifier(
                {"lane_id": "lane", "result_commit": result_commit},
                integrator,
                {"lane_id": "lane", "result_commit": result_commit,
                 "observed_shared_head": self.base,
                 "intended_integrated_head": result_commit,
                 "operation_id": "op-1"})

    def test_integration_publisher_performs_exact_head_conditional_fast_forward(self):
        remote = self.repo / "remote.git"
        subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
        git(self.repo, "remote", "add", "origin", str(remote))
        git(self.repo, "push", "-q", "origin", self.base + ":refs/heads/integration")

        git(self.repo, "checkout", "-qb", "worker-publish", self.base)
        result_commit = self.commit(Path("src/a/published.py"), "ok\n", "published result")
        git(self.repo, "checkout", "-q", self.primary)
        integrator = LaneClaim(
            "integrator", "integrator-inv", LaneKind.INTEGRATOR, self.base,
            str(self.repo), self.primary, executor_id="integrator", role="integrator")
        remote_id = project_lane_git.remote_identity(self.repo, "origin")
        attempts = MemoryAttemptStore(remote_id)
        publisher = project_lane_git.GitLaneIntegrationPublisher(
            self.repo, "origin", "refs/heads/integration", remote_id,
            attempt_store=attempts, clock=lambda: "2026-09-30T15:00:00Z")
        item = {"lane_id": "lane", "result_commit": result_commit}
        intent = {
            "lane_id": "lane", "result_commit": result_commit,
            "observed_shared_head": self.base,
            "intended_integrated_head": result_commit,
            "operation_id": "op-cas",
        }
        seen = {}
        original_run = publisher._run
        def inspect_before_push(*args, **kwargs):
            if "push" in args:
                _, state = attempts.read()
                seen["attempt"] = copy.deepcopy(state["attempts"]["op-cas"])
            return original_run(*args, **kwargs)
        publisher._run = inspect_before_push
        evidence = publisher(item, integrator, intent)
        self.assertTrue(evidence["conditional_update"])
        self.assertFalse(evidence["force_push"])
        self.assertEqual(evidence["integrated_head"], result_commit)
        self.assertEqual(seen["attempt"]["status"], "submitting")
        self.assertEqual(seen["attempt"]["operation_id"], "op-cas")
        self.assertEqual(attempts.read()[1]["attempts"]["op-cas"]["status"], "confirmed")
        remote_head = subprocess.check_output(
            ["git", "--git-dir", str(remote), "rev-parse", "refs/heads/integration"],
            text=True).strip()
        self.assertEqual(remote_head, result_commit)
        # Confirmed retry is read-only and retains the same durable attempt identity.
        retry = publisher(item, integrator, intent)
        self.assertEqual(retry["attempt_id"], evidence["attempt_id"])
        self.assertTrue(retry["conditional_update"])

    def test_lost_push_reply_recovers_from_same_durable_attempt_without_second_push(self):
        remote = self.repo / "remote-lost.git"
        subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
        git(self.repo, "remote", "add", "lost", str(remote))
        git(self.repo, "push", "-q", "lost", self.base + ":refs/heads/integration")
        git(self.repo, "checkout", "-qb", "worker-lost", self.base)
        result_commit = self.commit(Path("src/a/lost.py"), "ok\n", "worker result")
        git(self.repo, "checkout", "-q", self.primary)
        integrator = LaneClaim(
            "integrator", "integrator-inv", LaneKind.INTEGRATOR, self.base,
            str(self.repo), self.primary, executor_id="integrator", role="integrator")
        remote_id = project_lane_git.remote_identity(self.repo, "lost")
        attempts = MemoryAttemptStore(remote_id)
        publisher = project_lane_git.GitLaneIntegrationPublisher(
            self.repo, "lost", "refs/heads/integration", remote_id,
            attempt_store=attempts, clock=lambda: "2026-09-30T15:01:00Z")
        item = {"lane_id": "lane", "result_commit": result_commit}
        intent = {
            "lane_id": "lane", "result_commit": result_commit,
            "observed_shared_head": self.base,
            "intended_integrated_head": result_commit,
            "operation_id": "op-lost",
        }
        original_head = publisher._remote_head
        reads = {"count": 0}
        def lose_post_push_readback():
            reads["count"] += 1
            value = original_head()
            if reads["count"] == 2:
                raise ValueError("simulated lost publication reply")
            return value
        publisher._remote_head = lose_post_push_readback
        with self.assertRaisesRegex(ValueError, "unknown|reply|publication"):
            publisher(item, integrator, intent)
        prior = copy.deepcopy(attempts.read()[1]["attempts"]["op-lost"])
        self.assertEqual(prior["status"], "unknown")

        recovered = project_lane_git.GitLaneIntegrationPublisher(
            self.repo, "lost", "refs/heads/integration", remote_id,
            attempt_store=attempts, clock=lambda: "2026-09-30T15:02:00Z")
        pushes = []
        original_run = recovered._run
        def count_pushes(*args, **kwargs):
            if "push" in args:
                pushes.append(args)
            return original_run(*args, **kwargs)
        recovered._run = count_pushes
        evidence = recovered(item, integrator, intent)
        self.assertTrue(evidence["conditional_update"])
        self.assertEqual(evidence["attempt_id"], prior["attempt_id"])
        self.assertEqual(pushes, [])
        self.assertEqual(attempts.read()[1]["attempts"]["op-lost"]["status"], "confirmed")

    def test_preexisting_intended_remote_head_is_readback_only_without_this_intents_cas(self):
        remote = self.repo / "remote-preexisting.git"
        subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
        git(self.repo, "remote", "add", "preexisting", str(remote))
        git(self.repo, "push", "-q", "preexisting", self.base + ":refs/heads/integration")

        git(self.repo, "checkout", "-qb", "worker-preexisting", self.base)
        result_commit = self.commit(Path("src/a/preexisting.py"), "ok\n", "worker result")
        git(self.repo, "push", "-q", "preexisting", result_commit + ":refs/heads/integration")
        git(self.repo, "checkout", "-q", self.primary)

        integrator = LaneClaim(
            "integrator", "integrator-inv", LaneKind.INTEGRATOR, self.base,
            str(self.repo), self.primary, executor_id="integrator", role="integrator")
        remote_id = project_lane_git.remote_identity(self.repo, "preexisting")
        attempts = MemoryAttemptStore(remote_id)
        publisher = project_lane_git.GitLaneIntegrationPublisher(
            self.repo, "preexisting", "refs/heads/integration", remote_id,
            attempt_store=attempts, clock=lambda: "2026-09-30T15:03:00Z")
        evidence = publisher(
            {"lane_id": "lane", "result_commit": result_commit},
            integrator,
            {"lane_id": "lane", "result_commit": result_commit,
             "observed_shared_head": self.base,
             "intended_integrated_head": result_commit,
             "operation_id": "op-preexisting"})
        self.assertFalse(evidence["conditional_update"])
        self.assertIsNone(evidence["attempt_id"])
        self.assertTrue(attempts.read()[1] is None or attempts.read()[1]["attempts"] == {})

    def test_integration_publisher_persists_durable_attempt_state_before_push(self):
        remote = self.repo / "remote-no-attempt.git"
        subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
        git(self.repo, "remote", "add", "noattempt", str(remote))
        git(self.repo, "push", "-q", "noattempt", self.base + ":refs/heads/integration")
        git(self.repo, "checkout", "-qb", "worker-no-attempt", self.base)
        result_commit = self.commit(Path("src/a/noattempt.py"), "ok\n", "worker result")
        git(self.repo, "checkout", "-q", self.primary)
        integrator = LaneClaim(
            "integrator", "integrator-inv", LaneKind.INTEGRATOR, self.base,
            str(self.repo), self.primary, executor_id="integrator", role="integrator")
        remote_id = project_lane_git.remote_identity(self.repo, "noattempt")
        attempts = MemoryAttemptStore(remote_id)
        publisher = project_lane_git.GitLaneIntegrationPublisher(
            self.repo, "noattempt", "refs/heads/integration", remote_id,
            attempt_store=attempts, clock=lambda: "2026-09-30T15:04:00Z")
        seen = {}
        original_run = publisher._run
        def inspect(*args, **kwargs):
            if "push" in args:
                seen["attempt"] = copy.deepcopy(attempts.read()[1]["attempts"]["op-no-attempt"])
            return original_run(*args, **kwargs)
        publisher._run = inspect
        evidence = publisher(
            {"lane_id": "lane", "result_commit": result_commit},
            integrator,
            {"lane_id": "lane", "result_commit": result_commit,
             "observed_shared_head": self.base,
             "intended_integrated_head": result_commit,
             "operation_id": "op-no-attempt"})
        self.assertEqual(seen["attempt"]["status"], "submitting")
        self.assertTrue(evidence["conditional_update"])

    def test_rejected_attempt_cannot_be_upgraded_by_later_matching_head(self):
        remote = self.repo / "remote-rejected.git"
        subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
        git(self.repo, "remote", "add", "rejected", str(remote))
        git(self.repo, "push", "-q", "rejected", self.base + ":refs/heads/integration")
        git(self.repo, "checkout", "-qb", "worker-rejected", self.base)
        result_commit = self.commit(Path("src/a/rejected.py"), "ok\n", "worker result")
        git(self.repo, "checkout", "-q", self.primary)
        integrator = LaneClaim(
            "integrator", "integrator-inv", LaneKind.INTEGRATOR, self.base,
            str(self.repo), self.primary, executor_id="integrator", role="integrator")
        remote_id = project_lane_git.remote_identity(self.repo, "rejected")
        attempts = MemoryAttemptStore(remote_id)
        publisher = project_lane_git.GitLaneIntegrationPublisher(
            self.repo, "rejected", "refs/heads/integration", remote_id,
            attempt_store=attempts, clock=lambda: "2026-09-30T15:05:00Z")
        original_run = publisher._run
        def reject_push(*args, **kwargs):
            if "push" in args:
                return "!\trefs/heads/integration\t[rejected] stale info", 1
            return original_run(*args, **kwargs)
        publisher._run = reject_push
        item = {"lane_id": "lane", "result_commit": result_commit}
        intent = {
            "lane_id": "lane", "result_commit": result_commit,
            "observed_shared_head": self.base,
            "intended_integrated_head": result_commit,
            "operation_id": "op-rejected",
        }
        with self.assertRaisesRegex(ValueError, "rejected"):
            publisher(item, integrator, intent)
        self.assertEqual(attempts.read()[1]["attempts"]["op-rejected"]["status"], "rejected")
        git(self.repo, "push", "-q", "rejected", result_commit + ":refs/heads/integration")
        recovered = project_lane_git.GitLaneIntegrationPublisher(
            self.repo, "rejected", "refs/heads/integration", remote_id,
            attempt_store=attempts, clock=lambda: "2026-09-30T15:06:00Z")
        with self.assertRaisesRegex(ValueError, "rejected"):
            recovered(item, integrator, intent)

    def test_attempt_for_other_result_does_not_prove_matching_head(self):
        remote = self.repo / "remote-mismatch.git"
        subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
        git(self.repo, "remote", "add", "mismatch", str(remote))
        git(self.repo, "push", "-q", "mismatch", self.base + ":refs/heads/integration")
        git(self.repo, "checkout", "-qb", "worker-mismatch", self.base)
        result_commit = self.commit(Path("src/a/mismatch.py"), "ok\n", "worker result")
        git(self.repo, "push", "-q", "mismatch", result_commit + ":refs/heads/integration")
        git(self.repo, "checkout", "-q", self.primary)
        remote_id = project_lane_git.remote_identity(self.repo, "mismatch")
        attempts = MemoryAttemptStore(remote_id)
        attempts.value = {
            "schema": "lane-integration-publication-attempts/v1",
            "remote_id": remote_id,
            "source_ref": "refs/heads/integration",
            "attempts": {
                "op-mismatch": {
                    "attempt_id": "lane-publication-mismatch",
                    "operation_id": "op-mismatch",
                    "result_commit": "f" * 40,
                    "observed_shared_head": self.base,
                    "intended_integrated_head": result_commit,
                    "remote_id": remote_id,
                    "source_ref": "refs/heads/integration",
                    "status": "unknown",
                    "created_at_utc": "2026-09-30T15:00:00Z",
                    "updated_at_utc": "2026-09-30T15:00:00Z",
                    "detail": "test mismatch",
                }
            },
        }
        integrator = LaneClaim(
            "integrator", "integrator-inv", LaneKind.INTEGRATOR, self.base,
            str(self.repo), self.primary, executor_id="integrator", role="integrator")
        publisher = project_lane_git.GitLaneIntegrationPublisher(
            self.repo, "mismatch", "refs/heads/integration", remote_id,
            attempt_store=attempts, clock=lambda: "2026-09-30T15:07:00Z")
        with self.assertRaisesRegex(ValueError, "attempt.*bind|binding|result"):
            publisher(
                {"lane_id": "lane", "result_commit": result_commit},
                integrator,
                {"lane_id": "lane", "result_commit": result_commit,
                 "observed_shared_head": self.base,
                 "intended_integrated_head": result_commit,
                 "operation_id": "op-mismatch"})

    def test_integration_publisher_rejects_remote_head_movement_without_overwrite(self):
        remote = self.repo / "remote-race.git"
        subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
        git(self.repo, "remote", "add", "race", str(remote))
        git(self.repo, "push", "-q", "race", self.base + ":refs/heads/integration")

        git(self.repo, "checkout", "-qb", "worker-race", self.base)
        result_commit = self.commit(Path("src/a/race.py"), "worker\n", "worker result")
        git(self.repo, "checkout", "-qb", "concurrent", self.base)
        concurrent = self.commit(Path("src/b/concurrent.py"), "other\n", "concurrent")
        git(self.repo, "push", "-q", "race", concurrent + ":refs/heads/integration")
        git(self.repo, "checkout", "-q", self.primary)

        integrator = LaneClaim(
            "integrator", "integrator-inv", LaneKind.INTEGRATOR, self.base,
            str(self.repo), self.primary, executor_id="integrator", role="integrator")
        remote_id = project_lane_git.remote_identity(self.repo, "race")
        publisher = project_lane_git.GitLaneIntegrationPublisher(
            self.repo, "race", "refs/heads/integration", remote_id,
            attempt_store=MemoryAttemptStore(remote_id),
            clock=lambda: "2026-09-30T15:08:00Z")
        with self.assertRaisesRegex(ValueError, "moved"):
            publisher(
                {"lane_id": "lane", "result_commit": result_commit},
                integrator,
                {"lane_id": "lane", "result_commit": result_commit,
                 "observed_shared_head": self.base,
                 "intended_integrated_head": result_commit,
                 "operation_id": "op-race"})
        remote_head = subprocess.check_output(
            ["git", "--git-dir", str(remote), "rev-parse", "refs/heads/integration"],
            text=True).strip()
        self.assertEqual(remote_head, concurrent)

    def test_invalid_or_missing_commit_fails_closed(self):
        for value in ("main", "f" * 40):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.verifier(self.claim, value)


if __name__ == "__main__":
    unittest.main()
