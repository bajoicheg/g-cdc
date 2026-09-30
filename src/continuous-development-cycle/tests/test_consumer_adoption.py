from pathlib import Path
import copy,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from consumer_adoption import assess

A="a"*40;B="b"*40;TREE="c"*40
REQ=[".agents/skills/continuous-development-cycle","docs/cdc-consumer-lock.json","docs/development-cycle.yaml","docs/work-status/current.md","docs/cdc-adoption-2.11.3.md"]

def state():
 return {"schema":"consumer-adoption-publication/v1","source_head":A,"target_ref":"refs/heads/main","target_version":"2.11.3",
  "target_package_tree":TREE,"required_paths":REQ,"prepared_paths":[],"final_tree_sha":None,"observed_package_tree":None,
  "candidate_commit":None,"live_source_head":A,"publication_claim":None,"published_head":None,"readback_package_tree":None}

class T(unittest.TestCase):
 def ready(self):
  d=state();d["prepared_paths"]=REQ[:];d["final_tree_sha"]="d"*40;d["observed_package_tree"]=TREE;d["candidate_commit"]=B
  claim=assess(d)["claim"];d["publication_claim"]=claim;return d
 def test_partial_adoption_never_moves_shared_ref(self):
  d=state();d["prepared_paths"]=[REQ[0]]
  r=assess(d);self.assertEqual(r["action"],"PREPARE_DETACHED");self.assertFalse(r["publication_prerequisites_satisfied"]);self.assertFalse(r["authorizes_ref_move"])
 def test_version_only_preparation_is_still_detached(self):
  d=state();d["prepared_paths"]=[REQ[0],REQ[1]]
  self.assertEqual(assess(d)["action"],"PREPARE_DETACHED")
 def test_exact_tree_and_full_metadata_reaches_one_publish_boundary(self):
  d=state();d["prepared_paths"]=REQ[:];d["final_tree_sha"]="d"*40;d["observed_package_tree"]=TREE;d["candidate_commit"]=B
  r=assess(d);self.assertEqual(r["action"],"CLAIM_CONDITIONAL_PUBLISH");self.assertFalse(r["authorizes_ref_move"])
  d["publication_claim"]=r["claim"];r=assess(d);self.assertEqual(r["action"],"READY_CONDITIONAL_FAST_FORWARD");self.assertTrue(r["publication_prerequisites_satisfied"]);self.assertFalse(r["authorizes_force_push"])
 def test_live_head_move_replans_before_publication(self):
  d=state();d["prepared_paths"]=REQ[:];d["final_tree_sha"]="d"*40;d["observed_package_tree"]=TREE;d["candidate_commit"]=B;d["live_source_head"]="e"*40
  self.assertEqual(assess(d)["action"],"REPLAN_FRESH_HEAD")
 def test_wrong_package_tree_blocks_candidate_publication(self):
  d=state();d["prepared_paths"]=REQ[:];d["final_tree_sha"]="d"*40;d["observed_package_tree"]="e"*40
  self.assertEqual(assess(d)["action"],"REJECT_PACKAGE_DRIFT")
 def test_complete_requires_exact_published_head_and_readback(self):
  d=self.ready();d["published_head"]=B
  self.assertEqual(assess(d)["action"],"READBACK_PUBLISHED_PACKAGE")
  d["readback_package_tree"]=TREE;self.assertEqual(assess(d)["action"],"COMPLETE")
 def test_wrong_published_head_reconciles_not_retries(self):
  d=self.ready();d["published_head"]="f"*40
  self.assertEqual(assess(d)["action"],"RECONCILE_PUBLICATION")

if __name__=="__main__":unittest.main()
