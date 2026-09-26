# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source repository for CDC 2.7+.

CDC 2.7 introduces an independently bootstrappable release model:

- stable CDC N-1 develops N;
- candidate CDC never serves as its only release validator;
- consumers pin canonical repository + version + release commit + exact package Git tree;
- product repositories vendor immutable releases but are not CDC source repositories;
- compatibility, fault-injection and cross-consumer evidence are mandatory release classes;
- migration never crosses an active owner or unresolved external guard.

CDC 2.8.0 is released at `refs/heads/release/v2.8.0` (release commit `08996f44eee59750ba27b3169eec8735511f30f5`, package tree `ff5d24d685986a65a4239916020c969c9777ad05`). `g-cdc` uses released 2.8.0 to develop CDC 2.8.1 Operational Hardening.
