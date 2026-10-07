# CDC parallel maintenance

Owner authorized implementation on 2026-10-07 after proposing independent executors, bounded context, isolated writers, one integrator and fewer repeated checks.

Use the existing managed pool, worktree contracts, budget ledger and durable launch CAS. Prefer two independent writers in Work/Codex; an optional analyst may overlap only when existing slot/start caps permit. Do not increase a project's caps automatically. Serialize dependent or overlapping edits. Children return commits and evidence; root owns acceptance and publication.

Repair evidence-reuse argv validation: a nonempty list of strings accepts empty and whitespace elements verbatim. Contents and order remain significant; nonstrings and an empty list remain invalid. Repair the illustrative transport manifest by deriving VERSION bytes from its declared version and reconstructing its one-file Git tree. Keep placeholders illustrative.

Persist the operating recipe and honest metrics: elapsed time to acceptance, dependency/provider waits, validation repeats and integration rework. Unavailable token/cost measurements remain null. A parallel run alone does not prove comparative speedup.

Develop candidate 2.12.1 under immutable released 2.12.0, commit540d42b5a8b06b11d7aeae78585cffbff99da231/package247facf39eadf073883c5f1fe3b4a291278da7f8. Preserve legacy compatibility, FULL requirements for CDC core, required release/platform gates, paused schedulers, historical release evidence and GAD's separate owner. Archived Supervisor fixtures remain historical compatibility inputs.

Focused worker RED/GREEN tests precede integration. Freeze the aggregate package, run independent bootstrap/package/clean-consumer/fault/three-consumer checks and ordered independent spec/quality reviews. Required final CI remains separate. Repeat only when changed inputs or a concrete uncovered risk justify it. Source release, personal installation and live adoption require separate acceptance; implementation does not imply those outcomes.
