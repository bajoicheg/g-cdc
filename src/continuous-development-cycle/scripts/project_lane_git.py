#!/usr/bin/env python3
"""Real-Git result verifier for cooperative writer lanes."""
from __future__ import annotations

from pathlib import Path
import re
import subprocess

try:
    from git_object_integrity import git_object_environment
    from parallel_task_planner import validate_write_path
    from project_lanes import LaneKind, validate_claim
except ModuleNotFoundError:
    from scripts.git_object_integrity import git_object_environment
    from scripts.parallel_task_planner import validate_write_path
    from scripts.project_lanes import LaneKind, validate_claim

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


class GitLaneIntegrationVerifier(GitLaneResultVerifier):
    """Read-only proof that a claimed result is integrated by fast-forward ancestry."""

    def __init__(self, repo, source_ref):
        super().__init__(repo)
        if (not isinstance(source_ref, str) or not source_ref.startswith("refs/heads/")
                or source_ref.endswith(("/", ".")) or ".." in source_ref or "@{" in source_ref
                or "//" in source_ref):
            raise ValueError("integration source_ref must be a canonical branch ref")
        self.source_ref = source_ref

    def __call__(self, item, integrator, intent):
        validate_claim(integrator)
        if integrator.kind != LaneKind.INTEGRATOR:
            raise ValueError("integration verifier requires an integrator lane")
        if (not isinstance(item, dict) or not isinstance(intent, dict)
                or item.get("lane_id") != intent.get("lane_id")
                or item.get("result_commit") != intent.get("result_commit")):
            raise ValueError("integration result and durable intent disagree")
        result_commit = item["result_commit"]
        observed = intent.get("observed_shared_head")
        operation_id = intent.get("operation_id")
        if not isinstance(result_commit, str) or not SHA.fullmatch(result_commit):
            raise ValueError("integration result_commit invalid")
        if not isinstance(observed, str) or not SHA.fullmatch(observed):
            raise ValueError("integration observed_shared_head invalid")
        if not isinstance(operation_id, str) or not operation_id:
            raise ValueError("integration operation_id invalid")
        self._commit_exists(result_commit)
        self._commit_exists(observed)
        current, code = self._run("rev-parse", "--verify", self.source_ref + "^{commit}", check=False)
        if code or not SHA.fullmatch(current):
            raise ValueError("shared integration ref is unavailable")
        self._commit_exists(current)
        for ancestor in (observed, result_commit):
            _, status = self._run("merge-base", "--is-ancestor", ancestor, current, check=False)
            if status != 0:
                raise ValueError("shared HEAD does not prove conditional integration ancestry")
        return {
            "integrated": True,
            "operation_id": operation_id,
            "result_commit": result_commit,
            "observed_shared_head": observed,
            "integrated_head": current,
            "force_push": False,
            "evidence_ref": "git:" + self.source_ref + "@" + current,
        }
