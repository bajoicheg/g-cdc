"""Fresh shared account metadata; token counters never imply provider allowance.

Input is a normalized projection assembled by a trusted qualified observer.
This module neither reads credentials nor calls or refreshes a provider.
"""
import copy
import json
import math
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


def _number(v):
    return type(v) in (int, float) and math.isfinite(v)


def assess(snapshot, *, now, history=()):
    if not isinstance(snapshot, dict) or not _number(now):
        raise ValueError('missing quota')
    for key in ('provider', 'account_id'):
        if not isinstance(snapshot.get(key), str) or not snapshot[key]:
            raise ValueError('missing account bucket')
    if snapshot['provider'] not in ('kimi', 'codex'):
        raise ValueError('unsupported provider')
    at = snapshot.get('observed_at')
    if not _number(at) or not 0 <= now-at <= 90:
        raise ValueError('stale or future metadata')
    if snapshot.get('ordinary_usage_allowed') is not True or snapshot.get('paid_fallback') is not False:
        raise ValueError('included-only usage not proven')
    required = snapshot.get('required_windows')
    windows = snapshot.get('windows')
    if (not isinstance(required, list) or not required or len(required)>16
            or any(not isinstance(n,str) or not n for n in required)
            or len(set(required)) != len(required) or not isinstance(windows, list)
            or len(windows) != len(required)):
        raise ValueError('mandatory windows unavailable')
    names = set(); remaining = []; runways = []
    for w in windows:
        if not isinstance(w, dict) or set(w) != {'name','used_percent','resets_at','window_seconds'}:
            raise ValueError('invalid window')
        n = w['name']; used = w['used_percent']; end = w['resets_at']; duration = w['window_seconds']
        if (not isinstance(n,str) or n not in required or n in names
                or not _number(used) or not 0 <= used <= 100
                or not _number(end) or end <= now
                or not _number(duration) or duration <= 0):
            raise ValueError('invalid quota or expired reset')
        names.add(n); r = 100-used; remaining.append(r); rate = 0
        for old in history:
            if (old.get('provider'),old.get('account_id')) != (snapshot['provider'],snapshot['account_id']):
                continue
            dt = at-old.get('observed_at',at)
            if not 300 <= dt <= 21600:
                continue
            for prev in old.get('windows',[]):
                if (prev.get('name') == n and prev.get('resets_at') == end
                        and _number(prev.get('used_percent'))):
                    rate = max(rate,max(0,used-prev['used_percent'])*3600/dt)
        if rate > 0:
            runways.append(max(0,r-5)/rate)
    least = min(remaining); runway = min(runways,default=None)
    if least <= 5:mode = 'STOP'
    elif least < 15 or runway is not None and runway < 1:mode = 'PAUSE'
    elif least < 20 or runway is not None and runway < 2:mode = 'ROTATE'
    else:mode = 'ALLOW'
    return {'mode':mode,'remaining_percent':least,'hours_above_hard_reserve':runway}



# Local continuity policy, not a claim about provider bucket equivalence.
# This field is produced only from transactional stored state, never caller input.
_STATE = '_local_continuity_v1'


def _anchor(snapshot, window):
    state = snapshot.get(_STATE)
    return (state['anchors'][window['name']] if state is not None
            else window['resets_at'])


def _history_for(history, value):
    """Match burn history by immutable local anchor, including legacy copies.

    Changing a hold deadline must not erase a previously measured burn rate.
    Old epochs remain stored but cannot contribute new-epoch credit.
    """
    current = {w['name']: w for w in value['windows']}
    result = []
    for observation in history:
        item = copy.deepcopy(observation)
        for w in item['windows']:
            v = current.get(w['name'])
            if (v is not None and _anchor(observation, w) == _anchor(value, v)
                    and w['window_seconds'] == v['window_seconds']):
                w['resets_at'] = v['resets_at']
        result.append(item)
    return result


def _both(raw, effective):
    severity = {'ALLOW': 0, 'ROTATE': 1, 'PAUSE': 2, 'STOP': 3}
    runways = [v['hours_above_hard_reserve'] for v in (raw, effective)
               if v['hours_above_hard_reserve'] is not None]
    return {'mode': max((raw['mode'], effective['mode']), key=severity.__getitem__),
            'remaining_percent': min(raw['remaining_percent'], effective['remaining_percent']),
            'hours_above_hard_reserve': min(runways, default=None)}


class QuotaBook:
    def __init__(self,path):
        self.path=Path(path)
        fd=os.open(self.path,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600);os.close(fd)
        with self._db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS accounts (provider TEXT, account TEXT, snapshot TEXT, PRIMARY KEY(provider,account))')
            db.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, provider TEXT, account TEXT, observed_at REAL, snapshot TEXT)')

    @contextmanager
    def _db(self):
        db=sqlite3.connect(self.path,timeout=5)
        try:
            db.execute('PRAGMA synchronous=FULL');db.execute('BEGIN IMMEDIATE');yield db;db.commit()
        except BaseException:db.rollback();raise
        finally:db.close()

    def observe(self,profile_id,snapshot,*,now):
        if not isinstance(profile_id,str) or not profile_id:
            raise ValueError('trusted profile required')
        if not isinstance(snapshot, dict) or _STATE in snapshot:
            raise ValueError('official raw snapshot required; local state is not input')
        assess(snapshot,now=now)
        value=copy.deepcopy(snapshot);key=(value['provider'],value['account_id'])
        with self._db() as db:
            old=db.execute('SELECT snapshot FROM accounts WHERE provider=? AND account=?',key).fetchone()
            anchors={w['name']:w['resets_at'] for w in value['windows']}
            if old:
                previous=json.loads(old[0])
                if value['observed_at'] < previous['observed_at']:
                    raise ValueError('older profile cannot reset account observation')
                if set(value['required_windows']) != set(previous['required_windows']):
                    raise ValueError('account mandatory windows changed')
                prior={w['name']:w for w in previous['windows']}
                for w in value['windows']:
                    p=prior[w['name']]; anchor=_anchor(previous,p)
                    if p['window_seconds']!=w['window_seconds']:
                        raise ValueError('window binding changed')
                    within_bound=abs(w['resets_at']-anchor)<=1
                    if p['resets_at']<=now and within_bound:
                        raise ValueError('expired continuity hold; genuine reset required')
                    if p['resets_at']>now or within_bound:
                        # Only the measured fixed bound, against ORIGINAL anchor.
                        # Never infer a provider reset or accumulate rolling drift.
                        if (w['resets_at'] != anchor and
                                (value['provider'] != 'kimi' or abs(w['resets_at']-anchor)>1)):
                            raise ValueError('unverified reset change before original reset')
                        if w['used_percent']<p['used_percent']:
                            raise ValueError('usage rollback before conservative reset')
                        anchors[w['name']]=anchor
                        w['resets_at']=max(anchor,p['resets_at'],w['resets_at'])
                    # A within-bound observation remains continuity even after
                    # expiry: it cannot roll the anchor or mint reset credit.
                    # Otherwise existing true-reset conditions apply: fresh raw
                    # future deadline, previous effective hold expired. Only here
                    # can usage fall and a new immutable anchor be established.
            value[_STATE]={'anchors':anchors,'raw':copy.deepcopy(snapshot)}
            # The whole account, including all profiles, has ONE history.
            # Seed legacy account state before its first history-aware refresh.
            if old and not db.execute('SELECT 1 FROM history WHERE provider=? AND account=?',key).fetchone():
                db.execute('INSERT INTO history(provider,account,observed_at,snapshot) VALUES (?,?,?,?)',
                           (*key,previous['observed_at'],json.dumps(previous,allow_nan=False)))
            if db.execute('SELECT count(*) FROM history WHERE provider=? AND account=?',key).fetchone()[0]>=1024:
                raise ValueError('shared quota history bound; no silent burn-history eviction')
            history=[json.loads(row[0]) for row in db.execute(
                'SELECT snapshot FROM history WHERE provider=? AND account=? ORDER BY id',key)]
            db.execute('INSERT INTO history(provider,account,observed_at,snapshot) VALUES (?,?,?,?)',
                       (*key,value['observed_at'],json.dumps(value,allow_nan=False)))
            raw_history=[h.get(_STATE,{}).get('raw',h) for h in history]
            raw_decision=assess(snapshot,now=now,history=raw_history)
            decision=_both(raw_decision, assess(value,now=now,history=_history_for(history,value)))
            if old:
                db.execute('UPDATE accounts SET snapshot=? WHERE provider=? AND account=?',
                           (json.dumps(value,allow_nan=False),*key))
            else:
                db.execute('INSERT INTO accounts VALUES (?,?,?)',(*key,json.dumps(value,allow_nan=False)))
        return decision

    def account_count(self):
        with self._db() as db:return db.execute('SELECT count(*) FROM accounts').fetchone()[0]

    def read(self,provider,account_id):
        with self._db() as db:
            row=db.execute('SELECT snapshot FROM accounts WHERE provider=? AND account=?',(provider,account_id)).fetchone()
        if row is None:raise ValueError('account quota unknown')
        return json.loads(row[0])
