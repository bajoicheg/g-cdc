# CDC roadmap

## CDC 2.11 — Managed Multi-Executor & Watchdog Resilience — AUTHORIZED / ACTIVE

Owner authorization on 2026-09-27 starts a new CDC line under independently released CDC 2.10.2. The line extends 2.10.2 safe parallelism from isolated implementation workers to a managed multi-executor control plane and makes watchdog continuity a release-grade invariant.

CDC 2.11 preserves staged bootstrap/release discipline:
- develop 2.11.0 under independently released 2.10.2;
- develop 2.11.1 only after 2.11.0 is independently GREEN and released;
- develop 2.11.2 only after 2.11.1 is independently GREEN and released.

All three stages are explicitly authorized by the owner. They may be developed continuously without another approval boundary, but each release still requires its normal independent evidence.

### 2.11.0 — Managed Executor Pool — P0 / AUTHORIZED

Goal: provide a CDC-native analogue of Work-style subagents: one parent invocation can decompose work, launch or bind multiple bounded executors when the runtime supports it, observe them as first-class tasks, and integrate their results without granting workers shared-branch or release authority.

Required controls:
- durable executor-pool plan with parent invocation, exact source HEAD, task DAG, worker role, declared read/write set, expected artifacts/evidence, execution backend, budget and cancellation state;
- bounded parallel slots and per-task cost/runtime budgets; no unbounded worker fan-out;
- every writer receives an isolated branch/worktree contract and exact base SHA; read-only/review workers receive no write claim;
- parent/integrator owns task assignment, result acceptance, retries/replan and final integration;
- worker heartbeat/status/result are explicit durable states (`planned | queued | running | succeeded | failed | cancelled | stale`);
- a worker result is accepted only when identity, base ancestry, write-set containment and required evidence are exact;
- runtime without actual worker-launch capability falls back to the same plan sequentially instead of fabricating subagents;
- workers never gain shared-branch write, merge, release, scope-expansion, scheduler or user-approval authority.

**Dogfood RCA — portable worker result handoff (2026-09-27):** three isolated Codex worker environments completed useful work and local commits but had no configured Git remote/credentials, so a local commit was not a durable GitHub-visible result. Re-running the work would waste compute and weaken evidence lineage.

**Fix formulation:** managed executor attempts must separate **execution result identity** from **publication transport**. A successful worker can return a content-addressed patch/tree/file-set artifact plus base SHA, changed-path manifest and validation evidence when direct push is unavailable. The parent/integrator authenticates that artifact, reconstructs/publishes it on the assigned isolated branch, revalidates the exact remote result, and preserves the original attempt lineage. Missing worker push capability is a transport fallback, not permission to fabricate completion or rerun blindly.

**Expected invariant:** loss of Git remote credentials in a worker environment cannot discard completed work or force duplicate execution; every accepted worker result becomes durable through either direct exact-branch publication or an authenticated parent-mediated result artifact.

**Final-review RCA — contract trust boundaries (2026-09-27):** independent review found that a GREEN implementation test suite still left four trust-boundary gaps, followed by one discriminating-test failure in the correction: caller-supplied changed paths could diverge from the real Git diff; two stale dispatchers could both derive valid in-memory queue states; a content artifact was authenticated without proving the published tree came from it; an optional accepted success could be abandoned at terminal state; and the first artifact-index correction compared against checkout HEAD instead of the declared base.

**Fix formulation:** all writer acceptance now derives changed paths from `base..result` Git bytes and cross-checks the declared manifest/write claim; launch authority is emitted only after durable state compare-and-swap succeeds for a unique reservation token/revision; content handoff verification applies authenticated bytes to an alternate index initialized from the declared base and requires exact published-tree/path equality; every accepted successful result blocks terminal state until integration or explicit optional-result discard; artifact path derivation is explicitly `base -> reconstructed index`, never `HEAD -> index`.

**Defense-in-depth:** these five cases remain focused regressions and are mandatory targets for final source-freeze review. A passing general test suite cannot override an independent RED finding on any of these trust boundaries.

Acceptance:
- at least two independent worker tasks can execute concurrently when a capable backend exists;
- worker failure/staleness does not stop unrelated workers and cannot poison the integration branch;
- parent cannot report terminal while any required worker is runnable/running or an unintegrated successful result remains;
- duplicate launch of the same task/attempt is rejected or reconciled;
- cancellation and retry preserve exact attempt lineage rather than silently replacing evidence;
- a deterministic sequential fallback produces the same required task/evidence set.

**RCA reinforcement — portable worker-result handoff.** During 2.11.0 dogfooding, three Codex workers completed isolated local commits but their execution checkouts had no configured Git remote/credentials, so a local commit could not become a durable GitHub-visible result by `git push`.

**Fix formulation:** executor preflight must classify writeback capability separately from compute capability. Every managed worker completion must provide a durable, content-addressed result transport that the parent/integrator can consume even when the worker cannot push: exact commit/tree when remotely reachable, or an authenticated patch/tree/artifact bundle plus base SHA, write-set and evidence bindings. Missing worker push capability is a handoff mode, not a reason to rerun completed work. Integrator publication remains subject to normal ownership and exact-result validation.

**Expected invariant:** successful worker computation cannot be stranded solely because its execution environment lacks a Git remote; one completed attempt maps to one durable transferable result identity, and recovery publishes/reconstructs that exact result instead of recomputing it.


### 2.11.1 — Cooperative Project Lanes — P1 / AUTHORIZED

Goal: allow the foreground user chat and one or more watchdog/Work/Codex executors to make useful progress on the same repository at the same time without reverting to split-brain shared writers.

Required controls:
- replace project-wide mutual exclusion for ordinary work with durable **execution lanes**: each active executor declares identity, surface, exact observed HEAD, role and portable read/write claims;
- non-overlapping writer lanes may coexist; read-only/review lanes may coexist with writers;
- overlapping portable write claims serialize; a reserved shared-branch/integration lane remains exclusive;
- user chat and watchdog remain independently alive: starting foreground work does not disable/pause the watchdog, and a watchdog encountering an occupied lane chooses another runnable non-conflicting task or observer/review work;
- existing valid claims are never stolen merely because foreground work has higher urgency; handoff/preemption requires a safe checkpoint plus explicit quiescence of the relinquished lane;
- every lane heartbeat requires new observable activity; TTL/staleness alone never proves the executor stopped;
- shared HEAD movement is reconciled before integration; no executor force-pushes around another;
- terminal evaluation is project-scope aware: one idle lane cannot make the project terminal while runnable work exists in another lane/queue.

Acceptance:
- foreground chat + watchdog can both be `running` on one project with disjoint write claims and no ownership contradiction;
- overlapping claims deterministically block/serialize before either writer mutates the same portable path;
- one executor can finish/release its lane without releasing or invalidating other active lanes;
- watchdog stays scheduled while foreground execution is active;
- integrator remains the only shared-branch writer and validates all accepted lane results against fresh HEAD.

### 2.11.2 — Persistent Watchdogs & Fleet Wake Enforcement — P2 / AUTHORIZED

Goal: make an unexpectedly idle or disabled watchdog a critical recoverable control-plane fault whenever the project is not truly terminal.

Required controls:
- watchdog desired state is **enabled until verified project terminal state**. `disabled + nonterminal` is critical drift, not a normal pause;
- a watchdog invocation that ends after a primitive/milestone while runnable work remains is a liveness failure and must persist/requeue continuation state;
- runtime/time-budget exhaustion ends only the current wake; it must leave a durable continuation for the next wake and must not disable the recurring watchdog;
- scheduler enabled state, actual invocation state, meaningful progress, execution lanes, external guards and project terminal evidence remain separate signals;
- `watchdog_health` gains explicit critical liveness classification for disabled/overdue/prematurely-completed watchdogs with runnable project work;
- `watchdog_self_repair` may re-enable and/or request a run only under a durable owner-authorized liveness policy and only after duplicate-run/active-owner/external-submission safety checks;
- Fleet Watcher evaluates **all** registered projects each run and repairs/kicks every wrongfully resting watchdog that is eligible, rather than merely recommending one action;
- Fleet Watcher never wakes a watchdog proven terminal and never bypasses product write ownership, external-operation idempotency, merge/release or budget gates;
- a true terminal project may leave its project watchdog disabled; terminal proof must be fresh and exact, not inferred from quietness, TTL or a completed invocation.

Acceptance:
- disabled watchdog + runnable project => `CRITICAL`/recovery and an authorized enable/run action when scheduler control is available;
- completed watchdog invocation + runnable work => immediate continuation/requeue, not healthy idle;
- Fleet Watcher can return and execute a bounded batch of eligible watchdog wake repairs in one pass;
- active watchdog/executor is not duplicated;
- external `submitting|queued|running|unknown` state prevents duplicate external work while still allowing safe observation/reconciliation;