# Native administrative UNKNOWN recovery

These two protocols provide administrative custody. They never convert the
original effect to success, failure, cancellation, a wait return, or conditional
Git confirmation. They do not refund budgets or satisfy successful dependencies.
CDC 3.5.4 histories remain readable. The release binding changes only during the
reviewed release workflow; an implementation checkout is not release evidence.

## Prelaunch intake

`unknown_recovery` accepts the original `cdc-vps-control/v1` document through an
actual `GitDocumentStore`. Its public APIs are:

- `authenticate_prelaunch_intake(store, task_id, *, source_store, trusted_contract, at)`
  issues a `PrelaunchIntakeDispositionProof` after authenticating complete native
  ancestry, the original managed-host start request, intent, charged budget,
  guardian nonce and identity, canonical source lease, protected native channels,
  absence of native runtime artifacts, and current creator/guardian PID absence.
- `retire_prelaunch_intake_cas(store, expected_revision, task_id, proof, *, at)`
  makes one CAS on that same row and returns `revision`, `row`, and a newly issued
  retired `proof`. It preserves task, operation, budget, and the archived original
  row. `state` becomes `retired_unknown`; `result.administrative_disposition`
  records `original_effect=UNKNOWN`, `actual_wait=null`, and permanent no replay.
- `observe_prelaunch_intake_disposition(store, task_id, *, contract_digest, source_store)`
  observes an already committed tombstone and reissues its distinct administrative
  capability. After a lost reply, observe this entry; never repeat the CAS or start.
- `validate_prelaunch_disposition(store, task_id, row=None)` authenticates historical
  custody for host reads. It tolerates later genuine source generations. The
  row-only form is structural validation and grants no slot or terminal authority.
- `assert_new_intake_allowed(store, task)` and
  `assert_intake_start_allowed(store, task_id, start_request_digest)` check admission.
  The native document CAS also enforces replay exclusion atomically.
- `consume_intake_start(store, expected_revision, task_id, *, start_request_digest,
  controller_identity)` consumes a one-use start CAS before `bridge.start`.
  A tombstone and start consumption race on the original row; exactly one wins.
- `migrate_intake_registry_cas(store, expected_revision, old_digest, new_digest)`
  changes only the configured registry digest once every row is inactive. Supply
  independently reviewed old/new root configuration digests. It preserves every
  original task, charge, queue entry, and tombstone.

All guardian/controller entrypoints must enforce the native barrier. Stop old
creators and guardians before issuing a prelaunch proof; a check followed by
`Popen` supplies no start authority. Any controller history, including the legacy
`controllers` field, a controller identity, native handle, checkpoint, finish
result, start consumption, or actual native pool blocks prelaunch retirement.
Prepared-to-submitting intent history and the exact pinned observational metadata
remain readable; they cannot conceal consumed authority.

`trusted_contract` is deployment configuration, obtained independently from the
original protected channel. Required pins are `original_revision`, `row_digest`,
`source_revision`, `source_digest`, `creator`, `guardian`, `guardian_nonce`,
`pool_ref`, and `launch_roots`. Process identities contain `pid`, `birth`, and
`boot_id`. The canonical source ref/repository and pool endpoint are joined to
the original native request. Roots include the original journal and handle roots;
SDK-derived task/attempt identities scope checks inside shared native roots.
Also include the original protected controller and launch/output directories.
Optional `artifact_pins` permits only named original static files. A pin can be a
SHA-256 digest or `{sha256, uid, gid, mode}` for configured custody checks. Every
other file or symlink in the protected scope blocks disposition. Live, reused,
zombie, unprobeable, or wrong-boot process identities fail closed.

The replay key retains all task fields except `id` and `dependencies`, so changing
IDs, attempts, dispatch routing, or dependency names cannot replay the same
retired task contract. A genuinely distinct source candidate remains eligible.
`PrelaunchIntakeDispositionProof` is distinct from `VerifiedTerminalProof`.
Serialization discards its capability; hosts must never call normal terminal
completion with it or reinterpret UNKNOWN budget liabilities as terminal usage.

## Source publication quarantine

`source_publication_quarantine` supports a released native v2 source guard with
or without an original submission claim. Its public APIs are:

- `authenticate_source_publication_quarantine(store, *, terminal_proof,
  publication_store, source_remote, trusted_contract, at)` issues a sealed
  `SourcePublicationQuarantine` capability from actual native stores and an actual
  original `VerifiedTerminalProof`. Revalidation authenticates the original handle,
  issued controller/runtime descriptor, request, consumed pool attempt, genuine
  release, accepted integrated result, and complete relevant native ancestry.
- `quarantine_source_publication_cas(store, expected_revision, capability,
  evidence_reference, at)` archives the exact guard in one append-only
  `source-publication-quarantine/v1` entry in `submission_retirements`. All other
  lease fields, journal entries, generations, claims, terminal facts and charges
  stay unchanged. Raw CAS, serialized terminal proofs, and booleans cannot append it.
- `observe_source_publication_quarantine(store, *, operation_key, evidence_reference)`
  observes the authoritative entry after a lost reply and reports UNKNOWN with
  `conditional_update=false` and no submission authority.

The independently configured source pins contain `lease_revision`, `lease_digest`,
`original_lease_revision`, `handle_root`, `handle_id`, `request_ref`,
`publication_revision`, `publication_digest`, `operation_id`, `source_remote_id`,
`control_store_id`, `owner_decision`, and `publication_processes`. The owner
decision contains action `quarantine_source_unknown_without_replay`, the exact
`guard_digest`, and an immutable evidence `reference`. Publication processes are
all original sender birth identities from protected original observations; do not
invent a missing birth or infer complete closure from a wrapper's exit.

The guard must describe the original native `local_command` writer. Its exact
environment and contract stay bound through the original trusted lease digest.
The publication must join the actual integrated writer result and original handle.
The original publication entry must remain exactly SUBMITTED, with original
expected and intended commits. Fresh target HEAD must be a descendant of the old
expected HEAD, advance beyond it, and contain the intended candidate. This readback
never proves the old CAS. Observation time comes from the actual completed
physical/readback observations. Supply a fresh CAS `at` after issuing the capability;
do not reuse the timestamp from before network/history reads.
The native publication journal stays unchanged.
Native lease intent admission permanently rejects the original operation/candidate;
managed-host publication supplies `quarantine_store` to
`GitLaneIntegrationPublisher`, which checks the same native archive before
readback/admission and submission. Direct configured publisher users must supply
the canonical quarantine store, including when publishing to another ref.
A distinct corrective candidate still needs ordinary managed ownership and a
new one-use, ancestor-only, expected-head publication.
