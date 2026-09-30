#!/usr/bin/env python3
"""Fail closed before a final response when this invocation acquired a lease."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from execution_lease_v2 import validate as validate_lease
from execution_continuity import evaluate as evaluate_continuity

def evaluate(invocation_id,lease,continuity,owned_lease=None,now_utc=None):
    if not isinstance(invocation_id,str) or not invocation_id.strip():raise ValueError("invocation_id invalid")
    validate_lease(lease)
    if not isinstance(continuity,dict) or continuity.get("invocation_id")!=invocation_id:
        raise ValueError("continuity must bind exact invocation")
    common={"schema":"final-response-gate-result/v1","authorizes_product_write":False,"authorizes_takeover":False,
            "authorizes_external_start":False,"authorizes_merge":False,"authorizes_release":False}
    if owned_lease is not None:
        if not isinstance(owned_lease,dict) or set(owned_lease)!={"owner_id","generation"}:
            raise ValueError("owned_lease invalid")
        if type(owned_lease["generation"]) is not int or owned_lease["generation"]<0:raise ValueError("owned generation invalid")
        if lease["owner_id"] is not None:
            return {**common,"allowed":False,"final_response_allowed":False,"reason":"invocation_still_owns_or_lease_still_owned"}
        rel=lease.get("last_release")
        exact=bool(rel and rel.get("owner_id")==owned_lease["owner_id"] and rel.get("generation")==owned_lease["generation"]
                   and rel.get("invocation_id")==invocation_id)
        if not exact:
            return {**common,"allowed":False,"final_response_allowed":False,"reason":"exact_owned_generation_release_not_proven"}
        if continuity.get("lease_released") is not True or continuity.get("lease_release_required") is not True:
            return {**common,"allowed":False,"final_response_allowed":False,"reason":"continuity_does_not_record_post_release_state"}
    decision=evaluate_continuity(continuity,now_utc=now_utc)
    if not decision["allowed"] or decision.get("final_response_allowed") is not True:
        return {**common,"allowed":False,"final_response_allowed":False,"reason":decision["reason"]}
    return {**common,"allowed":True,"final_response_allowed":True,"reason":"verified_terminal_and_release_boundary"}

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument("request");p.add_argument("--now");a=p.parse_args(argv)
    try:
        d=json.loads(Path(a.request).read_text(encoding="utf-8"))
        fields={"schema","invocation_id","owned_lease","lease","continuity"}
        if not isinstance(d,dict) or set(d)!=fields or d.get("schema")!="final-response-gate/v1":raise ValueError("request invalid")
        r=evaluate(d["invocation_id"],d["lease"],d["continuity"],d["owned_lease"],a.now)
    except (OSError,ValueError,json.JSONDecodeError) as e:print("FAIL:",e,file=sys.stderr);return 2
    print(json.dumps(r,sort_keys=True));return 0 if r["allowed"] else 1
if __name__=="__main__":raise SystemExit(main())
