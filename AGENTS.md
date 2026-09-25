# CDC canonical development instructions

This repository develops CDC itself.

## Bootstrap rule

CDC N is developed under stable CDC N-1. For CDC 2.7 the development authority is stable CDC 2.6.0 with validated package tree `e2cf6199eb60ca998012184b460c9a05c9f33b80`.

Candidate CDC 2.7 must never be its only release validator. Run the stdlib-only `bootstrap/validate_release.py --mode bootstrap` before importing candidate runtime code.

## Canonical-source rule

`bajoicheg/g-cdc` is the only canonical source for CDC 2.7+. Consumer repositories may vendor immutable released packages but must not become CDC source repositories. Product-specific AGENTS/policy/checkpoint/coordination remain outside the core package.

## Release boundary

A 2.7 release requires independent bootstrap GREEN, candidate package GREEN, compatibility GREEN, fault-injection GREEN and three-consumer GREEN. Version strings alone are never release evidence.

## Self-hosting

2.7 is developed under stable 2.6. Only after an independently validated 2.7 release may this repository migrate its own development policy to 2.7. CDC 2.7 then develops 2.8.
