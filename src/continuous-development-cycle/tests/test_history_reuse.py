"""Real Git faults and work counts for process-local immutable history reuse."""
import copy,json,os,pathlib,subprocess,sys,tempfile,unittest
from unittest.mock import patch
SCRIPTS=pathlib.Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
from git_document_store import GitDocumentStore
from git_remote_identity import remote_identity
import unknown_recovery as native

class HistoryReuseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=pathlib.Path(self.temp.name);self.repo=self.root/'client';self.remote=self.root/'remote.git'
        self.git('init','--bare',str(self.remote),cwd=self.root);self.git('init',str(self.repo),cwd=self.root)
        self.git('remote','add','origin',str(self.remote))
        self.store=GitDocumentStore(self.repo,'origin','refs/heads/cdc/history-reuse',remote_identity(self.repo,'origin'))
        self.revisions=[];revision=None
        for i in range(3):
            revision=self.store.compare_and_swap(revision,{'value':{'number':i,'nested':['original']}})
            self.revisions.append(revision)
    def git(self,*args,cwd=None,input_text=None):
        p=subprocess.run(['git','-C',str(cwd or self.repo),*args],input=input_text,text=True,capture_output=True,check=True)
        return p.stdout.strip()
    def test_same_head_does_not_decode_verified_ancestors_again(self):
        with patch.object(self.store,'_read_document_object',wraps=self.store._read_document_object) as read:
            first=native._history(self.store);self.assertGreater(read.call_count,0)
            read.reset_mock();second=native._history(self.store)
            self.assertEqual(first,second);self.assertEqual(read.call_count,0)
    def test_new_head_only_decodes_the_unverified_suffix(self):
        old=native._history(self.store)
        revision=self.store.compare_and_swap(self.revisions[-1],{'value':{'number':3,'nested':['new']}})
        with patch.object(self.store,'_read_document_object',wraps=self.store._read_document_object) as read:
            result=native._history(self.store)
        self.assertEqual(result[:-1],old);self.assertEqual(result[-1][0],revision)
        self.assertLessEqual(read.call_count,1)
        self.assertFalse(any(call.args[0] in self.revisions for call in read.call_args_list))
    def test_returned_nested_documents_cannot_poison_reuse(self):
        expected=native._history(self.store)
        changed=native._history(self.store);changed[0][1]['value']['nested'].append('caller change')
        changed.clear();self.assertEqual(native._history(self.store),expected)
    def test_warm_reuse_cannot_hide_changed_endpoint(self):
        native._history(self.store)
        other=self.root/'other.git';self.git('init','--bare',str(other),cwd=self.root)
        self.git('remote','set-url','origin',str(other))
        with self.assertRaises(ValueError):native._history(self.store)
    def test_warm_reuse_cannot_hide_shallow_history(self):
        native._history(self.store)
        (self.repo/'.git/shallow').write_text(self.revisions[0]+'\n')
        with self.assertRaises(ValueError):native._history(self.store)
    def test_actual_remote_rewind_cannot_reuse_a_prior_snapshot(self):
        native._history(self.store)
        self.git('push','--force','origin',self.revisions[0]+':'+self.store.ref)
        with self.assertRaises(ValueError):native._history(self.store)
    def test_other_ref_never_returns_the_first_channel_documents(self):
        native._history(self.store)
        other=GitDocumentStore(self.repo,'origin','refs/heads/cdc/history-other',self.store.store_id)
        revision=other.compare_and_swap(None,{'other-channel':True})
        self.assertEqual(native._history(other),[(revision,{'other-channel':True})])
    def test_ref_movement_is_still_checked_at_end_of_warm_reuse(self):
        native._history(self.store);read=self.store.read;calls=[]
        def moving():
            calls.append(True)
            if len(calls)==2:
                self.store.compare_and_swap(self.revisions[-1],{'value':{'number':4,'nested':['moved']}})
            return read()
        with patch.object(self.store,'read',side_effect=moving):
            with self.assertRaises(ValueError):native._history(self.store)

class BatchDispositionTests(unittest.TestCase):
    def fixture(self):
        from test_native_unknown_recovery import IntakeTests
        fixture=IntakeTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        proof=fixture.proof()
        native.retire_prelaunch_intake_cas(fixture.store,fixture.rev,'task-one',proof,at='2026-10-13T12:00:00Z')
        return fixture
    def test_batch_uses_one_fresh_history_and_returns_detached_structural_entries(self):
        fixture=self.fixture();revision,document=fixture.store.read();row=document['tasks']['task-one']
        function=getattr(native,'validate_prelaunch_dispositions',None)
        self.assertIsNotNone(function,'batch native disposition validation is required')
        with patch.object(native,'_history',wraps=native._history) as history:
            entries=function(fixture.store,revision,{'task-one':row})
            self.assertEqual(history.call_count,1)
        self.assertEqual(entries['task-one'],row['result']['administrative_disposition'])
        entries['task-one']['original_row']['task']['goal']='caller mutation'
        self.assertEqual(function(fixture.store,revision,{'task-one':row})['task-one'],row['result']['administrative_disposition'])
    def test_batch_denies_stale_head_and_substituted_rows(self):
        fixture=self.fixture();revision,document=fixture.store.read();row=document['tasks']['task-one']
        function=getattr(native,'validate_prelaunch_dispositions',None)
        self.assertIsNotNone(function,'batch native disposition validation is required')
        with self.assertRaises(ValueError):function(fixture.store,fixture.rev,{'task-one':row})
        changed=copy.deepcopy(row);changed['task']['goal']='substituted'
        with self.assertRaises(ValueError):function(fixture.store,revision,{'task-one':changed})

if __name__=='__main__':unittest.main()
