# CDC 3.3.1 implementation plan

Root implements inline in candidate331, an isolated worktree from released 3.3.0. Owner accepted the administrative UNKNOWN isolation design before this implementation. Independent read-only SPEC and then distinct QUALITY reviewers are required by AGENTS; admit and durably reserve their actual starts first.

1. Add behavioral tests first and observe their failure on absent retirement support.
2. Implement a pure strict retirement API and one-CAS/readback helper. Extend v2 validation without changing legacy record shape. Validate append-only canonical transitions in GitLeaseStore and forbid retirement replay across attempts and modified bindings.
3. Update candidate version/source-lock/compatibility metadata and concise canonical recovery guidance. Run affected tests, freeze, run one full aggregate qualification and independent bootstrap/layout/package checks.
4. Ordered independent reviews against the frozen implementation. Fix actual findings and rebind only affected reviews/checks.
5. Stage exact candidate through the GitHub connector. Existing native host performs normal managed source publication, exact hosted CI qualification and immutable 3.3.1 release. Root verifies immutable evidence and actual package; update personal loader through normal verified save/sync.
6. Reread GPC source/lease/checkpoint and original immutable caller/runtime records. Persist exact owner decision and proof with hashes to the existing recovery checkpoint, independently read back, retire via released 3.3.1 canonical Git CAS only, and read back again. Continue the independent CDC package migration with original product policies/checkpoints/ledgers/history preserved. No original push/pilot replay or scheduler wake.
7. Finalize reviewers/native managed workers, verify physical quiescence and release receipts. Record honest source/adoption/UNKNOWN status and wall-time metrics.

The new bounded defect task links its predecessor all330 checkpoint and budget without resetting or completing any original UNKNOWN spending.
