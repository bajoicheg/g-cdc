#!/usr/bin/env python3
"""CDC 2.10.2 observed parallel-execution benchmark evidence contract."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
SCHEMA="parallel-benchmark/v1";SHA=re.compile(r"^[0-9a-f]{40}$")
def _text(v,n):
    if not isinstance(v,str) or not v.strip():raise ValueError(f"{n} must be nonempty text")
def validate(d):
    f={"schema","benchmark_id","representative_task_ref","candidate_sha","measurement_mode","environment_ref","plan_ref","workstreams","sequential_baseline_seconds",
       "parallel_elapsed_seconds","baseline_unresolved_conflicts","parallel_unresolved_conflicts",
       "baseline_rollbacks","parallel_rollbacks","evidence_refs"}
    if not isinstance(d,dict) or set(d)!=f or d.get("schema")!=SCHEMA:raise ValueError("benchmark fields/schema mismatch")
    _text(d["benchmark_id"],"benchmark_id");_text(d["representative_task_ref"],"representative_task_ref");_text(d["environment_ref"],"environment_ref");_text(d["plan_ref"],"plan_ref")
    if not isinstance(d["candidate_sha"],str) or not SHA.fullmatch(d["candidate_sha"]):raise ValueError("candidate_sha invalid")
    if d["measurement_mode"]!="observed":raise ValueError("benchmark must use observed measurement mode")
    if type(d["workstreams"]) is not int or d["workstreams"]<2:raise ValueError("workstreams must be >=2")
    for n in ("sequential_baseline_seconds","parallel_elapsed_seconds"):
        if type(d[n]) not in {int,float} or d[n]<=0:raise ValueError(n+" invalid")
    for n in ("baseline_unresolved_conflicts","parallel_unresolved_conflicts","baseline_rollbacks","parallel_rollbacks"):
        if type(d[n]) is not int or d[n]<0:raise ValueError(n+" invalid")
    if not isinstance(d["evidence_refs"],list) or len(d["evidence_refs"])<2 or any(not isinstance(x,str) or not x.strip() for x in d["evidence_refs"]):
        raise ValueError("benchmark needs multiple evidence refs")
    if len(d["evidence_refs"])!=len(set(d["evidence_refs"])):raise ValueError("benchmark evidence refs must be distinct")
    return d
def evaluate(d):
    validate(d);b=[]
    if d["parallel_elapsed_seconds"]>=d["sequential_baseline_seconds"]:b.append("no_wall_clock_improvement")
    if d["parallel_unresolved_conflicts"]>d["baseline_unresolved_conflicts"]:b.append("conflict_rate_regressed")
    if d["parallel_rollbacks"]>d["baseline_rollbacks"]:b.append("rollback_rate_regressed")
    passed=not b
    return {"schema":"parallel-benchmark-result/v1","benchmark_id":d["benchmark_id"],"candidate_sha":d["candidate_sha"],"measurement_mode":d["measurement_mode"],"environment_ref":d["environment_ref"],"plan_ref":d["plan_ref"],"passed":passed,
            "speedup_ratio":round(d["sequential_baseline_seconds"]/d["parallel_elapsed_seconds"],3),
            "seconds_saved":d["sequential_baseline_seconds"]-d["parallel_elapsed_seconds"],"blockers":b,
            "authorizes_worker_launch":False,"authorizes_product_write":False,"authorizes_merge":False,
            "authorizes_release":False}
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("input");a=p.parse_args(argv)
    try:r=evaluate(json.loads(Path(a.input).read_text()))
    except (OSError,ValueError,json.JSONDecodeError) as e:print(f"FAIL: {e}",file=sys.stderr);return 2
    print(json.dumps(r,sort_keys=True));return 0 if r["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
