from __future__ import annotations
import re
from .canonical_source import semver
SHA=re.compile(r"^[0-9a-f]{40}$")
def validate_lock(d):
    fields={"schema","canonical_repository","version","release_ref","release_commit","package_tree","checkpoint_schema","safe_boundary_required","local_core_modifications_allowed"}
    if not isinstance(d,dict) or set(d)!=fields or d["schema"]!="cdc-consumer-lock/v1": raise ValueError("invalid consumer lock")
    semver(d["version"])
    if d["canonical_repository"]!="bajoicheg/g-cdc" or d["release_ref"]!="refs/heads/release/v"+d["version"]: raise ValueError("release identity mismatch")
    if not SHA.fullmatch(d["release_commit"]) or not SHA.fullmatch(d["package_tree"]): raise ValueError("release binding invalid")
    if d["checkpoint_schema"]!="development-work-status/v4" or d["safe_boundary_required"] is not True or d["local_core_modifications_allowed"] is not False: raise ValueError("consumer safety invariant violated")
    return d
