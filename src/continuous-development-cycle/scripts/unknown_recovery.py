"""Native administrative UNKNOWN custody; never a terminal or send capability.

Trust inputs are deployment-owned original channel/contract pins. All effects
are single native CAS writes to the original record; lost replies are read only.
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
import stat
import subprocess
import uuid
from pathlib import Path
import operation_intent as op
from git_document_store import GitDocumentStore
from git_lease_store import GitLeaseStore
from managed_executor_runtime import _process, _boot, _digest as native_digest

_SEAL=object()
INTAKE_SCHEMA='cdc-vps-control/v1'
DISPOSITION_SCHEMA='prelaunch-intake-disposition/v1'


def _history(store):
    """Authenticate every ancestor, rejecting shallow, merged or truncated history."""
    if type(store) not in (GitDocumentStore,GitLeaseStore):raise ValueError('actual native Git store required')
    current,_=store.read()
    if current is None:raise ValueError('original native history missing')
    if store._git('rev-parse','--is-shallow-repository')!='false':raise ValueError('complete native history required')
    rows=store._git('rev-list','--parents',current).splitlines()
    if len(rows)>10000:raise ValueError('native history exceeds authentication bound')
    result=[]
    for row in reversed(rows):
        fields=row.split()
        if len(fields)>2:raise ValueError('native coordination history must be linear')
        document=store._read_document_object(fields[0]) if type(store) is GitDocumentStore else store._read_record(fields[0])
        result.append((fields[0],document))
    if current!=store.read()[0]:raise ValueError('native history moved during authentication')
    return result


def _identity(value,*,absent):
    op._object(value,{'pid','birth','boot_id'},'original process identity')
    if type(value['pid']) is not int or value['pid']<=0 or not isinstance(value['birth'],str) or not value['birth'].isdigit() or value['boot_id']!=_boot():raise ValueError('original native birth/boot identity required')
    current=_process(value['pid'])
    if absent:
        try:Path('/proc',str(value['pid'])).stat()
        except FileNotFoundError:pass
        except OSError:raise ValueError('original physical PID probe unavailable') from None
        else:raise ValueError('original PID present, including reused or zombie birth')
    if not absent and (current is None or current['birth']!=value['birth']):raise ValueError('start consumption requires exact current controller birth')


def _row(document,task_id):
    if document.get('schema')!=INTAKE_SCHEMA or not isinstance(document.get('tasks'),dict) or task_id not in document['tasks']:raise ValueError('registered native intake row required')
    row=document['tasks'][task_id]
    if row.get('task',{}).get('id')!=task_id:raise ValueError('immutable native intake task index mismatch')
    return row


def _consumed(row):
    operation=row.get('operation') or {}
    return 'controllers' in operation or operation.get('controller_identity') is not None or operation.get('checkpoint_ref') is not None or operation.get('finish_result') is not None or operation.get('start_consumption') is not None or operation.get('handle_id') is not None or row.get('result') is not None


def semantic_intake_contract(row):
    """Only task identity/dependency names are excluded from replay matching."""
    task=row.get('task')
    if not isinstance(task,dict):raise ValueError('immutable intake task contract required')
    return op._hash({key:value for key,value in task.items() if key not in {'id','dependencies'}})


def _contract(row):
    request=(row.get('operation') or {}).get('start_request')
    if not isinstance(request,dict) or row['operation'].get('start_request_digest')!=native_digest(request):raise ValueError('original unchanged native start contract required')
    return native_digest(request)


def _physical_and_artifacts(store,row,pins):
    request=row['operation']['start_request']
    _identity(pins['creator'],absent=True);_identity(pins['guardian'],absent=True)
    guardian=row['operation'].get('guardian')
    if not isinstance(guardian,dict) or guardian.get('nonce')!=pins['guardian_nonce'] or guardian.get('identity')!=pins['guardian']:raise ValueError('original canonical guardian nonce/identity required')
    if pins['pool_ref']!=request['plan']['coordination_ref'] or request['plan']['coordination_store_id']!=store.store_id:raise ValueError('original protected pool channel mismatch')
    store._assert_remote_identity();store._git('check-ref-format',pins['pool_ref'])
    if store._git('ls-remote','--refs',store.remote,pins['pool_ref']):raise ValueError('native original pool/runtime effect already exists')
    custody=pins.get('custody')
    op._object(custody,{'controller_root','worker_launch_root','controller_uid','worker_gid'},'complete original protected custody')
    if any(type(custody[k]) is not int or custody[k]<0 for k in ('controller_uid','worker_gid')):raise ValueError('configured custody UID/GID required')
    task_id=request['task_id'];executor=row['operation']['executor']
    for name in (task_id,executor):
        if not isinstance(name,str) or not name or name in {'.','..'} or '/' in name or '\\' in name:raise ValueError('exact original custody identity required')
    controller=Path(custody['controller_root'])/task_id
    launch=Path(custody['worker_launch_root'])/executor/task_id
    roots=pins['launch_roots'];allowed=pins.get('artifact_pins',{})
    expected={request['journal_root'],request['handle_root'],str(controller),str(launch)}
    if not isinstance(roots,list) or len(roots)!=len(set(roots)) or set(roots)!=expected or not isinstance(allowed,dict):raise ValueError('complete derived original controller/worker/native roots required')
    from managed_host_bridge import _canonical
    from git_remote_identity import repository_root
    identity={'repo_root':str(repository_root(request['repo_root'])),'store':request['plan']['coordination_store_id'],'coordination_ref':request['plan']['coordination_ref'],'pool_id':request['plan']['pool_id'],'task_id':task_id,'attempt_id':request['attempt_id']}
    handle=str(uuid.uuid5(uuid.NAMESPACE_URL,_canonical(identity)))
    native_paths=[Path(request['handle_root'])/(handle+'.json'),Path(request['handle_root'])/'gates'/handle,Path(request['handle_root'])/'locks'/(handle+'.lock'),Path(request['journal_root'])/native_digest({name:identity[name] for name in ('pool_id','task_id','attempt_id')}).split(':',1)[1]]
    publication_ref='refs/heads/cdc/managed-host-publish-'+handle.replace('-','')
    if store._git('ls-remote','--refs',store.remote,publication_ref):raise ValueError('original publication journal already exists')
    # Native effect scopes are absent unconditionally, including empty directories
    # and broken symlinks. Deployment pins can never turn effects into static data.
    for path in native_paths:
        if any(p.is_symlink() for p in [path,*path.parents]) or path.exists():raise ValueError('native session/gate/lock/journal effect blocks prelaunch disposition')
    for raw in [*roots,custody['controller_root'],custody['worker_launch_root']]:
        path=Path(raw)
        if not path.is_absolute() or str(path.resolve())!=raw or any(p.is_symlink() for p in [path,*path.parents]):raise ValueError('protected exact launch root required')
        if path.exists() and not path.is_dir():raise ValueError('launch root must be a directory')
    # Original output is an absence fact, never a hash whitelist. Native worker
    # preparation may create this empty directory before dispatch.
    output=launch/'output'
    if output.is_symlink() or output.exists() and (not output.is_dir() or any(output.iterdir())):raise ValueError('original worker output must be empty')
    static={str(controller/'guardian.lock'),str(launch/'record.json'),str(launch/'registered-record.json')}
    if not static<=set(allowed):raise ValueError('original controller/preparation/registered static records required')
    checkout=launch/'worktree'
    checkout_dirs={checkout}
    if checkout.exists():
        if checkout.is_symlink() or not checkout.is_dir():raise ValueError('original static checkout custody required')
        from git_object_integrity import git_object_environment
        def checkout_git(*args,check=True,binary=False):
            result=subprocess.run(['git','--no-optional-locks','-c','safe.directory='+str(checkout),'-c','core.fsmonitor=false','-c','core.hooksPath=/dev/null','-C',str(checkout),*args],env=git_object_environment(GIT_TERMINAL_PROMPT='0',GIT_OPTIONAL_LOCKS='0'),text=not binary,capture_output=True,timeout=20)
            if check and result.returncode:raise ValueError('original prepared checkout unavailable')
            return (result.stdout if binary else result.stdout.strip()),result.returncode
        if checkout_git('rev-parse','--show-toplevel')[0]!=str(checkout) or checkout_git('rev-parse','HEAD')[0]!=row['task']['source_sha'] or checkout_git('symbolic-ref','-q','HEAD',check=False)[1]!=1 or checkout_git('status','--porcelain','--untracked-files=all')[0] or checkout_git('remote')[0]:raise ValueError('prepared static checkout changed or is not isolated')
        # Index flags or cached stat data cannot turn changed worker bytes into a
        # static source snapshot. Compare every committed blob independently.
        tree=checkout_git('ls-tree','-r','-z','HEAD',binary=True)[0]
        source_files=set()
        for entry in tree.split(b'\0'):
            if not entry:continue
            metadata,name=entry.split(b'\t',1);mode,kind,oid=metadata.split()
            path=checkout/name.decode('utf-8');source_files.add(path)
            if mode not in (b'100644',b'100755') or kind!=b'blob' or path.is_symlink() or not path.is_file() or path.read_bytes()!=checkout_git('cat-file','blob',oid.decode(),binary=True)[0]:raise ValueError('original prepared source bytes differ from exact source commit')
        git_root=checkout/'.git'
        metadata_names={'HEAD','config','description','index','packed-refs','info/exclude','logs/HEAD'}
        samples={'applypatch-msg','commit-msg','fsmonitor-watchman','post-update','pre-applypatch','pre-commit','pre-merge-commit','pre-push','pre-rebase','pre-receive','prepare-commit-msg','push-to-checkout','sendemail-validate','update'}
        metadata_names.update('hooks/'+name+'.sample' for name in samples)
        metadata=set()
        for path in git_root.rglob('*'):
            if not path.is_file():continue
            name=path.relative_to(git_root).as_posix()
            is_ref=re.fullmatch(r'(?:logs/)?refs/(?:heads|tags|remotes)/[^\x00-\x20~^:?*\[\\]+',name)
            is_object=re.fullmatch(r'objects/(?:[0-9a-f]{2}/(?:[0-9a-f]{38}|[0-9a-f]{62})|pack/pack-(?:[0-9a-f]{40}|[0-9a-f]{64})\.(?:pack|idx|rev|bitmap))',name)
            if name not in metadata_names and not is_ref and not is_object:raise ValueError('unknown file cannot be pinned as static Git metadata')
            metadata.add(path)
        files={p for p in checkout.rglob('*') if p.is_file()}
        if files!=source_files|metadata:raise ValueError('unregistered worker file in prepared source checkout')
        static.update(str(p) for p in files)
        checkout_dirs.update(git_root/name for name in ('','branches','hooks','info','logs','objects','objects/info','objects/pack','refs','refs/heads','refs/tags','refs/remotes','logs/refs','logs/refs/heads','logs/refs/tags','logs/refs/remotes'))
        for path in files:
            checkout_dirs.update(parent for parent in path.parents if parent==checkout or checkout in parent.parents)
    if not set(allowed)<=static:raise ValueError('pins may describe only original pre-effect static custody')
    guardian_pin=allowed[str(controller/'guardian.lock')]
    op._object(guardian_pin,{'sha256','uid','gid','mode'},'original guardian static custody')
    seen=set()
    for root in (controller,launch):
        expected_gid=guardian_pin['gid'] if root==controller else custody['worker_gid']
        if not root.is_dir():raise ValueError('complete original protected controller/worker scope missing')
        for child in [root,*root.rglob('*')]:
            if child.is_symlink():raise ValueError('contradictory symlink in protected launch root')
            info=child.lstat()
            if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):raise ValueError('special entry in protected custody')
            if info.st_uid!=custody['controller_uid'] or info.st_gid!=expected_gid or info.st_mode & 0o002:raise ValueError('protected scope ownership/mode drift')
            if child.is_dir():
                if child!=output and info.st_mode & 0o020:raise ValueError('static custody must not be worker writable')
                if root==controller and child!=root:raise ValueError('unregistered controller effect directory')
                if root==launch and child not in {launch,output}|checkout_dirs:raise ValueError('unregistered worker effect directory')
                continue
            key=str(child);seen.add(key);pin=allowed.get(key)
            op._object(pin,{'sha256','uid','gid','mode'},'protected static artifact pin')
            if info.st_nlink!=1 or (info.st_uid,info.st_gid,info.st_mode & 0o7777)!=(pin['uid'],pin['gid'],pin['mode']) or info.st_mode & 0o022:raise ValueError('protected static file custody/mode drift')
            if 'sha256:'+hashlib.sha256(child.read_bytes()).hexdigest()!=pin['sha256']:raise ValueError('original static artifact bytes drift')
            if child==controller/'guardian.lock' and child.read_bytes()!=b'':raise ValueError('original guardian lock must be empty')
            if child.name in {'record.json','registered-record.json'} and child.parent==launch:
                try:record=json.loads(child.read_text())
                except (ValueError,OSError):raise ValueError('original protected preparation record unavailable') from None
                if child.name=='registered-record.json':
                    op._object(record,{'schema','task','registry','task_digest','executor'},'original registered launch record')
                    if record['schema']!='cdc-vps-launch/v1' or record['task']!=row['task'] or record['task_digest']!=native_digest(row['task']) or record['executor']!=executor or not isinstance(record['registry'],dict):raise ValueError('registered launch record/task/executor mismatch')
                else:
                    op._object(record,{'operation_id','profile_id','source_sha','source_ref','profile_digest'},'original preparation record')
                    if record['operation_id']!=task_id or record['source_sha']!=row['task']['source_sha'] or record['source_ref']!=request['lease_source_ref'] or not isinstance(record['profile_id'],str) or not re.fullmatch('[0-9a-f]{64}',record['profile_digest']):raise ValueError('original preparation record/source mismatch')
    if seen!=set(allowed):raise ValueError('pinned original static launch artifact missing')
    _identity(pins['creator'],absent=True);_identity(pins['guardian'],absent=True)


def _authenticate_intake(store,task_id,source,pins,*,retired=False):
    if type(store) is not GitDocumentStore or type(source) is not GitLeaseStore:raise ValueError('actual configured native stores required')
    required={'original_revision','row_digest','source_revision','source_digest','creator','guardian','guardian_nonce','pool_ref','launch_roots','custody'}
    if not isinstance(pins,dict) or set(pins) not in (required,required|{'artifact_pins'}):raise ValueError('independent trusted original contract pins required')
    history=_history(store);original=store.read_revision(pins['original_revision']);original_row=_row(original,task_id)
    if op._hash(original_row)!=pins['row_digest'] or _consumed(original_row):raise ValueError('pinned original unconsumed task row required')
    from managed_host_bridge import _validate_start
    _validate_start(original_row['operation']['start_request'])
    request=original_row['operation']['start_request']
    if source.ref!=request['lease_coordination_ref'] or original_row['operation']['attempt_id']!=request['attempt_id'] or request['task_id']!=task_id:raise ValueError('original native source/start/attempt channel mismatch')
    import budget
    budget.validate_ledger(original_row['budget'])
    original_intent=original_row['operation']['intent'];op.validate_intent(original_intent)
    if original_intent['binding']['repository']!=request['lease_repository'] or original_intent['binding']['candidate_sha']!=request['plan']['base_sha'] or original_intent['source_ref']!=request['lease_source_ref'] or original_intent['attempt_id']!=request['attempt_id']:raise ValueError('original native intake intent/start contract mismatch')
    digest=_contract(original_row);seen=False;admitted=False;intent_rank=-1
    for revision,doc in history:
        rows=doc.get('tasks',{})
        row=rows.get(task_id)
        if row is None:
            if seen:raise ValueError('original native task row was deleted')
            continue
        seen=True
        budget.validate_ledger(row['budget'])
        if {key:value for key,value in row['budget'].items() if key not in {'events','wake_ids'}}!={key:value for key,value in original_row['budget'].items() if key not in {'events','wake_ids'}} or original_row['budget']['wake_ids'][:len(row['budget']['wake_ids'])]!=row['budget']['wake_ids']:raise ValueError('original charged budget policy/identity history changed')
        if row.get('task')!=original_row['task']:raise ValueError('original task contract changed in history')
        if row.get('operation') is None:
            if admitted or row.get('state')!='queued' or row.get('result') is not None:raise ValueError('native admission/history erased')
            continue
        admitted=True
        if _consumed(row) and not (retired and row['state']=='retired_unknown'):raise ValueError('original controller/start/output history consumed')
        historical=copy.deepcopy(row['operation']);canonical=copy.deepcopy(original_row['operation'])
        historical.pop('guardian',None);canonical.pop('guardian',None)
        if historical.get('observation') is not None and historical['observation']!=canonical.get('observation'):raise ValueError('original observational history changed')
        historical.pop('observation',None);canonical.pop('observation',None)
        historical_intent=historical.get('intent');original_intent=canonical.get('intent')
        if isinstance(original_intent,dict) and original_intent.get('schema')==op.SCHEMA:
            op.validate_intent(historical_intent);op.validate_intent(original_intent)
            ranks={'prepared':0,'submitting':1,'unknown':2}
            rank=ranks.get(historical_intent['state'],-1)
            if rank<0 or rank<intent_rank or rank>ranks.get(original_intent['state'],-1) or historical_intent['task'] is not None:raise ValueError('prelaunch native intent ancestry must remain unconsumed and forward')
            intent_rank=rank
            for transient in ('state','updated_at_utc','durable_intent'):
                historical['intent'].pop(transient,None);canonical['intent'].pop(transient,None)
        if _contract(row)!=digest or historical!=canonical:raise ValueError('complete original start contract/controller history changed')
        if 'guardian' in row['operation'] and row['operation']['guardian']!=original_row['operation']['guardian']:raise ValueError('original guardian history changed')
        if row['budget']!=original_row['budget']:
            old_events=row['budget'].get('events');events=original_row['budget'].get('events')
            if not isinstance(old_events,list) or not isinstance(events,list) or events[:len(old_events)]!=old_events or revision==pins['original_revision']:raise ValueError('original budget event ancestry changed')
    revision,document=store.read();current=_row(document,task_id)
    if retired:validate_prelaunch_disposition(current)
    elif current!=original_row or current.get('state') not in ('unknown','starting','start_unknown'):raise ValueError('exact original prelaunch UNKNOWN row required')
    srev,sdoc=source.read()
    if retired:
        sdoc=source.read_revision(pins['source_revision']);srev=pins['source_revision']
    if srev!=pins['source_revision'] or op._hash(sdoc)!=pins['source_digest'] or sdoc['owner_id'] is not None or sdoc['external_guard'] is not None or sdoc['repository']!=request['lease_repository'] or sdoc['source_ref']!=request['lease_source_ref']:raise ValueError('unchanged canonical absent-native source lease required')
    if source.store_id!=store.store_id:raise ValueError('original source/control endpoint mismatch')
    _physical_and_artifacts(store,original_row,pins)
    return revision,current


class PrelaunchIntakeDispositionProof(dict):
    """Ephemeral administrative slot custody, distinct from terminal proof."""
    def __init__(self,seal,store,task_id,source,pins,at,*,retired=False):
        if seal is not _SEAL:raise ValueError('package issued prelaunch disposition required')
        revision,row=_authenticate_intake(store,task_id,source,pins,retired=retired)
        super().__init__(schema=DISPOSITION_SCHEMA,task_id=task_id,contract_digest=_contract(row),original_effect='UNKNOWN',actual_wait=None,original_revision=pins['original_revision'])
        self._evidence=copy.deepcopy(dict(self))
        self._seal=seal;self._store=store;self._source=source;self._pins=copy.deepcopy(pins);self._at=at;self._revision=revision;self._retired=retired
    def revalidate_for(self,store,task_id):
        if dict(self)!=self._evidence:raise ValueError('native disposition evidence capability was mutated')
        if self._seal is not _SEAL or store is not self._store or task_id!=self['task_id']:raise ValueError('original native disposition endpoint/task substituted')
        return _authenticate_intake(store,task_id,self._source,self._pins,retired=self._retired)[1]


def authenticate_prelaunch_intake(store,task_id,*,source_store,trusted_contract,at):
    op._timestamp(at,'administrative disposition time')
    return PrelaunchIntakeDispositionProof(_SEAL,store,task_id,source_store,trusted_contract,at)


def _validate_prelaunch_disposition_row(row):
    """Structural history validation only; serialized data supplies no authority."""
    entry=(row.get('result') or {}).get('administrative_disposition')
    fields={'schema','task_id','contract_digest','original_effect','actual_wait','replay_forbidden','original_revision','original_row','trusted_contract','retired_at_utc'}
    op._object(entry,fields,'native prelaunch disposition')
    if row.get('state')!='retired_unknown' or entry['schema']!=DISPOSITION_SCHEMA or entry['original_effect']!='UNKNOWN' or entry['actual_wait'] is not None or entry['replay_forbidden'] is not True or _contract(row)!=entry['contract_digest']:raise ValueError('prelaunch disposition must preserve UNKNOWN/no wait/no replay')
    if entry['task_id']!=row['task'].get('id'):raise ValueError('original task identity must match disposition')
    original=entry['original_row'];expected=copy.deepcopy(original);expected['state']='retired_unknown';expected['result']={'administrative_disposition':copy.deepcopy(entry)}
    if expected!=row or _consumed(original) or op._hash(original)!=entry['trusted_contract']['row_digest'] or entry['original_revision']!=entry['trusted_contract']['original_revision']:raise ValueError('administrative disposition cannot alter original liabilities/contract')
    op._timestamp(entry['retired_at_utc'],'disposition time')
    return entry


def validate_intake_transition(previous,document,*,store,expected_revision,recovery_capability=None):
    if (not previous or previous.get('schema')!=INTAKE_SCHEMA) and document.get('schema')!=INTAKE_SCHEMA:return
    if not previous or previous.get('schema')!=INTAKE_SCHEMA:
        if any(row.get('state')=='retired_unknown' for row in document.get('tasks',{}).values()):raise ValueError('raw initialization cannot mint native disposition')
        return
    if document.get('schema')!=INTAKE_SCHEMA:raise ValueError('native intake schema cannot be replaced')
    old_rows=previous['tasks'];new_rows=document['tasks'];retired=[]
    for task_id,row in old_rows.items():
        if row.get('state')=='retired_unknown':
            validate_prelaunch_disposition(row)
            if new_rows.get(task_id)!=row:raise ValueError('native tombstone/history cannot be changed or removed')
            retired.append((_contract(row),semantic_intake_contract(row)))
        elif (new_rows.get(task_id) or {}).get('state')=='retired_unknown':
            if type(recovery_capability) is not PrelaunchIntakeDispositionProof or recovery_capability._retired or recovery_capability._revision!=expected_revision:raise ValueError('native tombstone CAS requires issued exact revision proof')
            recovery_capability.revalidate_for(store,task_id)
            entry=validate_prelaunch_disposition(new_rows[task_id])
            if entry['original_row']!=row or entry['trusted_contract']!=recovery_capability._pins or entry['retired_at_utc']!=recovery_capability._at:raise ValueError('native disposition proposal substituted')
            expected=copy.deepcopy(previous);expected['tasks'][task_id]=copy.deepcopy(new_rows[task_id])
            if expected!=document:raise ValueError('tombstone CAS cannot mutate unrelated fields')
            retired.append((_contract(row),semantic_intake_contract(row)))
        new_consumption=((new_rows.get(task_id) or {}).get('operation') or {}).get('start_consumption')
        if new_consumption is not None and (row.get('operation') or {}).get('start_consumption') is None:
            if type(recovery_capability) is not _StartConsumption:raise ValueError('start CAS requires native one-use consumption capability')
            recovery_capability.revalidate(store,expected_revision,task_id,document)
        if (row.get('operation') or {}).get('start_consumption') is not None and ((new_rows.get(task_id) or {}).get('operation') or {}).get('start_consumption')!=row['operation']['start_consumption']:raise ValueError('native one-use start consumption is immutable')
    for task_id,row in new_rows.items():
        if row.get('state')!='retired_unknown' and any((row.get('operation') is not None and _contract(row)==contract) or semantic_intake_contract(row)==semantic for contract,semantic in retired):raise ValueError('retired original start contract cannot replay under another task/attempt')


def retire_prelaunch_intake_cas(store,expected_revision,task_id,proof,*,at):
    if type(proof) is not PrelaunchIntakeDispositionProof or proof._retired or at!=proof._at:raise ValueError('native issued administrative proof required')
    row=proof.revalidate_for(store,task_id);revision,document=store.read()
    if revision!=expected_revision or revision!=proof._revision:raise ValueError('stale original intake revision; observe without replay')
    changed=copy.deepcopy(document);new=changed['tasks'][task_id];new['state']='retired_unknown'
    new['result']={'administrative_disposition':dict(schema=DISPOSITION_SCHEMA,task_id=task_id,contract_digest=_contract(row),original_effect='UNKNOWN',actual_wait=None,replay_forbidden=True,original_revision=proof._pins['original_revision'],original_row=copy.deepcopy(row),trusted_contract=copy.deepcopy(proof._pins),retired_at_utc=at)}
    revision=store.compare_and_swap(expected_revision,changed,recovery_capability=proof)
    actual,readback=store.read()
    if actual!=revision or readback!=changed:raise ValueError('native disposition readback moved; observe without replay')
    retired_proof=observe_prelaunch_intake_disposition(store,task_id,contract_digest=_contract(row),source_store=proof._source)
    return {'revision':revision,'row':new,'proof':retired_proof}


def observe_prelaunch_intake_disposition(store,task_id,*,contract_digest,source_store=None):
    if type(store) is not GitDocumentStore:raise ValueError('actual native intake store required')
    _,document=store.read();row=_row(document,task_id);entry=validate_prelaunch_disposition(row)
    if entry['contract_digest']!=contract_digest:raise ValueError('original disposition contract mismatch')
    if source_store is None:
        request=row['operation']['start_request']
        source_store=GitLeaseStore(store.repo,store.remote,request.get('lease_coordination_ref','refs/heads/cdc/source-lease'))
    return PrelaunchIntakeDispositionProof(_SEAL,store,task_id,source_store,entry['trusted_contract'],entry['retired_at_utc'],retired=True)


def assert_intake_start_allowed(store,task_id,start_request_digest):
    _,document=store.read();row=_row(document,task_id)
    if row.get('state')=='retired_unknown' or _consumed(row) or _contract(row)!=start_request_digest:raise ValueError('native intake start blocked by tombstone/consumption/contract')
    for other in document['tasks'].values():
        if other.get('state')=='retired_unknown' and (validate_prelaunch_disposition(other)['contract_digest']==start_request_digest or semantic_intake_contract(other)==semantic_intake_contract(row)):raise ValueError('original contract replay prohibited')
    return row


def consume_intake_start(store,expected_revision,task_id,*,start_request_digest,controller_identity):
    if type(store) is not GitDocumentStore:raise ValueError('actual native intake store required')
    row=assert_intake_start_allowed(store,task_id,start_request_digest);_identity(controller_identity,absent=False)
    revision,document=store.read()
    if revision!=expected_revision or _row(document,task_id)!=row:raise ValueError('stale start consumption revision')
    changed=copy.deepcopy(document);changed['tasks'][task_id]['operation']['start_consumption']={'schema':'native-intake-start-consumption/v1','contract_digest':start_request_digest,'controller':copy.deepcopy(controller_identity)}
    capability=_StartConsumption(_SEAL,store,expected_revision,task_id,changed,controller_identity)
    return store.compare_and_swap(expected_revision,changed,recovery_capability=capability)


class _StartConsumption:
    def __init__(self,seal,store,revision,task_id,document,identity):
        if seal is not _SEAL:raise ValueError('native one-use start required')
        self.store=store;self.revision=revision;self.task_id=task_id;self.document=copy.deepcopy(document);self.identity=copy.deepcopy(identity)
    def revalidate(self,store,revision,task_id,document):
        if store is not self.store or revision!=self.revision or task_id!=self.task_id or document!=self.document:raise ValueError('native start CAS binding changed')
        _identity(self.identity,absent=False)
        assert_intake_start_allowed(store,task_id,document['tasks'][task_id]['operation']['start_request_digest'])


def migrate_intake_registry_cas(store,expected_revision,old_digest,new_digest):
    """Root configured registry pin migration; no row, charge or queue edits."""
    if type(store) is not GitDocumentStore:raise ValueError('actual native store required')
    op._digest(old_digest,'old trusted registry digest');op._digest(new_digest,'new trusted registry digest')
    revision,document=store.read()
    if revision!=expected_revision or document.get('schema')!=INTAKE_SCHEMA or document.get('registry_digest')!=old_digest or old_digest==new_digest:raise ValueError('stale registry migration binding')
    if any(row.get('state') not in {'queued','succeeded','failed','cancelled','timed_out','retired_unknown'} for row in document['tasks'].values()):raise ValueError('registry migration requires all active attempts reconciled')
    for row in document['tasks'].values():
        if row.get('state')=='retired_unknown':validate_prelaunch_disposition(row)
    changed=copy.deepcopy(document);changed['registry_digest']=new_digest
    revision=store.compare_and_swap(expected_revision,changed)
    actual,value=store.read()
    if actual!=revision or value!=changed:raise ValueError('registry migration reply changed; observe authoritative store')
    return {'revision':revision,'document':changed}


def validate_prelaunch_disposition(store_or_row,task_id=None,row=None):
    """Read validation authenticates immutable native custody, never terminal facts.

    The row-only form checks structure for the native transition validator. Hosts
    must use (native_store, task_id, row) to authenticate authoritative history.
    """
    if task_id is None:return _validate_prelaunch_disposition_row(store_or_row)
    store=store_or_row
    if type(store) is not GitDocumentStore:raise ValueError('actual original native intake channel required')
    _,document=store.read();current=_row(document,task_id)
    if row is not None and current!=row:raise ValueError('serialized disposition differs from authoritative original row')
    entry=_validate_prelaunch_disposition_row(current)
    original=_row(store.read_revision(entry['original_revision']),task_id)
    if original!=entry['original_row'] or entry['task_id']!=task_id:raise ValueError('disposition original ancestry/task mismatch')
    found=False
    for _,historical in _history(store):
        historic=historical.get('tasks',{}).get(task_id)
        if historic is None:
            if found:raise ValueError('native tombstone/history deleted')
            continue
        if historic.get('state')=='retired_unknown':
            if historic!=current:raise ValueError('native tombstone history rewritten')
            found=True
        elif found:raise ValueError('native tombstone was rearmed')
        elif _consumed(historic):raise ValueError('prelaunch disposition has consumed controller/effect ancestry')
    if not found:raise ValueError('native disposition not authoritative')
    return entry


def assert_new_intake_allowed(store,task):
    if type(store) is not GitDocumentStore:raise ValueError('native intake admission store required')
    _,document=store.read()
    for task_id,row in document['tasks'].items():
        if row.get('state')=='retired_unknown':
            validate_prelaunch_disposition(store,task_id,row)
            if semantic_intake_contract({'task':task})==semantic_intake_contract(row):raise ValueError('retired original task contract replay prohibited')
    return True
