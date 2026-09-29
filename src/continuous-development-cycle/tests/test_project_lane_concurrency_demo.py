import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from project_lanes import LaneClaim, LaneKind
from project_lane_runtime import ProjectLaneCoordinator


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


class MemoryStore:
    ref = "refs/heads/cdc/project-lanes-demo"
    store_id = "sha256:" + "d" * 64

    def __init__(self):
        self.rev = 0
        self.value = None

    def read(self):
        import copy
        return self.rev, copy.deepcopy(self.value)

    def compare_and_swap(self, expected, value):
        import copy
        if expected != self.rev:
            raise ValueError("stale")
        self.rev += 1
        self.value = copy.deepcopy(value)
        return str(self.rev)


class CooperativeLaneProcessDemoTests(unittest.TestCase):
    def test_foreground_and_watchdog_run_concurrently_in_disjoint_git_worktrees(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            repo = root / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            git(repo, "config", "user.email", "cdc@example.invalid")
            git(repo, "config", "user.name", "CDC test")
            (repo / "src").mkdir()
            (repo / "src/base.txt").write_text("base\n")
            git(repo, "add", ".")
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
            base = git(repo, "rev-parse", "HEAD")

            fg = root / "fg"
            wd = root / "wd"
            subprocess.run(["git", "-C", str(repo), "worktree", "add", "-qb", "lane-fg", str(fg), base], check=True)
            subprocess.run(["git", "-C", str(repo), "worktree", "add", "-qb", "lane-wd", str(wd), base], check=True)

            coordinator = ProjectLaneCoordinator(MemoryStore())
            claims = [
                LaneClaim("foreground", "fg-inv", LaneKind.FOREGROUND, base, str(fg), "lane-fg",
                          write_paths=frozenset({"src/fg"}), executor_id="fg", role="writer"),
                LaneClaim("watchdog", "wd-inv", LaneKind.WATCHDOG, base, str(wd), "lane-wd",
                          write_paths=frozenset({"src/wd"}), executor_id="wd", role="writer"),
            ]
            for claim in claims:
                self.assertTrue(coordinator.admit(claim, generation=1)["admitted"])

            worker = root / "worker.py"
            worker.write_text(
                "from pathlib import Path\n"
                "import sys,time\n"
                "root=Path(sys.argv[1]); name=sys.argv[2]\n"
                "target=root/'src'/name; target.mkdir(parents=True,exist_ok=True)\n"
                "(target/'result.txt').write_text(name+'\\n')\n"
                "(root/(name+'.ready')).write_text('ready')\n"
                "release=root/(name+'.release')\n"
                "while not release.exists(): time.sleep(0.02)\n"
            )
            processes = [
                subprocess.Popen([sys.executable, str(worker), str(fg), "fg"]),
                subprocess.Popen([sys.executable, str(worker), str(wd), "wd"]),
            ]
            try:
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline:
                    if (fg / "fg.ready").exists() and (wd / "wd.ready").exists():
                        break
                    time.sleep(0.02)
                self.assertTrue((fg / "fg.ready").exists())
                self.assertTrue((wd / "wd.ready").exists())
                self.assertTrue(all(process.poll() is None for process in processes))
                self.assertTrue((fg / "src/fg/result.txt").exists())
                self.assertFalse((fg / "src/wd").exists())
                self.assertTrue((wd / "src/wd/result.txt").exists())
                self.assertFalse((wd / "src/fg").exists())

                scheduler_mutations = []
                self.assertEqual(scheduler_mutations, [])
            finally:
                (fg / "fg.release").write_text("go")
                (wd / "wd.release").write_text("go")
                for process in processes:
                    process.wait(timeout=5)

            coordinator.release("foreground", invocation_id="fg-inv", generation=1)
            self.assertEqual(coordinator.snapshot()["lanes"]["watchdog"]["state"], "running")
            coordinator.release("watchdog", invocation_id="wd-inv", generation=1)


if __name__ == "__main__":
    unittest.main()
