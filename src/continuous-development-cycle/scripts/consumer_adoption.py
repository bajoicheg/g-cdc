#!/usr/bin/env python3
"""Fail-closed atomic consumer adoption publication planning."""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path

SCHEMA="consumer-adoption-publication/v1"
SHA=re.compile(r"^[0-9a-f]{40}$");SEMVER=re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")

def _sha(v,n,nullable=False):
    if v is None and nullable:return
    if not isinstance(v,str) or not SHA.fullmatch(v):raise ValueError(n+" invalid")

def _path(v):
    if not isinstance(v,str) or not v or v.startswith("/") or v.endswith("/") or any(x in {"",".",".."} for x in v.split("/")):raise ValueError("adoption path invalid")
    return v

def validate(s):
    fields={"schema","source_head","target_ref","target_version","target_package_tree","required_paths","prepared_paths",
            "final_tree_sha","observed_package_tree","candidate_commit","live_source_head","publication_claim",
            "published_head","readback_package_tree"}
    if not isinstance(s,dict) or set(s)!=fields or s.get("schema")!=SCHEMA:raise ValueError("atomic adoption state invalid")
    _sha(s["source_head"],"source_head");_sha(s["target_package_tree"],"target_package_tree");_sha(s["live_source_head"],"live_source_head")
    if not isinstance(s["target_ref"],str) or not s["target_ref"].startswith("refs/heads/"):raise ValueError("target_ref invalid")
    if not isinstance(s["target_version"],str) or not SEMVER.fullmatch(s["target_version"]):raise ValueError("target_version invalid")
    for n in ("final_tree_sha","observed_package_tree","candidate_commit","published_head","readback_package_tree"):_sha(s[n],n,True)
    if not isinstance(s["required_paths"],list) or not s["required_paths"]:raise ValueError("required_paths invalid")
    required=[_path(x) for x in s["required_paths"]]
    prepared=[_path(x) for x in s["prepared_paths"]] if isinstance(s["prepared_paths"],list) else (_ for _ in ()).throw(ValueError("prepared_paths invalid"))
    if len(required)!=len(set(required)) or len(prepared)!=len(set(prepared)):raise ValueError("duplicate adoption path")
    if not set(prepared)<=set(required):raise ValueError("prepared path outside required set")
    claim=s["publication_claim"]
    if claim is not None:
        if not isinstance(claim,dict) or set(claim)!={"effect_id","expected_head","intended_head","target_ref"}:raise ValueError("publication claim invalid")
        if not isinstance(claim["effect_id"],str) or not claim["effect_id"].startswith("sha256:"):raise ValueError("publication effect id invalid")
        _sha(claim["expected_head"],"claim expected_head");_sha(claim["intended_head"],"claim intended_head")
        if claim["target_ref"]!=s["target_ref"]:raise ValueError("publication claim ref mismatch")
    return s

def _claim(s):
    payload={"target_ref":s["target_ref"],"expected_head":s["source_head"],"intended_head":s["candidate_commit"],
             "target_version":s["target_version"],"target_package_tree":s["target_package_tree"]}
    digest=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {"effect_id":"sha256:"+digest,"expected_head":s["source_head"],"intended_head":s["candidate_commit"],"target_ref":s["target_ref"]}

def assess(s):
    validate(s)
    common={"schema":"consumer-adoption-publication-plan/v1","authorizes_ref_move":False,"authorizes_force_push":False,
            "authorizes_product_write":False,"publication_prerequisites_satisfied":False}
    missing=[p for p in s["required_paths"] if p not in s["prepared_paths"]]
    if missing:return {**common,"action":"PREPARE_DETACHED","missing_paths":missing,"reason":"shared_ref_must_remain_unchanged"}
    if s["final_tree_sha"] is None:return {**common,"action":"BUILD_FINAL_TREE","missing_paths":[],"reason":"all_required_paths_prepared_detached"}
    if s["observed_package_tree"] is None:return {**common,"action":"VERIFY_PACKAGE_TREE","missing_paths":[],"reason":"exact_target_subtree_not_observed"}
    if s["observed_package_tree"]!=s["target_package_tree"]:return {**common,"action":"REJECT_PACKAGE_DRIFT","missing_paths":[],"reason":"target_package_tree_mismatch"}
    if s["candidate_commit"] is None:return {**common,"action":"BUILD_CANDIDATE_COMMIT","missing_paths":[],"reason":"detached_tree_verified"}
    if s["live_source_head"]!=s["source_head"]:return {**common,"action":"REPLAN_FRESH_HEAD","missing_paths":[],"reason":"shared_ref_moved_before_publication"}
    expected=_claim(s)
    if s["publication_claim"] is None:return {**common,"action":"CLAIM_CONDITIONAL_PUBLISH","missing_paths":[],"claim":expected,"reason":"exact_candidate_ready"}
    if s["publication_claim"]!=expected:raise ValueError("publication claim does not bind exact candidate")
    if s["published_head"] is None:
        return {**common,"action":"READY_CONDITIONAL_FAST_FORWARD","missing_paths":[],"claim":expected,
                "publication_prerequisites_satisfied":True,"reason":"one_shared_ref_effect_required"}
    if s["published_head"]!=s["candidate_commit"]:
        return {**common,"action":"RECONCILE_PUBLICATION","missing_paths":[],"claim":expected,"reason":"published_head_not_exact_candidate"}
    if s["readback_package_tree"] is None:
        return {**common,"action":"READBACK_PUBLISHED_PACKAGE","missing_paths":[],"claim":expected,"reason":"publication_requires_exact_readback"}
    if s["readback_package_tree"]!=s["target_package_tree"]:
        return {**common,"action":"RECOVERY_REQUIRED","missing_paths":[],"claim":expected,"reason":"published_package_tree_mismatch"}
    return {**common,"action":"COMPLETE","missing_paths":[],"claim":expected,"publication_prerequisites_satisfied":True,
            "reason":"single_conditional_publish_and_exact_readback"}

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument("state");a=p.parse_args(argv)
    try:r=assess(json.loads(Path(a.state).read_text(encoding="utf-8")))
    except (OSError,ValueError,json.JSONDecodeError) as e:print("FAIL:",e,file=sys.stderr);return 2
    print(json.dumps(r,sort_keys=True));return 0 if r["action"] not in {"REJECT_PACKAGE_DRIFT","RECOVERY_REQUIRED"} else 1
if __name__=="__main__":raise SystemExit(main())
