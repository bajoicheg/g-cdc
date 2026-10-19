"""Real SDK graph plus deliberately oversized optional cache insertion."""
import copy
import unittest
from unittest.mock import patch
import test_history_reuse as fixtures
import immutable_history_cache as cachemod
import unknown_recovery as native

class OversizedHistory(unittest.TestCase):
    def fixture(self):
        f=fixtures.HistoryReuseTests();f.setUp();self.addCleanup(f.doCleanups);return f
    def test_refusal_does_not_remove_any_mandatory_document(self):
        f=self.fixture(); cache=cachemod._HistoryCache(max_decoded_bytes=8)
        with patch.object(cachemod,'_cache',cache):
            history=native._history(f.store)
            self.assertEqual([r for r,_ in history],f.revisions)
            self.assertEqual([v['value']['number'] for _,v in history],[0,1,2])
            self.assertEqual(len(cache._entries),0)
            self.assertEqual(native._history(f.store),history)
    def test_oversized_new_snapshot_keeps_prior_rewrite_guard(self):
        f=self.fixture();cache=cachemod._HistoryCache(max_decoded_bytes=4096)
        with patch.object(cachemod,'_cache',cache):
            first=native._history(f.store)
            f.store.compare_and_swap(f.revisions[-1],{'oversized':'x'*5000})
            second=native._history(f.store)
            self.assertEqual(second[:-1],first)
            cached=cache.get(cachemod._context(f.store,'document'))
            self.assertEqual(len(cached['chain']),len(first))
            f.git('push','--force','origin',f.revisions[0]+':'+f.store.ref)
            with self.assertRaises(ValueError):native._history(f.store)
    def test_oversize_cache_does_not_relax_parent_authentication(self):
        with self.assertRaises(ValueError):
            cachemod._linear_chain(['a'*40, 'b'*40+' '+'c'*40])
