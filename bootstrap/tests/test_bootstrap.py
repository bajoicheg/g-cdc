import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from src.cdc27.canonical_source import validate_source_lock
from src.cdc27.release_contract import validate_candidate
from src.cdc27.consumer_lock import validate_lock
from src.cdc27.compatibility import validate_matrix
from src.cdc27.faults import validate_scenarios
def load(p):return json.loads((ROOT/p).read_text())
class Tests(unittest.TestCase):
 def test_source_lock(self):validate_source_lock(load("release/source.lock.json"))
 def test_prior_stable_release_is_enforced(self):
  d=load("release/source.lock.json");d["development_driver_version"]="2.5.0"
  with self.assertRaises(ValueError):validate_source_lock(d)
 def test_patch_release_is_supported(self):
  validate_source_lock(load("release/source.lock.json"))
 def test_external_base_evidence_requires_ref(self):
  d=load("release/source.lock.json");d["base_validation_evidence_ref"]=None
  with self.assertRaises(ValueError):validate_source_lock(d)
 def test_actions_base_evidence_mode_is_supported(self):
  d=load("release/source.lock.json");d["base_validation_run_id"]=123;d["base_validation_evidence_ref"]=None
  validate_source_lock(d)
 def test_compatibility_preserves_history(self):validate_matrix(load("compatibility/matrix.json"))
 def test_fault_suite(self):validate_scenarios(load("fault-injection/scenarios.json"))
 def test_fault_suite_has_release_self_corruption(self):self.assertIn("bootstrap-self-corruption",{x["id"] for x in load("fault-injection/scenarios.json")["scenarios"]})
 def test_consumer_lock_template(self):validate_lock(load("consumer/lock.template.json"))
 def test_candidate_evidence_classes(self):validate_candidate(load("release/candidate.template.json"))
 def test_candidate_cannot_use_package_evidence_as_bootstrap(self):
  d=load("release/candidate.template.json");d["evidence"]["bootstrap"]=["package:self"]
  with self.assertRaises(ValueError):validate_candidate(d)
 def test_three_consumers_are_required(self):
  d=load("release/candidate.template.json");d["evidence"]["consumers"]=["consumer:one","consumer:two"]
  with self.assertRaises(ValueError):validate_candidate(d)
if __name__=="__main__":unittest.main()
