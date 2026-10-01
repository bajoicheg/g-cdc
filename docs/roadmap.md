# CDC roadmap

## CDC 2.10.3 — Continuous execution recovery — RELEASED

Owner-directed corrective priority (2026-09-28): retain stable 2.10.2 capabilities, reject milestone finalization while eligible work remains, bind lease completion to the real final-response decision, restore immutable prior evidence, and verify the installed skill against the released package. Current 2.11 progress remains preserved at `archive/2.11.2-before-continuity-recovery` (5ff81bc) and existing source/review branches. At the recovery boundary no 2.11 stage was released; current stage status is recorded below. Schedulers remain explicitly paused.

Acceptance: real acquire→finalization regressions RED→GREEN; candidate/manifest/source lock/version/tree agree; full bootstrap/package/three-consumer validation; independent review; installed package readback. See `docs/continuity-recovery-2026-09-28.md`.

Evidence: 525/525 package tests, 17/17 independent bootstrap tests, package validator PASS, 3/3 archived consumer snapshots, spec and code-quality review PASS, GitHub Actions run `36383383699` GREEN for `fd11ff5`, and installed runtime-byte readback against package tree `a1fdca8c4a00409069b790e6dd13944e64fbf9bd` (host metadata normalization recorded in release evidence). The recovery release changes no live consumer deployment or scheduler state. Release ref: `refs/heads/release/v2.10.3`; integration: PR #66.

## CDC 2.11 — Managed Multi-Executor & Watchdog Resilience — COMPLETE / TERMINAL

Initial owner authorization on 2026-09-27 started CDC 2.11 under released 2.10.2. The 2026-09-28 recovery plan resumes it under 2.10.3 and puts watchdog liveness before cooperative lanes. The line extends 2.10.2 safe parallelism from isolated implementation workers to a managed multi-executor control plane and makes watchdog continuity a release-grade invariant.

CDC 2.11 preserves staged bootstrap/release discipline:
- resume 2.11.0 under independently released corrective 2.10.3 (initial work used 2.10.2);
- develop 2.11.1 only after 2.11.0 is independently GREEN and released;
- develop 2.11.2 only after 2.11.1 is independently GREEN and released.

All four owner-authorized 2.11 stages are released. On 2026-10-01 the owner authorized the fourth patch stage, CDC 2.11.3, after live multi-subscription rollout exposed an orphan-lease/fleet-leadership integrity gap. No further 2.11 stage is authorized; a new version line requires explicit roadmap authorization.

### 2.11.0 — Managed Executor Pool — P0 / RELEASED

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

Acceptance:
- at least two independent worker tasks can execute concurrently when a capable backend exists;
- worker failure/staleness does not stop unrelated workers and cannot poison the integration branch;
- parent cannot report terminal while any required worker is runnable/running or an unintegrated successful result remains;
- duplicate launch of the same task/attempt is rejected or reconciled;
- cancellation and retry preserve exact attempt lineage rather than silently replacing evidence;
- a deterministic sequential fallback produces the same required task/evidence set.

Release: `refs/heads/release/v2.11.0`, integration PR #67, frozen source `ffc64490e069318221e2c0d05996d39ed231fd46`, package tree `06078676bef395c56453f9e9066b4c0583c84ba3`. Evidence: 656 package tests, 17 independent bootstrap tests, validator286files,3archivedconsumer snapshots, independent spec/quality closure, exact package CI `36389114227` at `9136058` plus final metadata-head gate. See `release/evidence-2.11.0.json`. This stage is a milestone; authorized2.11.1/2.11.2 remain runnable after its release.

### 2.11.1 — Persistent Watchdogs & Fleet Wake Enforcement — P1 / RELEASED

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
- no watchdog may self-disable merely because one wake, task, PR, validation step or status report completed;
- scheduler disable is acceptable without incident only after verified project `COMPLETE` (or a fresh explicit owner stop that intentionally supersedes this liveness policy).

Release: `refs/heads/release/v2.11.1`, integration PR #68, frozen source `a29fb4221b63bff9ecac4e1b8c821f6c25ca7c0c`, package tree `6ffacd32cce74c3537150778d9b37cfeb361a621`. Full validation: 740 package tests, 18 independent bootstrap tests, 299 required files/templates and three archived consumers PASS. Ordered spec and quality reviews closed durable wake, transport isolation and raw Git object/ancestry findings. Candidate CI `36394984137` GREEN; final metadata head has a separate required CI gate. See `release/evidence-2.11.1.json`. Owner pause remains authoritative; this release starts no scheduler. Authorized cooperative lanes remain the next stage.

### 2.11.2 — Cooperative Project Lanes — P2 / RELEASED

Goal: allow the foreground user chat and one or more watchdog/Work/Codex executors to make useful progress on the same repository at the same time without reverting to split-brain shared writers.

Required controls:
- replace project-wide mutual exclusion for ordinary work with durable **execution lanes**: each active executor declares identity, surface, exact observed HEAD, role and portable read/write claims;
- non-overlapping writer lanes may coexist; read-only/review lanes may coexist with writers;
- overlapping portable write claims serialize; a reserved shared-branch/integration lane remains exclusive;
- user chat and watchdog remain independently alive: starting foreground work does not disable/pause the watchdog, and a watchdog encountering an occupied lane chooses another runnable non-conflicting task or observer/review work;
- actual worker launch is bound to lane admission: a one-shot durable start claim is committed and re-read before any isolated-worktree/process backend effect; unknown starts retain the claim and are observed rather than replayed;
- existing valid claims are never stolen merely because foreground work has higher urgency; handoff/preemption requires a safe checkpoint plus explicit quiescence of the relinquished lane;
- every lane heartbeat requires a new activity reference plus independent observable-activity evidence; TTL/staleness or a caller-generated token alone never proves the executor is alive;
- normal lane release is executor/invocation/generation-bound, drains pending effects and persists an exact checkpoint reference;
- before any shared-ref integration effect, the single integrator persists a one-shot durable integration intent; queue removal requires fresh exact verification of the claimed no-force integration against the observed and resulting HEAD;
- shared HEAD movement is reconciled before integration; no executor force-pushes around another;
- terminal evaluation is project-scope aware: one idle lane cannot make the project terminal while runnable work exists in another lane/queue;
- watchdog runtime objects are replaceable materializations of durable desired state: missing, disabled, overdue, configuration-drifted, duplicate and flapping watchdogs are explicitly classified;
- a required missing watchdog on a nonterminal project may be recreated only after fresh owner/guard/external/pause gates and durable owner-authorized recovery policy; recreation advances generation before scheduler I/O so late old instances are fenced;
- lost/unknown scheduler effects are reconciled by exact post-claim readback and are never blindly replayed; already-running watchdogs are never kicked again from timestamp age alone; unresolved effects cannot be erased by desired-generation replacement;
- Fleet supervision assesses every registered desired watchdog while survivability repair and ordinary liveness recovery share one bounded scheduler-effect budget; deferred/broken repairs remain durable continuation work;
- a minimal independent Fleet Supervisor Sentinel may reconcile only the durable `fleet-supervisor` materialization through the same generation-fenced desired-state runtime; it is not a second Fleet controller and has no product-write authority; diverse-provider HA for the Sentinel is deferred beyond 2.11.2;
- fresh explicit owner pause/stop and exact project-terminal proof suppress watchdog self-heal; owner-paused schedulers remain paused unless that owner state changes.

Acceptance:
- foreground chat + watchdog can both be `running` on one project with disjoint write claims and no ownership contradiction;
- the real-process concurrency demonstration proves durable lane admission and start claim precede both worker launches; lost/unknown worker start cannot produce a duplicate launch;
- overlapping claims deterministically block/serialize before either writer mutates the same portable path;
- one executor can finish/release its lane without releasing or invalidating other active lanes;
- watchdog stays scheduled while foreground execution is active;
- integrator remains the only shared-branch writer; integration requires a durable pre-effect intent and independent exact-HEAD/no-force verification before an accepted result can leave the queue;
- deleting a required nonterminal watchdog is detected as `MISSING` and, when recovery is authorized and safe, results in one fenced-generation recreation plus exact readback;
- an old watchdog generation that later wakes cannot become current execution authority; duplicate recovery never produces two authoritative watchdogs;
- all registered desired watchdogs are assessed even when the repair budget is exhausted, while actual scheduler effects stay bounded and unfinished repair remains continuation work;
- when an independent scheduler backend is available, deleting the Fleet Supervisor materialization can be recovered by the Sentinel without granting project-development or product-write authority;
- explicit owner pause is stable under reconciliation and cannot be undone by survivability repair.

Release: `refs/heads/release/v2.11.2`, frozen source `6af4443b1afa86085622625bee9b62a045a08a07`, package tree `7a7a7faa75b7fc9160d912d8fb507c6b9573d17f`. Final technical SPEC recheck and internal quality hardening found no remaining material technical defect; exact-head hosted validation runs `36749087759` and `36750000629` are GREEN with 866/866 candidate tests, 37/37 independent bootstrap tests, package validator 316 files/templates, full bootstrap binding, and 3/3 archived consumers. The owner explicitly authorized a one-time exception for the unavailable fresh independent-reviewer identity requirement on this exact candidate; the waiver is recorded in `release/owner-review-waiver-2.11.2.json` and does not relabel the skipped independent stages as GREEN or weaken future review policy. Schedulers remain owner-paused and this release performs no live consumer deployment.

Expected benefit: CDC moves from “safe parallel tasks” to a resilient multi-executor development system: useful work continues concurrently, foreground and watchdog execution cooperate instead of excluding each other, and fleet supervision actively restores projects that are idle for the wrong reason.

### 2.11.3 — Multi-Subscription Coordination & Ownership Integrity — P0 / RELEASED

Goal: make several independent ChatGPT subscriptions safe as one CDC execution pool while preserving exactly one Fleet Supervisor side-effect leader and closing the orphan-lease / partial-adoption defect class reproduced during the 2.11.2 live rollout.

Required controls:
- dedicated Git-CAS Fleet Supervisor state embedding invocation-bound `execution-lease/v2`; one leader generation may emit Fleet-wide effects while other subscriptions remain standby observers or project executors;
- one-shot Fleet effect journal binding effect ID, exact leader owner/generation/invocation and exact observed Fleet HEAD; duplicate intent observes/reconciles and intent collision fails closed;
- leader replacement requires exact stopped-executor/quiescence evidence and no unresolved claimed/submitted/unknown effects; TTL alone never elects a replacement;
- independent runtime liveness classification: `active` requires exact runtime-running evidence plus a fresh lease, while stopped clean owners become `orphaned_recoverable`, pending effects become `blocked_unknown_effects`, unproven runtime is `unknown`, and no owner is `released`;
- fail-closed final-response gate: any invocation that acquired a lease must prove exact owner/generation/invocation release and post-release execution-continuity state before terminal response;
- atomic consumer adoption: package, lock, adapter, checkpoint and adoption/provenance state are assembled detached, exact target subtree is verified, then one expected-head conditional fast-forward and exact readback publishes the target; partial VERSION/metadata exposure is forbidden.

Acceptance:
- two supervisors racing from the same coordination revision produce at most one CAS leader;
- duplicate wake/repair/enqueue effect cannot produce two submissions;
- unknown prior effect blocks standby takeover, while terminal reconciled effects plus exact executor-stopped evidence permit a new generation;
- an owner record without exact runtime evidence is never reported as active;
- final-response gate is RED while exact acquired ownership remains and GREEN only after exact release;
- interrupted adoption before publication leaves the shared consumer ref unchanged;
- moved source/Fleet HEAD replans instead of force-updating;
- #81 is closed only after these regressions remain GREEN in release validation.

Authority boundary: Fleet leadership is control-plane only; it never grants project product-write, project takeover, merge, release, scope expansion or scheduler authority beyond separately authorized effect policy.

Tracking: issue #82; systemic RCA #81. Design: `docs/superpowers/specs/2026-10-01-multi-subscription-coordination-design.md`; plan: `docs/superpowers/plans/2026-10-01-cdc-2.11.3.md`.\n\nRelease: `refs/heads/release/v2.11.3`, frozen source `7f31544ffd80252587b7ff1bd76b9a3f38e019e5`, package tree `39f733127ac130de4f647cf9e5ec55afcca0769c`. Candidate validation is GREEN with 950/950 package tests, 37/37 independent bootstrap, package validator 331 files/templates, full bootstrap binding and 3/3 archived consumers. Historical Stage 1 RED remains truthful with all findings remediated; the exact-candidate fresh Stage 1 re-review and independent Stage 2 requirement were each skipped once by explicit owner waiver and are not relabeled GREEN. Release finalization retains a separate exact-head hosted CI gate before immutable ref creation. Schedulers remain owner-paused and this release performs no live consumer deployment.

## CDC 2.10 — Superpowers Execution Quality — COMPLETE / TERMINAL

Owner acceptance authorizes this roadmap. CDC 2.10 integrates the strongest Superpowers engineering disciplines as a **quality layer** under the CDC control plane. Superpowers workflows never grant ownership, external-start, merge, release, scheduler, scope-expansion or user-approval authority; CDC remains authoritative for those controls.

CDC 2.10 preserves staged bootstrap/release discipline:
- develop 2.10.0 under independently released 2.9.2;
- develop 2.10.1 only after 2.10.0 is independently GREEN and released;
- develop 2.10.2 only after 2.10.1 is independently GREEN and released.

The line is intentionally limited to three releases: first prove CDC behavior itself, then enforce specification/review quality, then safely increase parallelism.

### 2.10.0 — Behavioral Skill TDD & Verification Gate — P0 / RELEASED

Goal: make CDC behavior testable as an executable contract instead of relying only on prose, unit tests and post-hoc RCA.

- Add a behavioral/pressure-scenario eval harness for CDC skills, inspired by Superpowers skill TDD: establish baseline behavior, demonstrate the failure mode, apply the skill/control change, then prove the corrected behavior and retain the scenario as regression coverage.
- Convert high-value real CDC failures into behavioral evals, starting with:
  - premature stop after a milestone while runnable work remains;
  - provider terminal while durable guard still says running;
  - schema-invalid checkpoint control values;
  - duplicate command timestamp within one user command;
  - stale checkpoint ownership contradicting newer live coordination lease;
  - repeated unchanged recovery strategy after infrastructure/setup failure.
- Integrate systematic-debugging semantics into RCA: evidence collection → root-cause hypothesis → discriminating test → correction → defense-in-depth → deduplicated roadmap disposition.
- Add a mandatory verification-before-terminal-state gate. Before any success/COMPLETE claim, independently re-read the exact authoritative state needed for that claim: source HEAD/tree, required tests/evidence, checkpoint binding, lease/guard, artifact identity and clean state where applicable.
- Verification is evidence-only: it may reject completion but never grant missing authority.

Acceptance:
- every behavioral scenario has an explicit baseline RED/undesired outcome and corrected GREEN outcome;
- a skill/control change cannot close its fault scenario without a retained regression eval;
- COMPLETE cannot be emitted from stale checkpoint or cached provider evidence when a fresher authoritative source exists;
- a provider-terminal/stale-guard scenario reconciles without TTL-only takeover;
- typed checkpoint violations and duplicate timestamps are caught before a final response;
- repeated infrastructure/setup failures cannot trigger an unchanged retry strategy;
- behavioral evals run deterministically enough to serve as release evidence, with nondeterministic cases explicitly bounded and classified.

Expected benefit: CDC regressions become reproducible before fleet rollout, and “the instruction says so” is replaced by evidence that the agent actually behaves correctly under pressure.

Release: `refs/heads/release/v2.10.0`.
- candidate validation HEAD: `3a02384deb0ef9b6d9352c508c506a414d28290c`;
- package tree: `63f25fb7402bf07d2e037de88194b7359c9e0f93`;
- independent evidence: PR #11 comment `5849842887` — bootstrap 12/12, package 397/397, aggregate 409/409, 227 files, behavioral 6 RED→6 GREEN, 41 fault scenarios, 50 pressure scenarios and 3/3 consumers GREEN.
- GitHub Actions attempts on the same candidate failed pre-run with zero executable steps and were classified as execution-channel infrastructure; no source correction was made from those runs.

### 2.10.1 — Specification Compliance & Two-Stage Review — P1 / RELEASED

Goal: distinguish “tests are GREEN” from “we implemented the requested thing correctly and well.”

- Make Superpowers-style specification work first-class for new or scope-changing product work: concise design/spec → implementation plan → executable CDC continuation queue.
- Preserve selective brainstorming only for genuinely ambiguous product/design choices. Routine implementation, bug fixes and already-authorized continuation must not be forced through unnecessary human clarification.
- Introduce mandatory two-stage independent review for material changes:
  1. **spec-compliance review** — does the implementation satisfy the approved request/spec and avoid scope drift?
  2. **code-quality review** — is the implementation maintainable, safe, testable and appropriately simple?
- Reviewers are evidence/recommendation roles by default. They do not gain shared-branch write, merge, release or product-decision authority.
- Map plan tasks to exact evidence and continuation state so “plan complete” cannot be inferred from prose alone.
- Standardize finishing-development-branch behavior: fresh validation, diff/spec reconciliation, unresolved-review check, exact candidate binding, cleanup and only then CDC terminal/release handling.

Acceptance:
- material implementation cannot pass quality review before spec-compliance is GREEN;
- a change that is technically correct but violates the approved spec remains non-terminal;
- every plan task can be traced to an implementation/evidence state or an explicit blocker;
- review findings are either fixed, explicitly dispositioned, or retained as blockers before terminal completion;
- brainstorming never becomes a mandatory approval loop for unambiguous continuation work;
- branch finishing cannot discard open review findings, stale validation or ownership/guard state.

Expected benefit: fewer “GREEN but wrong” outcomes, especially for UI/UX and cross-cutting behavior where automated tests alone are insufficient.

Release: `refs/heads/release/v2.10.1`.
- candidate validation HEAD: `5f3e75847db9c4651bacdc36d44ec1eaa79ecbd1`;
- package tree: `07bea03a6cc23f658c1cefe41aba40c174474f25`;
- independent evidence: PR #12 comment `5849987854` — bootstrap 12/12, package 418/418, aggregate 430/430, 227 validated files/templates, 14/14 targeted review assertions, 45 fault scenarios, 58 numbered pressure scenarios and 3/3 consumers GREEN.
- GitHub Actions run `36272377691` failed before executable steps and was classified as `pre_run_infrastructure`; no source correction or blind rerun was used as release evidence.

### 2.10.2 — Worktree-Isolated Parallel Development & Single Integrator — P2 / RELEASED

Goal: gain real parallel-development speed without reintroducing split-brain writers or shared-branch corruption.

- Add a CDC task decomposition/DAG step that marks work as parallel-safe only when write sets and integration dependencies are sufficiently isolated.
- Use Superpowers-style Git worktree isolation for parallel implementation workers. Each writer owns one isolated worktree/branch; no worker writes directly to the shared integration/product branch.
- Preserve one CDC integrator as the only shared-branch writer. The integrator owns conflict reconciliation, final spec review, candidate assembly and branch finishing.
- Allow read-only/spec-review/quality-review workers to run in parallel with implementation when they do not mutate shared state.
- Require durable worker/task identity, exact base SHA and expected output/evidence contract before delegation.
- On worker failure or stale base, discard/rebase/re-run that isolated work rather than force-pushing or partially integrating.
- Feed completed isolated work back through 2.10.1 spec/quality gates and 2.10.0 verification before integration/terminal state.

Acceptance:
- no two implementation workers may own the same writable worktree or shared branch;
- workers cannot merge/release or expand product scope;
- parallel tasks with overlapping write sets are serialized or explicitly partitioned;
- a failed/stale worker cannot poison the shared branch;
- integrator detects base movement before integration and reconciles without force-push;
- parallel execution demonstrates lower wall-clock completion time on at least one representative multi-workstream task without increasing unresolved conflict/rollback rate;
- final integrated candidate remains exact-SHA validated and passes the normal CDC terminal/release gates.

Expected benefit: CDC gains safe concurrency — speed from parallel work, while ownership and final integration remain deterministic.

Release: `refs/heads/release/v2.10.2`.
- candidate validation HEAD: `52565ebbd97d9d6faba71cbe3cc353188c8a479b`;
- package tree: `2bee3b8159aaf80de981afba7cf284f21bafa1c3`;
- independent release evidence: `release/evidence-2.10.2.json`, PR #14 comment `5853585393` — bootstrap 12/12, package 516/516, aggregate 528/528, 260 validated files/templates, focused 98/98, Stage-2 review GREEN, 70 fault scenarios, 89 pressure scenarios and 3/3 consumers GREEN;
- durable observed benchmark: PR #14 comment `5853537039` — exactly one harness execution, 122/122 invocations, 88.93399239600012 s sequential vs 57.90157018700006 s parallel, speedup 1.5359513068260002×, conflicts 0→0 and rollbacks 0→0;
- benchmark plan, environment and observations are content-addressed and exact-source/tree-bound.


**Evidence reinforcement — 2026-09-27:** code-quality review found that write-set overlap and terminal changed-path containment must use a portable case-folded, Unicode-normalized identity rather than host-filesystem case semantics; otherwise Linux can classify `src/UI` and `src/ui` as independent while Windows sees one namespace. The same review found that planner/benchmark timing inputs must reject NaN and infinities rather than relying only on `> 0` comparisons.

**Fix formulation:** one canonical portable-path identity function governs planning, worker assignment and integration containment; case/Unicode aliases serialize or reject consistently. Estimated/observed durations are finite positive numbers by construction.

**Expected invariant:** a parallel plan cannot be GREEN on one filesystem and collide on another because of path aliasing, and non-finite numeric evidence can never satisfy speedup/release gates.

**Evidence reinforcement — 2026-09-27 (review closure):** independent review found four additional ways a formally valid parallel candidate could overstate safety: consumer compatibility evidence bound to an older package tree, benchmark fixtures mistaken for measured release evidence, an embedded worker plan mutable behind an unchanged human-readable plan reference, and a worker result commit not proven to descend from its contracted base.

**Fix formulation:** consumer evidence is exact-package-bound; package benchmark fixtures are explicitly non-observed and release-ineligible while release evidence uses externally observed candidate-bound records; worker plan references are canonical SHA-256 content addresses; successful writer Git proofs require base→result ancestry before diff acceptance.

**Expected invariant:** no CDC 2.10.2 release can rely on stale consumer compatibility, fixture timings, mutable plan identity, or unrelated Git history even when individual schemas and diffs otherwise look valid.


**Evidence reinforcement — 2026-09-27 (schema migration closure):** the prior-wave gate schema was hardened to require a content-addressed gate-result artifact, but one positive test producer still emitted the previous wrapper shape. Validators/templates were correct, negative regressions were GREEN, yet the end-to-end positive path failed.

**Fix formulation:** any CDC contract/schema evolution must migrate the validator, canonical templates and every positive producer/fixture atomically; release validation retains at least one end-to-end positive path that constructs the new schema through the same producer surface consumers use. Schema changes are not complete when only negative rejection tests and canonical static templates are GREEN.

**Expected invariant:** a released CDC schema cannot be internally self-inconsistent because a legacy positive producer survived a validator migration.

Finalization RCA — 2026-09-27:
- Root cause of the prolonged 2.10.2 closeout was a moving-target validation loop: source fixes continued after expensive benchmark/consumer evidence, which correctly made that evidence stale; release manifests were not refreshed atomically; and benchmark observations from different package trees/workload states were informally compared as one trend.
- Correction: freeze source/spec before expensive evidence; freeze the exact benchmark plan; run final consumer compatibility and observed benchmark once per exact package-tree + plan pair; persist environment, observations, benchmark manifest, consumer evidence and candidate binding atomically; metadata-only evidence commits do not invalidate package evidence; rerun expensive evidence only when package tree or benchmark plan changes.
- Concurrency correction: one canonical writer/reviewer owner per task; duplicate recovery/review requests are reconciled or cancelled; non-fast-forward ref updates fail closed and force-push remains forbidden.
- Evidence interpretation: provider/setup failure is not product RED, and benchmark comparisons are meaningful only for matching workload fingerprint/environment class; cross-candidate runs are separate observations rather than a degradation series.

### CDC 2.10 release proposal

Recommended release sequence:
1. **2.10.0 Behavioral Skill TDD & Verification Gate** — highest priority; directly attacks observed CDC reliability failures.
2. **2.10.1 Specification Compliance & Two-Stage Review** — next; prevents technically GREEN but requirement-wrong outcomes.
3. **2.10.2 Worktree-Isolated Parallel Development & Single Integrator** — last; adds speed only after behavior and review quality are independently proven.

Do **not** start with parallelism. The ordering is deliberate: first make CDC behavior measurable, then make implementation correctness reviewable, then scale execution concurrency.

Roadmap state: CDC 2.10.0, 2.10.1 and 2.10.2 are independently GREEN and released. CDC 2.10 is COMPLETE / TERMINAL.

## CDC 2.9 — COMPLETE / TERMINAL

Owner acceptance authorizes this roadmap. CDC 2.9 preserves the N-1 bootstrap/release rule: each release stage is developed only under the previously independently released stable CDC stage. The line is intentionally split so distribution/convergence becomes stable before migration/reconciliation depends on it, and the autonomy/learning layer is then developed under the released transactional core.

### 2.9.0 — Deterministic Distribution & Convergence — P0 / RELEASED

- Least-privilege immutable CDC package transport that does not require broad cross-repository credentials.
- Git-tree-faithful transport identity: path, mode and object identity are verified so reconstructed/vendored package tree must equal the canonical package tree exactly.
- Canonical Fleet Watcher convergence vector binding source ref + exact HEAD, CDC version, exact package tree, consumer lock, semantic policy digest, checkpoint validity, lease/guard state and adoption state.
- CI evidence classification into `pre_run_infrastructure`, `setup`, `product_test` and `terminal_success`; pre-run/zero-step failures route to execution-channel recovery rather than product correction.

Acceptance:
- a consumer can acquire/verify a released package without repository-wide canonical credentials;
- a consumer claiming version X cannot be integrated unless the exact canonical package tree is proven;
- Fleet Watcher cannot mark a project integrated from a version string alone;
- source changes are never prescribed solely from CI evidence where product validation did not execute.

Release: `refs/heads/release/v2.9.0`.
- release commit: `539d1282c5803fbc79147a18c871aaddbf29fe25`;
- package tree: `75702b88df4ac8c7e91a4e5055f8aa734dddeeae`;
- independent evidence: PR #8 comment `5847395070` — bootstrap 12/12, package 361/361, aggregate 373/373, 188 files, 31 fault scenarios, 3/3 consumers, 5/5 targeted 2.9.0 assertions.

Evidence reinforcement (2026-09-26): a release-validation job reached terminal failure before any executable step began. It was classified as `pre_run_infrastructure`; CDC made no product/source correction and routed to an alternate validation channel. This confirms the existing classifier/failover fix rather than creating a duplicate roadmap item.

### 2.9.1 — Transactional Migration & Provider Reconciliation — P1 / RELEASED

- Idempotent section-aware adapter/policy migration on a freshly re-read target HEAD; duplicate canonical top-level sections are forbidden.
- Schema-typed checkpoint builders and pre-commit checkpoint validation.
- Operation-budget-aware Git-object migration transactions with bounded chunks and detached intermediate tree checkpoints; product refs move only after exact subtree convergence.
- Terminal-provider reconciliation trigger for guarded external operations, preserving split-brain safety and requiring explicit executor-stopped evidence before any takeover.

Acceptance:
- repeated/concurrent adoption converges to one semantically valid policy document;
- every CDC-written checkpoint is schema-valid at the commit boundary;
- tool-operation limits cannot leave a product/adoption ref partially migrated;
- provider-terminal tasks cannot remain indefinitely represented as running, while provider terminal state or TTL alone never grants takeover.

Release: `refs/heads/release/v2.9.1`.
- release commit: `5579ac73e4df820ee163ecfb68829f3bf08173bf`;
- package tree: `a6a9ac4e4060112d77b58e8ac6aa67442dbb95c8`;
- independent evidence: PR #9 comment `5847492291` — bootstrap 12/12, package 378/378, 202 files, 35 fault scenarios, 3/3 consumers, 12/12 targeted 2.9.1 assertions, aggregate 402/402.

### 2.9.2 — Continuous Autonomy & Learning — P2 / RELEASED

- Enforce the Progress-Is-Not-Terminal invariant as executable continuation control: after every milestone/update, immediately repeat observe → reconcile → choose-next → act until Terminal-State v2 proves a real boundary.
- Emit one compact MSK timestamp for every user command handled under CDC as evidence metadata only.
- Bounded RCA-to-roadmap feedback loop: every material anomaly ends with a deduplicated systemic fix formulation, reinforcement or confirmation.
- Every CDC Fleet Watcher run emits exactly one evidence-based improvement proposal or deduplicated reinforcement.
- Dogfooding tracks premature milestone stops and feedback-loop closure without granting release or mutation authority.

Acceptance:
- reporting progress can never by itself end an authorized invocation;
- timestamps never become authority or control-plane state;
- material RCA cannot terminate without a systemic correction disposition;
- Fleet Watcher cannot terminate without exactly one bounded improvement/reinforcement record;
- no novelty spam: repeated evidence strengthens one canonical roadmap item.

Release: `refs/heads/release/v2.9.2`.
- release commit: `0dd30a888be852d2820f690be04dbd374d732c06`;
- package tree: `f9087eacbffee774c143eabf854c2cf08d610ec7`;
- independent evidence: PR #10 comment `5848036143` — bootstrap 12/12, package 384/384, aggregate 396/396, 216 files, 38 fault scenarios, 3/3 consumers, 13/13 targeted 2.9.2 assertions.

Roadmap state: 2.9.0, 2.9.1 and 2.9.2 are independently GREEN and released. CDC 2.9 is terminal; no runnable 2.9 scope remains.

## CDC 2.8 — COMPLETE / TERMINAL

The 2.8 roadmap is fully released and has no remaining runnable scope.

### 2.8.0 — Autonomous Continuity & Isolation — RELEASED

- Terminal-State v2 and No-Idle invariant.
- Execution-channel failover.
- Concurrent-writer reconciliation.
- Sensitive-context/publication guard.
- Control-plane isolation from publishable product state.

Release: `refs/heads/release/v2.8.0`.

### 2.8.1 — Operational Hardening — RELEASED

- Watchdog self-repair.
- Temporary-ref and coordination-state hygiene.
- Fresh blocker proof.
- Decision-authority policy.
- Evidence compaction.
- Progress enforcement.

Release: `refs/heads/release/v2.8.1`.

### 2.8.2 — Fleet & Publication Maturity — RELEASED

- Project-independent fleet control.
- Stuck-state detection.
- Counterfactual recovery.
- Sanitized public export with new public history.
- CDC dogfooding metrics.

Release: `refs/heads/release/v2.8.2`.

## Terminal-state evidence

CDC 2.8.2 independent validation:
- bootstrap: 12/12;
- package: 345/345;
- aggregate unittest: 357/357;
- package validation: 177 files/templates;
- fault scenarios: 28;
- consumers: 3/3;
- package tree: `bdf18b8dedb2f0cf62728935d92e6260b4a64ef0`.

There is no authorized next 2.8 development task. A new version line requires a new explicit roadmap; it must not be inferred from this completed roadmap.

## Consolidated backlog — owner-approved execution order

The former 13 future candidates contained 12 implemented capabilities and one remaining feature. Preserve their original problem statements in [backlog history](backlog-history-through-2.10.3.md); track observed defects independently instead of duplicating completed features. A release label proves only its scoped evidence, not live consumer adoption or general agent obedience.

| Former candidate | Implementation disposition | Executable entry point |
|---|---|---|
| Chat command timestamping | 2.9.2; freshness correction in 2.11.0 | `command_timestamp.py` |
| RCA-to-roadmap feedback | 2.9.2 | `rca_feedback.py` |
| Fleet improvement harvesting | 2.9.2 | `fleet_improvement.py` |
| Canonical distribution | 2.9.0 | `package_transport.py` |
| Git-tree transport fidelity | 2.9.0 | `package_transport.py` |
| Pre-run CI classification | 2.9.0 | `ci_evidence_classifier.py` |
| Idempotent policy migration | 2.9.1 | `policy_migration.py` |
| Nonterminal progress | 2.9.2; finalizer and effective-load defects corrected in 2.10.3 | `continuation_cycle.py / execution_continuity.py` |
| Schema-typed checkpoint migration | 2.9.1 | `checkpoint_builder.py` |
| Bounded Git-object migration | 2.9.1 | `migration_transaction.py` |
| Convergence vector | 2.9.0 | `convergence_vector.py` |
| Terminal-provider reconciliation | 2.9.1; operational liveness integration in 2.11.1 | `provider_reconciliation.py` |

Remaining feature: **registry-driven watchdog target resolution**, included in 2.11.1. Resolve the live `cdc/fleet` registry and target; project prompts load current repository policy, lock, checkpoint and coordination. Historical prompt targets never override live provenance.

Active recovery work:
- 2.11.0: released with real execution, exact parent finalization and independently verified corrections. Active installation passed runtime-byte readback; see release/active-package-acceptance-2.11.0.json.
- 2.11.1: combine target resolution, persistent liveness and bounded Fleet recovery; fresh explicit owner pause takes precedence.
- 2.11.2: released cooperative lanes with portable conflict exclusion, one integrator, durable integration provenance and watchdog survivability.\n- 2.11.3: released multi-subscription ownership integrity with Fleet leader/effect fencing, truthful execution liveness, fail-closed final response and atomic consumer adoption.
- Chat command timestamping dogfood defect — RCA reinforcement 2026-09-30: a live CDC-managed chat emitted zero per-command timestamps even though the rule was present. Reinforce existing fix key `chat-command-timestamping` with a missing-timestamp RED→GREEN pressure scenario and fail-closed first-response timestamp cardinality preflight/ledger; see the retained RCA/feedback reports.
- Independent review backend resilience — RCA 2026-09-30: a documented Copilot review request on a non-draft exact-head PR produced no reviewer/review/thread/comment, repeating an earlier no-op. Add fix key `independent-review-backend-fallback`: request acceptance is submission evidence only; require concrete reviewer identity + durable review artifact, classify non-materializing backends unavailable, suppress unchanged retries, and route to an alternate authorized reviewer or exact blocker.
- Consumer adoption: g-ad-control adopted2.10.3 and released generation42 at verified coordination794e152; g-supervisor, g-pc-health-check and g-switcher require current-owner release or independently established quiescence. Re-read live refs before every mutation.
- PR consolidation: #20/#61/#62/#63/#64 preserve one historical pool implementation and its review/consumer attempts. All five PRs were closed as superseded after #67 merge and release readback; historical branches and review evidence remain retained.

Schedulers are explicitly owner-paused. Neither liveness implementation nor backlog cleanup authorizes enabling or running them.
