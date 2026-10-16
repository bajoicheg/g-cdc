# Phase1 forward SDK integration plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. The owner has already requested continued execution; do not ask for routine intermediate confirmation.

**Goal:** Prepare a forward release candidate that combines the qualified3.6.8 native runtime with the qualified Phase1 provider adapters, without dropping later recovery or history fixes.

**Architecture:** Start from the frozen Phase1 source and import only the canonical released3.6.8 package bytes. Preserve all four agent modules, role profiles and their tests exactly. Combine package inventory requirements, update release metadata to3.6.9 and validate the resulting composition before any native Source publication or deployment.

**Tech Stack:** Existing Python CDC SDK, Git object pins, independent bootstrap and GitHub-hosted qualification.

**Spec:** `docs/superpowers/specs/2026-10-15-multiprovider-foundation.md`; this plan only prepares its safe release integration after live Codex+Kimi acceptance.

## Global constraints

- Preserve original native authority, leases, one-use launch CAS, budgets, charges and UNKNOWN replay exclusions.
- Released SDK baseline: source54241b599f39907012425275474f687ab8eb75ca, packagee68078eef63f53aedbcb246ca9a6310863d8fb6c, independent FULL38589277797.
- Phase1 source:cc26a6f7f632f4628c9bcc516c9714abccddfbc2. Its earlier FULL and live acceptance qualify those bytes and do not qualify the new composition automatically.
- Preserve existing public PR source until a newly admitted Source operation owns any advance. No direct main push, historical attempt replay or old budget reuse.
- Keep portable checks hosted. Use meaningful bounded checks before one exact frozen canonical FULL. No repeated FULL for unchanged source.
- Installed production, account sessions, registered task schemas, limits and project routes remain outside this preparation.

## Review focus

- Older native code must not replace authenticated history reuse or original preconsume/consumption recovery.
- All Phase1 provider modules, role policies and strict parsers must remain byte-identical to their accepted source.
- Package validation must require both native recovery and new agent assets.
- Source lock must identify the actually released development driver; candidate/package/three projection bindings must agree.
- Passing candidate tests does not authorize a Root policy change, task replay, merge or production deployment.

### Task1: Prepare the exact forward package

**Files:** `src/continuous-development-cycle/**`, `VERSION`, `release/source.lock.json`, `compatibility/matrix.json`, `AGENTS.md`.

**Interfaces:** Consumes the two immutable source/package pins above. Produces a combined3.6.9 candidate with original native code and exact agent modules.

- [ ] Verify both source refs, package trees and existing successful hosted receipts.
- [ ] Compare tracked package objects; record every changed/imported path in the private audit.
- [ ] Copy qualified native package bytes while preserving Phase1-only assets; combine `validate_package.py` inventory requirements.
- [ ] Update version/driver metadata and retain the independently qualified3.6.8 driver evidence.
- [ ] Verify all non-metadata native scripts and all agent assets against their original Git blobs. Run only cheap layout/metadata checks locally.
- [ ] Commit the candidate and bind its exact package tree in candidate metadata and the three supported projections.

### Task2: Hosted composition qualification

**Files:** Private operations checkpoint/workflow and receipts; `release/candidate.json`; `consumer/supported/fleet-{1,2,3}/source.json`.

**Interfaces:** Consumes Task1's exact candidate SHA. Produces independent targeted CI and ordered SPEC/QUALITY evidence for that exact source.

- [ ] Publish a labelled private checkpoint using a temporary index, expected-head checks and cloud readback; preserve all active worktrees and exclude credentials/raw model sessions.
- [ ] Run the existing agent tests together with changed native budget/history/recovery tests on hosted Linux. Record actual counts, failures and skips.
- [ ] Resolve only composition failures with targeted evidence. Do not re-run the old real acceptance or reuse its namespace.
- [ ] Obtain ordered independent SPEC then distinct QUALITY review of the final source and exact publication tooling.
- [ ] Admit any public Source advance through its new original receiving event, budget, guard and one-use claim; observe one exact canonical FULL before finish.

### Task3: Concrete Root adoption preparation

**Files:** Separate private Root integration design, qualification/configuration and rollback artifacts; no installed policy writes in this task.

**Interfaces:** Consumes the qualified forward SDK and the actual Root launch/account/sandbox contracts. Produces a concrete reviewable adoption proposal and required checks.

- [ ] Map one existing native launch owner; never independently start both host bridge and AgentWorker for the same task.
- [ ] Preserve registered legacy tasks and actual current attempts. Define any new explicit provider contract/configuration without mutating old schemas in place.
- [ ] Prepare and qualify the smallest compatible host integration in isolation with original native budgets/custody and hosted portable checks.
- [ ] Publish source and non-secret recovery evidence privately before requesting the concrete security-sensitive production adoption approval required by repository policy.
- [ ] While any approval is pending, continue independent qualification/documentation that does not depend on it.
