# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source for CDC.

Released CDC **2.10.3** repairs premature lease finalization, restores release consistency and puts the active continuation contract first. It was developed under independently released 2.10.2; the installed personal skill now matches the 2.10.3 package.

CDC **2.11.0** is the active managed-execution candidate under released 2.10.3. It adds real worker supervision and closes preserved pool identity/CAS defects; independent release gates are still pending. Watchdog liveness (2.11.1) precedes cooperative lanes (2.11.2); see [recovery findings](docs/continuity-recovery-2026-09-28.md) and [roadmap](docs/roadmap.md). Candidate/release status and exact package identity are recorded in `release/candidate.json`.
