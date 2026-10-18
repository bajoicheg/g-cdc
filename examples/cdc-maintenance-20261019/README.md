# Maintenance repair continuation — PREQUALIFICATION — 2026-10-19

This isolated standard-library Python kit is **unqualified and inactive**. It does
not repair the installed runtime or close the original task. No provider, model,
CI, installation, scheduler, or live process operation was executed to build it.
The fixed controller entrypoint owns checks, freeze/commit, and subsequent reviews.

## Artifacts and trusted boundary

`maintenance.py` provides callable candidates with no import-time effects:

* `signal_owned`: pidfd pin, birth recheck, same PID namespace and same UID checks,
  TERM/KILL only, explicit EPERM/absence/unknown outcomes. The caller must supply
  a **live supervisor-owned descendant**, never an arbitrary input PID. A sent
  signal is not closure. This reduces PID reuse risk without adding CAP_KILL.
* `Ledger`: durable SQLite aggregate reservation across threads per registered task,
  immutable original baseline/limits, one-use thread+turn, UNKNOWN charge retained
  after failure. `execute` reserves before native authorization and effect. The
  effect must consume the real native capability; adapters are trusted Python
  controller code. They cannot be sourced from untrusted JSON or user flags.
* `interrupt`: one exact reserved thread+turn attempt, durable intent before RPC,
  unsupported/owner-dialogue refusal. A crash before/after RPC leaves uncertain
  interruption spent. No fallback to stopping a thread/service, no automatic retry.
* `maintenance_step`: one scoped admitted operation followed by native verification;
  exceptions return UNKNOWN without granting closure/replay. No observer loop.
* `recovery_assessment`: bounded diagnostic containing a digest, not a native proof.
* `usage`: separate total/input/cached/uncached/output; reasoning is already output.

The SQLite database is additional local enforcement for **cooperating calls through
this wrapper only**. Place it in a dedicated controller-owned directory on durable
local disk, never a shared/untrusted path or network filesystem. Do not replace,
copy backward, delete, or reinitialize it to obtain allowance. Baselines must come
from authenticated original per-task aggregates; unknown baselines deny enrollment.
Use integer dimensions for calls, starts, time ceilings and token ceilings as
appropriate. A charge is a conservative reservation, not actual billing. All
status values, including RETURNED, remain charged. Observed usage never refunds.
If no genuine pre-effect turn hook exists, Desktop enforcement remains unavailable.
This code cannot intercept arbitrary existing Desktop turns or enforce a token
ceiling inside an already running turn. It claims no savings or exact billing.

## Runtime finding and proposed integration

Read-only inspected SDK3.6.8 `scripts/managed_executor_runtime.py`, `_supervise`
lines 324–332: `os.kill(current['signal_pid'], sig)` handles only ProcessLookupError.
EPERM therefore escapes the supervision loop. The provided crash is consistent
with that path. Root cause of permission denial itself is **not established**:
UID/namespace/LSM/seccomp/capability constraints need sanitized native observation.
Do not infer a permission fix from process absence.

Candidate integration into a separately reviewed runtime source (never this install):
replace only that signal operation with `signal_owned(target, identity['birth'],
sig, expected_uid=<frozen isolated worker uid>)`, using fresh descendants from the
live supervisor. Maintain the existing original waitpid loop and all proof logic.
Persist denied/unknown outcomes as nonterminal diagnostics before continuing the
live supervisor's bounded supervision. Do not label a denial success, change
`verify_terminal`, or emit `waitpid_ECHILD` unless the original wait actually returns
ECHILD. Avoid unbounded denied-signal retries: at the admitted deadline, retain the
supervisor/controller and existing lease in a blocked nonquiescent state pending
owner remediation. Any later retries need separately bounded native policy.
This module alone does not implement that live hold; activation requires the
runtime integration and hosted behavioral test of that boundary.

For cold-path execution the native `admit` adapter must validate registration,
expected source, claim/CAS, lease/one-use, original UNKNOWN gates, UID and dedicated
aggregate cgroup, deadline, account/quota and all budget dimensions **before any
operation**. Keep controller alive through start/observe/finish. `verify_and_record`
must retain actual stdout/stderr/exit and require birth-bound aggregate closure,
including detached descendants, native authentic terminal proof and readback.
An arbitrary callback return or diagnostic file cannot satisfy it. No new generic
native authority is implemented here.

No installed native postlaunch recovery endpoint was established: TaskStore
`complete_administrative` requires PrelaunchIntakeDispositionProof; `complete`
requires VerifiedTerminalProof. Both must remain unchanged. Recovery needs a
separately designed package-owned authenticated monotonic recovery capability,
binding original journal/request/launch, lease generation, aggregate closure and
new disposition. It must never mean success or authorize replay. Until then leave
the original task and receipt UNKNOWN/nonquiescent. Known PID absence is insufficient.
Use new recovery evidence files only; old receipt/journal/copies remain immutable.

## Exact portable qualification and activation

1. Fixed entrypoint records final kit tree/commit and `freeze.json` binding. No stage,
   commit, push or Git metadata writes by this worker. `result.json` describes the
   implementation, not a passing qualification. No RED/GREEN is claimed.
2. Controller schedules **one hosted compute start**, no CI start, frozen kit-only
   intent: `python3 -B -m unittest discover -s examples/cdc-maintenance-20261019 -p
   'test_maintenance.py' -v`, Linux Python 3.11+ with SQLite. This command has no
   provider effects and uses temporary hosted storage and fakes. Run the permitted
   diff check as fixed entrypoint policy requires. Capture separate stdout/stderr,
   true exit, source/kit digest and actual return; no local test execution on VPS.
3. Controller obtains independent SPEC, then distinct QUALITY against the same
   frozen tree. Worker used no agents. Budget total: compute 1, agent starts 3
   including implementation/SPEC/QUALITY, CI 0, calls 40, 900 seconds. Existing
   parent allocations remain unchanged. No automatic repeated qualification.
4. Native integration is a **separate activation gate**, not part of portable fake
   tests: qualify EPERM survivor/nonquiescence, namespace/UID mismatch, PID reuse,
   detached cgroup member, cold-path no-effect denial, durable crash at each charge/
   native grant/effect/RPC boundary, genuine account/quota denial, and historical
   UNKNOWN rejection. Establish the supported RPC schema and exact turn identity
   readback before enabling `turn/interrupt`; RPC transport alone is insufficient.
5. Owner authorizes a separately registered isolated activation only after native
   adapters and genuine managed expected-head release. Never resubmit the parent
   contract, original native submit or Kimi stage. Do not use the maintenance kit to
   take the infrastructure lease held by the original active handle.

The fixed entrypoint owns new final checks and commit after writer return.
Portable qualification has not run and is an explicit deployment blocker.
Native activation remains blocked by the missing integrations and physical closure
proof. External native acceptance cannot be conferred by any file in this kit.


## SPEC-001 repair: finite native interruption bridge

`Ledger.interrupt` accepts exactly `NativeInterruptRPC`, rather than an arbitrary
adapter callback. Its dedicated AF_UNIX stream is nonblocking. One monotonic
budget, explicitly configured in `(0, 5]` seconds, covers connection, partial send,
and bounded response read. Every readiness wait uses the remaining deadline;
there is no background worker, subprocess, reconnect, or retry. Socket closure
occurs on every return. This bounds transport waiting subject to ordinary host
scheduling, not a hard real-time execution guarantee. SQLite reservation may take
its existing finite lock timeout before RPC begins.

The trusted controller must pin a private, authenticated-by-local-permissions
native bridge endpoint in the same host monotonic clock domain. This is a new
explicit integration contract, not a claim that the existing WebSocket service
implements it. Request: one UTF-8 JSON line, at most 4096 bytes:
`{"method":"turn/interrupt","params":{"threadId":"<exact>","turnId":"<exact>"},"deadline_monotonic_ns":123}`.
The bridge must reject expired or unadmitted work before effect, never defer or
replay it, and preserve native provider/account/permission/quality gates. It must
independently verify that this is the admitted autonomous turn, not owner dialogue.
Only an exact JSON acknowledgement
`{"status":"acknowledged","threadId":"<exact>","turnId":"<exact>"}` is accepted.
The response cap is 4096 bytes. This acknowledgement never proves cancellation or
closure. Timeout, EOF, connection failure, malformed/oversized response, or wrong
identity returns explicit `uncertain`, with `replay_allowed:false`. The committed
stop row and original budget charge survive all such outcomes, including restart.
A timeout may follow a delivered effect; close does not retract the request.
Only native observation of the original turn can resolve that uncertainty.

Hosted tests now include a real unresponsive socketpair, EOF, identity mismatch,
finite configuration refusal, and durable no-replay/charge retention after reopen.
They use no threads, native service, GUI, or provider. Existing behavior tests are
retained; none were executed on this VPS. Native integration must additionally
qualify blocked connect/send/read, slow partial frames, bridge-side expiry,
permission denials, durable crash boundaries, and actual GUI owner/autonomous turn
identity and pre-effect hooks. Portable fakes cannot supply actual GUI coverage.

## Continuation provenance and evidence boundary

This is `cdc-maintenance-runtime-kit-fix-20261019`, linked to FAILED task
`cdc-maintenance-runtime-kit-20261019`, rejected candidate
`f50a68f9949cd7b4dbe256f087bb49f86eaa2b6f` (SPEC RED). All five source files were
copied only after verifying byte lengths and SHA-256 against its frozen
`candidate-evidence.json`. That external record preserves the original exit-0
`git diff --check`; it proves nothing about changed continuation code. No old
history, native UNKNOWN counters, terminal proof, or lease release is rewritten.
The new allowance is compute 1 / agent 3 / tools 40 / seconds 900 / CI 0; previous
allowances remain spent. No subagents were started by this writer.

The optional `/opt/cdc-tools/candidates/cdc-maintenance-runtime-kit-fix-evidence.json`
export was unavailable during writing. This is an evidence gap, not a failed check.
Reviewers must inspect this source and actual fixed-entrypoint final-check evidence
externally bound to the resulting candidate and frozen intent. No future commit
SHA or controller-receipt self-reference is embedded. Ordered native SPEC and
separate QUALITY own acceptance; future hosted portable qualification and genuine
native integration remain deployment blockers. The original crashed supervisor
cannot now supply its authentic waitpid_ECHILD; original UNKNOWN stays unresolved.
