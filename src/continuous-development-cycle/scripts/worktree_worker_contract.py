#!/usr/bin/env python3
"""CDC 2.10.2 durable per-wave isolated worker/worktree assignment contract."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
from parallel_task_planner import validate as validate_parallel_plan, plan as build_parallel_plan, validate_write_path, overlaps, canonical_plan_ref

SCHEMA="worktree-worker-contract/v1";SHA=re.compile(r"^[0-9a-f]{40}$");PLAN_REF=re.compile(r"^sha256:[0-9a-f]{64}$");ROLES={"writer","read_only","review"}

def _text(v,n):
    if not isinstance(v,str) or not v.strip():raise ValueError(f"{n} must be nonempty text")
def _refs(v,n,allow_empty=False):
    if not isinstance(v,list) or any(not isinstance(x,str) or not x.strip() for x in v):raise ValueError(f"{n} invalid")
    if not allow_empty and not v:raise ValueError(f"{n} must not be empty")
    if len(v)!=len(set(v)):raise ValueError(f"{n} contains duplicates")
def validate(d):
    fields={"schema","change_id","plan_ref","plan","wave","base_sha","prior_wave_integration","integrator_id","shared_branch","assignments"}
    if not isinstance(d,dict) or set(d)!=fields or d.get("schema")!=SCHEMA:
        raise ValueError("worker contract fields/schema mismatch")
    for n in ("change_id","integrator_id","shared_branch"):_text(d[n],n)
    if not isinstance(d["plan_ref"],str) or not PLAN_REF.fullmatch(d["plan_ref"]):raise ValueError("plan_ref must be content-addressed")
    if type(d["wave"]) is not int or d["wave"]<1:raise ValueError("wave invalid")
    if not isinstance(d["base_sha"],str) or not SHA.fullmatch(d["base_sha"]):raise ValueError("base_sha invalid")

    plan=validate_parallel_plan(d["plan"])
    if d["plan_ref"]!=canonical_plan_ref(plan):raise ValueError("embedded plan does not match durable plan_ref")
    if plan["change_id"]!=d["change_id"]:raise ValueError("plan change mismatch")
    if plan["integrator_id"]!=d["integrator_id"]:raise ValueError("plan integrator mismatch")
    if plan["shared_branch"]!=d["shared_branch"]:raise ValueError("plan shared branch mismatch")
    planned=build_parallel_plan(plan)
    if d["wave"]>len(planned["waves"]):raise ValueError("wave not present in plan")
    planned_wave=planned["waves"][d["wave"]-1]
    planned_ids=set(planned_wave["task_ids"])
    prior=d["prior_wave_integration"]
    if d["wave"]==1:
        if prior is not None:raise ValueError("first wave cannot have prior integration")
        if d["base_sha"]!=plan["base_sha"]:raise ValueError("first wave base must match plan base")
    else:
        if not isinstance(prior,dict) or set(prior)!={"wave","integrated_head","evidence_ref"}:raise ValueError("later wave requires prior integration proof")
        if type(prior["wave"]) is not int or prior["wave"]!=d["wave"]-1:raise ValueError("prior integration wave mismatch")
        if not isinstance(prior["integrated_head"],str) or not SHA.fullmatch(prior["integrated_head"]):raise ValueError("prior integrated_head invalid")
        _text(prior["evidence_ref"],"prior integration evidence_ref")
        if d["base_sha"]!=prior["integrated_head"]:raise ValueError("later wave base must equal prior integrated head")

    if not isinstance(d["assignments"],list) or not d["assignments"]:raise ValueError("assignments required")
    if {a.get("task_id") for a in d["assignments"]}!=planned_ids:
        raise ValueError("assignments must exactly match planned wave")
    plan_tasks={t["id"]:t for t in plan["tasks"]}

    seen={k:set() for k in ("worker","task","branch","worktree")}
    writers=[]
    for i,a in enumerate(d["assignments"]):
        fields={"worker_id","task_id","role","branch","worktree_id","base_sha","write_paths","expected_outputs","expected_evidence","can_write_shared_branch"}
        if not isinstance(a,dict) or set(a)!=fields:raise ValueError("assignment fields mismatch")
        for n in ("worker_id","task_id","branch","worktree_id"):_text(a[n],f"assignment[{i}].{n}")
        if a["worker_id"]==d["integrator_id"]:raise ValueError("integrator cannot be delegated worker")
        if a["role"] not in ROLES:raise ValueError("assignment role invalid")
        if not isinstance(a["base_sha"],str) or not SHA.fullmatch(a["base_sha"]) or a["base_sha"]!=d["base_sha"]:raise ValueError("assignment base mismatch")
        if a["branch"]==d["shared_branch"]:raise ValueError("worker branch cannot be shared branch")
        if type(a["can_write_shared_branch"]) is not bool or a["can_write_shared_branch"]:raise ValueError("worker shared-branch write forbidden")
        _refs(a["expected_outputs"],"expected_outputs");_refs(a["expected_evidence"],"expected_evidence")
        if not isinstance(a["write_paths"],list):raise ValueError("write_paths invalid")
        for p in a["write_paths"]:validate_write_path(p)
        if len(a["write_paths"])!=len(set(a["write_paths"])):raise ValueError("duplicate write path")
        if a["role"]=="writer" and not a["write_paths"]:raise ValueError("writer requires write_paths")
        if a["role"]!="writer" and a["write_paths"]:raise ValueError("non-writer write_paths forbidden")

        pt=plan_tasks[a["task_id"]]
        if a["role"]!=pt["role"]:raise ValueError("assignment role differs from plan")
        if set(a["write_paths"])!=set(pt["write_paths"]):raise ValueError("assignment write set differs from plan")
        if set(a["expected_outputs"])!=set(pt["expected_outputs"]):raise ValueError("assignment outputs differ from plan")
        if set(a["expected_evidence"])!=set(pt["expected_evidence"]):raise ValueError("assignment evidence differs from plan")

        for key,val in (("worker",a["worker_id"]),("task",a["task_id"]),("branch",a["branch"]),("worktree",a["worktree_id"])):
            if val in seen[key]:raise ValueError("duplicate "+key+" assignment")
            seen[key].add(val)
        if a["role"]=="writer":writers.append(a)

    for i,a in enumerate(writers):
        for b in writers[i+1:]:
            if any(overlaps(x,y) for x in a["write_paths"] for y in b["write_paths"]):
                raise ValueError("same-wave writer path overlap")
    return d

def assess(d):
    validate(d)
    return {"schema":"worktree-worker-contract-result/v1","valid":True,"wave":d["wave"],"assignment_count":len(d["assignments"]),
            "base_sha":d["base_sha"],"plan_ref":d["plan_ref"],"integrator_id":d["integrator_id"],"shared_branch":d["shared_branch"],
            "authorizes_worker_launch":False,"authorizes_shared_branch_write":False,
            "authorizes_merge":False,"authorizes_release":False,"authorizes_scope_expansion":False}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("input");a=p.parse_args(argv)
    try:r=assess(json.loads(Path(a.input).read_text()))
    except (OSError,ValueError,json.JSONDecodeError) as e:print(f"FAIL: {e}",file=sys.stderr);return 2
    print(json.dumps(r,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
