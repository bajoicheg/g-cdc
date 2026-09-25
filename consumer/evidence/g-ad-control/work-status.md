---
schema: development-work-status/v4
repository: bajoicheg-private/g-ad-control
branch: codex/build-0.2.0-engineer-attribute-workflow
policy_revision: 2026-09-24-cdc-2.6.0-fleet-control-plane
policy_digest: 9027ef09bc7b13f844cf4eb70b66b341aafd1185be70810ab9344bc34b200345
observed_at_utc: '2026-09-25T05:31:00Z'
orchestration_origin: chat
active_executor: none
lease_state: released
executor_heartbeat_at_utc: null
execution_lease_until_utc: null
waiting_external_kind: null
waiting_external_id: null
waiting_external_sha: null
operation_intent_ref: null
operation_key: null
resume_capsule_ref: 'https://github.com/bajoicheg-private/g-ad-control/blob/cdc/coordination/resume.json'
execution_continuity:
  invocation_id: null
  runnable_next_action: false
  meaningful_progress: true
  primitive_steps_since_progress: 0
  completion_gate: resumable_blocker
  last_progress_ref: 'cdc26-converged:git-tree:e2cf6199eb60ca998012184b460c9a05c9f33b80'
control:
  execution_lease_ref: refs/heads/cdc/coordination
  execution_lease_revision: abf3f335344a2c5bf87c940820fb99d77d550b88
  executor_id: null
  lease_generation: 26
  budget_ref: https://github.com/bajoicheg-private/g-ad-control/blob/cdc/coordination/budget-ledger.json
  recovery_snapshot_ref: null
  external_wait_ref: null
active_change: build-0.2.0-engineer-attribute-workflow
current_task: 0.2.0/8.3
phase: validation
implementation_sha: adb912d1aa4537615136cdcaac526a5c2432d4e4
candidate_sha: adb912d1aa4537615136cdcaac526a5c2432d4e4
last_green_sha: 060b358a35b07286de614c04eae715ae2873bb0f
last_green_evidence: https://github.com/bajoicheg-private/g-ad-control/pull/1#issuecomment-5807875527
active_compute: ''
active_ci_run_id: ''
last_ci_run_id: '36043963217'
last_ci_status: completed/failure
release_version: 0.2.0
release_candidate_sha: ''
release_state: not-started
blocker: 'task83_portable_validation_blocked; bounded payload correction adb912d1 includes docs/runbook/pilot-v0.1.0.md, but this runtime has no dotnet and the Codex PR execution path has no fresh recovery evidence after repeated setup failures; Windows/PostPublish final remains forbidden before exact-SHA portable GREEN'
next_action: 'Route exact candidate adb912d1 through fresh capability evidence. If the Codex PR execution path gains specific recovery evidence or an independent dotnet10 Linux runtime is available, run one guarded COMPUTE_ONLY exact-SHA portable GREEN. Only then dispatch the already-routable Windows/PostPublish final gate under the conserve repair authorization.'
---

# Task 8.3 — portable payload correction

Exact Windows evidence run `36043963217` established the RED: `docs/runbook/pilot-v0.1.0.md` was absent from the generated portable payload. Commit `adb912d1aa4537615136cdcaac526a5c2432d4e4` adds that existing repository runbook to the package file-set assertion and copy list for both products. No stale CI run was repeated. Exact-SHA portable GREEN and Windows final evidence are still pending.

# CDC 2.6 integrated policy checkpoint

Validated package source `bajoicheg/g-pc-health-check@1e20edd807e3bae60b82aafdb2b9daa503e37715`, package tree `e2cf6199eb60ca998012184b460c9a05c9f33b80`; validation run `36051402864` passed package validation, 233/233 CDC tests, adapter and checkpoint validation. Live package tree was independently re-read as the same `e2cf6199eb60ca998012184b460c9a05c9f33b80`. Task 8.3 product RED and conserve budget remain unchanged.

# CDC 2.5 integrated policy checkpoint

CDC 2.5 is live on the product branch. All 90 vendored CDC blobs are byte-identical to canonical commit `116d0a6ae6c3f35a22fc6170a25eece3e011eff5`. Live coordination is released `execution-lease/v2` generation 25, the exact a7 external guard is terminal/reconciled, and backend registry, continuation queue and resume capsule are initialized. The CDC migration does not claim Task 8.3 product GREEN.

# Task 8.3 — historical portable validation before current Windows RED

The integrated generated-PowerShell fixture and authenticated-context implementation are present. Exact SHA `30b12d64502e83e557f0ddb6dd805df6c23fc3af` passed OpenSpec strict validation, Engineer Application build and focused test `1/1`, Architecture build and dependency/graph tests `35/35`, with a clean unchanged worktree. Its Windows-only execution body remained `NOT_RUN` on Linux.

The same run established the corrected compute toolchain: PyYAML `6.0.3` and pinned OpenSpec `1.13.2`. The overall gate stayed RED only because this checkpoint used the unsupported free-form phase `powershell-auth-context-portable-green`; this status-only commit normalizes it to the schema value `validation`.

That earlier portable checkpoint predated the current Windows attempts. The authoritative current evidence is now Actions run `36043963217` on candidate `833c5d11d8d73197b9a230d53f5b4ceb69a72bab`: it is terminal `failure` in PostPublish because the portable payload is missing `docs/runbook/pilot-v0.1.0.md`. Actions remain `conserve`; do not repeat the stale attempt without the bounded corrective change recorded in frontmatter.
