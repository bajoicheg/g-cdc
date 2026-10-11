#!/usr/bin/env python3
"""Owner disposition of UNKNOWN isolated create-only Git effects; never replay.

The controller must authenticate and persist/read back the referenced owner,
caller and physical-runtime evidence before calling. Parsing is not authority.
This administrative transition supplies no provider outcome or launch authority.
"""
from __future__ import annotations
import copy
import re
import operation_intent as op
import execution_lease_v2 as lease
from submission_recovery import _reference, _fresh, SHA

PILOT = re.compile(r'^refs/heads/pilot/[A-Za-z0-9][A-Za-z0-9._/-]*$')

def _validate_proof(proof, guard, repository, source_ref, release, at):
    op._object(proof, {'schema','lease_revision','lease_digest','guard_digest','repository',
        'source_ref','observed_at_utc','owner_decision','effect','runtime'}, 'retirement proof')
    if proof['schema'] != 'unknown-submission-retirement/v1':
        raise ValueError('unsupported retirement proof')
    if not isinstance(proof['lease_revision'],str) or not SHA.fullmatch(proof['lease_revision']):
        raise ValueError('immutable current lease revision required')
    op._digest(proof['lease_digest'],'retirement lease digest')
    if (proof['guard_digest'] != op._hash(guard) or proof['repository'] != repository
            or proof['source_ref'] != source_ref):
        raise ValueError('retirement must bind exact guard and repository/source')
    claim=guard['submission_claim']; intent=guard['intent']
    if (claim is None or intent['state'] not in {'submitting','unknown'} or intent['task'] is not None
            or release is None or release['owner_id'] != claim['owner_id']
            or release['generation'] != claim['generation'] or not release['invocation_id']
            or release['external_reconciliation'] != 'unknown_preserved'):
        raise ValueError('exact released UNKNOWN claim required; accepted/taskful operations unsupported')
    released=op._timestamp(release['at_utc'],'release time')
    claimed=op._timestamp(claim['claimed_at_utc'],'claim time')
    if claimed > released:
        raise ValueError('release cannot precede original claim')
    _fresh(proof['observed_at_utc'],at,released)
    decision=proof['owner_decision']
    op._object(decision,{'action','reference'},'owner decision')
    if decision['action'] != 'retire_unknown_without_replay':
        raise ValueError('explicit owner UNKNOWN retirement decision required')
    _reference(decision['reference'])
    effect=proof['effect']
    op._object(effect,{'backend','target_ref','candidate_sha','expected_target','receive_pack_calls',
        'subprocess_returned','caller_reference','caller_digest','observation_reference'},'original effect')
    target=effect['target_ref']
    if (effect['backend'] != 'git-conditional-create' or intent['binding']['backend'] != effect['backend']
            or effect['candidate_sha'] != intent['binding']['candidate_sha']
            or not isinstance(target,str) or not PILOT.fullmatch(target)
            or any(x in target for x in ('..','//','@{')) or target.endswith(('/','.','.lock'))
            or any(x.endswith('.lock') or x.startswith('.') for x in target.split('/'))
            or target == source_ref or effect['expected_target'] is not None
            or type(effect['receive_pack_calls']) is not int or effect['receive_pack_calls'] != 1
            or effect['subprocess_returned'] is not True):
        raise ValueError('only original returned single create-only isolated pilot Git push supported')
    for name in ('caller_reference','observation_reference'): _reference(effect[name])
    op._digest(effect['caller_digest'],'original caller digest')
    runtime=proof['runtime']
    op._object(runtime,{'invocation_id','owner_id','generation','status','quiescent',
        'pending_shared_writes','observed_at_utc','reference'},'stopped original runtime')
    if (runtime['invocation_id'] != release['invocation_id'] or runtime['owner_id'] != claim['owner_id']
            or type(runtime['generation']) is not int or runtime['generation'] != claim['generation']
            or runtime['status'] != 'stopped' or runtime['quiescent'] is not True
            or runtime['pending_shared_writes'] is not False):
        raise ValueError('exact original physically stopped/quiescent runtime required')
    _fresh(runtime['observed_at_utc'],at,released); _reference(runtime['reference'])

def validate_retirement(entry, record):
    """Validate immutable history independently of the current generation/clock."""
    if isinstance(entry,dict) and entry.get('schema')=='actions-submission-retirement/v1':
        return _validate_actions_retirement(entry,record)
    op._object(entry,{'schema','outcome','replay_forbidden','guard','original_release','proof',
        'evidence_reference','retired_at_utc'},'submission retirement')
    if (entry['schema'] != 'submission-retirement/v1' or entry['outcome'] != 'UNKNOWN'
            or entry['replay_forbidden'] is not True):
        raise ValueError('retirement must preserve UNKNOWN and permanent no replay')
    at=entry['retired_at_utc']; op._timestamp(at,'retirement time'); _reference(entry['evidence_reference'])
    # Reuse the original strict legacy guard validator without recursing into v2.
    projected=lease._legacy_projection(record,sanitize_migrated=True)
    projected['external_guard']=copy.deepcopy(entry['guard'])
    lease.legacy.validate(projected)
    lease._validate_release(entry['original_release'],record['generation'])
    _validate_proof(entry['proof'],entry['guard'],record['repository'],record['source_ref'],entry['original_release'],at)
    return entry

def _forbids_intent(entry,intent):
    old=entry['guard']['intent']; binding=intent['binding']; old_binding=old['binding']
    # Changing attempt, mode, environment, key or backend cannot disguise the
    # same retired candidate. Distinct source upgrade candidates remain eligible.
    return (intent['operation_key']==old['operation_key']
            or (binding['repository']==old_binding['repository']
                and binding['candidate_sha']==old_binding['candidate_sha']))

def retire_unknown_guard(record, proof, evidence_reference, at):
    """Pure transition; no ownership, provider terminal fact or budget refund."""
    lease.validate(record); _reference(evidence_reference)
    if (record.get('schema') != 'execution-lease/v2' or record['owner_id'] is not None
            or record['invocation'] is not None or record['finalization'] is not None
            or record['external_guard'] is None):
        raise ValueError('retirement requires a released v2 guarded lease')
    guard=record['external_guard']; claim=guard['submission_claim']
    if claim is None or claim['generation'] != record['generation']:
        raise ValueError('retirement must bind original released generation')
    if claim['grant_id'] in lease._resolved_grant_ids(record):
        raise ValueError('terminal-resolved claims cannot be retired')
    if proof.get('lease_digest') != op._hash(record):
        raise ValueError('retirement proof must bind exact current lease digest')
    _validate_proof(proof,guard,record['repository'],record['source_ref'],record['last_release'],at)
    result=copy.deepcopy(record)
    result['external_guard']=None
    result.setdefault('submission_retirements',[]).append(dict(schema='submission-retirement/v1',
        outcome='UNKNOWN',replay_forbidden=True,guard=copy.deepcopy(guard),
        original_release=copy.deepcopy(record['last_release']),proof=copy.deepcopy(proof),
        evidence_reference=evidence_reference,retired_at_utc=at))
    return lease.validate(result)

def retire_unknown_cas(store, expected_revision, proof, evidence_reference, at):
    """One conditional coordination write and independent readback; no replay."""
    revision,previous=store.read()
    if revision != expected_revision or proof.get('lease_revision') != expected_revision:
        raise ValueError('stale retirement revision; re-observe without replay')
    result=retire_unknown_guard(previous,proof,evidence_reference,at)
    revision=store.compare_and_swap(expected_revision,result)
    observed_revision,observed=store.read()
    if observed_revision != revision or observed != result:
        raise ValueError('retirement readback changed; re-observe without replay')
    return dict(revision=revision,record=result,outcome='UNKNOWN',authorizes_submission=False,
        authorizes_takeover=False,authorizes_merge=False,authorizes_release=False)


# Actions UNKNOWN quarantine is deliberately separate from positive cancellation
# and create-only Git retirement. It supplies neither a transport result nor a send.
_ACTIONS_EVIDENCE_TOKEN=object()
_ACTIONS_ARTIFACTS={'scope','owner_decision','original_ui','runtime','provider_observation','physical_stop','provider_lookup','workflow_definition'}

def _actions_descriptor(value):
    op._object(value,{'revision','ref','path','pointer','sha256'},'Actions evidence pin')
    if not isinstance(value['revision'],str) or not SHA.fullmatch(value['revision']):
        raise ValueError('immutable Actions evidence revision required')
    if (not isinstance(value['ref'],str) or not value['ref'].startswith('refs/heads/')
            or not isinstance(value['path'],str) or value['path'].startswith('/')
            or any(x in {'','..','.'} for x in value['path'].split('/'))
            or not isinstance(value['pointer'],str) or not value['pointer'].startswith('/')):
        raise ValueError('exact native evidence ref, relative path and JSON pointer required')
    op._digest(value['sha256'],'Actions evidence byte hash')

def _validate_actions_proof(proof,guard,repository,source_ref,release,at):
    op._object(proof,{'schema','lease_revision','lease_digest','original_lease_revision',
        'guard_digest','repository','source_ref','observed_at_utc','scope','owner_decision',
        'original_ui','transport','runtime','provider_observation','physical_stop','provider_lookup','workflow_definition','evidence'},'Actions retirement proof')
    if proof['schema']!='actions-unknown-retirement-proof/v1':
        raise ValueError('unsupported Actions administrative proof')
    for key in ['lease_revision','original_lease_revision']:
        if not isinstance(proof[key],str) or not SHA.fullmatch(proof[key]):raise ValueError('immutable original/current lease revision required')
    op._digest(proof['lease_digest'],'Actions lease digest')
    if (proof['guard_digest']!=op._hash(guard) or proof['repository']!=repository or proof['source_ref']!=source_ref):
        raise ValueError('exact Actions guard/repository/source binding required')
    claim=guard['submission_claim'];intent=guard['intent'];binding=intent['binding']
    if (claim is None or intent['state'] not in {'submitting','unknown'} or intent['task'] is not None
            or binding['backend']!='github-actions' or binding['mode']!='ordinary-unsigned-pilot'
            or release is None or release['owner_id']!=claim['owner_id'] or release['generation']!=claim['generation']
            or not release['invocation_id'] or release['external_reconciliation']!='unknown_preserved'):
        raise ValueError('only exact taskless released ordinary-unsigned-pilot/github-actions UNKNOWN supported')
    claimed=op._timestamp(claim['claimed_at_utc'],'claim time');released=op._timestamp(release['at_utc'],'release time')
    if claimed>released:raise ValueError('original claim must precede release')
    _fresh(proof['observed_at_utc'],at,released)
    scope=proof['scope']
    op._object(scope,{'backend','mode','method','workflow','target','candidate_sha','read_only'},'original Actions scope')
    if (scope['backend']!=binding['backend'] or scope['mode']!=binding['mode'] or scope['method']!='POST'
            or scope['candidate_sha']!=binding['candidate_sha'] or scope['read_only'] is not True
            or not isinstance(scope['workflow'],str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+)*\.ya?ml',scope['workflow'])
            or scope['target']!='repos/'+repository+'/actions/workflows/'+scope['workflow']+'/dispatches'):
        raise ValueError('exact read-only ordinary unsigned pilot workflow-dispatch target required')
    decision=proof['owner_decision']
    op._object(decision,{'action','operation_key','grant_id','owner_id','generation','scope','at_utc'},'original owner decision')
    if (decision['action']!='retire_actions_unknown_without_replay' or decision['scope']!=scope
            or any(decision[k]!=claim[k] for k in ['operation_key','grant_id','owner_id','generation'])
            or type(decision['generation']) is not int):
        raise ValueError('explicit exact owner administrative UNKNOWN disposition required')
    if not released<=op._timestamp(decision['at_utc'],'owner decision time')<=op._timestamp(at,'retirement time'):
        raise ValueError('owner disposition must follow original release')
    ui=proof['original_ui'];op._object(ui,{'closed_without_run','final_run_clicked','original_ci_submitted','at_utc'},'original UI evidence')
    if (ui['closed_without_run'] is not True or ui['final_run_clicked'] is not False or ui['original_ci_submitted'] is not False
            or not claimed<=op._timestamp(ui['at_utc'],'UI close time')<=released):
        raise ValueError('original pre-release Close-without-Run evidence required')
    if proof['transport']!={'outcome':'UNKNOWN','cancellation_barrier':None,'dispatcher_birth':None,'no_in_flight':None}:
        raise ValueError('missing transport proof remains NULL/UNKNOWN, never manufactured cancellation')
    runtime=proof['runtime']
    op._object(runtime,{'invocation_id','owner_id','generation','status','quiescent','pending_shared_writes','observed_at_utc','reference'},'original stopped runtime')
    if (runtime['invocation_id']!=release['invocation_id'] or runtime['owner_id']!=claim['owner_id']
            or type(runtime['generation']) is not int or runtime['generation']!=claim['generation']
            or runtime['status']!='stopped' or runtime['quiescent'] is not True or runtime['pending_shared_writes'] is not False):
        raise ValueError('exact original locally stopped/quiescent runtime required')
    _fresh(runtime['observed_at_utc'],at,released);_reference(runtime['reference'])
    observation=proof['provider_observation'];decision=op.decide(intent,observation)
    if (observation['lookup_complete'] is not True or observation['tasks']!=[] or decision['action']!='reconcile'
            or observation['operation_key']!=claim['operation_key']):
        raise ValueError('complete exact provider lookup must retain UNKNOWN without an invented terminal')
    _fresh(observation['observed_at_utc'],at,released)
    physical=proof['physical_stop']
    op._object(physical,{'boot_id','executor_pid','executor_birth','supervisor_pid','supervisor_birth','absent','invocation_id','owner_id','generation','observed_at_utc'},'original native physical stop')
    if (physical['invocation_id']!=release['invocation_id'] or physical['owner_id']!=claim['owner_id']
            or type(physical['generation']) is not int or physical['generation']!=claim['generation'] or physical['absent'] is not True):
        raise ValueError('exact original physical stopped identity required')
    lease._uuid(physical['boot_id'],'original kernel boot identity')
    for prefix in ['executor','supervisor']:
        pid=physical[prefix+'_pid'];birth=physical[prefix+'_birth']
        if type(pid) is not int or pid<=0 or not isinstance(birth,str) or not re.fullmatch(r'[0-9]+',birth):
            raise ValueError('original birth-bound native PID required; missing dispatcher birth remains separately UNKNOWN')
    if physical['executor_pid']==physical['supervisor_pid']:raise ValueError('executor and supervisor identities must be distinct')
    _fresh(physical['observed_at_utc'],at,released)
    lookup=proof['provider_lookup']
    op._object(lookup,{'repository','workflow','candidate_sha','operation_key','grant_id','surfaces','pagination_complete','observed_at_utc','evidence_refs'},'complete original provider lookup')
    if (lookup['repository']!=repository or lookup['workflow']!=scope['workflow'] or lookup['candidate_sha']!=scope['candidate_sha']
            or lookup['operation_key']!=claim['operation_key'] or lookup['grant_id']!=claim['grant_id']
            or lookup['surfaces']!=['status','check_runs','actions'] or lookup['pagination_complete'] is not True
            or not isinstance(lookup['evidence_refs'],list) or len(lookup['evidence_refs'])<3):
        raise ValueError('complete status/check-runs/Actions original-window lookup required')
    for reference in lookup['evidence_refs']:_reference(reference)
    _fresh(lookup['observed_at_utc'],at,released);op._digest(proof['workflow_definition'],'original workflow byte hash')
    op._object(proof['evidence'],_ACTIONS_ARTIFACTS,'authenticated original-channel artifact pins')
    for descriptor in proof['evidence'].values():_actions_descriptor(descriptor)
    workflow_pin=proof['evidence']['workflow_definition']
    if (workflow_pin['revision']!=scope['candidate_sha'] or workflow_pin['path']!='.github/workflows/'+scope['workflow']
            or workflow_pin['sha256']!=proof['workflow_definition'] or workflow_pin['pointer']!='/'):
        raise ValueError('original exact candidate workflow bytes must be pinned')

def _validate_actions_retirement(entry,record):
    op._object(entry,{'schema','outcome','replay_forbidden','guard','original_release','proof','evidence_reference','retired_at_utc'},'Actions retirement history')
    if entry['schema']!='actions-submission-retirement/v1' or entry['outcome']!='UNKNOWN' or entry['replay_forbidden'] is not True:
        raise ValueError('Actions retirement must retain UNKNOWN permanently')
    _reference(entry['evidence_reference']);op._timestamp(entry['retired_at_utc'],'retirement time')
    projected=lease._legacy_projection(record,sanitize_migrated=True);projected['external_guard']=copy.deepcopy(entry['guard']);lease.legacy.validate(projected)
    lease._validate_release(entry['original_release'],record['generation'])
    if entry['guard']['submission_claim'] not in record['submission_claims']:raise ValueError('original consumed claim must remain exact history')
    _validate_actions_proof(entry['proof'],entry['guard'],record['repository'],record['source_ref'],entry['original_release'],entry['retired_at_utc'])
    return entry

def retire_actions_unknown_guard(record,proof,evidence_reference,at):
    """Pure proposal/history validation only. Native CAS additionally needs authentication."""
    lease.validate(record);_reference(evidence_reference)
    if (record.get('schema')!='execution-lease/v2' or any(record[k] is not None for k in ['owner_id','invocation','finalization'])
            or record['external_guard'] is None):raise ValueError('released guarded v2 lease required')
    guard=record['external_guard'];claim=guard['submission_claim']
    if (claim is None or claim['generation']!=record['generation'] or claim['grant_id'] in lease._resolved_grant_ids(record)
            or proof.get('lease_digest')!=op._hash(record)):raise ValueError('exact unresolved original lease/claim required')
    _validate_actions_proof(proof,guard,record['repository'],record['source_ref'],record['last_release'],at)
    result=copy.deepcopy(record);result['external_guard']=None
    result.setdefault('submission_retirements',[]).append(dict(schema='actions-submission-retirement/v1',outcome='UNKNOWN',replay_forbidden=True,
        guard=copy.deepcopy(guard),original_release=copy.deepcopy(record['last_release']),proof=copy.deepcopy(proof),evidence_reference=evidence_reference,retired_at_utc=at))
    return lease.validate(result)

class ActionsRetirementEvidence:
    """Ephemeral exact native-Git evidence capability, never caller proof syntax."""
    def __init__(self,token,store,proof,pins,at):
        if token is not _ACTIONS_EVIDENCE_TOKEN:raise ValueError('verified native evidence capability required')
        self._store=store;self._proof=copy.deepcopy(proof);self._pins=copy.deepcopy(pins);self._at=at

    def revalidate(self,store,expected_revision,previous,entry):
        if (store is not self._store or expected_revision!=self._proof['lease_revision']
                or entry['proof']!=self._proof or entry['retired_at_utc']!=self._at):
            raise ValueError('verified evidence capability must bind exact native CAS and proposal')
        _authenticate_actions_artifacts(store,self._proof,self._pins,self._at)
        if previous['external_guard']!=entry['guard'] or previous['last_release']!=entry['original_release']:
            raise ValueError('original authoritative guard/release changed before CAS')

def _authenticate_actions_artifacts(store,proof,pins,at):
    """Use deployment-pinned original-channel bytes, not pins derived from untrusted proof.

    The original native caller independently obtains real provider pages and fresh
    birth-bound local absence and saves/readbacks their exact reports. This code
    authenticates their configured Git endpoint and bytes; it never contacts a
    provider, invents a transport barrier, or upgrades UNKNOWN to a terminal fact.
    """
    import hashlib,json
    from pathlib import Path
    from git_lease_store import GitLeaseStore
    from git_remote_identity import isolated_remote_args
    if type(store) is not GitLeaseStore:raise ValueError('actual configured native Git lease store required')
    revision,record=store.read()
    if revision!=proof.get('lease_revision'):raise ValueError('stale Actions lease; observe without replay')
    retire_actions_unknown_guard(record,proof,'sha256:'+'0'*64,at)
    op._object(pins,_ACTIONS_ARTIFACTS,'trusted deployment evidence pins')
    if pins!=proof['evidence']:raise ValueError('proof must match independently trusted evidence pins')
    original=store.read_revision(proof['original_lease_revision'])
    if (original['external_guard']!=record['external_guard'] or original['last_release']!=record['last_release']
            or original['generation']!=record['generation'] or original['owner_id'] is not None):
        raise ValueError('exact immutable original released guard/claim required')
    physical=proof['physical_stop']
    if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=physical['boot_id']:
        raise ValueError('fresh original native kernel must verify stopped identity; boot change is not terminal proof')
    for prefix in ['executor','supervisor']:
        if Path('/proc',str(physical[prefix+'_pid'])).exists():raise ValueError('original exact native PID must be absent, never infer stop from elapsed time')
    fetched={};blobs={}
    for name,pin in pins.items():
        _actions_descriptor(pin);store._assert_remote_identity();store._git('check-ref-format',pin['ref'])
        if pin['ref'] not in fetched:
            rows=store._git('ls-remote','--refs',store.remote,pin['ref']).splitlines()
            if len(rows)!=1 or rows[0].split('\t')[1]!=pin['ref']:raise ValueError('missing authoritative evidence ref')
            current=rows[0].split('\t')[0]
            config,remote=isolated_remote_args(store.repo,store.remote,store.store_id)
            store._git(*config,'fetch','--no-tags','--no-write-fetch-head','--refmap=',remote,pin['ref']);fetched[pin['ref']]=current
        current=fetched[pin['ref']]
        if store._git('merge-base',pin['revision'],current)!=pin['revision']:raise ValueError('evidence revision lacks authoritative ancestry')
        blob_key=(pin['revision'],pin['path'])
        if blob_key not in blobs:
            rows=store._git('ls-tree','--full-tree','-z',pin['revision'],'--',pin['path'],raw=True).split(b'\0');rows=[r for r in rows if r]
            if len(rows)!=1:raise ValueError('authenticated evidence regular blob missing')
            metadata,path=rows[0].split(b'\t',1);mode,kind,_=metadata.split(b' ')
            if mode not in {b'100644',b'100755'} or kind!=b'blob' or path!=pin['path'].encode():raise ValueError('authenticated evidence must be an exact regular Git blob')
            blobs[blob_key]=store._git('show',pin['revision']+':'+pin['path'],raw=True)
        raw=blobs[blob_key]
        if 'sha256:'+hashlib.sha256(raw).hexdigest()!=pin['sha256']:raise ValueError('authenticated immutable evidence bytes mismatch')
        if name=='workflow_definition':
            import yaml
            definition=yaml.safe_load(raw)
            if not isinstance(definition,dict):raise ValueError('original read-only workflow definition required')
            permissions=definition.get('permissions')
            if (not isinstance(permissions,dict) or permissions.get('contents')!='read'
                    or any(p not in {'read','none'} for p in permissions.values())):
                raise ValueError('original workflow permissions must be read-only')
            trigger=definition.get('on',definition.get(True));jobs=definition.get('jobs')
            if (not isinstance(trigger,(dict,list)) or 'workflow_dispatch' not in trigger
                    or not isinstance(jobs,dict) or not jobs):raise ValueError('original read-only workflow-dispatch jobs required')
            for job in jobs.values():
                if not isinstance(job,dict):raise ValueError('original workflow job must be an object')
                job_permissions=job.get('permissions',permissions)
                if not isinstance(job_permissions,dict) or any(p not in {'read','none'} for p in job_permissions.values()):raise ValueError('job permissions exceed original read-only scope')
            continue
        body=json.loads(raw,object_pairs_hook=op._unique_object)
        for segment in pin['pointer'].split('/')[1:]:
            segment=segment.replace('~1','/').replace('~0','~')
            if not isinstance(body,dict) or segment not in body:raise ValueError('original evidence pointer missing')
            body=body[segment]
        if body!=proof[name]:raise ValueError('caller facts disagree with authenticated original evidence')
        store._assert_remote_identity()
    return record

def authenticate_actions_retirement(store,proof,trusted_evidence_pins,at):
    """Trusted original native channel only; inputs/refs alone are never authority."""
    _authenticate_actions_artifacts(store,proof,trusted_evidence_pins,at)
    return ActionsRetirementEvidence(_ACTIONS_EVIDENCE_TOKEN,store,proof,trusted_evidence_pins,at)

def retire_actions_unknown_cas(store,expected_revision,proof,evidence_reference,at,*,evidence_capability):
    revision,previous=store.read()
    if revision!=expected_revision or proof.get('lease_revision')!=expected_revision:raise ValueError('stale retirement revision; observe without replay')
    if type(evidence_capability) is not ActionsRetirementEvidence:raise ValueError('authenticated native evidence capability required')
    result=retire_actions_unknown_guard(previous,proof,evidence_reference,at)
    # The store revalidates the typed capability at its actual conditional write.
    # Do not repeat all native evidence fetches once more in this wrapper.
    revision=store.compare_and_swap(expected_revision,result,retirement_capability=evidence_capability)
    actual_revision,actual=store.read()
    if actual_revision!=revision or actual!=result:raise ValueError('retirement readback changed; observe without replay')
    return dict(revision=revision,record=result,outcome='UNKNOWN',authorizes_submission=False,authorizes_takeover=False,authorizes_merge=False,authorizes_release=False)

def observe_actions_retirement(store,proof,evidence_reference):
    """Read only recovery after lost reply; never another CAS or external send."""
    _reference(evidence_reference);revision,record=store.read()
    if record is None:raise ValueError('original authoritative lease absent; preserve UNKNOWN')
    matches=[e for e in record.get('submission_retirements',[]) if e['schema']=='actions-submission-retirement/v1' and e['proof']==proof and e['evidence_reference']==evidence_reference]
    if len(matches)!=1:raise ValueError('exact authoritative retirement not observed; preserve UNKNOWN')
    return dict(revision=revision,record=record,outcome='UNKNOWN',authorizes_submission=False,authorizes_takeover=False,authorizes_merge=False,authorizes_release=False)
