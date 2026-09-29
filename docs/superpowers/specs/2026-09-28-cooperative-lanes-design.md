# CDC 2.11.2 cooperative project lanes

Design for the already approved final stage. Implementation starts only after 2.11.1 is independently released and installed/read back. This document is advance design, not evidence of an implemented or released feature.

## Ownership model

Use a durable project-lane registry on a dedicated coordination ref. Configuration binds canonical repository identity, product source ref, coordination endpoint/ref and policy authority. Every admission binds a unique lane, executor, exact invocation, surface (foreground/watchdog/Work/Codex), role, source HEAD, declared portable read/write paths, isolated branch/worktree and bounded activity/effect evidence. The state/config digest prevents redefining an existing registry behind the same ID.

Writer lanes with disjoint portable write claims coexist. Read-only/review lanes may coexist using their pinned source snapshot. Case, Unicode normalization and ancestor/descendant aliases count as overlapping paths. No two live writers share a worktree or branch. Overlap blocks admission before effects; the caller selects another nonconflicting queued task or observational work. One exclusive integrator lane controls shared-branch integration; ordinary writers never receive shared-ref, merge or release authority.

An existing project-wide lease is a migration gate, not a claim to ignore. Lane mode begins only at an authorized safe boundary with the legacy owner released or independently proven quiescent and external guards reconciled. Lane mode does not automatically migrate any current consumer. Explicit scheduler pause remains separate; active foreground work never creates a new scheduler-pause action.

## Lifecycle and effect boundary

Admission/transition is a real durable CAS with unique proposals and no force push. Heartbeat requires a new exact activity reference plus independent observable-activity evidence; a caller-generated token alone is insufficient. A stale heartbeat/TTL never frees a claim. Normal release is exact executor/invocation/generation-bound, persists an exact checkpoint reference, and requires pending effects drained. Recovery release requires independently bound quiescence rather than urgency or silence. Releasing one lane preserves every other lane and its pending result.

The execution adapter prepares isolated worktrees and uses a real supplied worker backend only after the durable claim and refreshed gates. An uncertain start or process that can still write retains its claim; retry cannot relabel it away. Demonstrate foreground and watchdog-labelled workers genuinely running concurrently with disjoint writes in local Git, under a recording scheduler that receives no changes.

Before accepting/integrating a writer result, validate base ancestry and every introduced commit's touched paths against the original claim, plus required evidence and exact result identity. Shared HEAD movement requires fresh reconciliation: disjoint fast-forward changes may be replayed on the new base; overlap, divergence or unknown movement is blocked. The integrator persists a one-shot durable integration intent before any shared-ref effect. Publication remains external to the registry's evidence layer and must be conditional/no-force; unknown outcomes retain the same intent. A result leaves the integration queue only after a fresh independent verifier binds the exact intent, pre-publication shared HEAD, result commit and integrated HEAD. Successful computation is distinct from accepted/published/integrated work.

Project completion aggregates fresh lane state and the authoritative remaining queue. One completed/idle lane cannot hide another runnable/active lane, unknown effect or unintegrated required result. Combine this aggregate with the released execution-continuity gate; do not replace finalizer evidence with a lane status string.

## Verification

Retain RED→GREEN for disjoint concurrency, portable overlap, duplicate admission/CAS contenders, isolation collisions, stale-owner theft, fake heartbeat, release of another invocation, independent release, unknown start, result containment, moved shared HEAD and premature project completion. Use real local Git/process integration for the principal lifecycle. Run prior continuity, pool and liveness regressions, independent spec/quality review, bootstrap, archived three-consumer compatibility and exact-head CI before release. Record cooperative control limits: no OS sandbox, no arbitrary writer fencing and no fabricated scheduler/host API.


## Watchdog survivability and desired-state reconciliation

Scheduler objects are disposable materializations, not the source of watchdog identity. Durable desired state binds project identity, source ref, watchdog role, required/enabled-or-paused state, expected schedule/template digest, canonical object ID when known, generation, explicit owner-stop evidence and bounded recovery policy.

A fresh runtime inventory distinguishes `HEALTHY`, `OVERDUE`, `DISABLED_DRIFT`, `MISSING`, `CONFIG_DRIFT`, `DUPLICATE`, `FLAPPING`, `EXECUTION_BROKEN`, `OWNER_PAUSED` and `PROJECT_TERMINAL`. Missing/configuration-drift/flapping recovery advances the desired generation before scheduler I/O so an old object that wakes later is fenced. Disabled and overdue current objects may be enabled/kicked without a generation bump when every fresh safety gate permits it.

Every scheduler effect uses a durable one-shot operation claim plus a post-claim fresh desired/safety observation. Unknown provider outcomes retain the claim and are reconciled by exact inventory readback; create/run/enable/disable are never blindly replayed. Unknown run outcomes require a run timestamp at or after the durable claim. A currently running watchdog is not kicked again merely because an older timestamp crosses the overdue threshold. Duplicate objects are quiesced only after the canonical materialization is established, one scheduler effect per project reconciliation step. Unresolved effects block desired-generation replacement. Explicit owner stop/pause and exact fresh project-terminal proof suppress all self-heal, including when owner-pause evidence and scheduler state disagree.

The scheduler backend remains an explicit capability boundary. This release can reconcile only through a backend the host actually provides and authorizes; it does not fabricate automation APIs. Fleet supervision may compose survivability reconciliation with ordinary liveness recovery: every registered desired watchdog is assessed, scheduler mutations share a bounded fleet effect budget, and deferred/broken repairs remain continuation work. Existing owner-paused schedulers remain paused.

The Fleet Supervisor itself has one minimal sentinel role. When an independent scheduler backend exists, that sentinel reconciles only the `fleet-supervisor` desired-state materialization using the same generation fencing and owner-pause gates. Recreate/adopt/enable remains nonterminal for the sentinel until a real supervisor wake is requested or fresh healthy/paused/terminal evidence is observed. The sentinel never develops projects or becomes a super-writer. Diverse-provider HA for the sentinel is explicitly deferred.

Verification includes deletion/recreation, disabled recovery, overdue kick, configuration drift, duplicate materialization, flapping, lost create reply, unknown effect without materialization, post-claim owner stop, generation fencing and terminal/owner-pause suppression.
