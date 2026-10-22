# Continuous Development Cycle

Canonical source status as of **2026-10-22 (Europe/Moscow)**: `bajoicheg/g-cdc` publishes `release/v3.6.9` at `eef5be087a76f9cb877352ff720d449a060ee9dd` (2026-10-16), package tree `1a3f49bc95f2b3da04671cbe3b924a5f98b6c714`.

The [candidate manifest](release/candidate.json) remains labeled `candidate`, with preparation source `445820c43da276fa525447dee91957c0707cab3c`. Preparation metadata is distinct from published ref/source evidence and is not an installation or adoption receipt. See the [source lock](release/source.lock.json).

The current VPS immutable SDK is **VERSION 3.6.8**, root `cdc-3.6.8-intakefold-20261020`, TREE `0a39d44175d3b7fe7131670dd65980d582505db7`, with separately installed mutable host/operator/checkpoint fixes from 20–22 October. This is **not a 3.6.9 VPS installation**. These documentation changes do not move the release ref or constitute a new release.

See [current status and evidence](docs/current-status.md) and the [roadmap](docs/roadmap.md). Original documentation remains in Git history.

## Cloud entry

Read the actual project [AGENTS.md](AGENTS.md), source HEAD, checkpoint, lease/guard and journal before setup or a new request. Preserve known operations. Use the [Cloud profile](docs/cdc-cloud-profile.json), [entry implementation](src/continuous-development-cycle/scripts/codex_cloud_entrypoint.py) and [packaged guidance](src/continuous-development-cycle/references/cloud-fast-start.md). Build the current project-local input observations according to that guidance and pass their actual JSON path with `prepare --inputs`; the repository does not supply a shared ready input file.

In a consumer, substitute its actually verified vendor root; a personal loader uses its verified extracted package path. Inputs are project-local hash-bound observations, never credentials or cached authority. Supply genuine per-mode namespace, setup/policy and fresh host evidence. **Cloud setup readiness remains UNKNOWN** until the exact supported hosted GUI configuration and policy binding are established (#100). Authentication/backend binding alone does not configure every Cloud path. Do not repeat login or broad provider inventory.

Preparation returns one typed next action, not execution authority. Continue through the existing registered caller and its owner/intent/guard/budget/one-use gates. Unknown/submitting operations are observe/reconcile-only through their original transport; a new chat or reason string does not authorize replay. Preserve original attempts, charges, UNKNOWN outcomes and append-only history. Reuse verified evidence within its actual scope. Watchdog resumes preserve inherited pauses.

## Operational boundaries

See [multi-provider guidance](docs/multiprovider.md). `KIMI_PRIMARY_CLI_ACCEPTED` and an actual ACP COMPLETE artifact result are proved; full registered native Kimi scheduler success is unproved and `phase1_done=false`. Fleet remains paused by the owner; real Gemini connection remains deferred. Provider permissions, account boundaries, existing pauses and separate product/GAD ownership remain in force. Source publication, installation, execution and consumer adoption require separate evidence and gates.

Registered VPS dispatch is currently **PAUSED** after a consumed/pre-handle Kimi UNKNOWN blocked its executor slot. The status API remains active. A bounded controller permission repair is installed, but no new native Kimi success or guide publication is claimed. See the [incident and next P1](docs/current-status.md#registered-kimi-attempt-22-october).
