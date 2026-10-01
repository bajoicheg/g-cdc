# CDC 2.11.4 — Managed Host Bridge design

Status: owner-authorized on 2026-10-01 after the first live CDC 2.11.3 consumer retest exposed a bootstrap usability gap.

## Problem

CDC 2.11.3 correctly rejects new persistent execution-lease/v2 ownership from ordinary ChatGPT, Work, Codex, watchdog and generic API surfaces unless a package-owned managed terminal capability exists. The package already contains the real ManagedExecutorRuntime, LocalCommandBackend and managed terminal hold, but it does not expose a host-facing start/observe/cancel/finish surface. Its CLI only exposes the private supervisor entry point.

That leaves a live consumer in an observer-only state even though the released package contains the machinery capable of safe ownership. The safety gate is correct; the missing host adapter is the defect.

## Required behavior

1. Add a package-owned host bridge with a durable serializable handle, while the non-serializable managed terminal capability remains internal.
2. start MUST verify exact repository/remote/source HEAD and immutable managed-pool plan, launch through ManagedExecutorRuntime, acquire the project lease only from the live package-managed supervisor, persist ownership, then release a worker gate.
3. Worker code runs only in its isolated managed worktree/branch. start never publishes the shared product/source ref.
4. observe and cancel address the exact durable task/attempt/launch; they never replay a lost start.
5. finish requires the worker to have reached the managed terminal hold, verifies the exact result ancestry and write-set containment, performs one expected-head conditional publication with a durable publication-attempt journal, transactionally finalizes/releases the exact managed lease, then records pool acceptance/integration.
6. finish returns immutable execution-release-receipt/v1 and a final-response gate result. A crash after acquisition/publication/release is reconciled from durable runtime, lease and publication state instead of blind replay.
7. The bridge is transport-neutral: Chat/Work/plugin hosts invoke the same JSON request contract. The package does not pretend a ChatGPT plugin exists when the host has not installed one.
8. Arbitrary managed commands remain cooperative execution with the invoking host privileges; production hosts MUST apply their own authorization/command policy before accepting a bridge start request.

## Non-goals

- Do not weaken the 2.11.3 managed-only lease admission.
- Do not make Fleet Supervisor a product writer.
- Do not grant ordinary chat a serializable lease token.
- Do not merge/release CDC 2.11.4 from an unmanaged chat; integration remains a managed publication boundary.
