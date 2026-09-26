from pathlib import Path
import copy,json,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from parallel_task_planner import plan

class T(unittest.TestCase):
 def base(self):return json.loads((ROOT/"templates"/"parallel-task-plan.json").read_text())
 def test_independent_writers_share_wave(self):
  r=plan(self.base())
  self.assertEqual(r["waves"][0]["task_ids"],["task-model","task-ui"])
  self.assertEqual(r["waves"][1]["task_ids"],["task-review"])
  self.assertLess(r["parallel_estimate_seconds"],r["sequential_estimate_seconds"])
  self.assertFalse(r["authorizes_worker_launch"]);self.assertFalse(r["authorizes_merge"])
 def test_overlapping_writers_serialize(self):
  d=self.base();d["tasks"][1]["write_paths"]=["src/model/sub"]
  r=plan(d)
  self.assertNotEqual(r["waves"][0]["task_ids"],["task-model","task-ui"])
  self.assertNotIn("task-ui",r["waves"][0]["task_ids"])
 def test_cycle_rejected(self):
  d=self.base();d["tasks"][0]["dependencies"]=["task-review"]
  with self.assertRaises(ValueError):plan(d)
 def test_non_writer_cannot_claim_write_set(self):
  d=self.base();d["tasks"][2]["write_paths"]=["docs/review.md"]
  with self.assertRaises(ValueError):plan(d)
if __name__=="__main__":unittest.main()
