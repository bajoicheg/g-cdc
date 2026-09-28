# CDC 2.11.1 watchdog and live target design

The owner approved this stage and uninterrupted execution through 2.11.2. Develop under released 2.11.0 (5865399c2ddc0cb9c84fd8ebad207612d6e6e02b, package 06078676bef395c56453f9e9066b4c0583c84ba3). The installed package has been independently read back. All live project schedulers remain owner-paused.

## Scope

1. A fresh liveness contract separates scheduler, exact invocation, project runnable work/terminal proof, owner/guard, progress and explicit owner pause. Disabled/overdue or completed invocation with runnable work is CRITICAL unless a current explicit pause overrides liveness. Unknown facts fail closed. Quietness, TTL and completion of a child task never prove project completion or owner quiescence.
2. A bounded Fleet runtime examines every registered project and executes every eligible recovery within the batch budget. Durable conditional claims precede scheduler side effects. Unknown/lost replies cannot be replayed. Re-read policy/owner/pause before every effect, including between enable and run. Existing active/uncertain invocation, owner or external submission prevents duplicate starts. Backend capabilities are actual supplied adapters; no fabricated host API. Preserve schedules/prompts and require exact readback. Paused projects create no scheduler effects.
3. Resolve the registry and target from one fresh exact Git revision, then verify target against immutable canonical release/version/package evidence. Reject stale/future evidence, disagreement, moved refs and untrusted canonical identity. Prompts refer to live project policy and canonical registry authority, never a mutable version copied into prompt text. Safe-boundary consumer adoption remains separate.
4. Durable continuation persists across wake budget exhaustion and premature invocation completion. State/operation keys bind project/ref/watchdog/incident rather than only current invocation. CAS uses unique proposals, non-force updates, exact endpoint identity and a coordination ref isolated from product refs.

## Acceptance and limits

Real local Git integration tests exercise separate-controller contention, restart after claim, unknown provider response, all-project batch recovery, bounded remainder, pause before/between effects and active owner/guard suppression. Fresh target tests use actual Git objects/refs and release provenance. Preserve prior schemas/readers where possible; new contracts explicitly version changed schemas. Run retained 2.10.3 and 2.11.0 regressions plus bootstrap and three archived consumers. Independent spec then quality review precede exact-head CI/release.

This is a cooperative orchestrator, not a sandbox or platform final-channel interceptor. A generic adapter can exercise actual effects only where a caller provides real authorized capabilities. This session will use recording/local test backends, never enable or run the owner's paused automations. Live owner claims in three consumers remain blockers for those adoptions only.
