"""Native administrative UNKNOWN custody; never a terminal or send capability.

Trust inputs are deployment-owned original channel/contract pins. All effects
are single native CAS writes to the original record; lost replies are read only.
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
import os
from datetime import datetime, timezone, timedelta
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
    """Fresh channel/graph authentication; reuse only an immutable decoded prefix."""
    if type(store) not in (GitDocumentStore,GitLeaseStore):raise ValueError('actual native Git store required')
    from immutable_history_cache import _cache,_context,_linear_chain
    current,current_document=store.read()
    if current is None:raise ValueError('original native history missing')
    if store._git('rev-parse','--is-shallow-repository')!='false':raise ValueError('complete native history required')
    rows=store._git('rev-list','--parents',current).splitlines()
    if len(rows)>10000:raise ValueError('native history exceeds authentication bound')
    chain=_linear_chain(reversed(rows))
    if not chain or chain[-1][0]!=current:raise ValueError('complete native history required')
    context=_context(store,'document' if type(store) is GitDocumentStore else 'lease')
    prior=_cache.get(context)
    if prior is not None and chain[:len(prior['chain'])]!=prior['chain']:
        raise ValueError('native history rewound or rewritten')
    result=[] if prior is None else [(revision,document) for revision,document in prior['documents']]
    for parts in chain[len(result):]:
        revision=parts[0]
        document=(current_document if revision==current else
                  store._read_document_object(revision) if type(store) is GitDocumentStore else store._read_record(revision))
        result.append((revision,document))
    if current!=store.read()[0]:raise ValueError('native history moved during authentication')
    _cache.put(context,{'chain':chain,'documents':result})
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


def _intake_channels(store,row,pins,source=None):
    """Join independent configured channels to the original immutable request."""
    request=row['operation']['start_request'];channels=pins.get('channels')
    if channels is None:
        if ('preconsume_exit' in pins or 'guardian_bootstrap_failure' in pins) or source is not None and source.store_id!=store.store_id:
            raise ValueError('independent original intake/project channel pins required')
        return
    op._object(channels,{'intake_store_id','intake_ref','lease_store_id','lease_ref','pool_store_id','pool_ref'},'original intake/project channels')
    expected={'intake_store_id':store.store_id,'intake_ref':store.ref,
        'lease_store_id':request['plan']['coordination_store_id'],'lease_ref':request['lease_coordination_ref'],
        'pool_store_id':request['plan']['coordination_store_id'],'pool_ref':request['plan']['coordination_ref']}
    if channels!=expected:raise ValueError('original intake/project channel binding mismatch')
    if source is not None:
        from git_remote_identity import repository_root
        if type(source) is not GitLeaseStore or source.store_id!=channels['lease_store_id'] or source.ref!=channels['lease_ref'] or source.repo!=repository_root(request['repo_root']) or source.remote!=request.get('coordination_remote',request['remote']):
            raise ValueError('original typed project lease channel substituted')
        source._assert_remote_identity()


def _preconsume_artifacts(row,pins,controller,guardian_pin):
    """A protected infrastructure wait is documentary, never a terminal wait."""
    evidence=pins.get('preconsume_exit')
    if evidence is None:return {}
    op._object(evidence,{'schema','controller','receipt_sha256','stdout_sha256','stderr_sha256','guardian_stdout_sha256','guardian_stderr_sha256'},'original preconsume controller exit')
    if evidence['schema']!='native-preconsume-controller-exit/v1':raise ValueError('unsupported preconsume exit evidence')
    identity=evidence['controller'];_identity(identity,absent=True)
    if identity['pid'] in {pins['guardian']['pid'],pins['creator']['pid']}:raise ValueError('distinct original controller birth required')
    nonce=pins['guardian_nonce']
    if not isinstance(nonce,str) or re.fullmatch('[0-9a-f]{32}',nonce) is None:raise ValueError('original controller nonce must be canonical')
    names={'receipt':nonce+'.receipt.json','stdout':nonce+'.stdout','stderr':nonce+'.stderr',
        'guardian_stdout':nonce+'.guardian.stdout','guardian_stderr':nonce+'.guardian.stderr'}
    raw={}
    for label,name in names.items():
        digest=evidence[label+'_sha256']
        if not isinstance(digest,str) or re.fullmatch('sha256:[0-9a-f]{64}',digest) is None:raise ValueError('original preconsume artifact digest required')
        path=controller/name
        try:
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
            with os.fdopen(fd,'rb') as stream:
                info=os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_uid!=pins['custody']['controller_uid'] or info.st_gid!=guardian_pin['gid'] or stat.S_IMODE(info.st_mode) not in (0o600,0o640):raise ValueError('protected original wait artifact custody required')
                raw[label]=stream.read(65537)
        except OSError:raise ValueError('original wait artifact unavailable') from None
        if len(raw[label])>65536 or 'sha256:'+hashlib.sha256(raw[label]).hexdigest()!=digest:raise ValueError('original wait artifact bytes changed')
    try:receipt=json.loads(raw['receipt'],object_pairs_hook=op._unique_object)
    except (ValueError,UnicodeError):raise ValueError('original controller wait is not authentic JSON') from None
    op._object(receipt,{'schema','task_id','identity','controller','exit_code','observed_at_utc','stdout_path','stdout_sha256','stderr_path','stderr_sha256'},'original controller wait')
    if receipt['schema']!='cdc-vps-controller-wait/v1' or receipt['task_id']!=row['task']['id'] or receipt['identity']!=pins['guardian'] or receipt['controller']!=identity or type(receipt['exit_code']) is not int or receipt['exit_code']!=2:raise ValueError('original nonce/task/birth preconsume wait mismatch')
    observed=op._timestamp(receipt['observed_at_utc'],'original controller wait time')
    if observed>datetime.now(timezone.utc)+timedelta(seconds=5):raise ValueError('original controller wait observation is in the future')
    for label in ('stdout','stderr'):
        if receipt[label+'_path']!=str(controller/names[label]) or receipt[label+'_sha256']!=evidence[label+'_sha256'].split(':',1)[1]:raise ValueError('original controller stream path/digest mismatch')
    if raw['stdout'] or raw['guardian_stdout'] or raw['guardian_stderr'] or raw['stderr']!=b'CDC_VPS_ORIGINAL_CONTROLLER_RECONCILIATION_REQUIRED\n':raise ValueError('only original preconsume controller rejection artifacts are admissible')
    _identity(identity,absent=True)
    return {str(controller/name):raw[label] for label,name in names.items()}


def _bootstrap_artifacts(row,pins,controller,guardian_pin):
    evidence=pins['guardian_bootstrap_failure']
    if 'preconsume_exit' in pins:raise ValueError('bootstrap streams cannot substitute for a controller wait')
    op._object(evidence,{'schema','stdout_sha256','stderr_sha256'},'original guardian bootstrap streams')
    if evidence['schema']!='native-guardian-bootstrap-failure/v1':raise ValueError('unsupported guardian bootstrap evidence')
    nonce=pins['guardian_nonce']
    if not isinstance(nonce,str) or re.fullmatch('[0-9a-f]{32}',nonce) is None:raise ValueError('original guardian nonce must be canonical')
    documentary={}
    for label in ('stdout','stderr'):
        path=controller/(nonce+'.guardian.'+label);digest=evidence[label+'_sha256']
        op._digest(digest,'original guardian stream digest')
        try:
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
            with os.fdopen(fd,'rb') as stream:
                info=os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_uid!=pins['custody']['controller_uid'] or info.st_gid!=guardian_pin['gid'] or stat.S_IMODE(info.st_mode) not in (0o600,0o640):raise ValueError('protected original bootstrap stream custody required')
                data=stream.read(65537)
        except OSError:raise ValueError('original guardian bootstrap stream unavailable') from None
        if len(data)>65536 or 'sha256:'+hashlib.sha256(data).hexdigest()!=digest:raise ValueError('original guardian bootstrap bytes changed')
        if label=='stdout' and data:raise ValueError('original bootstrap stdout must be empty')
        if label=='stderr':
            marker=b'ValueError: original guardian birth never persisted; no child launch\n'
            if b'\0' in data or not data.startswith(b'Traceback (most recent call last):\n') or not data.endswith(marker) or data.count(marker)!=1:raise ValueError('original no-child bootstrap traceback required')
            try:data.decode('utf-8')
            except UnicodeError:raise ValueError('original bootstrap traceback encoding invalid') from None
        documentary[str(path)]=data
    return documentary


def _preparation_receipt(store,row,pins,budget_store,history):
    """Observe an original event; this never reserves, closes or grants launch."""
    preparation=row['operation'].get('reservation_preparation')
    if preparation is None:
        if 'preparation_budget' in pins or budget_store is not None:raise ValueError('unexpected original preparation budget channel')
        return None
    op._object(preparation,{'schema','root_parent_revision','project_budget'},'original reservation preparation')
    if preparation['schema']!='cdc-vps-reservation-preparation/v1':raise ValueError('original reservation preparation schema required')
    proposal=preparation['project_budget']
    if proposal is None:
        if 'preparation_budget' in pins or budget_store is not None or 'project_budget' in row['operation']:raise ValueError('unexpected original project receipt')
        return None
    from project_budget_store import GitProjectBudgetStore
    trusted=pins.get('preparation_budget')
    op._object(trusted,{'binding','registration_digest'},'trusted original preparation budget')
    op._digest(trusted['registration_digest'],'original registration digest')
    request=row['operation']['start_request'];task=row['task'];intent=row['operation']['intent']
    if type(budget_store) is not GitProjectBudgetStore or budget_store.binding!=trusted['binding'] or budget_store.repo!=Path(request['repo_root']).resolve() or budget_store.remote!=request.get('coordination_remote',request['remote']):raise ValueError('actual original typed preparation budget required')
    binding=budget_store.binding
    if binding['repository']!=request['lease_repository'] or binding['source_ref']!=request['lease_source_ref'] or binding['coordination_store_id']!=request['plan']['coordination_store_id']:raise ValueError('original project budget/source channel mismatch')
    fields={'schema','project_id','project_task_id','root_task_id','attempt_id','operation_key','registration_digest','budget_binding_digest','start_request_digest','prepared_budget_revision','event','event_digest','authorizes_launch'}
    op._object(proposal,fields,'original project budget proposal')
    receipt=row['operation'].get('project_budget')
    op._object(receipt,fields-{'prepared_budget_revision'}|{'reservation_revision'},'original project budget receipt')
    if proposal['authorizes_launch'] is not False or receipt['authorizes_launch'] is not False:raise ValueError('original preparation never authorizes launch')
    prepared=budget_store.read_revision(proposal['prepared_budget_revision'])
    event=proposal['event']
    expected_event={'type':'reserve','event_id':'vps-'+task['id']+'-original-compute-start','task_id':binding['task_id'],
        'wake_id':prepared['wake_ids'][-1],'at_utc':event['at_utc'],'operation_key':intent['operation_key'],
        'attempt_id':request['attempt_id'],'kind':'compute_start','scope':'registered-vps-project-adoption:'+task['id'],
        'recovery_ref':None,'cost':{'tool_calls':task['budget']['tool_calls'],'tokens':None,'elapsed_seconds':task['max_runtime_seconds']}}
    expected={'schema':'cdc-vps-project-budget-preparation/v1','project_id':task['project_id'],
        'project_task_id':binding['task_id'],'root_task_id':task['id'],'attempt_id':request['attempt_id'],
        'operation_key':intent['operation_key'],'registration_digest':trusted['registration_digest'],
        'budget_binding_digest':native_digest(binding),'start_request_digest':_contract(row),
        'prepared_budget_revision':proposal['prepared_budget_revision'],'event':expected_event,
        'event_digest':native_digest(expected_event),'authorizes_launch':False}
    if proposal!=expected:raise ValueError('original prepared project event/receipt contract mismatch')
    expected_receipt=copy.deepcopy(expected);expected_receipt.update(schema='cdc-vps-original-project-budget/v1',reservation_revision=receipt['reservation_revision']);del expected_receipt['prepared_budget_revision']
    if receipt!=expected_receipt:raise ValueError('original project receipt is not the exact preparation progress')
    import budget
    if any(e.get('event_id')==event['event_id'] or (e.get('operation_key'),e.get('attempt_id'))==(event['operation_key'],event['attempt_id']) for e in prepared['events']) or not budget.decide(prepared,event)['allow_reservation']:raise ValueError('original event did not follow eligible project preparation')
    recorded=budget_store.read_revision(receipt['reservation_revision']);_,current=budget_store.read()
    for ledger in (recorded,current):
        if sum(e==event for e in ledger['events'])!=1 or any(e['type']=='outcome' and e['reservation_id']==event['event_id'] for e in ledger['events']):raise ValueError('exact original unresolved project reservation required')
    parent=preparation['root_parent_revision'];parent_row=_row(store.read_revision(parent),task['id'])
    if parent_row['state']!='queued' or parent_row['task']!=task or parent_row.get('operation') is not None or parent_row.get('result') is not None or parent_row['budget']['events']:raise ValueError('original queued preparation predecessor required')
    first=next(((revision,_row(document,task['id'])) for revision,document in history if (document.get('tasks',{}).get(task['id']) or {}).get('operation') is not None),None)
    if first is None:raise ValueError('original prepared Root row absent')
    revision,initial=first;operation=initial['operation']
    if store._git('rev-parse',revision+'^')!=parent or initial['state']!='reserved' or operation['intent']['state']!='prepared' or operation.get('guardian') is not None or 'project_budget' in operation:raise ValueError('original project preparation boundary changed')
    return {'receipt':receipt,'prepared_revision':revision,'prepared_intent':operation['intent']}


def _physical_and_artifacts(store,row,pins,source_store=None):
    request=row['operation']['start_request']
    _identity(pins['creator'],absent=True);_identity(pins['guardian'],absent=True)
    guardian=row['operation'].get('guardian')
    if not isinstance(guardian,dict) or guardian.get('nonce')!=pins['guardian_nonce'] or guardian.get('identity')!=pins['guardian']:raise ValueError('original canonical guardian nonce/identity required')
    _intake_channels(store,row,pins,source_store)
    channel=source_store or store
    if pins['pool_ref']!=request['plan']['coordination_ref'] or request['plan']['coordination_store_id']!=channel.store_id:raise ValueError('original protected pool channel mismatch')
    channel._assert_remote_identity();channel._git('check-ref-format',pins['pool_ref'])
    if channel._git('ls-remote','--refs',channel.remote,pins['pool_ref']):raise ValueError('native original pool/runtime effect already exists')
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
    if channel._git('ls-remote','--refs',channel.remote,publication_ref):raise ValueError('original publication journal already exists')
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
    documentary=(_bootstrap_artifacts(row,pins,controller,guardian_pin) if 'guardian_bootstrap_failure' in pins else _preconsume_artifacts(row,pins,controller,guardian_pin))
    seen=set();seen_documentary=set()
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
            key=str(child)
            if key in documentary:
                if child.read_bytes()!=documentary[key]:raise ValueError('original wait artifact changed during authentication')
                seen_documentary.add(key);continue
            seen.add(key);pin=allowed.get(key)
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
    if seen!=set(allowed) or seen_documentary!=set(documentary):raise ValueError('pinned original static/documentary launch artifact missing')
    _identity(pins['creator'],absent=True);_identity(pins['guardian'],absent=True)
    if 'preconsume_exit' in pins:_identity(pins['preconsume_exit']['controller'],absent=True)


def _authenticate_intake(store,task_id,source,pins,*,retired=False,project_budget_store=None):
    if type(store) is not GitDocumentStore or type(source) is not GitLeaseStore:raise ValueError('actual configured native stores required')
    required={'original_revision','row_digest','source_revision','source_digest','creator','guardian','guardian_nonce','pool_ref','launch_roots','custody'}
    if not isinstance(pins,dict) or not required<=set(pins) or set(pins)-required-{'artifact_pins','channels','preconsume_exit','guardian_bootstrap_failure','preparation_budget'}:raise ValueError('independent trusted original contract pins required')
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
    progress=_preparation_receipt(store,original_row,pins,project_budget_store,history)
    digest=_contract(original_row);seen=False;admitted=False;intent_rank=-1;receipt_seen=False;submitted=None
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
        if progress is not None:
            receipt=historical.pop('project_budget',None);canonical.pop('project_budget')
            if receipt is not None:
                if receipt!=progress['receipt']:raise ValueError('original preparation receipt history changed')
                receipt_seen=True
            elif receipt_seen:raise ValueError('original preparation receipt was removed')
            initial=progress['prepared_intent'];current_intent=historical['intent']
            if current_intent['state']=='prepared':
                if current_intent!=initial or receipt is not None or row['operation'].get('guardian') is not None:raise ValueError('original prepared progress changed')
            elif current_intent['state']=='submitting':
                at=current_intent['updated_at_utc']
                readback=op.verify_readback(initial,initial,store.ref+'@'+progress['prepared_revision']+':tasks/'+task_id+'/operation/intent',at)
                expected=op.transition(initial,'submitting',at,receipt=readback)
                if current_intent!=expected or receipt is None or submitted is not None and submitted!=current_intent:raise ValueError('original submitted preparation/readback changed')
                submitted=copy.deepcopy(current_intent)
            else:raise ValueError('original preparation intent is not monotonic')
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
    elif current!=original_row or current.get('state') not in (('unknown','starting','start_unknown','running') if 'guardian_bootstrap_failure' in pins else ('unknown','starting','start_unknown')):raise ValueError('exact original prelaunch UNKNOWN row required')
    srev,sdoc=source.read()
    if retired:
        sdoc=source.read_revision(pins['source_revision']);srev=pins['source_revision']
    if srev!=pins['source_revision'] or op._hash(sdoc)!=pins['source_digest'] or sdoc['owner_id'] is not None or sdoc['external_guard'] is not None or sdoc['repository']!=request['lease_repository'] or sdoc['source_ref']!=request['lease_source_ref']:raise ValueError('unchanged canonical absent-native source lease required')
    _intake_channels(store,original_row,pins,source)
    _physical_and_artifacts(store,original_row,pins,source)
    return revision,current


class PrelaunchIntakeDispositionProof(dict):
    """Ephemeral administrative slot custody, distinct from terminal proof."""
    def __init__(self,seal,store,task_id,source,pins,at,*,retired=False,project_budget_store=None):
        if seal is not _SEAL:raise ValueError('package issued prelaunch disposition required')
        revision,row=_authenticate_intake(store,task_id,source,pins,retired=retired,project_budget_store=project_budget_store)
        super().__init__(schema=DISPOSITION_SCHEMA,task_id=task_id,contract_digest=_contract(row),original_effect='UNKNOWN',actual_wait=None,original_revision=pins['original_revision'])
        self._evidence=copy.deepcopy(dict(self))
        self._budget=project_budget_store
        self._seal=seal;self._store=store;self._source=source;self._pins=copy.deepcopy(pins);self._at=at;self._revision=revision;self._retired=retired
    def revalidate_for(self,store,task_id):
        if dict(self)!=self._evidence:raise ValueError('native disposition evidence capability was mutated')
        if self._seal is not _SEAL or store is not self._store or task_id!=self['task_id']:raise ValueError('original native disposition endpoint/task substituted')
        return _authenticate_intake(store,task_id,self._source,self._pins,retired=self._retired,project_budget_store=self._budget)[1]


def authenticate_prelaunch_intake(store,task_id,*,source_store,trusted_contract,at,project_budget_store=None):
    op._timestamp(at,'administrative disposition time')
    return PrelaunchIntakeDispositionProof(_SEAL,store,task_id,source_store,trusted_contract,at,project_budget_store=project_budget_store)


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
    retired_proof=observe_prelaunch_intake_disposition(store,task_id,contract_digest=_contract(row),source_store=proof._source,project_budget_store=proof._budget)
    return {'revision':revision,'row':new,'proof':retired_proof}


def observe_prelaunch_intake_disposition(store,task_id,*,contract_digest,source_store=None,project_budget_store=None):
    if type(store) is not GitDocumentStore:raise ValueError('actual native intake store required')
    _,document=store.read();row=_row(document,task_id);entry=validate_prelaunch_disposition(row)
    if entry['contract_digest']!=contract_digest:raise ValueError('original disposition contract mismatch')
    if source_store is None:
        request=row['operation']['start_request']
        if entry['trusted_contract'].get('channels') is not None:
            source_store=GitLeaseStore(request['repo_root'],request.get('coordination_remote',request['remote']),request['lease_coordination_ref'])
        else:source_store=GitLeaseStore(store.repo,store.remote,request.get('lease_coordination_ref','refs/heads/cdc/source-lease'))
    if project_budget_store is None and entry['trusted_contract'].get('preparation_budget') is not None:
        from project_budget_store import GitProjectBudgetStore
        request=row['operation']['start_request']
        project_budget_store=GitProjectBudgetStore(request['repo_root'],request.get('coordination_remote',request['remote']),entry['trusted_contract']['preparation_budget']['binding'])
    return PrelaunchIntakeDispositionProof(_SEAL,store,task_id,source_store,entry['trusted_contract'],entry['retired_at_utc'],retired=True,project_budget_store=project_budget_store)


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


def _disposition_from_history(store, task_id, current, history, documents):
    entry=_validate_prelaunch_disposition_row(current)
    if entry['original_revision'] not in documents:raise ValueError('disposition original ancestry/task mismatch')
    original=_row(documents[entry['original_revision']],task_id)
    _intake_channels(store,original,entry['trusted_contract'])
    if original!=entry['original_row'] or entry['task_id']!=task_id:raise ValueError('disposition original ancestry/task mismatch')
    found=False
    for _,historical in history:
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
    return copy.deepcopy(entry)


def validate_prelaunch_dispositions(store, expected_revision, rows):
    """Authenticate selected tombstones against one fresh native history snapshot.

    Returned entries remain structural observations: no wait, terminal or send
    capability is created. The exact caller head and every supplied row must
    match the independently read native channel, including at the end.
    """
    if type(store) is not GitDocumentStore or not isinstance(rows,dict):raise ValueError('actual original native intake channel and rows required')
    history=_history(store)
    revision,document=history[-1]
    if revision!=expected_revision:raise ValueError('serialized disposition snapshot differs from authoritative head')
    documents=dict(history);result={}
    for task_id,row in rows.items():
        current=_row(document,task_id)
        if current!=row:raise ValueError('serialized disposition differs from authoritative original row')
        result[task_id]=_disposition_from_history(store,task_id,current,history,documents)
    if store.read()[0]!=revision:raise ValueError('native disposition head moved during validation')
    return result


def validate_prelaunch_disposition(store_or_row,task_id=None,row=None):
    """Original single-row API; structural form never grants native authority."""
    if task_id is None:return _validate_prelaunch_disposition_row(store_or_row)
    store=store_or_row
    if type(store) is not GitDocumentStore:raise ValueError('actual original native intake channel required')
    history=_history(store);revision,document=history[-1];current=_row(document,task_id)
    if row is not None and current!=row:raise ValueError('serialized disposition differs from authoritative original row')
    result=_disposition_from_history(store,task_id,current,history,dict(history))
    if store.read()[0]!=revision:raise ValueError('native disposition head moved during validation')
    return result


def assert_new_intake_allowed(store,task):
    if type(store) is not GitDocumentStore:raise ValueError('native intake admission store required')
    revision,document=store.read()
    retired={task_id:row for task_id,row in document['tasks'].items() if row.get('state')=='retired_unknown'}
    if retired:validate_prelaunch_dispositions(store,revision,retired)
    for task_id,row in document['tasks'].items():
        if row.get('state')=='retired_unknown':
            if semantic_intake_contract({'task':task})==semantic_intake_contract(row):raise ValueError('retired original task contract replay prohibited')
    return True
