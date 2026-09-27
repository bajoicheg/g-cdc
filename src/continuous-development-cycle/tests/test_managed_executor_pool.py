import copy,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import managed_executor_pool as m

BASE="a"*40

def plan():
 return {
  "schema":"managed-executor-pool-plan/v1","pool_id":"p","change_id":"c",
  "parent_invocation_id":"parent","base_sha":BASE,"integrator_id":"integrator",
  "max_parallel":2,"total_runtime_budget_seconds":1000,"total_cost_budget_units":100,
  "tasks":[
   {"id":"a","role":"writer","required":True,"dependencies":[],"write_paths":["src/a"],
    "expected_outputs":["out:a"],"expected_evidence":["test:a"],"backend_preferences":["codex_compute"],
    "max_runtime_seconds":300,"max_cost_units":30},
   {"id":"b","role":"writer","required":True,"dependencies":[],"write_paths":["src/b"],
    "expected_outputs":["out:b"],"expected_evidence":["test:b"],"backend_preferences":["codex_compute"],
    "max_runtime_seconds":300,"max_cost_units":30},
   {"id":"review","role":"review","required":True,"dependencies":["a","b"],"write_paths":[],
    "expected_outputs":["out:review"],"expected_evidence":["review:green"],"backend_preferences":["codex_compute"],
    "max_runtime_seconds":200,"max_cost_units":20},
  ]}

def accept(p,s,task,attempt,changed,outputs,evidence,runtime=10,cost=1):
 return m.accept_result(p,s,task_id=task,attempt_id=attempt,result_ref=f"result:{task}:{attempt}",
  base_sha=BASE,changed_paths=changed,output_refs=outputs,evidence_refs=evidence,
  runtime_seconds=runtime,cost_units=cost)

class T(unittest.TestCase):
 def test_parallel_dispatches_two_independent_writers(self):
  p=plan();s=m.initial_state(p,parallel_capable=True)
  self.assertEqual(m.dispatch(p,s)["task_ids"],["a","b"])

 def test_sequential_fallback_dispatches_one_without_fabricating_parallel(self):
  p=plan();s=m.initial_state(p,parallel_capable=False);r=m.dispatch(p,s)
  self.assertEqual(r["task_ids"],["a"]);self.assertTrue(r["fallback_serialized"]);self.assertFalse(r["parallel_capable"])

 def test_overlapping_writer_paths_are_serialized(self):
  p=plan();p["tasks"][1]["write_paths"]=["src/A/sub"];s=m.initial_state(p,parallel_capable=True)
  self.assertEqual(m.dispatch(p,s)["task_ids"],["a"])

 def test_portable_unicode_aliases_are_serialized(self):
  p=plan();p["tasks"][0]["write_paths"]=["src/caf\u00e9"];p["tasks"][1]["write_paths"]=["src/cafe\u0301/x"]
  s=m.initial_state(p,parallel_capable=True);self.assertEqual(m.dispatch(p,s)["task_ids"],["a"])

 def test_queue_cannot_bypass_parallel_slot_or_write_conflict(self):
  p=plan();p["max_parallel"]=1;s=m.initial_state(p,parallel_capable=True)
  s=m.queue_task(p,s,"a","a1")
  with self.assertRaisesRegex(ValueError,"eligible"):
   m.queue_task(p,s,"b","b1")

 def test_review_waits_for_integrated_dependencies(self):
  p=plan();s=m.initial_state(p,parallel_capable=True)
  for task in ("a","b"):
   s=m.queue_task(p,s,task,task+"1");s=m.mark_running(p,s,task,task+"1")
   s=accept(p,s,task,task+"1",[f"src/{task}/x"],[f"out:{task}"],[f"test:{task}"])
  self.assertNotIn("review",m.ready_task_ids(p,s))
  s=m.mark_integrated(p,s,"a","result:a:a1");s=m.mark_integrated(p,s,"b","result:b:b1")
  self.assertIn("review",m.ready_task_ids(p,s))

 def test_unintegrated_success_blocks_terminal(self):
  p=plan();s=m.initial_state(p,parallel_capable=True)
  s=m.queue_task(p,s,"a","a1");s=m.mark_running(p,s,"a","a1")
  s=accept(p,s,"a","a1",["src/a/x"],["out:a"],["test:a"])
  r=m.assess(p,s);self.assertFalse(r["terminal_allowed"]);self.assertIn("a:unintegrated_success",r["blockers"])

 def test_failed_worker_does_not_remove_unrelated_ready_task(self):
  p=plan();s=m.initial_state(p,parallel_capable=True)
  s=m.queue_task(p,s,"a","a1");s=m.mark_running(p,s,"a","a1")
  s=m.fail_attempt(p,s,"a","a1",terminal_status="failed")
  self.assertIn("b",m.ready_task_ids(p,s))
  self.assertIn("b",m.dispatch(p,s)["task_ids"])

 def test_retry_preserves_attempt_history(self):
  p=plan();s=m.initial_state(p,parallel_capable=True)
  s=m.queue_task(p,s,"a","a1");s=m.fail_attempt(p,s,"a","a1",terminal_status="stale")
  s=m.retry_task(p,s,"a");s=m.queue_task(p,s,"a","a2")
  self.assertEqual(s["tasks"][0]["attempt_ids"],["a1","a2"])

 def test_result_must_stay_in_portable_write_set(self):
  p=plan();s=m.initial_state(p,parallel_capable=True);s=m.queue_task(p,s,"a","a1");s=m.mark_running(p,s,"a","a1")
  with self.assertRaisesRegex(ValueError,"escape"):
   accept(p,s,"a","a1",["src/z/x"],["out:a"],["test:a"])

 def test_result_requires_expected_outputs_and_evidence(self):
  p=plan();s=m.initial_state(p,parallel_capable=True);s=m.queue_task(p,s,"a","a1");s=m.mark_running(p,s,"a","a1")
  with self.assertRaisesRegex(ValueError,"missing expected outputs"):
   accept(p,s,"a","a1",["src/a/x"],["wrong"],["test:a"])
  with self.assertRaisesRegex(ValueError,"missing expected evidence"):
   accept(p,s,"a","a1",["src/a/x"],["out:a"],["wrong"])

 def test_budgets_fail_closed(self):
  p=plan();s=m.initial_state(p,parallel_capable=True);s=m.queue_task(p,s,"a","a1");s=m.mark_running(p,s,"a","a1")
  with self.assertRaisesRegex(ValueError,"task budget"):
   accept(p,s,"a","a1",["src/a/x"],["out:a"],["test:a"],runtime=301)

 def test_nonfinite_and_boolean_numeric_inputs_rejected(self):
  for value in (True,float("nan"),float("inf"),0,-1):
   p=plan();p["tasks"][0]["max_runtime_seconds"]=value
   with self.assertRaises(ValueError):m.validate_plan(p)

 def test_duplicate_and_cyclic_tasks_rejected(self):
  p=plan();p["tasks"][1]["id"]="a"
  with self.assertRaisesRegex(ValueError,"duplicate"):m.validate_plan(p)
  p=plan();p["tasks"][0]["dependencies"]=["review"]
  with self.assertRaisesRegex(ValueError,"cyclic"):m.validate_plan(p)

 def test_authority_is_always_false_and_full_completion_requires_integration(self):
  p=plan();s=m.initial_state(p,parallel_capable=True)
  for task in ("a","b"):
   s=m.queue_task(p,s,task,task+"1");s=m.mark_running(p,s,task,task+"1")
   s=accept(p,s,task,task+"1",[f"src/{task}/x"],[f"out:{task}"],[f"test:{task}"])
   s=m.mark_integrated(p,s,task,f"result:{task}:{task}1")
  s=m.queue_task(p,s,"review","r1");s=m.mark_running(p,s,"review","r1")
  s=accept(p,s,"review","r1",[],["out:review"],["review:green"])
  self.assertFalse(m.assess(p,s)["complete"])
  s=m.mark_integrated(p,s,"review","result:review:r1");r=m.assess(p,s)
  self.assertTrue(r["complete"]);self.assertTrue(r["terminal_allowed"])
  for name in m.AUTHORITY_FIELDS:self.assertFalse(r[name])

if __name__=="__main__":unittest.main()
