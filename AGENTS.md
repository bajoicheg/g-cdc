# CDC canonical development instructions

This repository develops CDC itself.

## Bootstrap rule

CDC N is developed under the previously released CDC N-1. CDC 2.10.0 is released at `refs/heads/release/v2.10.0`, package tree `63f25fb7402bf07d2e037de88194b7359c9e0f93`.

The current development authority is released CDC 2.10.0. CDC 2.10.1 is the next authorized roadmap stage and must preserve the N-1 independent-bootstrap rule.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

Self-hosting is converged on released CDC 2.10.0. See `docs/roadmap.md` for the active staged CDC 2.10 roadmap.
