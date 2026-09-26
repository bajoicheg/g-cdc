# CDC canonical development instructions

This repository develops CDC itself.

## Bootstrap rule

CDC N is developed under the previously released CDC N-1. CDC 2.8.2 is released at `refs/heads/release/v2.8.2`, release commit `d926f98f01017e9c007a6cbb66023f729516eb9a`, package tree `bdf18b8dedb2f0cf62728935d92e6260b4a64ef0`.

The current development authority for this repository is released CDC 2.8.2. The CDC 2.8 roadmap is terminal at 2.8.2; any later candidate must begin from a new explicit roadmap while preserving the N-1 rule. Future candidates must never be their own only release validator; use the independent bootstrap contract before candidate imports.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

Self-hosting is converged on released CDC 2.8.2. See `docs/roadmap.md` for terminal roadmap state.
