# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source repository for CDC 2.7+.

CDC 2.7 introduces an independently bootstrappable release model:

- stable CDC N-1 develops N;
- candidate CDC never serves as its only release validator;
- consumers pin canonical repository + version + release commit + exact package Git tree;
- product repositories vendor immutable releases but are not CDC source repositories;
- compatibility, fault-injection and cross-consumer evidence are mandatory release classes;
- migration never crosses an active owner or unresolved external guard.

CDC 2.7.0 is released at `refs/heads/release/v2.7.0` (release commit `5b84c89596e04d8411bf6cc24d8aa882a24c483a`, package tree `a667549d48c2e93cba36359335c1b1ff4534ac86`). `g-cdc` now self-hosts on released CDC 2.7 and uses it to develop CDC 2.8.
