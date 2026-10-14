# VPS development branch

This branch starts the owner-authorized CDC VPS integration scope. It preserves
the released CDC3.5.4 package, release branches and the completed source task
documented in AGENTS.md. Only examples and documentation are writer scope.

The released runtime at `/opt/cdc-tools/cdc-3.5.4` owns execution. The private
coordination repository is `bajoicheg/codex-compute`; the canonical lease is
`refs/heads/cdc/vps-production/g-cdc/lease`. The production adapter grants
registered tasks through its native bridge, pool, budget and intent contracts.
Generated Cloud profiles remain UNCONFIGURED and grant no execution authority.
The former unconfigured profile template is preserved byte-for-byte in
`docs/history/vps-initial-cloud-profile.json`.

The first code task supplies a JavaScript portable task-contract builder and Node test checks in
`examples/vps_compute`. It does not change the runtime package or authorize
Windows product acceptance. Before that task the generated example-test command
is preparatory: the example directory does not exist yet. Python source placement remains unchanged; the example uses `.mjs` files.
The registered final check is `diff-check`; the implementation and both independent
reviews must also inspect actual successful Node test evidence. Setup validation uses
the native adapter and checkpoint validators and Git whitespace checks.

The independent offline readiness-report example is documented in
`examples/vps_compute/readiness-README.md`. Pipe native `cdc-vps status` JSON into
`readiness.mjs` to obtain deterministic counts and readiness observations; run
`/opt/cdc-tools/node-v24.21.0/bin/node --test --test-isolation=none examples/vps_compute/test-readiness.mjs`
for its checks. Administrative `retired_unknown` remains unresolved and blocks
readiness. This example preserves the historical PAUSED source-package scope,
UNKNOWN records, retired contract-generator attempt, and failed readiness task
and its charges; it grants no scheduler authority or Windows final acceptance.
