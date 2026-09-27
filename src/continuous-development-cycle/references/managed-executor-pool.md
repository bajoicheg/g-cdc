# Managed executor pool

CDC 2.11.0 adds a managed executor pool above the CDC 2.10.2 worktree and single-integrator controls. It is intentionally analogous to Work-style subagents without pretending that every runtime can launch independent workers.

## Parent authority and bounded delegation

The parent invocation remains the CDC orchestrator for the authorized change. It owns task decomposition, backend selection within existing policy, attempt/retry decisions, result acceptance, integration routing and terminal-state evaluation.

A child executor receives only the task contract already authorized for it. It never inherits shared-branch write, merge, release, scope-expansion, scheduler-mutation or user-approval authority. Worker output is evidence for the parent/integrator; it is not an integration decision.

The pool is bounded by an explicit maximum parallelism and by runtime/cost budgets. Do not fan out work merely because concurrency is available. Prefer independent tasks whose expected wall-clock benefit exceeds delegation and integration overhead.

## Capability-gated execution and truthful fallback

Actual parallel worker launch is capability-gated. Work, Codex or another orchestration backend may execute multiple pool tasks concurrently only when the current runtime actually exposes that capability and higher-priority policy permits it.

When worker launch is unavailable, execute the **same managed pool plan** through deterministic sequential fallback. Preserve task identity, dependencies, write sets, expected outputs/evidence and attempt lineage. Serialization may change timing and dispatch order only; it must not silently drop requirements or replace the planned evidence.

Never fabricate subagents, worker heartbeats, parallel start times or worker results. A runtime that cannot launch workers reports sequential fallback explicitly.

Already-authorized pool tasks do not require a fresh user approval for every child launch when runtime and project policy allow delegation. This removes conversational approval loops; it does not create new scope or authority.

## Isolation and one integration point

Every writer is pinned to an exact base SHA and an isolated branch/worktree. Writer contracts carry portable, case-folded Unicode-normalized write claims. Read-only and review executors carry no write claim.

Independent non-overlapping writer tasks may run together. Overlapping portable write sets are serialized or replanned before dispatch. Workers never write the shared product/integration branch.

One integrator remains the only shared-branch writer. It independently checks result identity, exact base/ancestry, changed-path containment, required evidence and fresh shared HEAD before accepting an unintegrated worker result.

## Durable attempts and results

Each task attempt is durable and observable with explicit identity and lifecycle:

`planned -> queued -> running -> succeeded | failed | cancelled | stale`.

A heartbeat requires a new observable activity reference. Polling the same provider state or merely advancing time is not activity.

A retry creates a new attempt identity and points to its predecessor. Failure, cancellation or staleness never overwrites the old attempt evidence. Two active attempts for the same pool task are a duplicate-launch fault and must be reconciled before another start.

A successful writer result remains `integrated=false` until the single integrator accepts it. It binds the exact pool/task/attempt/base, result commit, changed paths and evidence refs. Changed paths outside the declared portable write set fail closed.

Failure of one worker does not cancel unrelated independent work. Other safe tasks continue while the failed required task is retried, replanned or explicitly dispositioned.

## Terminal-state relationship

Pool progress is not terminal progress. The parent cannot return COMPLETE while any required task is runnable, queued or running, while a required failed/stale task still needs recovery, or while a successful required result remains unintegrated.

Optional work may be omitted only through an explicit pool decision; already-running optional work must be drained or cancelled before the pool itself can close.

A worker completing one task, a parent reporting a milestone, or a validation subset becoming GREEN does not end the CDC invocation. The parent immediately continues observe -> reconcile -> choose-next -> act until the project-level terminal gate accepts a real boundary.

## Release evidence

CDC 2.11.0 release evidence must prove at minimum:

- two independent tasks can be active concurrently on a capable backend;
- the same pool plan falls back deterministically to sequential execution when capability is absent;
- duplicate task attempts are rejected or reconciled;
- worker failure does not stop unrelated independent tasks;
- required runnable/running or unintegrated-success state prevents parent terminal completion;
- isolated writer results cannot escape their declared portable write sets;
- all managed-pool outputs keep shared-branch, merge, release, scope, scheduler and user-approval authority false.
