# SPEC-compliance review — GREEN implementation; acceptance gates remain open

Date: 2026-10-08. Same cloud-continuation-a1 session; no new provider/worker start.
Exact reviewed HEAD: 9516aa1fafd32fcf7fcb239e96fa1e6b4d141d3a
Exact package tree: 9c45d98c3254e9658d452c505d8c97698e3fc9a7
Base: b72435542f40ec3f5b195f357c968c2346ab4f8f
Worktree: /workspace/work/cloud-continuation-a1-9516aa1
Specification: docs/superpowers/specs/2026-10-07-parallel-maintenance-design.md
Plan: docs/superpowers/plans/2026-10-07-parallel-maintenance.md

## Scope and result

Reviewed complete 35-path aggregate delta and eight introduced commits, including implementation, tests, metadata, recipe, execution records and compressed evidence. Full binary delta saved separately. No actionable implementation SPEC deviations found. This is a new final-SHA SPEC report, not a relabeling of the historical cf383f6 reviews, not CODE QUALITY approval and not release authority.

## Requirement evidence

- Exact argv: evidence_reuse.py changes only per-element nonblank validation to isinstance(str). Nonempty list validation remains. JSON canonical comparison preserves empty/whitespace strings and list order without trimming. Nonstrings and empty containers reject; failed/not-run source and exact_candidate_required blockers remain. Original SHA/evidence are retained; all authorization outputs remain false. Added tests cover both input sides, unchanged exact strings, changed whitespace, invalid types/containers and input nonmutation; existing order regression remains.
- Transport: version-derived bytes are b'2.12.1\n' (7 bytes). Independently recomputed Git blob 3cf561c0b67cfad5880cefd2c3cd5f96dee2af2f and one-file tree 4284906c47bf0189dc7eaa12887a87b931cc12bb, both match the illustrative manifest. New regression generates bytes from manifest version and calls real verify_directory. Canonical repository/zero commit placeholders remain illustrative and do not establish adoption.
- Existing machinery: no new pool/executor/lease/budget subsystem or cap increases. Runtime recipe requires durable budget readback then exact pool CAS, isolated same-base writers, explicit write claims, serialization of dependencies, full-history containment and a single root integrator. Optional analyst must fit existing caps; cap-two fallback queues analysis. Worker scopes in introduced history are confined to the two argv paths and two transport paths; remaining delta belongs to root candidate/docs/evidence preparation.
- Budgets and metrics: execution record reports reservation-to-acceptance durations, zero conflicts, concrete patch-heading rework, original failed validation and justified second cycle. Provider/dependency waits and tokens/cost are null with explanations; no comparative speedup is claimed. Reservation times are explicitly labeled and are not presented as measured worker processing times. Current budget9e606/handover187453 are user-supplied fresh state identifiers, not imported lease authority; historical budget snapshots are not used to admit any effect.
- Frozen tests/evidence reuse: all seven stored raw/compressed log hashes independently match. Historical argv RED6 subtests/GREEN16 and transport RED1/GREEN15 combined regressions remain traceable. Bootstrap log records 46 OK; corrected clean-consumer log records 1121 OK. The first FULL failure is preserved. Recorded tested d709c0c and package-source a717db0 both resolve to final package tree; package/bootstrap/workflow/consumer/compatibility/fault paths are unchanged from d709c0c to final HEAD. Therefore final metadata does not invalidate unchanged package evidence; it does not inherit exact-SHA CI. No tests or FULL were rerun for this review.
- Candidate/release boundaries: source lock pins immutable released2.12.0 commit540d42b/package247fac; version/manifest/agent metadata and compatibility/three archived source labels agree on candidate2.12.1/package9c45. Only archived source labels change, not live GAD/consumer state. Historical release/evidence, bootstrap/workflows, fault inventory, legacy quality gates and paused schedulers are preserved by the delta.

## Findings and remaining gates

No blocking implementation SPEC findings. Acceptance remains incomplete:
1. Required exact-final-candidate CI is absent per the user's fresh three-surface observation; obtain it only after separate real managed admission, latest budget/intent/claim and old ci-a1 reconciliation. Shell path remains blocked at injected proxy socket EPERM. Workflow supports dispatch and PR-to-main triggers, neither is launched here.
2. This final SPEC review does not satisfy the subsequent ordered final CODE QUALITY review. Historical reviews retain their original SHA. Previously observed final-review pool acceptance alone lacks reviewed report/receipt details here and is not retargeted as quality approval.
3. Explicit package/bootstrap/fault/three-consumer acceptance and evidence-reuse coverage must be assembled at release acceptance. Stored records identify prior successes, but this report does not freshly execute or independently establish every release gate.
4. Source publication/release acceptance and immutable receipts remain separate. Personal installation, adoption, Fleet and scheduler changes are excluded.

## Read-only commands and probes

Socket to injected proxy:8080: errno1 EPERM. timeout15s git ls-remote origin exact branch: exit128. timeout15s gh api repos/bajoicheg/g-cdc --jq .full_name: exit1. git rev-parse HEAD/package and git status: exit0, clean detached worktree. git diff/log/cat reads: exit0. This read-only hashing/binding probe: exit0 on success. No proxy/auth/allowlist changes, candidate edits, commits, CI, leases, or FULL. Reports written outside Git; old reports untouched.

## Complete changed-path inventory

- AGENTS.md
- README.md
- VERSION
- compatibility/matrix.json
- consumer/evidence/g-ad-control/source.json
- consumer/evidence/g-pc-health-check/source.json
- consumer/evidence/g-supervisor/source.json
- docs/execution/cdc-parallel-maintenance-20261007.json
- docs/execution/parallel-maintenance-20261007/argv-green.log.gz
- docs/execution/parallel-maintenance-20261007/argv-red.log.gz
- docs/execution/parallel-maintenance-20261007/audit-report.md
- docs/execution/parallel-maintenance-20261007/bootstrap-corrected.log.gz
- docs/execution/parallel-maintenance-20261007/consumer-corrected-full-result.json
- docs/execution/parallel-maintenance-20261007/consumer-corrected-full.log.gz
- docs/execution/parallel-maintenance-20261007/consumer-full-result.json
- docs/execution/parallel-maintenance-20261007/consumer-full.log.gz
- docs/execution/parallel-maintenance-20261007/quality-review.md
- docs/execution/parallel-maintenance-20261007/spec-review.md
- docs/execution/parallel-maintenance-20261007/transport-green.log.gz
- docs/execution/parallel-maintenance-20261007/transport-red.log.gz
- docs/execution/parallel-maintenance-20261007/validation-cycle-2.json
- docs/roadmap.md
- docs/superpowers/plans/2026-10-07-parallel-maintenance.md
- docs/superpowers/specs/2026-10-07-parallel-maintenance-design.md
- release/candidate.json
- release/source.lock.json
- src/continuous-development-cycle/SKILL.md
- src/continuous-development-cycle/VERSION
- src/continuous-development-cycle/agents/openai.yaml
- src/continuous-development-cycle/manifest.json
- src/continuous-development-cycle/references/runtime-routing-and-subagents.md
- src/continuous-development-cycle/scripts/evidence_reuse.py
- src/continuous-development-cycle/templates/package-transport.json
- src/continuous-development-cycle/tests/test_evidence_reuse.py
- src/continuous-development-cycle/tests/test_package_transport.py
