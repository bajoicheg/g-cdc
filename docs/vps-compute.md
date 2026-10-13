# Qualified Linux VPS compute

The qualified Linux VPS provides controlled Linux execution through the released
[public Host Bridge interface](https://github.com/bajoicheg/g-cdc/blob/a3193693a1c8747ec8095b4b43c0385b62aa12dc/src/continuous-development-cycle/references/managed-host-bridge.md).
The registered bridge currently supports a read-only pilot and this single
documentation writer. This scope does not authorize general queue or Fleet
activation.

The runtime is root-owned and immutable to task workers. Separate identities
keep responsibilities explicit: `cdchost` runs the controller, `cdcrunner`
handles GitHub transport, and `cdcexec1` executes the assigned work in its
credential-free clone. Executor access does not grant runtime administration,
controller authority, or permission to alter transport configuration.

Execution must use an authentic native lease with the applicable authority and
expected-head checks. A task stays within its authorized budget and records
checkpoints through its original managed lifecycle. The controller must remain
alive through start, observation, and finish. Record actual operation returns;
a requested stop or successful command alone is not proof of physical process
closure. Closure evidence must establish that the processes belonging to that
execution have ended, tied to their original process birth identities.

An `UNKNOWN` result requires recovery through the original handle. Observe and
reconcile that existing execution, retaining its lease, checkpoints, budget,
and closure evidence. Do not replay the command or create a replacement run to
resolve uncertainty. Report unresolved state truthfully until the original
lifecycle provides sufficient evidence for closeout.

This host is qualified for Linux compute. Windows builds require Windows
runners. Schedulers and Fleet remain paused, and this documentation task does
not change authority, runtime versions, scheduling, or main-branch controls.
