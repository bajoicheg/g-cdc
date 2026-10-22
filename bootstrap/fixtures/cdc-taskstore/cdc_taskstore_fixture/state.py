"""Unmodified pinned TaskStore read-method closure; no host policy or effects."""
import copy
import hashlib
import json
import time
import threading
from collections import namedtuple
from datetime import datetime
from . import runtime
from .policy import fields, identifier, validate_registry, validate_task, project_for, SHA

ACTIVE = {'reserved', 'running', 'unknown', 'terminal_pending'}

_RetiredObservation = namedtuple('_RetiredObservation', 'owner context revision rows chain ids')


def digest(value):
    return 'sha256:' + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


class TaskStore:
    def __init__(self, backend, registry, *, runtime_tree=None):
        from .kimi import OLD_TREE
        if runtime_tree is not None and (runtime_tree != OLD_TREE or len(registry.get('executors', [])) != 2):
            raise ValueError('only exact previous two-row registry pin may be observed')
        self.backend = backend
        self.registry = copy.deepcopy(validate_registry(registry, runtime_tree=runtime_tree))
        self._observation_owner = object()
        self._retired_observation = None
        self._history_lock = threading.RLock()
        self._preparation_cache = None

    def _observation_context(self):
        backend = self.backend
        if type(backend) is not runtime.module('git_document_store').GitDocumentStore:
            raise ValueError('actual original native intake channel required')
        return (id(backend), str(backend.repo.resolve()), backend.remote, backend.ref,
                backend.store_id, digest(self.registry))

    @staticmethod
    def _retired_rows(document):
        return {key: row for key, row in document['tasks'].items()
                if row['state'] == 'retired_unknown' or (row.get('result') or {}).get('unstarted_cancellation') is not None}

    def _fresh_parent_chain(self, revision):
        backend = self.backend
        if backend._git('rev-parse', '--is-shallow-repository') != 'false':
            raise ValueError('complete native history required')
        rows = backend._git('rev-list', '--parents', revision).splitlines()
        if len(rows) > 10000:raise ValueError('native history exceeds authentication bound')
        chain = tuple(tuple(row) for row in runtime.module('immutable_history_cache')._linear_chain(reversed(rows)))
        if not chain or chain[-1][0] != revision:raise ValueError('complete native history required')
        return chain

    def _validate_retired(self, revision, retired, *, preparation_task_id=None):
        with self._history_lock:
            return self._validate_retired_once(revision, retired, preparation_task_id=preparation_task_id)

    def _validate_retired_once(self, revision, retired, *, preparation_task_id=None):
        prior = self._retired_observation
        projection = None
        context = self._observation_context()
        chain = self._fresh_parent_chain(revision)
        rows = digest(retired)
        owned = (type(prior) is _RetiredObservation and prior.owner is self._observation_owner
                 and prior.context == context)
        if owned and chain[:len(prior.chain)] != prior.chain:
            if self.backend._remote_revision() != revision:
                raise ValueError('native disposition head moved during validation')
            raise ValueError('native history rewound or rewritten')
        if owned:
            if not prior.ids <= retired.keys() or digest({key:retired[key] for key in prior.ids}) != prior.rows:
                raise ValueError('native tombstone history changed or removed')
            added = {}
            for parts in chain[len(prior.chain):]:
                value = self.backend._read_document_object(parts[0])
                historical = self._retired_rows(value)
                runtime.module('unknown_recovery').assert_intake_disposition_replay_absent(value)
                if (not prior.ids <= historical.keys()
                    or digest({key:historical[key] for key in prior.ids}) != prior.rows
                    or any(key not in historical or digest(historical[key]) != expected for key,expected in added.items())):
                    raise ValueError('native tombstone history changed, removed or rearmed')
                for key,row in historical.items():
                    if key not in prior.ids:added[key] = digest(row)
            if set(added) != retired.keys() - prior.ids:
                raise ValueError('native disposition snapshot differs from authenticated history')
        if not owned or rows != prior.rows:
            # New instances/contexts and newly introduced tombstones retain
            # the complete released native authenticator. Cached data is never
            # a disposition, start or terminal capability.
            recovery = runtime.module('unknown_recovery')
            retired_rows = {key:row for key,row in retired.items() if row['state']=='retired_unknown'}
            cancelled_rows = {key:row for key,row in retired.items() if row['state']=='cancelled'}
            if preparation_task_id is None:
                recovery.validate_intake_dispositions(self.backend, revision, retired_rows, cancelled_rows)
            else:
                _, projection = recovery.validate_intake_dispositions_projecting(
                    self.backend, revision, retired_rows, cancelled_rows, preparation_task_id)
            if self._fresh_parent_chain(revision) != chain:
                raise ValueError('native history changed during observation')
        if self.backend._remote_revision() != revision:
            raise ValueError('native disposition head moved during validation')
        self._retired_observation = _RetiredObservation(self._observation_owner, context, revision, rows, chain, frozenset(retired))
        if projection is not None:
            self._remember_preparation_projection(preparation_task_id, projection)

    def _remember_preparation_projection(self, task_id, projection):
        """Seed only existing bounded DATA cache after complete native verification."""
        if (projection['task_id'] != task_id or projection['revision'] != self._retired_observation.revision
                or tuple(tuple(parts) for parts in projection['chain']) != self._retired_observation.chain):
            raise ValueError('preparation projection differs from authenticated history')
        document = projection['documents'][-1][1]
        try:
            context = self._preparation_context(task_id, document)
        except (KeyError, TypeError, AttributeError):
            return  # No usable preparation binding; original path remains authoritative.
        history_cache = runtime.module('immutable_history_cache')
        if self._preparation_cache is None:
            self._preparation_cache = history_cache._HistoryCache(max_entries=4)
        self._preparation_cache.put(context, {'chain':projection['chain'], 'documents':projection['documents']})

    def read(self, *, preparation_task_id=None):
        # The complete operation is observational. Never retry _commit or any
        # caller's mutation when the final head/ancestry check moves.
        moves = {'coordination ref moved during read', 'native history moved during authentication',
                 'serialized disposition snapshot differs from authoritative head',
                 'native disposition head moved during validation'}
        for ordinal in range(3):
            try:
                return self._read_once() if preparation_task_id is None else self._read_once(preparation_task_id=preparation_task_id)
            except Exception as error:
                # Read errors grant nothing. Retain the last immutable prefix
                # so repeated tampering cannot erase its tombstone anchor.
                if not isinstance(error, ValueError) or str(error) not in moves or ordinal == 2: raise
                time.sleep(.25)

    def _read_once(self, *, preparation_task_id=None):
        revision, value = self.backend.read()
        if value is None or value.get('schema') != 'cdc-vps-control/v1' or value.get('registry_digest') != digest(self.registry):
            raise ValueError('production bootstrap/registry missing or changed; observer-only')
        runtime.module('continuation_queue').validate_queue(value['queue'])
        fields(value,'schema registry_digest created_at_utc tasks queue','control document')
        if not isinstance(value['tasks'],dict):raise ValueError('task index required')
        retired = {}
        cancelled = {}
        for task_id,row in value['tasks'].items():
            identifier(task_id);fields(row,'task state operation result budget','task row')
            from .kimi import validate_launch_task
            validate_launch_task(row['task'], self.registry)
            runtime.module('budget').validate_ledger(row['budget'])
            if row['task']['id']!=task_id or row['state'] not in ACTIVE|{'queued','succeeded','failed','cancelled','timed_out','retired_unknown'}:
                raise ValueError('immutable task index/state mismatch')
            operation=row['operation']
            if row['state']=='cancelled' and operation is None:
                runtime.module('unknown_recovery').validate_queued_cancellation(row)
                cancelled[task_id] = row
            elif row['state']=='queued':
                if operation is not None or row['result'] is not None or row['budget']['events']:
                    raise ValueError('queued task cannot erase original admission')
            else:
                if not isinstance(operation,dict) or digest(operation['start_request'])!=operation['start_request_digest']:
                    raise ValueError('original native admission required')
                if operation['attempt_id']!=task_id+'-a1' or operation['executor'] not in {e['name'] for e in self.registry['executors']}:
                    raise ValueError('original task/attempt/executor drift')
                runtime.module('operation_intent').validate_intent(operation['intent'])
                if operation.get('ci') is not None:
                    from . import ci
                    attempt=operation['ci'];binding=attempt['binding']
                    if (binding!=ci.request_binding(row['task'],binding['source_sha'],binding['workflow_sha'])
                        or (row['task']['role']!='writer' and binding['source_sha']!=row['task']['source_sha'])
                        or attempt['state'] not in {'prepared','submitting','submitted','unknown','accepted','terminal','not_submitted'}):
                        raise ValueError('original CI task/source/custody binding changed')
                    intent=attempt['intent']
                    runtime.module('operation_intent').validate_intent(intent)
                    if (intent['binding']!=binding['intent_binding'] or intent['attempt_id']!=binding['attempt_id']
                        or intent['source_ref']!=project_for(self.registry,row['task']['project_id'])['source_ref']):
                        raise ValueError('native CI intent binding drift')
                    charges=[e for e in row['budget']['events'] if e['type']=='reserve' and e['kind']=='ci_start']
                    if (len(charges)!=1 or charges[0]['operation_key']!=binding['operation_key']
                        or charges[0]['attempt_id']!=binding['attempt_id']):raise ValueError('original one-CI budget charge missing')
                    if attempt['state']=='not_submitted':
                        self.validate_no_send(task_id,attempt)
                    elif attempt.get('guard_reconciled') is True and (intent['state']!='terminal' or not attempt.get('receipt_ref')):
                        raise ValueError('terminal CI intent and durable receipt required')
                if not row['budget']['events']:raise ValueError('original charged budget required')
                if row['state']=='retired_unknown':
                    retired[task_id] = row
                elif row['state']=='cancelled' and (row.get('result') or {}).get('unstarted_cancellation') is not None:
                    runtime.module('unknown_recovery').validate_queued_cancellation(row)
                    cancelled[task_id] = row
                elif row['state'] not in ACTIVE:
                    proof=(row['result'] or {}).get('native_terminal',{})
                    if proof.get('task_id')!=task_id or proof.get('attempt_id')!=operation['attempt_id'] or proof.get('status')!=row['state']:
                        raise ValueError('terminal task identity/status proof missing')
        if retired or cancelled or self._retired_observation is not None:
            if preparation_task_id is None:
                self._validate_retired(revision, {**retired, **cancelled})
            else:
                self._validate_retired(revision, {**retired, **cancelled}, preparation_task_id=preparation_task_id)
            runtime.module('unknown_recovery').assert_intake_disposition_replay_absent(value)
        else:
            self._retired_observation = None
        return revision, value

    def _preparation_context(self, task_id, document):
        return {'native':self._observation_context(), 'owner':id(self._observation_owner),
                'task_id':task_id, 'parent':document['tasks'][task_id]['operation']['reservation_preparation']['root_parent_revision']}

    def validate_no_send(self, task_id, attempt):
        """Authenticate durable negative evidence; it grants no effect permission."""
        from . import ci
        prefix='refs/heads/cdc/controller-ci-results/'+task_id
        reference=attempt.get('receipt_ref','')
        revision=reference.removeprefix(prefix+'@').removesuffix(':document.json')
        if (reference!=prefix+'@'+revision+':document.json' or not ci.SHA.fullmatch(revision)
            or attempt.get('guard_reconciled') is not True or attempt['intent']['state']!='prepared'
            or attempt.get('run_id') is not None or attempt.get('submitted_at') is not None):
            raise ValueError('original prepared no-send proof required')
        receipts=runtime.module('git_document_store').GitDocumentStore(self.backend.repo,self.backend.remote,
            prefix,self.backend.store_id,protected_refs=[self.backend.ref])
        head,_=receipts.read();document=receipts.read_revision(revision)
        if (head is None or document['schema']!='cdc-controller-ci-no-send/v1' or document['binding']!=attempt['binding']
            or document['actor']!=attempt['actor'] or document['disposition']!=attempt['no_send_disposition']):
            raise ValueError('original cloud no-send receipt differs')
        project=next(p for p in self.registry['projects'] if ci.PROFILES.get(p['id'],(None,))[0]
            and p['repository']==attempt['binding']['intent_binding']['repository'])
        leases=runtime.module('git_lease_store').GitLeaseStore(self.backend.repo,self.backend.remote,project['lease_ref'])
        _,current_lease=leases.read()
        if (any(c['operation_key']==attempt['binding']['operation_key'] for c in current_lease['submission_claims'])
            or (current_lease.get('external_guard') is not None
                and current_lease['external_guard']['operation_key']==attempt['binding']['operation_key'])):
            raise ValueError('original CI submission was consumed or armed; no no-send disposition')
        lease=leases.read_revision(document['original_lease_revision'])
        session=document['session']
        _,control=self.backend.read();operation=control['tasks'][task_id]['operation']
        if (session['task_id']!=task_id or session['attempt_id']!=operation['attempt_id']
            or session['owner_id']!=operation['start_request']['owner_id']):
            raise ValueError('original no-send parent task/attempt/owner differs')
        if (document['original_lease_ref']!=project['lease_ref'] or lease['repository']!=project['repository']
            or lease['source_ref']!=project['source_ref'] or lease['owner_id']!=session['owner_id']
            or lease['generation']!=session['generation'] or lease['invocation']['invocation_id']!=session['invocation_id']):
            raise ValueError('original native no-send lease binding differs')
        original=copy.deepcopy(attempt);original.update(state='prepared')
        observed=ci.no_send_disposition(original,lease,document['request'],document['observation'],session)
        if observed!=document['disposition']:raise ValueError('original native no-send disposition differs')
        return document

