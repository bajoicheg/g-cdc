# Reporting reference audit — #113

Audit date: 2026-10-22. This is a NEW registered g-cdc Source documentation
audit within the native examples/docs writer scope, not a replay of quickstart
or acceptance. Only this document is changed.

## Source evidence and boundary

The registered Source is `refs/heads/cdc/vps-development` at original HEAD
`9d09f6961af46bc8cb44ae5a8464b895d6106cbc`. Local `git rev-parse HEAD`
confirmed that exact commit. Local reads of `AGENTS.md`,
`src/continuous-development-cycle/SKILL.md`,
`src/continuous-development-cycle/VERSION`, `docs/development-cycle.yaml`
and the timestamp section of
`src/continuous-development-cycle/references/continuous-autonomy-and-learning.md`
provide the evidence below. Source VERSION is `3.5.4`; the adapter target is
`3.5.4`, with minimum supported runtime `3.3.0`.

AGENTS and SKILL require EACH substantive owner-facing Russian progress,
blocker, continuation and final report to carry a fresh Moscow
`[HH:MM DD.MM]` timestamp. However, the unchanged reference blob
`e72a2bc719f21a8e3020cb9d17ab180722565d6e` (confirmed locally with
`git hash-object`) says only that every command receives one timestamp before
or with its first substantive progress update. Its heading is “Per-command
timestamps in every CDC-managed chat.”

This initial-only guidance is insufficient: a long or resumed command can
produce several substantive reports after its first update. An initial timestamp
does not establish the observation time of later progress, blockers,
continuations or the final report. The reference therefore leaves stale or
missing later timestamps compatible with its wording, contrary to the current
AGENTS/SKILL reporting contract.

## Required current semantics

- Read a fresh runtime clock at the emission boundary of EACH substantive
  owner-facing Russian report and convert it to `Europe/Moscow`.
- Prefix that report with exactly `[HH:MM DD.MM]`, without seconds or any
  timezone suffix, including `MSK`. Never extrapolate, manually increment or
  reuse an earlier observation as a fresh clock reading.
- One command may have multiple distinct report IDs. Only an exact idempotent
  `command_id`/`report_id` retry may suppress a duplicate; sharing a command ID
  alone must not suppress timestamps for subsequent substantive reports.
- Legacy v1 per-command behavior is compatibility only, not the current
  per-report requirement. Timestamp evidence grants no authority.

## Owner-provided observations and proof limits

The following are owner-provided protected-audit observations at audit time,
not fresh remote or loader proof produced by this model:

- Canonical `release/v3.6.9` at
  `eef5be087a76f9cb877352ff720d449a060ee9dd`, package
  `1a3f49bc95f2b3da04671cbe3b924a5f98b6c714`, had the same stale reference
  blob and a per-report SKILL.
- Installed immutable SDK VERSION `3.6.8`, root
  `/opt/cdc-tools/cdc-3.6.8-reportfresh-20261022`, TREE
  `565288391ea560d5ae9723ebd15a4a17f26fb30e`, had the same ambiguity.
- The three inspected exact personal CDC skill paths were absent. This does
  not establish that every possible client loader is absent.

This native task uses the registered host SDK; it does not prove adoption in
every app, client or project. The operator is preparing a separate NEW qualified
immutable SDK documentation correction. This audit does not establish that
correction's activation or publication of a release. Old snapshot/release refs
and Source VERSION remain unchanged.

## Disposition

This documentation audit is applied through the current native doc scope. The
earlier unsubmitted draft sought a `src` reference change, but the registered
native writer permits only examples/docs. That pre-submit rejection created no
native task, attempt or handle. It does not authorize a source change or policy
expansion here.

The underlying source/reference wording is diagnosed and remains open in #113
until an authorized source integration. Broader audits of other registered
projects' canonical versions, effective loaders, instructions, adapters and real
outputs remain open, as do historical `admitted_open` RCA, including RCA101/113
without actual behavioral verification. No UNKNOWN is resolved by this audit.

This file records useful source-backed evidence, not a declaration of native
state, success or usage. The existing framework owns final diff-check, commit
and native publication. All IDs, UNKNOWN outcomes, budgets and spent remain
unchanged; no runtime, source/core, version, adapter, policy or scheduler change
is part of this task.

## Current adoption addendum — 2026-10-23 (Moscow)

The original audit above is preserved as history, including its exact identities
and proof limits. Its publication is `9860f312885fcdd90404badca97c41aefb2f6b1e`;
the earlier audited Source is `9d09f6961af46bc8cb44ae5a8464b895d6106cbc`.
The observations below are retained owner-provided authenticated evidence,
not fresh remote, native, installed-runtime or effective-loader checks by this
writer. Operator: `@bajoicheg`.

- **Canonical release:** `release/v3.6.11`, source
  `ec8dd91371db2d193d4a83a4e1612f48f3e1a261`, package TREE
  `51dc9c7f53af42e374ed81e4d00929c54865d126`. Exact hosted
  `CI39865949109`, attempt `1`, succeeded with `1801` tests; no rerun.
  Original failed `CI39861258360` remains failed history.
- **Installed immutable host SDK:** VERSION `3.6.11` at
  `/opt/cdc-tools/cdc-3.6.11-canonical-20261023`, identified by the canonical
  source/package above. The owner reports supported runtime-only registry CAS
  installation preserving all `51` old tasks, queue, IDs, UNKNOWN and spent,
  and current Codex-only dispatch; see the retained
  [installed receipt](https://github.com/bajoicheg/codex-compute/blob/91d370fea397a9bdce6fdfd89faed1c02293daf4/ops/operator/sdk3611-canonical-adoption-20261023/installed.json).
- **This registered project's Source:** `refs/heads/cdc/vps-development` at
  `9860f312885fcdd90404badca97c41aefb2f6b1e` before this task (locally
  confirmed). Local VERSION and adapter target remain `3.5.4`, minimum runtime
  `3.3.0`. Current AGENTS instructions retain the per-report fresh Moscow
  clock rule. This application changes only this audit; existing `src`
  reference/history, Source package, adapter and instructions are outside its
  write scope. Host/canonical success does not upgrade this Source or prove
  Windows/client effective-loader adoption.

The original corrected Source task `cdc-sdk3611-correction-20261023` had
successful candidate/main, but its release handle
`7fae62ea-7778-5d8a-a467-d2202bd7a166` ended `timed_out600/exit-15`;
its original foreground final remains `UNKNOWN`. Separately, task
`cdc-sdk3611-evidence-final-20261023`, handle
`2ee094a3-595f-57d1-8436-0815ea20ed3f`, genuinely succeeded with native
`261.87639682902955s`, foreground `493.2580256810179s`, CLI `0` and physical
`0`, according to the owner's
[joined release facts](https://github.com/bajoicheg/codex-compute/blob/91d370fea397a9bdce6fdfd89faed1c02293daf4/ops/operator/sdk3611-evidence-final-20261023/delivery-result.json).
Original `9/9` closed budget `766a2bd406736f1f8345faa5c09f11fd1263e6e2`
and new `2/2` closed budget `248f46e62845f500c7b6c2c156a96418cea91d8e`
remain separate. The final task reused exact old candidate/main and
`CI39865949109/attempt1/1801success`, first-submitting only the original
previously-unsent evidence ref to existing commit
`dcd9e3786c08b7d84eb9b66b29cb79dec14393ba`. No release-ref/Git Data effects
or CI were replayed.

The owner reports one actual installed general-economy consumer of
`3.424991157s`; its retained
[consumer receipt](https://github.com/bajoicheg/codex-compute/blob/91d370fea397a9bdce6fdfd89faed1c02293daf4/ops/operator/economy-corrected-source-delivery-20261023/actual-consumer.json)
preserves both old failed Source and corrected/final Source scopes, exact
original phase/budget/cost/usage identities and UNKNOWN model billing without
summation. App-window expense is a separate scope. These observations do not
declare native success or usage for this docs task.

Actual new application here is this documentation addendum. Broader per-project
Source/adapter/instructions and effective-loader adoption, including Windows
and clients, remain open. Both `native-report-freshness-602062-1` and
`native-report-freshness-602062-2` remain `admitted_open`; old-context RCA and
RCA101/113 are not closed without actual behavioral verification. All original
task/attempt/handle/report/checkpoint/RCA IDs, UNKNOWN, budgets/spent and old
audits remain intact. Fleet is paused, Gemini deferred, no Kimi.

Each substantive owner-facing Russian progress, blocker, continuation and final
report still requires a newly read runtime wall clock converted to
`Europe/Moscow`, prefixed exactly `[HH:MM DD.MM]` with no seconds or suffix.
Never reuse the first-update timestamp, infer time, or treat documentary
observations as authority. The framework owns diff-check, commit and native
publication; this addendum does not predeclare their outcomes.
