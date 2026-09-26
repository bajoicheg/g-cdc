#!/usr/bin/env python3
"""CDC 2.10.2 structured observed parallel-execution benchmark evidence contract."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
SCHEMA="parallel-benchmark/v1";SHA=re.compile(r"^[0-9a-f]{40}$");DIGEST=re.compile(r"^sha256:[0-9a-f]{64}$")
MODES={"sequential","parallel"}

def _text(v,n):
    if not isinstance(v,str) or not v.strip():raise ValueError(f"{n} must be nonempty text")
def _sha(v,n):
    if not isinstance(v,str) or not SHA.fullmatch(v):raise ValueError(f"{n} invalid")
def _obs(v,n):
    fields={"mode","observed","candidate_sha","environment_ref","plan_ref","workload_fingerprint","elapsed_seconds","evidence_ref"}
    if not isinstance(v,dict) or set(v)!=fields:raise ValueError(f"{n} fields mismatch")
    if v["mode"] not in MODES:raise ValueError(f"{n}.mode invalid")
    if v["observed"] is not True:raise ValueError(f"{n} must be an observed measurement")
    _sha(v["candidate_sha"],f"{n}.candidate_sha")
    for k in ("environment_ref","plan_ref","evidence_ref"):_text(v[k],f"{n}.{k}")
    if not isinstance(v["workload_fingerprint"],str) or not DIGEST.fullmatch(v["workload_fingerprint"]):raise ValueError(f"{n}.workload_fingerprint invalid")
    if type(v["elapsed_seconds"]) not in {int,float} or v["elapsed_seconds"]<=0:raise ValueError(f"{n}.elapsed_seconds invalid")
    return v

def validate(d):
    fields={"schema","benchmark_id","representative_task_ref","candidate_sha","environment_ref","plan_ref","workstreams","observations",
            "baseline_unresolved_conflicts","parallel_unresolved_conflicts","baseline_rollbacks","parallel_rollbacks"}
    if not isinstance(d,dict) or set(d)!=fields or d.get("schema")!=SCHEMA:raise ValueError("benchmark fields/schema mismatch")
    _text(d["benchmark_id"],"benchmark_id");_text(d["representative_task_ref"],"representative_task_ref")
    _text(d["environment_ref"],"environment_ref");_text(d["plan_ref"],"plan_ref");_sha(d["candidate_sha"],"candidate_sha")
    if type(d["workstreams"]) is not int or d["workstreams"]<2:raise ValueError("workstreams must be >=2")
    if not isinstance(d["observations"],list) or len(d["observations"])!=2:raise ValueError("benchmark requires exactly sequential and parallel observations")
    obs=[_obs(v,f"observation[{i}]") for i,v in enumerate(d["observations"])]
    by_mode={v["mode"]:v for v in obs}
    if set(by_mode)!=MODES:raise ValueError("benchmark requires one sequential and one parallel observation")
    refs=[v["evidence_ref"] for v in obs]
    if len(refs)!=len(set(refs)):raise ValueError("benchmark observation evidence refs must be distinct")
    fps={v["workload_fingerprint"] for v in obs}
    if len(fps)!=1:raise ValueError("sequential and parallel workloads differ")
    for v in obs:
        if v["candidate_sha"]!=d["candidate_sha"]:raise ValueError("observation candidate binding mismatch")
        if v["environment_ref"]!=d["environment_ref"]:raise ValueError("observation environment binding mismatch")
        if v["plan_ref"]!=d["plan_ref"]:raise ValueError("observation plan binding mismatch")
    for n in ("baseline_unresolved_conflicts","parallel_unresolved_conflicts","baseline_rollbacks","parallel_rollbacks"):
        if type(d[n]) is not int or d[n]<0:raise ValueError(n+" invalid")
    return d

def evaluate(d):
    validate(d);by={v["mode"]:v for v in d["observations"]};seq=by["sequential"]["elapsed_seconds"];par=by["parallel"]["elapsed_seconds"];b=[]
    if par>=seq:b.append("no_wall_clock_improvement")
    if d["parallel_unresolved_conflicts"]>d["baseline_unresolved_conflicts"]:b.append("conflict_rate_regressed")
    if d["parallel_rollbacks"]>d["baseline_rollbacks"]:b.append("rollback_rate_regressed")
    passed=not b
    return {"schema":"parallel-benchmark-result/v1","benchmark_id":d["benchmark_id"],"candidate_sha":d["candidate_sha"],
            "environment_ref":d["environment_ref"],"plan_ref":d["plan_ref"],"workload_fingerprint":by["sequential"]["workload_fingerprint"],
            "sequential_elapsed_seconds":seq,"parallel_elapsed_seconds":par,"passed":passed,
            "speedup_ratio":round(seq/par,3),"seconds_saved":seq-par,"blockers":b,
            "authorizes_worker_launch":False,"authorizes_product_write":False,"authorizes_merge":False,"authorizes_release":False}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("input");a=p.parse_args(argv)
    try:r=evaluate(json.loads(Path(a.input).read_text()))
    except (OSError,ValueError,json.JSONDecodeError) as e:print(f"FAIL: {e}",file=sys.stderr);return 2
    print(json.dumps(r,sort_keys=True));return 0 if r["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
