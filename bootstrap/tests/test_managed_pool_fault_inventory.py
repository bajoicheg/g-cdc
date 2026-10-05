import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]

class ManagedPoolFaultInventory(unittest.TestCase):
    def test_managed_pool_fault_regressions_are_retained(self):
        faults = json.loads((ROOT / 'fault-injection' / 'scenarios.json').read_text())
        ids = {x['id'] for x in faults['scenarios']}
        expected = {'managed-pool-fabricated-worker-launch', 'managed-pool-premature-parent-complete', 'managed-pool-duplicate-active-attempt', 'managed-pool-worker-failure-cancels-unrelated', 'managed-pool-sequential-fallback-drift', 'managed-pool-unintegrated-success-terminal', 'managed-pool-local-branch-fakes-publication', 'managed-pool-bundle-artifact-toctou', 'managed-pool-optional-work-silent-omission', 'managed-pool-retry-reserves-original-budget', 'managed-pool-inmemory-queue-bypasses-durable-cas', 'managed-pool-coordination-ref-split-brain', 'managed-pool-launch-grant-replay', 'managed-pool-history-touch-hidden', 'managed-pool-required-depends-on-optional', 'managed-pool-publication-remote-identity-drift'}
        self.assertTrue(expected <= ids)


if __name__=="__main__":unittest.main()
