# CDC canonical development instructions

This repository develops CDC itself.

## Implementation entry point and CI observations

After repository/access inspection, execute the next eligible action from the authorized plan in the same invocation. Inspection alone is not completion. Before concluding that implementation is absent, inspect relevant branches, pull requests, checkpoints and available worktrees; an unchanged `main` is insufficient evidence.

Repository access, local command execution and hosted CI are separate capabilities. A missing local shell does not establish that GitHub Actions is unavailable. For the exact candidate SHA inspect all three surfaces: commit status, check runs and Actions workflow runs. `bootstrap/github_ci_state.py --requests OWNER/REPO SHA` lists the read endpoints; `--snapshot FILE` reconciles their decoded responses. Failed reads must be recorded as null, and incomplete pagination remains unknown. Inspect run jobs, steps and logs before deciding what a run actually validated. Reuse an existing run rather than launching a duplicate.

The current release workflow triggers on pull requests to `main`, including drafts. Inspect the workflow definition before treating a missing dispatch tool as a blocker. Continue through authorized execution routes and other eligible work. If all eligible work is blocked, report the attempted operation, observed error or missing capability, and the exact remaining action. Successful CI only supports the files and checks it actually covers.

Core implementation belongs under `src/continuous-development-cycle`; independent development tooling belongs under `bootstrap`. Run `python -B bootstrap/repository_layout.py` after staging new files. The release workflow rejects misplaced Python code/tests before candidate imports. These checks protect repository validation; they cannot intercept arbitrary ChatGPT final responses or guarantee that another chat continues.

## Bootstrap rule

CDC N is developed under the previously released CDC N-1. CDC 2.10.2 is released at `refs/heads/release/v2.10.2`, package tree `2bee3b8159aaf80de981afba7cf284f21bafa1c3`.

CDC 2.11.3 is the current released development authority at `refs/heads/release/v2.11.3`, frozen source `7f31544ffd80252587b7ff1bd76b9a3f38e019e5`, package tree `39f733127ac130de4f647cf9e5ec55afcca0769c`. It was developed under released CDC 2.11.2. A new version line requires explicit roadmap authorization and must preserve the independent-bootstrap rule.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

The source release is CDC 2.11.3. The last retained personal-skill runtime-byte acceptance record is still `release/active-package-acceptance-2.11.0.json`; source release alone does not prove activation. Consumer snapshots prove compatibility only; they do not update consumers' vendored packages. See `release/evidence-2.11.3.json` and `docs/roadmap.md`.

## Recovery priority

CDC 2.11.3 completes the currently authorized 2.11 source-release sequence and closes the multi-subscription ownership-integrity patch scope. Live Fleet authority migration, safe consumer rollout and personal-skill activation/readback remain separate evidence surfaces. Do not infer deployment from a source release or VERSION. No task/milestone/commit is a final-response boundary while authorized runnable work remains. Schedulers remain owner-paused; recovery grants no authority to re-enable them.
