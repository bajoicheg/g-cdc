# CDC canonical development instructions

This repository develops CDC itself.

## Bootstrap rule

CDC N is developed under the previously released CDC N-1. CDC 2.10.2 is released at `refs/heads/release/v2.10.2`, package tree `2bee3b8159aaf80de981afba7cf284f21bafa1c3`.

The current development authority is released CDC 2.10.2. CDC 2.10 is complete; a new version line requires explicit roadmap authorization and must preserve the N-1 independent-bootstrap rule.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

Self-hosting is converged on released CDC 2.10.2. See `docs/roadmap.md` for terminal CDC 2.10 evidence and future explicitly authorized roadmap work.

## Recovery priority

CDC 2.10.3 is the corrective candidate developed under released 2.10.2. Complete continuity recovery before resuming 2.11. Unreleased 2.11 work is preserved in `archive/2.11.2-before-continuity-recovery` and existing `cdc/2.11.0-*` branches; consult `docs/continuity-recovery-2026-09-28.md`. Do not infer a release from VERSION. No task/milestone/commit is a final-response boundary while authorized runnable work remains.
