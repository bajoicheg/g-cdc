from pathlib import Path
import json,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import execution_lease_v2 as leasev2
from execution_liveness import classify

OWNER="11111111-1111-4111-8111-111111111111"
INV={"invocation_id":"chat-a","automation_id":None,"conversation_id":None,"execution_surface":"chat","started_at_utc":"2026-01-01T10:00:00Z"}

class T(unittest.TestCase):
 def owned(self):
  r=leasev2.initialize("o/r","refs/heads/main")
  return leasev2.acquire(r,OWNER,"2026-01-01T10:00:00Z",invocation=INV,ttl=1200)
 def runtime(self,state="running",inv="chat-a"):
  return {"schema":"runtime-observation/v1","invocation_id":inv,"state":state,"observed_at_utc":"2026-01-01T10:05:00Z","evidence_ref":"runtime:test"}
 def test_owner_record_without_runtime_is_not_active(self):
  self.assertEqual(classify(self.owned(),None,"2026-01-01T10:05:00Z")["state"],"unknown")
 def test_exact_running_runtime_plus_fresh_lease_is_active(self):
  self.assertEqual(classify(self.owned(),self.runtime(),"2026-01-01T10:05:00Z")["state"],"active")
 def test_stopped_clean_owner_is_orphaned_recoverable(self):
  r=classify(self.owned(),self.runtime("stopped"),"2026-01-01T10:05:00Z")
  self.assertEqual(r["state"],"orphaned_recoverable");self.assertTrue(r["quiescence_candidate"]);self.assertFalse(r["authorizes_takeover"])
 def test_stopped_with_guard_is_blocked_unknown_effects(self):
  r=self.owned();r["external_guard"]={"intent":{"state":"submitting"}}
  with self.assertRaises(ValueError): leasev2.validate(r)
 def test_stopped_with_pending_shared_write_is_blocked(self):
  r=self.owned();r["finalization"]["pending_shared_writes"]=True
  self.assertEqual(classify(r,self.runtime("stopped"),"2026-01-01T10:05:00Z")["state"],"blocked_unknown_effects")
 def test_mismatched_runtime_never_proves_active_or_stopped(self):
  self.assertEqual(classify(self.owned(),self.runtime("stopped","other"),"2026-01-01T10:05:00Z")["state"],"unknown")
 def test_expired_lease_plus_running_claim_is_unknown_not_active(self):
  self.assertEqual(classify(self.owned(),self.runtime(),"2026-01-01T10:25:00Z")["state"],"unknown")
 def test_released_is_released_without_runtime(self):
  r=leasev2.initialize("o/r","refs/heads/main")
  self.assertEqual(classify(r,None,"2026-01-01T10:05:00Z")["state"],"released")
 def test_old_running_observation_is_unknown_even_when_lease_was_renewed(self):
  r=self.owned()
  r=leasev2.renew(r,OWNER,1,"chat-a","2026-01-01T10:09:00Z",activity_ref="git:new",ttl=1200)
  self.assertEqual(classify(r,self.runtime("running"),"2026-01-01T10:09:30Z")["state"],"unknown")

if __name__=="__main__":unittest.main()
