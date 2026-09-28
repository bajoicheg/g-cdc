# CDC 2.11.1 independent whole-branch code-quality review

Verdict: **CHANGES REQUIRED** — one material P1 finding.

Reviewed frozen head `e3443640874dc6c72913959367b4c87998d22c02`, source `5df50e0a08bc688d26356366e32a65b09b8b5129`, package tree `ea4ba0fa068a8ef5321148e1996edfb6b5d7ec74`, against released 2.11.0 `5865399c2ddc0cb9c84fd8ebad207612d6e6e02b`. This is a code-quality verdict, not a release verdict. Candidate publication/final CI remain parent-owned gates.

## Q1 — P1: Disable local Git replacement objects before trusting exact remote objects

Locations:

- `src/continuous-development-cycle/scripts/live_target.py:122-128`, consumed by exact reads at lines 168-183.
- `src/continuous-development-cycle/scripts/git_document_store.py:63-69`, consumed by authoritative journal reads at lines 94-105.
- The related managed and lease store Git subprocess helpers have the same inherited replacement behavior (`managed_executor_store.py:98-115`, `git_lease_store.py:66-75`). Those paths should receive the same correction; the independently reproduced failures below use the newly added target/document implementations.

These subprocesses inherit ordinary Git object replacement behavior. A pre-existing local `refs/replace/<real-remote-commit>` can redirect `cat-file`, tree/path lookup, `show`, and ancestry checks to different local objects. `ls-remote` still returns the genuine unchanged remote SHA, so all current endpoint/ref readbacks pass. The successful result then labels locally substituted data with the remote commit identity. Fetching the real object again does not remove or neutralize replacement refs.

This directly violates the documented contract that the resolver reads actual exact remote objects and never labels a locally reconstructed commit with a remote SHA. It also affects the new durable journal: an unknown operation can disappear from the state read under the real remote revision, undermining the premise used by duplicate-effect prevention. This requires local replacement configuration, but that configuration can legitimately remain in a reusable Git cache after unrelated history repair; neither constructor rejects it nor documentation requires an empty replacement-free repository.

### Independent actual-Git reproduction A: target authority substitution

Using `test_live_target.LiveTargetTests` only as a local repository fixture:

1. Create the fixture and call `source('fleet').pin('refs/heads/main')` to fetch the genuine registry.
2. In the cache, check out that registry revision on a temporary local branch.
3. Change only `fleet/registry.json`'s first project's watchdog ID to `locally-fabricated-watchdog`, commit locally, and execute `git replace <registry_revision> <local_commit>`.
4. Call the ordinary `resolve()` with no altered source adapter.

Observed successful result:

```json
{
  "remote_ref": "f96c4a894586522a546eae357a52b63e19aac805",
  "reported_registry_revision": "f96c4a894586522a546eae357a52b63e19aac805",
  "remote_watchdog_id": "project-watchdog",
  "resolved_watchdog_id": "locally-fabricated-watchdog",
  "replacement_commit": "233456b5078740667e8767e667b9ca079fd7be72"
}
```

No remote registry changes were made by the probe.

### Independent actual-Git reproduction B: hidden durable operation

Using `test_coordination_transport.CoordinationTransportTests` only as a local repository fixture:

1. Create a document store and CAS `{"operations":{"active":{"status":"unknown"}}}` into the local bare remote.
2. In the controller cache create a local replacement commit whose canonical `document.json` is `{"operations":{}}`.
3. Execute `git replace <genuine_document_revision> <replacement_commit>` and call `store.read()`.
4. Separately read the bare remote with Git to compare its real document.

Observed:

```json
{
  "remote_actual": {"operations": {"active": {"status": "unknown"}}},
  "store_read": ["903ea052f6dc1104b4b402774965a340e5021a52", {"operations": {}}],
  "replacement": "627d99a6b8345f86309c03d27c47fdea41433d00"
}
```

The remote remained unchanged during the substitution. This is a demonstrated incorrect authoritative read, not a claim that the probe invoked a live scheduler.

Recommended correction: enforce replacement-free Git interpretation for integrity/provenance/CAS operations (for example, an explicitly overridden `GIT_NO_REPLACE_OBJECTS=1` or equivalent global Git option), consistently across these transports. Add real-Git regression fixtures with replacement refs; confirm target/project bytes, package trees/ancestry, and unresolved coordination claims remain bound to actual objects. Preserve the existing normal non-force CAS and endpoint isolation behavior.

## Broader review coverage

Read the full changed-file inventory and material implementation: live target identity/freshness/provenance, liveness classification, runtime planning and post-claim gates, durable budgets/deadlines, accepted invocation lifecycle, continuation settlement, shared transport isolation, legacy lease CAS nonce and endpoint pinning. Reviewed corresponding tests, public capability/CLI contracts, prompt/SKILL integration, recovery references, release bindings, and stage boundary documents.

No other material finding identified. In particular, the prior F1 continuation fix preserves unclaimed run steps after enable, and the F2 transport fix separates coordination fetch/push from persistent ref mappings. Unknown/claimed requests remain blocked across renamed incidents; accepted runs retain independent terminal reconciliation. The explicit backend contract appropriately requires real capabilities and authoritative provider-budget debiting rather than pretending to implement a host API. The future 2.11.2 design is not counted as implemented work.

Additional independent probes of GitSource with `fetch.prune=true` plus either `fetch.pruneTags=true` or `remote.fleet.pruneTags=true` preserved a local tag; these did not establish an additional finding. No duplicate full suite was run. Inspected parent-produced `/tmp/cdc-2111-spec-corrected/result.json` once available: exact reviewed head/package; all eleven recorded bootstrap/package/consumer validation commands PASS. Those existing results do not cover Q1.

All review mutations were confined to disposable local Git fixtures and this requested report. No source edits, external remote writes, live automation changes, subagents, or parent process polling. The reviewed working tree remained clean.
