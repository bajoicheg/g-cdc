from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from worktree_worker_contract import assess

class T(unittest.TestCase):
 def base(self):return json.loads((ROOT/"templates"/"worktree-worker-contract.json").read_text())
 def test_template_isolated_and_non_authoritative(self):
  r=assess(self.base());self.assertTrue(r["valid"]);self.assertEqual(r["assignment_count"],3)
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
if __name__=="__main__":unittest.main()
