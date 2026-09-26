# CDC roadmap

## CDC 2.8 — COMPLETE / TERMINAL

The 2.8 roadmap is fully released and has no remaining runnable scope.

### 2.8.0 — Autonomous Continuity & Isolation — RELEASED

- Terminal-State v2 and No-Idle invariant.
- Execution-channel failover.
- Concurrent-writer reconciliation.
- Sensitive-context/publication guard.
- Control-plane isolation from publishable product state.

Release: `refs/heads/release/v2.8.0`.

### 2.8.1 — Operational Hardening — RELEASED

- Watchdog self-repair.
- Temporary-ref and coordination-state hygiene.
- Fresh blocker proof.
- Decision-authority policy.
- Evidence compaction.
- Progress enforcement.

Release: `refs/heads/release/v2.8.1`.

### 2.8.2 — Fleet & Publication Maturity — RELEASED

- Project-independent fleet control.
- Stuck-state detection.
- Counterfactual recovery.
- Sanitized public export with new public history.
- CDC dogfooding metrics.

Release: `refs/heads/release/v2.8.2`.

## Terminal-state evidence

CDC 2.8.2 independent validation:
- bootstrap: 12/12;
- package: 345/345;
- aggregate unittest: 357/357;
- package validation: 177 files/templates;
- fault scenarios: 28;
- consumers: 3/3;
- package tree: `bdf18b8dedb2f0cf62728935d92e6260b4a64ef0`.

There is no authorized next 2.8 development task. A new version line requires a new explicit roadmap; it must not be inferred from this completed roadmap.
