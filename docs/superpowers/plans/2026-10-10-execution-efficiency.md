# Execution Efficiency Implementation Plan

> For agentic workers: implement inline with executing-plans; one ordered independent SPEC and distinct QUALITY review at the frozen critical candidate boundary.

**Goal:** Make issue101 economics apply to actual execution rather than advice alone.
**Architecture:** Extend the check runner and existing cdc/evidence/metrics gates; add bounded read-only adapters, no second control plane.
**Tech Stack:** Python standard library, existing CDC validators and Git evidence.
**Spec:** ../specs/2026-10-10-execution-efficiency-design.md

## Global constraints

Develop under actual released3.3.1; target3.4.0. Preserve original UNKNOWN/no-replay, budgets, platform gates, historical records and paused schedulers. Reuse evidence only for covered inputs; one hosted frozen FULL, no local duplicate. No implementation subagents for these coupled interfaces.

## Review focus

Corrupt/replaced receipt cannot be PASS; changed relevant files invalidate reuse; exact-candidate checks cannot move SHA; multibyte output obeys byte limit; terminal state cannot replace actual physical process absence.

## Tasks

- [ ] Add focused failing runner reuse and bounded-context regressions.
- [ ] Implement verification_economics.py and integrate command-check-plan/v2 in run_checks.py before subprocess spawning, retaining v1 behavior.
- [ ] Add bounded evidence/runtime/terminal helpers and expose through existing cdc.py; actual risk selection and bounded observation reuse existing controls.
- [ ] Extend existing operation metrics, add test audit and concise canonical instructions/current state/history archive; retain full audit provenance.
- [ ] Run affected tests and meaningful real subprocess/cold-warm probes once; refresh version/package/source contracts and review exact candidate.
- [ ] Deliver one native managed source release with one required hosted FULL, save/install exact personal package and independently accept actual exit/physical closure. Update issue101 with proven versus pending outcomes.
