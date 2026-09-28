# CDC 2.11.1 independent Q1 quality recheck

Verdict: **GREEN**. Q1 is closed. No material regression identified in the bounded fix diff.

Reviewed `e3443640874dc6c72913959367b4c87998d22c02..51ea128679a74862044004a60ea7f41a80fc9b5d` (original fix `9f0966b861890739927e6920453957350f53468c`); package tree `6ffacd32cce74c3537150778d9b37cfeb361a621`. The original whole-branch review had no other material finding. This recheck closes that review's sole finding; it does not substitute for parent-owned final integrated validation, CI, or release.

## Independently repeated original attacks

Used disposable actual local Git repositories and the original review's fixture-based attack construction, rather than relying solely on newly added tests.

- **Registry substitution:** fetched genuine registry, checked it out in the cache, committed a counterfeit watchdog ID locally, and installed `refs/replace` for the genuine remote commit. Ordinary Git still returned the counterfeit ID, proving that the overlay remained active. `resolve_live_target` returned the genuine `project-watchdog` and unchanged real registry SHA. PASS.
- **Unknown journal erasure:** wrote a genuine document containing an unknown operation; created a replacement commit containing empty operations; installed its replacement ref. Ordinary Git returned empty operations. `GitDocumentStore.read()` returned the actual unknown operation under the genuine remote SHA. A subsequent ordinary non-force CAS and read also retained the correct document. PASS.
- **Independent graft ancestry:** created two unrelated commits, wrote a legacy graft making one appear to descend from the other, and confirmed ordinary `git merge-base --is-ancestor` accepted the forged ancestry. `GitSource.is_ancestor` returned false. PASS.

The parent process environment retained its original absence of both `GIT_NO_REPLACE_OBJECTS` and `GIT_GRAFT_FILE` after these calls.

## Narrow regression execution

Independently ran only the added object-integrity suites:

- `PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover -s src/continuous-development-cycle/tests -p test_git_object_integrity.py -v`: **10/10 PASS**, 2.821 seconds. Includes genuine canonical package reads, all three coordination stores and subsequent CAS, pool/handoff/integration scope proofs, runtime object reads, package tree binding, graft rejection, and prior-wave replacement ancestry rejection.
- `PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover -s bootstrap/tests -p test_git_object_integrity.py -v`: **1/1 PASS**, 0.018 seconds.

## Fix review

`git_object_environment` builds a fresh child environment, preserves caller-specific index/author/transport settings, and then forcibly overrides both replacement and graft controls. Its order prevents inherited environment settings or caller overrides from re-enabling overlays. Exact object/provenance/CAS subprocesses consistently use this environment. The independent bootstrap helper applies equivalent stdlib-only controls without importing candidate implementation.

Reviewed all affected module diffs and their Git subprocess sites. The change does not alter non-force CAS construction, ref isolation, endpoint identity checks, or arbitrary worker/validation command environments. Existing local overlays are left intact for unrelated callers. Required-file registration and the reference documentation are consistent with the new helper. The added tests demonstrate genuine underlying contents and ancestry rather than merely asserting environment arguments.

No broad audit or duplicate full suite was performed. No source edits, external remote writes, live scheduler effects, or parent process polling. Mutations were limited to disposable local fixtures and this requested report. Parent package tree matched the reviewed source when checked, and the working tree was clean.
