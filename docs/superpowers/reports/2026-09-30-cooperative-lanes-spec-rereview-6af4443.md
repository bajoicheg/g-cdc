# CDC 2.11.2 specification-compliance re-review — source 6af4443

## Verdict

**VERDICT: SPEC TECHNICAL RECHECK GREEN**

No material specification-compliance finding remains in the exact target below.

This is a fresh isolated specification re-check after the internal Q2/Q3 hardening. It is not the separate code-quality review, not a merge/release verdict, and it is not represented as an external independent reviewer identity. The current harness still exposes no fresh reviewer/subagent identity.

No scheduler was enabled, run, rebound, recreated, or otherwise mutated by this review. No merge, release, force-push, or product shared-ref mutation was performed.

## Exact target

- repository: `bajoicheg/g-cdc`
- stacked quality PR: #74
- validation-only PR: #76
- corrected source: `6af4443b1afa86085622625bee9b62a045a08a07`
- corrected package tree: `7a7a7faa75b7fc9160d912d8fb507c6b9573d17f`
- candidate metadata HEAD: `ddb8503b3b8f2ff18009a90f4adc370965d38872`
- exact hosted validation run: `36749087759`
- review branch base: `ddb8503b3b8f2ff18009a90f4adc370965d38872`

The candidate metadata binds exactly the source and package tree above. Hosted run `36749087759` completed successfully: repository layout validation, independent bootstrap, package validation, **866/866 candidate tests**, full bootstrap binding, and all three archived consumer snapshots were GREEN. The consumer gate independently reported `THREE_CONSUMERS_GREEN package_tree=7a7a7faa75b7fc9160d912d8fb507c6b9573d17f`.

## Prior S1–S5 / R1 disposition

### S1 — CLOSED

No post-`075ef86` source change weakens watchdog replacement quiescence. Replacement still requires exact object/generation-bound quiescence evidence; generation fencing remains non-equivalent to stop proof; fresh safety observations still bracket replacement effects.

### S2 — CLOSED

No post-`075ef86` source change weakens explicit lane capability/role validation. REVIEW/read-only lanes remain unable to gain write authority; unknown roles and incompatible role/kind pairings remain rejected.

### S3 — CLOSED

No post-`075ef86` source change weakens portable reservation of the configured shared product ref to the integrator.

### S4 / R1 — CLOSED, with additional provenance hardening

The earlier R1 fix remains intact: exact per-ref `git push --porcelain` output controls rejection classification. `[rejected]` and `[remote rejected]` are explicit rejection; `[remote failure]`, malformed/missing target status, generic stderr, and transport ambiguity remain `unknown`.

The final source additionally closes a crash-gap discovered during internal quality review. The publisher persists `submitted` before invoking transport. Therefore a controller crash can leave a durable `submitted` marker even when `_push_cas()` was never entered. A later matching remote HEAD, possibly written by another actor, must not upgrade that marker into proof that this operation performed the expected-head CAS.

Final behavior:
- no attempt: matching intended HEAD is readback-only;
- `prepared`: matching HEAD is non-authoritative;
- raw `submitted`: matching HEAD is non-authoritative and is not replayed;
- `unknown`: matching authoritative readback may confirm the same already-attempted ambiguous operation without replay;
- `confirmed`: remains authoritative;
- `rejected` / `aborted`: remain non-authoritative even if bytes later coincide.

RED evidence for this hardening:
- source `a0479e46ad29e338d8f74eba7f87a5342bf73651`
- package tree `b3fee3be43552e2408cd74f0abc96d30fb2ef917`
- metadata `86a0171b6809f2ec2ef61b46d4786e24ffae7823`
- run `36748380426`
- 866 candidate tests, exactly one failure:
  `test_submitted_marker_without_push_outcome_does_not_become_conditional_proof`
- observed defect: `conditional_update` was `True` when the retained regression required `False`.

GREEN evidence:
- final source `6af4443b1afa86085622625bee9b62a045a08a07`
- run `36749087759`
- the same regression passed inside 866/866.

This preserves the S4 invariant that coincident/pre-existing bytes never manufacture operation-bound conditional-publication proof.

### S5 — CLOSED

No post-`075ef86` source change weakens migration authority revalidation. Fresh verifier evidence remains required on authoritative reads; restart without the verifier and authority/evidence drift remain fail-closed.

## Durable integration-state read-boundary hardening

Internal quality review also found that the lane registry previously validated lane/start-operation records strictly but checked only collection types for `integration_queue`, `integration_intents`, and `integrated_results`. A malformed persisted queue item that `record_result()` could never create could reach `claim_integration()` and seed a new durable intent.

RED evidence:
- source `fe60b3a05393d53c4c6787465a1b2259194616f3`
- package tree `31f0971cdb4a0bb4dda1a4deec9137134b621c96`
- metadata `46bfb2df1027c42c9e66a06e7181c5f641bd353a`
- run `36747351190`
- 865 tests, exactly one failure:
  `test_malformed_integration_queue_fails_before_claim_mutation`
- observed defect: `ValueError` was not raised.

The final source validates the durable integration collections before returning registry state or allowing any mutation. It binds queue/results to real writer lanes, source heads, contained touched paths and evidence; validates intent identity and exact integrator invocation/generation/executor; rejects duplicates/cross-state contradictions; and binds integrated results to matching integrated intents and publication evidence.

GREEN evidence:
- source `274ff6a6d34e1723c17a4dcaddeecddf98566e5c`
- package tree `43dc4794bc4507ba2c3eae2ab67af7fb0e8a547e`
- metadata `5bb8b2258c0423a3b5c3ebd4192f82cd0792578f`
- run `36747915923`
- 865/865 candidate tests plus bootstrap and three consumers GREEN.

The later Q3 source retains this correction and the final 866-test run remains GREEN.

## Non-finding retained regression

A suspected survivability batch-budget accounting defect was tested and disproved. `test_reconciled_unknown_does_not_consume_current_batch_effect_budget` ran on hosted run `36746663831` and passed; the full candidate suite was 864/864. The test is retained as useful regression coverage, but no production defect or corrective source change is claimed for it.

## Scope review

Relative to previously re-reviewed source `075ef86f21759d50392b3b58fdda252cdce474a7`, production changes are limited to:

1. fail-closed durable integration queue/intent/result validation in `project_lane_runtime.py`; and
2. publication provenance hardening for raw `submitted` attempts in `project_lane_git.py`.

The remaining package changes are retained regressions. Candidate and consumer metadata only bind the exact final source/package tree.

No material specification defect was found in this final delta.

## Gate state

- S1: closed
- S2: closed
- S3: closed
- S4: closed, including R1 and submitted-marker provenance gap
- S5: closed
- durable integration-state corruption gap: closed
- material open SPEC findings: **0**
- exact hosted package/bootstrap/consumer gate: **GREEN**
- external independent reviewer identity: **not available in this harness**
- separate final code-quality review gate: **not yet satisfied**

**SPEC technical re-check is GREEN for source `6af4443b...`. Do not merge or release from this report alone.**
