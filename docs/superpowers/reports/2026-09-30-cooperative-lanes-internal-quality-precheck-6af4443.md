# CDC 2.11.2 internal code-quality precheck — source 6af4443

## Status

**INTERNAL TECHNICAL PRECHECK: GREEN WITH FORMAL REVIEWER BLOCKER**

This pass is an implementation-quality hardening/precheck on the exact final candidate. It is not represented as the required fresh independent code-quality reviewer identity and therefore does not satisfy the formal CDC 2.10.1 code-quality review gate.

No merge, release, shared product-ref publication, scheduler enable/run/rebind/recreate, or owner-pause change was performed.

## Exact target

- repository: `bajoicheg/g-cdc`
- source: `6af4443b1afa86085622625bee9b62a045a08a07`
- package tree: `7a7a7faa75b7fc9160d912d8fb507c6b9573d17f`
- metadata HEAD: `ddb8503b3b8f2ff18009a90f4adc370965d38872`
- quality branch/PR: `cdc/2.11.2-quality-q1-survivability-budget` / #74
- final technical SPEC recheck: `review/2.11.2-spec-rereview-6af4443`
- full-diff external review PR: #77
- exact-head hosted validation: `36749087759` — SUCCESS
- repeated exact-head validation on review PR: `36750000629` — SUCCESS

Final hosted candidate evidence: 866/866 package tests, independent bootstrap GREEN, package validator 316 files/templates, full bootstrap binding GREEN, and 3/3 archived consumers GREEN.

## Internal quality findings and disposition

### Q1 — non-finding — survivability readback budget accounting

A suspected defect was tested directly: reconciling an already-consumed unknown scheduler effect by authoritative readback should not consume the current batch's effect budget.

Retained regression:
`test_reconciled_unknown_does_not_consume_current_batch_effect_budget`

Hosted run `36746663831` executed the regression inside 864/864 GREEN. No production defect was reproduced and no production correction was made for this hypothesis.

### Q2 — CLOSED — malformed durable integration state crossed the read boundary

The lane registry strictly validated lane and start-operation records but initially checked only collection types for `integration_queue`, `integration_intents`, and `integrated_results`. A malformed persisted queue record that `record_result()` could never produce could reach `claim_integration()` and seed a new durable integration intent.

RED:
- source `fe60b3a05393d53c4c6787465a1b2259194616f3`
- package tree `31f0971cdb4a0bb4dda1a4deec9137134b621c96`
- metadata `46bfb2df1027c42c9e66a06e7181c5f641bd353a`
- run `36747351190`
- 865 tests, exactly one failure:
  `test_malformed_integration_queue_fails_before_claim_mutation`
- observed: expected `ValueError` was not raised.

Correction:
`274ff6a6d34e1723c17a4dcaddeecddf98566e5c` adds fail-closed read-boundary validation for queued results, integration intents, integrated results, duplicate/cross-state contradictions, exact integrator identity/generation, and stored publication evidence.

GREEN:
- metadata `5bb8b2258c0423a3b5c3ebd4192f82cd0792578f`
- run `36747915923`
- 865/865 GREEN.

The final source retains this correction.

### Q3 — CLOSED — raw submitted marker could manufacture conditional-publication proof

The publisher persists `submitted` before invoking transport. A controller crash can therefore leave `submitted` even when `_push_cas()` was never entered. Previously, if the authoritative ref later equaled the intended commit, a raw `submitted` marker could be upgraded to `conditional_update=true`, allowing coincident bytes to impersonate proof of this intent's expected-head CAS.

RED:
- source `a0479e46ad29e338d8f74eba7f87a5342bf73651`
- package tree `b3fee3be43552e2408cd74f0abc96d30fb2ef917`
- metadata `86a0171b6809f2ec2ef61b46d4786e24ffae7823`
- run `36748380426`
- 866 tests, exactly one failure:
  `test_submitted_marker_without_push_outcome_does_not_become_conditional_proof`
- observed: `conditional_update` was `True`.

Correction:
`6af4443b1afa86085622625bee9b62a045a08a07` permits readback confirmation only for durable `unknown` or already `confirmed` attempts. Raw `prepared`, `submitted`, `rejected`, and `aborted` states remain non-authoritative and are not replayed.

GREEN:
- metadata `ddb8503b3b8f2ff18009a90f4adc370965d38872`
- run `36749087759`
- 866/866 GREEN.
- repeated review-PR run `36750000629` also SUCCESS.

## Maintainability / safety review of final delta

The final production delta after the prior post-R1 source is limited to:
1. explicit durable integration-state validators in `project_lane_runtime.py`; and
2. a narrow publication-attempt state/provenance rule in `project_lane_git.py`.

The validators keep authority checks at the durable read boundary rather than scattering assumptions across mutations. They bind persisted records back to validated lane claims and exact integration intents. The publication correction is small and conservative: it removes an unsafe proof upgrade without adding replay or broader write authority.

The retained tests reproduce the exact failure modes before correction and remain present in the final 866-test suite.

No additional material code-quality defect was established in this internal precheck.

## Formal gate blocker

CDC requires the separate final code-quality review to come from a fresh independent reviewer identity after SPEC compliance is GREEN.

A full-diff review PR (#77) was created for the exact final metadata HEAD and GitHub's documented Copilot reviewer `copilot-pull-request-reviewer[bot]` was requested through the review-request API. The request produced no requested reviewer, review submission, review thread, or review comment. This matches the earlier no-op review attempt recorded on PR #69.

No other independent reviewer/subagent backend is available in the current harness. Repeating the unchanged Copilot request would not be an information-gaining recovery.

## Gate state

- final technical SPEC recheck: GREEN
- internal quality hardening/precheck: GREEN
- exact final hosted validation: GREEN twice
- formal fresh independent SPEC reviewer identity: not materialized
- formal fresh independent code-quality reviewer identity: not materialized
- merge: BLOCKED
- release: BLOCKED
- scheduler state: owner-paused and unchanged

Next executable gate is a fresh independent review of the exact source/tree/metadata above. Until that review exists, do not claim the formal review gate, merge, or release.
