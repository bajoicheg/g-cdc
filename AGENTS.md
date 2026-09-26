# CDC canonical development instructions

This repository develops CDC itself.

## Bootstrap rule

CDC N is developed under the previously released CDC N-1. CDC 2.9.2 is released at `refs/heads/release/v2.9.2`, release commit `0dd30a888be852d2820f690be04dbd374d732c06`, package tree `f9087eacbffee774c143eabf854c2cf08d610ec7`.

The current development authority is released CDC 2.9.2. The CDC 2.9 roadmap is terminal at 2.9.2. Any later candidate requires a new explicit roadmap and must preserve the N-1 independent-bootstrap rule.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

Self-hosting is converged on released CDC 2.9.2. See `docs/roadmap.md` for terminal roadmap state.
