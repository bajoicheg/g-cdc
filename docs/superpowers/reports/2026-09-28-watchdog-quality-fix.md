# CDC 2.11.1 Q1 Git object-integrity quality fix

Base: `e3443640874dc6c72913959367b4c87998d22c02`. Isolated worktree/branch:
`g-cdc-quality-fix` / `work/watchdog-quality-fix`. The prior liveness worktree was
kept unchanged. Parent reserved `watchdog-quality-fix` for this bounded wave.

## Reproduced defects

Actual local Git replacement refs changed registry watchdog IDs, canonical package
bytes, and all three coordination-store documents beneath unchanged genuine object
IDs. The document-store case replaced an unknown operation journal with empty
operations. The same mechanism concealed out-of-scope changed paths from managed
pool/handoff/integration proofs, changed runtime object reads and package-tree
bindings, and fabricated prior-wave writer ancestry. The independent bootstrap
release-binding helper also read substituted VERSION bytes.

A separate concrete local-graft probe showed that `--no-replace-objects` alone does
not protect ancestry: an unrelated commit became an apparent descendant through
`.git/info/grafts`. Disabling the graft file restored the genuine non-ancestor
result. A committed regression reproduces that bypass through the integration gate.

## Correction

`git_object_integrity.git_object_environment` returns a fresh subprocess-only
environment that forces `GIT_NO_REPLACE_OBJECTS=1` and `GIT_GRAFT_FILE=os.devnull`.
It preserves explicitly needed author/committer, index, and transport settings.
The 38 Git subprocess sites across these 11 modules now receive that environment:

- `live_target`, `git_document_store`, `git_lease_store`, `managed_executor_store`,
  and `git_remote_identity`;
- `managed_executor_pool`, `managed_executor_handoff`, and the Git-only paths of
  `managed_executor_runtime`;
- `integration_gate`, `worktree_worker_contract`, and `package_transport`.

The independent bootstrap release-binding helper has the equivalent stdlib-only
environment and imports no candidate runtime. It suppresses only Git's graft-file
deprecation hint. No arbitrary user command in `run_checks`, worker subprocess
environment, parent process environment, scheduler adapter, or release metadata was
changed. Local overlays remain present for other callers; only authoritative CDC
Git reads/proofs/control operations ignore them.

## Actual verification

Retained output is under `watchdog-quality-evidence/`:

- `red-objects.txt`: 10 new object-integrity test methods exposed 10 assertion
  failures (including three store subcases) and two expected unreadable-genuine-data
  errors before correction.
- `red-bootstrap-objects.txt`: one independent bootstrap replacement test failed
  by returning counterfeit bytes under the genuine SHA.
- `green-objects.txt`: all 10 object-integrity methods passed after correction,
  including genuine read/CAS behavior with overlays still installed.
- `green-bootstrap-objects.txt`: the independent bootstrap test passed.
- `green-proof-regressions.txt`: **196 tests passed** across object integrity,
  live targets, coordination transport/identity, managed store/pool/handoff, lease
  v1/v2, integration gate, worker contract, and package transport.

Commands used `PYTHONDONTWRITEBYTECODE=1` and `python -B`; regression execution
returned exit 0. Static call-site inspection confirmed an explicit environment at
all 38 scoped Git subprocess sites, and `git diff --check` passed. No full package,
managed-process supervision, CI, or release gate was run by this worker: the parent
owns those final integrated checks and package manifest/validator refreshes.

No known focused regression remains failing. This fixes the reproduced local
replacement/graft overlay class; it does not claim a general untrusted-filesystem
sandbox. Only ephemeral local test repositories and this worktree were mutated.
There were no remote repository writes or live automation mutations.
