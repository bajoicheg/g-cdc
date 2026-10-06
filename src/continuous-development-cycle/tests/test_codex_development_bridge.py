import copy, hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from codex_development_bridge import admit_development, build_development_handoff, ContractError
from test_codex_cloud_development import request
import managed_executor_handoff as handoff

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.r=request()
        self.patch=b'diff --git a/docs/result.md b/docs/result.md\nnew file mode 100644\n--- /dev/null\n+++ b/docs/result.md\n@@ -0,0 +1 @@\n+result\n';self.file=self.root/'result.diff';self.file.write_bytes(self.patch)
        self.exported={'task_id':'task_exact','provider_attempt':1,'base_sha':self.r['base_sha'],'artifact_ref':{'path':str(self.file),'sha256':hashlib.sha256(self.patch).hexdigest(),'format':'unified_diff'}}
        self.report={'schema':'codex-cloud-development-report/v1','task_id':'task_exact','provider_attempt':1,'operation_key':self.r['operation_key'],'attempt_id':self.r['attempt_id'],'repository':self.r['repository'],'environment_id':self.r['environment_id'],'base_sha':self.r['base_sha'],'head_before':self.r['base_sha'],'changed_paths':['docs/result.md'],'checks':[{'id':'layout','argv':['python','-B','layout.py'],'exit_code':0,'test_count':None,'log_sha256':'d'*64}],'evidence_refs':['logs:actual']}
        self.context={'pool_id':'pool','change_id':'change','task_id':'writer','attempt_id':'dev-a1','parent_invocation_id':'parent','executor_id':'writer-owner','assigned_branch':'cdc/development','publication_repository':'org/repo','publication_remote_id':'sha256:'+'e'*64}
    def tearDown(self):self.tmp.cleanup()
    def build(self):return build_development_handoff(self.r,self.exported,self.report,context=self.context,evidence_root=self.root)
    def test_actual_patch_yields_existing_handoff_without_publication_authority(self):
        h=self.build();self.assertEqual(h['schema'],'managed-executor-handoff/v1');self.assertEqual(h['artifact_ref']['path'],'result.diff');self.assertEqual(handoff.resolve_artifact(h,self.root),self.patch)
        p=handoff.publication_plan(h,self.root)
        for field in handoff.AUTHORITY_FIELDS:self.assertFalse(p[field])
    def test_ready_missing_log_is_not_pass(self):
        del self.report['checks'][0]['log_sha256']
        with self.assertRaises(ContractError):self.build()
    def test_observed_worker_base_mismatch_rejected(self):
        self.report['head_before']='f'*40
        with self.assertRaises(ContractError):self.build()
    def test_artifact_hash_mismatch_rejected(self):
        self.file.write_bytes(self.patch+b'corrupt')
        with self.assertRaises(ContractError):self.build()
    def test_patch_scope_escape_rejected(self):
        self.patch=self.patch.replace(b'docs/result.md',b'outside.md');self.file.write_bytes(self.patch);self.exported['artifact_ref']['sha256']=hashlib.sha256(self.patch).hexdigest()
        with self.assertRaises(ContractError):self.build()
    def test_report_wrong_task_or_attempt_rejected(self):
        for key,value in [('task_id','task_other'),('provider_attempt',2),('operation_key','sha256:'+'f'*64)]:
            old=self.report[key];self.report[key]=value
            with self.assertRaises(ContractError):self.build()
            self.report[key]=old
    def test_platform_not_run_check_cannot_be_promoted(self):
        self.report['checks'][0].update(exit_code=None,test_count=None,log_sha256=None)
        with self.assertRaises(ContractError):self.build()
    def test_worker_boolean_is_not_admission_authority(self):
        with self.assertRaises(ContractError):admit_development(self.r,capability_receipt={'qualified':True},admission={'authorized':True})
    def admission_fixture(self):
        import budget, execution_lease_v2 as lease, execution_lease as legacy, managed_executor_pool as pool
        from test_managed_executor_pool import plan
        at='2026-01-01T10:00:00Z';owner='11111111-1111-4111-8111-111111111111'
        # Synthetic validator input only, never a runtime-issued capability.
        lr=lease.initialize('org/repo','refs/heads/main');lr.update(owner_id=owner,generation=1,acquired_at_utc=at,heartbeat_at_utc=at,expires_at_utc='2026-01-01T10:20:00Z',invocation={'invocation_id':'fixture','automation_id':None,'conversation_id':None,'execution_surface':'managed','started_at_utc':at},finalization={'state':'active','pending_shared_writes':False,'checkpoint_ref':None,'external_reconciliation':'pending','completion_reason':None,'updated_at_utc':at,'failure':None})
        policy={'task_limits':{'compute_starts':1},'wake_limits':{'compute_starts':1},'max_parallel_agents':1,'checkpoint_reserve':{'tokens':0,'tool_calls':0},'provider_max_age_seconds':60,'actions_budget':'exhausted'}
        ledger=budget.new_ledger('task','wake',policy)
        event={'type':'reserve','event_id':'reserve1','task_id':'task','wake_id':'wake','at_utc':at,'operation_key':self.r['operation_key'],'attempt_id':'dev-a1','kind':'compute_start','scope':'fixture/env','recovery_ref':None,'cost':{'tool_calls':1,'tokens':None,'elapsed_seconds':None}}
        ledger=budget.apply_event(ledger,event)
        p=plan(self.r['base_sha']);p['tasks']=p['tasks'][:1];p['max_parallel']=1;p['tasks'][0].update(branch='cdc/development',write_paths=['docs/result.md'])
        state=pool.initial_state(p,parallel_capable=False)
        cap={'schema':'cdc-codex-controller-capabilities/v1','qualified':True,'checks':{name:{'status':'passed','evidence_refs':['fixture:validator-only']} for name in ['git_native','coordination_cas','submit','observe','diff_export','validation_report','provider_quiescence']}}
        a={'lease_record':lr,'owner_id':owner,'generation':1,'invocation_id':'fixture','at_utc':at,'ledger':ledger,'reservation':event,'pool_plan':p,'pool_state':state,'task_id':'a','evidence_refs':[self.r['budget_ref'],'fixture:trusted-parent-snapshot']}
        return cap,a
    def test_existing_reserved_budget_and_free_writer_validate(self):
        cap,a=self.admission_fixture()
        self.assertEqual(admit_development(self.r,capability_receipt=cap,admission=a),self.r)
    def test_budget_denial_prevents_dispatch(self):
        cap,a=self.admission_fixture();a['ledger']['events']=[]
        with self.assertRaises(ContractError):admit_development(self.r,capability_receipt=cap,admission=a)
    def test_unknown_retains_reservation(self):
        import budget
        cap,a=self.admission_fixture();a['ledger']=budget.apply_event(a['ledger'],{'type':'outcome','event_id':'unknown1','task_id':'task','wake_id':'wake','at_utc':a['at_utc'],'reservation_id':'reserve1','status':'unknown','usage':{'tokens':None,'elapsed_seconds':None},'failure':None})
        before=copy.deepcopy(a['ledger'])
        with self.assertRaises(ContractError):admit_development(self.r,capability_receipt=cap,admission=a)
        self.assertEqual(a['ledger'],before);self.assertEqual(budget.summarize(a['ledger'])['task']['compute_starts'],1)
    def test_lease_loss_prevents_admission(self):
        cap,a=self.admission_fixture();a['owner_id']='22222222-2222-4222-8222-222222222222'
        with self.assertRaises(ContractError):admit_development(self.r,capability_receipt=cap,admission=a)
    def test_source_branch_drift_prevents_admission(self):
        cap,a=self.admission_fixture();a['pool_plan']['base_sha']='f'*40
        with self.assertRaises(ContractError):admit_development(self.r,capability_receipt=cap,admission=a)

if __name__=='__main__':unittest.main()

