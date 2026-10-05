# CDC 2.11.6: taskless Compute recovery correction

Owner instruction: «Исправляй», 2026-10-05 17:03:40 MSK. This extends the already authorized 2.11.6 corrective scope under immutable released CDC 2.11.5.

The observed controller stopped on a success-only assertion before releasing a timed-out worker. A subsequent Cloud attempt exhausted its final gate freshness during repeated inventory pagination. The gate raised before `cloud exec`, leaving a taskless submitting journal. Released taskless recovery supports GitHub operations but not Compute-only CLI operations.

Required behavior:

1. Cloud transport durably distinguishes a gate rejection before its runner boundary from a lost/failed reply after that boundary. An ordinary gate exception records `not_submitted` and a fsynced `cancelled_before_send` journal. A process interruption without that completed journal remains uncertain. No existing journal, including cancellation, authorizes replay.
2. Persist the `started` boundary before calling the CLI runner. Any error after this boundary remains `unknown`; a caller-supplied runner may perform I/O, so its exception is never treated as proof of no submission.
3. Taskless recovery permits Compute-only `codex_cloud_cli` solely for a positively authenticated historical cancellation-before-send proof. Its target binds the entire immutable execution binding. The existing exact claim, released ownership, after-release fresh complete provider lookup and independently stopped worker and dispatcher checks remain mandatory. GitHub 403 is not a supported Cloud outcome.
4. A failed/cancelled/timed-out managed worker can transactionally release while preserving its unresolved external guard and every original submission claim. It publishes no result, reports scope_complete=false and requires failure evidence; successful publication retains the expected output/evidence checks.
5. Slow inventory/setup/source checks precede the short-lived grant. Revalidate freshness after slow reads and immediately before dispatch. There is no second full inventory inside the final gate.

The historical a3 has no recorded cancellation barrier. Its guard, frozen candidate, three charged Compute attempts and main ref remain unchanged. The new code is a future protocol and cannot retrospectively turn a traceback or empty inventory into a historical barrier. No scheduler effect or budget reset is authorized.

Implementation is one isolated N-1 managed writer with an independent branch-bound lease. Main integration and release remain separately guarded. Require failing baseline regressions, full package/bootstrap/consumer checks, independent specification/quality review and exact-head hosted CI before integration eligibility.
