from __future__ import annotations
ALLOWED_EXPECTED={"RECOVERY_REQUIRED","DRIFT","IDEMPOTENT","WAITING_EXTERNAL","WAIT_SAFE_BOUNDARY","RELEASE_BLOCKED"}
DANGEROUS={"takeover_without_quiescence","product_write","merge","auto_merge","release","duplicate_external_start","blind_launch","policy_fast_forward","takeover_by_ttl","ignore_audit_failure"}
def validate_scenarios(d):
    if not isinstance(d,dict) or set(d)!={"schema","scenarios"} or d["schema"]!="cdc-fault-scenarios/v1": raise ValueError("invalid fault scenarios")
    if not isinstance(d["scenarios"],list) or len(d["scenarios"])<8: raise ValueError("fault suite too small")
    ids=set()
    for s in d["scenarios"]:
        if set(s)!={"id","fault","expected","forbidden_authorities"}: raise ValueError("fault scenario fields mismatch")
        if s["id"] in ids: raise ValueError("duplicate fault scenario")
        ids.add(s["id"])
        if s["expected"] not in ALLOWED_EXPECTED: raise ValueError("unknown expected state")
        if not s["forbidden_authorities"] or not set(s["forbidden_authorities"])<=DANGEROUS: raise ValueError("invalid forbidden authority set")
    return d
