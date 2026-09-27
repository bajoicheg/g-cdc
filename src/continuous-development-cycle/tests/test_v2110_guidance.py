from pathlib import Path
import json,re,unittest

ROOT=Path(__file__).resolve().parents[1]

class T(unittest.TestCase):
 def test_managed_executor_guidance_is_wired(self):
  skill=(ROOT/"SKILL.md").read_text().lower()
  ref=(ROOT/"references"/"managed-executor-pool.md").read_text().lower()
  readme=(ROOT/"README.md").read_text().lower()
  for term in ("managed executor pool","capability-gated","deterministic sequential fallback","must not fabricate subagents","single integrator","attempt lineage","unintegrated successful result","progress is not terminal"):
   self.assertIn(term,skill)
  for term in ("parent authority","capability-gated","sequential fallback","isolated branch/worktree","duplicate-launch","unintegrated","terminal-state"):
   self.assertIn(term,ref)
  self.assertIn("managed executor pool",readme)
  self.assertIn("never fabricate subagents",readme)

 def test_managed_pool_fault_regressions_are_retained(self):
  faults=json.loads((ROOT.parent.parent/"fault-injection"/"scenarios.json").read_text())
  ids={x["id"] for x in faults["scenarios"]}
  expected={
   "managed-pool-fabricated-worker-launch",
   "managed-pool-premature-parent-complete",
   "managed-pool-duplicate-active-attempt",
   "managed-pool-worker-failure-cancels-unrelated",
   "managed-pool-sequential-fallback-drift",
   "managed-pool-unintegrated-success-terminal",
  }
  self.assertTrue(expected<=ids)

 def test_pressure_numbering_is_continuous_through_95(self):
  text=(ROOT/"tests"/"pressure-scenarios.md").read_text()
  numbers=[int(x) for x in re.findall(r"(?m)^## (\d+)\.",text)]
  self.assertEqual(numbers,list(range(1,96)))

 def test_guidance_preserves_authority_boundary(self):
  ref=(ROOT/"references"/"managed-executor-pool.md").read_text().lower()
  for term in ("shared-branch write","merge","release","scope-expansion","scheduler-mutation","user-approval"):
   self.assertIn(term,ref)

 def test_failure_isolation_and_fallback_are_explicit(self):
  ref=(ROOT/"references"/"managed-executor-pool.md").read_text().lower()
  self.assertIn("failure of one worker does not cancel unrelated independent work",ref)
  self.assertIn("same managed pool plan",ref)
  self.assertIn("never fabricate subagents",ref)

if __name__=="__main__":unittest.main()
