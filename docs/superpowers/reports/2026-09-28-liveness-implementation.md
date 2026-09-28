# CDC 2.11.1 Task 1 implementation

Isolated branch: `work/liveness-2111`, base `03562f6`. Development authority remains
released CDC 2.11.0. This slice changes no version/release metadata, live target
resolver, roadmap, SKILL, remote refs, or live automation.

## Implemented boundary

- `watchdog_liveness.py`: versioned independent fresh signals, exact project/ref/
  watchdog/incident identity, explicit owner pause precedence, CRITICAL disabled/
  overdue/premature completion, exact Git-revision terminal proof, owner policy and
  safety gates. The legacy `watchdog_health` reader remains compatible and dispatches
  explicitly versioned new probes to this contract.
- `fleet_watchdog_runtime.py`: executable supplied adapter effects, all-project
  assessments, durable continuation and fixed per-invocation effect/deadline budgets,
  unique CAS claims before enable/run, post-claim checks, exact readback, and
  no replay after crashes or unknown results. Accepted run receipts retain exact
  provider invocation IDs until fresh completed evidence matches that exact ID.
  Renamed incidents, changed refs, idle visibility, and another completed invocation
  cannot bypass an outstanding watchdog operation.
- `git_document_store.py`: explicit fetch/push endpoint identity, dedicated
  `refs/heads/cdc/...` document-only tree, portable protected-ref isolation, fresh
  pinned reads, random proposal nonce, non-force CAS and exact readback. It rejects
  shared trees instead of erasing other root files.
- New reference `references/watchdog-liveness-runtime.md` and safe inactive probe
  template. No fictitious host API or platform final-channel interception is claimed.

## Retained RED and GREEN evidence

The `liveness-2111-evidence/` directory retains actual command output:

- Initial RED: 8 contract failures and 18 runtime failures on the absent feature.
- Additional RED: completion checkpoint loss exceeding a wake budget; stale or
  wrong-ID readback; post-claim invocation change; unknown continuation lost under
  zero budget; absent wrapper dispatch; same-invocation budget reset/increase;
  missing wake deadline API; missing exact terminal/owner policy gates; accepted
  run receipts incorrectly treated as terminal. Missing API/recognized-state cases
  initially produced expected TypeError/ValueError outcomes, not syntax failures.
- Final `test_fleet_watchdog_runtime.py`: **33 tests passed**, including real local
  Git contention under a fixed commit clock, actual child-process exit immediately
  after a committed claim and fresh-process restart, instrumented scheduler state
  mutation/receipt files, executable CLI, all-project budgeting, deadline handling,
  owner/pause/guard checks, and accepted-invocation lifecycle regressions.
- Final `test_watchdog*.py`: **25 tests passed** (10 new contract tests and 15 retained
  health/self-repair tests). New contract standalone run also passed all 10.
- New probe CLI executed successfully with `CRITICAL`, `recovery_eligible: false`,
  and `authorizes_scheduler_mutation: false` for its deliberately inactive template.
- `git diff --check` passed. No package bytecode artifacts were found.

Focused commands used `PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover`
with `-s src/continuous-development-cycle/tests` and the relevant test patterns.
The parent explicitly reserved the final integrated full suite/bootstrap/consumer
gates to avoid interference from parallel existing process-supervision tests.
This worker did not run those final integration/release gates and makes no claim
about their result.

## Integration notes and limits

Public API: `FleetRuntime(store, backend).run_batch(projects, max_effects=...,
invocation_id=..., deadline_utc=...)`; project identities omit incident, while fresh
backend observations include the durable incident. CLI accepts a JSON configuration
and an explicitly supplied `--backend module:factory`. There is no default provider
or live scheduler adapter. Successful starts remain in `pending` for exact-invocation
monitoring; the result's `continuation_required` is therefore not a duplicate-start
authorization. The parent should include new scripts/reference/template/tests in
its package validation and release manifest updates.

Actual test effects were local scheduler changes and receipt files; all Git writes
were ephemeral local test remotes or this isolated worktree commit. **Zero live
automation mutations and zero remote repository writes.**

The runtime is cooperative. Supplied adapters must verify authoritative evidence,
enforce bounded IO, and debit their provider budget. Git claims and a separate
scheduler cannot make pause and mutation atomically indivisible; stronger host
conditional effects require a real supporting adapter. Unknown submissions remain
blocked until independently verified, authorized reconciliation; the runtime never
uses TTL or an incident rename to release them. The 4 MiB store limit fails closed
and requires separately authorized retention when exhausted. No unresolved failing
focused test is known at handoff.
