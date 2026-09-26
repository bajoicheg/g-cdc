from pathlib import Path
import json,unittest
ROOT=Path(__file__).resolve().parents[1]
class T(unittest.TestCase):
 def test_version_is_291(self):
  version=(ROOT/"VERSION").read_text().strip();self.assertEqual(version,"2.9.1");self.assertEqual(json.loads((ROOT/"manifest.json").read_text())["version"],version)
 def test_skill_names_transactional_controls(self):
  t=(ROOT/"SKILL.md").read_text().lower()
  for term in ("fresh head","schema-typed","detached tree","terminal-provider reconciliation"):self.assertIn(term,t)
 def test_reference_preserves_split_brain_safety(self):
  t=(ROOT/"references"/"transactional-migration-and-provider-reconciliation.md").read_text().lower()
  for term in ("idempotent","pre-commit","operation budget","provider terminal state or ttl alone never grants takeover"):self.assertIn(term,t)
if __name__=="__main__":unittest.main()
