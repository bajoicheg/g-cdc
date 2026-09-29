import copy
import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
if importlib.util.find_spec("watchdog_survivability_runtime"):
    import watchdog_survivability_runtime as runtime_mod
else:
    runtime_mod = None

from test_watchdog_survivability import NOW, desired, inventory, obj


class MemoryStore:
    ref = "refs/heads/cdc/watchdog-survivability"
    store_id = "sha256:" + "c" * 64

    def __init__(self):
        self.revision = 0
        self.value = None
        self.after_cas = None

    def read(self):
        return self.revision, copy.deepcopy(self.value)

    def compare_and_swap(self, expected, value):
        if expected != self.revision:
            raise ValueError("stale")
        self.revision += 1
        self.value = copy.deepcopy(value)
        if self.after_cas:
            self.after_cas(self)
        return str(self.revision)


class RecordingBackend:
    def __init__(self, inv=None):
        self.inventory = copy.deepcopy(inv or inventory([]))
        self.effects = []
        self.lose_create_reply = False
        self.next_id = 1

    def observe(self, binding):
        self.inventory["binding"] = copy.deepcopy(binding)
        return copy.deepcopy(self.inventory)

    def create(self, binding, *, generation, schedule, template_digest, operation_id):
        object_id = f"wd-created-{self.next_id}"
        self.next_id += 1
        self.effects.append(("create", generation, operation_id))
        self.inventory["objects"].append(obj(object_id, generation=generation, schedule=schedule,
                                             template_digest=template_digest, last_run_at_utc=None))
        if self.lose_create_reply:
            raise TimeoutError("reply lost")
        return {"status": "accepted", "object_id": object_id, "generation": generation,
                "operation_id": operation_id}

    def enable(self, binding, *, object_id, operation_id):
        self.effects.append(("enable", object_id, operation_id))
        for item in self.inventory["objects"]:
            if item["object_id"] == object_id:
                item["enabled"] = True
        return {"status": "accepted", "object_id": object_id, "operation_id": operation_id}

    def run(self, binding, *, object_id, operation_id):
        self.effects.append(("run", object_id, operation_id))
        for item in self.inventory["objects"]:
            if item["object_id"] == object_id:
                item["last_run_at_utc"] = NOW
                item["execution_state"] = "running"
        return {"status": "accepted", "object_id": object_id, "operation_id": operation_id}

    def disable(self, binding, *, object_id, operation_id):
        self.effects.append(("disable", object_id, operation_id))
        for item in self.inventory["objects"]:
            if item["object_id"] == object_id:
                item["enabled"] = False
        return {"status": "accepted", "object_id": object_id, "operation_id": operation_id}


class WatchdogSurvivabilityRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(runtime_mod, "watchdog survivability runtime is not implemented")
        self.store = MemoryStore()
        self.backend = RecordingBackend()
        self.runtime = runtime_mod.WatchdogSurvivabilityRuntime(self.store, self.backend, clock=lambda: NOW)
        self.runtime.register(desired(canonical_object_id=None))

    def test_missing_watchdog_fences_generation_before_create_and_adopts_readback(self):
        result = self.runtime.reconcile(desired()["binding"])
        self.assertEqual(result["outcome"], "recreated")
        state = self.runtime.snapshot()
        current = state["entries"][runtime_mod.binding_key(desired()["binding"])]["desired"]
        self.assertEqual(current["generation"], 8)
        self.assertEqual(current["canonical_object_id"], "wd-created-1")
        self.assertEqual([e[0] for e in self.backend.effects], ["create"])

    def test_lost_create_reply_retains_generation_and_never_replays_create(self):
        self.backend.lose_create_reply = True
        first = self.runtime.reconcile(desired()["binding"])
        self.assertEqual(first["outcome"], "provider_outcome_unknown")
        state = self.runtime.snapshot()
        current = state["entries"][runtime_mod.binding_key(desired()["binding"])]["desired"]
        self.assertEqual(current["generation"], 8)
        self.assertIsNone(current["canonical_object_id"])
        self.backend.lose_create_reply = False
        second = self.runtime.reconcile(desired()["binding"])
        self.assertEqual(second["outcome"], "adopted")
        self.assertEqual([e[0] for e in self.backend.effects], ["create"])
        self.assertEqual(self.runtime.snapshot()["entries"][runtime_mod.binding_key(desired()["binding"])]["desired"]["canonical_object_id"], "wd-created-1")

    def test_unknown_create_without_materialization_is_not_replayed(self):
        self.backend.create = self._unknown_without_object
        first = self.runtime.reconcile(desired()["binding"])
        second = self.runtime.reconcile(desired()["binding"])
        self.assertEqual(first["outcome"], "provider_outcome_unknown")
        self.assertEqual(second["outcome"], "unreconciled_operation")
        self.assertEqual([e[0] for e in self.backend.effects], ["create"])

    def _unknown_without_object(self, binding, *, generation, schedule, template_digest, operation_id):
        self.backend.effects.append(("create", generation, operation_id))
        raise TimeoutError("unknown before readback")

    def test_owner_stop_committed_after_claim_blocks_scheduler_io(self):
        fired = {"done": False}
        def pause_after_claim(store):
            if fired["done"] or not store.value:
                return
            entry = next(iter(store.value["entries"].values()))
            if any(op["status"] == "claimed" for op in entry["operations"].values()):
                entry["desired"]["owner_stop_evidence"] = "owner-message:99"
                fired["done"] = True
        self.store.after_cas = pause_after_claim
        result = self.runtime.reconcile(desired()["binding"])
        self.assertEqual(result["outcome"], "post_claim_gate_denied")
        self.assertEqual(self.backend.effects, [])

    def test_duplicate_stale_generation_is_quiesced_not_recreated(self):
        d = desired()
        self.store = MemoryStore()
        self.backend = RecordingBackend(inventory([obj(), obj("wd-old", generation=6)]))
        self.runtime = runtime_mod.WatchdogSurvivabilityRuntime(self.store, self.backend, clock=lambda: NOW)
        self.runtime.register(d)
        result = self.runtime.reconcile(d["binding"])
        self.assertEqual(result["outcome"], "duplicates_quiesced")
        self.assertEqual([(e[0], e[1]) for e in self.backend.effects], [("disable", "wd-old")])

    def test_disabled_and_overdue_use_enable_and_run_without_generation_bump(self):
        for current, effect in ((obj(enabled=False), "enable"),
                                (obj(last_run_at_utc="2026-09-29T09:00:00Z"), "run")):
            with self.subTest(effect=effect):
                store = MemoryStore()
                backend = RecordingBackend(inventory([current]))
                runtime = runtime_mod.WatchdogSurvivabilityRuntime(store, backend, clock=lambda: NOW)
                runtime.register(desired())
                result = runtime.reconcile(desired()["binding"])
                self.assertEqual(result["outcome"], effect + "d")
                self.assertEqual(backend.effects[0][0], effect)
                self.assertEqual(runtime.snapshot()["entries"][runtime_mod.binding_key(desired()["binding"])]["desired"]["generation"], 7)

    def test_owner_paused_or_terminal_state_produces_no_scheduler_effect(self):
        for d, inv in (
            (desired(canonical_object_id=None, owner_stop_evidence="owner:stop"), inventory([])),
            (desired(canonical_object_id=None), inventory([], project={"state": "terminal", "source_revision": "a" * 40,
                "terminal_proof": {"project_id": "alpha", "source_ref": "refs/heads/main", "source_revision": "a" * 40,
                                   "evidence_ref": "git:terminal"}})),
        ):
            with self.subTest(d=d):
                store = MemoryStore()
                backend = RecordingBackend(inv)
                runtime = runtime_mod.WatchdogSurvivabilityRuntime(store, backend, clock=lambda: NOW)
                runtime.register(d)
                result = runtime.reconcile(d["binding"])
                self.assertEqual(result["outcome"], "no_effect")
                self.assertEqual(backend.effects, [])

    def test_stale_registered_generation_cannot_overwrite_newer_runtime_generation(self):
        self.runtime.reconcile(desired()["binding"])
        with self.assertRaisesRegex(ValueError, "generation"):
            self.runtime.register(desired(canonical_object_id=None))


if __name__ == "__main__":
    unittest.main()
