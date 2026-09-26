from pathlib import Path
import copy,json,sys,unittest
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
 def test_failed_worker_blocks(self):
  d=self.base();d["worker_results"][0]["state"]="failed"
  self.assertIn("worker_not_success:task-model",evaluate(d)["blockers"])
 def test_failed_worker_can_report_failure_without_success_outputs(self):
  d=self.base();r=d["worker_results"][0];r["state"]="failed";r["output_refs"]=[];r["evidence_refs"]=["failure:worker-log"]
  self.assertIn("worker_not_success:task-model",evaluate(d)["blockers"])
 def test_missing_worker_result_blocks(self):
  d=self.base();d["worker_results"]=d["worker_results"][:1]
  self.assertIn("missing_worker_result:task-ui",evaluate(d)["blockers"])
 def test_result_identity_must_match_contract(self):
  d=self.base();d["worker_results"][0]["worker_id"]="other-worker"
  with self.assertRaises(ValueError):evaluate(d)
 def test_result_base_must_match_assignment(self):
  d=self.base();d["worker_results"][0]["base_sha"]="6"*40
  with self.assertRaises(ValueError):evaluate(d)
 def test_changed_path_must_stay_inside_assigned_write_set(self):
  d=self.base();d["worker_results"][0]["changed_paths"]=["src/ui/foreign.py"]
  with self.assertRaises(ValueError):evaluate(d)
 def test_force_push_never_allowed(self):
  d=self.base();d["force_push_requested"]=True
  r=evaluate(d);self.assertIn("force_push_forbidden",r["blockers"]);self.assertFalse(r["authorizes_force_push"])
 def test_unresolved_conflict_blocks(self):
  d=self.base();d["unresolved_conflicts"]=["src/model/model.py"]
  self.assertIn("unresolved_conflicts",evaluate(d)["blockers"])
 def test_contract_change_mismatch_rejected(self):
  d=self.base();d["worker_contract"]["change_id"]="other-change"
  with self.assertRaises(ValueError):evaluate(d)
 def test_missing_expected_evidence_rejected(self):
  d=self.base();d["worker_results"][0]["evidence_refs"]=["test:other"]
  with self.assertRaises(ValueError):evaluate(d)
 def test_missing_expected_output_rejected(self):
  d=self.base();d["worker_results"][0]["output_refs"]=["commit:other"]
  with self.assertRaises(ValueError):evaluate(d)
 def test_successful_writer_requires_change_and_new_sha(self):
  d=self.base();d["worker_results"][0]["changed_paths"]=[]
  with self.assertRaises(ValueError):evaluate(d)
  d=self.base();d["worker_results"][0]["result_sha"]=d["worker_results"][0]["base_sha"]
  with self.assertRaises(ValueError):evaluate(d)
 def test_non_writer_success_must_keep_base_sha(self):
  d=self.base()
  a=d["worker_contract"]["assignments"][0]
  a["role"]="review";a["write_paths"]=[];a["worker_id"]="reviewer";a["task_id"]="review";a["expected_outputs"]=["review:report"];a["expected_evidence"]=["review:green"]
  d["worker_contract"]["assignments"]=[a]
  d["worker_results"]=[{"worker_id":"reviewer","task_id":"review","role":"review","base_sha":d["expected_shared_head"],"result_sha":"4"*40,"state":"success","changed_paths":[],"output_refs":["review:report"],"evidence_refs":["review:green"]}]
  with self.assertRaises(ValueError):evaluate(d)
 def test_non_writer_result_cannot_mutate(self):
  d=self.base()
  a=d["worker_contract"]["assignments"][0]
  a["role"]="review";a["write_paths"]=[];a["worker_id"]="reviewer";a["task_id"]="review"
  d["worker_contract"]["assignments"]= [a]
  d["worker_results"]=[{"worker_id":"reviewer","task_id":"review","role":"review","base_sha":d["expected_shared_head"],"result_sha":"4"*40,"state":"success","changed_paths":["src/fix.py"],"output_refs":["review:report"],"evidence_refs":["review:green"]}]
  with self.assertRaises(ValueError):evaluate(d)
if __name__=="__main__":unittest.main()
