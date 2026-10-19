"""Bounded process-local JSON reuse. Entries are data, never permissions/proofs.

Callers must authenticate the endpoint, current ref and complete parent chain on
EVERY read. Cache lineage may save decoding an immutable verified prefix; it
cannot stand in for current head, policy, lease, PID or authority observations.
"""
from __future__ import annotations
from collections import OrderedDict
import json
import threading
import zlib

class _HistoryCache:
    def __init__(self, *, max_bytes=16*1024*1024, max_entries=32, max_decoded_bytes=128*1024*1024):
        self._max_bytes=max_bytes;self._max_entries=max_entries
        self._max_decoded_bytes=max_decoded_bytes
        self._entries=OrderedDict();self._bytes=0;self._lock=threading.RLock()
    @staticmethod
    def _encode(value):
        return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
    def _decode(self, raw):
        try:
            decoder=zlib.decompressobj()
            decoded=decoder.decompress(raw,self._max_decoded_bytes+1)
            if (len(decoded)>self._max_decoded_bytes or decoder.unconsumed_tail
                    or not decoder.eof or decoder.unused_data):
                raise ValueError('compact history exceeds its decoding bound or is incomplete')
            return json.loads(decoded)
        except (zlib.error,UnicodeError,json.JSONDecodeError) as error:
            raise ValueError('compact history encoding changed') from error
    def get(self, context):
        key=self._encode(context)
        with self._lock:
            raw=self._entries.get(key)
            if raw is None:return None
            self._entries.move_to_end(key)
        # Detached decoding prevents any caller from changing a shared prefix.
        return self._decode(raw)
    def _bounded_compact(self, value, *, encoded_limit):
        """Optional entry: cheap conservative refusal before any JSON allocation.

        At most six UTF-8/JSON bytes per string codepoint. A depth bound avoids
        recursion attacks; no document is removed from the caller's history.
        Streaming compression avoids a complete decoded string/bytes copy.
        """
        remaining = self._max_decoded_bytes
        active = set()
        def charge(size):
            nonlocal remaining
            remaining -= size
            return remaining >= 0
        def fits(item, depth=0):
            if depth > 256:
                return False
            if isinstance(item, str):
                return charge(2 + 6 * len(item))
            if item is None or type(item) is bool:
                return charge(5)
            if type(item) is int:
                return charge(2 + item.bit_length())
            if type(item) is float:
                return charge(32)
            if type(item) not in (dict, list, tuple) or id(item) in active:
                return False
            active.add(id(item))
            try:
                if not charge(2):
                    return False
                if type(item) is dict:
                    return all(type(k) is str and fits(k, depth+1) and charge(2)
                               and fits(v, depth+1) for k, v in item.items())
                return all(charge(1) and fits(v, depth+1) for v in item)
            finally:
                active.remove(id(item))
        if encoded_limit <= 0 or not fits(value):
            return None
        compressor = zlib.compressobj(level=1)
        pieces = []; size = 0; decoded_size = 0
        encoder = json.JSONEncoder(sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=False, allow_nan=False)
        for part in encoder.iterencode(value):
            # Preflight bounds the largest encoder string; byte conversion and
            # compressor input use small slices rather than another full copy.
            for offset in range(0, len(part), 16384):
                data = part[offset:offset+16384].encode('utf-8')
                decoded_size += len(data)
                if decoded_size > self._max_decoded_bytes:
                    return None
                chunk = compressor.compress(data)
                size += len(chunk)
                if size > encoded_limit:
                    return None
                if chunk:
                    pieces.append(chunk)
        chunk = compressor.flush(); size += len(chunk)
        if size > encoded_limit:
            return None
        pieces.append(chunk)
        return b''.join(pieces)

    def put(self, context, snapshot):
        key=self._encode(context)
        raw=self._bounded_compact(snapshot, encoded_limit=self._max_bytes-len(key))
        if raw is None:return
        size=len(key)+len(raw)
        with self._lock:
            previous=self._entries.get(key)
            if previous is not None:
                old=self._decode(previous)['chain'];new=snapshot['chain']
                if new[:len(old)]!=old:
                    # A concurrent older reader may finish after a newer one.
                    # Keep the newer observation; never downgrade stored lineage.
                    if old[:len(new)]==new:return
                    raise ValueError('authenticated cached history diverged')
                self._bytes-=len(key)+len(previous)
            self._entries[key]=raw;self._entries.move_to_end(key);self._bytes+=size
            while self._bytes>self._max_bytes or len(self._entries)>self._max_entries:
                discarded,value=self._entries.popitem(last=False);self._bytes-=len(discarded)+len(value)

_cache=_HistoryCache()

def _context(store, kind, binding=None):
    return {'kind':kind,'repo':str(store.repo.resolve()),'remote':store.remote,'ref':store.ref,
            'endpoint':store.store_id,'binding':binding}

def _linear_chain(rows, *, anchor=None):
    """Authenticate the fresh complete ordered graph, including cached parents."""
    import re
    revision=re.compile(r'^(?:[0-9a-f]{40}|[0-9a-f]{64})$')
    chain=[];previous=anchor;seen=set()
    for row in rows:
        parts=row.split()
        if (not parts or any(not revision.fullmatch(value) for value in parts)
                or parts[0] in seen or parts[1:]!=([previous] if previous else [])):
            raise ValueError('native coordination history must preserve one complete parent chain')
        seen.add(parts[0]);chain.append(parts);previous=parts[0]
    return chain
