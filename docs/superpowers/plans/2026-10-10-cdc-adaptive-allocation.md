# CDC Adaptive Allocation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Release CDC 3.2.0 with measured, conservative effort and agent allocation.

**Architecture:** One pure layer composes existing strategy, quality, budget and operation measurements. The root implements inline; independent reviewers have no write or publication authority.

**Tech Stack:** Python standard library, unittest, Git, existing CDC bootstrap.

**Spec:** `docs/superpowers/specs/2026-10-10-cdc-adaptive-allocation-design.md`

## Global Constraints

- Driver: independently released and personally accepted CDC 3.1.0, canonical commit f5a704a93abdf0a36d0cb7a312a742f862af4946.
- Minimum supported CDC: 2.11.3. Existing ownership, budget, final platform and one-use submission contracts remain authoritative.
- Fleet rollout and schedulers remain paused. Every authorization result is false.
- Only measured compatible observations may affect allocation; unknown values stay unknown.

## Review Focus

- Comparable windows: reject mismatched groups and duplicate observation identities.
- Sparse or unknown evidence: select the safe default without claiming savings.
- Quality regression: exclude observed escaped defects and enforce the FULL effort floor.
- Active or exhausted budget: preserve WAIT or SINGLE and never consume the ledger.
- Invalid numeric/enumeration inputs: reject booleans, nonfinite values and unknown profiles.

### Task 1: Measured allocator and CLI

**Files:** Create `scripts/adaptive_allocation.py`, `tests/test_adaptive_allocation.py` in the source package.

**Interfaces:** Consumes `execution_strategy.evaluate(dict)` and `operation_report.measure(dict)`; produces `evaluate(request: dict) -> dict`, `main(argv=None) -> int`.

- [ ] Write tests with existing strategy fixtures; measured inline profile wins over a more costly parallel profile after two samples; no observations retains the default.
- [ ] Run `python3 -B -m unittest discover -s src/continuous-development-cycle/tests -p test_adaptive_allocation.py -v`; observe the missing allocator failure.
- [ ] Implement exact fields, profile and observation validation, safe floor, measured ranking, existing strategy composition and JSON CLI.
- [ ] Add and run the review-focus cases above plus tie stability, scope conflict, replay and immutable inputs. All must pass.
- [ ] Commit the independently testable allocator.

### Task 2: Package, release and personal acceptance

**Files:** Create `templates/adaptive-allocation.json`, `references/adaptive-allocation.md`; modify package manifest/SKILL/phase-routing, VERSION, release locks, compatibility matrix, current roadmap and AGENTS entry.

**Interfaces:** Consume the allocator API; produce complete CDC 3.2 package and exact candidate bindings.

- [ ] Register a runnable safe-default template and explain authenticated comparable evidence and unchanged launch/platform boundaries.
- [ ] Bump target to 3.2.0 and driver to 3.1.0; retain all historical compatibility and unchanged archived consumers.
- [ ] Commit and bind the exact package tree; freeze the candidate.
- [ ] Run required bootstrap/package/FULL/clean-consumer checks once; preserve raw logs, original SHA and dependency bindings.
- [ ] Obtain independent SPEC_GREEN, then a different QUALITY_GREEN; fix observed findings before required revalidation.
- [ ] Use the existing managed native control host to publish a draft PR, inspect mandatory exact-tree CI, conditionally publish main and immutable release/evidence.
- [ ] Adopt the complete released package into the personal skill; read back all package files and immutable archive identity.
- [ ] Verify managed release receipt, accepted pool, supervisor/worker/controller quiescence and actual Cloud terminal state; record stage completion before 3.3.
