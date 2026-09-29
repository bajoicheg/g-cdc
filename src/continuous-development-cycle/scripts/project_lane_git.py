#!/usr/bin/env python3
"""Real-Git result verifier for cooperative writer lanes."""
from __future__ import annotations

from pathlib import Path
import re
import subprocess

try:
    from git_object_integrity import git_object_environment
    from parallel_task_planner import validate_write_path
    from project_lanes import validate_claim
except ModuleNotFoundError:
    from scripts.git_object_integrity import git_object_environment
    from scripts.parallel_task_planner import validate_write_path
    from scripts.project_lanes import validate_claim

SHA = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})$")


class GitLaneResultVerifier:
    """Validate ancestry and the union of every path touched by introduced commits."""

    def __init__(self, repo):
        self.repo = Path(repo).resolve()
        root, _ = self._run("rev-parse", "--show-toplevel")
        if Path(root).resolve() != self.repo:
            raise ValueError("lane verifier repo must be the Git worktree root")

    def _run(self, *args, check=True):
        env = git_object_environment(GIT_TERMINAL_PROMPT="0")
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo), *args],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                timeout=20,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            raise ValueError("Git lane result verification unavailable") from None
        if check and result.returncode:
            raise ValueError("Git lane result verification command failed")
        return result.stdout.rstrip("\n"), result.returncode

    def _commit_exists(self, revision):
        if not isinstance(revision, str) or not SHA.fullmatch(revision):
            raise ValueError("lane result revision must be an exact Git commit SHA")
        _, code = self._run("cat-file", "-e", revision + "^{commit}", check=False)
        if code:
            raise ValueError("lane result revision is not an available commit")

    def __call__(self, claim, result_commit):
        validate_claim(claim)
        self._commit_exists(claim.source_head)
        self._commit_exists(result_commit)
        _, code = self._run(
            "merge-base", "--is-ancestor", claim.source_head, result_commit, check=False)
        if code not in {0, 1}:
            raise ValueError("Git ancestry verification failed")
        if code == 1:
            return {
                "observed_base": claim.source_head,
                "base_ancestor": False,
                "touched_paths": set(),
            }
        revs, _ = self._run(
            "rev-list", "--reverse", result_commit, "^" + claim.source_head)
        touched = set()
        for commit in [line for line in revs.splitlines() if line]:
            names, _ = self._run(
                "diff-tree", "--root", "--no-commit-id", "--name-only",
                "-r", "-m", "-z", commit)
            for path in names.split("\0"):
                if not path:
                    continue
                validate_write_path(path)
                touched.add(path)
        return {
            "observed_base": claim.source_head,
            "base_ancestor": True,
            "touched_paths": touched,
        }
