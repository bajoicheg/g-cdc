"""End-to-end contract for the package-owned Chat/host -> managed executor bridge."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import execution_lease_v2 as leasev2
import managed_executor_pool as pool
from git_lease_store import GitLeaseStore
from managed_executor_store import GitManagedExecutorStore, coordination_store_id_for_endpoint
import managed_host_bridge as bridge


@unittest.skipUnless(sys.platform == "linux", "managed local backend requires Linux /proc")
class ManagedHostBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.remote = self.root / "remote.git"
        subprocess.run(["git", "init", "--bare", "-q", str(self.remote)], check=True)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "cdc@example.invalid")
        self.git("config", "user.name", "CDC Host Bridge Test")
        (self.repo / "seed").write_text("base")
        self.git("add", "seed")
        self.git("commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD")
        self.git("remote", "add", "origin", str(self.remote))
        self.git("push", "-q", "-u", "origin", "main")

        self.store_id = coordination_store_id_for_endpoint(str(self.remote), repo_root=self.repo)
        self.plan = {
            "schema": "managed-executor-pool-plan/v1",
            "pool_id": "host-bridge-pool",
            "change_id": "host-bridge-change",
            "parent_invocation_id": "chat-orchestrator",
            "base_sha": self.base,
            "integrator_id": "managed-host-bridge",
            "coordination_ref": "refs/heads/cdc/host-bridge-pool",
            "coordination_store_id": self.store_id,
            "max_parallel": 1,
            "total_runtime_budget_seconds": 30,
            "total_cost_budget_units": 5,
            "tasks": [{
                "id": "closure",
                "role": "writer",
                "required": True,
                "dependencies": [],
                "executor_id": "managed-closure",
                "branch": "cdc/host-bridge-worker",
                "worktree": "managed-worktrees/host-bridge-worker",
                "write_paths": ["docs"],
                "expected_outputs": ["out:closure"],
                "expected_evidence": ["test:closure"],
                "backend_preferences": ["local_command"],
                "max_runtime_seconds": 12,
                "max_cost_units": 1,
            }],
        }
        self.lease_store = GitLeaseStore(self.repo, "origin", "refs/heads/cdc/lease")
        self.lease_store.compare_and_swap(
            None, leasev2.initialize("test/project", "refs/heads/main"))

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.repo), *args], stderr=subprocess.PIPE, text=True
        ).strip()

    def worker(self):
        code = """from pathlib import Path
import subprocess
p=Path('docs'); p.mkdir(exist_ok=True)
(p/'closed.txt').write_text('closed')
subprocess.run(['git','add','docs/closed.txt'],check=True)
subprocess.run(['git','commit','-qm','managed closure'],check=True)
"""
        return [sys.executable, "-c", code]

    def start_request(self):
        return {
            "schema": "managed-host-start/v1",
            "repo_root": str(self.repo),
            "remote": "origin",
            "plan": self.plan,
            "journal_root": str(self.root / "journal"),
            "handle_root": str(self.root / "handles"),
            "lease_coordination_ref": "refs/heads/cdc/lease",
            "lease_repository": "test/project",
            "lease_source_ref": "refs/heads/main",
            "task_id": "closure",
            "attempt_id": "closure-a1",
            "reservation_token": "reserve:closure",
            "owner_id": "99999999-9999-4999-8999-999999999999",
            "argv": self.worker(),
        }

    def wait_for(self, handle, wanted):
        end = time.monotonic() + 8
        while time.monotonic() < end:
            observed = bridge.observe({
                "schema": "managed-host-observe/v1",
                "handle_root": str(self.root / "handles"),
                "handle_id": handle["handle_id"],
            })
            if observed["runtime_status"] == wanted:
                return observed
            time.sleep(.025)
        self.fail("managed host bridge did not reach " + wanted)

    def remote_head(self):
        row = subprocess.check_output(
            ["git", "-C", str(self.repo), "ls-remote", "--refs", "origin", "refs/heads/main"],
            text=True,
        ).strip()
        return row.split("\t", 1)[0]

    def test_start_holds_exact_managed_lease_then_finish_publishes_and_releases(self):
        handle = bridge.start(self.start_request())
        self.assertEqual(handle["schema"], "managed-host-handle/v1")
        self.assertEqual(handle["state"], "running")
        self.assertTrue(handle["invocation_id"].startswith("managed-terminal:"))

        waiting = self.wait_for(handle, "awaiting_release")
        lease_revision, lease = self.lease_store.read()
        self.assertIsNotNone(lease_revision)
        self.assertEqual(lease["owner_id"], handle["owner_id"])
        self.assertEqual(lease["generation"], handle["generation"])
        self.assertEqual(lease["invocation"]["execution_surface"], "managed")
        self.assertEqual(lease["invocation"]["invocation_id"], handle["invocation_id"])
        self.assertEqual(self.remote_head(), self.base, "worker must not publish shared source before finish")
        self.assertFalse(waiting["quiescent"])

        finished = bridge.finish({
            "schema": "managed-host-finish/v1",
            "handle_root": str(self.root / "handles"),
            "handle_id": handle["handle_id"],
            "output_refs": ["out:closure"],
            "evidence_refs": ["test:closure"],
            "checkpoint_ref": None,
        })
        self.assertEqual(finished["state"], "released")
        self.assertTrue(finished["final_response_allowed"])
        self.assertEqual(self.remote_head(), finished["published_commit"])
        self.assertNotEqual(finished["published_commit"], self.base)
        self.assertEqual(finished["release_receipt"]["schema"], "execution-release-receipt/v1")

        _, released = self.lease_store.read()
        self.assertIsNone(released["owner_id"])
        observed = self.wait_for(handle, "succeeded")
        self.assertTrue(observed["quiescent"])

        pool_store = GitManagedExecutorStore(
            self.repo, "origin", self.plan["coordination_ref"], self.plan,
            protected_refs=["refs/heads/main", "refs/heads/cdc/lease"],
        )
        _, pool_state = pool_store.read()
        assessment = pool.assess(self.plan, pool_state)
        self.assertTrue(assessment["complete"])
        self.assertTrue(assessment["terminal_allowed"])

    def test_start_rejects_remote_source_drift_before_worker_effect(self):
        request = self.start_request()
        request["plan"] = dict(self.plan, base_sha="a" * 40)
        with self.assertRaisesRegex(ValueError, "source HEAD"):
            bridge.start(request)
        self.assertFalse((self.root / "journal").exists())


if __name__ == "__main__":
    unittest.main()
