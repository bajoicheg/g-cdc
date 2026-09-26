# Worktree-Isolated Parallel Development & Single Integrator

CDC 2.10.2 adds safe concurrency as an execution-quality layer. It does not change CDC authority, runtime routing or ownership rules.

## Runtime boundary

Parallel writer delegation is available only when the actual orchestration runtime already permits subagents/writers, such as ChatGPT Work or Codex orchestration under the project policy. Ordinary ChatGPT chat remains sequential. Planning a parallel wave never creates worker-launch authority.

## Parallel DAG and write-set planning

`scripts/parallel_task_planner.py` turns a dependency DAG into execution waves. Tasks may be `writer`, `read_only` or `review`. Writers declare bounded relative write paths; read-only/review tasks declare none.

Independent ready writers may share a wave only when their write sets do not overlap by exact or ancestor/descendant path. Overlapping ready writers are serialized into later waves. Cyclic dependencies are rejected. The planner reports sequential and parallel estimates for observability only and never launches workers.

## Isolated worker/worktree contract

`scripts/worktree_worker_contract.py` binds every delegated task to:

- durable worker and task identity;
- exact common base SHA;
- isolated branch and worktree identity;
- execution wave;
- write set for writers;
- expected outputs and evidence;
- an explicit prohibition on shared-branch writes.

The CDC integrator is not a delegated worker. Same-wave writer overlap is invalid. Read-only/review workers may not claim write paths.

## Single-integrator gate

`scripts/integration_gate.py` evaluates terminal worker results before integration. It requires the shared branch to remain at the expected base, all workers to succeed on that base, writer result paths to remain non-overlapping, spec-compliance and code-quality review to be GREEN, no unresolved conflicts and no force-push request.

A GREEN result is only `READY_FOR_INTEGRATOR`. The gate creates no shared-branch write, merge or release authority. The integrator must still re-read HEAD, use normal concurrent-writer reconciliation, assemble the candidate, and then pass CDC 2.10.1 branch-finishing plus CDC 2.10.0 verification-before-terminal gates.

Failed or stale worker output is discarded/rebased/re-run in isolation. It is never force-pushed or partially integrated merely to preserve effort already spent.

## Observed parallel benchmark

`scripts/parallel_benchmark.py` validates observed performance evidence. A benchmark is GREEN only when a representative task has at least two workstreams, measured parallel elapsed time is lower than the sequential baseline, and unresolved conflict/rollback counts do not regress.

Estimated planner savings are not release evidence by themselves. CDC 2.10.2 release evidence must include at least one observed multi-workstream benchmark with durable evidence refs.

## Superpowers relationship

Superpowers contributes worktree isolation, task decomposition, bounded delegation, independent review and a single integration point. CDC remains authoritative for scope, ownership, execution eligibility, shared writes, merge/release and terminal state.

## Release evidence

CDC 2.10.2 release evidence must prove:

- dependency cycles are rejected;
- independent non-overlapping writers can share a wave;
- overlapping writer paths are serialized or rejected when assigned to the same wave;
- every writer is pinned to an isolated branch/worktree and exact base SHA;
- no delegated worker can write the shared branch;
- stale/failed worker results cannot pass the integrator gate;
- shared HEAD movement forces reconciliation rather than force-push;
- final integration remains evidence-only until normal review/verification/release gates pass;
- an observed representative multi-workstream benchmark reduces wall-clock time without increasing unresolved conflicts or rollbacks.
