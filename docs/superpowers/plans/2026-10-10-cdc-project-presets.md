# CDC Project Presets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans
> to implement this plan task-by-task. Root is the inline implementer/integrator;
> independent reviewers cover the frozen whole branch.

**Goal:** Generate validated project initialization and conservative migration
previews through `cdc init` and `cdc migrate`, without granting write authority.

**Architecture:** Compose existing strict adapters, checkpoint validation,
policy_migration and codex_cloud_profile in one source-only project_setup module.
The existing cdc entry dispatches strict JSON requests. Existing managed writers
remain the application boundary; all planner authority flags remain false.

**Tech Stack:** Python 3.12, existing PyYAML, unittest, immutable CDC 3.0.0 driver.

**Spec:** ../specs/2026-10-10-cdc-project-presets-design.md

## Global Constraints

- Source base 6a7bebaf342f70fef058f63d24febb337a741cb0; minimum runtime 2.11.3.
- Presets: portable MEDIUM/any, windows MEDIUM/windows, android MEDIUM/android,
  critical FULL/any; explicit full/release command strings remain unexecuted data.
- Core FULL; preserve budgets, guards, pauses, exceptions, task and release history.
- No product/Fleet/lease/scheduler/Cloud writes; one aggregate check per environment.
- Russian owner messages, English source docs, measured rounded-minute suffixes.

## Review Focus

- YAML/JSON aliases, duplicate keys and wrong types fail before generating artifacts.
- An absent quality block cannot accidentally reduce existing legacy FULL gates.
- A stored external operation survives probe drift and blocks policy artifact output.
- Existing Windows/Android platform gates cannot be relaxed by a portable preset.
- Cloud reuse with changed policy preserves original bytes and requires requalification.

### Task 1: typed initialization and preset projection

**Files:** create scripts/project_setup.py, tests/test_project_setup.py inside
src/continuous-development-cycle; modify scripts/cdc.py and tests/test_cdc_entrypoint.py.

**Interfaces:** produces initialize(request: dict) -> cdc-project-plan/v1; fixed
files docs/development-cycle.yaml, docs/work-status/current.md,
docs/cdc-cloud-profile.json and docs/cdc-cloud-entry-inputs.json.

- [ ] Write behavioral tests: test_each_preset_validates, test_init_recovery_has_no_authority,
  test_literal_commands_never_execute, test_init_rejects_bad_identity_or_commands,
  test_cloud_reuse_preserves_bytes_and_rejects_other_project.
- [ ] Observe RED against absent initialization, retaining exact command/output.
- [ ] Implement initialize and shared strict parsers/rendered-file hashing; reuse templates.
- [ ] Add strict CLI init dispatch and duplicate-key regression; observe targeted GREEN.
- [ ] Commit isolated source slice; record command/test count and no external effects.

### Task 2: conservative migration preview

**Files:** same project_setup.py and test_project_setup.py; CLI migrate dispatch
and focused entrypoint regressions; references/project-setup.md, phase-routing.md.

**Interfaces:** consumes existing valid adapter/checkpoint/profile text and fresh
probe; produces migrate(request: dict, *, now_utc=None) -> cdc-project-plan/v1.

- [ ] Write tests: test_migration_preserves_controls_body_and_history,
  test_missing_quality_stays_full, test_platform_cannot_downgrade,
  test_drift_and_stale_probe_have_no_files, test_external_or_guard_wait_preserves_identity,
  test_noop_is_byte_exact, test_changed_revision_rebind_then_noop,
  test_cloud_policy_change_requires_requalification, test_nondecimal_revision_requires_choice.
- [ ] Observe meaningful RED for the absent behaviors before code changes.
- [ ] Compose policy_migration.plan, existing strict validators and conservative projections.
  Rebind only revision/digest; reject conflicting platform; enforce fresh runtime probe.
- [ ] Observe focused GREEN plus existing cdc/profile/policy/checkpoint regressions.
- [ ] Document exact JSON schemas and output interpretation; commit source slice.

### Task 3: freeze, independent review and release qualification

**Files:** package metadata, release candidate/source binding, current AGENTS/roadmap
status and existing checkpoint/evidence surfaces; no new accounting controller.

- [ ] Root requirements review the exact diff against the spec; independently review quality.
- [ ] Freeze a 3.1.0 candidate under immutable independently verified 3.0.0.
- [ ] Run repository layout, package metadata, bootstrap and focused binding checks first.
- [ ] Run one clean-consumer FULL and independent bootstrap; qualify three archived copies
  without changing original archive controls; retain actual command exits/counts/log hashes.
- [ ] Reserve one required exact-candidate CI before its existing PR/dispatch trigger.
- [ ] Use genuine managed start/observe/finish for expected-head source publication;
  verify immutable receipt, supervisor quiescence, pool acceptance and final gate.
- [ ] Publish immutable release evidence; separately save/read back actual personal package.
- [ ] Physically close controller and all workers; retain history/unknown charges and Fleet pause.

Ruling: this slice deliberately supplies plans to the existing managed writer rather
than adding direct apply effects. The owner-approved 3.3 release/adopt automation
remains separate; a planner's APPLY action is readiness data, never write permission.
