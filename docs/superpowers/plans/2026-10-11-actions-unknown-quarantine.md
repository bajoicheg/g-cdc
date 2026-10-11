# Native implementation plan: CDC 3.5.1 Actions UNKNOWN quarantine

Spec: 2026-10-11-actions-unknown-quarantine-design.md. Inline native execution;
Root provides the final two independent reviewers. Existing authorization covers
this plan, bounded internal migrations and managed Source release.

1. Add anonymized Actions fixtures and meaningful failing behavioral tests in
   tests/test_actions_submission_retirement.py. Exercise preservation of UNKNOWN,
   original guard/release/history, exact target/scope, missing evidence, transport
   NULLs, replay disguises, native source-write eligibility, raw-CAS rejection,
   immutable-byte authentication, real Git stale CAS and lost response.
2. Extend scripts/submission_retirement.py with separate Actions proof/history
   validation, pure transition and native authenticated-evidence capability/CAS.
   Existing Git and positive cancellation paths retain their semantics. Extend
   scripts/git_lease_store.py only to require/revalidate that capability for an
   Actions history append. Existing lease retirement validation dispatches the
   new history kind; all unrelated fields remain sealed.
3. Run affected retirement/recovery/lease/store tests only. Save actual commands,
   stdout/stderr/returncodes before interpreting RED→GREEN. Document the live
   original-channel application boundary and no-submission/no-replay limits.
4. Update patch metadata and exact package identity; perform cheap placement,
   package and bootstrap-binding checks. Normalize one-parent result on b8f5b2cc;
   history_paths must equal final_paths. Deliver a self-contained Git bundle with
   all base prerequisites and anchor objects; independently import into empty Git.
5. Persist frozen checkpoint + same-budget control instructions; await Root ordered
   SPEC→distinct QUALITY without duplicate review/CI/actor starts. After GREEN,
   exactly one hosted FULL; managed source/release/evidence; close actual worker,
   supervisor, lease, pool and same controller, then independent PID/readback proof.

Review focus: authentication is independent of caller proof syntax; missing
transport proof remains UNKNOWN; scope and replay disguises fail closed; unrelated
managed native source writes survive; stale/lost responses never authorize replay.
