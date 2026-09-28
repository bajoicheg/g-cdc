# Managed execution after continuity recovery

## Authorized intent

On 2026-09-28 the owner approved the backlog analysis and its proposed execution order, with this foreground chat managing the work. Deliver real continuous execution and recovery, then scale concurrency. Do not restart the owner's paused schedulers. Previously authorized implementation, review, Git integration, release and personal-skill activation remain authorized; routine engineering decisions do not require repeated approvals.

## Stages

1. Verify the actually loaded 2.10.3 package and real multi-step execution; inventory consumers and migrate only at proven safe boundaries.
2. Release 2.11.0 under 2.10.3: forward-port the preserved executor pool, close final3's three remote-identity findings, and connect durable launch claims to real worker execution and parent terminal decisions.
3. Release 2.11.1 under released 2.11.0: persistent watchdog/Fleet recovery, exact live target resolution, explicit owner-pause precedence and idempotent authorized effects.
4. Release 2.11.2 under released 2.11.1: independent foreground/watchdog execution lanes, portable write-conflict exclusion and one shared integrator.

The last two stages intentionally reverse the old roadmap order. Their written implementation plans are completed at their stage boundary, under the released predecessor. Preserve archive/history and consolidate obsolete future entries into implemented history with open defects separately tracked.

## 2.11.0 design

Reuse the frozen pool source d7156fecca13ee9989c5241ee8fc834ba88e7d7d and its historical evidence as source history, not acceptance of this new package. Preserve all 2.10.3 continuity fixes, positive terminal paths, source-binding tests and release evidence.

Separate remote identity into a single Git-aware helper. Resolve repository roots through Git, preserve SCP home-relative versus absolute semantics and SSH usernames, honor effective Git remote URL resolution, and do not disclose credentials in identifiers or errors. Coordination and publication use the same endpoint identity contract.

Add an execution adapter above the existing pool/store/attempt contracts. A durable queue reservation is not a start; only a successful one-shot launch CAS may cause the real backend effect. The adapter starts actual bounded workers, observes results, preserves failed/unknown attempts, and never retries an uncertain start blindly. Provide a real local-command backend using argument arrays, isolated Git worktrees and subprocesses; expose a narrow start/observe/cancel interface for host tool backends without claiming native Work/Codex capabilities that are unavailable.

A successful process is not an integrated result. Validate worker identity, exact Git base, output commit, full-history write claims, required evidence and publication, then route to the sole integrator. Parent terminal evaluation additionally consumes fresh pool state: planned/runnable/queued/running/recoverable required tasks and successful unintegrated results block completion. Failure of one worker leaves independent work runnable. Runtime-budget exhaustion leaves durable continuation, not project COMPLETE.

Verify active installation from files actually read. Canonical Git vendoring requires exact tree identity. Personal skill storage may normalize only recorded metadata; instructions, scripts, references, tests, manifest and version must remain byte-identical, interface YAML must remain semantically equal, and icon/mode normalization must be explicit evidence. A cached skill catalog is not an installation witness.

## Acceptance

- All three final3 identity defects have tests observed RED on preserved code and GREEN after correction.
- Real independent workers overlap on a parallel backend; the same required tasks execute sequentially when configured concurrency is one.
- Duplicate launch, stale CAS and crash/unknown-start reconciliation cannot create a second worker.
- Failure/cancellation/timeout preserve attempts and leave unrelated work eligible; required unintegrated results prevent parent finalization.
- Real Git publication/integration and exact package readback produce evidence outside synthetic event strings.
- Existing 2.10.3 recovery regressions remain GREEN; a multi-step agent smoke completes its entire assigned scope without a milestone final response.
- Bootstrap, package, fault/recovery cases, independent reviews and three-consumer compatibility pass for the frozen new package; CI validates the exact integration head. Consumer compatibility is not advertised as live adoption.

## Boundaries

Validators remain cooperative controls; they cannot intercept ChatGPT's final-response channel. Provider-specific tools remain host capabilities. Do not fabricate launches, external observations, model quotas or liveness. No blanket parallel benchmark reruns when the unchanged package/plan evidence already answers the release question.
