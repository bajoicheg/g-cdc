# Continuous Development Cycle

Current evidence: **22 October 2026**. [Status](docs/current-status.md) records what is installed and actually observed; [roadmap](docs/roadmap.md) records open work. [Detailed prior evidence](docs/status-evidence-history.md) remains immutable and does not need to be loaded on every resume.

Canonical **release/v3.6.9** is `eef5be087a76f9cb877352ff720d449a060ee9dd`, package TREE `1a3f49bc95f2b3da04671cbe3b924a5f98b6c714`. The installed VPS SDK is separately **VERSION3.6.8**, `cdc-3.6.8-rowreuse-20261022`, TREE `5631b2720edceed1d7567fee502302e7c85606bc`, with qualified maintenance overlays and mutable host/operator fixes. This is not a3.6.9 installation or a new release. [Candidate metadata](release/candidate.json) remains candidate preparation, separate from published refs, installation and adoption; see [source lock](release/source.lock.json).

Owner priority: no new Kimi work or dispatch; dedicated Kimi development/optimization/rollout/repeat acceptance is last. Installed `enabled_executors=[cdcexec1,cdcexec2]` retains the complete original registry, including Kimi. Preserve IDs, UNKNOWN, budgets/spent and history. Fleet is paused; real Gemini is deferred. Do not repeat completed acceptance, login or broad provider inventory.

<a id="operational-boundaries"></a>

## Existing operator consumers

- `cdc-vps status --summary` retains bounded original saved RCA/report IDs and explicit UNKNOWN coverage across tasks. These are historical metadata, never current closure or authority; [consumer details](https://github.com/bajoicheg/codex-compute/blob/5c3dfd0d8bc2f532f5bfd321eebf43abab0f796f/docs/aggregate-summary-reporting.md).
- `cdc-vps status --summary --task ORIGINAL_TASK_ID` selects before projection/IPC and observes recorded metadata; it grants no history/dispatch authority.
- `cdc-vps status --task ORIGINAL_TASK_ID --human` renders the authenticated original outcome, RCA and fresh Moscow owner report.
- `cdc-operator economy report` includes bounded saved RCA, per-task native usage and explicit UNKNOWN coverage with spending; `--task ORIGINAL_TASK_ID` retains the authenticated selected-task view. `--json` preserves structured observations and all original ledger rows; [consumer contract](https://github.com/bajoicheg/codex-compute/blob/6777e0304eaeeea1938bb893adb8b57e728d4fb8/docs/economy-reporting.md); [saved usage contract](https://github.com/bajoicheg/codex-compute/blob/578fc62f630a73694dde16c3a006cdde5fe8ce02/docs/general-economy-native-usage.md).

Native finish receipts and retrospective compact input preserve original RCA/provider-usage identity and UNKNOWN/partial coverage. Historical receipts do not refresh authority, backfill old UNKNOWN or change the ledger. [Current proofs and limits](docs/current-status.md), [registered-project audit](docs/reporting-adoption-audit.md), [multi-provider guidance](docs/multiprovider.md).

## Cloud entry

Read the actual consumer AGENTS, Source HEAD, checkpoint, lease/guard and journal. Use [Cloud profile](docs/cdc-cloud-profile.json), [entry implementation](src/continuous-development-cycle/scripts/codex_cloud_entrypoint.py) and [packaged guidance](src/continuous-development-cycle/references/cloud-fast-start.md). Build genuine current project-local setup/policy/host observations and pass their actual JSON path with `prepare --inputs`; there is no shared ready input file. Substitute the actually verified vendor/personal package root. Inputs contain observations, never credentials or cached authority.

Exact hosted Cloud GUI setup/policy binding remains **UNKNOWN (#100)**. Existing authentication/backend binding does not prove setup. Preparation supplies one typed next action; proceed only through the registered owner/intent/guard/budget/one-use gates. Unknown/submitting operations use original observe/reconcile transport; a new chat or reason does not permit replay. Watchdog resumes preserve inherited pauses.

[Prior full README](https://github.com/bajoicheg/g-cdc/blob/c54896b26fb73baa8c4e26169a40fef2a6a0a653/README.md) preserves every earlier installed slice and reference.
