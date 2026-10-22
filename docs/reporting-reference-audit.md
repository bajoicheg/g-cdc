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
