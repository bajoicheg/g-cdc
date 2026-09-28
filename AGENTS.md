# CDC canonical development instructions

This repository develops CDC itself.

## Implementation entry point and CI observations

After repository/access inspection, execute the next eligible action from the authorized plan in the same invocation. Inspection alone is not completion. Before concluding that implementation is absent, inspect relevant branches, pull requests, checkpoints and available worktrees; an unchanged `main` is insufficient evidence.

Repository access, local command execution and hosted CI are separate capabilities. A missing local shell does not establish that GitHub Actions is unavailable. For the exact candidate SHA inspect all three surfaces: commit status, check runs and Actions workflow runs. `bootstrap/github_ci_state.py --requests OWNER/REPO SHA` lists the read endpoints; `--snapshot FILE` reconciles their decoded responses. Failed reads must be recorded as null, and incomplete pagination remains unknown. Inspect run jobs, steps and logs before deciding what a run actually validated. Reuse an existing run rather than launching a duplicate.

The current release workflow triggers on pull requests to `main`, including drafts. Inspect the workflow definition before treating a missing dispatch tool as a blocker. Continue through authorized execution routes and other eligible work. If all eligible work is blocked, report the attempted operation, observed error or missing capability, and the exact remaining action. Successful CI only supports the files and checks it actually covers.

Core implementation belongs under `src/continuous-development-cycle`; independent development tooling belongs under `bootstrap`. Run `python -B bootstrap/repository_layout.py` after staging new files. The release workflow rejects misplaced Python code/tests before candidate imports. These checks protect repository validation; they cannot intercept arbitrary ChatGPT final responses or guarantee that another chat continues.

## Bootstrap rule

CDC N is developed under the previously released CDC N-1. CDC 2.10.2 is released at `refs/heads/release/v2.10.2`, package tree `2bee3b8159aaf80de981afba7cf284f21bafa1c3`.

CDC 2.10.3 was developed under released CDC 2.10.2. After the corrective release, CDC 2.11.0 is now released and is the current development authority at `refs/heads/release/v2.11.0`, commit `5865399c2ddc0cb9c84fd8ebad207612d6e6e02b`, package tree `06078676bef395c56453f9e9066b4c0583c84ba3`. A new version line requires explicit roadmap authorization and must preserve the independent-bootstrap rule.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

The installed personal skill is converged on released CDC 2.11.0, with runtime-byte readback and documented host metadata normalization. Consumer snapshots prove compatibility only; they do not update consumers' vendored packages. See `release/evidence-2.10.3.json` and `docs/roadmap.md`.

## Recovery priority

CDC 2.10.3 is the corrective release developed under released 2.10.2. Unreleased 2.11 work is preserved in the backlog, `archive/2.11.2-before-continuity-recovery` and existing `cdc/2.11.0-*` branches; consult `docs/continuity-recovery-2026-09-28.md`. Do not infer a release from VERSION. No task/milestone/commit is a final-response boundary while authorized runnable work remains. Schedulers remain owner-paused; recovery grants no authority to re-enable them.
