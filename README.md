# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source for CDC.

CDC **2.11.3** is an owner-authorized candidate developed under released CDC 2.11.2. It adds multi-subscription Fleet Supervisor leader fencing, one-shot Fleet effects, truthful execution liveness, fail-closed final-response ownership checks, and atomic consumer adoption publication. See issue #82 and the 2.11.3 design/plan under `docs/superpowers`.

CDC 2.11.2 remains the current immutable released development authority until 2.11.3 independently passes bootstrap, package, fault, review and consumer gates and receives its own release identity. Owner-paused schedulers remain paused.

Source release does not deploy a package. Consumer compatibility snapshots are evidence only and do not update consumers' vendored packages.
