# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source for CDC.

CDC **2.11.2** releases cooperative project lanes and watchdog survivability on the released 2.11.1 liveness foundation. Disjoint writers can coexist under portable claims, one integrator owns shared-ref publication, durable publication attempts preserve CAS provenance, and watchdog materializations are generation-fenced and owner-pause aware. See [release evidence](release/evidence-2.11.2.json).

The 2.11 code release line is complete. Live Fleet authority convergence and safe consumer adoption remain separate rollout work; owner-paused schedulers remain paused.

Source release does not deploy a package. Personal activation requires runtime-byte readback after release; the currently retained verified installation is recorded in `release/active-package-acceptance-2.11.0.json`. Consumer compatibility snapshots are evidence only and do not update consumers' vendored packages.
