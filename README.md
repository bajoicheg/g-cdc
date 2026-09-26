# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source repository for CDC 2.7+.

CDC 2.7 introduces an independently bootstrappable release model:

- stable CDC N-1 develops N;
- candidate CDC never serves as its only release validator;
- consumers pin canonical repository + version + release commit + exact package Git tree;
- product repositories vendor immutable releases but are not CDC source repositories;
- compatibility, fault-injection and cross-consumer evidence are mandatory release classes;
- migration never crosses an active owner or unresolved external guard.

CDC 2.7.3 is released at `refs/heads/release/v2.7.3` (release commit `88ee8a209caf562c02fe2ad53e047d7feee0e007`, package tree `806a66cd973954b3d5348ac36d39631717d9fe7b`). `g-cdc` uses released 2.7.3 to develop CDC 2.8.0 Autonomous Continuity & Isolation.
