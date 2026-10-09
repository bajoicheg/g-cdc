# Submission recovery alias maintenance design

Owner-approved bounded maintenance candidate 2.12.2 is developed under immutable released CDC 2.12.1. Support the exact historical `required_pr_validation` mode only with `github_create_pull_request`, positive `not_submitted` / `cancelled_before_send`, and exact `POST repos/<repository>/pulls`. The saved historical mode is never rewritten. Existing PR_VALIDATION, MERGE_VALIDATION and COMPUTE_ONLY behavior stays unchanged.

All bind/digest/revision/claim/generation, complete fresh provider lookup, independent worker and parent-dispatcher stop, immutable barrier, append-only resolution, three-field transition and real Git CAS checks remain required. Reject rejection/403, ambiguous or accepted outcomes, arbitrary mode/backend/method/target, stale/missing proof, mismatched claims/candidates/generations and unrelated mutations. Synthetic neutral regression fixtures cover positive canonical validation, real CAS contention and lost reply.

Candidate metadata synchronization is separate from release. Preserve issue100 proposed 2.13.0 planning and all history. No main integration, immutable release, installation, consumer adoption or product guard recovery occurs in this candidate scope. Operational authorizations, accounting and managed handles remain outside the product tree.
