# CDC canonical development instructions

This repository develops CDC itself.

## Bootstrap rule

CDC N is developed under the previously released CDC N-1. CDC 2.7.0 is now released at `refs/heads/release/v2.7.0`, release commit `5b84c89596e04d8411bf6cc24d8aa882a24c483a`, package tree `a667549d48c2e93cba36359335c1b1ff4534ac86`.

The current development authority for this repository is released CDC 2.7.0. CDC 2.7 now develops CDC 2.8. Future candidates must still never be their own only release validator; use the independent bootstrap contract before candidate imports.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A 2.7 release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

Self-hosting migration is complete: released CDC 2.7.0 is the repository development authority. CDC 2.7 develops 2.8.
