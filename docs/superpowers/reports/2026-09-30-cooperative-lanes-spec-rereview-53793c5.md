# CDC 2.11.2 specification-compliance re-review — corrected source 53793c5

## Verdict

**VERDICT: CHANGES REQUIRED**

This is a specification-compliance re-check of the exact corrected candidate, not a code-quality review and not a release verdict.

Reviewer limitation: this review was performed in an isolated review pass/ref after implementation, but the harness exposed no fresh reviewer/subagent identity. It therefore must not be represented as the fresh external identity requested by the previous report. The material finding below independently blocks SPEC-GREEN regardless of that identity limitation.

No implementation source, scheduler, merge, release or product-runtime state was changed by this review.

## Exact target

- canonical repository: `bajoicheg/g-cdc`
- prior implementation PR: #69
- corrective PR: #72
- corrected source: `53793c5f58e201127da409e27bce2bb2f3659cca`
- corrected package tree: `f28d2e040e9a9decb5df997a026d60130e498b46`
- candidate metadata HEAD: `be1fe4eb813526bd0feed100cf82301e714f2d7e`
- successful exact-head validation run: `36738700936`
- report-head validation run from the corrective branch: `36739496946` (success)
- review branch base: `be1fe4eb813526bd0feed100cf82301e714f2d7e`

The candidate metadata binds the corrected source and package tree above. The successful validation run reports 37/37 bootstrap tests, package validation of 316 files/templates, 862/862 candidate tests, full bootstrap binding GREEN and all three archived consumer snapshots GREEN.

## Previous S1–S5 disposition

### S1 — CLOSED by corrected source

The corrected watchdog inventory includes object/generation-bound `quiescence_evidence`. `replacement_quiescence_proven()` requires every extant materialization to be idle/failed and carry exact bound proof before destructive MISSING/config-drift/flapping replacement. `reconcile()` claims the operation first, re-observes before the generation fence, fences only if replacement remains eligible, then re-observes again before scheduler I/O. A generation bump is not used as stop proof.

Adversarial regressions for stale idle without proof, old running/unknown, exact quiescence binding, invocation fencing and the recreate race pass in the final candidate run.

### S2 — CLOSED by corrected source

Lane roles are constrained to an explicit capability schema. REVIEW and read-only/review/observer roles cannot carry write paths; incompatible integrator role/kind pairs are rejected. `LaneClaim.is_writer` cannot promote REVIEW/read-only lanes from write-path presence, and the execution adapter derives review/writer/integrator capability from validated lane semantics. Malformed persisted review claims fail before backend effects.

The final RED added `test_unknown_role_name_is_rejected`; run `36738171026` reproduced it as the sole failure, and the corrected source makes the full 862-test suite GREEN.

### S3 — CLOSED by corrected source

`ProjectLaneCoordinator.admit()` portable-normalizes the candidate branch and `LaneRegistryConfig.product_source_ref`, then rejects non-INTEGRATOR writers that claim the shared product ref before effects. Case/full-ref/Unicode aliases are covered. Shared publication authority is separately bound by `mark_integrated()` to an integration verifier whose `publication_binding.shared_ref` must equal the configured product source ref.

### S4 — PARTIALLY CLOSED; one material finding remains

The corrected source substantially fixes the original finding:

- a dedicated durable `GitDocumentStore` journals publication attempts;
- attempts bind operation, lane, result, observed head, intended head, remote identity and shared ref;
- prepared/submitted/unknown/confirmed/rejected/aborted states are persisted;
- pre-existing intended HEAD without a matching attempt is readback-only;
- a prepared-but-unsent attempt cannot be upgraded by matching readback;
- lost-reply recovery reuses the same attempt and does not replay the push;
- rejected attempts remain non-authoritative even if the remote later equals the intended head;
- `mark_integrated()` requires durable publication binding and independently re-reads the exact confirmed attempt before queue removal.

However, the push result classifier still violates the unknown-outcome contract; see R1 below.

### S5 — CLOSED by corrected source

Every authoritative registry read with a migration gate requires `migration_verifier`, obtains fresh evidence and requires it to equal the immutable stored evidence. A new coordinator without revalidation capability fails closed. Live lease/acquisition-disable drift and evidence-epoch change are covered by regressions and block admission/read authority.

## Material finding

### R1 / S4 — HIGH — generic Git push failure text can convert an unknown publication outcome into terminal rejection

**Requirement**

The design requires unknown publication outcomes to retain the same durable intent/attempt and reconcile from authoritative readback without a second grant. Explicit CAS rejection and transport/remote uncertainty are different states.

**Exact code**

`src/continuous-development-cycle/scripts/project_lane_git.py`, `GitLaneIntegrationPublisher._push_cas()`:

- executes `git push --porcelain --force-with-lease=<ref>:<observed>`;
- on non-zero exit, concatenates stdout/stderr;
- treats any diagnostic containing one of:
  `[rejected]`, `stale info`, `non-fast-forward`, `fetch first`, `remote rejected`, **`failed to push some refs`**
  as `_PublicationRejected`;
- only other non-zero outputs become `_PublicationUnknown`.

**Why this is incorrect**

Git's documented `--porcelain` result model distinguishes:
- `rejected`: Git did not send the ref;
- `remote rejected`: the remote explicitly refused the update;
- `remote failure`: the remote did not report successful update, possibly because of a temporary remote error or a network break.

The trailing human diagnostic `failed to push some refs` is not the authoritative machine-readable classification. Treating that generic phrase as explicit rejection can classify a documented `remote failure` as `rejected`.

Reference: https://git-scm.com/docs/git-push.html (OUTPUT / --porcelain status).

**Deterministic probe**

A `git push --porcelain` result with:
- non-zero return code;
- stdout status for the target ref: `! ... [remote failure] ...`;
- stderr containing the generic summary `error: failed to push some refs ...`

enters `explicit_rejection=True` solely because of the generic stderr phrase. `__call__()` then transitions the durable attempt from `submitted` to terminal `rejected`.

If the remote update actually became authoritative before the connection/reporting failure, a restart later observes `current == intended`, but the attempt remains `rejected`; the publisher correctly refuses to claim conditional proof, so the integration queue/pending effect cannot reconcile automatically. If the update did not occur, the same terminal misclassification still prevents the required unknown-attempt reconciliation path.

This is fail-closed for safety but violates the specified lost-reply/unknown-outcome continuity contract and can permanently stall an otherwise completed project after an ambiguous transport failure.

**Required correction**

Parse the machine-readable `--porcelain` status for the exact pushed ref. Only documented explicit `rejected` / `remote rejected` (and exact lease/stale rejection) should become terminal `rejected`. `remote failure`, missing/ambiguous per-ref status, connection failure, timeout, malformed output, or any case that does not prove explicit refusal must become durable `unknown`.

Add RED→GREEN coverage where a non-zero porcelain result is `remote failure` and generic stderr also contains `failed to push some refs`; assert the attempt becomes `unknown`, not `rejected`, and exact later readback can reconcile without replay.

## Re-check state

- S1: closed
- S2: closed
- S3: closed
- S4: **open residual R1**
- S5: closed
- material open findings: **1 HIGH**

**VERDICT: CHANGES REQUIRED**

Do not proceed to the separate code-quality review yet. Correct R1, run the exact candidate/bootstrap/consumer gates on the newly bound source/tree/metadata, then obtain a fresh specification re-check.
