# Continuous Development Cycle

Canonical source status as of **2026-10-22 (Europe/Moscow)**: `bajoicheg/g-cdc` publishes `release/v3.6.9` at `eef5be087a76f9cb877352ff720d449a060ee9dd` (2026-10-16), package tree `1a3f49bc95f2b3da04671cbe3b924a5f98b6c714`.

The [candidate manifest](release/candidate.json) remains labeled `candidate`, with preparation source `445820c43da276fa525447dee91957c0707cab3c`. Preparation metadata is distinct from published ref/source evidence and is not an installation or adoption receipt. See the [source lock](release/source.lock.json).

The current VPS immutable SDK is **VERSION 3.6.8**, root `cdc-3.6.8-prehandle-20261022`, TREE `145ba560e7d711d8f611d0a2b7b4d0b44592a0d9`, with separately installed mutable host/operator/checkpoint fixes from 20–22 October. This is **not a 3.6.9 VPS installation**. These documentation changes do not move the release ref or constitute a new release.

See [current status and evidence](docs/current-status.md) and the [roadmap](docs/roadmap.md). Original documentation remains in Git history.

**Owner priority, 22 October:** all dedicated Kimi development, optimization, rollout and repeat acceptance work is at the very bottom of the backlog. General CDC reporting/RCA, efficiency, Cloud setup and release reconciliation remain useful work; using Kimi is not a prerequisite for the next P1. Existing installed registration and execution evidence are retained. This priority update does not change runtime scheduler configuration. Preserve original IDs, UNKNOWN and spent; do not repeat completed acceptance.

## Cloud entry

Read the actual project [AGENTS.md](AGENTS.md), source HEAD, checkpoint, lease/guard and journal before setup or a new request. Preserve known operations. Use the [Cloud profile](docs/cdc-cloud-profile.json), [entry implementation](src/continuous-development-cycle/scripts/codex_cloud_entrypoint.py) and [packaged guidance](src/continuous-development-cycle/references/cloud-fast-start.md). Build the current project-local input observations according to that guidance and pass their actual JSON path with `prepare --inputs`; the repository does not supply a shared ready input file.

In a consumer, substitute its actually verified vendor root; a personal loader uses its verified extracted package path. Inputs are project-local hash-bound observations, never credentials or cached authority. Supply genuine per-mode namespace, setup/policy and fresh host evidence. **Cloud setup readiness remains UNKNOWN** until the exact supported hosted GUI configuration and policy binding are established (#100). Authentication/backend binding alone does not configure every Cloud path. Do not repeat login or broad provider inventory.

Preparation returns one typed next action, not execution authority. Continue through the existing registered caller and its owner/intent/guard/budget/one-use gates. Unknown/submitting operations are observe/reconcile-only through their original transport; a new chat or reason string does not authorize replay. Preserve original attempts, charges, UNKNOWN outcomes and append-only history. Reuse verified evidence within its actual scope. Watchdog resumes preserve inherited pauses.

## Operational boundaries

The existing VPS owner status path now exposes authenticated reporting/RCA through `cdc-vps status --task ORIGINAL_TASK_ID --human`: fresh Moscow format, original outcome, explicit UNKNOWN and open RCA/backlog references. This is one installed consumer of #113, implemented without Kimi. See the [consumer guide](https://github.com/bajoicheg/codex-compute/blob/0934ed42a44ec9cdcfe57167905f8804e2b4557a/docs/owner-status-report.md) and [installed evidence](docs/current-status.md#owner-status-reportingrca-consumer-22-october). Broader adoption remains open.

See [multi-provider guidance](docs/multiprovider.md). A new useful registered Kimi P1 `cdc-kimi-outcome-report-p1-20261022` reached genuine native `succeeded`, worker `succeeded`, `scope_complete=true`, published the corrected [outcome/reporting guide](https://github.com/bajoicheg/codex-compute/blob/1a493d891f646ceac28665fe5e44f7093d3fefca/docs/status-task-outcome.md), and released its lease. The earlier maxSteps3 failures and operator-applied quickstart remain separate historical facts; neither was replayed. Native projection/environment/request cap now agree on4 within the unchanged hard guard4 and no-retry policy. See [current evidence](docs/current-status.md#registered-kimi-attempt-22-october). This is one bounded native success; `phase1_done=false`, Fleet remains paused and real Gemini remains deferred. Installed operational fixes and consumer adoption remain distinct from canonical release.

Registered VPS dispatch is **RESTORED**. Supported administrative prehandle closure preserves original UNKNOWN/IDs/spent; the unconsumed reserve is cancelled. The new installed SDK snapshot remains VERSION 3.6.8; canonical release refs are unchanged. See [recovery and native evidence](docs/current-status.md#registered-kimi-attempt-22-october).
