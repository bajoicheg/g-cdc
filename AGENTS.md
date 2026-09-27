# CDC canonical development instructions

This repository develops CDC itself.

## Bootstrap rule

CDC N is developed under the previously released CDC N-1. CDC 2.10.2 is released at `refs/heads/release/v2.10.2`, package tree `2bee3b8159aaf80de981afba7cf284f21bafa1c3`.

The current development authority is released CDC 2.10.2. CDC 2.11 is explicitly authorized in `docs/roadmap.md`; develop 2.11.0 under 2.10.2, then preserve N-1 staged release discipline for 2.11.1 and 2.11.2.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

Self-hosting is converged on released CDC 2.10.2. CDC 2.11 development is authorized and must dogfood released 2.10.2 controls until 2.11.0 is independently released.
