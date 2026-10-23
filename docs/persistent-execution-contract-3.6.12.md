# Persistent execution contract — CDC 3.6.12 preparation

CDC 3.6.12 is a documentation-only candidate developed under independently
released 3.6.11 (`ec8dd91371db2d193d4a83a4e1612f48f3e1a261`, package tree
`51dc9c7f53af42e374ed81e4d00929c54865d126`). Its common skill entry requires
the [central persistent contract](../src/continuous-development-cycle/references/lean-execution-core.md)
for every CDC-managed project and resumed operation. The user need not restate
ID/UNKNOWN/spent preservation, bounded recovery, evidence reuse, minimum
coordination/checks and concrete result/actual-usage reporting in every task.

The existing project initializer reads `templates/work-status-v4.md`; its
checkpoint body now carries the central reference. Existing projects load the
same contract through SKILL start/resume. The project-setup reference supplies a
compact instruction snippet for managed project adoption. No runtime, schema,
provider eligibility, guard, ledger, daemon or orchestrator is added or changed.
Migration preserves original checkpoint bodies and authority/history bindings.

The contradictory default of two validation cycles is replaced with minimum
sufficient validation; another cycle needs changed inputs or a concrete
uncovered risk and a reason prior proof is insufficient. Each substantive
Russian report reads a fresh Moscow clock; only an exact same-command/report
idempotent retry may suppress a duplicate. Measured numeric counts are separate
from unavailable scope/tokens/money, which stay explicit UNKNOWN with a reason.
App/native/provider observations remain separate; each child is counted once,
cached input and reasoning remain subsets, and cumulative snapshots are not summed.

Runtime algorithms, scripts, tests, schemas, third-party bytes, workflow and
supported-consumer adapter/checkpoint bytes are unchanged. The original
[1801-case hosted success](https://github.com/bajoicheg/g-cdc/actions/runs/39865949109)
and original bootstrap/component proofs retain their original SHA and coverage;
they are reused for unchanged algorithm behavior, not relabeled as 3.6.12 exact
release proof. Local qualification checks only changed document/template and
release-metadata risk. Mandatory exact native Source and release admission
remain required. Preparation alone establishes no public release, installation,
Windows/client adoption or downstream-project application.

All original attempts, IDs, UNKNOWN, reservations, budgets/spent and append-only
history remain intact. Existing provider and pause restrictions remain in force.
