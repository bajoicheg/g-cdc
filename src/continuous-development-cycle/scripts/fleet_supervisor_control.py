#!/usr/bin/env python3
"""Generation-fenced single-leader Fleet Supervisor state and one-shot side-effect claims."""
from __future__ import annotations
import copy,hashlib,json,re
from datetime import datetime, timedelta
import execution_lease_v2 as leasev2

SCHEMA="fleet-supervisor-state/v1"
EFFECT_SCHEMA="fleet-side-effect/v1"
KINDS={"fleet_write","project_wake","scheduler_repair","continuation_enqueue"}
EFFECT_STATES={"claimed","submitted","unknown","terminal"}
SHA=re.compile(r"^[0-9a-f]{40}$")

def _time(v,n):
    if not isinstance(v,str) or not v.endswith("Z"):raise ValueError(n+" must be UTC Z timestamp")
    try:return datetime.fromisoformat(v[:-1]+"+00:00")
    except ValueError as e:raise ValueError(n+" invalid timestamp") from e

def _text(v,n):
    if not isinstance(v,str) or not v.strip():raise ValueError(n+" invalid")

def _digest(v):
    raw=json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode("utf-8")
    return "sha256:"+hashlib.sha256(raw).hexdigest()

def initialize(fleet_repository,fleet_ref):
    _text(fleet_repository,"fleet_repository")
    if not isinstance(fleet_ref,str) or not fleet_ref.startswith("refs/heads/"):raise ValueError("fleet_ref invalid")
    return {"schema":SCHEMA,"fleet_repository":fleet_repository,"fleet_ref":fleet_ref,
            "lease":leasev2.initialize(fleet_repository,fleet_ref),"effects":[]}

def validate_effect(e):
    fields={"schema","effect_id","kind","target","intent_digest","owner_id","generation","invocation_id",
            "observed_fleet_head","state","claimed_at_utc","receipt_ref","outcome"}
    if not isinstance(e,dict) or set(e)!=fields or e.get("schema")!=EFFECT_SCHEMA:raise ValueError("fleet effect invalid")
    for n in ("effect_id","target","owner_id","invocation_id","intent_digest"):_text(e[n],n)
    if e["kind"] not in KINDS:raise ValueError("effect kind invalid")
    if e["state"] not in EFFECT_STATES:raise ValueError("effect state invalid")
    if type(e["generation"]) is not int or e["generation"]<1:raise ValueError("effect generation invalid")
    if not SHA.fullmatch(e["observed_fleet_head"]):raise ValueError("effect observed fleet head invalid")
    _time(e["claimed_at_utc"],"effect claimed_at_utc")
    if e["receipt_ref"] is not None:_text(e["receipt_ref"],"receipt_ref")
    if e["outcome"] is not None:_text(e["outcome"],"outcome")
    if e["state"]=="claimed" and (e["receipt_ref"] is not None or e["outcome"] is not None):raise ValueError("claimed effect cannot have receipt/outcome")
    if e["state"]=="submitted" and e["receipt_ref"] is None:raise ValueError("submitted effect requires receipt")
    if e["state"]=="unknown" and e["receipt_ref"] is None:raise ValueError("unknown effect requires attempted-effect receipt")
    if e["state"]=="terminal" and (e["receipt_ref"] is None or e["outcome"] is None):raise ValueError("terminal effect requires receipt/outcome")
    return e

def validate(state):
    if not isinstance(state,dict) or set(state)!={"schema","fleet_repository","fleet_ref","lease","effects"} or state.get("schema")!=SCHEMA:
        raise ValueError("fleet supervisor state invalid")
    _text(state["fleet_repository"],"fleet_repository")
    if not isinstance(state["fleet_ref"],str) or not state["fleet_ref"].startswith("refs/heads/"):raise ValueError("fleet_ref invalid")
    leasev2.validate(state["lease"])
    if state["lease"]["repository"]!=state["fleet_repository"] or state["lease"]["source_ref"]!=state["fleet_ref"]:
        raise ValueError("fleet leader lease binding mismatch")
    if not isinstance(state["effects"],list):raise ValueError("effects invalid")
    ids=set()
    for e in state["effects"]:
        validate_effect(e)
        if e["effect_id"] in ids:raise ValueError("duplicate fleet effect id")
        ids.add(e["effect_id"])
    return state

def _leader(state,owner_id,generation,invocation_id,at,freshness_seconds=600):
    validate(state);lease=state["lease"]
    if lease["owner_id"]!=owner_id or lease["generation"]!=generation:raise ValueError("not fleet leader")
    if lease["invocation"] is None or lease["invocation"]["invocation_id"]!=invocation_id:raise ValueError("fleet leader invocation mismatch")
    if lease["finalization"]["state"]!="active":raise ValueError("fleet leader not active")
    now=_time(at,"at");heartbeat=_time(lease["heartbeat_at_utc"],"heartbeat");expiry=_time(lease["expires_at_utc"],"expiry")
    if now>=expiry or (now-heartbeat).total_seconds()>=freshness_seconds:raise ValueError("fleet leader lease not fresh")
    return lease

def _unresolved_effects(state,generation):
    return [e for e in state["effects"] if e["generation"]==generation and e["state"]!="terminal"]

def acquire_record(state,owner_id,at,invocation,*,ttl=1200,quiescence=None):
    validate(state);old=state["lease"]
    if old["owner_id"] is not None and _unresolved_effects(state,old["generation"]):
        raise ValueError("prior fleet leader has unresolved side effects")
    result=copy.deepcopy(state)
    result["lease"]=leasev2.acquire(old,owner_id,at,invocation=invocation,ttl=ttl,quiescence=quiescence)
    return validate(result)

def acquire_cas(store,expected_revision,fleet_repository,fleet_ref,owner_id,at,invocation,*,ttl=1200,quiescence=None):
    revision,state=store.read()
    if revision!=expected_revision:raise ValueError("stale fleet supervisor revision")
    if state is None:state=initialize(fleet_repository,fleet_ref)
    validate(state)
    if state["fleet_repository"]!=fleet_repository or state["fleet_ref"]!=fleet_ref:raise ValueError("fleet supervisor endpoint binding mismatch")
    result=acquire_record(state,owner_id,at,invocation,ttl=ttl,quiescence=quiescence)
    new_revision=store.compare_and_swap(expected_revision,result)
    return {"revision":new_revision,"state":result,"owner_id":owner_id,"generation":result["lease"]["generation"]}

def claim_effect_record(state,owner_id,generation,invocation_id,at,live_fleet_head,request):
    _leader(state,owner_id,generation,invocation_id,at)
    if not SHA.fullmatch(live_fleet_head):raise ValueError("live fleet head invalid")
    fields={"effect_id","kind","target","observed_fleet_head","intent"}
    if not isinstance(request,dict) or set(request)!=fields:raise ValueError("effect request invalid")
    for n in ("effect_id","target"):_text(request[n],n)
    if request["kind"] not in KINDS:raise ValueError("effect kind invalid")
    if not SHA.fullmatch(request["observed_fleet_head"]):raise ValueError("request fleet head invalid")
    intent_digest=_digest(request)
    for e in state["effects"]:
        if e["effect_id"]==request["effect_id"]:
            if e["intent_digest"]!=intent_digest:raise ValueError("fleet effect id collision")
            return copy.deepcopy(state),{"action":"OBSERVE_EXISTING","authorizes_effect":False,"effect":copy.deepcopy(e)}
    if request["observed_fleet_head"]!=live_fleet_head:
        return copy.deepcopy(state),{"action":"REPLAN_FLEET_HEAD","authorizes_effect":False,"effect":None}
    result=copy.deepcopy(state)
    effect={"schema":EFFECT_SCHEMA,"effect_id":request["effect_id"],"kind":request["kind"],"target":request["target"],
            "intent_digest":intent_digest,"owner_id":owner_id,"generation":generation,"invocation_id":invocation_id,
            "observed_fleet_head":live_fleet_head,"state":"claimed","claimed_at_utc":at,"receipt_ref":None,"outcome":None}
    result["effects"].append(effect);validate(result)
    return result,{"action":"SUBMIT_ONCE","authorizes_effect":True,"effect":copy.deepcopy(effect)}

def claim_effect_cas(store,expected_revision,owner_id,generation,invocation_id,at,live_fleet_head,request):
    revision,state=store.read()
    if revision!=expected_revision or state is None:raise ValueError("stale fleet supervisor revision")
    result,decision=claim_effect_record(state,owner_id,generation,invocation_id,at,live_fleet_head,request)
    if decision["action"]!="SUBMIT_ONCE":return {"revision":revision,"state":state,**decision}
    new_revision=store.compare_and_swap(expected_revision,result)
    return {"revision":new_revision,"state":result,**decision}

def update_effect_record(state,owner_id,generation,invocation_id,at,effect_id,new_state,receipt_ref,outcome=None):
    _leader(state,owner_id,generation,invocation_id,at)
    if new_state not in {"submitted","unknown","terminal"}:raise ValueError("effect transition invalid")
    result=copy.deepcopy(state);match=None
    for e in result["effects"]:
        if e["effect_id"]==effect_id:match=e;break
    if match is None:raise ValueError("effect not found")
    if match["owner_id"]!=owner_id or match["generation"]!=generation or match["invocation_id"]!=invocation_id:
        raise ValueError("effect not owned by exact leader")
    if match["state"]=="terminal":raise ValueError("terminal effect immutable")
    _text(receipt_ref,"receipt_ref")
    if new_state=="terminal":_text(outcome,"outcome")
    elif outcome is not None:raise ValueError("nonterminal effect cannot have outcome")
    match["state"]=new_state;match["receipt_ref"]=receipt_ref;match["outcome"]=outcome
    validate(result);return result

def assess_takeover(state):
    validate(state);lease=state["lease"]
    if lease["owner_id"] is None:return {"action":"ACQUIRE_FREE","pending_effects":[],"authorizes_takeover":False}
    pending=_unresolved_effects(state,lease["generation"])
    if pending:return {"action":"BLOCK_PENDING_EFFECTS","pending_effects":[e["effect_id"] for e in pending],"authorizes_takeover":False}
    return {"action":"REQUIRE_EXECUTOR_STOPPED_EVIDENCE","pending_effects":[],"authorizes_takeover":False}
