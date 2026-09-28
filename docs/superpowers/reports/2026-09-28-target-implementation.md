# CDC 2.11.1 live target slice

Task 2, isolated worktree `/workspace/scratch/6ddf12473f4a/g-cdc-target-worker`, branch `work/target-2111`, base `03562f6`. Parent owns integration, release and all remote writes. This slice makes no scheduler effects, remote writes or adoption.

## Files

- `src/continuous-development-cycle/scripts/live_target.py`
- `src/continuous-development-cycle/tests/test_live_target.py`
- `src/continuous-development-cycle/references/live-target-resolution.md`
- `src/continuous-development-cycle/templates/watchdog-prompt.md`

## API/schema

`GitSource(repo, remote, expected_identity, *, clock=...)` uses the existing `git_remote_identity` normalization. The expected opaque endpoint identities and canonical repository name must be independently established in deployment policy; aliases or self-declared labels are not authority.

`resolve_live_target(registry_source, canonical_source, *, registry_ref, canonical_repository, registry_path='fleet/registry.json', target_path=None, release_path='fleet/target-release.json', package_path='src/continuous-development-cycle', max_age_seconds=300, clock=...)` raises `ValueError` on unknown/stale/future/disagreement/moved authority. It returns `live-target-resolution/v1` containing compatible registry/target, exact registry SHA/ref/source identity, canonical source identity, observation timestamps, and verified release binding. Adoption and scheduler write authorization are always false.

Narrow `RegistrySource` protocol: `identity()`, `pin(ref)->Revision(revision, ref, source_identity, observed_at_utc)`, `read_file(snapshot,path)`, `assert_current(snapshot)`. Canonical `ReleaseSource` additionally implements exact-object `tree_oid(snapshot,path,revision=None)` and `is_ancestor(a,b)`. Registry may use genuinely observed connector reads at actual remote SHAs; canonical provenance can use real Git. Caller adapters must prove independently configured identity, fresh observation time, exact revision reads and fresh pre/post ref checks. This slice provides no invented connector API and never re-labels a reconstructed local commit with a remote SHA.

Required companion `live-target-release/v1` fields are exactly `schema`, `version`, `canonical_repository`, `release_ref`, `release_commit`, `package_tree`. Registry, optional standalone v1 target and companion must all be read at the same exact registry revision. Optional configured standalone target is required when configured and must equal the embedded v1 target. The missing companion at legacy live Fleet is a deliberate fail-closed migration boundary. Publish the three documents together after release; parent owns that later authorized migration.

Canonical live release ref must equal companion release_commit. Exact release package tree and VERSION must agree. Canonical release evidence status/schema/repository/version/ref/tree and optional release_commit must agree. Its candidate source commit must be an actual ancestor with the same package tree. Freshness describes live read observations, not release age; final freshness/ref/identity checks reject a slow or moving read. GitSource fetches only local objects (no product/tracking ref or FETCH_HEAD update), never pushes.

## RED → GREEN evidence

Initial 14 tests failed as assertions because the resolver did not exist:
`/workspace/scratch/6ddf12473f4a/target-2111-red.log`.

Initial real-Git GREEN: 14/14, 6.180 seconds. A second concrete boundary run exposed malformed timestamp error handling plus the stale hardcoded prompt version:
`/workspace/scratch/6ddf12473f4a/target-2111-boundaries-red.log` (1 failure, 1 error; the implementation produced the malformed-date TypeError).

Both corrected: focused GREEN 16/16, 6.496 seconds:
`/workspace/scratch/6ddf12473f4a/target-2111-green.log`.

Tests exercise real local Git registry/release refs, exact objects, dirty-worktree independence, no cache ref changes, legacy embedded target, required standalone disagreement/missing, missing companion, trusted/changed endpoint identities, registry ref movement, release ref movement before/during read, stale/future/canonical/malformed observations, provenance mismatches, actual VERSION/tree agreement, candidate provenance, duplicate keys/unsafe paths and live prompt policy authority.

The first full-suite log ended without terminal unittest summary, so it is incomplete/unknown and not GREEN. A single supervised rerun explicitly captured child exit code 0: 672/672 PASS in 52.971 seconds, at the 16-test target revision. Log: `/workspace/scratch/6ddf12473f4a/target-2111-full-suite-retry.log`; exit capture: `/workspace/scratch/6ddf12473f4a/target-2111-full-suite-result.json`.

Final narrow-adapter inspection found a concrete missing identity-format boundary (an adapter could return None/empty/textual identity). Added one test with three cases, observed all three RED, then required opaque identity validation at initial and final observation checks. RED: `/workspace/scratch/6ddf12473f4a/target-2111-adapter-red.log`. Final focused GREEN count/time follows. Parent will run final integrated exact-head validation; no further duplicate full-suite attempt. Parent owns package-validator integration for new file references and any final release metadata changes.

Final target focused verification: 17/17 PASS in 5.998 seconds, including malformed identity and timestamp adapters. `git diff --check` also passes. No external effects occurred.

Committed slice: `d7a3c8bf7a75042353230730c21c15c6f4872550` on `work/target-2111`; worktree clean. Parent can cherry-pick the single commit. Independent integration/spec/quality reviews remain parent-owned.
