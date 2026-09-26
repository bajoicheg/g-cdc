# Self-hosting model

CDC 2.9.0 is independently released and is the current development authority for `bajoicheg/g-cdc`.

Release identity:
- ref: `refs/heads/release/v2.9.0`;
- release commit: `539d1282c5803fbc79147a18c871aaddbf29fe25`;
- package tree: `75702b88df4ac8c7e91a4e5055f8aa734dddeeae`;
- independent release evidence: `release/evidence-2.9.0.json` (Codex bootstrap 12/12, package 361/361, aggregate 373/373, 188 files, 31 fault scenarios, three-consumer GREEN).

The CDC 2.9 roadmap is active. CDC 2.9.1 is the current candidate and is developed under released 2.9.0 according to the N-1 rule. Candidate code, tests or package validation do not make 2.9.1 an authority before independent release.

The bootstrap validator remains deliberately outside candidate runtime imports and standard-library-only. Candidate runtime tests add evidence but cannot replace bootstrap evidence.
