# Current CDC status

As of **2026-10-22 (Europe/Moscow)**, based on the operator's bounded evidence summary. Source presence, source acceptance, installation, actual execution and consumer adoption are distinct. This refresh adds no release, installation, fresh model/CI acceptance or provider readiness.

## Three layers

| Layer | Completed scope and evidence | Residual acceptance |
| --- | --- | --- |
| Canonical published source | [`release/v3.6.9` source](https://github.com/bajoicheg/g-cdc/tree/eef5be087a76f9cb877352ff720d449a060ee9dd), commit `eef5be087a76f9cb877352ff720d449a060ee9dd` (2026-10-16); package tree `1a3f49bc95f2b3da04671cbe3b924a5f98b6c714`. | Publication does not establish installation or all-consumer acceptance. [Candidate metadata](../release/candidate.json) still says `candidate`, preparation source `445820c43da276fa525447dee91957c0707cab3c`; this is not a fresh adoption receipt. |
| Installed VPS SDK and operational fixes | Immutable VERSION `3.6.8`, root `cdc-3.6.8-intakefold-20261020`, TREE `0a39d44175d3b7fe7131670dd65980d582505db7`; separate mutable host/operator/checkpoint fixes below. | Not a 3.6.9 installation. Later operational fixes are not automatically in canonical package 3.6.9. Future reconciliation requires genuine scope, compatibility and required gates. |
| Execution evidence and consumer adoption | `KIMI_PRIMARY_CLI_ACCEPTED`; actual ACP COMPLETE artifact result proved. These are bounded execution proofs, not general consumer adoption. Token usage was not disclosed, not zero. | Full registered native Kimi scheduler success is NOT_PROVED; `phase1_done=false`. Fleet PAUSED; real Gemini connection DEFERRED. Broad original and all-project acceptance remain open. |

## Installed operational scopes, 20–22 October

Source is the [private evidence: codex-compute operational branch](https://github.com/bajoicheg/codex-compute/tree/cdc/vps-production-20261013). These are bounded VPS receipts, not universal adoption or an undelivered consolidation release. Dates below use Europe/Moscow; task identifiers remain unchanged.

| Date | Completed installed scope | Exact evidence reference |
| --- | --- | --- |
| 2026-10-20 | Compact TaskStore/status current-head task outcome summary | `status-task-outcome-20261020`; [private evidence: `e0ef8bff144f2694b5c46caf4557160e92eb1c54`](https://github.com/bajoicheg/codex-compute/commit/e0ef8bff144f2694b5c46caf4557160e92eb1c54) |
| 2026-10-20 | Authenticated postlaunch UNKNOWN administrative dispositions; original outcomes remain UNKNOWN | `native-postlaunch-disposition-20261020`; [private evidence: `1ae91eb905601272ac11859f5110dcd2866c8bea`](https://github.com/bajoicheg/codex-compute/commit/1ae91eb905601272ac11859f5110dcd2866c8bea) |
| 2026-10-20 | Typed Kimi artifact result consumer installed | `kimi-executor-consumer-20261020`; [private evidence: `c2d58904cf46d1c602f44c2cf718fc83d704f4e7`](https://github.com/bajoicheg/codex-compute/commit/c2d58904cf46d1c602f44c2cf718fc83d704f4e7) |
| 2026-10-20 | Kimi primary scheduler entry registered and installed; live task start denied, full native success unproved | `kimi-native-scheduler-20261020`; [private evidence: `049102b6d59915196d2221eea3ab299a6314205d`](https://github.com/bajoicheg/codex-compute/commit/049102b6d59915196d2221eea3ab299a6314205d) |
| 2026-10-20 | Backup/heartbeat manifest repair; verified ordinary checkpoint and Cloud recovery | `next-delivery-p1-20261020`; [private evidence: `cc9e4da61c391263bf6c3b881c84c259671213e8`](https://github.com/bajoicheg/codex-compute/commit/cc9e4da61c391263bf6c3b881c84c259671213e8) |
| 2026-10-21 | Widened bounded cross-component efficiency facts and capture-local scanner cache | `cdc-wide-efficiency-20261021`; [private evidence: `ef036ce165964f2d9a50e79074114f7ab54e3289`](https://github.com/bajoicheg/codex-compute/commit/ef036ce165964f2d9a50e79074114f7ab54e3289) |
| 2026-10-21 | Safe prelaunch diagnostics preserved through terminal receipt and fast summary | `native-safe-failure-20261021`; [private evidence: `4aa3c25c28049a4012861a9d9b6c4f11198a9eb4`](https://github.com/bajoicheg/codex-compute/commit/4aa3c25c28049a4012861a9d9b6c4f11198a9eb4) |
| 2026-10-22 | Heartbeat semantic filtering; unchanged commits do not trigger a model | `retrospective-heartbeat-filter-20261022`; [private evidence: `24f7c4e22e598d6b51be5cc04079410c2aebea4f`](https://github.com/bajoicheg/codex-compute/commit/24f7c4e22e598d6b51be5cc04079410c2aebea4f) |

See also the [public heartbeat update](https://github.com/bajoicheg/g-cdc/issues/101#issuecomment-6329229148). No new savings or measurement is claimed. Administrative disposition does not convert original UNKNOWN into successful execution or permit replay.

## Open acceptance boundaries

| Issue | Completed scope | Remaining boundary and selection |
| --- | --- | --- |
| #86 | Published [lease store source](../src/continuous-development-cycle/scripts/git_lease_store.py) preserves non-lease root entries, original lease mode and expected-parent push. | Full original live-layout/consumer adoption unproved. Conditional on an affected legacy migration; no newly observed active P0. |
| #100 | Cloud read authentication/backend binding proved; supported configuration-reader search exhausted. | P1: exact hosted Cloud setup/policy binding through supported GUI configuration. Readiness UNKNOWN; no repeated login/API search. |
| #101 | Published source and installed operational scopes above are distinct completed slices. | P1: first genuine registered Kimi result on useful newly admitted work; scope future canonical reconciliation only after compatibility and required gates. Broader efficiency acceptance remains open. |
| #111 | Published [receiving preflight](../src/continuous-development-cycle/scripts/receiving_ci_preflight.py), [release delivery](../src/continuous-development-cycle/scripts/release_delivery.py) and [host bridge](../src/continuous-development-cycle/scripts/managed_host_bridge.py) contain receiving admission and cumulative workflow/budget candidate binding. | Conditional on next actual authorized receiving delivery. No confirmed new active callsite defect; full original end-to-end acceptance unproved. |
| #112 | Bounded installed VPS/host/operator callsite search on 20 October found no active wrong-phase caller. | Conditional on next real receiving delivery: original detached-preview/assigned-branch result end-to-end acceptance stays open. |
| #113 | Published [reporting contract](../src/continuous-development-cycle/scripts/reporting_contract.py), [final response gate](../src/continuous-development-cycle/scripts/final_response_gate.py) and [host bridge](../src/continuous-development-cycle/scripts/managed_host_bridge.py) contain fresh reporting and authenticated durable RCA inventory/final boundary. | P1: authentic current execution producer/consumer report/RCA callback at the next authorized real boundary. Full original live consumer and all-project adoption unproved. |

No new unresolved active P0 is established by this bounded audit. All six issues remain open for their residual acceptance; completed source and installed scopes are recorded above. See the [roadmap](roadmap.md) and [entry instructions](../README.md). Owner pauses, provider limits, account boundaries, original attempts, charges and history remain binding.
