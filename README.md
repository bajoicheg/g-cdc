# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source repository for CDC 2.7+.

CDC 2.7 introduces an independently bootstrappable release model:

- stable CDC N-1 develops N;
- candidate CDC never serves as its only release validator;
- consumers pin canonical repository + version + release commit + exact package Git tree;
- product repositories vendor immutable releases but are not CDC source repositories;
- compatibility, fault-injection and cross-consumer evidence are mandatory release classes;
- migration never crosses an active owner or unresolved external guard.

CDC 2.8.1 is released at `refs/heads/release/v2.8.1` (release commit `a3f3e8db0d6a863e1dfa19c27af51820c954bf69`, package tree `fda5e955b987fcebbe49c3c27bf3b24114983eab`). `g-cdc` uses released 2.8.1 to develop CDC 2.8.2 Fleet & Publication Maturity.
