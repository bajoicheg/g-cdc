# CDC canonical development instructions

This repository develops CDC itself.

## Bootstrap rule

CDC N is developed under the previously released CDC N-1. CDC 2.7.3 is released at `refs/heads/release/v2.7.3`, release commit `88ee8a209caf562c02fe2ad53e047d7feee0e007`, package tree `806a66cd973954b3d5348ac36d39631717d9fe7b`.

The current development authority for this repository is released CDC 2.7.3. CDC 2.7.3 develops CDC 2.8.0. Future candidates must still never be their own only release validator; use the independent bootstrap contract before candidate imports.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A 2.8 release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

Self-hosting migration is complete: released CDC 2.7.3 is the repository development authority. CDC 2.7.3 develops 2.8.0.
