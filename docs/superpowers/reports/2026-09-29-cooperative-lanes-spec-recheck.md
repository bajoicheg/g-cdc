# CDC 2.11.2 independent specification-compliance recheck

## Verdict

**VERDICT: CHANGES REQUIRED**

This is a **SPECIFICATION-COMPLIANCE review**, not a code-quality verdict and not a release verdict. The implementation must not be called specification-GREEN until the material findings below are corrected and independently rechecked by a fresh reviewer identity.

No implementation, scheduler, watchdog, release, merge, or product-runtime state was changed by this review. Owner-paused schedulers remain paused.

## Exact review target

- canonical repository: bajoicheg/g-cdc
- base release ref: release/v2.11.1
- base release resolved commit: a262f78b82cd9e8eba9bc3b6108e0b52a17c33b0
- implementation source: c63db9a5c18386d0cca2945313ec9314037d31d1
- candidate package tree: d56d4fd0fa2b074e2a6c85ecd2b40e3debc493e2
- metadata HEAD: af45ec793290c1aaf7fff48b7ed5b10b998fb4e5
- supporting CI run: 36605922181

The live PR #69 head had already advanced beyond the requested target during this review. I did not retarget the review to that newer head. Comparison of c63db9a5... to af45ec7... showed only candidate/consumer evidence metadata changes, so the frozen implementation inspected here remains c63db9a5....

release/candidate.json at af45ec7... binds source_commit=c63db9a5... and package_tree=d56d4fd....

## Sources reviewed before findings

The independent review read, in order and without using prior review conclusions as project-state evidence:

- AGENTS.md
- docs/roadmap.md
- docs/superpowers/specs/2026-09-28-cooperative-lanes-design.md
- docs/superpowers/plans/2026-09-28-cooperative-lanes.md
- PR #69 metadata, changed-file list, exact source/base comparison, source-to-metadata comparison, and CI evidence
- the frozen implementation and tests for project lanes, execution adapter, Git integration, watchdog survivability, Fleet runtime, Sentinel, managed executor runtime, Git document CAS, and Git remote identity
- src/continuous-development-cycle/SKILL.md
- src/continuous-development-cycle/references/cooperative-project-lanes-and-watchdog-survivability.md

I did **not** read docs/superpowers/reports/2026-09-29-cooperative-lanes-spec-review.md until after the independent finding set below had been formed. Post-hoc comparison found that earlier report was scoped to source 7da65fbc887590632d841d851c700bec2ab2c47a and package tree f23211101e4497c7c3b52d2f2c57fea3b7b77e6d, not this exact frozen target. It does not close the findings below.

## Methodology and adversarial probes

The review treated passing tests as supporting evidence, not as proof of the effect boundaries. It traced durable state and authority across CAS, process/Git, scheduler, lost-reply, stale-observation, and recovery boundaries.

Adversarial cases examined included:

- REVIEW/read-only lane claims carrying write paths;
- ordinary writer claims naming the configured product/shared source branch;
- migration gate reuse by a fresh coordinator after initial establishment;
- stale legacy-state change after a stored migration proof;
- worker start claim replay and missing local request journal;
- touched-and-restored writer path escape across introduced commits;
- pre-existing intended integration HEAD before the publisher's first publication attempt;
- concurrent remote movement around exact-head publication;
- read-only integration evidence attempting queue closure;
- MISSING watchdog with a stale-generation materialization still execution_state=running;
- running CONFIG_DRIFT / FLAPPING / stale-last-run cases;
- lost create/run replies and generation fencing;
- duplicate cleanup while an old invocation is still running;
- Fleet shared effect budget and continuation;
- Sentinel role restriction and continuation after recreate/adopt/enable.

A direct local clone of GitHub was unavailable in this reviewer runtime because the sandbox had no DNS path to github.com. Repository state and exact source bytes were therefore read through the GitHub connector. Disposable process/Git semantics already present in the frozen tests were inspected, and material probes below are stated as exact deterministic call scenarios against the frozen source branches. No live scheduler was touched.

## Supporting CI evidence

GitHub Actions run 36605922181 completed successfully. Its job logs show:

- independent bootstrap: 37 tests, OK;
- package validator: continuous-development-cycle 2.11.2, 316 files/templates;
- full candidate suite: 828 tests, OK;
- full bootstrap binding: GREEN;
- all three archived consumer snapshots: GREEN;
- observed package tree: d56d4fd0fa2b074e2a6c85ecd2b40e3debc493e2.

This CI does not negate the adversarial effect-boundary findings below.

## Material findings

### S1 — HIGH — MISSING recovery can create a new watchdog while an older materialization is still running

**Requirement violated**

A running watchdog materialization must not be destructively replaced merely because its object identity/generation is stale or missing from desired state. Generation fencing is not proof that the old process stopped. Destructive replacement must wait for independently established quiescence.

**Exact code**

- src/continuous-development-cycle/scripts/watchdog_survivability.py — assess()
- src/continuous-development-cycle/scripts/watchdog_survivability_runtime.py — reconcile(), _set_operation()

**Concrete failure scenario**

Desired state is generation 7 with canonical_object_id="wd-current". Fresh safe inventory contains no object with that ID, but does contain object "wd-old", generation 6, execution_state="running".

In assess(), canonical lookup fails. Because the stale running object does not match desired generation/config, the code falls through to the unconditional canonical-is-None branch and returns MISSING / RECREATE with next_generation=8. It does not first prove every potentially executing old materialization quiescent.

WatchdogSurvivabilityRuntime.reconcile() then persists generation 8 before scheduler I/O and can call backend.create(). The generation fence makes the old process non-current in durable authority, but it does not stop an already-running process. The result can therefore be two concurrent watchdog invocations.

**Probe / reproduction evidence**

Using the frozen test fixtures, the missing adversarial case is equivalent to:

- desired(): generation=7, canonical_object_id="wd-current"
- inventory([obj("wd-old", generation=6, execution_state="running")])
- assess(..., now=NOW)

The exact assess() control flow returns overall=MISSING, action=RECREATE, recovery_eligible=true, next_generation=8. Existing tests cover a running duplicate only when the canonical object is still present, and cover running CONFIG_DRIFT/FLAPPING on the canonical object; they do not cover canonical-missing + stale-running.

**Impact**

A still-running watchdog can overlap a newly created generation and perform duplicate development/external work. This defeats the explicit active-watchdog safety invariant and can produce split execution even though the old generation is logically fenced.

**Required correction**

Before MISSING/RECREATE advances generation or creates anything, independently prove that every extant materialization that could still execute is stopped/quiescent. Any running or unknown stale object must force OBSERVE/EXECUTION_BROKEN (or another non-destructive continuation state) until quiescence is established. Do not treat execution_is_current()==false or a generation bump as stop proof. Add an end-to-end regression for canonical-missing + old-running and old-unknown materializations.

### S2 — HIGH — REVIEW lanes can carry write claims and are promoted to writer execution

**Requirement violated**

Read-only/review lanes must receive no write authority.

**Exact code**

- src/continuous-development-cycle/scripts/project_lanes.py — LaneClaim.is_writer, validate_claim(), admit_writer()
- src/continuous-development-cycle/scripts/project_lane_executor.py — _identity(), start()

**Concrete failure scenario**

Construct LaneClaim(kind=LaneKind.REVIEW, role="review", write_paths={"src/a"}, with otherwise valid identity/branch/worktree). validate_claim() validates the paths but never rejects write_paths for REVIEW. LaneClaim.is_writer becomes true solely because write_paths is non-empty, and admit_writer() can admit it as a writer.

ProjectLaneExecutionAdapter._identity() then rewrites the execution role to "writer" whenever write_paths is non-empty. start() blocks only INTEGRATOR lanes, not REVIEW lanes. Thus a lane labelled REVIEW can reach a writer backend.

**Probe / reproduction evidence**

The deterministic frozen-source probe is:

1. create an otherwise valid LaneClaim with kind=REVIEW and non-empty write_paths;
2. validate_claim(claim) succeeds;
3. claim.is_writer is true;
4. admit_writer([], claim) is true;
5. executor identity role becomes "writer".

Current tests exercise REVIEW only with an empty write set and contain no negative test for REVIEW + writes.

**Impact**

The role/surface boundary is not authoritative. A caller can accidentally or deliberately turn review execution into product-write execution, contradicting the contract that review/read-only lanes coexist without write authority.

**Required correction**

Enforce role/kind semantics at claim validation and again at the effect adapter: REVIEW/read-only/observer roles must have an empty write set and must never enter writer worktree/branch execution. Constrain role to an explicit schema rather than arbitrary text, and add negative admission/start regressions.

### S3 — HIGH — An ordinary writer can claim the configured shared product source branch

**Requirement violated**

There must be exactly one shared-branch writer: the integrator. Ordinary writer lanes must never receive shared-ref authority.

**Exact code**

- src/continuous-development-cycle/scripts/project_lane_runtime.py — ProjectLaneCoordinator.admit()
- src/continuous-development-cycle/scripts/project_lanes.py — validate_claim(), admit_writer()

**Concrete failure scenario**

LaneRegistryConfig binds product_source_ref="refs/heads/main". An ordinary WORKER/FOREGROUND/WATCHDOG writer claim can set branch="refs/heads/main". Neither validate_claim() nor admit() compares an ordinary lane's branch against config.product_source_ref. With no conflicting active writer, the lane is admitted.

Branch/worktree collision checks only compare one lane against another; they do not reserve the shared product ref for the integrator. A later integrator using the same branch can even be blocked by the ordinary writer.

The bundled local Git backend may incidentally fail if a local branch of that name already exists, but that is not a pre-effect authority check and cannot be relied upon for other authorized backends or arbitrary worker commands.

**Probe / reproduction evidence**

Against a fresh coordinator with migration gate established:

- config.product_source_ref = "refs/heads/main"
- ordinary LaneClaim(kind=WORKER, branch="refs/heads/main", write_paths={"src/a"})
- coord.admit(..., generation=1)

The frozen admission path has no shared-ref reservation test and returns admitted when no other writer conflicts.

**Impact**

The single-integrator invariant is not enforced by the lane control plane. Ordinary execution can be assigned the shared branch, creating a split-brain/shared-writer authority contradiction before the Git publication layer is reached.

**Required correction**

Reserve the configured shared/product ref at lane admission. Reject any portable-equivalent shared branch for non-INTEGRATOR lanes before effects. Bind the integrator lane explicitly to the authorized shared publication target, and add regressions for ordinary writer attempts to claim the shared branch.

### S4 — HIGH — GitLaneIntegrationPublisher can claim conditional_update=true without performing or proving the intent's CAS

**Requirement violated**

Queue removal requires evidence that the exact intended publication was performed through an expected-head conditional update. Read-only exact-HEAD/ancestry evidence alone is not authoritative. Lost-reply reconciliation must not manufacture a second publication effect or upgrade weak readback into CAS proof.

**Exact code**

- src/continuous-development-cycle/scripts/project_lane_git.py — GitLaneIntegrationPublisher.__call__()
- src/continuous-development-cycle/scripts/project_lane_runtime.py — mark_integrated()

**Concrete failure scenario**

An integration intent binds observed shared HEAD A and intended integrated HEAD B. Before the publisher is called for the first time, another actor publishes B to the authoritative remote.

GitLaneIntegrationPublisher reads current=B. Because current already equals intended, it skips the branch that verifies current==observed and executes push --force-with-lease=<ref>:A. It then returns evidence with conditional_update=true.

ProjectLaneCoordinator.mark_integrated() accepts that evidence and removes the result from the integration queue. No expected-head conditional update by this intent was executed or proven.

**Probe / reproduction evidence**

The frozen publisher's decisive branch is:

- current = _remote_head()
- if current != intended: perform observed-head check + lease push
- otherwise skip all publication I/O
- unconditionally return conditional_update=True

The existing publisher test verifies a genuine first CAS and then invokes the publisher a second time to model lost-reply reconciliation. It does not distinguish that legitimate retry from the adversarial case where current==intended before this intent ever attempted publication.

**Impact**

Exact readback can be mislabeled as conditional publication authority. This bypasses the design's explicit distinction between GitLaneIntegrationVerifier read-only evidence and release-grade CAS evidence, and can make an accepted result disappear from the queue without proof of the required effect boundary.

**Required correction**

Persist a publication-attempt/submission state tied to operation_id before Git I/O. Return conditional_update=true only when the same operation either (a) actually executes the expected-head CAS and exact readback succeeds, or (b) is reconciling a durably recorded unknown CAS attempt and authoritative readback proves its exact intended result. If remote already equals intended before any recorded CAS attempt for this operation, treat it as read-only/unproven or moved state and do not close the queue.

### S5 — HIGH — The legacy-to-lane migration gate is not independently revalidated on registry reads

**Requirement violated**

The lane migration gate must be immutable and must be revalidated when read. Lane admission must remain fail-closed unless independent evidence still establishes the safe legacy boundary.

**Exact code**

- src/continuous-development-cycle/scripts/project_lane_runtime.py — _read(), establish_migration_gate(), admit()

**Concrete failure scenario**

establish_migration_gate() correctly calls migration_verifier once and stores an immutable evidence mapping. Later _read() only calls _validate_migration_evidence() on the already stored mapping; it does not invoke migration_verifier or otherwise re-observe the legacy lease/guard/acquisition-disable authority.

A fresh ProjectLaneCoordinator can therefore be constructed against an already-gated registry without any migration_verifier. admit() checks only stored gate.safe and stored legacy_mode_disabled. If the external legacy acquisition control or lease state is no longer safe, admission still succeeds because the stored proof is treated as permanently sufficient.

**Probe / reproduction evidence**

The frozen source has migration_verifier invocation only in establish_migration_gate(). _read() schema-validates the stored gate, and admit() checks fields from that stored gate. The registry-binding tests verify initial unsafe/safe establishment and immutability, but contain no test in which authoritative legacy state changes after gate establishment or a new coordinator lacks the verifier.

**Impact**

Lane mode can coexist with revived legacy ownership, reintroducing the exact project-wide lease/lane split-brain that the migration gate is intended to prevent.

**Required correction**

Make every authoritative read/admission revalidate the immutable migration proof against an independent, authoritative migration/tombstone source, or bind the gate to an independently verifiable irreversible legacy-disable epoch. A coordinator unable to perform that revalidation must fail closed. Add restart and post-gate legacy-state-drift regressions.

## Requirements that were positively evidenced

The following material requirements were present in the frozen target and were exercised by code/tests reviewed here:

- disjoint foreground/watchdog writer claims can coexist;
- portable case/Unicode/ancestor-descendant overlap serializes writers;
- active writers cannot share branch/worktree with another active writer;
- worker start claims are durable before backend worktree/process effects and unknown starts are observed rather than replayed;
- worker worktree root is separated from product root and journal;
- integrator lanes are denied ordinary worker launch;
- the principal Linux test uses real Git worktrees and two real foreground/watchdog-labelled processes concurrently;
- heartbeat requires independent observed activity;
- normal release is executor/invocation/generation-bound, checkpointed, and effect-drained;
- recovery release requires independently proven executor_stopped quiescence;
- writer result verification uses genuine Git ancestry and every touched path of every introduced commit, including touched-and-restored escapes;
- one lane cannot submit multiple accepted results;
- integration intent replay with mismatched intended HEAD is rejected;
- queue closure requires verifier output with conditional_update=true (but S4 shows the publisher can incorrectly manufacture that bit);
- project lane aggregation counts active lanes, runnable tasks, pending integration results, and caller-supplied unknown effects;
- running canonical watchdogs are not kicked from stale timestamps and running CONFIG_DRIFT/FLAPPING canonical objects are observed rather than recreated;
- lost create/run replies retain durable operations and are not blindly replayed;
- duplicate cleanup is bounded and does not claim quiescence until a disabled stale object is idle/failed/absent;
- all registered desired watchdogs are assessed under a bounded survivability effect budget;
- Fleet composes survivability and ordinary liveness under one total scheduler-effect budget and retains continuation;
- Sentinel accepts only role=fleet-supervisor, uses the survivability runtime, grants no product-write authority, and keeps continuation after recreate/adopt/enable until a real wake/settled state.

## Post-hoc comparison with the earlier review report

Only after the five findings above were fixed as the independent result, I read docs/superpowers/reports/2026-09-29-cooperative-lanes-spec-review.md.

That report reviewed an earlier source/tree (7da65fbc... / f232111...) and records six earlier findings that were corrected there. It is not evidence that c63db9a5... is specification-GREEN. None of S1-S5 above is closed by that report:

- its active-watchdog discussion covers stale timestamps and current running config/flap behavior, but not canonical-missing + stale-running recreation;
- it does not enforce REVIEW=no-write;
- it does not reserve the configured shared source branch to the integrator;
- it does not distinguish a pre-existing intended remote HEAD from reconciliation of a durably attempted CAS;
- it does not establish independent migration-proof revalidation on every registry read.

## Final spec-review state

**VERDICT: CHANGES REQUIRED**

Material findings: **5 HIGH**.

Reviewed:
- source: c63db9a5c18386d0cca2945313ec9314037d31d1
- package tree: d56d4fd0fa2b074e2a6c85ecd2b40e3debc493e2
- metadata head: af45ec793290c1aaf7fff48b7ed5b10b998fb4e5
- base release: release/v2.11.1 -> a262f78b82cd9e8eba9bc3b6108e0b52a17c33b0

Next step: the implementation owner should correct S1-S5 without weakening the stated invariants, then a **new independent SPEC reviewer identity** should recheck the exact corrected source/tree/head. Do not proceed to the separate code-quality review until specification findings are independently closed.
