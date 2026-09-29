from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import project_lane_runtime as runtime


class MemoryStore:
    ref = "refs/heads/cdc/project-lanes"
    store_id = "sha256:" + "c" * 64

    def __init__(self):
        self.rev = 0
        self.value = None

    def read(self):
        import copy
        return self.rev, copy.deepcopy(self.value)

    def compare_and_swap(self, expected, value):
        import copy
        if expected != self.rev:
            raise ValueError("stale")
        self.rev += 1
        self.value = copy.deepcopy(value)
        return str(self.rev)


def config(**patch):
    value = {
        "canonical_repository": "bajoicheg/g-cdc",
        "product_source_ref": "refs/heads/main",
        "coordination_ref": "refs/heads/cdc/project-lanes",
        "coordination_store_id": "sha256:" + "c" * 64,
        "policy_authority": "sha256:" + "d" * 64,
    }
    value.update(patch)
    return runtime.LaneRegistryConfig(**value)


class ProjectLaneRegistryBindingTests(unittest.TestCase):
    def test_state_is_content_bound_to_exact_registry_configuration(self):
        store = MemoryStore()
        first = runtime.ProjectLaneCoordinator(store, config())
        snapshot = first.snapshot()
        self.assertEqual(snapshot["config"]["canonical_repository"], "bajoicheg/g-cdc")
        self.assertRegex(snapshot["config_digest"], r"^sha256:[0-9a-f]{64}$")

        drifted = runtime.ProjectLaneCoordinator(
            store, config(policy_authority="sha256:" + "e" * 64))
        with self.assertRaisesRegex(ValueError, "configuration"):
            drifted.snapshot()

    def test_coordination_endpoint_must_match_store_identity(self):
        for value in (
            config(coordination_ref="refs/heads/cdc/other"),
            config(coordination_store_id="sha256:" + "f" * 64),
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                runtime.ProjectLaneCoordinator(MemoryStore(), value)

    def test_source_ref_and_repository_identity_are_canonical(self):
        with self.assertRaises(ValueError):
            config(product_source_ref="main")
        with self.assertRaises(ValueError):
            config(canonical_repository="not-a-repository")

    def test_configuration_digest_is_deterministic(self):
        left = config()
        right = config()
        self.assertEqual(left.digest(), right.digest())


if __name__ == "__main__":
    unittest.main()
