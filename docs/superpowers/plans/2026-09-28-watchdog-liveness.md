# CDC 2.11.1 implementation plan

Use subagent-driven-development for independent isolated slices and executing-plans discipline for parent integration, as requested by CDC. Architecture and stage order are already approved; no additional conversational approval boundary. Parent is sole integrator and remote writer.

## Task 1: liveness contract and executable Fleet recovery

Own new scripts/watchdog_liveness.py, scripts/fleet_watchdog_runtime.py, optional reusable scripts/git_document_store.py, their tests/templates/reference, and compatible watchdog_health.py integration. Write failing scenarios first, retain RED output, implement durable one-shot recovery and real Git tests. Do not edit target resolver, version/release metadata, SKILL or shared roadmap. Acceptance: disabled/overdue/premature completion CRITICAL; owner pause wins; budget remainder durable; every registered project assessed; duplicate/unknown owner/external/run denied; policy refreshed before each effect; process restart does not replay claims.

## Task 2: live target resolver

Own new scripts/live_target.py, its tests and reference, templates/watchdog-prompt.md. Write failing tests first. Read registry/target from one pinned live revision, validate release provenance and freshness, reject disagreeing or moved authority. Accept actual Git source/transport interfaces with existing identity normalization. Never perform adoption or scheduler writes. No hardcoded mutable target versions in prompt.

## Task 3: parent integration and release

Record 2.11.0 release/activation/PR consolidation; update development driver and stage metadata. Integrate workers, reconcile interfaces and guidance. Run focused regressions then full package/bootstrap/validator/three snapshots. Freeze source before independent spec review, fix findings, then independent quality review. Refresh evidence only for changed package identity. Publish exact-head PR, observe CI and release only GREEN. Activate/read back personal 2.11.1. Continue the approved 2.11.2 lanes stage in the same invocation.

## Budget and continuity

This is a new approved release task, not a reset of managed-execution attempts. Preserve the previous ledger. Task/wake agent cap 8, active workers at most 3, checkpoint reserve 3000 tokens/15 calls; provider quotas unknown. Reserve before agent/CI starts. Local useful RED/GREEN loops, public standard Actions final gate. No new scheduler starts. Consumer ownership blockers cannot stop independent core work.
