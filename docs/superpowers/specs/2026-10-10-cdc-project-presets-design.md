# CDC 3.1.0 project presets and initialization/migration plans

Status: proposed implementation under independently released CDC 3.0.0,
commit 6a7bebaf342f70fef058f63d24febb337a741cb0, package
2b8f3101a8fc6930e08387db1f509ab23c02d2f0. The owner authorized the 3.x
sequence and continuation; Fleet rollout and schedulers remain paused.

## Intent and scope

Make a new project usable without reconstructing CDC settings, and make an
existing project migration reviewable before any product write. Reuse the
existing adapter, checkpoint, policy-migration, Cloud-profile and managed
publication contracts. Do not introduce another controller or grant authority.
This is architectural work: define and independently review the typed interfaces
before implementation. Native inline implementation with focused TDD and one
aggregate FULL validation is the economical execution method. Root integrates;
independent ordered requirements/quality review remains mandatory.

The first 3.1 slice provides `cdc init REQUEST` and `cdc migrate REQUEST` as
deterministic read-only planners. They return concrete generated file contents
and a bounded change manifest, suitable for existing managed writers. The CLI
does not apply, execute validation commands, create a Cloud environment, mutate
leases, adopt consumers or change scheduler state. Live application remains with
the existing expected-head, invocation/intent/budget/guard/one-use publication
path; 3.3 release/adopt automation remains a separate roadmap stage.

## Presets

| Preset | Default quality | Required final platform |
|---|---|---|
| portable | MEDIUM | any |
| windows | MEDIUM | windows |
| android | MEDIUM | android |
| critical | FULL | any |

Every preset preserves required final remote GREEN, compute-only exact-SHA and
clean before/after requirements, Codex preference, conserved Actions, explicit
owner pause, existing budget/lease/operation semantics. Presets are starting
requirements, never platform evidence. Validation quick/full/release commands
are explicit input strings; full and release must be nonempty. Command strings
are data and never executed by these planners. No test fixtures are assumed.

## Interfaces and behavior

`project_setup.initialize(request: dict) -> dict` accepts exactly
`schema=cdc-init-request/v1`, `repository`, `branch`, `source_head`, `preset`,
`validation={quick,full,release}`, and nullable `cloud_profile_json`.
Repository is canonical owner/name, branch is a safe refs/heads suffix, and
source_head is an exact 40-character Git SHA. It renders an adapter from the
packaged development-cycle template, a validated v4 recovery checkpoint, an
unconfigured Cloud profile or the exact supplied reusable Cloud-profile text,
and an explicitly inert UNCONFIGURED Cloud-entry input scaffold. The scaffold uses
cloud-entry-inputs-template/v1 (not the runnable cloud-entry-inputs/v1), names
the five required snapshots and contains no invented probes or hashes. It must
fail the existing prepare command until genuine snapshots are materialized.
Outputs have portable fixed relative paths.
The checkpoint records no active owner, no operation, no validation success and
no release. It binds the adapter revision/digest and project/source identity.

`project_setup.migrate(request: dict, *, now_utc=None) -> dict` accepts exactly
`schema=cdc-migrate-request/v1`, `current_adapter_yaml`,
`current_checkpoint_markdown`, nullable `cloud_profile_json`, `preset`,
`expected_source_head`, and `probe={source_head,observed_at_utc,lease_released,
guard_reconciled}`. The runtime clock enforces a 90-second probe age (5-second
future tolerance). Pure injected clock is for embedded deterministic tests;
the CLI uses its own clock. Validate existing adapter/checkpoint bindings before
proposing updates. Add a backward-compatible optional keyword-only skill_version
diagnostic parameter through validate_checkpoint_24 -> validate_checkpoint ->
validate_adapter. Validate original structures at max(original minimum, 2.11.3)
only if inside the original range; default callers still use actual VERSION and
reject incompatible installations. Report original target incompatibility
separately. For explicit migration only, a known exclusive ceiling 3.0.0 may be
proposed as 4.0.0; other unsupported bounds require a reviewed migration.
Validate detached proposed adapter/checkpoint under the actual target runtime. Invalid/legacy policy, mismatched repository, unsupported
versions, duplicate YAML/JSON keys and malformed control data fail explicitly.

A stale/source-drifted probe returns RECONCILE with no proposed write artifacts.
Unreleased ownership, unreconciled guard or recorded external operation returns
WAIT preserving the original checkpoint and operation identity. A textual claim
in the request is only planning input, never an authenticated write grant.

For an eligible migration, use policy_migration.plan to change only quality,
validation.final_platform and policy revision/version compatibility when needed.
Preserve the higher current quality and never relax an existing non-any platform:
incompatible platforms require a separate reviewed migration and return CONFLICT.
An absent legacy quality block is conservatively FULL. Retain all other policy
sections, budgets, exceptions, pauses and custom values. Advance a decimal policy
revision by one only for a semantic policy change; a nondecimal revision that
needs change fails with an explicit request for a reviewed revision choice.
Rebind only checkpoint policy_revision/policy_digest; preserve all task/control/
external/history fields and Markdown body. NOOP preserves original YAML/Markdown
bytes. Profile selection is reported independently of application authority.

Cloud reuse validates codex_cloud_profile and requires the same repository and
source ref. Preserve its input text exactly. A changed adapter policy digest
reports REQUALIFY through the existing cloud-fast-start entry, never edits a
configured flag, invents current capability evidence or silently creates a new
environment. Without reuse, generated profiles remain UNCONFIGURED.

Every successful result has `schema=cdc-project-plan/v1`, `action`, `preset`,
`source_head`, `policy_digest`, `files=[{path,content,before_sha256,after_sha256}]`,
`changed_paths`, `cloud_reuse`, `reason`, `existing_operation`,
`original_compatibility`, and false write/external/lease/release/
adoption authority. File hash previews cover exact UTF-8 contents; identical
files are omitted from changed_paths. Results and request objects are never
mutated. No caller-defined output paths or free-text executable actions.

## Acceptance

- Each preset produces a validated adapter and v4 checkpoint with the expected
  quality/platform, repository/branch/SHA, no active authority and recovery state.
- Malicious command text remains literal; planning creates/edits no files and
  invokes no shell/provider/lease API. CLI duplicate JSON keys are rejected.
- Migration preserves every neighboring policy/control field, budgets, owner
  pause, checkpoint body and historical validation/release evidence.
- Stale/different/future probe and active/external/guarded work cannot produce
  applicable artifacts; original external identity remains available for recovery.
- FULL cannot become MEDIUM; Windows/Android cannot silently become any or each
  other; missing quality retains FULL; unknown presets and revisions fail clearly.
- Original installation incompatibility is distinct from proposed-bound validity;
  default checkpoint callers retain rejection, including archived ceilings.
- NOOP retains exact bytes; a real change advances revision/digest once and a
  second plan from that output is NOOP.
- Reused Cloud profile bytes survive unchanged; wrong repository/ref is rejected;
  stale policy returns REQUALIFY rather than READY or an environment start.
- Source-only packaged tests run in detached clean consumer layout. Core FULL,
  bootstrap, compatibility/fault, archived consumers, independent ordered review,
  exact-candidate CI and installation-byte acceptance remain release gates.

## Archived compatibility qualification

For later 3.x candidates, qualification of the original 3.0.0 archive ceiling
requires the candidate source lock to bind the independently released 3.x driver
and actual target version. Report original baseline and target installation
incompatibility explicitly. Validate original bindings under a supported diagnostic
version inside the original range, then validate only a detached ceiling-4.0.0 /
checkpoint-digest copy. Preserve revision, all controls/history and archive bytes.
This is compatibility qualification, not live migrate eligibility or adoption.
Other ceilings, missing/substituted locks and invalid original bindings fail.

## Alternatives and release

Recommended: planner composition with existing managed application. Automatic
filesystem/Cloud writes would duplicate authority and require new side-effect
contracts. Template-only documentation would leave migration preservation and
platform checks manual. Both alternatives are excluded from this first slice.
Do not claim all 3.1 features released until the concrete candidate passes gates.
3.2 adaptive allocation and 3.3 release/adopt remain planned. No live Fleet work.
