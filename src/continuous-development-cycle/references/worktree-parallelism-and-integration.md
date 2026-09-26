# Worktree-Isolated Parallel Development & Single Integrator

CDC 2.10.2 adds safe concurrency as an execution-quality layer. It does not change CDC authority, runtime routing or ownership rules.

## Runtime boundary

Parallel writer delegation is available only when the actual orchestration runtime already permits subagents/writers, such as ChatGPT Work or Codex orchestration under the project policy. Ordinary ChatGPT chat remains sequential. Planning a parallel wave never creates worker-launch authority.

## Parallel DAG and write-set planning

`scripts/parallel_task_planner.py` turns a dependency DAG into execution waves. Tasks may be `writer`, `read_only` or `review`. Writers declare bounded relative write paths; read-only/review tasks declare none.

Independent ready writers may share a wave only when their write sets do not overlap by exact or ancestor/descendant path under a portable case-folded Unicode-normalized identity. This prevents Linux-only case distinctions from creating collisions on Windows/macOS. Overlapping ready writers are serialized into later waves. Cyclic dependencies are rejected. The planner reports sequential and parallel estimates for observability only and never launches workers.

## Isolated worker/worktree contract

`scripts/worktree_worker_contract.py` is **per-wave**. The contract embeds the immutable planner input in addition to a durable plan reference, recomputes the selected wave, and requires the assignment set plus role/write-set/output/evidence contract to match that wave exactly. Before each wave starts, it binds every delegated task in that wave to:

- durable worker and task identity;
- exact common base SHA;
- isolated branch and worktree identity;
- the wave's exact current base SHA;
- write set for writers;
- expected outputs and evidence;
- an explicit prohibition on shared-branch writes.

The CDC integrator is not a delegated worker. Same-wave writer overlap is invalid. Read-only/review workers may not claim write paths. A later writer wave is contracted only after the prior writer wave has been integrated/reconciled, so it receives the new exact shared-branch base instead of inheriting a stale original base.

## Single-integrator gate

`scripts/integration_gate.py` evaluates terminal results for **one wave** before the single integrator assembles that wave onto the shared integration branch. The integration input embeds the exact worker contract for that wave. The gate cross-checks worker/task/role/base identity and requires every changed path to remain inside that worker's assigned write set. It also requires the shared branch to remain at the wave's expected base, all workers to succeed, no unresolved conflicts and no force-push request.

A GREEN result is only `READY_FOR_INTEGRATOR`. The gate creates no shared-branch write, merge or release authority. Every successful writer carries a `git_diff_name_only` proof bound to worker/task/base/result and the **complete** changed-path set. Real integration invokes the gate with `--git-worktree`, which resolves both commits and re-computes the Git diff; `--contract-only` exists only for package fixtures/tests. The integrator must still re-read HEAD and use normal concurrent-writer reconciliation before the separately authorized assembly write. If the current wave is not the final planned wave, the gate routes to `integrate_wave_then_contract_next_wave_on_fresh_head`; only after all implementation waves are assembled does it route to CDC 2.10.1 spec/code review and branch finishing, then CDC 2.10.0 verification-before-terminal.

Failed or stale worker output is discarded/rebased/re-run in isolation. It is never force-pushed or partially integrated merely to preserve effort already spent. A successful worker result must satisfy the delegated output/evidence contract; successful writers must report a new result SHA plus changed paths inside the assigned write set, while read-only/review workers must remain at the base SHA.

## Observed parallel benchmark

`scripts/parallel_benchmark.py` validates observed performance evidence. A benchmark is GREEN only when a representative task has at least two workstreams, measured parallel elapsed time is lower than the sequential baseline, and unresolved conflict/rollback counts do not regress.

Estimated planner savings are not release evidence by themselves. The benchmark contract contains exactly one structured sequential observation and one structured parallel observation. Both must be marked observed, bind the same exact candidate SHA, environment, plan and `sha256:` workload fingerprint, and carry distinct durable evidence refs. Timings are derived from those observations; arbitrary top-level timing labels are not accepted. Estimates and observed timings must be finite positive numbers; NaN and infinities are invalid evidence. CDC 2.10.2 release evidence must include at least one actually measured multi-workstream benchmark with those bindings.

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
