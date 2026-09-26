# Self-hosting model

CDC 2.8.2 is independently released and remains the current development authority for `bajoicheg/g-cdc`.

Release identity:
- ref: `refs/heads/release/v2.8.2`;
- release commit: `d926f98f01017e9c007a6cbb66023f729516eb9a`;
- package tree: `bdf18b8dedb2f0cf62728935d92e6260b4a64ef0`;
- independent release evidence: `release/evidence-2.8.2.json` (Codex bootstrap 12/12, package 345/345, aggregate 357/357, three-consumer GREEN).

The CDC 2.9 roadmap is explicitly accepted. CDC 2.9.0 is the active candidate and is developed under released 2.8.2 according to the N-1 rule. Candidate code, tests or package validation do not make 2.9.0 an authority before independent release.

The bootstrap validator remains deliberately outside candidate runtime imports and standard-library-only. Candidate runtime tests add evidence but cannot replace bootstrap evidence.
