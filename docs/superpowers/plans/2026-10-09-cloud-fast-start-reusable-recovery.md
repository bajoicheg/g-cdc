# CDC 2.13.0 implementation plan — issue100

> **For agentic workers:** Use superpowers:executing-plans for inline work or subagent-driven-development only when actually authorized and durably reserved. Track every step against exact evidence; no implementation before Root's independent design review.

Goal: fast Cloud continuation with reusable verified recovery, integrating the existing routing, journals and managed gates. Authority: immutable released2.12.1 (9b38bd4d/package9c45), design in docs/superpowers/specs/2026-10-09-cloud-fast-start-reusable-recovery-design.md. Architecture: two small pure preparation/profile modules and explicit schema extensions over existing transports; no second orchestrator. Python standard library, existing unittest suite, native Git CAS and managed_host_bridge.

## Phase 0 — admission and ordered plan review (current)

1. Fresh exact source main5720 identity, immutable2.12.1 package and canonical main lease56 unowned/unguarded/released; retain provider inventory unknown and GPC claimed guard. Use existing connected Cloud, no CLI auth retries/nested task/Codespace starts.
2. Start new task cdc-issue100-cloud-start-and-recovery and wake issue100-preparation-to-implementation-20261009 with released ordinary budget template. Preserve immutable predecessor a353467b965c686b416459b3fe0363e63eaffefb/143events and historical operations in dedicated history links. No cap migration/reset/refund. Genuine newtask is issue100, not a workaround for exhausted predecessor.
3. Actual managed local planning writer uses new issue100 pool/journal/attempt and isolated /workspace/work/issue100-cloud-fast-start-20261009. Its source main authority uses canonical historical codex-compute cdc/g-cdc-2114-main-20261003-lease; never create another main lease under a different ref. Claim only AGENTS.md, docs/roadmap.md and these two new planning documents. Stage all4, cheap staged layout check, one clean commit; core must verify changed paths == history touched paths and package unchanged.
4. Publish detached review branch under fresh owned action-specific intent/budget/guard/one-use claim and native non-force push/exact readback. Main remains unchanged. Reserve ONE agent_start issue100_design_review_a1 under exact plan/source/request bindings with actual remote CAS/readback. Root launches the independent reviewer; no claimed completion before actual child/report.
5. Record the actual physical reviewer terminal result separately from semantic CHANGES_REQUIRED/GREEN; preserve the original admission snapshot. Await Root plan review. A terminal held writer result cannot be edited by another shell writer. If revision is needed, finish the current documentation-only proposed-plan writer normally, verify release/quiescence, then admit a genuine next bounded planning-revision writer with fresh source/lease/budget. Keep resume checkpoint and real completed-work admission renewal as appropriate; no idle heartbeats or expired-owner takeover. If core requires closure, actual normal finish/release/quiescence and later fresh admission preserve the same task ledger/history. Planning completion is not overall scope completion.

Coordination prefix refs/heads/cdc/issue100-cloud-fast-start-20261009 on private bajoicheg/codex-compute: -pool (pool-state.json), -budget (budget-ledger.json), -handover and -review (document.json); source detached review branch on bajoicheg/g-cdc. Canonical main writer lease retains its original ref/history. Future independently scoped CI/read-only lease refs must bind their actual reviewed source/task, never substitute for canonical main publication authority.

## Phase 1 — profile and access-mode qualification

Files: NEW scripts/codex_cloud_profile.py and tests/test_codex_cloud_profile.py; NEW templates/codex-cloud-profile.json; candidate-only schema/reference documentation; project-owned docs/cdc-cloud-profile.json outside package.

- Write tests first: strict keys/secrets/URL credentials; null environment/version; exact list argv roundtrip; repo/env/setup/policy invalidation; CLI-version invalidates CLI only; future/incomplete/stale probe; current native ready with CLI401 yields native route and CLI unavailable, no Codespace recommendation.
- Run python -B -m unittest discover -s src/continuous-development-cycle/tests -p test_codex_cloud_profile.py. Observe actual failures because interface is missing, save RED receipt.
- Implement validate_profile and assess_profile exactly as design. No auth/proxy changes/provider calls. Run same focused command GREEN; inspect semantics, not tests mirroring assertions.
- Bind profile schema1/qualification probe1; unknown stays unknown. Existing ready flags do not silently become qualified. Review this narrow code diff before integrating phase2.

## Phase 2 — entrypoint delegates existing operation ownership

Files: NEW scripts/codex_cloud_entrypoint.py, tests/test_codex_cloud_entrypoint.py; narrow changes only when necessary in codex_cloud_cli.py, codex_cloud_development.py, capability_router.py, cost_router.py and their focused tests.

- RED behavioral contracts using actual existing transports with bounded fake runner/provider fixtures: active/submitting/unknown same key returns OBSERVE_EXISTING; lost response no second submit; prepare never calls submit; native current runtime with CLI401 continues locally; official UI unqualified stays unknown; wrong binding callback denies; report/diff mismatch fails; Cloud Development and COMPUTE_ONLY remain separate.
- Implement pure prepare and thin submit/observe/intake adapters. Preserve existing durable journal lock/idempotency and launch_authorized keyword callback. No global ready override, monkeypatch or direct private endpoint.
- Extend expensive-backend predicate only through existing cost_router: fresh allowed reason/evidence/budget required; missing CLI/transient Cloud failure alone cannot select Codespace create/resume. Existing explicit platform exception retains platform gate.
- Focused RED→GREEN command for new test file and affected router/transport regression files; do not rerun unchanged historical pilot/live transport probes. Save exact command/exit/input fingerprints.

## Phase 3 — qualified recipes and handoff

Files: scripts/recovery_recipes.py, scripts/resume_capsule.py only if required; NEW handoff validator adjacent to entrypoint or profile (no duplicated capsule validator); tests/test_recovery_recipes.py and new focused handoff tests; templates/recovery-recipes.json, references/deterministic-recovery.md, references/submission-recovery.md, references/runtime-routing-and-subagents.md.

- RED v1 compatibility, explicit v2 dispatch, stale/future provenance, cross-project local qualification, action allowlist, new correction signal required before repeated probe, partial inventory remains unknown, exact one next_action/reference bindings.
- Add explicit v2 catalog validation/selection; preserve v1 strict behavior and existing false authority flags. No arbitrary shell action strings/dependency installs.
- Use unchanged resume capsule assessor for mandatory fresh lease/source/checkpoint/provider recovery; cloud handoff references it. Historical unavailable may be superseded only by fresh bounded observation.
- Run affected narrow tests GREEN; inspect that recipe reuse cannot generate a new operation key or drop a guard.

## Phase 4 — instructions, package metadata and compatibility

Files: SKILL.md, VERSION/manifest/package metadata when release candidate is actually implemented; references/codex-compute.md and capability-routing.md; templates/AGENTS.snippet.md, watchdog-prompt.md, development-cycle.yaml; project-owned profile/checkpoint references. Do not edit installed personal skill from Cloud implementer.

- One startup entrypoint/profile, clear native/UI/CLI access qualification and control-host/compute separation; historical Codespace examples clearly labeled. Preserve platform/release gates and paused scheduling defaults.
- Explicit adapter schema evolution only if needed for profile field; old adapters remain supported, migration retains all product policy/budget/checkpoint fields. Unknown setup cannot be normalized to ready.
- Update package version to2.13.0 and manifest only as candidate metadata. Run changed schema/adapter/instruction consistency tests and staged python -B bootstrap/repository_layout.py. Refresh package file manifest after actual implementation; immutable2.12.1 untouched.

## Phase 5 — freeze, exact final reviews and required CI

- Review entire implementation history for touched==changed claims; normalize through a new honest single reviewed commit if gate requires, preserving every old branch/receipt and exact tree provenance. No bypass/history rewrite.
- Freeze ONE candidate SHA and package tree. Run python -B bootstrap/repository_layout.py; independent bootstrap configured tests; python -B bootstrap/consumer_package_checks.py (FULL new candidate); candidate package, compatibility/fault injection and three archived consumers required by current release protocol. Test names/counts are observed output, not historical expected GREEN.
- Publish exact detached candidate for ordered Root SPEC then distinct independent QUALITY. Reserve actual reviewer starts in same ledger before Root launches them. All open Critical/Important findings must close; changed candidate needs honest rebind/evidence.
- Fresh three CI surfaces/pulls; one exact required PR-triggered CI through actual managed scope and callback/claim. No duplicate trigger for an already active/unknown run. Official run/jobs/full logs and actual checkout/root/package provenance bind final exact candidate. Retain historical prior FULL evidence as history, not new-SHA claims.

## Phase 6 — source publication, personal installation and safe rollout

- Under actual canonical main managed writer, fresh expectedHEAD CAS main→accepted tested candidate, immutable refs/heads/release/v2.13.0, separately pinned evidence ref. No force, no API pretend lease. Own effects/intents/guards all reconciled, real managed finish/release/quiescence, pending reservations accurately settled.
- Root performs personal installation and independently verifies actual saved archive/loader, all file bytes/modes/package tree and remote readback. Report file acceptance separately from model behavior.
- Fresh per-consumer source/package/lock/adapter/checkpoint and canonical ownership; complete atomic package+lock+adapter+checkpoint+AGENTS provenance migration under actual scope. Ordered migration SPEC then independent QUALITY; no product source implementation or platform gate changes. Eligible independent scopes may run within genuine shared-budget CAS; GPC unresolved claimed guard remains protected until genuine reconciliation. Never infer quiescence from TTL/provider terminal status alone.
- Fleet target/registry and observer snapshots under genuine sole leader, pinned separate release evidence and fresh paused watchdog observations. No enable/run/rebind/reschedule; no retired consumer resurrection. Convergence vector retains actual source bindings and blockers, tolerates only audited budget-only descendants preserving lease/snapshot/source/checkpoint bindings.
- Final checkpoint exact source/release/personal/consumer/Fleet receipts, all own scopes released/quiescent, actual ledger pending missing/unknown0 if COMPLETE; otherwise truthful resumable blocked scope with charged unresolved operations. No milestone-only final while authorized runnable work remains.

## Stop/reconcile rules

Before each real effect: fresh exact source/identity/live owner/generation/invocation, action-specific intent, current policy/budget reservation, matching guard and one-use live callback. Unknown submission never replay. On interruption inspect persisted phase/readback, continue only missing terminal steps; no whole controller rerun. Budget ceilings/quota are independent of owner authorization: defaults do not prove provider capacity; unknown stays null. All actual starts/polls/tool calls/outcomes must be charged by caller. Root design review is next dependency; it is not a request for additional owner permission.

## Concrete review corrections and pre-implementation interface freeze (D100-01..04)

Actual report: /root/issue100_design_review,28761bytes/SHA441dead9592a390496c7bae81a3929026920c0a80c21ba85f269624f48b09676, physical completed/semantic CHANGES_REQUIRED. All4 Important findings accepted; revised design's typed-contract supplement and interface table are normative. No code before actual same-reviewer plan acceptance. Preserve old143events plus every new reservation/outcome/unknown; no other child start merely to correct stale admission metadata.

Phase1 preflight freezes profile.environments provider namespaces/per-mode probes, cloud-entry-context/v1, cloud-restored-operation/v1, cloud-live-recovery/v1, cloud-entrypoint-preparation/v1 and cloud-entry-inputs/v1. NEW tests first cover every journal state, missing/corrupt/conflicting restore, unknown-before-profile precedence, CLI401 with qualified native, global inventory unknown, mode-only invalidation, request/deep-copy mutation, exact accepted argv/no trim, namespace mismatch, concrete --inputs loading/digests and final callback freshness. Add public read-only snapshot wrapper to each existing transport's locked validator; no alternate journal/executor. Field mapping table binds every request value before route/submit.

Phase2 freezes explicit compute-cost-context/v2 and backend-provider-bindings/v1, typed provider_action/exception and cost_router.assess_provider_action. Test v1 readability, absent/expired/future/wrong action/provider/config/policy/request/budget exceptions, every costly branch and separate control-host consumption. Bind predicates into existing route/channel supervisor and ORIGINAL effect callback. Missing CLI/transient failure/outage alone cannot start Codespace. No live Codespace trial.

Phase3 implements explicit recovery-observation-history/v1 append-only project CAS events, v2 select history/new_signal contract and pure action_plan mapping. NEW fixtures perform two independently loaded fresh contexts against the SAME persisted history: second reuses verified evidence, skips present dependencies and cannot repeat identical diagnostics/install/unknown investigation. Unknown interrupted attempts only reconcile. Genuine changed efficacy input/completed correction enables only its bounded retry. Caller persists real pre/post event through existing owner/intent/budget gates; selector remains authority-free. Do not test by overwriting history or restamping time.

Phase4 aligns actual runnable prepare --profile/--inputs invocation in candidate SKILL, project AGENTS and watchdog, including actual verified consumer vendor_root, typed one next_action and parameter loader. No copied credentials or private HTTP. Shared-interface preflight matrix in spec is a checklist with actual test-command/exit/input hashes before phase5; if an interface changes, update spec/plan and affected evidence first.

## Phase5a — candidate-bound isolated new-chat behavior and measurements

After the aggregate candidate is frozen and cheap layout/interface preflight passes, Root reserves/admit one bounded independent fresh-chat actor under SAME ledger/task/default caps and genuine queued→running CAS; no nested Cloud, CI, Codespace or paid environment start. Provide only actual frozen startup surfaces/profile/inputs and isolated durable fixture history, not previous chats or expected commands. A new context must choose the concrete documented invocation itself. Actor may read-only execute approved native checks in THIS connected Cloud environment through normal scope; no product source/scheduler effects. Any unavailable actor capacity is a release acceptance blocker, not fabricated behavior evidence.

Run cold ready-native/CLI401 scenario and independently loaded warm active/unknown/verified-recipe scenario with existing bounded transport fixtures explicitly labeled simulated provider data. Preserve actual actor dispatch/terminal identity, full instruction/tool/action transcript and exact startup/profile/history hashes. Actual first useful cold action is approved native check argv/exit; warm is same-key observe/reconcile, never another send. Present dependency skip and no repeated investigation are observed, not asserted from template strings.

Use an operational standard-library trace recorder OUTSIDE the core (source included in targeted independent review before execution), initialized before scenario. It records real UTC and monotonic start/first-action times and all exploratory-probe/paid-environment-start events from the bounded actor trace. No recording helper may execute starts or infer zero from incomplete trace. Produce candidate-cloud-start-metrics/v1 exact schema in spec for cold/warm; actual consumption/prices/quota unavailable remain null. Counts and elapsed are actual observed values with declared method/simulated fields, no predicted latency/speedup claim. If code/instructions/fixtures change, identify affected dependencies and rebind/repeat only that scenario.

The final A1-A12 matrix points to actual unit/fault/actor/metrics receipts from the spec's explicit coverage table. Independent final Root SPEC and distinct QUALITY inspect transcripts and cold/warm measurements in addition to whole delta; clean consumer tests alone never satisfy A12. Exact final frozen-candidate package/FULL/CI still required. The actor observation does not prove live adoption/model behavior in unrelated consumers.
