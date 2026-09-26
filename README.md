# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source repository for CDC 2.7+.

CDC uses an independently bootstrappable release model:

- stable CDC N-1 develops N;
- candidate CDC never serves as its only release validator;
- consumers pin canonical repository + version + release commit + exact package Git tree;
- product repositories vendor immutable releases but are not CDC source repositories;
- compatibility, fault-injection and cross-consumer evidence are mandatory release classes;
- migration never crosses an active owner or unresolved external guard.

CDC 2.9.0 is the current released authority at `refs/heads/release/v2.9.0` (release commit `539d1282c5803fbc79147a18c871aaddbf29fe25`, package tree `75702b88df4ac8c7e91a4e5055f8aa734dddeeae`).

CDC 2.9 is active. The current candidate is 2.9.1 Transactional Migration & Provider Reconciliation, developed under released 2.9.0. Release requires the normal independent bootstrap, package, compatibility, fault-injection and three-consumer gates.
