# CDC 2.11.2 corrective implementation S1–S5

## Status

**IMPLEMENTATION COMPLETE — READY FOR INDEPENDENT SPEC RE-REVIEW**

This is an implementation report, not an independent SPEC verdict, code-quality verdict, merge/release record, or scheduler-state attestation.

## Exact provenance

- canonical repository: `bajoicheg/g-cdc`
- implementation PR: #69
- implementation baseline branch: `cdc/2.11.2-cooperative-lanes-implementation`
- implementation baseline SHA observed before correction: `0aaa656d3172fdf21b6ab3856a8d4153506ca8ba`
- independently reviewed source: `c63db9a5c18386d0cca2945313ec9314037d31d1`
- reviewed package tree: `d56d4fd0fa2b074e2a6c85ecd2b40e3debc493e2`
- reviewed metadata HEAD: `af45ec793290c1aaf7fff48b7ed5b10b998fb4e5`
- independent review report commit: `3ba2564fac07888fd20cdc5f12a7a9126ab91240`
- review verdict at that target: `CHANGES REQUIRED` (S1–S5, all HIGH)
- corrective continuation branch: `cdc/2.11.2-spec-corrections-20260930-sol-cont2`
- corrective PR used for hosted validation: #72
- continuation base after preserving concurrent corrective commits: `a414218114a09e41128a6abf86daa1af6f37f5c3`
- corrected source SHA: `53793c5f58e201127da409e27bce2bb2f3659cca`
- corrected package tree: `f28d2e040e9a9decb5df997a026d60130e498b46`
- final candidate metadata HEAD: `be1fe4eb813526bd0feed100cf82301e714f2d7e`
- exact-head validation run: `36738700936` — **success**

The implementation branch had advanced 29 commits beyond the independently reviewed source before this correction began. Existing changes were inspected rather than reset. Concurrent useful corrective commits on the first corrective branch were preserved; the final continuation branch was split from their read-back HEAD instead of overwriting them.

## S1–S5 correction map

| Finding | Correction | Adversarial regression/evidence | Final result |
| --- | --- | --- | --- |
| S1 — replacement while stale watchdog may execute | Runtime objects now require object/generation-bound quiescence evidence before destructive replacement. Running/unknown and idle-without-proof materializations remain observational. Recreate performs a fresh safety assessment before generation fencing and another fresh assessment before scheduler I/O; generation change itself is not stop proof. Exact invocation/generation fencing remains mandatory. | `test_missing_canonical_idle_label_without_quiescence_proof_blocks_replacement`; `test_missing_stale_unknown_object_blocks_replacement`; `test_bound_quiescence_proof_allows_stale_object_replacement`; `test_quiescence_proof_must_bind_exact_object_and_generation`; `test_recreate_race_does_not_bump_generation_before_fresh_execution_safety_recheck`; running config/flap/duplicate/invocation-fence regressions. | PASS in final candidate run. |
| S2 — REVIEW/read-only escalation | REVIEW and read-only/review/observer roles have zero write authority; incompatible kind/role/write paths fail validation; executor identity derives from validated capability rather than `bool(write_paths)`; malformed persisted review claims fail before backend start. Lane roles are constrained to an explicit capability schema. | `test_review_kind_cannot_gain_write_authority_from_write_paths`; `test_review_kind_rejects_writer_role_even_without_write_paths`; `test_read_only_role_cannot_carry_write_paths`; `test_review_lane_keeps_read_only_executor_identity`; `test_malformed_persisted_review_claim_never_reaches_writer_backend`; `test_unknown_role_name_is_rejected`; ordinary writer regression. | PASS in final candidate run. |
| S3 — shared product branch reserved to integrator | Admission portable-normalizes branch aliases and rejects ordinary WORKER/FOREGROUND/WATCHDOG writers whose branch is equivalent to `LaneRegistryConfig.product_source_ref` before writer effects; integrator use of the shared branch remains allowed. | `test_shared_product_branch_is_reserved_for_integrator`; short/full-ref, case, and Unicode-normalization alias regressions; existing disjoint concurrent writer demo. | PASS in final candidate run. |
| S4 — truthful conditional publication proof | Git publication now uses a durable `GitDocumentStore` attempt journal bound to operation/result/observed head/intended head/remote/shared ref with prepared/submitted/unknown/confirmed/rejected/aborted states and timestamps. A CAS attempt is persisted before push. Pre-existing intended HEAD without an attempt is readback-only. Lost reply recovery reuses the same durable attempt and never replays push. Explicit rejection stays non-authoritative. `mark_integrated` requires the publisher's durable publication binding and independently re-reads the exact confirmed attempt before queue removal; a returned boolean/evidence mapping alone is insufficient. | Real disposable Git/remotes: normal exact-head lease publication; pre-existing intended HEAD; missing durable attempt store; lost reply + new publisher/no replay; prepared-unsent attempt; other operation/result mismatch; concurrent remote movement/rejection; rejected attempt followed by matching HEAD; readonly verifier; mismatched trusted-attempt readback. | PASS in final candidate run. |
| S5 — fresh migration authority | Every authoritative registry read revalidates the immutable migration evidence through the configured verifier. A restarted coordinator without verifier fails closed; live legacy lease/acquisition drift and evidence-epoch mismatch block authority. | `test_new_coordinator_without_migration_verifier_fails_closed_after_gate`; `test_live_migration_authority_drift_blocks_admission`; `test_live_legacy_acquisition_reenabled_blocks_authority`; `test_live_migration_evidence_epoch_mismatch_blocks_authority`; safe restart/admission regressions. | PASS in final candidate run. |

## RED → GREEN evidence

### Initial S1–S5 RED

Metadata commit `95bf0ecffc081c1977161f1f7ade4ca5dda8083e` bound test-only source `e13a7457ab9647b67705541dd7b5af43376a5550`, package tree `fe2a77d327d994129740ef4f7c71f65f10a86ce5`.

GitHub Actions run `36732360458`:
- repository layout: PASS, 433 tracked paths;
- independent bootstrap: 37/37 PASS;
- full candidate suite: **847 tests, FAILED (17 failures, 4 errors)**;
- failures reproduced S1 stale-idle/generation-race, S2 review/read-only escalation, S3 shared-ref aliases, S4 pre-existing-head/no-durable-attempt proof, and S5 restart/live-drift authority.

### S4 extended RED and integration hardening

Metadata `f29b2380be05cc73e473a9646fe34aa699eb7853` bound source `8047edd324167ca23bc09a5b99a7159e7834a565`, package tree `726696d9eff20fa84e879e61747e3a36b9e2813d`.

Run `36736085241` executed 855 candidate tests and demonstrated that S1/S2/S3/S5 regressions had turned green while the expanded durable-publication tests still failed against the pre-S4 implementation. Additional fixture expectations exposed by the stronger S1/S5 contracts were corrected without weakening those contracts.

### Explicit role-schema RED

Metadata `1b00d89d95b0d3db5eed541866c165751e716cc8` bound source `7e61fe3b98bdcd24b78dda5462b97825263b83f5`, package tree `887060ed27d94713f546e65a536111d253de5c38`.

Run `36738171026`:
- full candidate suite: **862 tests, 861 PASS / 1 FAIL**;
- sole failure: `test_unknown_role_name_is_rejected` because an unknown role did not raise;
- minimal fix: explicit allowed role schema in `project_lanes.py`.

### Final GREEN implementation evidence

Exact final metadata HEAD `be1fe4eb813526bd0feed100cf82301e714f2d7e`, Actions run `36738700936`:
- repository layout: PASS, **433 tracked paths**;
- independent bootstrap contract: PASS;
- bootstrap unittest suite: **37/37 PASS**;
- package validator: **PASS — continuous-development-cycle 2.11.2, 316 files and parsed templates**;
- full candidate unittest discovery: **862/862 PASS**;
- full bootstrap binding: PASS;
- archived consumer snapshots: **3/3 PASS**;
- observed package tree: `f28d2e040e9a9decb5df997a026d60130e498b46`.

Within the full candidate run, the focused groups all passed: **67 `test_project_lane*` tests**, **78 `test_watchdog*` tests**, and **40 `test_fleet_watchdog_runtime` tests**. These were executed by the release workflow's full discovery command rather than by a separate local focused invocation.

## Exact validation commands and results

Commands are the current `.github/workflows/release-validation.yml` commands at the final metadata HEAD:

```text
python -B bootstrap/repository_layout.py
# exit 0 — LAYOUT_GREEN: 433 tracked paths inspected

python -B bootstrap/validate_release.py --mode bootstrap
python -B -m unittest discover -s bootstrap/tests -v
# exit 0 — BOOTSTRAP_GREEN; 37/37 tests PASS

python -m pip install -r src/continuous-development-cycle/scripts/requirements.txt
# exit 0

(cd src/continuous-development-cycle && python -B scripts/validate_package.py)
# exit 0 — PASS: continuous-development-cycle 2.11.2, 316 files and parsed templates

python -B -m unittest discover -s src/continuous-development-cycle/tests -v
# exit 0 — 862/862 PASS
# included 67 project_lane*, 78 watchdog*, and 40 fleet_watchdog_runtime tests

python -B bootstrap/validate_release.py --mode full
# exit 0 — BOOTSTRAP_GREEN

for consumer in g-supervisor g-ad-control g-pc-health-check; do
  python -B src/continuous-development-cycle/scripts/validate_adapter.py "consumer/evidence/$consumer/development-cycle.yaml"
  python -B src/continuous-development-cycle/scripts/validate_checkpoint_24.py "consumer/evidence/$consumer/work-status.md" --adapter "consumer/evidence/$consumer/development-cycle.yaml"
  # candidate version/package-tree/source binding assertion from release-validation.yml
done
# exit 0 — THREE_CONSUMERS_GREEN package_tree=f28d2e040e9a9decb5df997a026d60130e498b46
```

A separate local checkout could not be obtained because the shell environment could not resolve `github.com`; repository reads/writes and exact bytes used the connected GitHub capability, and executable verification used GitHub Actions. No historical GREEN run was substituted for the corrected candidate.

## Changed files from implementation baseline

Production/package:
- `src/continuous-development-cycle/scripts/project_lanes.py`
- `src/continuous-development-cycle/scripts/project_lane_executor.py`
- `src/continuous-development-cycle/scripts/project_lane_runtime.py`
- `src/continuous-development-cycle/scripts/project_lane_git.py`
- `src/continuous-development-cycle/scripts/watchdog_survivability.py`
- `src/continuous-development-cycle/scripts/watchdog_survivability_runtime.py`

Regression tests:
- `src/continuous-development-cycle/tests/test_project_lanes.py`
- `src/continuous-development-cycle/tests/test_project_lanes_extended.py`
- `src/continuous-development-cycle/tests/test_project_lane_executor.py`
- `src/continuous-development-cycle/tests/test_project_lane_registry_binding.py`
- `src/continuous-development-cycle/tests/test_project_lane_git.py`
- `src/continuous-development-cycle/tests/test_watchdog_survivability.py`
- `src/continuous-development-cycle/tests/test_watchdog_survivability_runtime.py`

Candidate bindings:
- `release/candidate.json`
- `consumer/evidence/g-supervisor/source.json`
- `consumer/evidence/g-ad-control/source.json`
- `consumer/evidence/g-pc-health-check/source.json`

Implementation evidence:
- `docs/superpowers/reports/2026-09-30-cooperative-lanes-S1-S5-implementation.md`

Historical consumer `source_commit` values were preserved; only candidate package bindings changed.

## Safety / scope observations

- This implementation session invoked no scheduler enable/run/rebind/recreate actions. The live scheduler fleet was not independently inventoried here, so this report does not claim that no other actor changed scheduler state.
- This implementation session invoked no merge or release operation. It does not claim global repository immutability outside the refs observed during this work.
- Real Git publication behavior was tested only against disposable local Git repositories/remotes inside the candidate test suite.
- The corrected implementation remains cooperative authority enforcement; it does not claim an OS sandbox for arbitrary hostile code.
- PR #69 was not merged by this work, and no release ref was created or changed by this work.
- Independent SPEC re-review and the separate later code-quality review have **not** been performed by this implementation owner.

## Handoff

Fresh independent SPEC re-review should use exactly:
- source: `53793c5f58e201127da409e27bce2bb2f3659cca`
- package tree: `f28d2e040e9a9decb5df997a026d60130e498b46`
- candidate metadata HEAD: `be1fe4eb813526bd0feed100cf82301e714f2d7e`
- validation run: `36738700936` (success)
- this implementation report as implementation evidence only.

Do not treat this report as an independent SPEC or code-quality verdict.
