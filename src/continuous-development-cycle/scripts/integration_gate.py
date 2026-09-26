#!/usr/bin/env python3
"""CDC 2.10.2 per-wave single-integrator evidence gate for isolated worker results."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
SCHEMA="integration-gate/v1";SHA=re.compile(r"^[0-9a-f]{40}$");ROLES={"writer","read_only","review"};STATES={"success","failed","stale"}

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
    fields={"schema","change_id","wave","integrator_id","shared_branch","expected_shared_head","observed_shared_head",
            "worker_results","spec_compliance_green","code_quality_green","unresolved_conflicts",
            "force_push_requested","verification_refs"}
    if not isinstance(d,dict) or set(d)!=fields or d.get("schema")!=SCHEMA:raise ValueError("integration gate fields/schema mismatch")
    for n in ("change_id","integrator_id","shared_branch"):_text(d[n],n)
    if type(d["wave"]) is not int or d["wave"]<1:raise ValueError("wave invalid")
    for n in ("expected_shared_head","observed_shared_head"):
        if not isinstance(d[n],str) or not SHA.fullmatch(d[n]):raise ValueError(n+" invalid")
    for n in ("spec_compliance_green","code_quality_green","force_push_requested"):
        if type(d[n]) is not bool:raise ValueError(n+" must be boolean")
    _refs(d["verification_refs"],"verification_refs")
    _refs(d["unresolved_conflicts"],"unresolved_conflicts",allow_empty=True)
    if not isinstance(d["worker_results"],list) or not d["worker_results"]:raise ValueError("worker_results required")
    seen_workers=set();seen_tasks=set()
    for i,r in enumerate(d["worker_results"]):
        f={"worker_id","task_id","role","base_sha","result_sha","state","changed_paths","evidence_refs"}
        if not isinstance(r,dict) or set(r)!=f:raise ValueError("worker result fields mismatch")
        for n in ("worker_id","task_id"):_text(r[n],f"worker[{i}].{n}")
        if r["worker_id"] in seen_workers or r["task_id"] in seen_tasks:raise ValueError("duplicate worker/task result")
        seen_workers.add(r["worker_id"]);seen_tasks.add(r["task_id"])
        if r["role"] not in ROLES or r["state"] not in STATES:raise ValueError("worker role/state invalid")
        for n in ("base_sha","result_sha"):
            if not isinstance(r[n],str) or not SHA.fullmatch(r[n]):raise ValueError("worker SHA invalid")
        _refs(r["evidence_refs"],"worker evidence")
        if not isinstance(r["changed_paths"],list) or any(not isinstance(x,str) or not x.strip() for x in r["changed_paths"]):raise ValueError("changed_paths invalid")
        if r["role"]!="writer" and r["changed_paths"]:raise ValueError("non-writer changed paths forbidden")
    return d
def evaluate(d):
    validate(d);b=[];base=d["expected_shared_head"]
    if d["observed_shared_head"]!=base:b.append("shared_head_moved_reconcile_required")
    if d["force_push_requested"]:b.append("force_push_forbidden")
    if not d["spec_compliance_green"]:b.append("spec_compliance_not_green")
    if not d["code_quality_green"]:b.append("code_quality_not_green")
    if d["unresolved_conflicts"]:b.append("unresolved_conflicts")
    writers=[]
    for r in d["worker_results"]:
        if r["state"]!="success":b.append("worker_not_success:"+r["task_id"])
        if r["base_sha"]!=base:b.append("worker_base_stale:"+r["task_id"])
        if r["role"]=="writer":writers.append(r)
    for i,a in enumerate(writers):
        for x in writers[i+1:]:
            if any(overlap(p,q) for p in a["changed_paths"] for q in x["changed_paths"]):
                b.append("same_wave_worker_result_path_overlap:"+a["task_id"]+":"+x["task_id"])
    ready=not b
    return {"schema":"integration-gate-result/v1","change_id":d["change_id"],"wave":d["wave"],
            "action":"READY_FOR_INTEGRATOR" if ready else "RECONCILE_OR_REPLAN","ready":ready,"blockers":b,
            "integrator_id":d["integrator_id"],"authorizes_shared_branch_write":False,
            "authorizes_force_push":False,"authorizes_merge":False,"authorizes_release":False,
            "authorizes_scope_expansion":False}
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("input");a=p.parse_args(argv)
    try:r=evaluate(json.loads(Path(a.input).read_text()))
    except (OSError,ValueError,json.JSONDecodeError) as e:print(f"FAIL: {e}",file=sys.stderr);return 2
    print(json.dumps(r,sort_keys=True));return 0 if r["ready"] else 1
if __name__=="__main__":raise SystemExit(main())
