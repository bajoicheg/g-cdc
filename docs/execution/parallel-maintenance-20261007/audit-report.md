# Read-only CDC parallelism/status audit

Audited source base `b72435542f40ec3f5b195f357c968c2346ab4f8f`, 2026-10-07. No repository edits, external writes, new workers, CI starts or test reruns performed.

## Minimal persistent change

Edit `src/continuous-development-cycle/references/runtime-routing-and-subagents.md` to add the missing operational default; add one concise cross-reference in `src/continuous-development-cycle/SKILL.md`. Existing DAG, worktree contracts, single integration gate, managed pool, durable CAS, host runtime, budget ledger and validation-cycle machinery already implement the safety/control plane. Do not build another pool/executor API.

For an authorized Work/Codex implementation with genuinely independent paths, prefer two isolated writers on the same exact base. An optional third read-only analyst may overlap only when task/wake start caps, active-agent cap, checkpoint reserve and actual runtime capacity admit it. A configured cap is an upper bound, not a target. If only two slots fit, defer analysis/review until a writer is terminal. If launch is unavailable, retain the same plan and sequential fallback. Each worker contract needs exact input/base, exact portable write paths (none for analysis), branch/worktree, required outputs, focused behavior checks, bounded time/context and explicit no shared integration/release authority. Child context should be bounded task input, rather than full inherited conversation.

Writers run focused behavioral RED/GREEN and affected regressions; the integrator audits every introduced path and reconciles fresh shared HEAD before assembling. Freeze one aggregate candidate and run the required FULL validation set once on that aggregate, followed by required ordered independent reviews and exact CI/release gates where applicable. These are separate evidence requirements, not permission to waive checks. A changed aggregate/input, failed result or concrete review finding needs a validation-cycle record explaining why existing proof is insufficient. Never blindly repeat the full suite per writer or for unchanged documentation. Do not reinterpret the final aggregate requirement as a reason to skip necessary focused correctness checks.

Record observed wall-clock phase elapsed, queued/provider waits, focused and aggregate validation counts, correction/rework count, conflicts/rollback and agent starts. Separate consumption accounting (sum of admitted runtime) from phase wall-clock duration. Tokens/cost absent from actual platform telemetry remain null with reason; no savings claim without a comparable observed baseline. Existing `parallel_benchmark.py` requires matched exact-candidate/workload/environment observations, so this one implementation alone proves execution, not a quantified speedup.

## Current release evidence and status correction

Root-owned metadata edits: prepend a current verified section to `AGENTS.md` and `docs/roadmap.md`; retain older candidate/history sections as history. Both currently begin with 2.12.0 candidate instructions. `release/evidence-2.12.0.json` records source-released 2.12.0:

- Immutable release/candidate source `540d42b5a8b06b11d7aeae78585cffbff99da231`, package Git tree `247facf39eadf073883c5f1fe3b4a291278da7f8`.
- Development driver released 2.11.9 `62cd32e91446675799d42247eac2a0312c33d363`, package `6867b012d01d776c2c0236b110980ba2c1292c26`.
- CI run 37610915069/job 112757678726 completed success, 13 steps, independent 46 bootstrap tests/full 1116 tests and three archived consumers. Reported head is `540d42b...`; actual PR checkout is `1fc3ee06ff558cb2362a9f1fd3f0bed7d9c577fd`; both root trees are `a89014cadd044ad2412709c22184f455b37446c1`. State tree equivalence explicitly, not literal checkout-SHA equality.
- Clean consumer 1116 GREEN originally bound to `397ba19aae37d260cccaf917ce167b39aa8256ba`, reused under the recorded unchanged package/bootstrap/workflow/consumer invariant.
- Ordered spec review GREEN; quality review initially RED and corrected with actual RED/GREEN/full1116 pass. Reviewed head `12ea9e8832f23396974407615f1cf1bdc6a0f1be`; final SHA independent rereview explicitly NOT_RUN. Preserve that limitation.
- Current main `b724355...` differs from release `540d42b...` only by the 77-line `release/evidence-2.12.0.json`. Its commit message is `docs(release): record independently validated CDC 2.12.0 [skip ci]`. Metadata exact-SHA CI is NOT_RUN, not inherited.
- Local `git rev-parse 540d42b...:src/continuous-development-cycle` equals the recorded `247facf...` package tree. Immutable release ref remote readback was outside this audit; do not turn local object verification into fresh remote authority.
- Canonical evidence ref in JSON is `refs/heads/cdc/release-evidence/v2.12.0`; its commit field remains an instruction to resolve/read back separately. Do not substitute current main as a resolved evidence endpoint.
- Personal installation and live consumer deployment remain separate acceptance gates. Archived checks do not establish adoption. Schedulers remain owner-paused; no Fleet convergence claim.

## Issue 86 and PR 79/80

Issue 86 is the legacy multi-document `GitLeaseStore.compare_and_swap` neighbor preservation defect, already corrected in 2.11.6 and present unchanged in released 2.12.0 and audited base. Current `scripts/git_lease_store.py:268` uses root `ls-tree --full-tree -z` raw bytes, excludes only exact root `lease.json`, preserves lease mode, reuses neighbor entries/objects/subtrees, parents to expected revision and retains non-force push/readback. Do not duplicate this fix or confuse it with the separate managed pool store CAS.

Regression evidence: `tests/test_git_lease_multidoc.py` covers neighbor modes/objects/nested tree; historical reads; CR/LF and non-UTF8 names; stale CAS preserving competing documents; nested cwd root lease selection; nested lease/root-neighbor preservation; invalid historical symlink entries. `docs/superpowers/reports/2026-10-05-cdc-2.11.6-progress.md` records initial real-Git RED (3 failures/1 error in 5) to GREEN (15 lease tests), then separate review findings and targeted fixes. `2026-10-05-cdc-2.11.6-spec.md` root-topology table and `...-quality.md` confirm exact raw byte/mode/subtree and stale-CAS behavior; quality adds independent executable lease mode and invalid root-entry probes.

PR79 retained RCA: canonical hidden fixture reproduced; exact fault inventory test relocated to independent `bootstrap/tests/test_managed_pool_fault_inventory.py`, with clean consumer package gate `bootstrap/consumer_package_checks.py` and its tests. PR80 retained RCA supports existing exact-blob/tree carrier-neutral adoption controls; old rollout statuses are historical. Roadmap already consolidates both; do not recreate features or destroy reports.

Fresh GitHub `github_fetch_issue` reads for issue86, PR79 and PR80 were attempted independently in one parallel read batch. All returned `ReadTimeout`, `error_code: UNKNOWN`, `isError: true`. Fresh external open/closed/merged status is therefore unknown. No issue closing/comment/PR action is justified by these reads. This audit intentionally did not retry unchanged unavailable reads or run a duplicate suite.

## Risks

The durable pool and ledger use distinct admission/start gates; budget admission alone never grants launch. Unknown spawn/receipt retains slot and charge until genuine reconciliation. Optional analysis/review cannot masquerade as the two separate ordered FULL reviewers. A later metadata candidate must not inherit exact-SHA CI. New package guidance changes the package fingerprint, even when behavior code is untouched, and must follow the actual scoped publication/release policy. User-authorized faster operation does not grant GAD ownership, Fleet writes, scheduler wake, repeated Cloud pilot or installation/adoption evidence.
