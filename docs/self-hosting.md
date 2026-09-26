# Self-hosting model

CDC 2.8.1 is independently released and is the development authority for `bajoicheg/g-cdc` while CDC 2.8.2 is developed.

Release identity:
- ref: `refs/heads/release/v2.8.1`;
- release commit: `a3f3e8db0d6a863e1dfa19c27af51820c954bf69`;
- package tree: `fda5e955b987fcebbe49c3c27bf3b24114983eab`;
- independent release evidence: `release/evidence-2.8.1.json` (Codex bootstrap 12/12, package 329/329, three-consumer GREEN).

CDC 2.8.1 now develops CDC 2.8.2. The N-1 rule remains unchanged: each future candidate is developed under the previous released CDC and may never serve as its only release validator.

The bootstrap validator remains deliberately outside candidate runtime imports and standard-library-only. Candidate runtime tests add evidence but cannot replace bootstrap evidence.
