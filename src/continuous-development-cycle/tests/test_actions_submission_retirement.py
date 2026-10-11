"""Anonymized real-Git administrative Actions quarantine; never a provider send."""
import copy
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import execution_lease_v2 as lease
import operation_intent as op
from git_lease_store import validate_coordination_transition
from test_submission_recovery import fixture, NOW, REV

WORKFLOW_BYTES=b'on: [workflow_dispatch]\npermissions:\n  contents: read\njobs:\n  pilot:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo anonymized-read-only-pilot\n'

def actions_fixture(candidate_sha='a'*40):
    record,old=fixture('not_submitted');guard=record['external_guard']
    binding=copy.deepcopy(guard['intent']['binding'])
    binding.update(backend='github-actions',mode='ordinary-unsigned-pilot',candidate_sha=candidate_sha)
    intent=op.prepare(binding,'original-pilot',record['source_ref'],'2026-10-04T17:00:00Z')
    receipt=op.verify_readback(intent,copy.deepcopy(intent),'git:'+'b'*40,intent['updated_at_utc'])
    intent=op.transition(intent,'submitting','2026-10-04T17:00:01Z',receipt=receipt)
    claim=guard['submission_claim'];claim.update(operation_key=intent['operation_key'],intent_digest=op._hash(intent),attempt_id=intent['attempt_id'])
    guard.update(intent=intent,operation_key=intent['operation_key'],intent_digest=op._hash(intent));record['submission_claims']=[copy.deepcopy(claim)]
    scope={'backend':'github-actions','mode':'ordinary-unsigned-pilot','method':'POST','workflow':'ordinary-unsigned-pilot.yml','target':'repos/example/project/actions/workflows/ordinary-unsigned-pilot.yml/dispatches','candidate_sha':binding['candidate_sha'],'read_only':True}
    decision={'action':'retire_actions_unknown_without_replay','operation_key':claim['operation_key'],'grant_id':claim['grant_id'],'owner_id':claim['owner_id'],'generation':claim['generation'],'scope':copy.deepcopy(scope),'at_utc':NOW}
    proof={'schema':'actions-unknown-retirement-proof/v1','lease_revision':REV,'lease_digest':op._hash(record),'original_lease_revision':REV,'guard_digest':op._hash(guard),'repository':record['repository'],'source_ref':record['source_ref'],'observed_at_utc':NOW,'scope':scope,'owner_decision':decision,'original_ui':{'closed_without_run':True,'final_run_clicked':False,'original_ci_submitted':False,'at_utc':'2026-10-04T17:00:03Z'},'transport':{'outcome':'UNKNOWN','cancellation_barrier':None,'dispatcher_birth':None,'no_in_flight':None},'runtime':copy.deepcopy(old['runtime']),'provider_observation':copy.deepcopy(old['provider_observation']),'evidence':{}}
    proof['provider_observation']['operation_key']=claim['operation_key']
    proof['physical_stop']={'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'executor_pid':1500001,'executor_birth':'11111','supervisor_pid':1500002,'supervisor_birth':'11112','absent':True,'invocation_id':old['runtime']['invocation_id'],'owner_id':claim['owner_id'],'generation':claim['generation'],'observed_at_utc':NOW}
    proof['provider_lookup']={'repository':record['repository'],'workflow':scope['workflow'],'candidate_sha':binding['candidate_sha'],'operation_key':claim['operation_key'],'grant_id':claim['grant_id'],'surfaces':['status','check_runs','actions'],'pagination_complete':True,'observed_at_utc':NOW,'evidence_refs':['sha256:'+'2'*64,'sha256:'+'3'*64,'sha256:'+'4'*64]}
    proof['workflow_definition']='sha256:'+hashlib.sha256(WORKFLOW_BYTES).hexdigest()
    for name in ['scope','owner_decision','original_ui','runtime','provider_observation','physical_stop','provider_lookup']:
        proof['evidence'][name]={'revision':REV,'ref':'refs/heads/cdc/actions-evidence','path':'evidence.json','pointer':'/'+name,'sha256':'sha256:'+'1'*64}
    proof['evidence']['workflow_definition']={'revision':candidate_sha,'ref':'refs/heads/main','path':'.github/workflows/'+scope['workflow'],'pointer':'/','sha256':proof['workflow_definition']}
    lease.validate(record);return record,proof

class Tests(unittest.TestCase):
    def module(self):
        m=importlib.import_module('submission_retirement')
        self.assertTrue(callable(getattr(m,'retire_actions_unknown_guard',None)), 'Canonical administrative Actions UNKNOWN quarantine is required; UI closure is not positive cancellation')
        return m

    def retire(self,old,proof):return self.module().retire_actions_unknown_guard(old,proof,'git:'+'5'*40,NOW)

    def test_unknown_preserved_without_manufactured_transport_terminal(self):
        old,proof=actions_fixture();new=self.retire(old,proof);entry=new['submission_retirements'][0]
        self.assertIsNone(new['external_guard']);self.assertEqual(entry['outcome'],'UNKNOWN');self.assertIs(entry['replay_forbidden'],True)
        self.assertEqual(entry['guard'],old['external_guard']);self.assertEqual(entry['original_release'],old['last_release'])
        self.assertEqual(entry['proof']['transport'],proof['transport'])
        for k in old.keys()-{'external_guard'}:self.assertEqual(new[k],old[k],k)

    def test_scope_identity_and_missing_evidence_rejected(self):
        old,proof=actions_fixture()
        edits=[('scope','mode','required-release'),('scope','backend','native_git'),('scope','method','PUT'),('scope','target','repos/other/project/actions/workflows/ordinary-unsigned-pilot.yml/dispatches'),('scope','candidate_sha','f'*40),('scope','read_only',False),('original_ui','final_run_clicked',True),('original_ui','original_ci_submitted',True),('runtime','quiescent',False),('runtime','pending_shared_writes',True),('runtime','invocation_id','another'),('provider_observation','lookup_complete',False),('owner_decision','action','cancelled_before_send'),('transport','cancellation_barrier','cancelled_before_send'),('transport','no_in_flight',False)]
        for section,key,value in edits:
            p=copy.deepcopy(proof);p[section][key]=value
            with self.subTest(section=section,key=key),self.assertRaises(ValueError):self.retire(old,p)
        for key in ['owner_decision','original_ui','runtime','provider_observation']:
            p=copy.deepcopy(proof);p['evidence'].pop(key)
            with self.subTest(missing=key),self.assertRaises(ValueError):self.retire(old,p)

    def test_provider_absence_never_becomes_positive_cancellation(self):
        from submission_recovery import resolve_released_guard
        old,proof=actions_fixture();_,positive=fixture('not_submitted')
        positive.update(lease_digest=op._hash(old),claim=old['external_guard']['submission_claim'])
        positive['provider_observation']['operation_key']=old['external_guard']['operation_key']
        positive['dispatch'].update(claim_digest=op._hash(positive['claim']),intent_digest=old['external_guard']['intent_digest'],target=proof['scope']['target'])
        with self.assertRaises(ValueError):resolve_released_guard(old,positive,'git:'+'8'*40,NOW)

    def test_attempt_ref_mode_backend_environment_disguises_never_rearm(self):
        old,proof=actions_fixture();new=self.retire(old,proof)
        for mode,backend in [('ordinary-unsigned-pilot','github-actions'),('COMPUTE_ONLY','codex_cloud_cli'),('SOURCE_RELEASE','native_git')]:
            binding=copy.deepcopy(old['external_guard']['intent']['binding']);binding.update(mode=mode,backend=backend,environment_id='changed')
            intent=op.prepare(binding,'new-disguised-attempt','refs/heads/new-ref','2026-10-04T17:00:00Z')
            receipt=op.verify_readback(intent,copy.deepcopy(intent),'git:'+'b'*40,intent['updated_at_utc']);intent=op.transition(intent,'submitting','2026-10-04T17:00:01Z',receipt=receipt)
            bad=copy.deepcopy(new);bad['external_guard']={'operation_key':intent['operation_key'],'intent':intent,'intent_digest':op._hash(intent),'intent_reference':'git:'+'b'*40,'submission_claim':None}
            with self.subTest(mode=mode,backend=backend),self.assertRaises(ValueError):lease.validate(bad)

    def test_raw_history_append_and_guard_clear_are_not_authenticated_authority(self):
        old,proof=actions_fixture();new=self.retire(old,proof)
        with self.assertRaisesRegex(ValueError,'authenticated|verified'):validate_coordination_transition(old,new,expected_revision=REV)
        bad=copy.deepcopy(old);bad['external_guard']=None
        with self.assertRaises(ValueError):validate_coordination_transition(old,bad,expected_revision=REV)

    def test_same_sha_fresh_native_compute_only_source_write_is_not_globally_blocked(self):
        old,proof=actions_fixture();new=self.retire(old,proof)
        # Exercise the existing fresh managed product_write gate. No external
        # operation is armed; this is source correction, not a disguised send.
        from unittest.mock import patch
        invocation={'invocation_id':'fresh-native-correction','automation_id':None,'conversation_id':None,'execution_surface':'managed','started_at_utc':NOW}
        # Only the runtime-capability issuer is isolated, as in the existing
        # lease unit fixture; canonical acquisition/write/history checks run.
        with patch.object(lease.terminal_capability_api,'validate_verified',return_value={}):
            owned=lease.acquire(new,'33333333-3333-4333-8333-333333333333','2026-10-04T17:00:06Z',invocation=invocation,terminal_capability=object())
        lease.check_record(owned,owned['owner_id'],2,owned['invocation']['invocation_id'],'2026-10-04T17:00:07Z',action='product_write')
        self.assertIsNone(owned['external_guard']);self.assertEqual(owned['submission_retirements'][0]['outcome'],'UNKNOWN')

    def test_local_stop_and_complete_provider_lookup_are_required_distinct_from_transport(self):
        old,proof=actions_fixture()
        for field in ['physical_stop','provider_lookup']:
            p=copy.deepcopy(proof);p[field]=None
            with self.subTest(field=field),self.assertRaises(ValueError):self.retire(old,p)

    def test_missing_original_birth_or_incomplete_provider_surfaces_cannot_be_retired(self):
        old,proof=actions_fixture()
        self.assertIn('physical_stop',proof,'Original executor birth-bound local stop proof required, separate from missing dispatcher proof')
        for section,key,val in [('physical_stop','executor_birth',None),('physical_stop','supervisor_birth',None),('physical_stop','absent',False),('provider_lookup','surfaces',['actions']),('provider_lookup','pagination_complete',False)]:
            p=copy.deepcopy(proof);p[section][key]=val
            with self.subTest(section=section,key=key),self.assertRaises(ValueError):self.retire(old,p)

    def test_complete_original_stop_and_lookup_are_supported_without_cancellation_barrier(self):
        old,proof=actions_fixture()
        try:new=self.module().retire_actions_unknown_guard(old,proof,'git:'+'5'*40,NOW)
        except ValueError as e:self.fail('Complete original physical-stop/provider-lookup proof must be supported without manufacturing a transport barrier: '+str(e))
        self.assertEqual(new['submission_retirements'][0]['outcome'],'UNKNOWN')

class GitTests(unittest.TestCase):
    module=Tests.module
    retire=Tests.retire
    def setUp(self):
        from test_submission_recovery import GitTests as GitFixture
        GitFixture.setUp(self)

    def authenticated(self,workflow_bytes=WORKFLOW_BYTES):
        store=self.stores[0];repo=store.repo
        def git(*args):return subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True,text=True).stdout.strip()
        git('checkout','--orphan','main');path=repo/'.github/workflows/ordinary-unsigned-pilot.yml';path.parent.mkdir(parents=True);path.write_bytes(workflow_bytes)
        git('add','.github');git('-c','user.name=test','-c','user.email=test@example.invalid','commit','-m','Anonymized original pilot source');candidate=git('rev-parse','HEAD');git('push','origin','HEAD:refs/heads/main')
        old,proof=actions_fixture(candidate);proof['workflow_definition']='sha256:'+hashlib.sha256(workflow_bytes).hexdigest();proof['evidence']['workflow_definition']['sha256']=proof['workflow_definition']
        revision=store.compare_and_swap(None,old);proof.update(lease_revision=revision,original_lease_revision=revision)
        git('checkout','-B','evidence',revision)
        body={k:proof[k] for k in proof['evidence'] if k!='workflow_definition'};raw=(json.dumps(body,sort_keys=True,indent=2)+'\n').encode();(repo/'evidence.json').write_bytes(raw)
        (repo/'checkpoint.json').write_text('{"original":"preserved"}\n');git('add','evidence.json','checkpoint.json');git('-c','user.name=test','-c','user.email=test@example.invalid','commit','-m','Authenticated original-channel evidence')
        commit=git('rev-parse','HEAD');git('push','origin','HEAD:refs/heads/cdc/actions-evidence')
        git('push','origin','HEAD:'+store.ref);proof['lease_revision']=commit
        pins={k:dict(revision=commit,ref='refs/heads/cdc/actions-evidence',path='evidence.json',pointer='/'+k,sha256='sha256:'+hashlib.sha256(raw).hexdigest()) for k in body}
        pins['workflow_definition']=proof['evidence']['workflow_definition']
        proof['evidence']=copy.deepcopy(pins)
        capability=self.module().authenticate_actions_retirement(store,proof,pins,NOW)
        return old,proof,store,capability

    def test_real_git_authenticated_quarantine_cas_and_race(self):
        old,proof,store,cap=self.authenticated();m=self.module()
        result=m.retire_actions_unknown_cas(store,proof['lease_revision'],proof,'git:'+'5'*40,NOW,evidence_capability=cap)
        self.assertIs(result['authorizes_submission'],False);self.assertIs(result['authorizes_release'],False)
        rev,new=self.stores[1].read();self.assertEqual(new,result['record']);self.assertEqual(len(new['submission_retirements']),1)
        neighbor=subprocess.check_output(['git','-C',str(store.repo),'show',rev+':checkpoint.json']).decode();self.assertEqual(neighbor,'{"original":"preserved"}\n')
        with self.assertRaises(ValueError):self.stores[1].compare_and_swap(proof['lease_revision'],new,retirement_capability=cap)
        bad=copy.deepcopy(new);bad['submission_retirements']=[]
        with self.assertRaises(ValueError):store.compare_and_swap(rev,bad)

    def test_native_evidence_missing_substitution_or_caller_bool_cannot_write(self):
        old,proof,store,cap=self.authenticated();m=self.module()
        for alteration in [dict(runtime=dict(proof['runtime'],quiescent=False)),dict(evidence={}),dict(guard_digest='sha256:'+'0'*64)]:
            p=copy.deepcopy(proof);p.update(alteration)
            with self.subTest(alteration=list(alteration)),self.assertRaises(ValueError):m.authenticate_actions_retirement(store,p,proof['evidence'],NOW)
        p=copy.deepcopy(proof);p['runtime']['reference']='git:'+'8'*40
        with self.assertRaisesRegex(ValueError,'authenticated'):m.authenticate_actions_retirement(store,p,proof['evidence'],NOW)
        p=copy.deepcopy(proof);p['evidence']['original_ui']['sha256']='sha256:'+'0'*64
        with self.assertRaisesRegex(ValueError,'bytes'):m.authenticate_actions_retirement(store,p,p['evidence'],NOW)
        with self.assertRaises(ValueError):m.retire_actions_unknown_cas(store,proof['lease_revision'],proof,'git:'+'5'*40,NOW,evidence_capability=True)
        self.assertEqual(store.read()[1],old)

    def test_actual_write_permission_workflow_is_outside_unsigned_read_only_scope(self):
        with self.assertRaisesRegex(ValueError,'read.only|permission'):
            self.authenticated(WORKFLOW_BYTES.replace(b'contents: read',b'contents: write'))

    def test_lost_reply_is_same_entry_readback_not_cas_or_submission_replay(self):
        old,proof,store,cap=self.authenticated();original=store.compare_and_swap;calls=[]
        def lost(expected,record,**kw):calls.append(expected);original(expected,record,**kw);raise OSError('lost reply')
        store.compare_and_swap=lost;m=self.module()
        with self.assertRaises(OSError):m.retire_actions_unknown_cas(store,proof['lease_revision'],proof,'git:'+'5'*40,NOW,evidence_capability=cap)
        result=m.observe_actions_retirement(store,proof,'git:'+'5'*40)
        self.assertEqual(result['outcome'],'UNKNOWN');self.assertEqual(len(calls),1)
        with self.assertRaises(ValueError):m.retire_actions_unknown_cas(store,proof['lease_revision'],proof,'git:'+'5'*40,NOW,evidence_capability=cap)
        self.assertEqual(len(calls),1)
