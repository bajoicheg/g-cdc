# CDC Parallel Maintenance Implementation Plan

> **For agentic workers:** Use superpowers:dispatching-parallel-agents for independent tasks. Steps use checkbox syntax. Owner selected parallel execution and authorized implementation on 2026-10-07.

**Goal:** Make useful parallel CDC work the documented operating default and correct two known maintenance defects.

**Architecture:** Reuse existing durable pool/CAS and budget controls. Two isolated writers return scoped commits; root integrates them while a read-only analyst verifies status and missing guidance. Ordered reviewers examine the frozen aggregate.

**Tech Stack:** Python 3, unittest, Git worktrees, GitHub refs, native Work agents.

**Spec:** `docs/superpowers/specs/2026-10-07-parallel-maintenance-design.md`.

## Global Constraints

- Develop candidate 2.12.1 under immutable released 2.12.0; never edit released/installed runtime bytes.
- Existing project start/slot budgets remain binding; unavailable token/cost measurements are null.
- Root alone integrates; children have no shared-source/release/Fleet authority.
- Preserve FULL, required platform gates, legacy behavior, paused schedulers and separate GAD ownership.

## Review Focus

- Empty and whitespace argv elements remain exact strings: argv worker regression.
- Nonstring argv elements and an empty list still fail: argv worker regression.
- Changed whitespace/order invalidates evidence reuse: argv worker regression.
- Transport labels resolve to actual VERSION bytes and a reconstructed tree: transport worker regression.
- Optional analysts never bypass existing caps; required final CI and historical fixtures remain: independent aggregate review.

### Task 1: argv writer

**Files:** `src/continuous-development-cycle/scripts/evidence_reuse.py`, `src/continuous-development-cycle/tests/test_evidence_reuse.py`.

**Interface:** existing `evaluate(data: dict) -> dict`; string contents preserved verbatim.

- [x] Write and observe failing empty/whitespace reuse regressions.
- [x] Replace item nonblank validation with string-type validation.
- [x] Run evidence-reuse/gate/quality regressions and return scoped commit.

### Task 2: transport writer, independent of Task 1

**Files:** `src/continuous-development-cycle/templates/package-transport.json`, `src/continuous-development-cycle/tests/test_package_transport.py`.

**Interface:** existing `verify_directory(manifest, root)`; version-derived fixture verifies content/tree binding.

- [x] Observe failing real-byte verification of declared VERSION.
- [x] Correct illustrative blob/tree fingerprints and run transport regressions.
- [x] Return scoped commit; integrator updates version-derived example at candidate preparation.

### Task 3: analyst and integrator

**Files:** `AGENTS.md`, `docs/roadmap.md`, runtime `SKILL.md` and `references/runtime-routing-and-subagents.md`; candidate version/source-lock/compatibility/archived consumer bindings; `docs/execution/cdc-parallel-maintenance-20261007.json`.

- [x] Audit existing machinery and recorded release/status without duplicating subsystems.
- [x] Integrate both exact-base commits after changed-history containment checks.
- [x] Persist the operating recipe, candidate admission and factual status reconciliation.
- [ ] Freeze candidate; run bootstrap, package, clean consumer FULL and three archived consumer checks.
- [ ] Obtain independent ordered spec then code-quality review.
- [ ] Publish the isolated candidate, obtain required CI and record exact checkout provenance.
- [ ] Retain the concrete candidate and evidence for normal source-release acceptance; never infer installation/adoption.
