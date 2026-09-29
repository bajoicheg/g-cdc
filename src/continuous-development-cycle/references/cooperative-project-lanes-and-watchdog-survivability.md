# Cooperative project lanes and watchdog survivability

CDC 2.11.2 extends the released managed executor pool and watchdog liveness controls without granting new product-write or scheduler authority.

## Cooperative lane invariants

- Each lane binds executor + invocation + generation + exact source HEAD + surface/role + portable read/write claims + isolated branch/worktree.
- Non-overlapping writers may coexist. Portable case/Unicode/ancestor overlap serializes before effects.
- Read-only/review lanes may coexist with writers on pinned snapshots.
- Exactly one integrator may own the shared-branch integration lane.
- Foreground work does not pause the watchdog. A blocked watchdog chooses non-conflicting runnable or observational work.
- Claims are not stolen for urgency. Handoff/recovery requires checkpointed independently verified quiescence; TTL/silence is insufficient.
- Heartbeat requires a new activity reference plus independent observable-activity evidence; caller-generated labels alone are not heartbeat proof.
- Writer acceptance validates base ancestry and every touched path in every introduced commit, including touched-and-restored paths.
- Normal release is executor/invocation/generation-bound, drains pending effects and persists an exact checkpoint reference.
- Computed/accepted work remains nonterminal until required integration is complete.
- Before any shared-ref publication, the integrator persists a one-shot durable integration intent. Unknown publication outcomes retain that intent for readback/reconciliation rather than creating a new effect grant.
- Fresh shared-HEAD movement is reconciled before publication; force-push is forbidden. Integration is removed from the queue only after an independent verifier proves the claimed operation and records durable integration evidence.

## Watchdog survivability invariants

The durable desired-state record, not a scheduler object ID, defines whether a watchdog must exist. The runtime inventory may classify the materialization as HEALTHY, OVERDUE, DISABLED_DRIFT, MISSING, CONFIG_DRIFT, DUPLICATE, FLAPPING or EXECUTION_BROKEN. Intentional owner pause and exact terminal proof are separate non-recovery states.

A recovery effect is legal only when desired state requires an enabled watchdog, no fresh owner pause supersedes it, project state is freshly runnable, owner/guard are released, external work is absent or reconciled, scheduler pause state permits recovery, and the durable recovery policy contains explicit owner authorization.

Missing/configuration-drift/flapping recreation advances desired generation before scheduler I/O. Any old generation is then fenced by `execution_is_current`. Lost/unknown provider outcomes retain their durable operation claim and require inventory reconciliation rather than replay.

Duplicate materializations are disabled only after the canonical object is known, and at most one duplicate scheduler effect is consumed per project reconciliation step. A post-claim owner stop is re-read before I/O and blocks the effect. A currently running watchdog is never kicked a second time merely because its last-run timestamp is old. Unknown run replies reconcile only from a run timestamp observed at or after the durable operation claim.

Fleet recovery may compose `WatchdogSurvivabilityRuntime` with `FleetRuntime`. Every registered desired watchdog is assessed, while scheduler mutations share a bounded fleet effect budget; exhausted repairs remain continuation work. An unresolved scheduler effect prevents desired-generation replacement, so missing/lost replies cannot be erased by configuration churn.

A scheduler backend must be genuinely available and authorized; CDC cannot manufacture one.

## Terminal aggregation

Project completion is project-wide. Runnable or active lanes, unknown/pending effects, queued runnable work and unintegrated required results all keep the project nonterminal. Watchdog survivability state contributes evidence but never replaces execution-continuity/finalizer evidence.

## Current rollout constraint

Owner-paused schedulers remain paused. Implementing survivability does not itself authorize enabling, recreating or running them.
