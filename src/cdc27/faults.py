from __future__ import annotations
ALLOWED_EXPECTED={"RECOVERY_REQUIRED","DRIFT","IDEMPOTENT","WAITING_EXTERNAL","WAIT_SAFE_BOUNDARY","RELEASE_BLOCKED","CONTINUE_TO_TERMINAL_STATE","ROUTE_BY_VISIBILITY_AWARE_COST","ROUTE_ALTERNATE_BACKEND","REPLAY_ON_FRESH_HEAD","PUBLICATION_BLOCKED","SANITIZED_EXPORT_REQUIRED","REPAIR_SCHEDULER","RETAIN_REF","AUTO_EXECUTE","KICK_WATCHDOG","COMPACT_EVIDENCE","CONTROL_PLANE_ONLY","CHANGE_STRATEGY","EXPORT_NEW_HISTORY","MEASURE_ONLY","TRANSPORT_REJECTED","CONVERGENCE_NOT_PROVEN","RECOVER_EXECUTION_CHANNEL"}
DANGEROUS={"takeover_without_quiescence","product_write","merge","auto_merge","release","duplicate_external_start","blind_launch","policy_fast_forward","takeover_by_ttl","ignore_audit_failure","primitive_only_completion","forced_codex_due_to_private_cost_assumption","terminal_response_while_runnable","silent_idle","manual_mechanical_escalation","force_push","discard_remote_progress","visibility_toggle","direct_publication","accept_stale_blocker","delete_protected_ref","unnecessary_human_escalation","drop_evidence_binding","fleet_product_write","repeat_failed_strategy","direct_visibility_toggle","dogfood_release_authority","accept_package_tree_drift","version_only_integration","source_change_without_product_execution"}
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
