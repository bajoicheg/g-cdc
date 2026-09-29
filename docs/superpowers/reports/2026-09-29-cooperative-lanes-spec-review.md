# CDC 2.11.2 specification review and corrective closure

Reviewed cooperative-lanes source through package source commit `7da65fbc887590632d841d851c700bec2ab2c47a`, package tree `f23211101e4497c7c3b52d2f2c57fea3b7b77e6d`, against `docs/superpowers/specs/2026-09-28-cooperative-lanes-design.md` and the 2.11.2 implementation plan.

Verdict: **GREEN after corrective findings below**. This is a specification-compliance review; code-quality and release/CI gates remain separate.

## Findings reproduced and corrected

### S1 — lane release was not checkpointed or executor-bound

The initial coordinator permitted a running lane to release using lane + invocation + generation only. The design requires executor/invocation/generation binding, drained effects and a durable checkpoint.

Correction: lifecycle mutations now bind executor identity; normal release requires a non-empty checkpoint reference and preserves an existing handoff checkpoint exactly. Regressions reject cross-executor release and missing checkpoint.

### S2 — heartbeat accepted caller-generated labels as activity

The initial heartbeat accepted any new string, which did not satisfy the requirement that heartbeat represent new observable activity.

Correction: heartbeat now requires an independent activity verifier returning the exact activity reference plus evidence. Replay of the same activity remains rejected.

### S3 — integration queue could be cleared without a durable integration intent

The initial `mark_integrated` path could remove a result from the integration queue solely because an integrator lane was active. The configured integration verifier was not used and no pre-effect intent was durable.

Correction: the integrator first claims a one-shot durable integration intent for the exact lane/result and observed shared HEAD. The intent is idempotent and retained across unknown outcomes. Queue removal requires fresh independent verification binding the same operation ID, result commit, observed shared HEAD, integrated HEAD and no-force ancestry. `GitLaneIntegrationVerifier` provides a read-only real-Git implementation that proves both the pre-publication shared HEAD and result commit are ancestors of the current shared ref.

### S4 — owner-pause disagreement and already-running watchdog could permit unsafe recovery

A fresh `owner_pause_evidence` paired with an inconsistent scheduler `pause=running` was not itself sufficient to suppress repair. An already-running watchdog whose last-run timestamp was old could also be classified OVERDUE and receive another run request.

Correction: fresh owner-pause evidence independently suppresses self-heal. A current running materialization is never kicked again from timestamp age alone. Current-execution fencing also requires required/enabled state plus exact generation, schedule and template digest.

### S5 — uncertain run effects were not reconcilable and desired-state replacement could erase them

Create/enable/disable uncertain effects had readback paths, but an uncertain run claim could remain permanently unreconciled. A newer desired generation could also replace an entry and clear unresolved operation history.

Correction: run readback requires a materialization run timestamp at or after the durable operation claim. Claimed/unknown effects block desired-state replacement until reconciled.

### S6 — survivability repair was not fleet-bounded

The first all-registered reconciliation could consume an unbounded number of scheduler effects, especially when quiescing duplicates, and it was not composed with the existing Fleet recovery effect budget.

Correction: every registered desired watchdog is still assessed, while scheduler mutations are bounded by `max_effects`; duplicate cleanup consumes at most one scheduler effect per project reconciliation step. `FleetRuntime` can compose an authorized survivability runtime and shares one total effect budget between materialization repair and ordinary liveness recovery. Deferred/broken repair remains continuation work.

## Requirement coverage

- Disjoint foreground/watchdog writer lanes coexist; portable path overlap and branch/worktree reuse fail before writer effects.
- Existing claims are not stolen by urgency; handoff requires checkpoint plus independent quiescence.
- Heartbeat is evidence-bound rather than TTL/token-bound.
- Writer-result acceptance checks exact base ancestry and all paths touched across introduced history.
- Successful worker computation remains queued until evidence-backed single-integrator reconciliation.
- Project terminal aggregation counts active lanes, runnable work, pending results and unknown effects.
- Missing/disabled/overdue/config-drifted/duplicate/flapping watchdog materializations are classified from fresh desired/actual state.
- Missing/config/flapping recreation fences generation before scheduler I/O.
- Owner pause, project terminal state, active execution and unresolved effects fail safe.
- Fleet materialization repair is bounded and does not manufacture scheduler authority.

No scheduler was enabled or run by this review. Owner-paused scheduler state remains authoritative.

Final release remains contingent on the separate code-quality review, final exact-head validation, release evidence, immutable release ref and active-package readback.
