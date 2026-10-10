# CDC 3.3 release delivery and safe rollback — design

## Authorized outcome

Complete the owner's approved final 3.x stage: reusable automation that verifies
an immutable release, builds an exact atomic consumer adoption, and can restore
a previously accepted release through a new forward commit. Source release,
consumer publication, personal installation, and executor closure remain distinct
evidence surfaces. Fleet and schedulers stay paused. Develop only after released
3.2 and strict personal acceptance, using that unchanged runtime as N-1.

## Approach

Extend the existing mechanisms rather than create a second orchestrator. Extract
canonical release verification from live_target into a reusable function while
preserving every legacy v1/v2 resolver check. Add release_delivery.py with a real
Git assembly API and explicit publication API composing GitSource,
migration_transaction, GitDocumentStore and GitConsumerAdoptionPublisher. Keep
cdc.py's new delivery command read-only: it validates a proposed delivery and
reports prerequisites. Effects are exposed separately to an already authorized
managed owner, never inferred from the CLI's successful exit.

The alternative of only adding another recommendation planner does not automate
the missing assembly step. A replacement publisher/lease system would duplicate
existing durable attempts and introduce unnecessary authority paths.

## Exact release verification

Verify configured canonical endpoint and repository, exact release ref/commit,
actual VERSION/package tree, released evidence and original candidate ancestry.
Split evidence requires its independently pinned ref/commit on that same endpoint
and descendant/package equality. Retain strict colocated evidence compatibility.
Freshly pin and recheck every authority before returning and again at publication.
Unknown, stale, moved or malformed provenance fails closed. Reuse the same checks
in live_target; do not weaken existing Fleet validation.

## Detached delivery

The real Git builder reads the pinned consumer source and existing lock, adapter
and checkpoint. It verifies the target release through the configured canonical
GitSource in the same object cache. It imports the exact canonical package tree
without copying/rewriting core files. A temporary index starts from the fresh
consumer tree, updates only the package, release lock and append-only adoption
record, and carries the current adapter/checkpoint objects unchanged after
validating them against the target version. Write a detached tree and a candidate
commit whose sole direct parent is the original source HEAD. Preserve
all other files and history. Reject unsafe/overlapping paths, invalid objects,
incompatible policy, active checkpoint or pending operation. Package/lock/control
bindings must all agree before an authoritative assembly record is committed.
No product ref moves during assembly.

An incompatible policy requires the existing separately reviewed migration before
delivery; this API cannot silently rewrite policy, budgets, guards or checkpoint
history. Reject initial package/lock drift for separate bounded repair. Before
preparing a new candidate, inspect the existing authoritative attempt journal;
any submitted/unknown publication requires reconciliation of that exact original
operation and prevents manufacturing a replacement candidate/attempt.

Publication re-verifies the canonical release, authoritative assembly and actual
candidate tree, then delegates to the existing durable consumer publisher. Its
expected-head fast-forward, attempt journal, exact readback and UNKNOWN/no-replay
behavior remain authoritative. Before any coordination or product write, perform
the existing authentic GitLeaseStore action check bound to this repository/ref,
owner/generation/invocation and fresh clock. The API acquires/releases no lease,
launches no executor/CI, raises no budgets and operates no scheduler.

## Rollback

Rollback uses the same exact-release verification, assembly and publication path.
Its target must match a previous accepted consumer lock retrieved from immutable
consumer history, with that historical package tree independently checked. The
new candidate descends from the current consumer HEAD and replaces only the CDC
package and release lock; current adapter/checkpoint remain unchanged and are
validated against the restored runtime. Append to any existing target-version
adoption audit instead of replacing its history. A new audit
record binds original acceptance, current source and restoration. Preserve budget,
guard and prior audit history. Ref reset, force push, unverified version downgrades
and reuse of an uncertain publication attempt are forbidden.

## Validation and completion

Observe behavioral RED before implementation. Use actual local bare Git fixtures
for forward adoption, whole-tree/mode identity, preservation, rollback ancestry,
stale source, wrong history, moved release/evidence, guard/owner rejection,
interrupted assembly and lost publication response. Exercise CLI duplicates and
malformed inputs. Existing live-target and consumer-adoption regressions remain
mandatory after composition changes. Freeze one consistent candidate, run
independent N-1/bootstrap, clean consumer FULL and three archived consumers, then
ordered exact-candidate SPEC and distinct QUALITY. Required hosted CI must prove
the full candidate root. Release and physically finalize its actual executor,
strictly install/read back all personal package bytes, and close the owner queue
only after the final gates pass.
