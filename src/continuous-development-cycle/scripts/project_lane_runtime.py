#!/usr/bin/env python3
"""Durable cooperative lane registry over a caller-supplied compare-and-swap store."""
from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Optional

try:
    from project_lanes import (
        LaneClaim, LaneKind, admit_writer, project_can_finalize,
        result_within_claim, validate_claim,
    )
except ModuleNotFoundError:
    from scripts.project_lanes import (
        LaneClaim, LaneKind, admit_writer, project_can_finalize,
        result_within_claim, validate_claim,
    )

SCHEMA = "project-lane-registry/v1"
DIGEST = re.compile(r"sha256:[0-9a-f]{64}$")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


@dataclass(frozen=True)
class LaneRegistryConfig:
    canonical_repository: str
    product_source_ref: str
    coordination_ref: str
    coordination_store_id: str
    policy_authority: str

    def __post_init__(self):
        if not isinstance(self.canonical_repository, str) or not REPOSITORY.fullmatch(self.canonical_repository):
            raise ValueError("canonical_repository must be owner/name")
        if (not isinstance(self.product_source_ref, str)
                or not self.product_source_ref.startswith("refs/heads/")
                or self.product_source_ref.endswith(("/", "."))
                or ".." in self.product_source_ref or "@{" in self.product_source_ref
                or "//" in self.product_source_ref):
            raise ValueError("product_source_ref must be a canonical refs/heads/ ref")
        if not isinstance(self.coordination_ref, str) or not self.coordination_ref.startswith("refs/heads/cdc/"):
            raise ValueError("coordination_ref must be a dedicated CDC branch ref")
        if not isinstance(self.coordination_store_id, str) or not DIGEST.fullmatch(self.coordination_store_id):
            raise ValueError("coordination_store_id must be sha256")
        if not isinstance(self.policy_authority, str) or not DIGEST.fullmatch(self.policy_authority):
            raise ValueError("policy_authority must be sha256")

    def to_dict(self):
        return {
            "canonical_repository": self.canonical_repository,
            "product_source_ref": self.product_source_ref,
            "coordination_ref": self.coordination_ref,
            "coordination_store_id": self.coordination_store_id,
            "policy_authority": self.policy_authority,
        }

    def digest(self):
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return "sha256:" + hashlib.sha256(payload).hexdigest()


class LaneState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    HANDOFF_PENDING = "handoff_pending"
    RELEASED = "released"
    STALE = "stale"


@dataclass
class LaneRuntime:
    lane_id: str
    generation: int
    state: LaneState = LaneState.QUEUED
    last_activity_ref: Optional[str] = None
    pending_effects: bool = False

    def heartbeat(self, activity_ref):
        if not activity_ref or activity_ref == self.last_activity_ref:
            raise ValueError("heartbeat requires a new activity reference")
        self.last_activity_ref = activity_ref
        self.state = LaneState.RUNNING

    def request_handoff(self):
        if self.state != LaneState.RUNNING:
            raise ValueError("only active lanes can handoff")
        self.state = LaneState.HANDOFF_PENDING

    def release(self):
        if self.pending_effects:
            raise ValueError("lane release requires drained effects")
        if self.state not in (LaneState.HANDOFF_PENDING, LaneState.RUNNING):
            raise ValueError("lane is not releasable")
        self.state = LaneState.RELEASED


def _claim_dict(claim):
    validate_claim(claim)
    return {
        "lane_id": claim.lane_id,
        "invocation_id": claim.invocation_id,
        "kind": claim.kind.value,
        "source_head": claim.source_head,
        "worktree": claim.worktree,
        "branch": claim.branch,
        "read_paths": sorted(claim.read_paths),
        "write_paths": sorted(claim.write_paths),
        "executor_id": claim.executor_id,
        "role": claim.role,
    }


def _claim_from(value):
    return LaneClaim(
        lane_id=value["lane_id"],
        invocation_id=value["invocation_id"],
        kind=LaneKind(value["kind"]),
        source_head=value["source_head"],
        worktree=value["worktree"],
        branch=value["branch"],
        read_paths=frozenset(value["read_paths"]),
        write_paths=frozenset(value["write_paths"]),
        executor_id=value["executor_id"],
        role=value["role"],
    )


class ProjectLaneCoordinator:
    def __init__(self, store, config, *, result_verifier=None, quiescence_verifier=None,
                 integration_verifier=None):
        if not isinstance(config, LaneRegistryConfig):
            raise ValueError("project lane registry configuration is required")
        if config.coordination_ref != store.ref or config.coordination_store_id != store.store_id:
            raise ValueError("project lane registry configuration disagrees with coordination store")
        self.store = store
        self.config = config
        self.result_verifier = result_verifier
        self.quiescence_verifier = quiescence_verifier
        self.integration_verifier = integration_verifier

    def _initial(self):
        return {
            "schema": SCHEMA,
            "coordination_ref": self.store.ref,
            "coordination_store_id": self.store.store_id,
            "config": self.config.to_dict(),
            "config_digest": self.config.digest(),
            "lanes": {},
            "integration_queue": [],
        }

    def _read(self):
        revision, state = self.store.read()
        if state is None:
            return revision, self._initial()
        if (not isinstance(state, dict) or set(state) != set(self._initial()) or state["schema"] != SCHEMA
                or state["coordination_ref"] != self.store.ref
                or state["coordination_store_id"] != self.store.store_id):
            raise ValueError("project lane registry identity mismatch")
        if state["config"] != self.config.to_dict() or state["config_digest"] != self.config.digest():
            raise ValueError("project lane registry configuration drift")
        if not isinstance(state["lanes"], dict) or not isinstance(state["integration_queue"], list):
            raise ValueError("project lane registry collections invalid")
        return revision, state

    def _change(self, transform):
        for _ in range(6):
            revision, state = self._read()
            changed = copy.deepcopy(state)
            result = transform(changed)
            if result is False:
                return False
            try:
                self.store.compare_and_swap(revision, changed)
                return result
            except ValueError:
                continue
        raise ValueError("project lane registry CAS contention")

    def snapshot(self):
        return copy.deepcopy(self._read()[1])

    def _active_claims(self, state):
        return [
            _claim_from(value["claim"])
            for value in state["lanes"].values()
            if value["state"] in {"running", "handoff_ready"}
        ]

    def admit(self, claim, *, generation):
        validate_claim(claim)
        if type(generation) is not int or generation < 1:
            raise ValueError("lane generation invalid")
        decision = {"admitted": False, "reason": "coordination_contention"}

        def transform(state):
            if claim.lane_id in state["lanes"]:
                decision.update(reason="duplicate_lane")
                return False
            existing = self._active_claims(state)
            if claim.kind != LaneKind.INTEGRATOR:
                for item in existing:
                    if (item.kind != LaneKind.INTEGRATOR and item.is_writer and claim.is_writer
                            and (item.branch == claim.branch or item.worktree == claim.worktree)):
                        decision.update(reason="isolation_conflict")
                        return False
                    if (item.kind != LaneKind.INTEGRATOR and item.is_writer and claim.is_writer
                            and not admit_writer([item], claim)):
                        decision.update(reason="write_claim_conflict")
                        return False
            elif any(item.kind == LaneKind.INTEGRATOR for item in existing):
                decision.update(reason="integrator_conflict")
                return False
            state["lanes"][claim.lane_id] = {
                "claim": _claim_dict(claim),
                "generation": generation,
                "state": "running",
                "last_activity_ref": None,
                "pending_effects": False,
                "checkpoint_ref": None,
                "quiescence_evidence": None,
            }
            decision.update(admitted=True, reason="admitted")
            return True

        self._change(transform)
        return decision

    def _bound(self, state, lane_id, invocation_id, generation):
        lane = state["lanes"].get(lane_id)
        if lane is None:
            raise ValueError("unknown lane")
        claim = lane["claim"]
        if claim["invocation_id"] != invocation_id or lane["generation"] != generation:
            raise ValueError("lane identity/generation mismatch")
        return lane

    def heartbeat(self, lane_id, *, invocation_id, generation, activity_ref):
        if not isinstance(activity_ref, str) or not activity_ref.strip():
            raise ValueError("activity_ref required")

        def transform(state):
            lane = self._bound(state, lane_id, invocation_id, generation)
            if lane["state"] != "running" or lane["last_activity_ref"] == activity_ref:
                raise ValueError("heartbeat requires new activity on running lane")
            lane["last_activity_ref"] = activity_ref
            return True

        self._change(transform)

    def handoff(self, lane_id, *, invocation_id, generation, checkpoint_ref):
        if not isinstance(checkpoint_ref, str) or not checkpoint_ref.strip():
            raise ValueError("handoff requires checkpoint_ref")
        if self.quiescence_verifier is None:
            raise ValueError("handoff requires independent quiescence verifier")

        def transform(state):
            lane = self._bound(state, lane_id, invocation_id, generation)
            if lane["state"] != "running" or lane["pending_effects"]:
                raise ValueError("lane is not handoff-safe")
            evidence = self.quiescence_verifier(copy.deepcopy(lane), checkpoint_ref)
            if (not isinstance(evidence, dict) or evidence.get("quiescent") is not True
                    or not isinstance(evidence.get("evidence_ref"), str) or not evidence["evidence_ref"].strip()):
                raise ValueError("independent quiescence not proven")
            lane.update(
                state="handoff_ready",
                checkpoint_ref=checkpoint_ref,
                quiescence_evidence=copy.deepcopy(evidence),
            )
            return True

        self._change(transform)

    def set_pending_effects(self, lane_id, *, invocation_id, generation, pending):
        if type(pending) is not bool:
            raise ValueError("pending must be bool")

        def transform(state):
            self._bound(state, lane_id, invocation_id, generation)["pending_effects"] = pending
            return True

        self._change(transform)

    def record_result(self, lane_id, *, invocation_id, generation, result_commit, evidence_refs):
        if self.result_verifier is None:
            raise ValueError("writer result requires independent verifier")
        if not isinstance(result_commit, str) or len(result_commit) not in {40, 64}:
            raise ValueError("result_commit invalid")
        if (not isinstance(evidence_refs, list) or not evidence_refs
                or any(not isinstance(item, str) or not item.strip() for item in evidence_refs)):
            raise ValueError("evidence_refs invalid")

        def transform(state):
            lane = self._bound(state, lane_id, invocation_id, generation)
            claim = _claim_from(lane["claim"])
            if lane["state"] != "running" or not claim.is_writer or claim.kind == LaneKind.INTEGRATOR:
                raise ValueError("lane cannot submit writer result")
            verified = self.result_verifier(claim, result_commit)
            if not isinstance(verified, dict) or set(verified) != {"observed_base", "base_ancestor", "touched_paths"}:
                raise ValueError("result verifier contract invalid")
            if (verified["observed_base"] != claim.source_head or verified["base_ancestor"] is not True
                    or not result_within_claim(claim, verified["touched_paths"])):
                raise ValueError("writer result violates bound base or write claim")
            if any(item["lane_id"] == lane_id and item["result_commit"] == result_commit
                   for item in state["integration_queue"]):
                raise ValueError("duplicate writer result")
            state["integration_queue"].append({
                "lane_id": lane_id,
                "result_commit": result_commit,
                "source_head": claim.source_head,
                "touched_paths": sorted(verified["touched_paths"]),
                "evidence_refs": list(evidence_refs),
            })
            return True

        self._change(transform)

    def release(self, lane_id, *, invocation_id, generation):
        def transform(state):
            lane = self._bound(state, lane_id, invocation_id, generation)
            if lane["pending_effects"]:
                raise ValueError("lane release requires drained effects")
            if lane["state"] not in {"running", "handoff_ready"}:
                raise ValueError("lane not releasable")
            lane["state"] = "released"
            return True

        self._change(transform)

    def mark_integrated(self, lane_id, *, result_commit, integrator_lane_id,
                        integrator_invocation_id, integrator_generation):
        def transform(state):
            integrator = self._bound(
                state, integrator_lane_id, integrator_invocation_id, integrator_generation)
            if (integrator["state"] != "running"
                    or integrator["claim"]["kind"] != LaneKind.INTEGRATOR.value):
                raise ValueError("active integrator lane required")
            matches = [
                item for item in state["integration_queue"]
                if item["lane_id"] == lane_id and item["result_commit"] == result_commit
            ]
            if len(matches) != 1:
                raise ValueError("pending integration result not found")
            state["integration_queue"].remove(matches[0])
            return True

        self._change(transform)

    def can_finalize(self, *, runnable_task_count, unknown_effect_count):
        state = self._read()[1]
        active = sum(
            value["state"] in {"running", "handoff_ready"}
            for value in state["lanes"].values()
        )
        return project_can_finalize(
            active_lane_count=active,
            runnable_task_count=runnable_task_count,
            pending_result_count=len(state["integration_queue"]),
            unknown_effect_count=unknown_effect_count,
        )
