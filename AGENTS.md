# CDC canonical development instructions

This repository develops CDC itself.

## Bootstrap rule

CDC N is developed under the previously released CDC N-1. CDC 2.8.2 is released at `refs/heads/release/v2.8.2`, release commit `d926f98f01017e9c007a6cbb66023f729516eb9a`, package tree `bdf18b8dedb2f0cf62728935d92e6260b4a64ef0`.

The current development authority remains released CDC 2.8.2. The CDC 2.9 roadmap is explicitly accepted; CDC 2.9.0 Deterministic Distribution & Convergence is the active candidate scope and is developed under 2.8.2. Candidate 2.9.0 must never be its own only release validator; use the independent bootstrap contract before candidate imports. It becomes development authority only after independent release.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

Self-hosting remains converged on released CDC 2.8.2 while 2.9.0 is a candidate. See `docs/roadmap.md` for the accepted 2.9 roadmap.
