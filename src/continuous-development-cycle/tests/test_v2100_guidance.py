from pathlib import Path
import json,unittest
ROOT=Path(__file__).resolve().parents[1]

class T(unittest.TestCase):
 def test_behavioral_tdd_and_verification_guidance(self):
  t=(ROOT/"SKILL.md").read_text().lower()
  for term in ("behavioral skill tdd","pressure scenario","verification-before-terminal","systematic debugging","baseline red","corrected green"):
   self.assertIn(term,t)
  ref=(ROOT/"references"/"behavioral-tdd-and-verification.md").read_text().lower()
  for term in ("superpowers","behavioral eval","verification gate","evidence-only","no authority"):
   self.assertIn(term,ref)

if __name__=="__main__":
 unittest.main()
