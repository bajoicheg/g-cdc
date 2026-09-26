# Self-hosting model

CDC 2.8.0 is independently released and is the development authority for `bajoicheg/g-cdc` while CDC 2.8.1 is developed.

Release identity:
- ref: `refs/heads/release/v2.8.0`;
- release commit: `08996f44eee59750ba27b3169eec8735511f30f5`;
- package tree: `ff5d24d685986a65a4239916020c969c9777ad05`;
- independent release evidence: `release/evidence-2.8.0.json` (Codex bootstrap 12/12, package 297/297, three-consumer GREEN).

CDC 2.8.0 now develops CDC 2.8.1. The N-1 rule remains unchanged: each future candidate is developed under the previous released CDC and may never serve as its only release validator.

The bootstrap validator remains deliberately outside candidate runtime imports and standard-library-only. Candidate runtime tests add evidence but cannot replace bootstrap evidence.
