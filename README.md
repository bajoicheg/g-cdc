# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source repository for CDC 2.7+.

CDC uses an independently bootstrappable release model:

- stable CDC N-1 develops N;
- candidate CDC never serves as its only release validator;
- consumers pin canonical repository + version + release commit + exact package Git tree;
- product repositories vendor immutable releases but are not CDC source repositories;
- compatibility, fault-injection and cross-consumer evidence are mandatory release classes;
- migration never crosses an active owner or unresolved external guard.

CDC 2.8.2 is the current released authority at `refs/heads/release/v2.8.2` (release commit `d926f98f01017e9c007a6cbb66023f729516eb9a`, package tree `bdf18b8dedb2f0cf62728935d92e6260b4a64ef0`).

CDC 2.9 is accepted and active. The current candidate is 2.9.0 Deterministic Distribution & Convergence, developed under released 2.8.2. Release requires the normal independent bootstrap, package, compatibility, fault-injection and three-consumer gates.
