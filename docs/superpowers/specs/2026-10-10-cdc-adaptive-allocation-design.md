# CDC 3.2 measured adaptive allocation

The owner approved completion of the existing 3.x roadmap. This stage adds measured allocation under released and personally accepted CDC 3.1.0. CDC 3.3 follows only after this stage is released and accepted. Fleet rollout and schedulers remain paused.

## Architecture

Add `scripts/adaptive_allocation.py` as a pure recommendation layer over `execution_strategy.evaluate`, `quality_levels.evaluate`, `budget.decide`, and `operation_report.measure`. Retain one integrator and the existing budget. No new scheduler, telemetry store, launch grant, compute provider, or policy migration is introduced. Existing compute cost and platform routing remains authoritative.

`evaluate(request: dict) -> dict` consumes `adaptive-allocation/v1`: `comparison_group`, `strategy` (the complete existing execution-strategy request), `default_profile_id`, `profiles`, and `observations`. Profiles have exactly `id`, `reasoning_effort` (`low`, `medium`, `high`, `xhigh`), nonnegative integer `max_agents`, and `agent_reservations` in the existing strategy format. Each profile's reservations conservatively cover that profile's effort and integration overhead; costs are caller-supplied estimates, not inferred from historical savings. Inline profiles use an empty list. Observations have exactly `profile_id` and `operation` (the existing operation-observation/v1).

Allocation profiles describe execution alternatives for the same work, environment and validation window, identified by the caller's comparison group. The caller retrieves and authenticates the actual observations; the helper cannot attest them. Observation references are globally unique in the request. Other comparison groups are rejected rather than pooled.

## Selection and safeguards

Quality is evaluated first. Any FULL task requires at least `high`; other work requires at least `medium`. The default profile must satisfy that floor. At least two compatible completed measurements are needed for a profile to be selected adaptively. Each must have positive delivered units, known zero escaped defects and measured tokens. Estimated or unknown token values cannot prove savings. A profile with any observed escaped defect is excluded from adaptive selection. Measurements with unknown delivery or defect outcomes are ineligible.

Among eligible profiles, minimize aggregate measured tokens per delivered unit, then elapsed seconds per delivered unit, then reasoning effort, agent count and profile ID. Report the original observation references and measured totals. Reject aggregate overflow and emit strict finite JSON. Do not claim a causal improvement or provider price. With insufficient measurements, use the explicit safe default and explain the fallback. If the default has any observed defect and no eligible measured alternative exists, return WAIT with no agent tasks; unknown tokens or zero delivery never hide an observed defect.

The existing strategy evaluates portable scopes, dependencies, every prospective sequential budget admission and reservation replay. Reevaluate an immutable strategy copy with the selected profile's own reservations and report their event IDs. Preserve any baseline or selected-profile WAIT. Recommend PARALLEL only if that strategy permits it and the selected profile's max_agents covers every independent task; otherwise use SINGLE. Never mutate the input ledger, consume reservations or authorize any start, write, release, takeover or scheduler mutation.

## Evidence and delivery

Tests cover measured selection, sample threshold, unknown/estimated tokens, escaped defects, incompatible groups, duplicate identities, quality floors, budget exhaustion and replay, portable scope conflicts, malformed finite numbers, deterministic ties and input immutability. The JSON CLI uses the same evaluator and fails closed. Ship a runnable template and phase guide, register required package files, then validate a frozen package with bootstrap, FULL, isolated clean consumer, fault inventory, three unchanged archived consumers and ordered independent SPEC then QUALITY review. Mandatory hosted CI remains required. Publication and personal adoption use the existing managed host and strict whole-package acceptance; finalize the real executor before continuing to 3.3.
