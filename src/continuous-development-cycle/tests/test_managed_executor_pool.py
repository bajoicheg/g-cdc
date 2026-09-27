import subprocess,sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import managed_executor_pool as m

FAKE_BASE="a"*40

def plan(base=FAKE_BASE):
 return {
  "schema":"managed-executor-pool-plan/v1","pool_id":"p","change_id":"c",
  "parent_invocation_id":"parent","base_sha":base,"integrator_id":"integrator",
  "max_parallel":2,"total_runtime_budget_seconds":1000,"total_cost_budget_units":100,
  "tasks":[
   {"id":"a","role":"writer","required":True,"dependencies":[],"executor_id":"exec-a",
    "branch":"worker-a","worktree":"worktrees/a","write_paths":["src/a"],
    "expected_outputs":["out:a"],"expected_evidence":["test:a"],"backend_preferences":["codex_compute"],
    "max_runtime_seconds":300,"max_cost_units":30},
   {"id":"b","role":"writer","required":True,"dependencies":[],"executor_id":"exec-b",
    "branch":"worker-b","worktree":"worktrees/b","write_paths":["src/b"],
    "expected_outputs":["out:b"],"expected_evidence":["test:b"],"backend_preferences":["codex_compute"],
    "max_runtime_seconds":300,"max_cost_units":30},
   {"id":"review","role":"review","required":True,"dependencies":["a","b"],"executor_id":"reviewer",
    "branch":None,"worktree":None,"write_paths":[],
    "expected_outputs":["out:review"],"expected_evidence":["review:green"],"backend_preferences":["codex_compute"],
    "max_runtime_seconds":200,"max_cost_units":20},
  ]}

class T(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.repo=Path(self.tmp.name)
  def git(*args):
   return subprocess.check_output(["git","-C",str(self.repo),*args],text=True).strip()
  git("init","-q")
  git("config","user.email","cdc@example.invalid")
  git("config","user.name","CDC Test")
  (self.repo/"seed").write_text("base")
  git("add","seed");git("commit","-q","-m","base")
  self.base=git("rev-parse","HEAD")
  git("switch","-q","-c","worker-a")
  (self.repo/"a").write_text("a");git("add","a");git("commit","-q","-m","a")
  self.result_a=git("rev-parse","HEAD")
  git("switch","-q","-c","worker-b",self.base)
  (self.repo/"b").write_text("b");git("add","b");git("commit","-q","-m","b")
  self.result_b=git("rev-parse","HEAD")

 def tearDown(self):
  self.tmp.cleanup()

 def _accept(self,p,s,task,attempt,changed,outputs,evidence,runtime=10,cost=1,result_commit=None):
  t={x["id"]:x for x in p["tasks"]}[task]
  if result_commit is None and t["role"]=="writer":
   result_commit=self.result_a if task=="a" else self.result_b
  return m.accept_result(
   p,s,task_id=task,attempt_id=attempt,result_ref=f"result:{task}:{attempt}",
   base_sha=p["base_sha"],executor_id=t["executor_id"],parent_invocation_id=p["parent_invocation_id"],
   integrator_id=p["integrator_id"],branch=t["branch"],worktree=t["worktree"],
   result_commit=result_commit,changed_paths=changed,output_refs=outputs,evidence_refs=evidence,
   runtime_seconds=runtime,cost_units=cost,git_worktree=self.repo if t["role"]=="writer" else None)

 def test_parallel_dispatches_two_independent_writers_with_isolation_assignments(self):
  p=plan();s=m.initial_state(p,parallel_capable=True);r=m.dispatch(p,s)
  self.assertEqual(r["task_ids"],["a","b"])
  self.assertEqual([x["branch"] for x in r["assignments"]],["worker-a","worker-b"])
  self.assertEqual([x["worktree"] for x in r["assignments"]],["worktrees/a","worktrees/b"])
  self.assertEqual({x["base_sha"] for x in r["assignments"]},{FAKE_BASE})

 def test_sequential_fallback_dispatches_one_without_fabricating_parallel(self):
  p=plan();s=m.initial_state(p,parallel_capable=False);r=m.dispatch(p,s)
  self.assertEqual(r["task_ids"],["a"]);self.assertTrue(r["fallback_serialized"]);self.assertFalse(r["parallel_capable"])

 def test_overlapping_writer_paths_are_serialized(self):
  p=plan();p["tasks"][1]["write_paths"]=["src/A/sub"];s=m.initial_state(p,parallel_capable=True)
  self.assertEqual(m.dispatch(p,s)["task_ids"],["a"])

 def test_portable_unicode_aliases_are_serialized(self):
  p=plan();p["tasks"][0]["write_paths"]=["src/caf\u00e9"];p["tasks"][1]["write_paths"]=["src/cafe\u0301/x"]
  s=m.initial_state(p,parallel_capable=True);self.assertEqual(m.dispatch(p,s)["task_ids"],["a"])

 def test_dispatch_reserves_inflight_runtime_and_cost_budget(self):
  p=plan();p["total_runtime_budget_seconds"]=400;p["total_cost_budget_units"]=40
  s=m.initial_state(p,parallel_capable=True);r=m.dispatch(p,s)
  self.assertEqual(r["task_ids"],["a"]);self.assertEqual(r["reserved_runtime_seconds"],300);self.assertEqual(r["reserved_cost_units"],30)

 def test_queue_cannot_bypass_parallel_slot_or_write_conflict(self):
  p=plan();p["max_parallel"]=1;s=m.initial_state(p,parallel_capable=True)
  s=m.queue_task(p,s,"a","a1")
  with self.assertRaisesRegex(ValueError,"eligible"):m.queue_task(p,s,"b","b1")

 def test_review_waits_for_integrated_dependencies(self):
  p=plan(self.base);s=m.initial_state(p,parallel_capable=True)
  for task in ("a","b"):
   s=m.queue_task(p,s,task,task+"1");s=m.mark_running(p,s,task,task+"1")
   s=self._accept(p,s,task,task+"1",[f"src/{task}/x"],[f"out:{task}"],[f"test:{task}"])
  self.assertNotIn("review",m.ready_task_ids(p,s))
  s=m.mark_integrated(p,s,"a","result:a:a1");s=m.mark_integrated(p,s,"b","result:b:b1")
  self.assertIn("review",m.ready_task_ids(p,s))

 def test_result_identity_and_exact_assigned_branch_are_verified(self):
  p=plan(self.base);s=m.initial_state(p,parallel_capable=True);s=m.queue_task(p,s,"a","a1");s=m.mark_running(p,s,"a","a1")
  t=p["tasks"][0]
  with self.assertRaisesRegex(ValueError,"assignment identity"):
   m.accept_result(p,s,task_id="a",attempt_id="a1",result_ref="r",base_sha=self.base,
    executor_id="other",parent_invocation_id="parent",integrator_id="integrator",
    branch=t["branch"],worktree=t["worktree"],result_commit=self.result_a,
    changed_paths=["src/a/x"],output_refs=["out:a"],evidence_refs=["test:a"],
    runtime_seconds=1,cost_units=1,git_worktree=self.repo)
  with self.assertRaisesRegex(ValueError,"exact assigned branch head"):
   self._accept(p,s,"a","a1",["src/a/x"],["out:a"],["test:a"],result_commit=self.result_b)

 def test_result_git_ancestry_is_live_verified(self):
  p=plan(self.base);s=m.initial_state(p,parallel_capable=True);s=m.queue_task(p,s,"a","a1");s=m.mark_running(p,s,"a","a1")
  tree=subprocess.check_output(["git","-C",str(self.repo),"rev-parse",f"{self.result_a}^{{tree}}"],text=True).strip()
  unrelated=subprocess.check_output(["git","-C",str(self.repo),"commit-tree",tree,"-m","unrelated"],text=True).strip()
  subprocess.check_call(["git","-C",str(self.repo),"branch","-f","worker-a",unrelated],stdout=subprocess.DEVNULL)
  with self.assertRaisesRegex(ValueError,"does not descend"):
   self._accept(p,s,"a","a1",["src/a/x"],["out:a"],["test:a"],result_commit=unrelated)

 def test_unintegrated_success_blocks_terminal(self):
  p=plan(self.base);s=m.initial_state(p,parallel_capable=True);s=m.queue_task(p,s,"a","a1");s=m.mark_running(p,s,"a","a1")
  s=self._accept(p,s,"a","a1",["src/a/x"],["out:a"],["test:a"])
  r=m.assess(p,s);self.assertFalse(r["terminal_allowed"]);self.assertIn("a:unintegrated_success",r["blockers"])

 def test_failed_worker_does_not_remove_unrelated_ready_task(self):
  p=plan();s=m.initial_state(p,parallel_capable=True);s=m.queue_task(p,s,"a","a1");s=m.mark_running(p,s,"a","a1")
  s=m.fail_attempt(p,s,"a","a1",terminal_status="failed")
  self.assertIn("b",m.ready_task_ids(p,s));self.assertIn("b",m.dispatch(p,s)["task_ids"])

 def test_retry_preserves_attempt_history(self):
  p=plan();s=m.initial_state(p,parallel_capable=True);s=m.queue_task(p,s,"a","a1");s=m.fail_attempt(p,s,"a","a1",terminal_status="stale")
  s=m.retry_task(p,s,"a");s=m.queue_task(p,s,"a","a2");self.assertEqual(s["tasks"][0]["attempt_ids"],["a1","a2"])

 def test_result_must_stay_in_portable_write_set(self):
  p=plan(self.base);s=m.initial_state(p,parallel_capable=True);s=m.queue_task(p,s,"a","a1");s=m.mark_running(p,s,"a","a1")
  with self.assertRaisesRegex(ValueError,"escape"):self._accept(p,s,"a","a1",["src/z/x"],["out:a"],["test:a"])

 def test_result_requires_expected_outputs_and_evidence(self):
  p=plan(self.base);s=m.initial_state(p,parallel_capable=True);s=m.queue_task(p,s,"a","a1");s=m.mark_running(p,s,"a","a1")
  with self.assertRaisesRegex(ValueError,"missing expected outputs"):self._accept(p,s,"a","a1",["src/a/x"],["wrong"],["test:a"])
  with self.assertRaisesRegex(ValueError,"missing expected evidence"):self._accept(p,s,"a","a1",["src/a/x"],["out:a"],["wrong"])

 def test_budgets_and_invalid_numeric_inputs_fail_closed(self):
  p=plan(self.base);s=m.initial_state(p,parallel_capable=True);s=m.queue_task(p,s,"a","a1");s=m.mark_running(p,s,"a","a1")
  with self.assertRaisesRegex(ValueError,"task budget"):self._accept(p,s,"a","a1",["src/a/x"],["out:a"],["test:a"],runtime=301)
  for value in (True,float("nan"),float("inf"),0,-1):
   q=plan();q["tasks"][0]["max_runtime_seconds"]=value
   with self.assertRaises(ValueError):m.validate_plan(q)

 def test_duplicate_cyclic_and_missing_writer_isolation_rejected(self):
  p=plan();p["tasks"][1]["id"]="a"
  with self.assertRaisesRegex(ValueError,"duplicate"):m.validate_plan(p)
  p=plan();p["tasks"][0]["dependencies"]=["review"]
  with self.assertRaisesRegex(ValueError,"cyclic"):m.validate_plan(p)
  p=plan();p["tasks"][0]["branch"]=None
  with self.assertRaises(ValueError):m.validate_plan(p)

 def test_authority_is_false_and_full_completion_requires_integration(self):
  p=plan(self.base);s=m.initial_state(p,parallel_capable=True)
  for task in ("a","b"):
   s=m.queue_task(p,s,task,task+"1");s=m.mark_running(p,s,task,task+"1")
   s=self._accept(p,s,task,task+"1",[f"src/{task}/x"],[f"out:{task}"],[f"test:{task}"])
   s=m.mark_integrated(p,s,task,f"result:{task}:{task}1")
  s=m.queue_task(p,s,"review","r1");s=m.mark_running(p,s,"review","r1")
  s=self._accept(p,s,"review","r1",[],["out:review"],["review:green"],result_commit=None)
  self.assertFalse(m.assess(p,s)["complete"])
  s=m.mark_integrated(p,s,"review","result:review:r1");r=m.assess(p,s)
  self.assertTrue(r["complete"]);self.assertTrue(r["terminal_allowed"])
  for name in m.AUTHORITY_FIELDS:self.assertFalse(r[name])

 def test_writer_branch_and_worktree_assignments_are_portable_unique(self):
  p=plan();p["tasks"][1]["branch"]="refs/heads/WORKER-A"
  with self.assertRaisesRegex(ValueError,"branches must be portable-unique"):m.validate_plan(p)
  p=plan();p["tasks"][1]["worktree"]="WORKTREES/A"
  with self.assertRaisesRegex(ValueError,"worktrees must be portable-unique"):m.validate_plan(p)

if __name__=="__main__":unittest.main()
