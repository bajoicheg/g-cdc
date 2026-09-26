# CDC roadmap

## CDC 2.8 — COMPLETE / TERMINAL

The 2.8 roadmap is fully released and has no remaining runnable scope.

### 2.8.0 — Autonomous Continuity & Isolation — RELEASED

- Terminal-State v2 and No-Idle invariant.
- Execution-channel failover.
- Concurrent-writer reconciliation.
- Sensitive-context/publication guard.
- Control-plane isolation from publishable product state.

Release: `refs/heads/release/v2.8.0`.

### 2.8.1 — Operational Hardening — RELEASED

- Watchdog self-repair.
- Temporary-ref and coordination-state hygiene.
- Fresh blocker proof.
- Decision-authority policy.
- Evidence compaction.
- Progress enforcement.

Release: `refs/heads/release/v2.8.1`.

### 2.8.2 — Fleet & Publication Maturity — RELEASED

- Project-independent fleet control.
- Stuck-state detection.
- Counterfactual recovery.
- Sanitized public export with new public history.
- CDC dogfooding metrics.

Release: `refs/heads/release/v2.8.2`.

## Terminal-state evidence

CDC 2.8.2 independent validation:
- bootstrap: 12/12;
- package: 345/345;
- aggregate unittest: 357/357;
- package validation: 177 files/templates;
- fault scenarios: 28;
- consumers: 3/3;
- package tree: `bdf18b8dedb2f0cf62728935d92e6260b4a64ef0`.

There is no authorized next 2.8 development task. A new version line requires a new explicit roadmap; it must not be inferred from this completed roadmap.

## Future roadmap candidates — owner-requested backlog

These items are explicit future CDC roadmap candidates. They do not reopen the completed CDC 2.8 scope and do not assign a version number by themselves.

### Chat command timestamping

**Problem:** long-running CDC conversations make it hard to correlate a user command with repository, watchdog and compute events after the fact.

**Proposed fix:** after every user command handled under CDC, emit a compact chat timestamp in Moscow time (MSK, UTC+3) before or with the first progress update. The timestamp is evidence metadata only; it must not be treated as authorization, lease ownership or a repository event.

**Acceptance direction:**
- one MSK timestamp per user command;
- timestamp appears before substantive CDC progress for that command;
- format is compact and unambiguous, for example `[MSK 14:42]`;
- no duplicate timestamp spam inside one command unless a later update crosses a meaningful time boundary.

### RCA-to-roadmap feedback loop

**Problem:** anomalous or unclear CDC behavior can be diagnosed and fixed locally but then recur because the systemic correction never becomes roadmap input.

**Proposed fix:** for every materially unclear, contradictory or unexpected CDC case, perform a bounded RCA and convert the result into a short **fix formulation** in the CDC roadmap/backlog. Record the corrective mechanism, not a verbose incident diary. Deduplicate against existing roadmap items before adding a new one.

**Acceptance direction:**
- RCA distinguishes product failure, policy failure, execution-channel failure, stale state, concurrent-writer movement and operator/tooling error where applicable;
- every material RCA ends with one of: existing fix confirmed, existing roadmap item strengthened, or new fix formulation added;
- roadmap entries state the invariant/control to add or change;
- secrets, sensitive operational identifiers and disposable incident noise are not copied into the roadmap;
- repeated occurrences strengthen one canonical fix instead of creating duplicate backlog items.

### Fleet Watcher improvement harvesting

**Problem:** Fleet Watcher currently observes project health but can finish without converting repeated operational friction into CDC product improvement.

**Proposed fix:** every CDC Fleet Watcher run must produce exactly one bounded improvement proposal for CDC based on evidence from that run. The proposal may strengthen an existing roadmap item instead of creating a new one. If no novel improvement exists, record a deduplicated reinforcement/evidence update rather than inventing novelty.

**Acceptance direction:**
- exactly one proposal or reinforcement per Fleet Watcher run;
- proposal is derived from observed fleet evidence;
- proposal is checked against existing roadmap/backlog for duplicates;
- proposal does not grant new authority or expand project scope;
- proposal is concise: problem → fix formulation → expected invariant/benefit;
- low-value noise is prevented by allowing an existing item to receive additional evidence instead of forcing a new item.

### RCA-derived fix — canonical package distribution

**Observed failure class:** consumer GitHub Actions could not fetch private canonical `g-cdc` using its repository-scoped `GITHUB_TOKEN`; cross-repository checkout failed before migration logic.

**Root cause:** CDC release provenance and CDC package distribution currently share one private repository boundary, while consumer automation tokens are intentionally repository-scoped.

**Fix formulation:** publish or expose an immutable **CDC package transport** that can be consumed without broadening consumer repository credentials. The transport must remain bound to canonical release commit + exact package Git tree and must not require making the canonical development repository public.

**Expected invariant:** a consumer can fetch a released CDC package with least privilege while independently verifying the canonical release identity and exact package tree.

### RCA-derived fix — Git-tree fidelity in package transport

**Observed failure class:** archive/tarball transport preserved file contents but produced a different vendored subtree SHA because Git mode metadata was not faithfully reconstructed.

**Root cause:** filesystem/archive transport is content-oriented, while CDC package identity is a Git tree identity that includes path/mode/object metadata.

**Fix formulation:** CDC package transport and adoption tooling must be **Git-object-aware** or carry a signed/validated mode manifest sufficient to reconstruct the exact canonical subtree. Adoption must fail closed when reconstructed subtree SHA differs.

**Expected invariant:** every consumer that claims CDC version X has vendored subtree SHA exactly equal to the canonical package tree for X.

### RCA-derived fix — pre-run CI failure classification

**Observed failure class:** several GitHub Actions runs failed at `Set up job` / zero executable steps; treating those as product RED would trigger wrong remediation.

**Root cause:** CI state classification does not always distinguish runner/provider/pre-execution failure from executed test failure early enough.

**Fix formulation:** classify CI evidence into at least `pre_run_infrastructure`, `setup`, `product_test`, and `terminal_success` before applying recovery policy. Zero-step/pre-job failure must route to execution-channel recovery/failover rather than product correction.

**Expected invariant:** no source change is made solely in response to a run where product validation never executed.

