from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from integration_gate import evaluate

class T(unittest.TestCase):
 def base(self):return json.loads((ROOT/"templates"/"integration-gate.json").read_text())
 def test_ready_without_granting_shared_write(self):
  r=evaluate(self.base());self.assertTrue(r["ready"]);self.assertEqual(r["action"],"READY_FOR_INTEGRATOR");self.assertEqual(r["wave"],1)
  self.assertEqual(r["next_gate"],"cdc_2.10.1_review_branch_finish_then_2.10.0_verification")
  self.assertFalse(r["authorizes_shared_branch_write"]);self.assertFalse(r["authorizes_merge"])
 def test_moved_shared_head_requires_reconcile(self):
  d=self.base();d["observed_shared_head"]="5"*40
  self.assertIn("shared_head_moved_reconcile_required",evaluate(d)["blockers"])
 def test_failed_or_stale_worker_blocks(self):
  d=self.base();d["worker_results"][0]["state"]="failed";d["worker_results"][1]["base_sha"]="6"*40
  r=evaluate(d);self.assertIn("worker_not_success:task-model",r["blockers"]);self.assertIn("worker_base_stale:task-ui",r["blockers"])
 def test_same_wave_worker_result_overlap_blocks(self):
  d=self.base();d["worker_results"][1]["changed_paths"]=["src/model/other.py"]
  self.assertTrue(any(x.startswith("same_wave_worker_result_path_overlap:") for x in evaluate(d)["blockers"]))
 def test_force_push_never_allowed(self):
  d=self.base();d["force_push_requested"]=True
  r=evaluate(d);self.assertIn("force_push_forbidden",r["blockers"]);self.assertFalse(r["authorizes_force_push"])
 def test_unresolved_conflict_blocks(self):
  d=self.base();d["unresolved_conflicts"]=["src/model/model.py"]
  self.assertIn("unresolved_conflicts",evaluate(d)["blockers"])
 def test_non_writer_result_cannot_mutate(self):
  d=self.base();d["worker_results"]=[{"worker_id":"reviewer","task_id":"review","role":"review","base_sha":d["expected_shared_head"],"result_sha":"4"*40,"state":"success","changed_paths":["src/fix.py"],"evidence_refs":["review:green"]}]
  with self.assertRaises(ValueError):evaluate(d)
if __name__=="__main__":unittest.main()
