# CDC 2.11.1 independent specification review

Reviewed Task 2 at `d7a3c8bf7a75042353230730c21c15c6f4872550`, Task 1 at `30e71fcc1dc242dc389436548f73866f637d8eae`, and parent integration glue at `ef0e2419139d47f321e4e5cab88ae7364a3a1618`. Compared actual code, tests and references with `docs/superpowers/specs/2026-09-28-watchdog-liveness-design.md` and its implementation plan. No full-suite repeat; independent concrete probes used temporary real local Git repositories and recording scheduler only. No live scheduler or external repository effects.

## Verdicts

- Task 2 live target: GREEN, no material specification finding.
- Task 1 runtime/liveness: NOT GREEN, two material findings below.
- Integration guidance/imports: GREEN within reviewed glue; no contradictory authorization discovered. Legacy health remains diagnostic, new liveness is required for recovery, explicit repair-controller capability is distinct from ordinary project wakes. Integrated validator/runtime/target/health import probe passed.
- Combined branch: NOT GREEN until findings are corrected and independently rechecked. This does not claim release, CI, or compatibility gates.

## F1 — Budget/deadline remainder disappears for initially idle invocation

`src/continuous-development-cycle/scripts/fleet_watchdog_runtime.py:310-313,335-339` only preserves continuation for unhealthy assessment or uncertain submitted operations. It ignores an unfinished durable recovery plan. An idle invocation becomes HEALTHY after enable, so the planned run is removed from pending when the batch expires after enable.

Independent reproduction from the Task 1 worktree:

```python
import sys
sys.path.insert(0, 'src/continuous-development-cycle/tests')
import test_fleet_watchdog_runtime as t
x = t.FleetTests(); x.setUp()
try:
    x.backend.live['alpha']['signals']['invocation'].update(state='idle', invocation_id=None)
    result = x.batch(budget=1)
    print(x.backend.effects, result['pending'], result['continuation_required'], result['outcomes'])
finally:
    x.doCleanups()
```

Observed: effects `[('alpha', 'enable')]`; pending `[]`; continuation_required `False`; outcome `batch_budget_exhausted`. Durable recovery still has steps `['enable', 'run']`, with run unclaimed. This violates required durable continuation across wake budget exhaustion. Existing budget test starts from completed invocation, which stays CRITICAL and masks this case. Preserve unfinished eligible recovery plans both during settlement and next-wake checkpoint, including zero budget; honor current explicit pause and project-terminal proof.

## F2 — Coordination read and CAS push can mutate protected product refs

`src/continuous-development-cycle/scripts/git_document_store.py:92,119` inherits configured remote fetch mappings. Constructor protection compares coordination ref names but does not prevent Git's incidental mapping updates. Both fetch and push can update `refs/heads/main` even when it is explicitly in protected_refs.

Independent real-Git reproduction using the same fixture:

```python
revision = x.store.compare_and_swap(None, {'value': 1})
x.git('config', '--unset-all', 'remote.origin.fetch', cwd=x.store.repo)
x.git('config', '--add', 'remote.origin.fetch',
      '+refs/heads/cdc/fleet-state:refs/heads/main', cwd=x.store.repo)
x.store.read()
```

Observed: absent `refs/heads/main` is created at the coordination document commit. The fixture constructs the store with `protected_refs=['refs/heads/main']`.

To isolate the second mechanism, independently monkey-patched only the fetch invocation to add `--refmap=`. `read()` then preserved refs, but `compare_and_swap(revision, {'value':2})` still created `refs/heads/main` at the new coordination commit through push's tracking-ref update. Thus fetch-only correction is insufficient. Both read and push must avoid incidental configured ref mappings while retaining exact endpoint identity and non-force CAS semantics. Violates dedicated coordination/product ref isolation.

## Task 2 evidence

Inspected same-revision registry/optional standalone/required companion reads; independent configured endpoint identity; exact canonical release commit, package tree, VERSION and released evidence; actual candidate ancestry/package equality; final freshness/ref/identity checks; explicit absence of adoption and scheduler authority. Missing legacy companion correctly remains a migration blocker. No mutable version is embedded in the watchdog prompt.

Two additional independent real-Git probes passed: an otherwise valid resolution whose final clock exceeded the 300-second observation window was rejected; a real candidate ancestor with a different package tree was rejected even when current release and registry bindings agreed. These complement actual test/code review without repeating the completed suite.
