#!/usr/bin/env python3
"""Durable cooperative lane registry over a caller-supplied compare-and-swap store."""
from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
import secrets
from typing import Optional

try:
    from project_lanes import (
        LaneClaim, LaneKind, admit_writer, paths_overlap, project_can_finalize,
        result_within_claim, validate_claim,
    )
except ModuleNotFoundError:
    from scripts.project_lanes import (
        LaneClaim, LaneKind, admit_writer, paths_overlap, project_can_finalize,
        result_within_claim, validate_claim,
    )

SCHEMA = "project-lane-registry/v1"
DIGEST = re.compile(r"sha256:[0-9a-f]{64}$")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
INVALID_REF = re.compile(r"[\x00-\x20\x7f~^:?*\[\\]")


def _branch_ref(value, label, prefix="refs/heads/"):
    if (not isinstance(value, str) or not value.startswith(prefix)
            or value.endswith(("/", ".")) or ".." in value or "@{" in value
            or "//" in value or INVALID_REF.search(value)):
        raise ValueError(label + " must be a canonical branch ref")
    return value


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
        _branch_ref(self.product_source_ref, "product_source_ref")
        _branch_ref(self.coordination_ref, "coordination_ref", "refs/heads/cdc/")
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
                 integration_verifier=None, activity_verifier=None):
        if not isinstance(config, LaneRegistryConfig):
            raise ValueError("project lane registry configuration is required")
        if config.coordination_ref != store.ref or config.coordination_store_id != store.store_id:
            raise ValueError("project lane registry configuration disagrees with coordination store")
        self.store = store
        self.config = config
        self.result_verifier = result_verifier
        self.quiescence_verifier = quiescence_verifier
        self.integration_verifier = integration_verifier
        self.activity_verifier = activity_verifier
        self._ensure_initialized()

    def _ensure_initialized(self):
        for _ in range(6):
            revision, state = self.store.read()
            if state is not None:
                self._read()
                return
            try:
                self.store.compare_and_swap(revision, self._initial())
                return
            except ValueError:
                continue
        raise ValueError("project lane registry initialization CAS contention")

    def _initial(self):
        return {
            "schema": SCHEMA,
            "coordination_ref": self.store.ref,
            "coordination_store_id": self.store.store_id,
            "config": self.config.to_dict(),
            "config_digest": self.config.digest(),
            "lanes": {},
            "integration_queue": [],
            "integration_intents": {},
            "integrated_results": [],
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
        if (not isinstance(state["lanes"], dict) or not isinstance(state["integration_queue"], list)
                or not isinstance(state["integration_intents"], dict)
                or not isinstance(state["integrated_results"], list)):
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
            if not admit_writer(existing, claim):
                writer_isolation = any(
                    item.is_writer and claim.is_writer
                    and not admit_writer([item], claim)
                    and not (item.kind != LaneKind.INTEGRATOR
                             and claim.kind != LaneKind.INTEGRATOR
                             and paths_overlap(item, claim))
                    for item in existing
                )
                if writer_isolation:
                    decision.update(reason="isolation_or_integrator_conflict")
                else:
                    decision.update(reason="write_claim_conflict")
                return False
            state["lanes"][claim.lane_id] = {
                "claim": _claim_dict(claim),
                "generation": generation,
                "state": "running",
                "last_activity_ref": None,
                "last_activity_evidence": None,
                "pending_effects": False,
                "checkpoint_ref": None,
                "quiescence_evidence": None,
            }
            decision.update(admitted=True, reason="admitted")
            return True

        self._change(transform)
        return decision

    def _bound(self, state, lane_id, invocation_id, generation, executor_id=None):
        lane = state["lanes"].get(lane_id)
        if lane is None:
            raise ValueError("unknown lane")
        claim = lane["claim"]
        if claim["invocation_id"] != invocation_id or lane["generation"] != generation:
            raise ValueError("lane identity/generation mismatch")
        if executor_id is not None and claim["executor_id"] != executor_id:
            raise ValueError("lane executor identity mismatch")
        return lane

    def heartbeat(self, lane_id, *, invocation_id, generation, executor_id, activity_ref):
        if not isinstance(activity_ref, str) or not activity_ref.strip():
            raise ValueError("activity_ref required")
        if self.activity_verifier is None:
            raise ValueError("heartbeat requires independent activity verifier")

        def transform(state):
            lane = self._bound(state, lane_id, invocation_id, generation, executor_id)
            if lane["state"] != "running" or lane["last_activity_ref"] == activity_ref:
                raise ValueError("heartbeat requires new activity on running lane")
            evidence = self.activity_verifier(copy.deepcopy(lane), activity_ref)
            if (not isinstance(evidence, dict) or evidence.get("observed") is not True
                    or evidence.get("activity_ref") != activity_ref
                    or not isinstance(evidence.get("evidence_ref"), str)
                    or not evidence["evidence_ref"].strip()):
                raise ValueError("heartbeat activity is not independently observed")
            lane["last_activity_ref"] = activity_ref
            lane["last_activity_evidence"] = copy.deepcopy(evidence)
            return True

        self._change(transform)

    def handoff(self, lane_id, *, invocation_id, generation, executor_id, checkpoint_ref):
        if not isinstance(checkpoint_ref, str) or not checkpoint_ref.strip():
            raise ValueError("handoff requires checkpoint_ref")
        if self.quiescence_verifier is None:
            raise ValueError("handoff requires independent quiescence verifier")

        def transform(state):
            lane = self._bound(state, lane_id, invocation_id, generation, executor_id)
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

    def set_pending_effects(self, lane_id, *, invocation_id, generation, executor_id, pending):
        if type(pending) is not bool:
            raise ValueError("pending must be bool")

        def transform(state):
            self._bound(state, lane_id, invocation_id, generation, executor_id)["pending_effects"] = pending
            return True

        self._change(transform)

    def record_result(self, lane_id, *, invocation_id, generation, executor_id, result_commit, evidence_refs):
        if self.result_verifier is None:
            raise ValueError("writer result requires independent verifier")
        if not isinstance(result_commit, str) or not SHA.fullmatch(result_commit):
            raise ValueError("result_commit invalid")
        if (not isinstance(evidence_refs, list) or not evidence_refs
                or any(not isinstance(item, str) or not item.strip() for item in evidence_refs)):
            raise ValueError("evidence_refs invalid")

        def transform(state):
            lane = self._bound(state, lane_id, invocation_id, generation, executor_id)
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

    def release(self, lane_id, *, invocation_id, generation, executor_id, checkpoint_ref):
        if not isinstance(checkpoint_ref, str) or not checkpoint_ref.strip():
            raise ValueError("lane release requires checkpoint_ref")

        def transform(state):
            lane = self._bound(state, lane_id, invocation_id, generation, executor_id)
            if lane["pending_effects"]:
                raise ValueError("lane release requires drained effects")
            if lane["state"] not in {"running", "handoff_ready"}:
                raise ValueError("lane not releasable")
            if lane["checkpoint_ref"] is not None and lane["checkpoint_ref"] != checkpoint_ref:
                raise ValueError("lane release checkpoint disagrees with handoff checkpoint")
            lane["checkpoint_ref"] = checkpoint_ref
            lane["state"] = "released"
            return True

        self._change(transform)

    @staticmethod
    def _integration_key(lane_id, result_commit):
        raw = json.dumps({"lane_id": lane_id, "result_commit": result_commit},
                         sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def claim_integration(self, lane_id, *, result_commit, integrator_lane_id,
                          integrator_invocation_id, integrator_generation,
                          integrator_executor_id, observed_shared_head):
        if not isinstance(result_commit, str) or not SHA.fullmatch(result_commit):
            raise ValueError("result_commit invalid")
        if not isinstance(observed_shared_head, str) or not SHA.fullmatch(observed_shared_head):
            raise ValueError("observed_shared_head must be an exact Git commit")
        key = self._integration_key(lane_id, result_commit)
        decision = {"claimed": False, "operation_id": None}

        def transform(state):
            integrator = self._bound(
                state, integrator_lane_id, integrator_invocation_id,
                integrator_generation, integrator_executor_id)
            if (integrator["state"] != "running"
                    or integrator["claim"]["kind"] != LaneKind.INTEGRATOR.value):
                raise ValueError("active integrator lane required")
            matches = [
                item for item in state["integration_queue"]
                if item["lane_id"] == lane_id and item["result_commit"] == result_commit
            ]
            if len(matches) != 1:
                raise ValueError("pending integration result not found")
            existing = state["integration_intents"].get(key)
            if existing is not None:
                decision.update(claimed=False, operation_id=existing["operation_id"])
                return False
            operation_id = "lane-integration-" + secrets.token_hex(24)
            state["integration_intents"][key] = {
                "operation_id": operation_id,
                "status": "claimed",
                "lane_id": lane_id,
                "result_commit": result_commit,
                "integrator_lane_id": integrator_lane_id,
                "integrator_invocation_id": integrator_invocation_id,
                "integrator_generation": integrator_generation,
                "integrator_executor_id": integrator_executor_id,
                "observed_shared_head": observed_shared_head,
            }
            decision.update(claimed=True, operation_id=operation_id)
            return True

        self._change(transform)
        return decision

    def mark_integrated(self, lane_id, *, result_commit, operation_id, integrator_lane_id,
                        integrator_invocation_id, integrator_generation, integrator_executor_id):
        if self.integration_verifier is None:
            raise ValueError("integration requires fresh independent verifier")
        key = self._integration_key(lane_id, result_commit)
        _, snapshot = self._read()
        intent = snapshot["integration_intents"].get(key)
        if (intent is None or intent.get("status") != "claimed"
                or intent.get("operation_id") != operation_id):
            raise ValueError("durable integration intent is required before publication reconciliation")
        integrator = self._bound(
            snapshot, integrator_lane_id, integrator_invocation_id,
            integrator_generation, integrator_executor_id)
        matches = [
            item for item in snapshot["integration_queue"]
            if item["lane_id"] == lane_id and item["result_commit"] == result_commit
        ]
        if len(matches) != 1:
            raise ValueError("pending integration result not found")
        evidence = self.integration_verifier(
            copy.deepcopy(matches[0]), _claim_from(integrator["claim"]), copy.deepcopy(intent))
        expected = {"integrated", "operation_id", "result_commit", "observed_shared_head",
                    "integrated_head", "force_push", "evidence_ref"}
        if (not isinstance(evidence, dict) or set(evidence) != expected
                or evidence["integrated"] is not True
                or evidence["operation_id"] != operation_id
                or evidence["result_commit"] != result_commit
                or evidence["observed_shared_head"] != intent["observed_shared_head"]
                or not isinstance(evidence["integrated_head"], str)
                or not SHA.fullmatch(evidence["integrated_head"])
                or evidence["force_push"] is not False
                or not isinstance(evidence["evidence_ref"], str)
                or not evidence["evidence_ref"].strip()):
            raise ValueError("integration verifier did not prove claimed conditional integration")

        def transform(state):
            current = state["integration_intents"].get(key)
            if (current is None or current.get("status") != "claimed"
                    or current.get("operation_id") != operation_id):
                raise ValueError("integration intent changed before reconciliation")
            self._bound(state, integrator_lane_id, integrator_invocation_id,
                        integrator_generation, integrator_executor_id)
            queued = [
                item for item in state["integration_queue"]
                if item["lane_id"] == lane_id and item["result_commit"] == result_commit
            ]
            if len(queued) != 1:
                raise ValueError("pending integration result changed before reconciliation")
            state["integration_queue"].remove(queued[0])
            current["status"] = "integrated"
            current["integration_evidence"] = copy.deepcopy(evidence)
            state["integrated_results"].append({
                **copy.deepcopy(queued[0]),
                "integrator_lane_id": integrator_lane_id,
                "integration_evidence": copy.deepcopy(evidence),
            })
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
