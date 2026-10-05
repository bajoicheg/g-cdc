import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import codex_cloud_cli as cloud

KEY='sha256:'+'a'*64
TASK='task_e_'+'b'*32
REQUEST={'schema':'codex-cloud-cli-request/v1','operation_key':KEY,'attempt_id':'compute-a1','repository':'test/project','candidate_sha':'c'*40,'environment_id':'d'*32,'environment_label':'test-env','source_branch':'cdc/candidate','checks':[{'id':'suite','argv':['python','-B','-m','unittest','discover'],'minimum_test_count':4}]}

class Runner:
    def __init__(self):self.calls=[];self.exec_error=False;self.pages=[{'tasks':[],'cursor':None}]
    def __call__(self,argv,**kwargs):
        self.calls.append(argv)
        if argv[2]=='exec':
            if self.exec_error:raise subprocess.TimeoutExpired(argv,1)
            return subprocess.CompletedProcess(argv,0,'https://chatgpt.com/codex/tasks/'+TASK,'')
        if argv[2]=='status':return subprocess.CompletedProcess(argv,0,'[READY] Task','')
        return subprocess.CompletedProcess(argv,0,json.dumps(self.pages.pop(0)),'')

class CloudTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.runner=Runner();self.adapter=cloud.CodexCloudCLI(self.tmp.name,runner=self.runner)
    def submit(self):return self.adapter.submit(copy.deepcopy(REQUEST),launch_authorized=lambda:None)
    def report(self):
        return {'schema':'codex-cloud-cli-report/v1','task_id':TASK,**{k:REQUEST[k] for k in ('operation_key','attempt_id','repository','environment_id','environment_label')},'head_before':REQUEST['candidate_sha'],'head_after':REQUEST['candidate_sha'],'clean_before':True,'clean_after':True,'checks':[{'id':'suite','argv':REQUEST['checks'][0]['argv'],'exit_code':0,'test_count':4,'log_sha256':'e'*64}]}
    def task(self,**overrides):
        return {'id':TASK,'title':'CDC '+KEY+' compute-a1','environment_id':None,'environment_label':'test-env','status':'ready',**overrides}
    def test_submit_once_across_reconnect(self):
        self.submit();cloud.CodexCloudCLI(self.tmp.name,runner=self.runner).submit(REQUEST,launch_authorized=lambda:self.fail('repeated authorization'))
        self.assertEqual(sum(a[2]=='exec' for a in self.runner.calls),1)
        self.assertEqual(self.runner.calls[0][1:9],['cloud','exec','--env',REQUEST['environment_id'],'--branch','cdc/candidate','--attempts','1'])
    def test_missing_live_callback_never_dispatches(self):
        with self.assertRaises(ValueError):self.adapter.submit(REQUEST,launch_authorized=True)
        self.assertFalse(self.runner.calls)
    def test_conflicting_attempt_context_rejected(self):
        self.submit();other=copy.deepcopy(REQUEST);other['candidate_sha']='f'*40
        with self.assertRaises(ValueError):self.adapter.submit(other,launch_authorized=lambda:None)
    def test_lost_reply_remains_unknown_and_never_restarts(self):
        self.runner.exec_error=True;self.assertEqual(self.submit()['state'],'unknown')
        self.runner.pages=[{'tasks':[],'cursor':None}]
        self.adapter.observe(KEY);self.adapter.submit(REQUEST,launch_authorized=lambda:self.fail('repeat'))
        self.assertEqual(sum(a[2]=='exec' for a in self.runner.calls),1)
    def test_pagination_locally_filters_environment_and_recovers_exact_marker(self):
        self.runner.exec_error=True;self.submit()
        self.runner.pages=[{'tasks':[self.task(id='task_e_'+'9'*32,environment_label='other')],'cursor':'page2'},{'tasks':[self.task()],'cursor':None}]
        observed=self.adapter.observe(KEY)
        self.assertEqual(observed['task_id'],TASK);self.assertEqual(observed['state'],'waiting_report')
        self.assertIn('--cursor',self.runner.calls[-2])
    def test_repeated_cursor_stays_unknown(self):
        self.runner.exec_error=True;self.submit()
        self.runner.pages=[{'tasks':[self.task()],'cursor':'loop'},{'tasks':[],'cursor':'loop'}]
        self.assertEqual(self.adapter.observe(KEY)['state'],'unknown')
    def test_ambiguous_marker_stays_unknown(self):
        self.runner.exec_error=True;self.submit();self.runner.pages=[{'tasks':[self.task(),self.task(id='task_e_'+'f'*32)],'cursor':None}]
        self.assertEqual(self.adapter.observe(KEY)['state'],'unknown')
    def test_ready_without_report_is_not_pass(self):
        self.submit();observed=self.adapter.observe(KEY)
        self.assertEqual(observed['state'],'waiting_report');self.assertFalse(observed['validation_passed'])
    def test_corrupt_journal_cannot_claim_success_without_report(self):
        self.submit();path=self.adapter._path(KEY);state=json.loads(path.read_text())
        state.update(state='succeeded',validation_passed=True);path.write_text(json.dumps(state))
        with self.assertRaises(ValueError):self.adapter.observe(KEY)
        self.assertEqual(sum(a[2]=='exec' for a in self.runner.calls),1)
    def test_corrupt_persisted_report_cannot_pass_after_reconnect(self):
        self.submit();self.adapter.observe(KEY);self.adapter.ingest_report(KEY,self.report(),'provider:report/1')
        path=self.adapter._path(KEY);original=json.loads(path.read_text())
        for update_digest in (False,True):
            state=copy.deepcopy(original);state['report']['head_after']='f'*40
            if update_digest:state['report_digest']=cloud._digest(state['report'])
            path.write_text(json.dumps(state))
            with self.assertRaises(ValueError):cloud.CodexCloudCLI(self.tmp.name,runner=self.runner).observe(KEY)
    def test_exact_report_proves_success(self):
        self.submit();self.adapter.observe(KEY)
        result=self.adapter.ingest_report(KEY,self.report(),'provider:report/1')
        self.assertEqual(result['state'],'succeeded');self.assertTrue(result['validation_passed'])
    def test_failed_check_report_proves_failure(self):
        self.submit();self.adapter.observe(KEY);report=self.report();report['checks'][0]['exit_code']=1
        self.assertEqual(self.adapter.ingest_report(KEY,report,'provider:report/1')['state'],'failed')
    def test_report_mismatches_never_pass(self):
        self.submit();self.adapter.observe(KEY)
        changes=[('head_after','f'*40),('task_id','task_e_'+'f'*32),('environment_id','f'*32),('clean_before',False),('clean_after',1),('attempt_id','other'),('repository','other/repo')]
        for field,value in changes:
            with self.subTest(field=field):
                report=self.report();report[field]=value
                with self.assertRaises(ValueError):self.adapter.ingest_report(KEY,report,'provider:report/1')
        for change in ({'argv':['echo','pass']},{'log_sha256':'bad'},{'test_count':3},{'exit_code':False}):
            report=self.report();report['checks'][0].update(change)
            with self.assertRaises(ValueError):self.adapter.ingest_report(KEY,report,'provider:report/1')
    def test_report_requires_observed_provider_ready(self):
        self.submit()
        with self.assertRaises(ValueError):self.adapter.ingest_report(KEY,self.report(),'provider:report/1')
    def test_exact_report_replay_is_idempotent_but_changed_report_rejected(self):
        self.submit();self.adapter.observe(KEY);report=self.report();self.adapter.ingest_report(KEY,report,'provider:report/1')
        self.adapter.ingest_report(KEY,report,'provider:report/1');report['checks'][0]['exit_code']=1
        with self.assertRaises(ValueError):self.adapter.ingest_report(KEY,report,'provider:report/2')

if __name__=='__main__':unittest.main()
