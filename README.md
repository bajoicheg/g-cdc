# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source for CDC.

CDC **2.11.3** is the current immutable source release. It adds multi-subscription Fleet Supervisor leader fencing, one-shot Fleet effects, truthful execution liveness, fail-closed final-response ownership checks, and atomic consumer adoption publication. Release identity: `refs/heads/release/v2.11.3`; frozen source `7f31544ffd80252587b7ff1bd76b9a3f38e019e5`; package tree `39f733127ac130de4f647cf9e5ec55afcca0769c`.

CDC 2.11.3 is the current released development authority. Bootstrap, package, fault and three-consumer validation are GREEN; the exact-candidate Stage 1 re-review and Stage 2 review requirements were each skipped once by explicit owner waiver without relabeling the missing independent reviews GREEN. Owner-paused schedulers remain paused.

Source release does not deploy a package. Consumer compatibility snapshots are evidence only and do not update consumers' vendored packages.
