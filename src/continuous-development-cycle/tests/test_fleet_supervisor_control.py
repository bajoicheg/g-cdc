from pathlib import Path
import copy,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import fleet_supervisor_control as m

A="33333333-3333-4333-8333-333333333333";B="44444444-4444-4444-8444-444444444444"
HEAD="a"*40
def inv(name):return {"invocation_id":name,"automation_id":None,"conversation_id":None,"execution_surface":"chat","started_at_utc":"2026-01-01T10:00:00Z"}

class Store:
 def __init__(self):self.rev=None;self.doc=None;self.n=0
 def read(self):return self.rev,copy.deepcopy(self.doc)
 def compare_and_swap(self,expected,doc):
  if self.rev!=expected:raise ValueError("stale expected document revision")
  self.n+=1;self.rev="r"+str(self.n);self.doc=copy.deepcopy(doc);return self.rev

class T(unittest.TestCase):
 def leader(self):
  s=m.initialize("o/fleet","refs/heads/cdc/fleet")
  return m.acquire_record(s,A,"2026-01-01T10:00:00Z",inv("a"))
 def req(self,eid="wake:x",intent=None):
  return {"effect_id":eid,"kind":"project_wake","target":"o/project","observed_fleet_head":HEAD,"intent":intent or {"reason":"stalled"}}
 def test_cas_allows_only_one_subscription_to_become_leader(self):
  store=Store()
  a=m.acquire_cas(store,None,"o/fleet","refs/heads/cdc/fleet",A,"2026-01-01T10:00:00Z",inv("a"))
  self.assertEqual(a["generation"],1)
  with self.assertRaisesRegex(ValueError,"stale"):m.acquire_cas(store,None,"o/fleet","refs/heads/cdc/fleet",B,"2026-01-01T10:00:00Z",inv("b"))
 def test_nonleader_cannot_claim_fleet_effect(self):
  s=self.leader()
  with self.assertRaisesRegex(ValueError,"not fleet leader"):m.claim_effect_record(s,B,1,"b","2026-01-01T10:01:00Z",HEAD,self.req())
 def test_same_effect_id_is_one_shot(self):
  s,d=m.claim_effect_record(self.leader(),A,1,"a","2026-01-01T10:01:00Z",HEAD,self.req())
  self.assertTrue(d["authorizes_effect"]);self.assertEqual(len(s["effects"]),1)
  s2,d2=m.claim_effect_record(s,A,1,"a","2026-01-01T10:02:00Z",HEAD,self.req())
  self.assertFalse(d2["authorizes_effect"]);self.assertEqual(d2["action"],"OBSERVE_EXISTING");self.assertEqual(len(s2["effects"]),1)
 def test_effect_id_collision_fails(self):
  s,_=m.claim_effect_record(self.leader(),A,1,"a","2026-01-01T10:01:00Z",HEAD,self.req())
  with self.assertRaisesRegex(ValueError,"collision"):m.claim_effect_record(s,A,1,"a","2026-01-01T10:02:00Z",HEAD,self.req(intent={"reason":"different"}))
 def test_changed_fleet_head_replans_before_claim(self):
  s,d=m.claim_effect_record(self.leader(),A,1,"a","2026-01-01T10:01:00Z","b"*40,self.req())
  self.assertEqual(d["action"],"REPLAN_FLEET_HEAD");self.assertFalse(d["authorizes_effect"]);self.assertEqual(s["effects"],[])
 def test_unknown_effect_blocks_leader_replacement(self):
  s,_=m.claim_effect_record(self.leader(),A,1,"a","2026-01-01T10:01:00Z",HEAD,self.req())
  s=m.update_effect_record(s,A,1,"a","2026-01-01T10:02:00Z","wake:x","unknown","scheduler:request-1")
  self.assertEqual(m.assess_takeover(s)["action"],"BLOCK_PENDING_EFFECTS")
  q={"owner_id":A,"generation":1,"repository":"o/fleet","source_ref":"refs/heads/cdc/fleet","invocation_id":"a","kind":"executor_stopped","reference":"runtime:a:stopped","pending_shared_writes":False,"external_effects_state":"preserved_unknown"}
  with self.assertRaisesRegex(ValueError,"unresolved side effects"):m.acquire_record(s,B,"2026-01-01T10:03:00Z",inv("b"),quiescence=q)
 def test_terminal_effect_allows_quiescence_based_replacement(self):
  s,_=m.claim_effect_record(self.leader(),A,1,"a","2026-01-01T10:01:00Z",HEAD,self.req())
  s=m.update_effect_record(s,A,1,"a","2026-01-01T10:02:00Z","wake:x","terminal","scheduler:run-1","success")
  q={"owner_id":A,"generation":1,"repository":"o/fleet","source_ref":"refs/heads/cdc/fleet","invocation_id":"a","kind":"executor_stopped","reference":"runtime:a:stopped","pending_shared_writes":False,"external_effects_state":"reconciled"}
  s=m.acquire_record(s,B,"2026-01-01T10:03:00Z",inv("b"),quiescence=q)
  self.assertEqual(s["lease"]["owner_id"],B);self.assertEqual(s["lease"]["generation"],2)

if __name__=="__main__":unittest.main()
