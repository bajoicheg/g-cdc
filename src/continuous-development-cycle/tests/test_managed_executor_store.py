import copy,hashlib,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import managed_executor_pool as pool
from managed_executor_store import GitManagedExecutorStore, coordination_store_id_for_endpoint

BASE="a"*40

def plan(coordination_ref,coordination_store_id):
 return {
  "schema":"managed-executor-pool-plan/v1","pool_id":"p","change_id":"c",
  "parent_invocation_id":"parent","base_sha":BASE,"integrator_id":"integrator",
  "coordination_ref":coordination_ref,"coordination_store_id":coordination_store_id,
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
  self.ref="refs/heads/cdc/pool-state"
  self.store_id=coordination_store_id_for_endpoint(str(self.remote), repo_root=self.repo)
  self.plan=plan(self.ref,self.store_id)
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
  self.assertFalse(first["launch_allowed"])
  with self.assertRaisesRegex(ValueError,"stale expected pool-store revision"):
   pool.queue_task_cas(self.store,rev,self.plan,"a","a2",reservation_token="reserve:a2")
  started=pool.claim_launch_cas(self.store,first["store_revision"],self.plan,"a","a1",
                                reservation_token="reserve:a1")
  self.assertTrue(started["launch_allowed"])
  with self.assertRaises(ValueError):
   pool.claim_launch_cas(self.store,first["store_revision"],self.plan,"a","a1",
                         reservation_token="reserve:a1")
  live_rev,live=self.store.read()
  self.assertEqual(live_rev,started["store_revision"])
  task=live["tasks"][0]
  self.assertEqual(task["attempt_ids"],["a1"]);self.assertEqual(task["status"],"running")

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
  q=copy.deepcopy(self.plan);q["coordination_ref"]="refs/heads/MAIN"
  with self.assertRaisesRegex(ValueError,"portable-isolated"):
   GitManagedExecutorStore(self.repo,"origin","refs/heads/MAIN",q,
                           protected_refs=["refs/heads/main"])
  q=copy.deepcopy(self.plan);q["coordination_ref"]="refs/heads/WORKER-A"
  with self.assertRaisesRegex(ValueError,"portable-isolated"):
   GitManagedExecutorStore(self.repo,"origin","refs/heads/WORKER-A",q)

 def test_remote_fetch_push_configuration_must_match(self):
  other=self.root/"other.git";subprocess.check_call(["git","init","--bare","-q",str(other)])
  subprocess.check_call(["git","-C",str(self.repo),"remote","set-url","--add","--push","origin",str(other)])
  with self.assertRaisesRegex(ValueError,"configuration drift"):
   GitManagedExecutorStore(self.repo,"origin",self.ref,self.plan)

 def test_plan_binds_one_coordination_ref_and_store_identity(self):
  with self.assertRaisesRegex(ValueError,"coordination ref does not match"):
   GitManagedExecutorStore(self.repo,"origin","refs/heads/cdc/other",self.plan)
  wrong=copy.deepcopy(self.plan);wrong["coordination_store_id"]="sha256:"+"0"*64
  with self.assertRaisesRegex(ValueError,"identity does not match"):
   GitManagedExecutorStore(self.repo,"origin",self.ref,wrong)

 def test_remote_repointing_is_detected_before_read_or_cas(self):
  rev=self.store.compare_and_swap(None,self.state)
  other=self.root/"other2.git";subprocess.check_call(["git","init","--bare","-q",str(other)])
  subprocess.check_call(["git","-C",str(self.repo),"remote","set-url","origin",str(other)])
  with self.assertRaisesRegex(ValueError,"identity drift"):
   self.store.read()
  with self.assertRaises(ValueError):
   self.store.compare_and_swap(rev,self.state)


 def test_relative_remote_identity_resolves_from_repository_root(self):
  root_a=self.root/"a";root_b=self.root/"b";root_a.mkdir();root_b.mkdir()
  repo_a=root_a/"work";repo_b=root_b/"work";repo_a.mkdir();repo_b.mkdir()
  remote_a=root_a/"remote.git";remote_b=root_b/"remote.git"
  subprocess.check_call(["git","init","--bare","-q",str(remote_a)])
  subprocess.check_call(["git","init","--bare","-q",str(remote_b)])
  for repo in (repo_a,repo_b):
   subprocess.check_call(["git","-C",str(repo),"init","-q"])
   subprocess.check_call(["git","-C",str(repo),"remote","add","origin","../remote.git"])
  id_a=coordination_store_id_for_endpoint("../remote.git",repo_root=repo_a)
  id_b=coordination_store_id_for_endpoint("../remote.git",repo_root=repo_b)
  self.assertNotEqual(id_a,id_b)
  p=plan(self.ref,id_a)
  GitManagedExecutorStore(repo_a,"origin",self.ref,p)
  with self.assertRaisesRegex(ValueError,"identity does not match|identity drift"):
   GitManagedExecutorStore(repo_b,"origin",self.ref,p)

 def test_ssh_username_is_part_of_store_identity(self):
  a=coordination_store_id_for_endpoint("alice@example.com:repo.git")
  b=coordination_store_id_for_endpoint("bob@example.com:repo.git")
  self.assertNotEqual(a,b)

if __name__=="__main__":unittest.main()
