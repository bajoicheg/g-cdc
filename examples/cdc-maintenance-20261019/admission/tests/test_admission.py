"""Hosted-only tests; ADMISSION_VARIANT selects frozen baseline/candidate modules."""
import concurrent.futures
import copy
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
VARIANT = os.environ.get('ADMISSION_VARIANT', 'candidate')
def load(name):
    spec = importlib.util.spec_from_file_location('packet_' + name, ROOT / VARIANT / (name + '.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module
quota = load('quota'); cachemod = load('immutable_history_cache')
FACTS = json.loads((ROOT / 'evidence/reset-facts.json').read_text())

def snapshot():
    return copy.deepcopy(FACTS['previous_accepted_snapshot'])

class OldExpectedRed(unittest.TestCase):
    def test_oversized_cache_does_not_materialize_snapshot(self):
        cache = cachemod._HistoryCache(max_decoded_bytes=1024)
        value = {'chain': [['a']], 'documents': [['a', {'huge': 'x' * 2048}]]}
        original = cache._encode
        def guard(item):
            self.assertIsNot(item, value, 'eager full snapshot serialization')
            return original(item)
        with patch.object(cache, '_encode', side_effect=guard):
            cache.put({'channel': 'a'}, value)
        self.assertIsNone(cache.get({'channel': 'a'}))

    def test_recorded_correction_is_conservative(self):
        with tempfile.TemporaryDirectory() as temp:
            book = quota.QuotaBook(Path(temp) / 'q.sqlite')
            old = snapshot(); book.observe('one', old, now=old['observed_at'])
            new = copy.deepcopy(FACTS['current_official_normalized_snapshot'])
            try:
                decision = book.observe('two', new, now=new['observed_at'])
            except ValueError:
                self.fail('bounded conservative correction denied')
            self.assertEqual(decision['mode'], 'ALLOW')
            stored = book.read('kimi', old['account_id'])
            self.assertEqual(stored['windows'][0]['resets_at'], old['windows'][0]['resets_at'])
            self.assertEqual(stored['windows'][0]['used_percent'], 0.2)

class QuotaSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'q.sqlite'; self.book = quota.QuotaBook(self.path)
        self.old = snapshot(); self.book.observe('one', self.old, now=self.old['observed_at'])
    def rows(self):
        with sqlite3.connect(self.path) as db:
            return [db.execute('SELECT rowid,* FROM ' + table + ' ORDER BY rowid').fetchall()
                    for table in ('accounts', 'history')]
    def next(self, delta=0, used=0.2, seconds=400):
        value=copy.deepcopy(self.old); value['observed_at']+=seconds
        value['windows'][0]['resets_at']+=delta
        value['windows'][0]['used_percent']=used
        return value
    def observe(self,value):
        return self.book.observe('two',value,now=value['observed_at'])
    def denied(self,value,now=None):
        before=self.rows()
        with self.assertRaises(ValueError):
            self.book.observe('two',value,now=value['observed_at'] if now is None else now)
        self.assertEqual(self.rows(),before)
    def test_original_anchor_and_hold_never_roll(self):
        anchor=self.old['windows'][0]['resets_at']
        for i,delta in enumerate([-1,0,1,-1,1,0]*8):
            value=self.next(delta,used=i+1,seconds=400+i)
            self.observe(value)
            stored=self.book.read('kimi',self.old['account_id'])
            self.assertEqual(stored['_local_continuity_v1']['anchors']['limit_5h'],anchor)
            self.assertEqual(stored['windows'][0]['resets_at'],anchor+(i>=2))
            self.assertEqual(stored['_local_continuity_v1']['raw'],value)
        self.denied(self.next(2,used=50,seconds=500))
        self.denied(self.next(-2,used=50,seconds=500))
    def test_within_bound_after_expiry_cannot_mint_credit_or_reanchor(self):
        anchor=self.old['windows'][0]['resets_at']
        self.observe(self.next(0,10))
        value=self.next(1,0);value['observed_at']=anchor+0.5
        self.denied(value)
        value['windows'][0]['used_percent']=10
        self.denied(value)
        value['observed_at']=anchor-0.5
        self.observe(value)
        stored=self.book.read('kimi',self.old['account_id'])
        self.assertEqual(stored['_local_continuity_v1']['anchors']['limit_5h'],anchor)
        self.assertEqual(stored['windows'][0]['resets_at'],anchor+1)
        value['windows'][0]['resets_at']=anchor+2
        self.denied(value)
    def test_decision_never_exceeds_raw_or_cumulative_remaining(self):
        last=100
        for i,delta in enumerate([-1,1,0,-1,1]):
            value=self.next(delta,used=10*i,seconds=400+i)
            untouched=copy.deepcopy(value)
            raw=quota.assess(value,now=value['observed_at'])
            decision=self.observe(value)
            self.assertEqual(value,untouched)
            self.assertLessEqual(decision['remaining_percent'],raw['remaining_percent'])
            self.assertLessEqual(decision['remaining_percent'],last)
            last=decision['remaining_percent']
    def test_expired_raw_cannot_be_hidden_by_later_effective_hold(self):
        anchor=self.old['windows'][0]['resets_at']
        self.observe(self.next(1,10))
        value=self.next(-1,10);value['observed_at']=anchor
        self.denied(value)
    def test_concurrent_corrections_preserve_rowids_and_highwater(self):
        before=self.rows(); new=self.next(-1)
        def observe(_):
            return quota.QuotaBook(self.path).observe('two',new,now=new['observed_at'])
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            decisions=list(pool.map(observe,range(8)))
        after=self.rows()
        self.assertEqual(after[0][0][0],before[0][0][0])
        self.assertEqual(after[1][:len(before[1])],before[1])
        self.assertEqual(len(after[1]),len(before[1])+8)
        self.assertTrue(all(d['remaining_percent']<=99.8 for d in decisions))
    def test_old_copy_and_usage_rollback_denied(self):
        self.observe(self.next(-1,10))
        self.denied(self.old,now=self.old['observed_at']+400)
        self.denied(self.next(0,1,401))
        self.denied(self.next(1,1,401))
    def test_all_original_denials(self):
        changes=[lambda v:v.update(paid_fallback=True),
                 lambda v:v.update(ordinary_usage_allowed=False),
                 lambda v:v.update(provider='other'),
                 lambda v:v.update(observed_at=v['observed_at']-1000),
                 lambda v:v['required_windows'].pop(),
                 lambda v:v['windows'][0].update(name='wrong'),
                 lambda v:v['windows'][0].update(window_seconds=17999),
                 lambda v:v['windows'][0].update(resets_at=1792382891),
                 lambda v:v['windows'][0].update(resets_at=1792382895),
                 lambda v:v['windows'][0].update(used_percent=float('nan')),
                 lambda v:v['windows'][0].pop('resets_at'),
                 lambda v:v.update(_local_continuity_v1={})]
        for change in changes:
            value=self.next();change(value);self.denied(value,now=self.old['observed_at']+400)
        self.denied(self.next(),now=self.old['observed_at']+491)
        for used,mode in [(95,'STOP'),(86,'PAUSE'),(81,'ROTATE'),(100,'STOP')]:
            # Separate books avoid intentionally denied usage rollback.
            with tempfile.TemporaryDirectory() as temp:
                book=quota.QuotaBook(Path(temp)/'q.sqlite')
                book.observe('one',self.old,now=self.old['observed_at'])
                value=self.next(-1,used)
                self.assertEqual(book.observe('two',value,now=value['observed_at'])['mode'],mode)
    def test_burn_rate_survives_later_hold(self):
        first=self.observe(self.next(0,10,400))
        second=self.observe(self.next(1,10,401))
        self.assertEqual(first['mode'],'PAUSE')
        self.assertEqual(second['mode'],'PAUSE')
        self.assertLess(second['hours_above_hard_reserve'],1)
    def test_no_new_credit_until_both_deadlines_then_true_reset(self):
        anchor=self.old['windows'][0]['resets_at']
        self.observe(self.next(1,90))
        value=self.next(2,0);value['observed_at']=anchor+0.5
        self.denied(value)
        value['observed_at']=anchor+1
        value['windows'][0]['resets_at']=anchor+18000
        self.assertEqual(self.observe(value)['remaining_percent'],98.47)
        stored=self.book.read('kimi',self.old['account_id'])
        self.assertEqual(stored['_local_continuity_v1']['anchors']['limit_5h'],anchor+18000)
        self.assertEqual(stored['windows'][0]['used_percent'],0)
        self.denied(dict(value,observed_at=anchor+2,
                         windows=[dict(value['windows'][0],window_seconds=17999)]+value['windows'][1:]))
    def test_legacy_account_seed_and_old_history_preserved(self):
        with sqlite3.connect(self.path) as db:
            db.execute('DELETE FROM history')
            db.execute('UPDATE accounts SET snapshot=?',(json.dumps(self.old),))
        before=self.rows(); value=self.next(-1)
        self.observe(value); after=self.rows()
        self.assertEqual(after[0][0][0],before[0][0][0])
        self.assertEqual(json.loads(after[1][0][-1]),self.old)
        # Older than six hours: retain raw historical bytes and rowids.
        with sqlite3.connect(self.path) as db:
            db.execute('INSERT INTO history VALUES (99,?,?,?,?)',
                       ('kimi',self.old['account_id'],0,json.dumps(self.old)))
        before=self.rows()[1]; self.observe(self.next(1,1,401))
        self.assertEqual(self.rows()[1][:len(before)],before)
    def test_history_bound_fails_without_eviction(self):
        with sqlite3.connect(self.path) as db:
            for i in range(1023):
                db.execute('INSERT INTO history(provider,account,observed_at,snapshot) VALUES (?,?,?,?)',
                           ('kimi',self.old['account_id'],0,json.dumps(self.old)))
        self.denied(self.next(-1))
    def test_non_kimi_has_no_timestamp_correction(self):
        with tempfile.TemporaryDirectory() as temp:
            book=quota.QuotaBook(Path(temp)/'q.sqlite')
            old=dict(self.old,provider='codex');book.observe('one',old,now=old['observed_at'])
            value=dict(self.next(-1),provider='codex')
            with self.assertRaises(ValueError):book.observe('two',value,now=value['observed_at'])

class CacheSafety(unittest.TestCase):
    def test_early_refusal_before_encoder(self):
        cache=cachemod._HistoryCache(max_decoded_bytes=4096)
        with patch.object(cache, '_encode', return_value=b'{}'), \
                patch.object(cachemod.json.JSONEncoder,'iterencode',side_effect=AssertionError('serialized')):
            cache.put({}, {'chain':[['a']], 'documents':[['a', {'x':'x'*4097}]]})
        self.assertIsNone(cache.get({}))
    def test_stream_is_identical_and_detached(self):
        cache=cachemod._HistoryCache()
        value={'chain':[['a']], 'documents':[['a',{'unicode':'é😀\n"'*300,'nested':[None,True,12,2.5]}]]}
        cache.put({},value); expected=copy.deepcopy(value)
        value['documents'][0][1]['nested'].append('poison')
        self.assertEqual(cache.get({}),expected)
        cache.get({})['chain'].clear(); self.assertEqual(cache.get({}),expected)
    def test_oversized_refusal_keeps_old_snapshot(self):
        cache=cachemod._HistoryCache(max_decoded_bytes=4096)
        old={'chain':[['a']], 'documents':[['a',{}]]}; cache.put({},old)
        cache.put({}, {'chain':[['a'],['b','a']], 'documents':[['a',{}],['b',{'x':'x'*5000}]]})
        self.assertEqual(cache.get({}),old)
    def test_concurrent_old_and_new_and_divergence(self):
        cache=cachemod._HistoryCache()
        old={'chain':[['a']], 'documents':[['a',{}]]}
        new={'chain':[['a'],['b','a']], 'documents':[['a',{}],['b',{}]]}
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda v: cache.put({},v), [old,new]*8))
        self.assertEqual(cache.get({}),new)
        with self.assertRaises(ValueError):
            cache.put({}, {'chain':[['z']], 'documents':[['z',{}]]})
        self.assertEqual(cache.get({}),new)
    def test_encoded_and_entry_bounds(self):
        cache=cachemod._HistoryCache(max_bytes=250,max_entries=2,max_decoded_bytes=10000)
        for i in range(8):cache.put({'i':i},{'chain':[['a']], 'documents':[['a',{}]]})
        self.assertLessEqual(cache._bytes,250);self.assertLessEqual(len(cache._entries),2)
        self.assertIsNone(cache.get({'i':0}))
    def test_oversize_peak_is_bounded_in_child(self):
        # Hosted Linux only: compare incremental RSS above already allocated input.
        import subprocess,sys
        code = '''import importlib.util,resource,sys
s=importlib.util.spec_from_file_location('cache',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
v={'chain':[['a']], 'documents':[['a',{'x':'x'*(140*1024*1024)}]]}
before=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
c=m._HistoryCache();c.put({},v)
assert c.get({}) is None
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss-before < 32*1024
'''
        subprocess.run([sys.executable,'-B','-c',code,str(ROOT/VARIANT/'immutable_history_cache.py')],check=True)


class SessionBoundary(unittest.TestCase):
    def test_reserve_denials_never_create_or_refund_starts(self):
        from cdc_operator.session import SessionBudget
        from cdc_operator.ownership import VerifiedTarget
        for kind in ('exhausted','stale','paid','mandatory','duration','provider','account','rollback'):
            with tempfile.TemporaryDirectory() as temp:
                budget=SessionBudget(Path(temp)/'session.sqlite')
                old=snapshot();old['windows'][0]['used_percent']=1
                budget.quota.observe('one',old,now=old['observed_at'])
                new=copy.deepcopy(FACTS['current_official_normalized_snapshot'])
                new['windows'][0]['used_percent']=2;at=new['observed_at']
                if kind=='exhausted':new['windows'][0]['used_percent']=100
                elif kind=='stale':new['observed_at']-=91
                elif kind=='paid':new['paid_fallback']=True
                elif kind=='mandatory':new['required_windows'].pop()
                elif kind=='duration':new['windows'][0]['window_seconds']+=1
                elif kind=='provider':new['provider']='codex'
                elif kind=='account':new['account_id']='wrong'
                elif kind=='rollback':new['windows'][0]['used_percent']=0
                target=VerifiedTarget('kimi',old['account_id'],'one','session',at,'1'*64)
                with self.assertRaises(ValueError):budget.start('denied',target,'turn',new,now=at)
                with sqlite3.connect(budget.path) as db:
                    self.assertEqual(db.execute('SELECT count(*) FROM stages').fetchone()[0],0)
                    self.assertEqual(db.execute('SELECT count(*) FROM requests').fetchone()[0],0)

    def test_real_start_correction_preserves_unknown_caps(self):
        from cdc_operator.session import SessionBudget
        from cdc_operator.ownership import VerifiedTarget
        with tempfile.TemporaryDirectory() as temp:
            budget=SessionBudget(Path(temp)/'session.sqlite')
            old=snapshot(); budget.quota.observe('one',old,now=old['observed_at'])
            new=FACTS['current_official_normalized_snapshot']; at=new['observed_at']
            target=VerifiedTarget('kimi',old['account_id'],'one','session',at,'1'*64)
            invalid=copy.deepcopy(new);invalid['windows'][0]['resets_at']-=1
            with self.assertRaises(ValueError):
                budget.start('denied',target,'turn',invalid,now=at)
            for key,value in [('account_id','wrong'),('provider','codex')]:
                with self.assertRaises(ValueError):
                    budget.start('denied',target,'turn',dict(new,**{key:value}),now=at)
            with sqlite3.connect(budget.path) as db:
                self.assertEqual(db.execute('SELECT count(*) FROM stages').fetchone()[0],0)
            valid=copy.deepcopy(new)
            stage=budget.start('original',target,'turn',valid,now=at)
            self.assertEqual(stage['request_cap'],4)
            self.assertEqual(stage['expires_at'],at+900)
            with self.assertRaises(ValueError):budget.reserve_native('original','task','attempt',4,now=at)
            budget.reserve_native('original','task','attempt',3,now=at)
            with self.assertRaises(ValueError):budget.reserve_native('original','task','other',1,now=at)
            for i in range(4):budget.reserve_request('original',str(i),'session',valid,now=at)
            with self.assertRaises(ValueError):budget.reserve_request('original','fifth','session',valid,now=at)
            self.assertEqual(budget.read('original')['expires_at'],at+900)
            with self.assertRaises(ValueError):budget.reserve_request('original','late','session',valid,now=at+900)
            with self.assertRaises(ValueError):budget.close('original',{})
            self.assertEqual(budget.read('original')['status'],'UNKNOWN')
            with self.assertRaises(ValueError):budget.start('replacement',target,'other',valid,now=at)
            self.assertEqual(budget.read('original')['requests'],4)


class NormalizationBoundary(unittest.TestCase):
    def test_exact_runtime_projection_does_not_round_reset(self):
        import datetime
        spec=importlib.util.spec_from_file_location('normalization',ROOT/'baseline/normalization.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        epoch=lambda v:datetime.datetime.fromtimestamp(v,datetime.timezone.utc).isoformat()
        for key in ('previous_accepted_snapshot','current_official_normalized_snapshot'):
            expected=FACTS[key];at=expected['observed_at']
            metadata={'status':'observed','actual_uid':1005,
                      'identity':{'user_id':expected['account_id'],'status':'USER_STATUS_NORMAL'},
                      'tools_enabled':['mcp__cdc__*'],'extra_usage_policy':'OWNER_REPORTED_OFF',
                      'observed_at':epoch(at),'access_expires_at':at+300,
                      'quota':{w['name']:{'used_ratio':w['used_percent']/100,
                                          'reset_time':epoch(w['resets_at'])} for w in expected['windows']}}
            actual=module.normalize(metadata,expected['account_id'],now=at)
            self.assertEqual([w['resets_at'] for w in actual['windows']],
                             [w['resets_at'] for w in expected['windows']])
            self.assertEqual([w['window_seconds'] for w in actual['windows']],
                             [w['window_seconds'] for w in expected['windows']])
            with self.assertRaises(ValueError):module.normalize(metadata,'other-account',now=at)
            with self.assertRaises(ValueError):module.normalize(metadata,expected['account_id'],now=at+91)

if __name__ == '__main__': unittest.main()
