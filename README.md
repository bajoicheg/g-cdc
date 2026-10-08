# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source for CDC.

The current immutable source release is **2.12.0**, at `refs/heads/release/v2.12.0`, commit `540d42b5a8b06b11d7aeae78585cffbff99da231`, package tree `247facf39eadf073883c5f1fe3b4a291278da7f8`. It adds explicit quality levels, dependency-bound evidence reuse and bounded validation cycles. See `release/evidence-2.12.0.json` for exact CI checkout/tree provenance and separate metadata boundaries.

**2.12.1 is a maintenance candidate**, developed under released 2.12.0. It documents two independent writers, an optional analyst within existing caps and one integrator; repairs exact argv string validation and the transport example; and checks version metadata before expensive validation. See `docs/superpowers/plans/2026-10-07-parallel-maintenance.md` and `docs/execution/cdc-parallel-maintenance-20261007.json`. A candidate version is not a release or installation claim.

Source release, personal installation and live adoption are separate gates. Archived consumer snapshots prove compatibility and do not deploy consumers. Required FULL/platform/release checks remain in force. GAD has a separate owner; paused schedulers remain paused.
