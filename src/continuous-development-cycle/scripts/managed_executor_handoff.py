#!/usr/bin/env python3
"""CDC 2.11.0 portable managed-executor result handoff and publication proof."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

from parallel_task_planner import validate_write_path, portable_path_key
from worktree_worker_contract import canonical_branch_ref

HANDOFF_SCHEMA = "managed-executor-handoff/v1"
PROOF_SCHEMA = "managed-executor-publication-proof/v1"
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
TRANSPORTS = {"direct_branch", "content_artifact"}
ARTIFACT_FORMATS = {"git_bundle", "unified_diff"}
AUTHORITY_FIELDS = (
    "authorizes_product_write",
    "authorizes_shared_branch_write",
    "authorizes_force_push",
    "authorizes_merge",
    "authorizes_release",
    "authorizes_scope_expansion",
    "authorizes_scheduler_mutation",
)
HANDOFF_FIELDS = {
    "schema", "pool_id", "change_id", "task_id", "attempt_id", "parent_invocation_id",
    "executor_id", "base_sha", "assigned_branch", "transport", "source_result_commit",
    "direct_result_commit", "artifact_ref", "changed_paths", "evidence_refs",
}
PROOF_FIELDS = {
    "schema", "handoff_ref", "pool_id", "task_id", "attempt_id", "base_sha",
    "assigned_branch", "published_commit", "observed_changed_paths", "evidence_refs",
    "result_verified", *AUTHORITY_FIELDS,
}


def _text(value, name, nullable=False):
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")


def _sha(value, name, nullable=False):
    if value is None and nullable:
        return
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError(f"{name} must be a full lowercase SHA")


def _digest(value, name):
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise ValueError(f"{name} must be sha256:<hex>")


def _refs(value, name):
    if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(f"{name} must be a nonempty list of text refs")
    if len(value) != len(set(value)):
        raise ValueError(f"{name} contains duplicates")


def _paths(value, name):
    if not isinstance(value, list) or not value:
        raise ValueError(f"{name} must be a nonempty list")
    keys = []
    for path in value:
        validate_write_path(path)
        keys.append(portable_path_key(path))
    if len(keys) != len(set(keys)):
        raise ValueError(f"{name} contains portable aliases")
    return value


def _safe_rel(path):
    validate_write_path(path)
    return path


def _artifact_ref(value):
    if not isinstance(value, dict) or set(value) != {"path", "sha256", "format"}:
        raise ValueError("artifact_ref fields mismatch")
    _safe_rel(value["path"])
    _digest(value["sha256"], "artifact_ref.sha256")
    if value["format"] not in ARTIFACT_FORMATS:
        raise ValueError("unsupported artifact format")
    return value


def validate_handoff(handoff):
    if not isinstance(handoff, dict) or set(handoff) != HANDOFF_FIELDS or handoff.get("schema") != HANDOFF_SCHEMA:
        raise ValueError("managed executor handoff fields/schema mismatch")
    for name in ("pool_id", "change_id", "task_id", "attempt_id", "parent_invocation_id", "executor_id"):
        _text(handoff[name], name)
    _sha(handoff["base_sha"], "base_sha")
    canonical_branch_ref(handoff["assigned_branch"])
    if handoff["transport"] not in TRANSPORTS:
        raise ValueError("unsupported handoff transport")
    _sha(handoff["source_result_commit"], "source_result_commit", nullable=True)
    _paths(handoff["changed_paths"], "changed_paths")
    _refs(handoff["evidence_refs"], "evidence_refs")
    if handoff["transport"] == "direct_branch":
        _sha(handoff["direct_result_commit"], "direct_result_commit")
        if handoff["artifact_ref"] is not None:
            raise ValueError("direct_branch handoff cannot contain artifact_ref")
        if handoff["source_result_commit"] is not None and handoff["source_result_commit"] != handoff["direct_result_commit"]:
            raise ValueError("direct source/result commit mismatch")
    else:
        if handoff["direct_result_commit"] is not None:
            raise ValueError("content_artifact handoff cannot claim direct_result_commit")
        _artifact_ref(handoff["artifact_ref"])
    return handoff


def canonical_handoff_ref(handoff):
    validate_handoff(handoff)
    payload = json.dumps(handoff, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def resolve_artifact(handoff, evidence_root):
    validate_handoff(handoff)
    if handoff["transport"] != "content_artifact":
        raise ValueError("resolve_artifact requires content_artifact transport")
    if evidence_root is None:
        raise ValueError("content artifact requires evidence_root")
    root = Path(evidence_root).resolve()
    target = (root / handoff["artifact_ref"]["path"]).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("artifact escapes evidence root") from exc
    try:
        payload = target.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read result artifact: {exc}") from exc
    if not payload:
        raise ValueError("result artifact must not be empty")
    observed = "sha256:" + hashlib.sha256(payload).hexdigest()
    if observed != handoff["artifact_ref"]["sha256"]:
        raise ValueError("result artifact digest mismatch")
    return payload


def publication_plan(handoff, evidence_root=None):
    validate_handoff(handoff)
    if handoff["transport"] == "content_artifact":
        resolve_artifact(handoff, evidence_root)
        action = "IMPORT_CONTENT_ARTIFACT_TO_ASSIGNED_BRANCH"
    else:
        action = "VERIFY_DIRECT_ASSIGNED_BRANCH"
    return {
        "schema": "managed-executor-publication-plan/v1",
        "handoff_ref": canonical_handoff_ref(handoff),
        "pool_id": handoff["pool_id"],
        "task_id": handoff["task_id"],
        "attempt_id": handoff["attempt_id"],
        "base_sha": handoff["base_sha"],
        "assigned_branch": canonical_branch_ref(handoff["assigned_branch"]),
        "transport": handoff["transport"],
        "action": action,
        "artifact_ref": handoff["artifact_ref"],
        "direct_result_commit": handoff["direct_result_commit"],
        "requires_reexecution": False,
        **{name: False for name in AUTHORITY_FIELDS},
    }


def _portable_set(paths):
    _paths(paths, "paths")
    return {portable_path_key(p) for p in paths}


def validate_publication_proof(proof, handoff, git_worktree):
    validate_handoff(handoff)
    if not isinstance(proof, dict) or set(proof) != PROOF_FIELDS or proof.get("schema") != PROOF_SCHEMA:
        raise ValueError("managed executor publication proof fields/schema mismatch")
    if proof["handoff_ref"] != canonical_handoff_ref(handoff):
        raise ValueError("publication proof handoff_ref mismatch")
    for name in ("pool_id", "task_id", "attempt_id", "base_sha"):
        expected = handoff[name]
        if proof[name] != expected:
            raise ValueError(f"publication proof {name} mismatch")
    if canonical_branch_ref(proof["assigned_branch"]) != canonical_branch_ref(handoff["assigned_branch"]):
        raise ValueError("publication proof branch mismatch")
    _sha(proof["published_commit"], "published_commit")
    if handoff["transport"] == "direct_branch" and proof["published_commit"] != handoff["direct_result_commit"]:
        raise ValueError("direct publication commit mismatch")
    if handoff["source_result_commit"] is not None and handoff["artifact_ref"] and handoff["artifact_ref"]["format"] == "git_bundle":
        if proof["published_commit"] != handoff["source_result_commit"]:
            raise ValueError("git_bundle publication must preserve source result commit")
    if _portable_set(proof["observed_changed_paths"]) != _portable_set(handoff["changed_paths"]):
        raise ValueError("published changed paths do not match handoff manifest")
    _refs(proof["evidence_refs"], "publication proof evidence_refs")
    if type(proof["result_verified"]) is not bool or not proof["result_verified"]:
        raise ValueError("publication proof must be result_verified")
    for name in AUTHORITY_FIELDS:
        if type(proof[name]) is not bool or proof[name]:
            raise ValueError(f"{name} must remain false")
    root = Path(git_worktree)
    if not root.is_dir():
        raise ValueError("publication proof requires live git_worktree")
    branch_ref = canonical_branch_ref(handoff["assigned_branch"])
    try:
        for sha in (handoff["base_sha"], proof["published_commit"]):
            kind = subprocess.check_output(
                ["git", "-C", str(root), "cat-file", "-t", sha],
                text=True, stderr=subprocess.PIPE, timeout=15,
            ).strip()
            if kind != "commit":
                raise ValueError("publication ancestry endpoint is not a commit")
        ancestry = subprocess.run(
            ["git", "-C", str(root), "merge-base", "--is-ancestor", handoff["base_sha"], proof["published_commit"]],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15,
        )
        if ancestry.returncode != 0:
            raise ValueError("published result does not descend from handoff base")
        live = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--verify", branch_ref],
            text=True, stderr=subprocess.PIPE, timeout=15,
        ).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError(f"cannot verify published result: {exc}") from exc
    if live != proof["published_commit"]:
        raise ValueError("published commit is not exact assigned branch head")
    return proof


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("handoff")
    p.add_argument("--evidence-root")
    a = p.parse_args(argv)
    try:
        handoff = json.loads(Path(a.handoff).read_text())
        result = publication_plan(handoff, evidence_root=a.evidence_root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
