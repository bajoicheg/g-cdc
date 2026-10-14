# CDC Admission Performance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Install qualified budget replay and authenticated-history improvements,
then measure actual useful-work admission and completion on the VPS.

**Architecture:** Keep the native budget/lease/pool/intent mechanisms. Optimize
private scratch replay first; reuse only authenticated immutable history in a
second release with fresh channel/head checks. Controller bindings and actual
host adoption are separate qualified steps.

**Tech Stack:** Python 3.12, native Git CAS, GitHub-hosted Linux CI, systemd.

**Spec:** ../specs/2026-10-14-sdk-admission-performance.md

## Global Constraints

- Preserve current task identities, charges, UNKNOWN history and replay bans.
- Preserve old immutable SDK trees and separate controller/Host Bridge instances.
- Ordered independent SPEC then QUALITY and one exact hosted FULL per release.
- No local FULL; portable regressions are hosted; real host gates stay on VPS.
- No source/config adoption while original native work is active or unknown.
- No cached ready flag or serialized value becomes execution authority.

## Review Focus

- A rejected replay must leave the caller's original ledger byte-equivalent.
- Public append results must isolate nested prior events from caller mutation.
- A cached head must not hide merged, truncated or changed/restored ancestry.
- Different endpoints/refs/instances and concurrent readers must not share authority.
- Cold restart must rebuild cache and preserve original native ownership/charges.

---

### Task 1: Budget replay release and adoption

**Files:** `scripts/budget.py`, `tests/test_budget.py` inside the SDK package;
release locks/projections and existing hosted qualification workflow. Private
delivery tools bind exact source/review/CI/object hashes and native effects.

**Interfaces:** Existing `validate_ledger(ledger)`, `apply_event(ledger,event)`
and `decide(ledger,event)` keep their public behavior and isolation contracts.

- [ ] Add a large real-ledger replay work regression and caller-isolation cases.
- [ ] Obtain hosted RED, then optimize only the scratch replay path.
- [ ] Run focused hosted GREEN and cheap bootstrap/package closure.
- [ ] Freeze/review SDK and delivery tools; publish through native ownership.
- [ ] Observe one exact receiving FULL; create immutable 3.6.5 release/install.
- [ ] Qualify compatible controller binding, stopped-unit upgrade and readbacks.

### Task 2: Authenticated-history reuse release and adoption

**Files:** SDK native history/store implementation and real bare-Git regression
tests; compatible controller runtime binding and protected release manifests.

**Interfaces:** Existing native history consumers receive the same detached
historical values; fresh channel/head/ancestry checks precede any reuse.

- [ ] Reproduce repeated immutable object reads with real bare-Git histories.
- [ ] Add changed/restored, merge, shallow, rewind, endpoint and mutation tests.
- [ ] Implement bounded process-local immutable reuse; keep native gates intact.
- [ ] Freeze/review, hosted FULL, immutable release and quiescent adoption.

### Task 3: Useful-work stability and durable completion

**Files:** Private workload contracts, original native budget/control evidence
and bounded phase-timing report; no product implementation writes.

- [ ] Reconcile all original rows and register new bounded COMPUTE_ONLY work.
- [ ] Run useful fixed checks through both eligible executor identities.
- [ ] Verify actual results, terminal proofs, queue ACK, process closure and charges.
- [ ] Measure cold/warm admission and bounded repeated workload; report limits.
- [ ] Verify current source/config recovery coverage and durable cloud evidence.
