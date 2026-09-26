# Self-hosting model

CDC 2.9.1 is independently released and is the current development authority for `bajoicheg/g-cdc`.

Release identity:
- ref: `refs/heads/release/v2.9.1`;
- release commit: `5579ac73e4df820ee163ecfb68829f3bf08173bf`;
- package tree: `a6a9ac4e4060112d77b58e8ac6aa67442dbb95c8`;
- independent release evidence: `release/evidence-2.9.1.json` (Codex bootstrap 12/12, package 378/378, aggregate 402/402 including 12 targeted assertions, 202 files, 35 fault scenarios, three-consumer GREEN).

CDC 2.9.2 is the current candidate and is developed under released 2.9.1 according to the N-1 rule. Candidate code, tests or package validation do not make 2.9.2 an authority before independent release.

The bootstrap validator remains deliberately outside candidate runtime imports and standard-library-only. Candidate runtime tests add evidence but cannot replace bootstrap evidence.
