# CDC canonical development instructions

This repository develops CDC itself.

## Bootstrap rule

CDC N is developed under the previously released CDC N-1. CDC 2.9.0 is released at `refs/heads/release/v2.9.0`, release commit `539d1282c5803fbc79147a18c871aaddbf29fe25`, package tree `75702b88df4ac8c7e91a4e5055f8aa734dddeeae`.

The current development authority is released CDC 2.9.0. The CDC 2.9 roadmap is explicitly accepted; CDC 2.9.1 Transactional Migration & Provider Reconciliation is the active candidate scope and is developed under 2.9.0. Candidate 2.9.1 must never be its own only release validator; use the independent bootstrap contract before candidate imports. It becomes development authority only after independent release.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

Self-hosting is converged on released CDC 2.9.0 while 2.9.1 is the active candidate. See `docs/roadmap.md` for the accepted 2.9 roadmap.
