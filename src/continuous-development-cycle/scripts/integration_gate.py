#!/usr/bin/env python3
"""CDC 2.10.2 per-wave single-integrator gate bound to the worker contract."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
from worktree_worker_contract import validate as validate_worker_contract

SCHEMA="integration-gate/v1"
SHA=re.compile(r"^[0-9a-f]{40}$")
STATES={"success","failed","stale"}

def _text(v,n):
    if not isinstance(v,str) or not v.strip():
        raise ValueError(f"{n} must be nonempty text")

def _refs(v,n,allow_empty=False):
    if not isinstance(v,list) or any(not isinstance(x,str) or not x.strip() for x in v):
        raise ValueError(f"{n} invalid")
    if not allow_empty and not v:
        raise ValueError(f"{n} must not be empty")
    if len(v)!=len(set(v)):
        raise ValueError(f"{n} contains duplicates")

def _within(path,allowed):
    path=path.rstrip("/");allowed=allowed.rstrip("/")
    return path==allowed or path.startswith(allowed+"/")

def validate(d):
    fields={"schema","change_id","integrator_id","shared_branch","expected_shared_head",
            "observed_shared_head","worker_contract","worker_results",
            "unresolved_conflicts","force_push_requested","verification_refs"}
    if not isinstance(d,dict) or set(d)!=fields or d.get("schema")!=SCHEMA:
        raise ValueError("integration gate fields/schema mismatch")
    for n in ("change_id","integrator_id","shared_branch"):
        _text(d[n],n)
    for n in ("expected_shared_head","observed_shared_head"):
        if not isinstance(d[n],str) or not SHA.fullmatch(d[n]):
            raise ValueError(n+" invalid")
    if type(d["force_push_requested"]) is not bool:
        raise ValueError("force_push_requested must be boolean")
    _refs(d["verification_refs"],"verification_refs")
    _refs(d["unresolved_conflicts"],"unresolved_conflicts",allow_empty=True)

    contract=validate_worker_contract(d["worker_contract"])
    if contract["change_id"]!=d["change_id"]:
        raise ValueError("worker contract change mismatch")
    if contract["integrator_id"]!=d["integrator_id"]:
        raise ValueError("worker contract integrator mismatch")
    if contract["shared_branch"]!=d["shared_branch"]:
        raise ValueError("worker contract shared branch mismatch")
    if contract["base_sha"]!=d["expected_shared_head"]:
        raise ValueError("worker contract base mismatch")

    assignments={a["task_id"]:a for a in contract["assignments"]}
    if not isinstance(d["worker_results"],list):
        raise ValueError("worker_results must be list")
    seen_tasks=set();seen_workers=set()
    for i,r in enumerate(d["worker_results"]):
        f={"worker_id","task_id","role","base_sha","result_sha","state","changed_paths","output_refs","evidence_refs"}
        if not isinstance(r,dict) or set(r)!=f:
            raise ValueError("worker result fields mismatch")
        for n in ("worker_id","task_id"):
            _text(r[n],f"worker[{i}].{n}")
        if r["task_id"] in seen_tasks or r["worker_id"] in seen_workers:
            raise ValueError("duplicate worker/task result")
        seen_tasks.add(r["task_id"]);seen_workers.add(r["worker_id"])
        if r["task_id"] not in assignments:
            raise ValueError("result references unknown assignment")
        a=assignments[r["task_id"]]
        if r["worker_id"]!=a["worker_id"] or r["role"]!=a["role"]:
            raise ValueError("result identity/role does not match assignment")
        if r["state"] not in STATES:
            raise ValueError("worker state invalid")
        for n in ("base_sha","result_sha"):
            if not isinstance(r[n],str) or not SHA.fullmatch(r[n]):
                raise ValueError("worker SHA invalid")
        if r["base_sha"]!=a["base_sha"]:
            raise ValueError("result base does not match assignment")
        _refs(r["output_refs"],"worker outputs",allow_empty=r["state"]!="success")
        _refs(r["evidence_refs"],"worker evidence")
        if r["state"]=="success" and not set(a["expected_outputs"])<=set(r["output_refs"]):
            raise ValueError("worker result missing expected output")
        if r["state"]=="success" and not set(a["expected_evidence"])<=set(r["evidence_refs"]):
            raise ValueError("worker result missing expected evidence")
        if not isinstance(r["changed_paths"],list) or any(not isinstance(x,str) or not x.strip() for x in r["changed_paths"]):
            raise ValueError("changed_paths invalid")
        if r["role"]!="writer":
            if r["changed_paths"]:
                raise ValueError("non-writer changed paths forbidden")
            if r["state"]=="success" and r["result_sha"]!=r["base_sha"]:
                raise ValueError("non-writer result SHA must remain at base")
        if r["role"]=="writer":
            if r["state"]=="success" and not r["changed_paths"]:
                raise ValueError("successful writer requires changed paths")
            if r["state"]=="success" and r["result_sha"]==r["base_sha"]:
                raise ValueError("successful writer result SHA must differ from base")
            for changed in r["changed_paths"]:
                if not any(_within(changed,allowed) for allowed in a["write_paths"]):
                    raise ValueError("worker changed path outside assigned write set")
    return d

def evaluate(d):
    validate(d)
    contract=d["worker_contract"];base=d["expected_shared_head"];b=[]
    if d["observed_shared_head"]!=base:
        b.append("shared_head_moved_reconcile_required")
    if d["force_push_requested"]:
        b.append("force_push_forbidden")
    if d["unresolved_conflicts"]:
        b.append("unresolved_conflicts")
    results={r["task_id"]:r for r in d["worker_results"]}
    for a in contract["assignments"]:
        r=results.get(a["task_id"])
        if r is None:
            b.append("missing_worker_result:"+a["task_id"])
            continue
        if r["state"]!="success":
            b.append("worker_not_success:"+a["task_id"])
        if r["base_sha"]!=base:
            b.append("worker_base_stale:"+a["task_id"])
    writers=[r for r in d["worker_results"] if r["role"]=="writer"]
    for i,a in enumerate(writers):
        for x in writers[i+1:]:
            for p in a["changed_paths"]:
                for q in x["changed_paths"]:
                    if _within(p,q) or _within(q,p):
                        b.append("same_wave_worker_result_path_overlap:"+a["task_id"]+":"+x["task_id"])
    ready=not b
    return {
        "schema":"integration-gate-result/v1",
        "change_id":d["change_id"],
        "wave":contract["wave"],
        "plan_ref":contract["plan_ref"],
        "action":"READY_FOR_INTEGRATOR" if ready else "RECONCILE_OR_REPLAN",
        "ready":ready,
        "blockers":b,
        "integrator_id":d["integrator_id"],
        "next_gate":"cdc_2.10.1_review_branch_finish_then_2.10.0_verification",
        "authorizes_shared_branch_write":False,
        "authorizes_force_push":False,
        "authorizes_merge":False,
        "authorizes_release":False,
        "authorizes_scope_expansion":False,
    }

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("input");a=p.parse_args(argv)
    try:r=evaluate(json.loads(Path(a.input).read_text()))
    except (OSError,ValueError,json.JSONDecodeError) as e:
        print(f"FAIL: {e}",file=sys.stderr);return 2
    print(json.dumps(r,sort_keys=True));return 0 if r["ready"] else 1

if __name__=="__main__":
    raise SystemExit(main())
