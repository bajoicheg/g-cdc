# Command terminal evidence implementation plan

> For agentic workers: use superpowers:executing-plans in this existing managed writer.

Goal: preserve terminal command bytes before interpretation and prevent a rejected authentic closeout from returning success.
Architecture: extend existing run_checks/validate_evidence and cdc CLI; no new authority or orchestrator.
Tech stack: Python standard library, real Git/subprocess tests.
Spec: owner-approved source354-owner-scope.json in SAME PRIVATE control branch.

## Constraints
Runtime floor3.3.0 unchanged; legacy command-evidence/v1 readers remain.
Separate stdout/stderr are raw local observations, never provider attestation.
Unexecuted commands retain null exit; classified evidence still requires source/plan/environment/JUnit checks.
No local FULL, product changes, new identity or replay; one hosted reviewed FULL.

## Review focus
Classifier/JUnit/source-observation failures must not destroy raw terminal receipts.
Timeout/interruption preserves genuine exit without fabricating completed success.
Missing/changed raw files/exit or removing the new capture marker must be rejected.
Old genuine combined-log evidence remains readable; new log projection has no chronology claim.
Negative closeout remains authoritative even if a compact result was saved; no caller label grants authority.

## Tasks
- [ ] Extend existing failure test for exact stdout/stderr/exit; add real classifier-failure and tamper/legacy checks; watch RED.
- [ ] Persist terminal before interpretation; independent validator verifies new capture joins; targeted GREEN.
- [ ] CLI returns1 for accepted:false and optionally saves create-only full result before bounded pointers; negative dispatch RED→GREEN then native dogfood.
- [ ] Necessary354 metadata, cheap bindings/package/discovery/object closure; freeze exact one-parent artifact/anchor.
- [ ] Ordered SPEC→distinct QUALITY, one prospectively reserved hosted FULL, managed release/evidence/expected-head main.
- [ ] Native real terminal/quiescence/readback and controller exit; preserve every historic failure and open RCA.
