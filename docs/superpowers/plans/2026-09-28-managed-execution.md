# Managed Execution Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans for parent integration and isolated workers for independent implementation. User explicitly approved execution of this proposal; continue across tasks and releases.

**Goal:** release a working managed executor pool on the corrected continuity foundation.

**Architecture:** preserve 2.10.3, forward-port the four existing pool modules, share Git endpoint identity, add a real execution adapter and active-package verification, then validate and release the frozen package.

**Tech Stack:** Python stdlib, unittest, PyYAML, Git, GitHub connector/Actions.

**Spec:** docs/superpowers/specs/2026-09-28-managed-execution-design.md

## Global Constraints
- Only the parent writes shared refs and releases; workers use isolated worktrees.
- Schedulers remain explicitly owner-paused.
- Preserve 2.10.3 continuity and source-binding tests and immutable prior evidence.
- Real backend effects require durable launch CAS; unknown starts never justify replay.
- Existing authorization governs execution and review; no routine approval loops.

## Review Focus
- SCP/SSH/local remote identity differences, Git subdirectory invocation and rewritten URLs.
- Crash between launch claim, actual process start and persisted receipt; uncertain outcomes must fail closed.
- Timeout/cancellation while a process or descendant can still write.
- Parent completion while required workers or unpublished/unintegrated results remain.
- Cached skill metadata or harmless host normalization concealing changed runtime instructions.

### Task 1: Preserve source and close endpoint identity findings
**Files:** managed_executor_{pool,attempt,handoff,store}.py, shared git_remote_identity.py, managed tests/templates/reference under src/continuous-development-cycle.
**Interfaces:** consumes preserved source; produces coordination_store_id_for_endpoint(value, repo_root=None) and publication_remote_identity(root, remote) with one shared canonicalization implementation.
- [ ] Import additions from frozen 2.11.0 without replacing corrected continuity files.
- [ ] Add three real-Git identity regressions; run focused identity tests. Expected: RED on preserved source.
- [ ] Correct shared endpoint resolution; run all managed tests. Expected: GREEN with distinct destinations never aliased.
- [ ] Commit bounded correction and record RED/GREEN evidence.

### Task 2: Execute managed work and enforce parent closure
**Files:** scripts/managed_executor_runtime.py, tests/test_managed_executor_runtime.py, references/managed-executor-runtime.md.
**Interfaces:** consumes real GitManagedExecutorStore and one-shot pool claims; produces documented start/observe/cancel adapter and parent terminal evaluation combining pool and existing execution_continuity evidence.
- [ ] Write real subprocess/Git tests for parallel overlap, sequential fallback, failure isolation, duplicate/unknown starts, timeout and unintegrated parent rejection. Expected: RED before runtime exists.
- [ ] Implement minimal runtime/backend and durable receipts with exact task/attempt/claim binding.
- [ ] Run runtime and full package tests; retain observed process/result evidence. Expected: GREEN.
- [ ] Commit adapter and integration guidance.

### Task 3: Verify actual package loading and operational continuity
**Files:** scripts/active_package.py, tests/test_active_package.py, release/active-package-acceptance-2.11.0.json; consumer records under release/ as appropriate.
**Interfaces:** consumes canonical directory and installed directory; produces explicit byte/semantic/mode comparison and active version evidence without conflating canonical and host-normalized trees.
- [ ] Test changed SKILL/script rejection, version mismatch, unexpected files and narrow documented host normalization. Expected: RED without verifier.
- [ ] Implement verifier and run it against saved 2.10.3 then the released 2.11.0 installation. Expected: exact runtime content PASS, explicit metadata normalization only.
- [ ] Run real multi-task agent/backend acceptance; discover live consumer refs/ownership and migrate at safe boundaries. Unknown ownership is a per-consumer blocker, not a reason to stop unrelated core work.
- [ ] Commit evidence and preserve one actionable state per consumer.

### Task 4: Freeze, review, release and continue
**Files:** VERSION, manifest/SKILL/agent metadata, bootstrap release bindings, release/source.lock.json, release/candidate.json, compatibility/matrix.json, consumer snapshots, roadmap and evidence.
**Interfaces:** prior driver 2.10.3 at 685d35cac8316c303fc466345a18ed8abf9fb256 / a1fdca8c4a00409069b790e6dd13944e64fbf9bd; target 2.11.0.
- [ ] Refresh source lock and exact package bindings; preserve old evidence.
- [ ] Run bootstrap/package/three snapshot checks, independent spec and quality review; fix material findings with RED/GREEN regressions.
- [ ] Freeze source, publish exact-head PR, observe Actions to success and merge/release. Expected: release ref and remote readback bind validated package.
- [ ] Activate installed skill, reconcile readback, consolidate legacy backlog, then begin the authorized 2.11.1 stage; this release is not the parent task's terminal boundary.

## Execution ledger

Ruling: architectural scope and release order are already approved by the owner; write reviewable design/plan and execute without another conversational approval boundary. Cost if wrong: bounded engineering choices require correction; no scheduler authority is inferred.

Pre-flight: Task 1 identity API is consumed by publication and runtime; Task 2 uses existing pool/store contracts rather than replacing their authority model; Task 3 distinguishes host normalization from canonical tree identity; Task 4 records a frozen source before expensive evidence.
