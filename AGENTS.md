# CDC canonical development instructions

This repository develops CDC itself.

## Bootstrap rule

CDC N is developed under the previously released CDC N-1. CDC 2.9.1 is released at `refs/heads/release/v2.9.1`, release commit `5579ac73e4df820ee163ecfb68829f3bf08173bf`, package tree `a6a9ac4e4060112d77b58e8ac6aa67442dbb95c8`.

The current development authority is released CDC 2.9.1. The CDC 2.9 roadmap is explicitly accepted; CDC 2.9.2 Continuous Autonomy & Learning is the active candidate scope and is developed under 2.9.1. Candidate 2.9.2 must never be its own only release validator; use the independent bootstrap contract before candidate imports. It becomes development authority only after independent release.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

Self-hosting is converged on released CDC 2.9.1 while 2.9.2 is the active candidate. See `docs/roadmap.md` for the accepted 2.9 roadmap.
