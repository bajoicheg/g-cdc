# Self-hosting model

CDC 2.7.0 is independently released and is now the development authority for `bajoicheg/g-cdc`.

Release identity:
- ref: `refs/heads/release/v2.7.0`;
- release commit: `5b84c89596e04d8411bf6cc24d8aa882a24c483a`;
- package tree: `a667549d48c2e93cba36359335c1b1ff4534ac86`;
- release validation: Actions run `36114289175` GREEN after candidate evidence was marked released.

CDC 2.7 now develops CDC 2.8. The N-1 rule remains unchanged: each future candidate is developed under the previous released CDC and may never serve as its only release validator.

The bootstrap validator remains deliberately outside candidate runtime imports and standard-library-only. Candidate runtime tests add evidence but cannot replace bootstrap evidence.
