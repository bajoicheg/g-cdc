# CDC release process

1. Start from the immutable stable N-1 source lock.
2. Run independent bootstrap validation before candidate imports.
3. Materialize the candidate core under `src/continuous-development-cycle`.
4. Run candidate package/unit/contract tests.
5. Run compatibility and fault-injection suites.
6. Validate the exact candidate package in the registered three-consumer set.
7. Produce a release manifest binding canonical commit and package Git tree.
8. Publish immutable release ref `refs/heads/release/vN`; create a Git tag when the execution channel supports tag creation.
9. Roll out through consumer locks only at safe ownership boundaries.
10. After fleet convergence, migrate `g-cdc` self-hosting policy from N-1 to N.
