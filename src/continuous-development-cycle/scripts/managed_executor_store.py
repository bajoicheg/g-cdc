#!/usr/bin/env python3
"""CDC 2.11.0 durable Git CAS store for managed executor pool state."""
from __future__ import annotations

import copy
import json
import os
import re
import subprocess
from pathlib import Path

from managed_executor_pool import validate_plan, validate_state
from parallel_task_planner import portable_path_key

REVISION = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
STATE_FILE = "pool-state.json"


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _canonical(state):
    return json.dumps(
        state, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8") + b"\n"


def _canonical_heads_ref(value, name):
    if not isinstance(value, str) or not value.startswith("refs/heads/"):
        raise ValueError(f"{name} must be an exact refs/heads/ ref")
    if value != "refs/heads/" + value.removeprefix("refs/heads/"):
        raise ValueError(f"{name} must be canonical")
    return value


class GitManagedExecutorStore:
    """One-file Git-ref CAS store.

    Each state transition creates a sibling/child coordination commit and performs a
    normal non-force push. Competing proposals based on one revision therefore race
    at the remote ref; at most one can advance it.
    """

    def __init__(self, repo, remote, coordination_ref, plan, *, protected_refs=()):
        self.repo = Path(repo)
        if not self.repo.is_dir():
            raise ValueError("pool store repository missing")
        validate_plan(plan)
        self.plan = copy.deepcopy(plan)
        if not isinstance(remote, str) or not remote.strip() or remote.startswith("-"):
            raise ValueError("pool store remote name invalid")
        self.remote = remote
        self.ref = _canonical_heads_ref(coordination_ref, "coordination_ref")
        protected = {_canonical_heads_ref(ref, "protected_ref") for ref in protected_refs}
        writer_refs = set()
        for task in plan["tasks"]:
            if task["role"] == "writer":
                branch = task["branch"]
                writer_refs.add(branch if branch.startswith("refs/heads/") else "refs/heads/" + branch)
        coordination_key = portable_path_key(self.ref.removeprefix("refs/heads/"))
        occupied_keys = {
            portable_path_key(ref.removeprefix("refs/heads/"))
            for ref in protected | writer_refs
        }
        if coordination_key in occupied_keys:
            raise ValueError("coordination ref must be portable-isolated from product/shared/worker refs")
        self._git("check-ref-format", self.ref)
        remotes = self._git("remote").splitlines()
        if remote not in remotes:
            raise ValueError("pool store remote is not configured")
        fetch_urls = self._git("remote", "get-url", "--all", remote).splitlines()
        push_urls = self._git("remote", "get-url", "--push", "--all", remote).splitlines()
        if len(fetch_urls) != 1 or push_urls != fetch_urls:
            raise ValueError("pool store remote requires one identical fetch/push URL")

    def _git(self, *args, input_text=None):
        env = dict(
            os.environ,
            GIT_TERMINAL_PROMPT="0",
            GIT_AUTHOR_NAME="CDC managed executor",
            GIT_AUTHOR_EMAIL="cdc@example.invalid",
            GIT_COMMITTER_NAME="CDC managed executor",
            GIT_COMMITTER_EMAIL="cdc@example.invalid",
        )
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo), *args],
                input=input_text,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                check=False,
                timeout=20,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise ValueError("Git managed-executor coordination unavailable") from exc
        if result.returncode:
            raise ValueError(f"Git managed-executor coordination {args[0]} failed")
        return result.stdout.strip()

    def _remote_rows(self):
        rows = self._git("ls-remote", "--refs", self.remote, self.ref).splitlines()
        if not rows:
            return []
        if len(rows) != 1:
            raise ValueError("ambiguous managed-executor coordination ref")
        parts = rows[0].split("\t")
        if len(parts) != 2 or parts[1] != self.ref or not REVISION.fullmatch(parts[0]):
            raise ValueError("invalid managed-executor coordination revision")
        return rows

    def _decode_state(self, payload):
        try:
            state = json.loads(payload, object_pairs_hook=_unique_object)
        except (json.JSONDecodeError, UnicodeError) as exc:
            raise ValueError("invalid managed-executor pool state JSON") from exc
        if not isinstance(state, dict):
            raise ValueError("managed-executor pool state must be an object")
        if _canonical(state) != payload.encode("utf-8"):
            raise ValueError("managed-executor pool state must use canonical JSON encoding")
        validate_state(self.plan, state)
        return state

    def read(self):
        rows = self._remote_rows()
        if not rows:
            return None, None
        revision = rows[0].split("\t", 1)[0]
        self._git("fetch", "--no-tags", "--no-write-fetch-head", self.remote, self.ref)
        if self._git("cat-file", "-t", revision) != "commit":
            raise ValueError("managed-executor coordination ref must point to a commit")
        tree_rows = self._git("ls-tree", "--name-only", revision).splitlines()
        if tree_rows != [STATE_FILE]:
            raise ValueError("managed-executor coordination commit must contain only pool-state.json")
        payload = self._git("show", f"{revision}:{STATE_FILE}") + "\n"
        state = self._decode_state(payload)
        if self._remote_rows() != rows:
            raise ValueError("managed-executor coordination ref moved during read")
        return revision, state

    def compare_and_swap(self, expected_revision, new_state):
        validate_state(self.plan, new_state)
        current_revision, current_state = self.read()
        if current_revision != expected_revision:
            raise ValueError("stale expected managed-executor store revision")
        if expected_revision is None and current_state is not None:
            raise ValueError("managed-executor store already initialized")
        payload = _canonical(new_state).decode("utf-8")
        blob = self._git("hash-object", "-w", "--stdin", input_text=payload)
        tree = self._git("mktree", input_text=f"100644 blob {blob}\t{STATE_FILE}\n")
        parent = ["-p", expected_revision] if expected_revision is not None else []
        commit = self._git(
            "commit-tree", tree, *parent,
            input_text="Update managed executor pool state\n",
        )
        self._git(
            "-c", "push.followTags=false", "push", "--porcelain",
            self.remote, f"{commit}:{self.ref}",
        )
        rows = self._remote_rows()
        if len(rows) != 1 or rows[0].split("\t", 1)[0] != commit:
            raise ValueError("managed-executor CAS push did not become authoritative")
        return commit
