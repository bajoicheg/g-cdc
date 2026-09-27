from pathlib import Path
import copy,hashlib,json,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from worktree_worker_contract import assess
from parallel_task_planner import canonical_plan_ref

class T(unittest.TestCase):
 def base(self):return json.loads((ROOT/"templates"/"worktree-worker-contract.json").read_text())
 def rebind(self,d):
  d["plan_ref"]=canonical_plan_ref(d["plan"]);return d
 def later_wave_case(self,root,integrated_head=None):
  d=self.base();d["plan"]["tasks"][1]["write_paths"]=["src/model/sub"];self.rebind(d)
  d["wave"]=2;d["base_sha"]=integrated_head or "2"*40
  record={"schema":"wave-integration-record/v1","change_id":d["change_id"],"plan_ref":d["plan_ref"],
          "wave":1,"integrated_head":d["base_sha"],"shared_branch":d["shared_branch"],
          "gate_evidence_ref":"integration-gate:wave-1-green","assembly_evidence_ref":"assembly:wave-1@"+d["base_sha"]}
  path=Path(root)/"wave-1-integration.json";path.write_text(json.dumps(record,indent=2)+"\n")
  digest="sha256:"+hashlib.sha256(path.read_bytes()).hexdigest()
  d["prior_wave_integration"]={"wave":1,"integrated_head":d["base_sha"],
                               "artifact_path":"wave-1-integration.json","artifact_sha256":digest}
  a=copy.deepcopy(d["assignments"][1]);a["base_sha"]=d["base_sha"];a["write_paths"]=["src/model/sub"]
  d["assignments"]=[a]
  return d,path
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
 def test_worker_branch_alias_cannot_equal_shared(self):
  d=self.base();d["shared_branch"]="refs/heads/feature/integration";d["plan"]["shared_branch"]="refs/heads/feature/integration"
  d["assignments"][0]["branch"]="feature/integration";self.rebind(d)
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
  self.rebind(d);self.assertTrue(assess(d)["valid"])
 def test_case_only_writer_overlap_rejected(self):
  d=self.base();d["plan"]["tasks"][0]["write_paths"]=["src/UI"];d["plan"]["tasks"][1]["write_paths"]=["src/ui/sub"];self.rebind(d)
  # planner serializes them; forcing both into wave one is therefore invalid.
  with self.assertRaises(ValueError):assess(d)
 def test_later_wave_can_bind_resolved_prior_integration(self):
  with tempfile.TemporaryDirectory() as td:
   d,_=self.later_wave_case(td)
   r=assess(d,evidence_root=td);self.assertTrue(r["valid"]);self.assertEqual(r["wave"],2);self.assertEqual(r["base_sha"],"2"*40)
 def test_later_wave_requires_resolvable_prior_integration(self):
  with tempfile.TemporaryDirectory() as td:
   d,path=self.later_wave_case(td)
   with self.assertRaises(ValueError):assess(d)
   d["prior_wave_integration"]["artifact_sha256"]="sha256:"+"0"*64
   with self.assertRaises(ValueError):assess(d,evidence_root=td)
   d,_=self.later_wave_case(td)
   record=json.loads(path.read_text());record["integrated_head"]="3"*40;path.write_text(json.dumps(record,indent=2)+"\n")
   d["prior_wave_integration"]["artifact_sha256"]="sha256:"+hashlib.sha256(path.read_bytes()).hexdigest()
   with self.assertRaises(ValueError):assess(d,evidence_root=td)
 def test_invented_prior_integration_record_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   d,path=self.later_wave_case(td)
   record=json.loads(path.read_text());record["gate_evidence_ref"]="unverified:never-integrated";record["assembly_evidence_ref"]="unverified:invented-head"
   path.write_text(json.dumps(record,indent=2)+"\n")
   d["prior_wave_integration"]["artifact_sha256"]="sha256:"+hashlib.sha256(path.read_bytes()).hexdigest()
   # A durable artifact still needs distinct gate/assembly refs, but those refs are evidence labels only.
   # The contract cannot independently authenticate external systems; it does require the exact artifact bytes.
   self.assertTrue(assess(d,evidence_root=td)["valid"])
 def test_windows_reserved_or_drive_relative_path_rejected(self):
  for bad in ("C:temp","src/CON","src/com1.txt","src/name.","src/name "):
   d=self.base();d["plan"]["tasks"][0]["write_paths"]=[bad];d["assignments"][0]["write_paths"]=[bad]
   with self.subTest(path=bad):
    with self.assertRaises(ValueError):assess(d)
 def test_embedded_plan_must_match_plan_digest(self):
  d=self.base();d["plan"]["tasks"][0]["expected_outputs"]=["commit:tampered"]
  d["assignments"][0]["expected_outputs"]=["commit:tampered"]
  with self.assertRaises(ValueError):assess(d)
 def test_assignment_set_must_equal_planned_wave(self):
  d=self.base();d["assignments"]=d["assignments"][:1]
  with self.assertRaises(ValueError):assess(d)
if __name__=="__main__":unittest.main()
