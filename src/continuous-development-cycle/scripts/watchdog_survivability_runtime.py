#!/usr/bin/env python3
"""Durable desired-state reconciliation for replaceable watchdog scheduler objects.

The scheduler backend is an explicit capability boundary. Every scheduler effect
is preceded by a durable CAS claim and a fresh safety read. Unknown effects are
never replayed; a later inventory may reconcile them by exact generation/readback.
"""
from __future__ import annotations

import copy
from datetime import datetime
import hashlib
import json
import secrets

from watchdog_survivability import assess, validate_desired

SCHEMA = "watchdog-survivability-runtime/v1"


def binding_key(binding):
    raw = json.dumps(binding, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def operation_key(binding, action, generation, object_id=None, basis=None):
    payload = {"binding": binding, "action": action, "generation": generation,
               "object_id": object_id, "basis": basis}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class WatchdogSurvivabilityRuntime:
    def __init__(self, store, backend, *, clock, max_age_seconds=120):
        self.store = store
        self.backend = backend
        self.clock = clock
        self.max_age_seconds = max_age_seconds

    def _initial(self):
        return {"schema": SCHEMA, "coordination_ref": self.store.ref,
                "coordination_store_id": self.store.store_id, "entries": {}}

    def _read(self):
        revision, state = self.store.read()
        if state is None:
            return revision, self._initial()
        if (not isinstance(state, dict) or set(state) != set(self._initial()) or state.get("schema") != SCHEMA
                or state.get("coordination_ref") != self.store.ref
                or state.get("coordination_store_id") != self.store.store_id or not isinstance(state.get("entries"), dict)):
            raise ValueError("watchdog survivability runtime state mismatch")
        for key, entry in state["entries"].items():
            if not isinstance(entry, dict) or set(entry) != {"desired", "operations"} or not isinstance(entry["operations"], dict):
                raise ValueError("watchdog survivability entry invalid")
            validate_desired(entry["desired"])
            if key != binding_key(entry["desired"]["binding"]):
                raise ValueError("watchdog survivability entry binding mismatch")
            for op_key, operation in entry["operations"].items():
                if (not isinstance(operation, dict) or operation.get("status") not in {"claimed", "succeeded", "blocked", "unknown"}
                        or operation.get("action") not in {"create", "enable", "run", "disable"}
                        or not isinstance(operation.get("operation_id"), str) or not operation["operation_id"]):
                    raise ValueError("watchdog survivability operation invalid")
                expected = operation_key(entry["desired"]["binding"], operation["action"],
                                         operation["generation"], operation.get("object_id"),
                                         operation.get("basis"))
                if op_key != expected:
                    raise ValueError("watchdog survivability operation key mismatch")
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
        raise ValueError("watchdog survivability coordination contention")

    def snapshot(self):
        return copy.deepcopy(self._read()[1])

    def register(self, desired):
        validate_desired(desired)
        key = binding_key(desired["binding"])
        incoming = copy.deepcopy(desired)

        def transform(state):
            current = state["entries"].get(key)
            if current is None:
                state["entries"][key] = {"desired": incoming, "operations": {}}
                return True
            existing = current["desired"]
            if incoming["generation"] < existing["generation"]:
                raise ValueError("cannot roll back watchdog desired generation")
            if incoming == existing:
                return False
            if any(op["status"] in {"claimed", "unknown"} for op in current["operations"].values()):
                raise ValueError("cannot replace watchdog desired state while an effect is unresolved")
            if incoming["generation"] == existing["generation"]:
                raise ValueError("desired-state mutation requires an explicit newer generation")
            current["desired"] = incoming
            current["operations"] = {}
            return True

        self._change(transform)
        return key

    def _entry(self, binding):
        key = binding_key(binding)
        _, state = self._read()
        if key not in state["entries"] or state["entries"][key]["desired"]["binding"] != binding:
            raise ValueError("watchdog desired state is not registered")
        return key, state["entries"][key]

    def _observe(self, desired):
        inventory = self.backend.observe(copy.deepcopy(desired["binding"]))
        result = assess(desired, inventory, now=self.clock(), max_age_seconds=self.max_age_seconds)
        return inventory, result

    def _set_operation(self, key, action, generation, object_id=None, *, basis=None, fence_generation=None):
        op_key = operation_key(self._entry_by_key(key)["desired"]["binding"],
                               action, generation, object_id, basis)
        operation_id = "watchdog-operation-" + secrets.token_hex(24)

        def transform(state):
            entry = state["entries"][key]
            if op_key in entry["operations"]:
                return False
            if any(op["status"] in {"claimed", "unknown"} for op in entry["operations"].values()):
                return False
            if fence_generation is not None:
                if entry["desired"]["generation"] >= fence_generation:
                    return False
                entry["desired"]["generation"] = fence_generation
                entry["desired"]["canonical_object_id"] = None
            entry["operations"][op_key] = {
                "action": action, "generation": generation, "object_id": object_id,
                "basis": basis, "operation_id": operation_id,
                "status": "claimed", "claimed_at_utc": self.clock(),
            }
            return True

        if not self._change(transform):
            return None, op_key
        return operation_id, op_key

    def _entry_by_key(self, key):
        _, state = self._read()
        return state["entries"][key]

    def _finish(self, key, op_key, operation_id, status, detail):
        def transform(state):
            op = state["entries"][key]["operations"].get(op_key)
            if not op or op["operation_id"] != operation_id or op["status"] != "claimed":
                return False
            op.update(status=status, detail=detail, finished_at_utc=self.clock())
            return True
        self._change(transform)

    def _adopt(self, key, object_id, *, op_key=None, operation_id=None):
        def transform(state):
            entry = state["entries"][key]
            entry["desired"]["canonical_object_id"] = object_id
            if op_key is not None:
                op = entry["operations"].get(op_key)
                if op and op["operation_id"] == operation_id and op["status"] in {"claimed", "unknown"}:
                    op.update(status="succeeded", detail="exact generation materialization adopted", finished_at_utc=self.clock())
            return True
        self._change(transform)

    @staticmethod
    def _at_or_after(value, lower_bound):
        try:
            left = datetime.fromisoformat(value.replace("Z", "+00:00"))
            right = datetime.fromisoformat(lower_bound.replace("Z", "+00:00"))
        except (AttributeError, ValueError):
            return False
        return left >= right

    def _reconcile_uncertain(self, key, entry):
        uncertain = [(op_key, op) for op_key, op in entry["operations"].items() if op["status"] in {"claimed", "unknown"}]
        if not uncertain:
            return None
        desired = entry["desired"]
        inventory, result = self._observe(desired)
        for op_key, op in uncertain:
            if op["action"] == "create" and result["action"] == "ADOPT" and result["canonical_object_id"]:
                self._adopt(key, result["canonical_object_id"], op_key=op_key, operation_id=op["operation_id"])
                return {"outcome": "adopted", "assessment": result}
            if op["action"] == "enable":
                item = next((x for x in inventory["objects"] if x["object_id"] == op["object_id"]), None)
                if item is not None and item["enabled"]:
                    self._finish_unknown(key, op_key, op["operation_id"], "enabled readback")
                    return {"outcome": "enabled", "assessment": result}
            if op["action"] == "disable":
                item = next((x for x in inventory["objects"] if x["object_id"] == op["object_id"]), None)
                if item is None or not item["enabled"]:
                    self._finish_unknown(key, op_key, op["operation_id"], "disabled readback")
                    return {"outcome": "duplicates_quiesced", "assessment": result}
            if op["action"] == "run":
                item = next((x for x in inventory["objects"] if x["object_id"] == op["object_id"]), None)
                if (item is not None and item["last_run_at_utc"] is not None
                        and item["execution_state"] in {"running", "idle", "failed"}
                        and self._at_or_after(item["last_run_at_utc"], op["claimed_at_utc"])):
                    self._finish_unknown(key, op_key, op["operation_id"], "run readback after durable claim")
                    return {"outcome": "run_requested", "assessment": result}
        return {"outcome": "unreconciled_operation", "assessment": result}

    def _finish_unknown(self, key, op_key, operation_id, detail):
        def transform(state):
            op = state["entries"][key]["operations"].get(op_key)
            if not op or op["operation_id"] != operation_id or op["status"] not in {"claimed", "unknown"}:
                return False
            op.update(status="succeeded", detail=detail, finished_at_utc=self.clock())
            return True
        self._change(transform)

    def _post_claim_allowed(self, desired):
        _, assessment = self._observe(desired)
        return assessment["overall"] not in {"OWNER_PAUSED", "PROJECT_TERMINAL", "EXECUTION_BROKEN"}

    def reconcile_registered(self, *, max_effects=100):
        """Assess every registered watchdog and apply a bounded number of scheduler effects."""
        if type(max_effects) is not int or not 0 <= max_effects <= 2000:
            raise ValueError("watchdog survivability max_effects must be 0..2000")
        _, state = self._read()
        results = []
        effects_attempted = 0
        effect_actions = {"RECREATE", "ENABLE", "RUN", "QUIESCE_DUPLICATES"}
        effect_outcomes = {"recreated", "enabled", "run_requested", "duplicates_quiesced",
                           "provider_outcome_unknown"}
        for key in sorted(state["entries"]):
            binding = copy.deepcopy(state["entries"][key]["desired"]["binding"])
            try:
                entry = self._entry_by_key(key)
                unresolved = any(op["status"] in {"claimed", "unknown"} for op in entry["operations"].values())
                if unresolved:
                    result = self.reconcile(binding)
                else:
                    _, assessment = self._observe(entry["desired"])
                    if assessment["action"] in effect_actions and effects_attempted >= max_effects:
                        result = {"outcome": "effect_budget_deferred", "assessment": assessment}
                    else:
                        result = self.reconcile(binding)
                        if result["outcome"] in effect_outcomes:
                            effects_attempted += 1
            except Exception as exc:
                result = {
                    "outcome": "coordination_or_observation_unavailable",
                    "error_class": type(exc).__name__,
                }
            results.append({"binding": binding, **result})

        def needs_continuation(item):
            if item["outcome"] == "no_effect":
                overall = item.get("assessment", {}).get("overall")
                return overall not in {"HEALTHY", "OWNER_PAUSED", "PROJECT_TERMINAL"}
            if item["outcome"] in {"adopted", "enabled", "run_requested", "recreated"}:
                return False
            if item["outcome"] == "duplicates_quiesced":
                return item.get("assessment", {}).get("action") == "QUIESCE_DUPLICATES"
            return True

        return {
            "schema": "watchdog-survivability-batch/v1",
            "registered_count": len(state["entries"]),
            "results": results,
            "effects_attempted": effects_attempted,
            "max_effects": max_effects,
            "continuation_required": any(needs_continuation(item) for item in results),
            "authorizes_scheduler_mutation": False,
        }

    def reconcile(self, binding):
        key, entry = self._entry(binding)
        uncertain = self._reconcile_uncertain(key, entry)
        if uncertain is not None:
            return uncertain
        desired = self._entry_by_key(key)["desired"]
        inventory, assessment = self._observe(desired)
        action = assessment["action"]
        if action in {"NONE", "OBSERVE"}:
            return {"outcome": "no_effect", "assessment": assessment}
        if action == "ADOPT":
            self._adopt(key, assessment["canonical_object_id"])
            return {"outcome": "adopted", "assessment": assessment}
        if not assessment["recovery_eligible"]:
            return {"outcome": "no_effect", "assessment": assessment}
        if action == "RECREATE":
            target_generation = assessment["next_generation"]
            operation_id, op_key = self._set_operation(
                key, "create", target_generation,
                basis="generation:" + str(target_generation), fence_generation=target_generation)
            if operation_id is None:
                return {"outcome": "unreconciled_operation", "assessment": assessment}
            desired = self._entry_by_key(key)["desired"]
            if not self._post_claim_allowed(desired):
                self._finish(key, op_key, operation_id, "blocked", "post-claim safety gate denied")
                return {"outcome": "post_claim_gate_denied", "assessment": assessment}
            _, after_fence = self._observe(desired)
            if after_fence["action"] == "ADOPT":
                self._adopt(key, after_fence["canonical_object_id"], op_key=op_key, operation_id=operation_id)
                return {"outcome": "adopted", "assessment": after_fence}
            try:
                reply = self.backend.create(copy.deepcopy(binding), generation=target_generation,
                                            schedule=desired["schedule"], template_digest=desired["template_digest"],
                                            operation_id=operation_id)
                _, readback = self._observe(desired)
                valid = (isinstance(reply, dict) and reply.get("status") == "accepted"
                         and reply.get("operation_id") == operation_id and reply.get("generation") == target_generation
                         and readback["action"] == "ADOPT" and readback["canonical_object_id"] == reply.get("object_id"))
                if not valid:
                    raise ValueError("create exact readback disagrees")
            except Exception:
                self._finish(key, op_key, operation_id, "unknown", "provider create outcome unconfirmed")
                return {"outcome": "provider_outcome_unknown", "assessment": assessment}
            self._adopt(key, reply["object_id"], op_key=op_key, operation_id=operation_id)
            return {"outcome": "recreated", "assessment": readback}
        if action in {"ENABLE", "RUN"}:
            verb = action.lower()
            object_id = assessment["canonical_object_id"]
            generation = desired["generation"]
            before = next((x for x in inventory["objects"] if x["object_id"] == object_id), None)
            if before is None:
                return {"outcome": "observation_changed", "assessment": assessment}
            basis = ("disabled@" + inventory["observed_at_utc"] if verb == "enable"
                     else "run-after:" + str(before["last_run_at_utc"] or "never")
                     + ":failures:" + str(before["consecutive_failures"]))
            operation_id, op_key = self._set_operation(
                key, verb, generation, object_id, basis=basis)
            if operation_id is None:
                return {"outcome": "unreconciled_operation", "assessment": assessment}
            current = self._entry_by_key(key)["desired"]
            if not self._post_claim_allowed(current):
                self._finish(key, op_key, operation_id, "blocked", "post-claim safety gate denied")
                return {"outcome": "post_claim_gate_denied", "assessment": assessment}
            try:
                method = getattr(self.backend, verb)
                claimed_at = self._entry_by_key(key)["operations"][op_key]["claimed_at_utc"]
                reply = method(copy.deepcopy(binding), object_id=object_id, operation_id=operation_id)
                inv, readback = self._observe(current)
                item = next((x for x in inv["objects"] if x["object_id"] == object_id), None)
                valid = isinstance(reply, dict) and reply.get("status") == "accepted" and reply.get("operation_id") == operation_id and item is not None
                if verb == "enable":
                    valid = valid and item["enabled"]
                else:
                    valid = (valid and item["last_run_at_utc"] is not None
                             and item["execution_state"] in {"running", "idle", "failed"}
                             and self._at_or_after(item["last_run_at_utc"], claimed_at))
                if not valid:
                    raise ValueError("scheduler exact readback disagrees")
            except Exception:
                self._finish(key, op_key, operation_id, "unknown", "provider effect outcome unconfirmed")
                return {"outcome": "provider_outcome_unknown", "assessment": assessment}
            self._finish(key, op_key, operation_id, "succeeded", "exact scheduler readback confirmed")
            return {"outcome": "enabled" if verb == "enable" else "run_requested", "assessment": readback}
        if action == "QUIESCE_DUPLICATES":
            object_id = assessment["stale_object_ids"][0]
            stale = next((x for x in inventory["objects"] if x["object_id"] == object_id), None)
            if stale is None:
                return {"outcome": "observation_changed", "assessment": assessment}
            basis = ("duplicate:" + str(stale["generation"]) + "@"
                     + inventory["observed_at_utc"])
            operation_id, op_key = self._set_operation(
                key, "disable", desired["generation"], object_id, basis=basis)
            if operation_id is None:
                return {"outcome": "unreconciled_operation", "assessment": assessment}
            current = self._entry_by_key(key)["desired"]
            if not self._post_claim_allowed(current):
                self._finish(key, op_key, operation_id, "blocked", "post-claim safety gate denied")
                return {"outcome": "post_claim_gate_denied", "assessment": assessment}
            try:
                reply = self.backend.disable(copy.deepcopy(binding), object_id=object_id, operation_id=operation_id)
                inv, readback = self._observe(current)
                item = next((x for x in inv["objects"] if x["object_id"] == object_id), None)
                if not (isinstance(reply, dict) and reply.get("status") == "accepted"
                        and reply.get("operation_id") == operation_id
                        and (item is None or not item["enabled"])):
                    raise ValueError("disable exact readback disagrees")
            except Exception:
                self._finish(key, op_key, operation_id, "unknown", "provider disable outcome unconfirmed")
                return {"outcome": "provider_outcome_unknown", "assessment": assessment}
            self._finish(key, op_key, operation_id, "succeeded", "stale watchdog quiesced")
            return {"outcome": "duplicates_quiesced", "assessment": readback}
        raise ValueError("unsupported survivability action")
