# CDC release process

1. Start from the immutable stable N-1 source lock.
2. Run independent bootstrap validation before candidate imports.
3. Materialize the candidate core under `src/continuous-development-cycle`.
4. Run candidate package/unit/contract tests.
5. Run compatibility and fault-injection suites.
6. Validate the exact candidate package in the registered three-consumer set.
7. Produce a release manifest binding canonical commit and package Git tree.
8. Publish immutable release ref `refs/heads/release/vN`; create a Git tag when the execution channel supports tag creation.
9. Roll out through consumer locks only at safe ownership boundaries.
10. After fleet convergence, migrate `g-cdc` self-hosting policy from N-1 to N.

## CI scope and evidence

Before candidate imports, run `python -B bootstrap/repository_layout.py`.
The gate reads the Git index: stage intended new files before local validation.
Python source is limited to `bootstrap`, `src/cdc27` and
`src/continuous-development-cycle`. Tests discovered by the workflow belong in
`bootstrap/tests` or `src/continuous-development-cycle/tests`. Nested test
directories need tracked `__init__.py` files for unittest discovery on Python 3.12.
Test module filenames must also be accepted by unittest discovery; names such as
`test-hidden.py` or `test.hidden.py` are rejected because discovery skips them.
Python files and nested package markers must be tracked regular files; symlinks
cannot stand in for discoverable modules or package markers.

For the candidate's full commit SHA, read commit status, check runs and Actions
workflow runs. An empty legacy `statuses` array does not establish that CI is
absent. Use `bootstrap/github_ci_state.py --requests OWNER/REPO SHA` to list the
three read URLs. Supply fresh decoded API responses under `statuses`, `checks`
and `actions`, together with `repository` and `head_sha`, to `--snapshot FILE`.
Use null for unavailable reads; do not replace an error with an empty result.
Incomplete inventories cannot prove success or absence. The helper interprets a
caller-supplied snapshot; it does not authenticate it, launch work, authorize
writes, or satisfy release gates.

A draft PR targeting `main` triggers the current workflow. Observe existing runs
and their jobs/logs before starting another run. Verify which candidate paths
were executed: a successful workflow is not proof of unexecuted tests or release
readiness. See [the September 28 incident](ci-execution-recovery-2026-09-28.md).
