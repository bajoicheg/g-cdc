# CDC 2.11.2 post-R1 specification-compliance re-check

## Status

**TECHNICAL SPEC RE-CHECK: NO OPEN MATERIAL FINDINGS**

**PROCESS GATE: FRESH INDEPENDENT REVIEWER IDENTITY STILL REQUIRED**

This report separates technical findings from the process requirement. The corrected source below has no material specification mismatch found in this isolated post-fix re-check, but this harness exposes no fresh reviewer/subagent identity. Therefore this report does **not** claim that the project requirement for a fresh independent SPEC-GREEN verdict has been satisfied.

This is not a code-quality review, merge verdict, release verdict, or scheduler-state attestation.

## Exact target

- canonical repository: `bajoicheg/g-cdc`
- original implementation PR: #69
- R1 corrective PR: #73
- corrected source: `075ef86f21759d50392b3b58fdda252cdce474a7`
- corrected package tree: `dd693f53ed07b870ee45cbe71ff9216b47314303`
- candidate metadata HEAD: `ce5adede534ff760dbc41d99fcd985fb8b71a4be`
- exact-head release-validation run: `36744212026` — **success**
- review branch base: `ce5adede534ff760dbc41d99fcd985fb8b71a4be`

Candidate validation evidence at the exact metadata HEAD:
- repository layout: 433 tracked paths, PASS;
- independent bootstrap: 37/37 PASS;
- package validator: CDC 2.11.2, 316 files/templates, PASS;
- full candidate suite: **863/863 PASS**;
- full bootstrap binding: PASS;
- three archived consumer snapshots: 3/3 GREEN;
- observed package tree: `dd693f53ed07b870ee45cbe71ff9216b47314303`.

## Prior findings disposition

### S1 — CLOSED

Destructive watchdog replacement requires exact object/generation-bound quiescence evidence for extant materializations. The runtime re-observes after durable claim before generation fencing and again before scheduler I/O. Running/unknown/stale-idle-without-proof cases remain non-destructive. Invocation fencing remains exact generation/object/safety-bound.

### S2 — CLOSED

REVIEW/read-only/observer claims cannot carry write paths or become writer execution. Integrator role/kind is constrained. Arbitrary role names are rejected by an explicit role schema. Backend identity is derived from validated capability.

### S3 — CLOSED

Ordinary writer lanes cannot claim a portable-equivalent configured product/shared ref before effects. Shared publication is bound independently to the configured product source ref through the trusted integration publication binding.

### S4 — CLOSED in this technical re-check

The durable publication-attempt model remains bound to operation/lane/result/observed head/intended head/remote/shared ref. Pre-existing intended HEAD is non-authoritative without a matching attempt. Prepared-unsent and rejected attempts cannot be upgraded by coincidental readback. Unknown attempts reconcile from exact authoritative readback without replay. `mark_integrated()` independently reads the exact confirmed durable attempt before removing the queue item.

The R1 correction removes the generic stderr heuristic. `_push_cas()` now interprets only the machine-readable `git push --porcelain` status row for the exact target ref as explicit rejection:
- `[rejected]` -> terminal rejected;
- `[remote rejected]` -> terminal rejected;
- `[remote failure]`, malformed/missing target status, connection/timeout/subprocess failures -> durable unknown.

This matches Git's documented distinction between explicit refusal and remote/transport uncertainty.

Official behavior reference: https://git-scm.com/docs/git-push.html

### S5 — CLOSED

Every authoritative lane-registry read after migration-gate establishment requires fresh verifier evidence and exact immutable binding equality. Restart without verifier, legacy lease/acquisition drift and evidence-epoch drift fail closed.

## R1 RED → GREEN

### RED

Test-only source:
- `fa7a251b10f14ba06eabec1d577fff93f858fa6a`
- package tree: `d1e46a12a2f2b0c3597b1a40484acf4e57422f54`
- metadata HEAD: `779453dfafa7242fcee2d37f88d29af6d9400c7a`
- run: `36743680697`

The run reached the full candidate suite and executed **863 tests**. Exactly one test failed:

`test_remote_failure_porcelain_is_unknown_and_reconciles_without_replay`

Observed pre-fix result: `ValueError: conditional integration publication was explicitly rejected`, while the test required the documented remote-failure path to be `unknown`.

### GREEN

Corrected source:
- `075ef86f21759d50392b3b58fdda252cdce474a7`
- package tree: `dd693f53ed07b870ee45cbe71ff9216b47314303`
- metadata HEAD: `ce5adede534ff760dbc41d99fcd985fb8b71a4be`
- run: `36744212026` — success

The regression passes:

`test_remote_failure_porcelain_is_unknown_and_reconciles_without_replay ... ok`

Existing explicit rejection/concurrency regressions also remain green, including:

- `test_concurrent_remote_move_during_cas_is_rejected_without_overwrite`
- pre-existing intended-head readback-only case;
- lost-push-reply restart/no-replay reconciliation;
- durable-attempt requirement;
- prepared-unsent and operation/result mismatch cases.

Full candidate result: **863/863 PASS**.

## Scope / safety

- No scheduler enable/run/rebind/recreate action was invoked by this review/fix loop.
- No merge or release operation was performed.
- Real conditional publication behavior in tests used disposable local Git repositories/remotes.
- No live product/shared ref was published by the test suite.
- Historical consumer source commits were preserved; candidate package-tree bindings were updated to the exact corrected package.

## Gate conclusion

Technical material findings from S1–S5 plus residual R1: **0 open**.

However, the previous project contract explicitly requires a **fresh independent SPEC reviewer identity** before the separate code-quality review. The current harness cannot provide that identity.

Therefore:

- technical re-check: **NO OPEN MATERIAL SPEC FINDINGS**
- independent SPEC-GREEN process gate: **OUTSTANDING**
- independent code-quality review: **NOT STARTED**
- merge/release: **NOT AUTHORIZED BY THIS REPORT**

A fresh independent reviewer should re-check exactly:
- source `075ef86f21759d50392b3b58fdda252cdce474a7`
- package tree `dd693f53ed07b870ee45cbe71ff9216b47314303`
- metadata HEAD `ce5adede534ff760dbc41d99fcd985fb8b71a4be`
- validation run `36744212026`.
