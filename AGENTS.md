# CDC canonical development instructions

This repository develops CDC itself.

## Bootstrap rule

CDC N is developed under the previously released CDC N-1. CDC 2.8.1 is released at `refs/heads/release/v2.8.1`, release commit `a3f3e8db0d6a863e1dfa19c27af51820c954bf69`, package tree `fda5e955b987fcebbe49c3c27bf3b24114983eab`.

The current development authority for this repository is released CDC 2.8.1. CDC 2.8.1 develops CDC 2.8.2. Future candidates must still never be their own only release validator; use the independent bootstrap contract before candidate imports.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A 2.8 release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

Self-hosting migration is complete: released CDC 2.8.1 is the repository development authority. CDC 2.8.1 develops 2.8.2.
