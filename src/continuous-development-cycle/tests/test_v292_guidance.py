from pathlib import Path
import json,unittest
ROOT=Path(__file__).resolve().parents[1]
class T(unittest.TestCase):
 def test_timestamp_guidance(self):
  t=(ROOT/"SKILL.md").read_text().lower()
  for term in ("progress-is-not-terminal","[hh:mm dd.mm]","actual current moscow time","rca-to-roadmap","exactly one improvement"):
   self.assertIn(term,t)
if __name__=="__main__":
 unittest.main()
