# Continuous Development Cycle

`bajoicheg/g-cdc` is the canonical source for CDC.

This branch contains the **initial 3.0.0 source candidate**: a compact instruction core, an executable read-only `cdc resume` entry, composed risk/evidence assessments, honest operation observations and bounded executor recommendations. It is not a released or installed runtime. The qualified 2.13.0 Cloud fast-start integration and final release gates remain prerequisites.

Development uses an independent verified **2.12.1** driver from `refs/heads/release/v2.12.1`, commit `9b38bd4d9f5fb113ec10bdbca9fbe33908619a54`, package tree `9c45d98c3254e9658d452c505d8c97698e3fc9a7`. See `release/development-driver-2.12.1.json` for the actual 352-file byte-identity witness; it does not claim candidate CI, behavioral acceptance or adoption.

The approved baseline and implementation plan are in `docs/superpowers/specs/2026-10-09-cdc-3.0.0-lean-core-design.md` and `docs/superpowers/plans/2026-10-09-cdc-3.0.0-lean-core.md`. **Live Fleet rollout is paused by the owner for this work.**

Source release, personal installation and live adoption are separate gates. Archived consumer snapshots prove compatibility and do not deploy consumers. Required FULL/platform/release checks remain in force. GAD has a separate owner; paused schedulers remain paused.
