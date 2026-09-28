# CDC 2.11.1 independent bounded specification recheck

Verdict: **GREEN** for the reviewed specifications. Both material findings in `/tmp/cdc2111-spec-review.md` are resolved. No new material specification finding in the fix diff.

Reviewed fix `7b02befae6cc94a7835995d85d2a51e61ef517c4` on original Task 1 commit `30e71fcc1dc242dc389436548f73866f637d8eae`. Task 2 remains GREEN at `d7a3c8bf7a75042353230730c21c15c6f4872550`; parent guidance/import assessment from the original review remains unchanged. Parent integration/release metadata and final CI remain separately owned gates; this is not a release or code-quality verdict.

## F1 resolved

Both initial checkpoint and post-attempt settlement now call `_needs_continuation`, which includes unconsumed durable recovery steps. Current explicit pause and exact project terminal proof suppress unclaimed work; uncertain accepted/claimed effects remain monitored.

Independently reran the original idle/null invocation reproduction using actual Git coordination and the recording scheduler, extended through three wakes:

1. Disabled + runnable + idle with budget one executes only enable; pending retains the project.
2. A new wake with budget zero still retains pending and continuation_required.
3. A later authorized wake with budget one executes exactly one run, without replaying enable.

All assertions passed. Inspected the added deadline and pause/terminal boundary tests and predicate behavior.

## F2 resolved

Document, managed-executor, and lease stores now fetch/push through a unique command-scoped remote alias without inherited tracking mappings. Fetch also supplies `--refmap=`. The shared helper copies raw fetch/push endpoint configuration, preserving Git's single-pass URL rewriting; verifies independently pinned effective identity; and adds no persistent remote. Non-force pushes and exact authoritative readback remain.

Independently reran the original malicious/accidental mapping reproduction with `remote.origin.fetch=+refs/heads/cdc/fleet-state:refs/heads/main`, while main is protected by the store. Compared all local refs before and after read and after a subsequent CAS push. Both preserve the exact ref snapshot, the new coordination document reads back correctly, and the persistent remote inventory remains only origin.

## Fix-diff review and bounded regression evidence

Inspected shared helper, all three store edits, Fleet continuation edits, and new tests/reference changes. Legacy lease identity pinning, random proposal nonce, and exact push readback address the separately reproduced analogous gaps without changing lease schemas or public constructor.

Ran three narrow existing real-Git tests against the fixed code, independently of the implementation report:

- Fixed-clock identical legacy lease proposals yield one winner and distinct commits.
- Raw command-scoped alias preserves single rewrite and pushInsteadOf across all three stores.
- Explicit raw pushURL does not receive a second rewrite.

Result: 3/3 PASS (1.030 seconds), plus the two independent F1/F2 reproduction probes PASS. No duplicate full suite, external repository writes, or live scheduler operations. Temporary local Git fixtures and recording scheduler effects only.
