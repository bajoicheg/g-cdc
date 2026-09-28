# CDC 2.11.2 implementation plan

This is the final implementation stage of the owner's approved recovery plan. Execute only after 2.11.1 is released, installed and read back. The design is `docs/superpowers/specs/2026-09-28-cooperative-lanes-design.md`. Do not treat completion of 2.11.1, a child task or a review as the parent terminal boundary. All owner-paused schedulers stay paused.

## Task 1: project lanes and executable lifecycle

Use one isolated implementation worker for the coupled contract/runtime rather than inventing two incompatible state machines. Own new `scripts/project_lanes.py`, `scripts/project_lane_runtime.py`, their tests, templates and references. Reuse the released Git document CAS, raw-object Git environment, portable path overlap checks and process backend where appropriate. Preserve existing global-lease and managed-pool contracts.

First retain failing real-Git/process scenarios for disjoint writers, portable overlap, configuration drift, CAS contention, duplicate worktree/branch, stale-owner theft, fake heartbeat, cross-invocation release, independent release, unknown starts, touched-and-restored path escape, source movement and premature completion. Implement exact bound admission, safe legacy migration, effect journaling, result acceptance and conditional integration. A writer cannot become its own shared-branch integrator. An idle lane cannot authorize project finalization. A real local process demonstration must show concurrent foreground/watchdog-labelled lanes without any scheduler mutation.

Keep all provider boundaries explicit. Read-only observations or caller labels do not manufacture live host authority. A backend must independently observe exact processes/effects; unknown outcomes retain claims. Do not modify arbitrary user validation command environments or promise OS-level fencing.

## Task 2: parent integration and release

The parent alone integrates and writes remote refs. Advance the independent driver to released 2.11.1; version package metadata and transport fixtures atomically. Add package integrity requirements, fault scenarios and SKILL guidance that invokes the actual lane lifecycle. Keep historical deployment evidence distinct from compatibility snapshots.

Run focused checks and complete package/bootstrap/three-consumer gates at the final source identity. Obtain ordered independent spec and quality reviews of the whole coupled lifecycle, resolve material findings, then publish the exact source and evidence. CI must pass at the exact final metadata head before merge. Create/read back the immutable release ref, then activate/read back the personal skill.

## Task 3: live authority and safe rollout

Re-read the Fleet authority and atomically migrate its target documents plus immutable release companion to the latest completed release. Preserve project identities and scheduler pause. Exercise target resolution against genuine pinned remote data; no reconstructed commit may impersonate the remote revision.

Re-read consumer source/coordination. Adopt the final release only in a consumer with a legitimately available lease; acquire, checkpoint, reconcile and release the exact invocation. Preserve explicit blockers for consumers whose existing owners have no independent stop proof. Refresh the read-only scheduler inventory and close superseded backlog entries, retaining original history.

## Budget and continuity

Create a separate ledger for this new approved release task only after 2.11.1 completion; preserve its predecessor ledger. Agent-start cap 8, at most 2 active workers, checkpoint reserve 3000 tokens/15 calls, provider consumption unknown. Reserve every agent or CI start before the effect. One implementation task and ordered reviews minimize handoff churn; fixes and scoped rechecks consume the same budget. Budget exhaustion never permits relabelling the task or skipping a required gate.

Final response requires all eligible approved work completed, exact release/activation evidence, honest ownership blockers and the existing execution-continuity gate. No scheduled wake or automation restart is part of this plan.
