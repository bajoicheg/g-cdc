# CDC 2.11.3 — Multi-Subscription Coordination & Ownership Integrity

Status: owner-authorized implementation scope. Base authority: released CDC 2.11.2 at `48e637b230e7640d0dcd13da60d712f38f59a2b6`.

## Problem

Multiple ChatGPT subscriptions may concurrently operate the same CDC Fleet. Project-level leases and lanes protect project writers, but CDC 2.11.2 does not define an active-active-safe Fleet Supervisor leadership boundary. Separately, live rollout reproduced orphaned invocation leases on three consumers and a partial metadata adoption on one consumer.

## Required behavior

1. Exactly one Fleet Supervisor invocation can hold side-effect leadership for one Fleet at a time through durable CAS.
2. Standby supervisors can observe, assess and work as independent project executors, but cannot emit Fleet-wide side effects without leadership.
3. Fleet effects are one-shot and bind leader generation/invocation plus exact observed Fleet HEAD.
4. Runtime liveness is independent evidence. Owner/TTL alone never means `active`.
5. Final response is fail-closed for an invocation that acquired a lease until exact release is durable.
6. Consumer adoption is detached/atomic: no shared ref movement until package tree and all required bindings are complete.
7. TTL/provider terminal/scheduler silence never grants takeover.
8. All controls remain authority-minimizing: no project product-write/merge/release/scope authority is created.

## Acceptance

- two concurrent supervisor acquisition attempts from the same coordination revision yield at most one CAS winner;
- duplicate Fleet effect intent produces one claim; differing intent under the same effect ID is rejected;
- unknown leader effect blocks replacement; terminal reconciled effects allow replacement only with exact executor-stopped evidence;
- no-runtime lease is `unknown`, not `active`;
- stopped/no-effect lease is `orphaned_recoverable`, not `active`;
- an owned lease makes the final-response gate RED; exact post-release state makes it GREEN;
- partial adoption preparation never reaches a shared-ref publication state;
- exact detached package tree + full bindings + unchanged live HEAD yields one conditional-fast-forward boundary and exact readback requirement.
