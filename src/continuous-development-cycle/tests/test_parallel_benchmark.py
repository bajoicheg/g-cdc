from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from parallel_benchmark import evaluate

class T(unittest.TestCase):
 def base(self):return json.loads((ROOT/"templates"/"parallel-benchmark.json").read_text())
 def test_template_demonstrates_benefit(self):
  r=evaluate(self.base());self.assertTrue(r["passed"]);self.assertGreater(r["speedup_ratio"],1)
  self.assertEqual(r["candidate_sha"],"1"*40)
  self.assertFalse(r["authorizes_worker_launch"]);self.assertFalse(r["authorizes_release"])
 def test_unobserved_measurement_rejected(self):
  d=self.base();d["observations"][0]["observed"]=False
  with self.assertRaises(ValueError):evaluate(d)
 def test_candidate_sha_required(self):
  d=self.base();d["candidate_sha"]="not-a-sha"
  with self.assertRaises(ValueError):evaluate(d)
 def test_observation_candidate_must_match(self):
  d=self.base();d["observations"][0]["candidate_sha"]="2"*40
  with self.assertRaises(ValueError):evaluate(d)
 def test_observation_environment_must_match(self):
  d=self.base();d["observations"][0]["environment_ref"]="other:env"
  with self.assertRaises(ValueError):evaluate(d)
 def test_observation_plan_must_match(self):
  d=self.base();d["observations"][0]["plan_ref"]="other:plan"
  with self.assertRaises(ValueError):evaluate(d)
 def test_workload_fingerprint_must_match(self):
  d=self.base();d["observations"][1]["workload_fingerprint"]="sha256:"+"2"*64
  with self.assertRaises(ValueError):evaluate(d)
 def test_duplicate_evidence_ref_rejected(self):
  d=self.base();d["observations"][1]["evidence_ref"]=d["observations"][0]["evidence_ref"]
  with self.assertRaises(ValueError):evaluate(d)
 def test_both_modes_required(self):
  d=self.base();d["observations"][1]["mode"]="sequential"
  with self.assertRaises(ValueError):evaluate(d)
 def test_slower_parallel_run_fails(self):
  d=self.base();d["observations"][1]["elapsed_seconds"]=d["observations"][0]["elapsed_seconds"]
  self.assertIn("no_wall_clock_improvement",evaluate(d)["blockers"])
 def test_conflict_regression_fails(self):
  d=self.base();d["parallel_unresolved_conflicts"]=1
  self.assertIn("conflict_rate_regressed",evaluate(d)["blockers"])
 def test_rollback_regression_fails(self):
  d=self.base();d["parallel_rollbacks"]=1
  self.assertIn("rollback_rate_regressed",evaluate(d)["blockers"])
if __name__=="__main__":unittest.main()
