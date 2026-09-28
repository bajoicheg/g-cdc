# CI execution and coverage recovery, 2026-09-28

## Observed incident

[PR #69](https://github.com/bajoicheg/g-cdc/pull/69), at head
`0ddeaac476dde1625448b5ec97a885a53549f480`, introduced these files:

- `scripts/project_lanes.py`
- `scripts/project_lane_runtime.py`
- `tests/test_project_lanes.py`

The release workflow only discovered candidate tests under
`src/continuous-development-cycle/tests`. It therefore skipped the new root
test. [Actions run 36406335587](https://github.com/bajoicheg/g-cdc/actions/runs/36406335587)
was created at 2026-09-28T09:53:29Z for this PR head and completed successfully.
The reported empty legacy commit-status list was not evidence that no execution
backend existed. Checks and Actions runs are separate evidence surfaces.

This establishes an evidence-reading error and a validation coverage gap. It
does not establish why a model stopped or prove that prior context caused it.

## Bounded correction

The independent bootstrap and release workflow now reject tracked Python code
outside canonical source roots and tests outside the executed test roots. Nested
tests require tracked package markers so Python 3.12 discovery can reach them.
Test filenames skipped by discovery, such as `test-hidden.py`, are rejected.
The gate runs before candidate imports and uses only the standard library.

The advisory GitHub CI snapshot helper considers commit status, check runs and
Actions runs for the requested SHA. Empty legacy statuses cannot conceal a
running workflow. Missing reads, incomplete pagination and conflicting results
remain explicit. Even a successful workflow observation is not a release claim.

Repository startup instructions require continuing with eligible authorized work
after inspection and checking branches/worktrees before declaring code absent.
They do not provide a platform-level mechanism to force ChatGPT to continue.

Regression tests first failed with the missing gates, then passed after the
implementation. They cover PR #69's misplaced paths, undiscovered nested tests,
empty and partial CI inventories, mismatched workflow/SHA and conflicting
observations. The existing independent bootstrap tests remain part of the suite.

Local verification of this correction passed:

- 34 independent bootstrap tests, including the new regressions;
- 740 candidate package tests;
- repository placement, full independent bootstrap and package validation;
- all three archived consumer snapshot validations, bound to unchanged package
  tree `6ffacd32cce74c3537150778d9b37cfeb361a621`.

The helper was also exercised against fresh GitHub responses for PR #69's SHA:
zero legacy statuses, one successful check and one successful Actions run yielded
`workflow_succeeded`, with `release_ready` still false. The initial independent
review found the filename-discovery gap; its regression failed before correction
and passed afterwards. Hosted validation of this correction must be observed on
its own PR head; the earlier PR #69 run is incident evidence only.

## Remaining development

This correction does not alter the released CDC 2.11.1 package, release 2.11.2,
or enable paused schedulers. PR #69's draft and the separate existing local
cooperative-lanes worktree must retain their provenance. Identical filenames do
not mean equivalent implementations. Cooperative-lane implementation, review,
package tests and release evidence remain separate work under the approved plan.
