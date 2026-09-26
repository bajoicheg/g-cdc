from pathlib import Path
import copy,json,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from worktree_worker_contract import assess

class T(unittest.TestCase):
 def base(self):return json.loads((ROOT/"templates"/"worktree-worker-contract.json").read_text())
 def test_template_isolated_and_non_authoritative(self):
  r=assess(self.base());self.assertTrue(r["valid"]);self.assertEqual(r["assignment_count"],2);self.assertEqual(r["wave"],1)
  self.assertFalse(r["authorizes_worker_launch"]);self.assertFalse(r["authorizes_shared_branch_write"])
 def test_same_wave_overlap_rejected(self):
  d=self.base();d["assignments"][1]["write_paths"]=["src/model/sub"]
  with self.assertRaises(ValueError):assess(d)
 def test_worker_shared_branch_write_rejected(self):
  d=self.base();d["assignments"][0]["can_write_shared_branch"]=True
  with self.assertRaises(ValueError):assess(d)
 def test_worker_branch_cannot_equal_shared(self):
  d=self.base();d["assignments"][0]["branch"]=d["shared_branch"]
  with self.assertRaises(ValueError):assess(d)
 def test_stale_assignment_base_rejected(self):
  d=self.base();d["assignments"][0]["base_sha"]="2"*40
  with self.assertRaises(ValueError):assess(d)
 def test_first_wave_contract_base_must_match_plan(self):
  d=self.base();d["base_sha"]="2"*40
  for a in d["assignments"]:a["base_sha"]=d["base_sha"]
  with self.assertRaises(ValueError):assess(d)
 def test_assignment_must_match_plan_contract(self):
  d=self.base();d["assignments"][0]["expected_evidence"]=["test:other"]
  with self.assertRaises(ValueError):assess(d)
  d=self.base();d["assignments"][0]["expected_outputs"]=["commit:other"]
  with self.assertRaises(ValueError):assess(d)
  d=self.base();d["assignments"][0]["role"]="review";d["assignments"][0]["write_paths"]=[]
  with self.assertRaises(ValueError):assess(d)
 def test_backslash_write_path_rejected(self):
  d=self.base();d["plan"]["tasks"][0]["write_paths"]=["src\\model"];d["assignments"][0]["write_paths"]=["src\\model"]
  with self.assertRaises(ValueError):assess(d)
 def test_unsafe_write_path_rejected_even_if_plan_and_assignment_match(self):
  d=self.base();d["plan"]["tasks"][0]["write_paths"]=["../escape"];d["assignments"][0]["write_paths"]=["../escape"]
  with self.assertRaises(ValueError):assess(d)
 def test_review_assignment_can_be_read_only_when_plan_says_review(self):
  d=self.base()
  d["plan"]["tasks"]=[{"id":"review","role":"review","dependencies":[],"write_paths":[],"expected_outputs":["review:report"],"expected_evidence":["review:green"],"estimated_seconds":10}]
  d["assignments"]=[{"worker_id":"reviewer","task_id":"review","role":"review","branch":"review/check","worktree_id":"wt-review","base_sha":d["base_sha"],"write_paths":[],"expected_outputs":["review:report"],"expected_evidence":["review:green"],"can_write_shared_branch":False}]
  self.assertTrue(assess(d)["valid"])
 def test_case_only_writer_overlap_rejected(self):
  d=self.base();d["plan"]["tasks"][0]["write_paths"]=["src/UI"];d["plan"]["tasks"][1]["write_paths"]=["src/ui/sub"]
  # planner serializes them; forcing both into wave one is therefore invalid.
  with self.assertRaises(ValueError):assess(d)
 def test_later_wave_can_bind_new_exact_base(self):
  d=self.base()
  d["plan"]["tasks"][1]["write_paths"]=["src/model/sub"]
  d["wave"]=2;d["base_sha"]="2"*40;d["prior_wave_integration"]={"wave":1,"integrated_head":d["base_sha"],"evidence_ref":"integration:wave-1"}
  a=copy.deepcopy(d["assignments"][1]);a["base_sha"]=d["base_sha"];a["write_paths"]=["src/model/sub"]
  d["assignments"]=[a]
  r=assess(d);self.assertTrue(r["valid"]);self.assertEqual(r["wave"],2);self.assertEqual(r["base_sha"],"2"*40)
 def test_later_wave_requires_matching_prior_integration(self):
  d=self.base();d["plan"]["tasks"][1]["write_paths"]=["src/model/sub"];d["wave"]=2;d["base_sha"]="2"*40
  a=copy.deepcopy(d["assignments"][1]);a["base_sha"]=d["base_sha"];a["write_paths"]=["src/model/sub"];d["assignments"]=[a]
  with self.assertRaises(ValueError):assess(d)
  d["prior_wave_integration"]={"wave":1,"integrated_head":"3"*40,"evidence_ref":"integration:wave-1"}
  with self.assertRaises(ValueError):assess(d)
  d["prior_wave_integration"]={"wave":2,"integrated_head":d["base_sha"],"evidence_ref":"integration:wrong-wave"}
  with self.assertRaises(ValueError):assess(d)
 def test_windows_reserved_or_drive_relative_path_rejected(self):
  for bad in ("C:temp","src/CON","src/com1.txt","src/name.","src/name "):
   d=self.base();d["plan"]["tasks"][0]["write_paths"]=[bad];d["assignments"][0]["write_paths"]=[bad]
   with self.subTest(path=bad):
    with self.assertRaises(ValueError):assess(d)
 def test_assignment_set_must_equal_planned_wave(self):
  d=self.base();d["assignments"]=d["assignments"][:1]
  with self.assertRaises(ValueError):assess(d)
if __name__=="__main__":unittest.main()
