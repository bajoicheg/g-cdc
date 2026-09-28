# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source for CDC.

CDC **2.11.0** releases real managed execution on the corrected 2.10.3 continuity foundation: durable plan/launch claims, actual bounded Linux workers, result publication/integration checks and parent completion gating. Independent reviews closed reproduced endpoint, CAS, bytecode, exhausted-budget, queued-plan and preparation-deadline defects. See [release evidence](release/evidence-2.11.0.json).

The approved sequence continues with **2.11.1 watchdog/Fleet liveness and live target resolution**, then **2.11.2 cooperative lanes**. Schedulers remain explicitly owner-paused. [Roadmap](docs/roadmap.md) separates active work from implemented historical candidates.

Actual installed and consumer package versions require separate byte/remote readback; source release alone does not deploy them. Prior verified2.10.3installation and safe g-ad-control adoption are recorded separately. Candidate/release identity is in `release/candidate.json`; installation2.11.0 follows release.
