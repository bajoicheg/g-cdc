# Continuous execution recovery implementation plan

> Use superpowers:executing-plans inline. Owner authorized recovery and possible rollback; no additional approval boundary is needed. Schedulers remain paused by owner request.

**Goal:** prevent milestone finalization while executable work remains, repair the active installed skill, and preserve unfinished 2.11 work.

**Architecture:** recover source from released 2.10.2 without rewriting history; publish corrective 2.10.3 under that release. The lease finalizer must consume an explicit final-response decision, not a generic progress result. Keep completed release evidence immutable.

**Tech Stack:** Python stdlib, unittest, PyYAML, Git, GitHub Actions.

**Spec:** the 2026-09-28 owner request and docs/roadmap.md Progress-Is-Not-Terminal invariant.

## Global constraints
- A commit, subset test, report or child task does not complete the authorized scope.
- Runnable work prevents progress, waiting or blocker claims from terminating the invocation.
- Genuine exhausted runtime/budget may checkpoint and hand off; it does not prove project completion or authorize scheduler enable/disable.
- Keep 2.11 source/history in archive/2.11.2-before-continuity-recovery and existing branches; no force push.
- No new scheduler starts. The foreground executor has the owner's sole recovery assignment.

## Review focus
- Progress plus runnable next action; waiting/blocker plus unrelated runnable work.
- Completed child task vs completed scope; fake progress without real completion evidence.
- A real wait/blocker after all eligible local work is exhausted.
- Exact invocation/checkpoint binding at lease finalization.
- Installed skill version and package bytes vs merely changing repository labels.

### Task 1: Correct the finalization boundary
Files: scripts/execution_continuity.py, scripts/execution_lease_v2.py, tests/test_execution_continuity.py, tests/test_execution_lease_v2.py, tests/test_continuity_recovery.py under src/continuous-development-cycle.
- [x] Add end-to-end failing tests for milestone, wait and blocker bypasses and exact checkpoint binding.
- [x] Run the tests and retain baseline RED.
- [x] Add explicit final_response_allowed; reject finalization for progress/continue or remaining runnable work. Preserve valid COMPLETE/WAIT/BLOCKED paths.
- [x] Migrate positive fixtures to actual completed-scope or eligible wait/blocker boundaries, then run focused tests and package suite.

### Task 2: Recover release truth and active guidance
Files: VERSION, package manifest/SKILL.md, release/source.lock.json, compatibility/matrix.json, README.md, AGENTS.md, docs/roadmap.md, docs/continuity-recovery-2026-09-28.md.
- [ ] Restore stable metadata/history; mark 2.11 incomplete/backlog with exact preserved refs.
- [ ] Put the continuation loop and active-version check at the front of SKILL.md; remove contradictory milestone-terminal wording.
- [ ] Add executable discovery/release binding checks; verify package tree after source freeze.
- [ ] Validate bootstrap, package, fault/behavioral cases and all three consumer snapshots.

### Task 3: Review, integrate and activate
- [ ] Independent spec review then code-quality review; fix material findings with regression tests.
- [ ] Push bounded candidate, open PR for exact-SHA Actions validation, observe to terminal and merge only GREEN.
- [ ] Publish immutable 2.10.3 release with actual evidence; update installed personal skill and verify byte identity after saving.
- [ ] Leave scheduler state unchanged and record residual limits honestly.

## Rulings and evidence
- The request authorizes inline recovery, local worktree, Git integration and updating the user's CDC skill; no new product scope or scheduler authority is inferred.
- Baseline main 5ff81bc: bootstrap 11/12, package 510/524, package validation FAIL. Installed CDC 2.3.5.
- Native prior chat transcripts are unavailable; historical start time and a causal Superpowers attribution cannot be established from summaries.

Task 1 complete: real-runtime RED (6 tests, 7 failing assertions/subtests) → GREEN; package suite 522/522. Source freeze 9ea87e08ed363634c94e70d33367ef00df3531f0, package ce9bfb5383fd13e3a104e19fd30205339fd553f1.
