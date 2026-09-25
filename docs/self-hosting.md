# Self-hosting model

CDC 2.7.3 is independently released and is the development authority for `bajoicheg/g-cdc` while CDC 2.8.0 is developed.

Release identity:
- ref: `refs/heads/release/v2.7.3`;
- release commit: `88ee8a209caf562c02fe2ad53e047d7feee0e007`;
- package tree: `806a66cd973954b3d5348ac36d39631717d9fe7b`;
- independent release evidence: `release/evidence-2.7.3.json` (Codex bootstrap/package/three-consumer GREEN).

CDC 2.7.3 now develops CDC 2.8.0. The N-1 rule remains unchanged: each future candidate is developed under the previous released CDC and may never serve as its only release validator.

The bootstrap validator remains deliberately outside candidate runtime imports and standard-library-only. Candidate runtime tests add evidence but cannot replace bootstrap evidence.
