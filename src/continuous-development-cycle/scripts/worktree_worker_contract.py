#!/usr/bin/env python3
"""CDC 2.10.2 durable isolated worker/worktree assignment contract."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
SCHEMA="worktree-worker-contract/v1";SHA=re.compile(r"^[0-9a-f]{40}$");ROLES={"writer","read_only","review"}

def _text(v,n):
    if not isinstance(v,str) or not v.strip():raise ValueError(f"{n} must be nonempty text")
def _refs(v,n,allow_empty=False):
    if not isinstance(v,list) or any(not isinstance(x,str) or not x.strip() for x in v):raise ValueError(f"{n} invalid")
    if not allow_empty and not v:raise ValueError(f"{n} must not be empty")
    if len(v)!=len(set(v)):raise ValueError(f"{n} contains duplicates")
def overlap(a,b):
    a=a.rstrip("/");b=b.rstrip("/")
    return a==b or a.startswith(b+"/") or b.startswith(a+"/")
def validate(d):
    if not isinstance(d,dict) or set(d)!={"schema","change_id","base_sha","integrator_id","shared_branch","assignments"} or d.get("schema")!=SCHEMA:
        raise ValueError("worker contract fields/schema mismatch")
    for n in ("change_id","integrator_id","shared_branch"):_text(d[n],n)
    if not isinstance(d["base_sha"],str) or not SHA.fullmatch(d["base_sha"]):raise ValueError("base_sha invalid")
    if not isinstance(d["assignments"],list) or not d["assignments"]:raise ValueError("assignments required")
    seen={k:set() for k in ("worker","task","branch","worktree")}
    writers=[]
    for i,a in enumerate(d["assignments"]):
        fields={"worker_id","task_id","role","wave","branch","worktree_id","base_sha","write_paths","expected_outputs","expected_evidence","can_write_shared_branch"}
        if not isinstance(a,dict) or set(a)!=fields:raise ValueError("assignment fields mismatch")
        for n in ("worker_id","task_id","branch","worktree_id"):_text(a[n],f"assignment[{i}].{n}")
        if a["worker_id"]==d["integrator_id"]:raise ValueError("integrator cannot be delegated worker")
        if a["role"] not in ROLES:raise ValueError("assignment role invalid")
        if type(a["wave"]) is not int or a["wave"]<1:raise ValueError("assignment wave invalid")
        if not isinstance(a["base_sha"],str) or not SHA.fullmatch(a["base_sha"]) or a["base_sha"]!=d["base_sha"]:raise ValueError("assignment base mismatch")
        if a["branch"]==d["shared_branch"]:raise ValueError("worker branch cannot be shared branch")
        if type(a["can_write_shared_branch"]) is not bool or a["can_write_shared_branch"]:raise ValueError("worker shared-branch write forbidden")
        _refs(a["expected_outputs"],"expected_outputs");_refs(a["expected_evidence"],"expected_evidence")
        if not isinstance(a["write_paths"],list):raise ValueError("write_paths invalid")
        if a["role"]=="writer" and not a["write_paths"]:raise ValueError("writer requires write_paths")
        if a["role"]!="writer" and a["write_paths"]:raise ValueError("non-writer write_paths forbidden")
        for key,val in (("worker",a["worker_id"]),("task",a["task_id"]),("branch",a["branch"]),("worktree",a["worktree_id"])):
            if val in seen[key]:raise ValueError("duplicate "+key+" assignment")
            seen[key].add(val)
        if a["role"]=="writer":writers.append(a)
    for i,a in enumerate(writers):
        for b in writers[i+1:]:
            if a["wave"]==b["wave"] and any(overlap(x,y) for x in a["write_paths"] for y in b["write_paths"]):
                raise ValueError("same-wave writer path overlap")
    return d
def assess(d):
    validate(d)
    return {"schema":"worktree-worker-contract-result/v1","valid":True,"assignment_count":len(d["assignments"]),
            "integrator_id":d["integrator_id"],"shared_branch":d["shared_branch"],
            "authorizes_worker_launch":False,"authorizes_shared_branch_write":False,
            "authorizes_merge":False,"authorizes_release":False,"authorizes_scope_expansion":False}
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("input");a=p.parse_args(argv)
    try:r=assess(json.loads(Path(a.input).read_text()))
    except (OSError,ValueError,json.JSONDecodeError) as e:print(f"FAIL: {e}",file=sys.stderr);return 2
    print(json.dumps(r,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
