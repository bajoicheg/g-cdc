# Offline VPS readiness report

From the repository root, pipe the native status observation into the example:

```sh
/opt/cdc-tools/cdc-vps/bin/cdc-vps status | /opt/cdc-tools/node-v24.21.0/bin/node examples/vps_compute/readiness.mjs
```

From `examples/vps_compute`:

```sh
/opt/cdc-tools/cdc-vps/bin/cdc-vps status | /opt/cdc-tools/node-v24.21.0/bin/node readiness.mjs
```

The status command is run by the operator. The example itself only reads stdin
and writes stdout/stderr. It never executes commands, reads files or credentials,
contacts the network, submits tasks, or changes dispatch or schedulers. Check the
producer's exit status as well as the report command's exit status when using a
shell pipeline.

The accepted document has exactly `revision` (40 hexadecimal characters),
`dispatch_enabled` (boolean), and `tasks` (an object keyed by task ID). Each task
has exactly `state`, `project_id`, `handle_id` (null or a hyphenated hexadecimal
UUID), and `result` (null or an object). Task IDs contain 1–128 ASCII characters,
start with a letter or digit, and otherwise use letters, digits, dots, underscores
or hyphens; `constructor` and `prototype` are reserved. Projects are
`infrastructure`, `g-cdc`, `g-switcher`, `g-pc-health-check`, and `g-ad-control`.
Missing, extra, duplicate (including escaped aliases), unsafe, or wrongly typed
fields are rejected. Input is one UTF-8 JSON document, at most 1 MiB including
whitespace; failures produce diagnostics and a nonzero exit without a report.

The deterministic report preserves the revision and dispatch flag, counts every
registered state (including zeros), and sorts each task ID list:

- Active: `reserved`, `running`, `unknown`, `terminal_pending`.
- Queued: `queued`.
- Unresolved: `unknown`, `retired_unknown`.
- Failed: `failed`, `timed_out`.
- Other terminal observations: `succeeded`, `cancelled`.

`ready_to_accept` is true only when dispatch is enabled and all four lists are
empty. Administrative `retired_unknown` remains visibly unresolved and blocks
readiness; it is never converted into success. Task result objects are observations
and cannot override state or grant authority. A false readiness value is still a
valid report and exits zero; the caller must examine the JSON field.

This is readiness to accept work under the stated observations, not product
acceptance or authorization to submit work. Windows final acceptance remains
required under the existing owner process. The historical PAUSED source-package
task, existing UNKNOWN records, retired contract-generator attempt, and failed
readiness task and its charges remain preserved. This example is independent of
those tasks and does not change any of their outcomes.

For an offline demonstration without invoking the status producer:

```sh
printf '%s\n' '{"revision":"3e5db1acc293e31e6a3b62b95f9ae68407d8132c","dispatch_enabled":true,"tasks":{}}' | /opt/cdc-tools/node-v24.21.0/bin/node examples/vps_compute/readiness.mjs
```

Run the tests using the assigned writable `TMPDIR` (all subprocess fixtures and
regular-file stdin/stdout/stderr live there):

```sh
/opt/cdc-tools/node-v24.21.0/bin/node --test --test-isolation=none examples/vps_compute/test-readiness.mjs
```

The module also exports `summarizeStatus(status)` without mutating its input.
