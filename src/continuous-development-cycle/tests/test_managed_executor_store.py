# R8 corrective pool/store workstream seed; worker removes before final validation.
import copy,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import managed_executor_pool as pool
from managed_executor_store import GitManagedExecutorStore

BASE="a"*40

def plan():
 return {
  "schema":"managed-executor-pool-plan/v1","pool_id":"p","change_id":"c",
  "parent_invocation_id":"parent","base_sha":BASE,"integrator_id":"integrator",
  "max_parallel":1,"total_runtime_budget_seconds":300,"total_cost_budget_units":30,
  "tasks":[
   {"id":"a","role":"writer","required":True,"dependencies":[],"executor_id":"exec-a",
    "branch":"worker-a","worktree":"worktrees/a","write_paths":["src/a"],
    "expected_outputs":["out:a"],"expected_evidence":["test:a"],"backend_preferences":["local"],
    "max_runtime_seconds":300,"max_cost_units":30}
  ]}

class T(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.repo=self.root/"work";self.remote=self.root/"remote.git";self.repo.mkdir()
  subprocess.check_call(["git","init","--bare","-q",str(self.remote)])
  subprocess.check_call(["git","-C",str(self.repo),"init","-q"])
  subprocess.check_call(["git","-C",str(self.repo),"config","user.email","cdc@example.invalid"])
  subprocess.check_call(["git","-C",str(self.repo),"config","user.name","CDC Test"])
  subprocess.check_call(["git","-C",str(self.repo),"remote","add","origin",str(self.remote)])
  self.plan=plan()
  self.ref="refs/heads/cdc/pool-state"
  self.store=GitManagedExecutorStore(
   self.repo,"origin",self.ref,self.plan,
   protected_refs=["refs/heads/main","refs/heads/integration"])
  self.state=pool.initial_state(self.plan,parallel_capable=True)

 def tearDown(self):self.tmp.cleanup()

 def git(self,*args,input=None):
  r=subprocess.run(["git","-C",str(self.repo),*args],input=input,text=True,
                   stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
  return r.stdout.strip()

 def test_initial_cas_and_exact_canonical_readback(self):
  rev=self.store.compare_and_swap(None,self.state)
  observed,state=self.store.read()
  self.assertEqual(observed,rev);self.assertEqual(state,self.state)
  payload=self.git("show",f"{rev}:pool-state.json")
  self.assertEqual(payload, __import__("json").dumps(self.state,sort_keys=True,separators=(",",":"),ensure_ascii=False))

 def test_real_store_allows_exactly_one_stale_competing_queue_reservation(self):
  rev=self.store.compare_and_swap(None,self.state)
  first=pool.queue_task_cas(self.store,rev,self.plan,"a","a1",reservation_token="reserve:a1")
  self.assertTrue(first["launch_allowed"])
  with self.assertRaisesRegex(ValueError,"stale expected pool-store revision"):
   pool.queue_task_cas(self.store,rev,self.plan,"a","a2",reservation_token="reserve:a2")
  live_rev,live=self.store.read()
  self.assertEqual(live_rev,first["store_revision"])
  task=live["tasks"][0]
  self.assertEqual(task["attempt_ids"],["a1"]);self.assertEqual(task["reservation_token"],"reserve:a1")

 def test_stale_cas_and_remote_ref_movement_fail_closed(self):
  rev=self.store.compare_and_swap(None,self.state)
  with self.assertRaisesRegex(ValueError,"stale expected managed-executor store revision"):
   self.store.compare_and_swap(None,self.state)
  rows1=[f"{rev}\t{self.ref}"];rows2=[f"{'b'*40}\t{self.ref}"]
  with mock.patch.object(self.store,"_remote_rows",side_effect=[rows1,rows2]):
   with self.assertRaisesRegex(ValueError,"moved during read"):
    self.store.read()

 def test_malformed_remote_state_is_rejected(self):
  rev=self.store.compare_and_swap(None,self.state)
  blob=self.git("hash-object","-w","--stdin",input='{"schema":"broken"}\n')
  tree=self.git("mktree",input=f"100644 blob {blob}\tpool-state.json\n")
  bad=self.git("commit-tree",tree,"-p",rev,input="malformed\n")
  subprocess.check_call(["git","-C",str(self.repo),"push","-q","origin",f"{bad}:{self.ref}"])
  with self.assertRaises(ValueError):self.store.read()

 def test_identity_mismatch_and_forbidden_ref_aliases_are_rejected(self):
  bad=copy.deepcopy(self.state);bad["pool_id"]="other"
  with self.assertRaisesRegex(ValueError,"pool_id mismatch"):
   self.store.compare_and_swap(None,bad)
  with self.assertRaisesRegex(ValueError,"portable-isolated"):
   GitManagedExecutorStore(self.repo,"origin","refs/heads/MAIN",self.plan,
                           protected_refs=["refs/heads/main"])
  with self.assertRaisesRegex(ValueError,"portable-isolated"):
   GitManagedExecutorStore(self.repo,"origin","refs/heads/WORKER-A",self.plan)

 def test_remote_fetch_push_configuration_must_match(self):
  other=self.root/"other.git";subprocess.check_call(["git","init","--bare","-q",str(other)])
  subprocess.check_call(["git","-C",str(self.repo),"remote","set-url","--add","--push","origin",str(other)])
  with self.assertRaisesRegex(ValueError,"identical fetch/push"):
   GitManagedExecutorStore(self.repo,"origin","refs/heads/cdc/other",self.plan)

if __name__=="__main__":unittest.main()
