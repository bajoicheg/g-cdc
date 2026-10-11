---
schema: development-work-status/v4
repository: bajoicheg-private/g-ad-control
branch: codex/build-0.2.0-engineer-attribute-workflow
policy_revision: 2026-09-25-cdc-2.7.1-autonomy-lease-v2
policy_digest: 567ecb4abcadada50bcfae447bda2c06925928724a4f220902d9ebb6fe51a1a3
observed_at_utc: '2026-09-25T12:16:00Z'
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
  completion_gate: scope_complete
  last_progress_ref: 'cdc-release:8e97192ef89bf37657a4444a954530f22e8b2267'
control:
  execution_lease_ref: refs/heads/cdc/coordination
  execution_lease_revision: null
  executor_id: null
  lease_generation: 34
  budget_ref: https://github.com/bajoicheg-private/g-ad-control/blob/cdc/coordination/budget-ledger.json
  recovery_snapshot_ref: null
  external_wait_ref: null
active_change: ''
current_task: ''
phase: complete
implementation_sha: b8bd8573eb815801c5b4cf0e49e942d197e83f6d
candidate_sha: 3d449fe00927ab367a52d9ab680612c250dc2ee1
last_green_sha: 3d449fe00927ab367a52d9ab680612c250dc2ee1
last_green_evidence: https://github.com/bajoicheg-private/g-ad-control/actions/runs/36118643314
active_compute: ''
active_ci_run_id: ''
last_ci_run_id: '36117227433'
last_ci_status: completed/success
release_version: 0.2.0
release_candidate_sha: b8bd8573eb815801c5b4cf0e49e942d197e83f6d
release_state: released
blocker: 'none'
next_action: 'No runnable action; 0.2.0 scope is complete and archived. Await the next authorized OpenSpec change.'
---

# 0.2.0 — terminal scope checkpoint

OpenSpec change `build-0.2.0-engineer-attribute-workflow` is complete and archived at
`openspec/changes/archive/2026-09-25-build-0.2.0-engineer-attribute-workflow`.
Task 8.3 is checked complete in the archived task list.

## Final Windows evidence

Exact product candidate `b8bd8573eb815801c5b4cf0e49e942d197e83f6d` passed GitHub Actions run
`36117227433`:

- solution build: 0 warnings / 0 errors;
- PrePublish: 684/684 passed across 11 suites;
- PostPublish: 28/28 passed;
- Central portable smoke: `SMOKE_VERIFIED`;
- Engineer fake-directory-writer portable smoke: `SMOKE_VERIFIED`;
- final release gate: `RELEASE_GATES_PASSED`.

The verified pilot release bundle is Actions artifact `10855727566`
(`portable-pilot-36117227433-1`). Its two application ZIPs and sidecars were
read back and hashed independently:

- `GAdControl-0.2.0-win-x64.zip` — SHA-256
  `ac4c56f9d8f45860255d2cf7f91802a72099f61ed7c6dc4560d29858a9b38412`;
- `GAdEngineer-0.2.0-win-x64.zip` — SHA-256
  `268e432c8331cfc8047304c90e25e9719c47b0782443ae2b166e9eda2e222d52`.

Both sidecar checksums match the corresponding ZIP bytes. The artifacts are
explicitly `UNSIGNED-NOT-FOR-PRODUCTION`, which is the accepted pilot state
and does not claim protected production signing.

## OpenSpec closure evidence

Closure commit `3d449fe00927ab367a52d9ab680612c250dc2ee1` synchronized the five
0.2.0 delta capabilities into canonical specs, marked task 8.3 complete and
moved the change into the dated archive.

Isolated validation run `36118643314` checked that exact closure SHA:
canonical specs strict = 9/9 passed, archived changes strict = 2/2 passed,
active change absent, archived task 8.3 checked, worktree unchanged.

No active OpenSpec task or external operation remains.


## CDC 2.7 canonical core adoption — 2026-09-25

At released execution-lease/v2 safe boundary generation 31, the vendored CDC core
was replaced with immutable canonical CDC 2.7.0 from `bajoicheg/g-cdc`.
Consumer lock: `docs/cdc-consumer-lock.json`; release ref
`refs/heads/release/v2.7.0`; release commit
`5b84c89596e04d8411bf6cc24d8aa882a24c483a`; required exact package tree
`a667549d48c2e93cba36359335c1b1ff4534ac86`.

This process-only adoption does not alter the already terminal/released 0.2.0
product evidence or create a new OpenSpec scope.

Adapter reconciliation completed under generation 33: policy minimum and
convergence target are CDC 2.7.0, with semantic policy digest `7011536eaa123f009f02bdf0d4a4cb8b6c50b6d3d8a96d3337a5959cfb25a9a3`.


## CDC 2.7.1 autonomy + lease-v2 hotfix convergence — 2026-09-25

At released generation 33, generation 34 acquired an invocation-bound v2 lease only
for process convergence. The vendored canonical core was advanced from CDC 2.7.0 to
released CDC 2.7.1 from `bajoicheg/g-cdc`, release ref
`refs/heads/release/v2.7.1`, release commit
`8e97192ef89bf37657a4444a954530f22e8b2267`.

The exact vendored subtree is
`a78b8e7df4bfdd5a067f9e9da5a3a8a4b33394fc` and
`docs/cdc-consumer-lock.json` binds that exact identity. Adapter policy minimum and
convergence target are 2.7.1. The semantic adapter digest was independently recomputed
from the live YAML with the same canonical JSON/SHA-256 algorithm as
`contracts.digest`; the implementation was first checked against the prior known
2.7.0 digest before use. Result:
`567ecb4abcadada50bcfae447bda2c06925928724a4f220902d9ebb6fe51a1a3`.

Two Codex COMPUTE_ONLY attempts returned service-level
`Codex couldn't complete this request` before producing repository execution evidence;
both reservations/intents were reconciled terminal and no product/Actions work was
started. Convergence therefore used immutable canonical release identity plus local
deterministic policy-digest verification. Product scope 0.2.0 remains terminal,
released and unchanged.
