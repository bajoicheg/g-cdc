#!/usr/bin/env python3
"""Independent CDC bootstrap validator. Stdlib-only; never imports candidate runtime."""
from __future__ import annotations
import argparse,ast,json,re,sys
from pathlib import Path
from repository_layout import validate as validate_repository_layout
ROOT=Path(__file__).resolve().parents[1]
SEMVER=re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
SHA=re.compile(r"^[0-9a-f]{40}$")
def load(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
def ver(v):
    if not isinstance(v,str) or not SEMVER.fullmatch(v):raise ValueError("stable semver required")
    return tuple(map(int,v.split(".")))
def source_lock(d):
    target=ver(d["target_version"]);base=ver(d["development_driver_version"])
    if d.get("schema")!="cdc-source-lock/v1" or d.get("canonical_repository")!="bajoicheg/g-cdc":raise ValueError("canonical source lock invalid")
    minor=(target[0]==base[0] and target[1]==base[1]+1 and target[2]==0)
    patch=(target[0]==base[0] and target[1]==base[1] and target[2]==base[2]+1)
    if not (minor or patch):raise ValueError("stable minor or patch release invariant failed")
    if not SHA.fullmatch(d.get("base_validation_commit","")) or not SHA.fullmatch(d.get("base_package_tree","")):raise ValueError("base binding invalid")
    run_id=d.get("base_validation_run_id"); evidence_ref=d.get("base_validation_evidence_ref")
    if type(run_id) is not int or run_id<0:raise ValueError("base validation run id invalid")
    if evidence_ref is not None and (not isinstance(evidence_ref,str) or not evidence_ref.strip()):raise ValueError("base validation evidence ref invalid")
    if (run_id>0)==(evidence_ref is not None):raise ValueError("exactly one base validation evidence mode required")
    if d.get("direct_product_repo_development") is not False:raise ValueError("product repo cannot be canonical CDC source")
def matrix(d):
    if d.get("schema")!="cdc-compatibility-matrix/v1" or d.get("developed_under_version") not in d.get("supported_from_versions",[]):raise ValueError("compatibility matrix invalid")
    m=d.get("migration",{})
    for k in ("requires_released_or_verified_quiescent_owner","requires_reconciled_or_empty_guard","preserve_budget_history","preserve_validation_history","preserve_audit_history"):
        if m.get(k) is not True:raise ValueError("migration safety weakened: "+k)
def faults(d):
    if d.get("schema")!="cdc-fault-scenarios/v1" or len(d.get("scenarios",[]))<8:raise ValueError("fault suite incomplete")
    ids=[x.get("id") for x in d["scenarios"]]
    if len(ids)!=len(set(ids)):raise ValueError("duplicate fault scenario")
def syntax_check():
    for p in (ROOT/"src"/"cdc27").glob("*.py"):ast.parse(p.read_text(encoding="utf-8"),filename=str(p))
def full_source():
    pkg=ROOT/"src"/"continuous-development-cycle"
    if not pkg.is_dir():raise ValueError("source_package_missing")
    target=load("release/source.lock.json")["target_version"]
    if (pkg/"VERSION").read_text(encoding="utf-8").strip()!=target:raise ValueError("candidate VERSION must match source lock")
    if json.loads((pkg/"manifest.json").read_text(encoding="utf-8")).get("version")!=target:raise ValueError("candidate manifest mismatch")
def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument("--mode",choices=("bootstrap","full"),default="full");a=p.parse_args(argv)
    try:
        validate_repository_layout(ROOT)
        if (ROOT/"VERSION").read_text().strip()!=load("release/source.lock.json")["target_version"]:raise ValueError("repository VERSION mismatch")
        source_lock(load("release/source.lock.json"));matrix(load("compatibility/matrix.json"));faults(load("fault-injection/scenarios.json"));syntax_check()
        if a.mode=="full":full_source()
    except (OSError,ValueError,json.JSONDecodeError,SyntaxError) as e:
        print("BOOTSTRAP_RED:",e,file=sys.stderr);return 1
    print("BOOTSTRAP_GREEN: CDC independent bootstrap contract");return 0
if __name__=="__main__":raise SystemExit(main())
