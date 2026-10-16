# Phase 1 multi-provider foundation

## Current scope

This candidate adds Codex, Gemini and Kimi model workers to existing CDC native execution. The owner deferred real Gemini connection and subsequently requested Kimi plus Phase1 completion with Codex+Kimi. Implementation, deterministic validation, real provider acceptance and production adoption are separate gates. Synthetic tests do not prove live acceptance. The owner handles the Kimi subscription and browser login; no purchase or paid API fallback is authorized.

The existing release version, native v1 records and installed consumers remain separate. This change adds no scheduler, provider fallback engine, database, MCP service, n8n, Jev or LiteLLM. Downstream projects are outside this Phase1 rollout.

## One execution authority

`agent_contract.validate_task` accepts a detached strict `cdc-agent-task/v1` envelope. The packaged schema and developer/reviewer examples define immutable repository/base, native task/worktree/branch, allowed operations/files, provider/model, security classification, budget, timeout, dependencies, deterministic checks, review and artifacts. Only public or synthetic input is accepted in v1. A declaration grants no permission.

`AgentWorker` retains exact `ManagedExecutorRuntime`, `GitManagedExecutorStore` and `LocalCommandBackend` types. Host code authenticates project/repository, the original native plan and the registered `GitProjectBudgetStore` binding. Every overlapping field must match. One original charged agent-start event binds attempt, operation key, scope and cost before the native pool launch CAS. No automatic retry, session resume, provider fallback or account rotation is added. Unknown token usage remains null, not a free or unlimited allowance.

The existing native runtime owns worktrees, conflict/dependency admission, supervision, timeout/cancel and persistent original-attempt observation. Host code supplies native lease admission and terminal release custody; constructing a facade does not acquire a lease. Native acceptance/integration and Source publication gates retain their authority. `accepted:false` in a model result prevents confusing observed execution with accepted integration.

## Provider boundary and host setup

Codex command construction uses explicit `exec --json --sandbox workspace-write|read-only --model MODEL --ignore-user-config`. Gemini CLI uses `--output-format stream-json --approval-mode auto_edit|plan --model MODEL --skip-trust -p PROMPT`. The host selects a pinned executable and independently eligible model/account; no auth material is embedded in envelopes or examples. Installed-version compatibility must be verified before later live use. Existing Codex integrations are preserved.

CLI approval settings and separate worktrees are not an operating-system security sandbox. Before real providers, qualify least-privilege UID/profile isolation, filesystem and network boundaries, hooks/configuration and exact credential exposure. Authentication remains external to task JSON. Google interactive subscription quotas are separate from API quotas. Never store credentials or raw model sessions in source.

An explicit nondefault `antigravity-cli` variant preserves the same provider/schema and binds its parser/command choice into the operation key and immutable CLI configuration. It remains an unadopted technical prototype. Google's [FAQ](https://antigravity.google/docs/faq/) excludes consumer-plan wrapping inside third-party coding agents/applications. Do not use consumer subscriptions as this CDC worker connection. Real Gemini configuration remains deferred.

Prompts bind the whole canonical task; reviewers also receive the actual Git diff. Input over96KiB is blocked before native claim. Strict JSONL parsing requires genuine session/final/terminal evidence. Mixed streams, duplicate fields, malformed/nonfinite usage, missing terminal events or contradictory errors cannot prove success. Usage is copied only when observed.

## Deterministic checks and review

`agent_check_runner.py` runs one provider and then the exact registered check argv sequentially under the original supervisor, without shell interpolation or retries. Provider nonzero exit skips checks; any check failure fails execution. Private fsynced receipts retain actual commands, exits, timestamps and log references. Missing evidence remains unknown.

After the checked developer bytes are committed within the admitted writer scope, a separate opposite-provider reviewer runs at that exact head. `review_of` binds the original base/head, developer provider and host-authenticated test references. Reviewer required_tests must be empty: reviews inspect developer evidence without executing modifying tests.

A review result is strict JSON: approved with no findings; changes_requested with actionable path/line/severity/message findings; or blocked. Approval requires successful native/provider execution, complete receipts and exact unchanged tracked bytes/modes, with no untracked/ignored files or hidden index flags. A clean Git status alone is insufficient. Cross-provider review never replaces deterministic tests, native integration or required human approval.

`max_iterations:1` means one review round. Requested changes return findings to the original worker/controller, but any correction needs separately admitted bounded work. Preserve all original starts, outcomes, charges and UNKNOWN liabilities.

## Host API and recovery

See packaged [agent-workers.md](../src/continuous-development-cycle/references/agent-workers.md) for a host construction/reservation/start recipe, observation/cancellation, exact reconstruction, checked-commit review handoff, native acceptance and original budget closure. The examples are inputs to existing admission, not launch commands.

After restart, rebuild the original runtime/store/facade from the same immutable plan/envelope/CLI/budget binding and journal path. Observe or collect the original attempt; never call start again. Changing a prompt, provider, executable or CLI variant cannot attach to an earlier result. Retain custody until actual descendants stop. A lost response is not a failed operation and does not authorize replay.

Checkpoint source, immutable candidate SHA, selected non-secret original state and required receipts in the existing durable store. Keep raw sessions and authentication caches private and excluded. Replacement hosts require fresh account/UID/endpoint qualification; restored metadata is not current eligibility.

## Automated validation

Provider executables in tests are synthetic. Git repositories, CAS stores, process supervision, deterministic check commands and recovery observations are real. Coverage includes both developer→commit→opposite default-CLI reviewer directions using actual test references, parallel isolated worktrees, conflicting claims, timeout/cancel, provider unavailability and active-controller reconstruction without duplicate launch.

Run focused checks through hosted CI. The canonical draft PR's existing release-validation workflow supplies the one frozen full package/bootstrap/compatibility gate; observe its original run rather than manually dispatching another FULL. Synthetic fixtures do not prove live Google access, provider billing state or successful real coding/review.

## Deployment and rollback

No fleet installation is authorized by this candidate. Before later live acceptance, use approved synthetic data, verified account identity, fresh eligibility/quota and original model admission. Complete real scenarios in both directions and retain genuine exits/check/review evidence. Before production adoption, freeze and qualify a release under existing package/projection, hosted and actual host gates; present that concrete security-sensitive deployment for owner approval.

Until adoption, rollback means stop new launches, reconcile original attempts, retain dirty/untracked worktrees and all charge/UNKNOWN evidence, and keep installed SDK/controller policy unchanged. After adoption, use the existing reviewed release/consumer rollback process. Never replace credentials under an active worker, reset a budget or replay an uncertain effect.

## Owner continuation: Kimi Code

The owner subsequently requested a Kimi adapter and live Phase1 completion using
Codex and Kimi. Gemini remains available in the contract with its real connection
deferred. The owner handles the Plus subscription and browser authorization;
CDC does not buy a plan, enable Extra Usage or fall back to a paid API.

The Kimi protocol is pinned to official `@moonshot-ai/kimi-code@2.2.0` (Node
>=22.19.0). Headless argv uses `--output-format stream-json --model MODEL
--agent-file PINNED_ROLE_FILE -p PROMPT`. Print mode uses auto permissions
internally. The explicit packaged developer agent exposes Read/Glob/Grep/Write/Edit;
the reviewer exposes only Read/Glob/Grep. Both forbid subagents. Deterministic
checks run afterward through the original CDC check runner, not a model shell.
The explicit agent file must be immutable to the provider UID; filesystem
containment remains mandatory.

The host must qualify an isolated HOME and KIMI_CODE_HOME with no project/user
extensions, hooks or MCP configuration, an empty explicit skills directory,
verified `config.toml` with `loop_control.max_attempts_per_step=1` and
`compaction_max_attempts=1`, `KIMI_LOOP_MAX_ATTEMPTS_PER_STEP=1`,
`KIMI_CODE_INFINITE_RETRY=0` and `KIMI_CODE_NO_AUTO_UPDATE=1`. There is no CLI
config-file flag in this version. Bind the executable/package tree, agent files,
profile config and environment in the host sandbox's immutable launch record.
Never place credentials in that record. One-attempt controls do not prove that
all credential/media/context recovery paths disappear; observable retry events
cannot produce adapter success.

Ordinary JSONL contains chat messages rather than turn result envelopes. The
pinned implementation emits `system.version` first and `session.resume_hint`
only after its internal completed turn. Require the exact version, completed
tool calls, a final assistant answer and one last resume hint, alongside genuine
native exit zero and check receipts. Never execute the hint. Missing, mixed,
truncated, duplicate or retry-bearing streams stay unaccepted. No token usage
is emitted; retain null. The terminal witness is source-derived for2.2.0 and
must be requalified before any CLI upgrade.
