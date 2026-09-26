# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source repository for CDC 2.7+.

CDC uses an independently bootstrappable release model:

- stable CDC N-1 develops N;
- candidate CDC never serves as its only release validator;
- consumers pin canonical repository + version + release commit + exact package Git tree;
- product repositories vendor immutable releases but are not CDC source repositories;
- compatibility, fault-injection and cross-consumer evidence are mandatory release classes;
- migration never crosses an active owner or unresolved external guard.

CDC 2.9.1 is the current released authority at `refs/heads/release/v2.9.1` (release commit `5579ac73e4df820ee163ecfb68829f3bf08173bf`, package tree `a6a9ac4e4060112d77b58e8ac6aa67442dbb95c8`).

CDC 2.9 is active. The current candidate is 2.9.2 Continuous Autonomy & Learning, developed under released 2.9.1. Release requires the normal independent bootstrap, package, compatibility, fault-injection and three-consumer gates.
