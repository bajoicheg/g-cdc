from __future__ import annotations
from .canonical_source import semver
def validate_matrix(d):
    fields={"schema","target_version","developed_under_version","supported_from_versions","checkpoint_schemas","lease_schemas","resume_schemas","consumer_contract","migration"}
    if not isinstance(d,dict) or set(d)!=fields or d["schema"]!="cdc-compatibility-matrix/v1": raise ValueError("invalid compatibility matrix")
    target=semver(d["target_version"]); driver=semver(d["developed_under_version"])
    if target[0]!=driver[0] or target[1]!=driver[1]+1: raise ValueError("driver/target mismatch")
    if d["developed_under_version"] not in d["supported_from_versions"]: raise ValueError("development base must be supported")
    if "development-work-status/v4" not in d["checkpoint_schemas"] or "execution-lease/v2" not in d["lease_schemas"] or "resume-capsule/v1" not in d["resume_schemas"]: raise ValueError("durable schema compatibility lost")
    expected={"requires_released_or_verified_quiescent_owner":True,"requires_reconciled_or_empty_guard":True,"preserve_budget_history":True,"preserve_validation_history":True,"preserve_audit_history":True}
    if d["migration"]!=expected: raise ValueError("migration safety weakened")
    return d
