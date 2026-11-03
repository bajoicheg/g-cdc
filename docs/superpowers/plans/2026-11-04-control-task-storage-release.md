# CDC 3.6.17: bounded original control task storage

The owner authorized closure of R01–R05. This release contains only R01's
opt-in storage format on the exact native GitDocumentStore class. The existing
control document has 15,008 bytes left below its unchanged 4 MiB legacy bound.
No task, original ID, UNKNOWN, budget/spent, receipt, claim or history may be
deleted or retired to obtain capacity. Operator R02–R05 changes remain separate.

The independently released development driver is CDC 3.6.16, source
`3b916acffaf930b70ebca163057b64ead04bc818`, package TREE
`aa76a1446867d31c54d6fec8d06ed57785844e74`; original FULL run
`41184809539` is retained N-1 provenance. Installed SDK snapshots remain immutable.

The optional physical tree contains exactly a bounded document.json manifest
and a tasks tree of canonical immutable task blobs. Hash filenames bind original
task IDs, the manifest binds the full logical document digest and count, and
reads reconstruct the unchanged cdc-vps-control/v1 document. Legacy mode keeps
its original schema and 4 MiB cap. Opted-in readers support mixed historical
formats. Every task blob and metadata object remains bounded at 4 MiB, total
logical/aggregate bytes at 128 MiB and task count at 16,384. Size checks precede
blob body materialization. The original native type, endpoint, ancestry,
transition/capability, expected-parent and nonforce single-ref CAS checks remain.

1. Preserve this single document-only bootstrap commit as PR_BASE, with the
   original package tree unchanged. The first next commit is IMPLEMENTATION;
   final binding commits retain a complete linear touched-path ancestry.
2. Integrate the isolated R01 RED/GREEN implementation, version/metadata and
   strict public synthetic tests. The private original control fixture and its
   exact preservation test/evidence stay outside the public package.
3. Validate changed package/release bindings, strict discovery inventory and
   supported consumer projections. Reuse qualified unchanged regression/FULL
   coverage; no local FULL or repeated completed acceptance. A new exact
   candidate hosted gate and genuine native release requirements remain pending.
4. Publish only through the existing registered Source/receiving/role/budget/
   guard/lease/one-use/expected-head pipeline under the independent N-1 driver.
   Preparation, publication, canonical release, installation and adoption retain
   distinct evidence. No credentials or native effects belong to this step.
5. Stage adoption in legacy mode. Before opting the control store into physical
   shards, use the existing genuine native quiet/completion/disposition boundary
   to establish that no original 3.6.16 actor can still act. An already launched
   actor can continue its external effect even though old readers reject the new
   tree. Do not rewrite terminal_pending or retire tasks for storage. Migrate by
   one genuine expected-head CAS with identical logical contents; never replay
   an UNKNOWN write. Preserve original history and all old outcomes.

Acceptance includes logical documents above 4 MiB with bounded physical head,
exact original-row/UNKNOWN/spent preservation, mixed authenticated history and
preparation projection, detached reads, unchanged-blob reuse, malformed/missing/
extra/duplicate index denial, per-object/aggregate bounds before bodies, SHA-256
Git repositories, stale CAS, interrupted object preparation and lost push replies.
Actual private control history authentication and Windows/client adoption remain
separate from these local synthetic checks. Fleet/Kimi stay paused and Gemini
remains deferred. No reviewing model or extra helper is introduced.
