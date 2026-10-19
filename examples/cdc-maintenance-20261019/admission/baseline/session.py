"""Bounded operator coordination state, distinct from native attempt authority.

Evidence and official-refresh callback are trusted internal broker inputs.
Actual official collector/maintenance wiring remains CLOSED until Task4 binds
its real principal, whole-package pin and existing protected provider gates.
"""
import contextlib
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3

from .ownership import VerifiedTarget
from .quota import assess,QuotaBook

GATES={'official_identity','included_usage_only','session_horizon','refresh',
       'egress','containment','actual_principal'}
IDENTITY={'provider','account_id','profile_id','session_id','principal','uid','package_tree'}


def verify_session(expected,evidence,*,now):
    if not isinstance(expected,dict) or set(expected)!=IDENTITY or not isinstance(evidence,dict):
        raise ValueError('protected session binding required')
    if (expected['provider']!='kimi' or expected['principal']!='cdcopkimi'
            or type(expected['uid']) is not int or expected['uid']<1005
            or any(not isinstance(expected[k],str) or not expected[k] for k in IDENTITY-{'uid'})
            or not re.fullmatch('[0-9a-f]{40}',expected['package_tree'])):
        raise ValueError('whole package and dedicated principal must be qualified')
    if any(evidence.get(k)!=expected[k] for k in IDENTITY):
        raise ValueError('actual session identity mismatch')
    at=evidence.get('observed_at');proof=evidence.get('proof_sha256')
    if (type(now) not in (int,float) or not math.isfinite(now)
            or type(at) not in (int,float) or not math.isfinite(at) or not 0<=now-at<=90
            or not isinstance(proof,str) or not re.fullmatch('[0-9a-f]{64}',proof)
            or not isinstance(evidence.get('gates'),dict) or set(evidence['gates'])!=GATES
            or any(v is not True for v in evidence['gates'].values())):
        raise ValueError('fresh protected provider gates required')
    return VerifiedTarget(**{k:expected[k] for k in ('provider','account_id','profile_id','session_id')},
                          observed_at=at,proof_sha256=proof)


def serial_refresh(lock_root,profile_id,official_refresh):
    if not isinstance(profile_id,str) or not profile_id or not callable(official_refresh):
        raise ValueError('fixed official refresh callback required')
    name=hashlib.sha256(profile_id.encode()).hexdigest()+'.refresh.lock'
    fd=os.open(Path(lock_root)/name,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX)
        return official_refresh()
    finally:os.close(fd)


class SessionBudget:
    def __init__(self,path):
        self.path=Path(path);fd=os.open(self.path,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600);os.close(fd)
        self.quota=QuotaBook(self.path.parent/'quota.sqlite')
        with self._db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS stages (id TEXT PRIMARY KEY, body TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS requests (operation TEXT PRIMARY KEY, stage TEXT)')

    @contextlib.contextmanager
    def _db(self):
        db=sqlite3.connect(self.path,timeout=5)
        try:
            db.execute('PRAGMA synchronous=FULL');db.execute('BEGIN IMMEDIATE');yield db;db.commit()
        except BaseException:db.rollback();raise
        finally:db.close()

    @staticmethod
    def _read(db,stage):
        row=db.execute('SELECT body FROM stages WHERE id=?',(stage,)).fetchone()
        if row is None:raise ValueError('original stage unknown')
        return json.loads(row[0])

    @staticmethod
    def _save(db,row):
        db.execute('INSERT OR REPLACE INTO stages VALUES (?,?)',(row['id'],json.dumps(row,allow_nan=False)))

    def _quota(self,target,snapshot,now):
        if (snapshot.get('provider'),snapshot.get('account_id')) != (target['provider'],target['account_id']):
            raise ValueError('quota account mismatch')
        decision=self.quota.observe(target['profile_id'],snapshot,now=now)
        if decision['mode']!='ALLOW':
            raise ValueError('fresh shared reserve required')

    def start(self,stage,target,turn_id,snapshot,*,now):
        if not isinstance(target,VerifiedTarget) or not isinstance(stage,str) or not stage or not isinstance(turn_id,str) or not turn_id:
            raise ValueError('verified original stage required')
        if type(now) not in (int,float) or not math.isfinite(now) or not 0<=now-target.observed_at<=90:
            raise ValueError('stale target')
        binding={k:getattr(target,k) for k in ('provider','account_id','profile_id','session_id')}
        self._quota(binding,snapshot,now)
        with self._db() as db:
            if db.execute('SELECT 1 FROM stages WHERE id=?',(stage,)).fetchone():
                raise ValueError('original stage cannot be restarted')
            # Same provider account cannot open overlapping operator stages.
            for row in db.execute('SELECT body FROM stages'):
                active=json.loads(row[0])
                if (active['target']['provider'],active['target']['account_id'])==(target.provider,target.account_id) and active['status']!='CLOSED':
                    raise ValueError('original account session must close first')
            value={'id':stage,'target':binding,'turn_id':turn_id,'started_at':now,'expires_at':now+900,
                   'request_cap':4,'requests':0,'native':None,'status':'ACTIVE'}
            self._save(db,value)
            return value

    @staticmethod
    def _active(row,now):
        if row['status']!='ACTIVE' or now<row['started_at'] or now>=row['expires_at']:
            raise ValueError('original session deadline or UNKNOWN')

    def reserve_request(self,stage,operation_id,session_id,snapshot,*,now):
        if not isinstance(operation_id,str) or not operation_id:
            raise ValueError('original operation required')
        with self._db() as db:
            row=self._read(db,stage);self._active(row,now)
            if row['target']['session_id']!=session_id or row['requests']>=row['request_cap']:
                raise ValueError('session mismatch or four-request cap')
            if db.execute('SELECT 1 FROM requests WHERE operation=?',(operation_id,)).fetchone():
                raise ValueError('original reservation consumed; do not replay')
            self._quota(row['target'],snapshot,now)
            db.execute('INSERT INTO requests VALUES (?,?)',(operation_id,stage));row['requests']+=1;self._save(db,row)
            return {'operation_id':operation_id,'expires_at':row['expires_at'],'reserved':True}

    def reserve_native(self,stage,task_id,attempt_id,model_starts,*,now):
        if (not isinstance(task_id,str) or not task_id or not isinstance(attempt_id,str) or not attempt_id
                or type(model_starts) is not int or not 0<=model_starts<=3):
            raise ValueError('one original native attempt, at most three model starts')
        with self._db() as db:
            row=self._read(db,stage);self._active(row,now)
            if row['native'] is not None:raise ValueError('native allowance already consumed')
            row['native']={'task_id':task_id,'attempt_id':attempt_id,'max_model_starts':model_starts};self._save(db,row)
            return row['native']

    def may_cancel(self,stage,turn_id,*,now):
        row=self.read(stage)
        return (row['turn_id']==turn_id and row['status']!='CLOSED' and now>=row['expires_at'])

    def close(self,stage,proof):
        valid=(isinstance(proof,dict) and set(proof)=={'physical_absence','waitpid_echild'}
               and proof['physical_absence'] is True and proof['waitpid_echild'] is True)
        with self._db() as db:
            row=self._read(db,stage);row['status']='CLOSED' if valid else 'UNKNOWN';self._save(db,row)
        if not valid:raise ValueError('actual original process closure unresolved')
        return row

    def read(self,stage):
        with self._db() as db:return self._read(db,stage)
