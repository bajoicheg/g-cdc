#!/usr/bin/env python3
"""CDC 2.10.2 resolved observed parallel-execution benchmark evidence contract."""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
SCHEMA="parallel-benchmark/v1";OBS_SCHEMA="parallel-benchmark-observation/v1"
SHA=re.compile(r"^[0-9a-f]{40}$");DIGEST=re.compile(r"^sha256:[0-9a-f]{64}$");MODES={"sequential","parallel"}

def _text(v,n):
    if not isinstance(v,str) or not v.strip():raise ValueError(f"{n} must be nonempty text")
def _sha(v,n):
    if not isinstance(v,str) or not SHA.fullmatch(v):raise ValueError(f"{n} invalid")
def _safe_rel(path):
    if not isinstance(path,str) or not path.strip() or "\\" in path or path.startswith("/") or "//" in path:
        raise ValueError("unsafe observation path")
    parts=path.split("/")
    if any(x in {"",".",".."} for x in parts):raise ValueError("unsafe observation path")
    return path
def validate_observation(v):
    fields={"schema","observation_id","mode","observed","candidate_sha","environment_ref","plan_ref","workload_fingerprint","elapsed_seconds","evidence_ref"}
    if not isinstance(v,dict) or set(v)!=fields or v.get("schema")!=OBS_SCHEMA:raise ValueError("benchmark observation fields/schema mismatch")
    _text(v["observation_id"],"observation_id")
    if v["mode"] not in MODES:raise ValueError("observation mode invalid")
    if v["observed"] is not True:raise ValueError("benchmark observation must be observed")
    _sha(v["candidate_sha"],"observation candidate_sha")
    for k in ("environment_ref","plan_ref","evidence_ref"):_text(v[k],k)
    if not isinstance(v["workload_fingerprint"],str) or not DIGEST.fullmatch(v["workload_fingerprint"]):raise ValueError("workload_fingerprint invalid")
    if type(v["elapsed_seconds"]) not in {int,float} or v["elapsed_seconds"]<=0:raise ValueError("elapsed_seconds invalid")
    return v
def validate(d):
    fields={"schema","benchmark_id","representative_task_ref","candidate_sha","environment_ref","plan_ref","workstreams","observation_refs",
            "baseline_unresolved_conflicts","parallel_unresolved_conflicts","baseline_rollbacks","parallel_rollbacks"}
    if not isinstance(d,dict) or set(d)!=fields or d.get("schema")!=SCHEMA:raise ValueError("benchmark fields/schema mismatch")
    _text(d["benchmark_id"],"benchmark_id");_text(d["representative_task_ref"],"representative_task_ref")
    _text(d["environment_ref"],"environment_ref");_text(d["plan_ref"],"plan_ref");_sha(d["candidate_sha"],"candidate_sha")
    if type(d["workstreams"]) is not int or d["workstreams"]<2:raise ValueError("workstreams must be >=2")
    refs=d["observation_refs"]
    if not isinstance(refs,list) or len(refs)!=2:raise ValueError("benchmark requires exactly two observation refs")
    paths=[]
    for i,ref in enumerate(refs):
        if not isinstance(ref,dict) or set(ref)!={"path","sha256"}:raise ValueError("observation ref fields mismatch")
        paths.append(_safe_rel(ref["path"]))
        if not isinstance(ref["sha256"],str) or not DIGEST.fullmatch(ref["sha256"]):raise ValueError("observation ref sha256 invalid")
    if len(paths)!=len(set(paths)):raise ValueError("observation paths must be distinct")
    for n in ("baseline_unresolved_conflicts","parallel_unresolved_conflicts","baseline_rollbacks","parallel_rollbacks"):
        if type(d[n]) is not int or d[n]<0:raise ValueError(n+" invalid")
    return d
def load_observations(d,evidence_root):
    validate(d);root=Path(evidence_root).resolve();observations=[]
    for ref in d["observation_refs"]:
        path=(root/ref["path"]).resolve()
        try:path.relative_to(root)
        except ValueError as exc:raise ValueError("observation path escapes evidence root") from exc
        try:payload=path.read_bytes()
        except OSError as exc:raise ValueError(f"cannot read benchmark observation: {exc}") from exc
        observed_digest="sha256:"+hashlib.sha256(payload).hexdigest()
        if observed_digest!=ref["sha256"]:raise ValueError("benchmark observation digest mismatch")
        try:obs=json.loads(payload)
        except json.JSONDecodeError as exc:raise ValueError("benchmark observation JSON invalid") from exc
        validate_observation(obs);observations.append(obs)
    return observations
def evaluate(d,observations):
    validate(d)
    if not isinstance(observations,list) or len(observations)!=2:raise ValueError("resolved observations required")
    obs=[validate_observation(x) for x in observations];by={x["mode"]:x for x in obs}
    if set(by)!=MODES:raise ValueError("benchmark requires one sequential and one parallel observation")
    if len({x["observation_id"] for x in obs})!=2:raise ValueError("observation_id must be distinct")
    if len({x["evidence_ref"] for x in obs})!=2:raise ValueError("observation evidence refs must be distinct")
    if len({x["workload_fingerprint"] for x in obs})!=1:raise ValueError("sequential and parallel workloads differ")
    for x in obs:
        if x["candidate_sha"]!=d["candidate_sha"]:raise ValueError("observation candidate binding mismatch")
        if x["environment_ref"]!=d["environment_ref"]:raise ValueError("observation environment binding mismatch")
        if x["plan_ref"]!=d["plan_ref"]:raise ValueError("observation plan binding mismatch")
    seq=by["sequential"]["elapsed_seconds"];par=by["parallel"]["elapsed_seconds"];b=[]
    if par>=seq:b.append("no_wall_clock_improvement")
    if d["parallel_unresolved_conflicts"]>d["baseline_unresolved_conflicts"]:b.append("conflict_rate_regressed")
    if d["parallel_rollbacks"]>d["baseline_rollbacks"]:b.append("rollback_rate_regressed")
    passed=not b
    return {"schema":"parallel-benchmark-result/v1","benchmark_id":d["benchmark_id"],"candidate_sha":d["candidate_sha"],
            "environment_ref":d["environment_ref"],"plan_ref":d["plan_ref"],"workload_fingerprint":by["sequential"]["workload_fingerprint"],
            "sequential_elapsed_seconds":seq,"parallel_elapsed_seconds":par,"passed":passed,
            "speedup_ratio":round(seq/par,3),"seconds_saved":seq-par,"blockers":b,
            "resolved_observation_count":2,
            "authorizes_worker_launch":False,"authorizes_product_write":False,"authorizes_merge":False,"authorizes_release":False}
def evaluate_from_files(d,evidence_root):
    return evaluate(d,load_observations(d,evidence_root))
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("input");p.add_argument("--evidence-root",required=True);a=p.parse_args(argv)
    try:d=json.loads(Path(a.input).read_text());r=evaluate_from_files(d,a.evidence_root)
    except (OSError,ValueError,json.JSONDecodeError) as e:print(f"FAIL: {e}",file=sys.stderr);return 2
    print(json.dumps(r,sort_keys=True));return 0 if r["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
