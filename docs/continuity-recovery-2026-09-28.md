# CDC continuity recovery — 2026-09-28

## Scope and confidence

Investigate repeated premature final responses, repair demonstrated mechanisms, restore consistent release provenance, and update the active personal skill. The owner assigned recovery to this foreground chat and explicitly paused scheduled tasks. They remain paused. Source inspected: `5ff81bc6fc3b515aab22550a192ad522bec0e102`; stable reference: `bafed26bc91fd490c94c37113dc7fcc28340aca9` (2.10.2).

The findings below are source/runtime observations. Full transcripts of prior chats were unavailable in this runtime; retrieved conversation summaries are supporting context only. Neither the first affected historical invocation nor a causal change in a model or Superpowers plugin is proven. The installed package already told agents to continue, so installation drift alone is not a complete explanation.

## Findings

1. **Contradictory finalization rules, reproduced.** At the inspected source, `scripts/execution_continuity.py:80-95` allows progress, external wait or a blocker to bypass `runnable_next_action`. `scripts/execution_lease_v2.py:366-375` consumes this weaker decision. Each case can reach ready/release with work remaining. The defect is already present in released 2.10.2; rolling back to that release alone does not fix it. `scripts/terminal_state_v2.py:55-59` has the correct invariant but is not the finalizer's decision path. Existing tests explicitly expect the unsafe behavior (`tests/test_execution_continuity.py:19-26`, `tests/test_execution_lease_v2.py:10-34`). The skill also contradicts itself: its early durable-control paragraph permits progress boundaries while its later 2.9.2 section forbids them.

2. **Active installation differs from canonical development.** The personal skill actually loaded in this runtime identifies 2.3.5 in VERSION, manifest and SKILL.md. Compared with released 2.10.2: 39 identical files, 16 changed, 211 missing (Git blob comparison). Developing or relabeling the repository did not install the new continuation controls. This is a demonstrated delivery gap, not proof of what every old chat loaded.

3. **2.11 protection was not effective.** The response-string Execution Guard has no production caller and treats unknown text as an action. The added lease check for `plan_only` is unreachable because that state is already rejected by the existing enum validator. Its test is accidentally nested under `tests/src/continuous-development-cycle/tests/`; discovery runs zero of these tests. Direct invocation fails its relative import. A passing string-classifier test is not evidence that a chat continues execution.

4. **Release metadata advanced without release evidence.** Root/package VERSION became 2.11.2 while the manifest stayed 2.10.2. The source lock claimed an unreleased 2.11.1 base and referenced 2.11.2's own stabilization record. The matrix did not support its claimed base. An old 2.10.2 consumer evidence file was overwritten with pending 2.11.2 labels. Candidate package SHA did not match either the declared source commit or HEAD. Baseline: bootstrap 11/12; package 510/524; package validator FAIL. These are source/provenance defects, not GitHub access failure.

5. **Workflow application remains necessary.** These helpers validate caller-supplied state; they do not install a host final-response hook. An executor that does not load/call the correct gate can still stop incorrectly. The repair therefore covers code, early skill instructions, actual installation readback and a bounded agent scenario. It does not claim an unimplemented autonomous runtime.

## Decision and preserved work

Use 2.10.2 as the independent development base and ship corrective **2.10.3**. Restore earlier release evidence byte-for-byte. Preserve the inspected 2.11.2 state at `archive/2.11.2-before-continuity-recovery` and preserve existing 2.11.0 source/review branches and PRs. This is a normal descendant recovery commit, not a history reset or force push.

2.11.0 executor pool, 2.11.1 cooperative lanes, and 2.11.2 watchdog enforcement return to the authorized backlog after recovery. Their staged independent release criteria remain; version labels and experimental branches are not releases. Revisit the pool PRs from their own exact source after recovery, preserving their review history. Rework the detached string guard as real lifecycle behavior if it is still needed; do not redeploy its current classifier.

## Corrective mechanism

- All terminal claims are rejected while another eligible action remains, even with a commit, external binding or blocker.
- Continue/progress are always nonterminal. Finalization requires explicit `final_response_allowed=true`, Terminal-State v2 evidence and the exact persisted checkpoint/invocation. Completion requires separate scope evidence; blockers require fresh blocked-state-proof/v1 and waits retain their recheck action.
- Preflight before entering draining. A task is complete only relative to the original authorized scope; completing one child never empties the other children.
- Genuine waits/blockers and exhausted runtime/budget may hand off only after exhausting eligible work and preserving a real next action. They do not disable or re-enable schedules.
- Put the execution loop and active-package identity check at the top of the skill; existing authorization avoids redundant plan/continue approvals.
- Restore consistent candidate metadata; bind consumer snapshot checks to the actual package tree. Retain their original consumer source commits and deployed-version labels: these are compatibility snapshots, not live migrations.

## Verification record

Before correction, the new real-runtime regression suite ran six tests with seven failing assertions/subtests. After correction it passes; it exercises acquire/finalization/release rather than response wording. It includes a two-action sequence with no intermediate finalization, runnable progress/wait/blocker rejection, genuine completion/wait/blocker success, and checkpoint binding. Full-suite, CI, reviewer and installed-package readback results are recorded with the 2.10.3 release evidence after validation.

## Residual limits

No blanket historical claim that all old stalls had the same cause. No automatic provider hook or perpetual background execution is claimed. Schedules stay owner-paused. Existing 2.11 PRs remain preserved, not merged during recovery. Deployment to other product repositories is a separate safe-boundary rollout; installing the personal skill does not update their vendored packages.

## Independent review correction

The first spec review rejected c6d0a66: a progress reference could still be relabeled as scope completion, a free-form blocker could finalize, and waiting could discard its next action. Three additional RED tests reproduced those paths. The correction binds real finalization to existing Terminal-State v2 and fresh blocker proof, rather than adding another text classifier. No historical or remote evidence is synthesized by the validators.

A separate fresh agent completed an isolated three-step local project using the candidate skill: both requested functions, 4/4 tests, checkpoint and local commit 48cf3c69be34d1b66d7faffc24e4b735349370ee, with a clean worktree. This is bounded smoke evidence, not a guarantee for arbitrary long sessions.
