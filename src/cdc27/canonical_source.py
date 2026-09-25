from __future__ import annotations
import re
SEMVER=re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
TREE=re.compile(r"^[0-9a-f]{40}$")
SHA=re.compile(r"^[0-9a-f]{40}$")
def semver(v):
    if not isinstance(v,str) or not SEMVER.fullmatch(v): raise ValueError("stable semver required")
    return tuple(map(int,v.split(".")))
def validate_source_lock(d):
    required={"schema","canonical_repository","target_version","development_driver_version","base_validation_repository","base_validation_commit","base_package_tree","base_validation_run_id","bootstrap_contract","direct_product_repo_development"}
    if not isinstance(d,dict) or set(d)!=required or d["schema"]!="cdc-source-lock/v1": raise ValueError("invalid source lock")
    if d["canonical_repository"]!="bajoicheg/g-cdc": raise ValueError("unexpected canonical repository")
    target=semver(d["target_version"]); driver=semver(d["development_driver_version"])
    if target[0]!=driver[0] or target[1]!=driver[1]+1 or target[2]!=0: raise ValueError("N-1 must develop next minor N")
    if not SHA.fullmatch(d["base_validation_commit"]) or not TREE.fullmatch(d["base_package_tree"]): raise ValueError("invalid base evidence")
    if type(d["base_validation_run_id"]) is not int or d["base_validation_run_id"]<=0: raise ValueError("validation run id required")
    if d["bootstrap_contract"]!="cdc-bootstrap/v1" or d["direct_product_repo_development"] is not False: raise ValueError("bootstrap/canonical invariant violated")
    return d
