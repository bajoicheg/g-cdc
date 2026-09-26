from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from parallel_benchmark import evaluate

class T(unittest.TestCase):
 def base(self):return json.loads((ROOT/"templates"/"parallel-benchmark.json").read_text())
 def test_template_demonstrates_benefit(self):
  r=evaluate(self.base());self.assertTrue(r["passed"]);self.assertGreater(r["speedup_ratio"],1)
  self.assertFalse(r["authorizes_worker_launch"]);self.assertFalse(r["authorizes_release"])
 def test_slower_parallel_run_fails(self):
  d=self.base();d["parallel_elapsed_seconds"]=d["sequential_baseline_seconds"]
  self.assertIn("no_wall_clock_improvement",evaluate(d)["blockers"])
 def test_conflict_regression_fails(self):
  d=self.base();d["parallel_unresolved_conflicts"]=1
  self.assertIn("conflict_rate_regressed",evaluate(d)["blockers"])
 def test_rollback_regression_fails(self):
  d=self.base();d["parallel_rollbacks"]=1
  self.assertIn("rollback_rate_regressed",evaluate(d)["blockers"])
if __name__=="__main__":unittest.main()
