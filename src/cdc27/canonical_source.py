from __future__ import annotations
import re
SEMVER=re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
TREE=re.compile(r"^[0-9a-f]{40}$")
SHA=re.compile(r"^[0-9a-f]{40}$")
def semver(v):
    if not isinstance(v,str) or not SEMVER.fullmatch(v): raise ValueError("stable semver required")
    return tuple(map(int,v.split(".")))
def validate_source_lock(d):
    required={"schema","canonical_repository","target_version","development_driver_version","base_validation_repository","base_validation_commit","base_package_tree","base_validation_run_id","base_validation_evidence_ref","bootstrap_contract","direct_product_repo_development"}
    if not isinstance(d,dict) or set(d)!=required or d["schema"]!="cdc-source-lock/v1": raise ValueError("invalid source lock")
    if d["canonical_repository"]!="bajoicheg/g-cdc": raise ValueError("unexpected canonical repository")
    target=semver(d["target_version"]); driver=semver(d["development_driver_version"])
    if min(target,driver)<(2,11,3):raise ValueError("minimum supported CDC version is 2.11.3")
    minor=target[0]==driver[0] and target[1]==driver[1]+1 and target[2]==0
    patch=target[0]==driver[0] and target[1]==driver[1] and target[2]==driver[2]+1
    if not (minor or patch): raise ValueError("stable driver must develop next minor or patch")
    if not SHA.fullmatch(d["base_validation_commit"]) or not TREE.fullmatch(d["base_package_tree"]): raise ValueError("invalid base evidence")
    run_id=d["base_validation_run_id"]; evidence_ref=d["base_validation_evidence_ref"]
    if type(run_id) is not int or run_id<0: raise ValueError("validation run id invalid")
    if evidence_ref is not None and (not isinstance(evidence_ref,str) or not evidence_ref.strip()): raise ValueError("validation evidence ref invalid")
    if (run_id>0)==(evidence_ref is not None): raise ValueError("exactly one base validation evidence mode required")
    if d["bootstrap_contract"]!="cdc-bootstrap/v1" or d["direct_product_repo_development"] is not False: raise ValueError("bootstrap/canonical invariant violated")
    return d

