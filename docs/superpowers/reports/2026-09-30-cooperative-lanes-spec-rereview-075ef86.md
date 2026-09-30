# CDC 2.11.2 specification-compliance re-review — corrected source 075ef86

## Verdict

**VERDICT: SPEC TECHNICAL RECHECK GREEN**

No material specification-compliance finding remains in the exact target below. This is a specification re-check only; it is not the separate code-quality review and not a merge/release verdict.

Reviewer limitation: this review was performed in a new isolated review pass/ref after the R1 correction, but the current harness exposes no fresh reviewer/subagent identity. It therefore must not be represented as an external independent reviewer identity. The technical re-check itself found no remaining material SPEC defect.

No implementation source, scheduler, merge, release, shared product ref or product-runtime state was changed by this review.

## Exact target

- canonical repository: `bajoicheg/g-cdc`
- prior implementation PR: #69
- corrective PR: #72
- R1 corrective PR: #73
- corrected source: `075ef86f21759d50392b3b58fdda252cdce474a7`
- corrected package tree: `dd693f53ed07b870ee45cbe71ff9216b47314303`
- candidate metadata HEAD: `ce5adede534ff760dbc41d99fcd985fb8b71a4be`
- successful exact-head validation run: `36744212026`
- review branch base: `ce5adede534ff760dbc41d99fcd985fb8b71a4be`

The candidate metadata binds exactly the corrected source and package tree above. Hosted validation run `36744212026` completed successfully with repository layout validation, 37/37 independent bootstrap tests, package validation of 316 files/templates, 863/863 candidate tests, full bootstrap binding GREEN, and all three archived consumer snapshots GREEN. The consumer step independently recomputed `HEAD:src/continuous-development-cycle` and reported `THREE_CONSUMERS_GREEN package_tree=dd693f53ed07b870ee45cbe71ff9216b47314303`.

## RED → GREEN evidence for R1

The first R1 test attempt at metadata `8cef95300a3dbd4665a76ffadda6e1b053e7ca07` / Actions `36743165637` failed too early because the broad subprocess monkeypatch also intercepted publication-journal Git operations. That run is retained as diagnostic evidence but is not the accepted behavioral RED for R1.

The test was isolated at source `fa7a251b10f14ba06eabec1d577fff93f858fa6a` and rebound at metadata `779453dfafa7242fcee2d37f88d29af6d9400c7a`. Hosted Actions run `36743680697` then reproduced the intended defect as the sole candidate failure:

- test: `test_remote_failure_porcelain_is_unknown_and_reconciles_without_replay`
- candidate suite: 863 tests, exactly 1 failure
- observed old behavior: `conditional integration publication was explicitly rejected`
- required behavior asserted by the RED: durable `unknown`

Production source `075ef86f21759d50392b3b58fdda252cdce474a7` then corrected the classifier. Exact candidate metadata `ce5adede534ff760dbc41d99fcd985fb8b71a4be` produced hosted GREEN run `36744212026`, including the same regression test and the full 863-test suite.

## Previous S1–S5 disposition

### S1 — CLOSED

No source change since the prior re-review weakens the watchdog quiescence correction. Replacement still requires object/generation-bound quiescence evidence for every extant materialization; generation fencing is not stop proof; fresh observations bracket the destructive replacement path. The full candidate suite remains GREEN.

### S2 — CLOSED

No source change since the prior re-review weakens explicit lane role/capability validation. REVIEW/read-only lanes cannot carry write authority; unknown roles and incompatible review/integrator pairings remain rejected; executor capability remains derived from validated lane semantics. The full candidate suite remains GREEN.

### S3 — CLOSED

No source change since the prior re-review weakens portable shared-ref reservation. Non-INTEGRATOR writers remain unable to claim the configured product source ref through case/full-ref/Unicode aliases. The full candidate suite remains GREEN.

### S4 / R1 — CLOSED

The durable publication-attempt design remains intact, and the residual result-classification defect is corrected.

`GitLaneIntegrationPublisher._push_cas()` now:

1. runs `git push --porcelain --force-with-lease=<exact-ref>:<observed>`;
2. on execution/transport exception, returns the unknown-outcome path;
3. for a non-zero process result, parses only the machine-readable stdout status line for the exact pushed target ref;
4. classifies as explicit terminal rejection only when the exact target line has flag `!` and a summary beginning with `[rejected]` or `[remote rejected]`;
5. classifies every other non-zero result — including `[remote failure]`, malformed/missing per-ref status and generic stderr such as `failed to push some refs` — as unknown.

This matches Git's documented `--porcelain` model: per-ref records are tab-separated machine-readable stdout; `rejected` means Git did not send the ref, `remote rejected` means the remote refused it, while `remote failure` means the remote did not report successful update and can reflect transient remote/network failure.

The retained regression proves the required restart semantics: a `remote failure` plus generic failure stderr persists the same attempt as `unknown`; after the authoritative remote ref is made equal to the intended head, a restarted publisher confirms that same attempt by exact readback and a subclass that raises if `_push_cas` is called proves no publication replay occurs.

Existing explicit-rejection/CAS-race tests also remain GREEN, so the correction does not turn proven refusal into ambiguous success.

### S5 — CLOSED

No source change since the prior re-review weakens migration-gate revalidation. Authoritative reads continue to require fresh verifier evidence equal to the immutable stored gate; restart without verifier and live authority/evidence drift remain fail-closed. The full candidate suite remains GREEN.

## Scope/diff review

Relative to previously re-reviewed source `53793c5f58e201127da409e27bce2bb2f3659cca`, the only production-code change in the package is the R1 classifier correction in `scripts/project_lane_git.py`; the remaining package change is regression coverage in `tests/test_project_lane_git.py`. Metadata changes only rebind the release candidate and three archived consumer snapshots to the corrected package tree.

No new material specification issue was found in that delta.

## Gate state

- S1: closed
- S2: closed
- S3: closed
- S4: closed, including residual R1
- S5: closed
- material open SPEC findings: **0**
- exact hosted candidate/bootstrap/consumer gate: **GREEN**
- external independent reviewer identity: **not available in this harness**
- separate code-quality review: **not yet satisfied**

**SPEC technical re-check is GREEN. Do not merge or release from this report alone. Proceed next to the separate code-quality review gate using a fresh independent reviewer identity when that capability is available.**
