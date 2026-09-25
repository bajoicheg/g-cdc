from __future__ import annotations
import re
from .canonical_source import semver
SHA=re.compile(r"^[0-9a-f]{40}$")
def validate_candidate(d):
    fields={"schema","version","developed_under_version","canonical_repository","source_commit","package_tree","status","evidence"}
    if not isinstance(d,dict) or set(d)!=fields or d["schema"]!="cdc-release-candidate/v1": raise ValueError("invalid release candidate")
    v=semver(d["version"]); base=semver(d["developed_under_version"])
    minor=v[0]==base[0] and v[1]==base[1]+1 and v[2]==0
    patch=v[0]==base[0] and v[1]==base[1] and v[2]==base[2]+1
    if not (minor or patch): raise ValueError("candidate not developed by stable prior release")
    if d["canonical_repository"]!="bajoicheg/g-cdc" or not SHA.fullmatch(d["source_commit"]) or not SHA.fullmatch(d["package_tree"]): raise ValueError("candidate source binding invalid")
    if d["status"] not in {"candidate","released"}: raise ValueError("invalid candidate status")
    ev=d["evidence"]; required={"bootstrap","package","compatibility","fault_injection","consumers"}
    if not isinstance(ev,dict) or set(ev)!=required: raise ValueError("release evidence classes mismatch")
    for name in required:
        if not isinstance(ev[name],list) or not ev[name] or any(not isinstance(x,str) or not x.strip() for x in ev[name]): raise ValueError(f"missing {name} evidence")
    if any(x.startswith("package:") for x in ev["bootstrap"]): raise ValueError("bootstrap evidence must be independent")
    if len(set(ev["consumers"]))<3: raise ValueError("three distinct consumer validations required")
    return d
