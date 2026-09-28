# CDC 2.11.1 liveness spec review fix wave

Base: `30e71fcc1dc242dc389436548f73866f637d8eae`, isolated branch
`work/liveness-2111`. Parent reserved `liveness-spec-fix-1` and explicitly authorized
the analogous managed-executor/lease transport corrections after reproduction.

## Findings and corrections

1. **Unfinished idle recovery disappeared from continuation.** RED reproduced
   disabled + runnable + idle with an effect budget of one: enable succeeded,
   planned run remained unclaimed, but a now-healthy observation cleared `pending`.
   Both checkpoint and settlement now use one predicate that includes unfinished
   durable recovery steps. Tests cover budget/deadline exhaustion, a subsequent
   zero-budget wake, and an actual run on a later authorized wake. Current explicit
   pause or exact terminal proof still suppresses unclaimed work and prevents effects.

2. **Configured fetch mappings mutated local product refs during read and push.**
   Actual local Git RED tests reproduced both paths in the new document store and
   independently in managed-executor and lease stores. An empty-remote first CAS
   isolates push behavior, proving that a fetch-only correction is insufficient.
   All three now use `isolated_remote_args` from `git_remote_identity.py`: a unique
   command-scoped alias copies raw URL/pushURL values and inherits no local tracking
   mappings. Fetch additionally uses `--refmap=`. Raw endpoints preserve single-pass
   `insteadOf`/`pushInsteadOf`; already resolved URLs are never fed back to Git.
   Source effective fetch/push identities and alias fetch resolution are rechecked;
   the source pushURL (including its absence) is copied unchanged. Git's
   `remote get-url` rejects command-only aliases, so alias fetch verification uses
   the actual supported `ls-remote --get-url` path. No persistent remote is added.

3. **Legacy lease CAS admitted identical proposal replay.** Under a fixed clock,
   two equal state/parent proposals produced the same commit and both pushes returned
   success. RED reproduced this with two controllers and ordered real pushes.
   Lease proposals now have independent nonces and exact authoritative push readback.
   A separate RED reproduction showed that repointing the lease's configured remote
   after construction was accepted. The store now pins and rechecks the endpoint
   identity, keeping its public constructor and lease schemas unchanged.

## Verification

- Initial review reproduction: 5 tests, 4 expected failures; the pause/terminal
  control already passed. Retained as `red-spec-review.txt`.
- Shared store reproduction: 6 tests, 6 expected failures (lease/pool fetch and push
  mappings, lease endpoint repointing, identical lease proposals). Retained as
  `red-shared-transport.txt`.
- Focused transport and retained lease/managed-store/identity regressions:
  **53 tests passed** in `green-transport-regressions.txt`. This includes actual Git
  rewrite-chain traps, pushInsteadOf, explicit raw pushURL, unchanged local ref
  snapshots, unchanged persistent remote inventory, credential-safe identity errors,
  and old lease v1/v2 behavior.
- Focused Fleet file: **38 tests passed**, retained in `green-spec-runtime.txt`.
  The parent retains ownership of the full package/bootstrap/consumer/CI gates.

All evidence files are in `liveness-2111-evidence/`. Commands use
`PYTHONDONTWRITEBYTECODE=1` and `python -B`. Only ephemeral local test remotes and
this isolated worktree were mutated. No live automation or remote repository writes
occurred. The original documented cooperative scheduler atomicity and unknown-result
reconciliation limits remain unchanged; this wave makes no broader release claim.
