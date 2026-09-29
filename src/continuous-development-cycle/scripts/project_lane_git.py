#!/usr/bin/env python3
"""Real-Git result verifier for cooperative writer lanes."""
from __future__ import annotations

from pathlib import Path
import re
import subprocess

try:
    from git_object_integrity import git_object_environment
    from git_remote_identity import isolated_remote_args, remote_identity
    from parallel_task_planner import validate_write_path
    from project_lanes import LaneKind, validate_claim
except ModuleNotFoundError:
    from scripts.git_object_integrity import git_object_environment
    from scripts.git_remote_identity import isolated_remote_args, remote_identity
    from scripts.parallel_task_planner import validate_write_path
    from scripts.project_lanes import LaneKind, validate_claim

SHA = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})$")
DIGEST = re.compile(r"sha256:[0-9a-f]{64}$")
INVALID_REF = re.compile(r"[\x00-\x20\x7f~^:?*\[\\]")


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
    """Read-only ancestry/readback evidence.

    This helper deliberately does NOT claim that publication was conditional.
    It may support diagnosis/reconciliation, but ProjectLaneCoordinator must not
    accept it as publication proof by itself.
    """

    def __init__(self, repo, source_ref):
        super().__init__(repo)
        if (not isinstance(source_ref, str) or not source_ref.startswith("refs/heads/")
                or source_ref.endswith(("/", ".")) or ".." in source_ref or "@{" in source_ref
                or "//" in source_ref or INVALID_REF.search(source_ref)):
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
        intended = intent.get("intended_integrated_head")
        operation_id = intent.get("operation_id")
        for value, label in (
            (result_commit, "integration result_commit"),
            (observed, "integration observed_shared_head"),
            (intended, "integration intended_integrated_head"),
        ):
            if not isinstance(value, str) or not SHA.fullmatch(value):
                raise ValueError(label + " invalid")
        if not isinstance(operation_id, str) or not operation_id:
            raise ValueError("integration operation_id invalid")
        for revision in (result_commit, observed, intended):
            self._commit_exists(revision)
        current, code = self._run("rev-parse", "--verify", self.source_ref + "^{commit}", check=False)
        if code or not SHA.fullmatch(current):
            raise ValueError("shared integration ref is unavailable")
        self._commit_exists(current)
        for ancestor in (observed, result_commit):
            _, status = self._run("merge-base", "--is-ancestor", ancestor, current, check=False)
            if status != 0:
                raise ValueError("shared HEAD does not prove integration ancestry")
        if current != intended:
            raise ValueError("shared HEAD does not match the intended integrated head")
        return {
            "integrated": True,
            "operation_id": operation_id,
            "result_commit": result_commit,
            "observed_shared_head": observed,
            "integrated_head": current,
            "conditional_update": False,
            "force_push": False,
            "evidence_ref": "git-readback:" + self.source_ref + "@" + current,
        }


class GitLaneIntegrationPublisher(GitLaneResultVerifier):
    """Conditional fast-forward publication bound to the durable integration intent.

    The push uses force-with-lease only as a compare-and-swap primitive for the
    exact expected old SHA. A separate ancestry check forbids a non-fast-forward
    update, so this never authorizes rewriting another executor's history.
    """

    def __init__(self, repo, remote, source_ref, remote_id):
        super().__init__(repo)
        if not isinstance(remote, str) or not remote.strip() or remote.startswith("-"):
            raise ValueError("integration remote must be a configured remote name")
        if (not isinstance(source_ref, str) or not source_ref.startswith("refs/heads/")
                or source_ref.endswith(("/", ".")) or ".." in source_ref or "@{" in source_ref
                or "//" in source_ref or INVALID_REF.search(source_ref)):
            raise ValueError("integration source_ref must be a canonical branch ref")
        if not isinstance(remote_id, str) or not DIGEST.fullmatch(remote_id):
            raise ValueError("integration remote_id must be sha256")
        self.remote = remote
        self.source_ref = source_ref
        self.remote_id = remote_id
        if remote_identity(self.repo, self.remote) != self.remote_id:
            raise ValueError("integration remote identity drift")

    def _remote_head(self):
        if remote_identity(self.repo, self.remote) != self.remote_id:
            raise ValueError("integration remote identity drift")
        config, alias = isolated_remote_args(self.repo, self.remote, self.remote_id)
        output, _ = self._run(
            *config, "ls-remote", "--refs", alias, self.source_ref)
        rows = [line for line in output.splitlines() if line.strip()]
        if len(rows) != 1:
            raise ValueError("shared integration remote ref must resolve exactly once")
        parts = rows[0].split("\t")
        if len(parts) != 2 or parts[1] != self.source_ref or not SHA.fullmatch(parts[0]):
            raise ValueError("shared integration remote ref response invalid")
        return parts[0]

    def __call__(self, item, integrator, intent):
        validate_claim(integrator)
        if integrator.kind != LaneKind.INTEGRATOR:
            raise ValueError("integration publisher requires an integrator lane")
        if (not isinstance(item, dict) or not isinstance(intent, dict)
                or item.get("lane_id") != intent.get("lane_id")
                or item.get("result_commit") != intent.get("result_commit")):
            raise ValueError("integration result and durable intent disagree")
        result_commit = item["result_commit"]
        observed = intent.get("observed_shared_head")
        intended = intent.get("intended_integrated_head")
        operation_id = intent.get("operation_id")
        for value, label in (
            (result_commit, "integration result_commit"),
            (observed, "integration observed_shared_head"),
            (intended, "integration intended_integrated_head"),
        ):
            if not isinstance(value, str) or not SHA.fullmatch(value):
                raise ValueError(label + " invalid")
            self._commit_exists(value)
        if not isinstance(operation_id, str) or not operation_id:
            raise ValueError("integration operation_id invalid")
        for ancestor in (observed, result_commit):
            _, status = self._run(
                "merge-base", "--is-ancestor", ancestor, intended, check=False)
            if status != 0:
                raise ValueError("intended integration is not a fast-forward containing required ancestry")

        current = self._remote_head()
        if current != intended:
            if current != observed:
                raise ValueError("shared integration ref moved before conditional publication")
            config, alias = isolated_remote_args(self.repo, self.remote, self.remote_id)
            self._run(
                *config, "-c", "push.followTags=false", "push", "--porcelain",
                "--force-with-lease=" + self.source_ref + ":" + observed,
                alias, intended + ":" + self.source_ref)
            current = self._remote_head()
            if current != intended:
                raise ValueError("conditional integration publication did not become authoritative")

        return {
            "integrated": True,
            "operation_id": operation_id,
            "result_commit": result_commit,
            "observed_shared_head": observed,
            "integrated_head": intended,
            "conditional_update": True,
            "force_push": False,
            "evidence_ref": "git-cas:" + self.source_ref + "@" + intended,
        }
