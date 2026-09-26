# CDC roadmap

## CDC 2.10 — Superpowers Execution Quality — AUTHORIZED / PROPOSED

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

### 2.10.2 — Worktree-Isolated Parallel Development & Single Integrator — P2 / PROPOSED

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

**Evidence reinforcement — 2026-09-27:** code-quality review found that write-set overlap and terminal changed-path containment must use a portable case-folded, Unicode-normalized identity rather than host-filesystem case semantics; otherwise Linux can classify `src/UI` and `src/ui` as independent while Windows sees one namespace. The same review found that planner/benchmark timing inputs must reject NaN and infinities rather than relying only on `> 0` comparisons.

**Fix formulation:** one canonical portable-path identity function governs planning, worker assignment and integration containment; case/Unicode aliases serialize or reject consistently. Estimated/observed durations are finite positive numbers by construction.

**Expected invariant:** a parallel plan cannot be GREEN on one filesystem and collide on another because of path aliasing, and non-finite numeric evidence can never satisfy speedup/release gates.

**Evidence reinforcement — 2026-09-27 (review closure):** independent review found four additional ways a formally valid parallel candidate could overstate safety: consumer compatibility evidence bound to an older package tree, benchmark fixtures mistaken for measured release evidence, an embedded worker plan mutable behind an unchanged human-readable plan reference, and a worker result commit not proven to descend from its contracted base.

**Fix formulation:** consumer evidence is exact-package-bound; package benchmark fixtures are explicitly non-observed and release-ineligible while release evidence uses externally observed candidate-bound records; worker plan references are canonical SHA-256 content addresses; successful writer Git proofs require base→result ancestry before diff acceptance.

**Expected invariant:** no CDC 2.10.2 release can rely on stale consumer compatibility, fixture timings, mutable plan identity, or unrelated Git history even when individual schemas and diffs otherwise look valid.

### CDC 2.10 release proposal

Recommended release sequence:
1. **2.10.0 Behavioral Skill TDD & Verification Gate** — highest priority; directly attacks observed CDC reliability failures.
2. **2.10.1 Specification Compliance & Two-Stage Review** — next; prevents technically GREEN but requirement-wrong outcomes.
3. **2.10.2 Worktree-Isolated Parallel Development & Single Integrator** — last; adds speed only after behavior and review quality are independently proven.

Do **not** start with parallelism. The ordering is deliberate: first make CDC behavior measurable, then make implementation correctness reviewable, then scale execution concurrency.

Roadmap state: CDC 2.10.0 and 2.10.1 are independently GREEN and released. The first runnable scope is now 2.10.2.

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

## Future roadmap candidates — owner-requested backlog

These items are explicit future CDC roadmap candidates. They do not reopen the completed CDC 2.8 scope and do not assign a version number by themselves.

### Chat command timestamping

**Problem:** long-running CDC conversations make it hard to correlate a user command with repository, watchdog and compute events after the fact.

**Accepted fix:** after every user command handled under CDC in any conversation, read the actual current Moscow time (MSK, UTC+3) from a runtime/authoritative clock and emit exactly one compact timestamp before or with the first substantive progress update. Never extrapolate from the previous timestamp and never manually increment minutes. The timestamp is evidence metadata only; it must not be treated as authorization, lease ownership or a repository event.

**Acceptance direction:**
- one timestamp per user command in every CDC-managed chat;
- timestamp appears before substantive CDC progress for that command;
- exact display format: `[HH:MM DD.MM]`, for example `[19:31 26.09]`;
- source time is freshly observed for that command, not derived from an earlier chat timestamp;
- no `MSK` label, seconds or synthetic minute advancement;
- no duplicate timestamp spam inside one command.

**Evidence reinforcement — 2026-09-26:** one live CDC invocation emitted a second fresh timestamp on a later progress update within the same user command. Freshness alone is insufficient: the per-command ledger is authoritative. After the first emitted `[HH:MM DD.MM]` marker, all later progress updates in that same command must suppress additional timestamps even if real time has advanced.

### RCA-to-roadmap feedback loop

**Problem:** anomalous or unclear CDC behavior can be diagnosed and fixed locally but then recur because the systemic correction never becomes roadmap input.

**Proposed fix:** for every materially unclear, contradictory or unexpected CDC case, perform a bounded RCA and convert the result into a short **fix formulation** in the CDC roadmap/backlog. Record the corrective mechanism, not a verbose incident diary. Deduplicate against existing roadmap items before adding a new one.

**Acceptance direction:**
- RCA distinguishes product failure, policy failure, execution-channel failure, stale state, concurrent-writer movement and operator/tooling error where applicable;
- every material RCA ends with one of: existing fix confirmed, existing roadmap item strengthened, or new fix formulation added;
- roadmap entries state the invariant/control to add or change;
- secrets, sensitive operational identifiers and disposable incident noise are not copied into the roadmap;
- repeated occurrences strengthen one canonical fix instead of creating duplicate backlog items.

### Fleet Watcher improvement harvesting

**Problem:** Fleet Watcher currently observes project health but can finish without converting repeated operational friction into CDC product improvement.

**Proposed fix:** every CDC Fleet Watcher run must produce exactly one bounded improvement proposal for CDC based on evidence from that run. The proposal may strengthen an existing roadmap item instead of creating a new one. If no novel improvement exists, record a deduplicated reinforcement/evidence update rather than inventing novelty.

**Acceptance direction:**
- exactly one proposal or reinforcement per Fleet Watcher run;
- proposal is derived from observed fleet evidence;
- proposal is checked against existing roadmap/backlog for duplicates;
- proposal does not grant new authority or expand project scope;
- proposal is concise: problem → fix formulation → expected invariant/benefit;
- low-value noise is prevented by allowing an existing item to receive additional evidence instead of forcing a new item.

### RCA-derived fix — canonical package distribution

**Observed failure class:** consumer GitHub Actions could not fetch private canonical `g-cdc` using its repository-scoped `GITHUB_TOKEN`; cross-repository checkout failed before migration logic.

**Root cause:** CDC release provenance and CDC package distribution currently share one private repository boundary, while consumer automation tokens are intentionally repository-scoped.

**Fix formulation:** publish or expose an immutable **CDC package transport** that can be consumed without broadening consumer repository credentials. The transport must remain bound to canonical release commit + exact package Git tree and must not require making the canonical development repository public.

**Expected invariant:** a consumer can fetch a released CDC package with least privilege while independently verifying the canonical release identity and exact package tree.

### RCA-derived fix — Git-tree fidelity in package transport

**Observed failure class:** archive/tarball transport preserved file contents but produced a different vendored subtree SHA because Git mode metadata was not faithfully reconstructed.

**Root cause:** filesystem/archive transport is content-oriented, while CDC package identity is a Git tree identity that includes path/mode/object metadata.

**Fix formulation:** CDC package transport and adoption tooling must be **Git-object-aware** or carry a signed/validated mode manifest sufficient to reconstruct the exact canonical subtree. Adoption must fail closed when reconstructed subtree SHA differs.

**Expected invariant:** every consumer that claims CDC version X has vendored subtree SHA exactly equal to the canonical package tree for X.

### RCA-derived fix — pre-run CI failure classification

**Observed failure class:** several GitHub Actions runs failed at `Set up job` / zero executable steps; treating those as product RED would trigger wrong remediation.

**Root cause:** CI state classification does not always distinguish runner/provider/pre-execution failure from executed test failure early enough.

**Fix formulation:** classify CI evidence into at least `pre_run_infrastructure`, `setup`, `product_test`, and `terminal_success` before applying recovery policy. Zero-step/pre-job failure must route to execution-channel recovery/failover rather than product correction.

**Expected invariant:** no source change is made solely in response to a run where product validation never executed.

### RCA-derived fix — idempotent policy migration under concurrent writers

**Observed failure class:** CDC adoption appended 2.8 policy sections after another writer had already introduced equivalent sections, producing duplicate strict-YAML keys even though package and lock identity were correct.

**Root cause:** migration logic was presence-aware only at an earlier observation and did not re-read/reconcile the live adapter immediately before applying section additions.

**Fix formulation:** CDC adoption/migration must be **idempotent and section-aware at commit time**. Re-read the current target adapter immediately before mutation; merge or replace canonical control sections by key, never append duplicate top-level keys. If HEAD moved, rerun semantic reconciliation on the fresh HEAD before commit.

**Expected invariant:** repeated or concurrent CDC adoption converges to one valid semantic policy document; rerunning adoption is a no-op when the same target version is already represented.

### RCA-derived fix — non-terminal progress must never stop execution

**Observed failure class:** a CDC invocation completes a smaller implementation or validation step, reports that milestone to the user, and then stops even though authorized runnable work remains and no real blocker exists.

**Root cause:** progress reporting and terminal control are insufficiently separated. A successful primitive or milestone can be misinterpreted as an invocation boundary, allowing the conversational response path to end execution before the CDC terminal-state evaluator proves COMPLETE, WAIT_EXTERNAL, or BLOCKED.

**Fix formulation:** introduce a strict **Progress-Is-Not-Terminal invariant**. A progress update is informational only and MUST NOT transfer control back to the user, release ownership, or end the continuation loop. After every reported milestone, CDC must immediately re-run observe → reconcile → choose-next → act. Final response is permitted only when Terminal-State v2 accepts a real terminal boundary.

**Acceptance direction:**
- completion of a primitive step, commit, test subset, migration batch, validation stage, PR creation, artifact creation, or status report is never sufficient to stop execution by itself;
- if any authorized runnable action remains, the same invocation continues automatically after the progress update;
- progress updates and durable actions may be interleaved, but progress text never changes execution state;
- `WAIT_EXTERNAL` requires a durable external binding and no same-invocation useful work;
- `BLOCKED` requires fresh blocker proof and exhaustion of useful same-invocation work;
- `COMPLETE` requires scope-completion evidence;
- an invocation that returns control after a milestone while runnable work remains is a CDC contract violation and must trigger recovery/self-correction;
- Fleet Watcher and dogfooding metrics should track occurrences of premature milestone stops as No-Idle violations.

**Expected invariant:** CDC never pauses merely because it has something useful to report. It reports progress and keeps working until a genuine terminal state.

**Evidence reinforcement — 2026-09-26:** a consumer adoption reached `finalization.state=reconciled` with `pending_shared_writes=false` and all exact-head validation GREEN, but ownership remained unreleased and no independent `executor_stopped` proof existed. TTL expiry was correctly rejected as takeover evidence. This strengthens the existing Progress-Is-Not-Terminal control: `reconciled` is still a continuation point; the owning invocation must immediately proceed to ready/release, while other executors may only observe or wake/re-enter the owner until explicit quiescence is proven.

### RCA-derived fix — schema-typed checkpoint migration

**Observed failure class:** an adoption checkpoint stored explanatory text in `execution_continuity.runnable_next_action`, while checkpoint v4 requires a Boolean; package, adapter and lock were GREEN but the terminal checkpoint failed validation.

**Root cause:** migration logic reused human-readable next-action text for a typed control field instead of constructing checkpoint fields from the checkpoint schema.

**Fix formulation:** checkpoint migration must be **schema-typed by construction**. Typed control fields are generated from schema-aware builders/templates, never inferred from arbitrary display text. Run checkpoint validation before committing a migration boundary; if a field type is wrong, correct the migration logic rather than weakening the validator.

**Expected invariant:** every CDC-written checkpoint is schema-valid at commit time; descriptive text stays in descriptive fields and cannot leak into Boolean/enumerated control fields.

**Evidence reinforcement — 2026-09-26:** a consumer checkpoint under CDC 2.9.2 stored a task-specific label in `execution_continuity.completion_gate` while runnable validation work remained. Strict v4 validation correctly rejected it. Corrective rule remains schema-typed construction: use the enum value `continue` for ongoing runnable work and keep task labels in descriptive fields.

### RCA-derived fix — bounded Git-object migration transactions

**Observed failure class:** a bulk CDC vendor-copy operation exceeded the execution connector's per-call tool-operation limit before a target tree was created.

**Root cause:** migration batching was sized by file count only and did not account for the execution channel's maximum nested tool-call budget.

**Fix formulation:** CDC migration planning must calculate a conservative **operation budget per batch**, split large Git-object transfers into bounded chunks, and persist each intermediate result only as an unreferenced/detached tree checkpoint. Product/adoption refs move only after exact subtree convergence and final policy reconciliation.

**Expected invariant:** channel/tool-call limits cannot leave a branch partially migrated; oversized migrations automatically chunk and resume from the last detached tree checkpoint.

### Fleet Watcher proposal — canonical convergence vector

**Fleet observation:** a project may report CDC version `2.8.2` while exact package-tree readback, policy digest, checkpoint binding, or live ownership state is not yet proven on the same source ref. Version-only fleet status therefore overstates convergence.

**Proposed fix:** Fleet Watcher should emit one normalized **convergence vector** per project: source ref + exact HEAD, CDC version, exact package tree, consumer-lock identity, semantic policy digest, checkpoint-valid flag, lease/guard state, and adoption state (`not_started | staged | validated | integrated | blocked`). A project is `integrated` only when all required components are mutually consistent on the same ref.

**Expected invariant/benefit:** fleet status cannot show a project as fully converged from a version string alone; rollout state becomes deterministic, comparable across projects, and safe under concurrent writers.

**Fleet Watcher reinforcement — 2026-09-26:** one consumer had canonical 2.9.2 version/tree plus all validation GREEN while its invocation-bound lease remained unreleased. Fleet status therefore correctly distinguishes package/policy adoption from full integrated convergence; exact version/tree evidence cannot erase live ownership state.

**Evidence reinforcement — 2026-09-26:** a product checkpoint reported `lease_state: released` while the authoritative `cdc/coordination/lease.json` still held a newer active watchdog generation. Safe-boundary decisions must therefore read the live coordination lease/guard first; checkpoint ownership fields are historical/projected evidence only and may never override a newer coordination record.

### RCA-derived fix — terminal-provider guard reconciliation

**Observed failure class:** a guarded external CI operation becomes terminal at the provider, but the CDC lease/control-plane record remains `active` with `external_guard.state=running` and pending finalization.

**Root cause:** provider-terminal observation and owner/finalization reconciliation are decoupled; a foreground owner can stop or lose execution after the provider finishes, leaving truthful provider state and durable CDC guard state inconsistent.

**Fix formulation:** add a **terminal-provider reconciliation trigger**. Whenever Fleet Watcher/watchdog/provider observation proves a guarded task terminal, CDC must immediately schedule/re-enter reconciliation for that exact operation key. Reconciliation updates the guard/operation observation and prompts owner finalization. If the original executor is independently proven stopped and no pending shared writes/effects exist, recovery may construct explicit `executor_stopped` takeover evidence. Provider terminal state or lease TTL alone never grants takeover.

**Expected invariant:** no provider-terminal task remains indefinitely represented as running in CDC state, while split-brain safety remains intact.



### RCA-derived fix — registry-driven watchdog target resolution

**Observed failure class:** recurring project/Fleet watchdog automation prompts retained hardcoded historical CDC targets after canonical CDC had advanced. Repository package/policy could be current while the scheduler prompt continued evaluating against an obsolete version/tree or remained disabled.

**Root cause:** scheduler configuration duplicated mutable release identity instead of resolving authority from durable live sources. Updating repositories did not atomically update every automation prompt, creating a second configuration plane that could silently drift.

**Fix formulation:** watchdog prompts must be **target-resolution instructions, not target storage**. Fleet Supervisor resolves the current target from live `cdc/fleet/fleet/registry.json` + `fleet/target.json`. Project watchdogs re-read their live `AGENTS.md`, `docs/cdc-consumer-lock.json`, adapter/checkpoint and coordination state on every run; a fleet-announced newer target is adopted only through normal safe-boundary migration. Any version/commit/tree mentioned in an automation prompt is informational bootstrap context only and can never override live durable provenance.

**Expected invariant:** releasing or adopting a newer CDC version cannot leave watchdog logic pinned to an older target; scheduler state and project state converge from one durable authority chain instead of duplicated hardcoded constants.
