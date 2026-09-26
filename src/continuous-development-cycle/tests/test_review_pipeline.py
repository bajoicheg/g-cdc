from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from review_pipeline import evaluate

class T(unittest.TestCase):
 def base(self): return json.loads((ROOT/"templates"/"review-pipeline.json").read_text())
 def test_template_two_stage_green(self):
  r=evaluate(self.base());self.assertTrue(r["review_green"]);self.assertEqual(r["action"],"REVIEW_GREEN")
  self.assertFalse(r["authorizes_merge"]);self.assertFalse(r["authorizes_release"])
 def test_quality_cannot_precede_spec_green(self):
  d=self.base();d["spec_compliance"]={"state":"red","reviewer_ref":"reviewer:spec","sequence":1,"evidence_refs":["review:red"],"findings":["wrong behavior"]}
  r=evaluate(d);self.assertIn("quality_review_before_spec_green",r["blockers"]);self.assertFalse(r["review_green"])
 def test_reviewers_must_be_independent(self):
  d=self.base();d["code_quality"]["reviewer_ref"]="reviewer:spec"
  self.assertIn("reviewers_not_independent",evaluate(d)["blockers"])
 def test_findings_block_green(self):
  d=self.base();d["code_quality"]["findings"]=["simplify unsafe branch"]
  self.assertIn("unresolved_quality_findings",evaluate(d)["blockers"])
 def test_quality_required_after_spec(self):
  d=self.base();d["code_quality"]={"state":"not_run","reviewer_ref":None,"sequence":None,"evidence_refs":[],"findings":[]}
  self.assertIn("code_quality_review_required",evaluate(d)["blockers"])
if __name__=="__main__": unittest.main()
