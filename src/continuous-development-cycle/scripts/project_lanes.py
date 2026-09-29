#!/usr/bin/env python3
"""Portable cooperative project-lane claims and terminal aggregation."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import os
import re
from typing import FrozenSet

try:
    from parallel_task_planner import overlaps, portable_path_key, validate_write_path
except ModuleNotFoundError:
    from scripts.parallel_task_planner import overlaps, portable_path_key, validate_write_path

SHA = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})$")
INVALID_REF = re.compile(r"[\x00-\x20\x7f~^:?*\[\\]")


class LaneKind(str, Enum):
    FOREGROUND = "foreground"
    WATCHDOG = "watchdog"
    WORKER = "worker"
    REVIEW = "review"
    INTEGRATOR = "integrator"


@dataclass(frozen=True)
class LaneClaim:
    lane_id: str
    invocation_id: str
    kind: LaneKind
    source_head: str
    worktree: str
    branch: str
    read_paths: FrozenSet[str] = field(default_factory=frozenset)
    write_paths: FrozenSet[str] = field(default_factory=frozenset)
    executor_id: str = "unknown"
    role: str = "worker"

    def normalized_writes(self):
        return frozenset(portable_path_key(path) for path in self.write_paths)

    @property
    def is_writer(self):
        return bool(self.write_paths) or self.kind == LaneKind.INTEGRATOR


def _text(value, name):
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{name} must be nonempty text")


def validate_claim(claim):
    if not isinstance(claim, LaneClaim):
        raise ValueError("lane claim type invalid")
    for name in ("lane_id", "invocation_id", "worktree", "branch", "executor_id", "role"):
        _text(getattr(claim, name), name)
    branch = claim.branch.removeprefix("refs/heads/")
    parts = branch.split("/")
    if (claim.branch.startswith("-") or not branch or claim.branch.startswith("refs/")
            and not claim.branch.startswith("refs/heads/")
            or claim.branch.endswith(("/", ".", ".lock"))
            or ".." in claim.branch or "@{" in claim.branch or "//" in claim.branch
            or INVALID_REF.search(claim.branch)
            or any(part in {"", ".", ".."} or part.startswith(".") or part.endswith(".lock")
                   for part in parts)):
        raise ValueError("branch must be a safe Git heads ref/name")
    if not isinstance(claim.kind, LaneKind):
        raise ValueError("lane kind invalid")
    if not isinstance(claim.source_head, str) or not SHA.fullmatch(claim.source_head):
        raise ValueError("source_head must be an exact Git commit")
    for collection, name in ((claim.read_paths, "read_paths"), (claim.write_paths, "write_paths")):
        if not isinstance(collection, frozenset):
            raise ValueError(name + " must be a frozenset")
        for path in collection:
            validate_write_path(path)
        keys = [portable_path_key(path) for path in collection]
        if len(keys) != len(set(keys)):
            raise ValueError(name + " contains portable duplicates")
    return claim


def normalize_path(path):
    return portable_path_key(path)


def paths_overlap(left, right):
    validate_claim(left)
    validate_claim(right)
    return any(overlaps(a, b) for a in left.write_paths for b in right.write_paths)


def _worktree_key(path):
    return os.path.normcase(os.path.realpath(os.path.abspath(path)))


def _same_isolation(left, right):
    return (portable_path_key(left.branch) == portable_path_key(right.branch)
            or _worktree_key(left.worktree) == _worktree_key(right.worktree))


def admit_writer(existing, candidate):
    validate_claim(candidate)
    for item in existing:
        validate_claim(item)
    if any(item.lane_id == candidate.lane_id for item in existing):
        return False
    if not candidate.is_writer:
        return True
    writers = [item for item in existing if item.is_writer]
    if any(_same_isolation(item, candidate) for item in writers):
        return False
    if candidate.kind == LaneKind.INTEGRATOR:
        return not any(item.kind == LaneKind.INTEGRATOR for item in writers)
    for item in writers:
        if item.kind == LaneKind.INTEGRATOR:
            continue
        if paths_overlap(item, candidate):
            return False
    return True


def result_within_claim(claim, touched_paths):
    validate_claim(claim)
    if not isinstance(touched_paths, (set, frozenset, list, tuple)):
        raise ValueError("touched_paths must be a collection")
    for path in touched_paths:
        validate_write_path(path)
        key = portable_path_key(path)
        if not any(key == portable_path_key(allowed) or key.startswith(portable_path_key(allowed) + "/")
                   for allowed in claim.write_paths):
            return False
    return True


def project_can_finalize(*, active_lane_count, runnable_task_count, pending_result_count, unknown_effect_count):
    values = (active_lane_count, runnable_task_count, pending_result_count, unknown_effect_count)
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError("project completion counts must be nonnegative integers")
    return not any(values)
