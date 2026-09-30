# Multi-subscription coordination and ownership integrity

CDC 2.11.3 allows multiple independent ChatGPT subscriptions/executors to cooperate without making the Fleet control plane active-active.

## Fleet Supervisor leader

Use a dedicated `fleet-supervisor-state/v1` document on an isolated Git CAS ref such as `refs/heads/cdc/fleet-supervisor`. The embedded `execution-lease/v2` is bound to the authoritative Fleet repository and `refs/heads/cdc/fleet`.

Exactly one owner/generation/invocation may be the Fleet side-effect leader. Other subscriptions remain observers/standby Fleet supervisors or ordinary project executors. A Fleet leader never receives project product-write, project takeover, merge, release, scope-expansion, or implicit scheduler authority.

Every Fleet-wide effect is a one-shot durable claim identified by a **deterministic canonical SHA-256 effect ID** derived from kind + target + intent + observed Fleet HEAD, plus exact leader generation/invocation. Callers cannot choose alternate IDs for the same semantic effect. Supported effect classes include Fleet-ref publication, project wake, scheduler repair, and continuation enqueue. Reusing the same effect ID with the same intent observes/reconciles the original claim; reusing it with different intent is a collision. A moved Fleet HEAD requires replanning before a claim. Unknown/submitted effects block leader replacement until reconciled. A standby may perform only evidence-only provider reconciliation against the original effect ID + intent digest: complete terminal/not-found lookup may close the effect, running/unknown observation keeps it pending, and reconciliation never grants submit/replay authority.

Leader replacement never follows TTL alone. Use exact `executor_stopped` evidence plus no unresolved leader effects. The ordinary execution-lease transactional finalization/release contract remains authoritative.

## Truthful liveness

Use `scripts/execution_liveness.py` with independent **fresh** runtime evidence. A historical running observation that exceeds the runtime-observation freshness bound degrades to `unknown` even if the lease was renewed. Lease presence, owner ID, heartbeat age, scheduler timestamps, or TTL do not by themselves prove an executor is active or stopped.

The normalized states are:
- `active`: exact invocation is independently observed running and the lease is fresh;
- `orphaned_recoverable`: exact invocation is independently observed stopped with no pending shared writes, guard, or current-generation submissions;
- `blocked_unknown_effects`: exact invocation stopped but pending effects require reconciliation;
- `unknown`: runtime identity/liveness is not independently proven;
- `released`: lease has no owner.

Liveness classification is evidence only and never authorizes takeover.

## Final-response boundary

Use `scripts/final_response_gate.py` immediately before a CDC terminal/final response. An invocation that acquired a lease must prove that the exact owner/generation/invocation appears in `last_release`, and execution continuity must be in post-release terminal state. Pre-release `ready` evidence is insufficient.

This gate makes the orphan-lease defect a failed executable check instead of a prose-only instruction. Host runtimes that cannot intercept a final channel must still run/persist this gate as the required terminal evidence; inability to enforce a host channel is a capability boundary, not permission to report a released state.

## Atomic consumer adoption

Use `scripts/consumer_adoption.py` together with the existing detached migration transaction. Package bytes, consumer lock, adapter, checkpoint, adoption/provenance record, and other required paths are prepared away from the shared source ref. Exact target package subtree is verified before building the candidate commit.

The shared source ref has exactly one publication boundary: an exact expected-head conditional fast-forward to the fully assembled candidate, followed by exact readback. A moved source HEAD replans; an uncertain publication reconciles; package-tree mismatch fails closed. VERSION-only or metadata-only exposure on the shared source ref is never a valid adoption state.

## Multi-subscription pressure invariants

Release evidence must cover two supervisor identities racing from one initial coordination revision, duplicate effect claims, stopped leaders with both clean and unknown-effect states, final-response attempts while a lease remains owned, and interrupted consumer adoption before publication. At most one leader/effect CAS may win, no force update is allowed, and no partial target version may appear on a shared consumer ref.
