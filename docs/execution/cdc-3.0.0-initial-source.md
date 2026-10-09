# CDC 3.0.0 initial source candidate

Status: source implementation reviewed; not released, installed or adopted.
Branch: cdc/3.0.0-lean-core-20261009. Issue: #101.
Qualified 2.13.0 Cloud fast-start integration remains an external dependency.
Live Fleet rollout is explicitly paused by the owner for this work.

## Source identity and implemented scope

Frozen source commit: ce7e2d0f6d348a36e8b79b633b820acd23cb5f92
Candidate package tree: 6d9183527e7081b947625a88084d1f215b6a1070
Independent driver: verified 2.12.1, 352 byte-identical files, exact witness in
release/development-driver-2.12.1.json. Candidate metadata and archived snapshot
candidate identities bind this actual source/package. Snapshot product/source
identities, policy version ceilings, histories and live consumers are unchanged.

Implemented: compact core (8146 to 908 words before source identity adjustment),
phase routing and byte-preserved historical core; read-only cdc resume/assess/
report/strategy commands; composed quality/cycle/reuse gates; selective TDD and
batching recommendations; disjoint portable scope and sequential existing-budget
admission; rounded Russian operation reports with unknown tokens omitted;
phase/delivery observations and comparable observed deltas; package fixtures
that execute actual contracts; consolidated phrase-only tests with coverage map.

## Observed verification and review

Initial aggregate candidate suite at local source SHA
14c409aa1bdec9cdf8ca298049070110773b97f8: 1109 tests, command exit 0,
330.966 seconds. This is original local evidence, not a CI or final-SHA claim.
The same initial bootstrap test command had 46 tests and one real failure:
old candidate/snapshot package binding. That failure drove the source identity
rebinding rather than being ignored or relabelled GREEN. Initial bootstrap
full mode and package parser passed. Subsequent code changes receive scoped
verification; unchanged behavior coverage remains attributed to its original
source SHA, never relabelled as a new full run.

Independent review found two Important and one Minor issue. Regression RED
reproduced intra-request reservation replay, portable path aliases and loss of
a known token endpoint. Fixes now reuse existing portable scope rules, require
unique admissions, guard simulation replay and retain observation provenance.
Independent scoped re-review: no remaining findings; 17 focused tests and
boundary experiments passed. Stable-major source/candidate validators were
verified with additional RED/GREEN coverage for exactly next major at zero
minor/patch, skipped majors, invalid base identity and same-driver rejection.

## Remaining qualification and next action

1. Published source readback matched every tracked byte. After fixes, 51
   independent bootstrap tests and 111 focused core/package/template/version
   tests passed locally. These observations are not final CI or a second full
   candidate run. Final narrow independent review had no new findings.
2. Integrate the qualified 2.13 Cloud fast-start source once available; do not
   copy an unqualified scratch snapshot or duplicate its transport.
3. Complete final exact-candidate CI, clean consumer-layout and archived-consumer
   qualification plus required ordered release reviews. Existing archived/live
   policies with an exclusive 3.0.0 ceiling correctly reject installation of
   3.0.0. This is a real compatibility/migration gate, not permission to widen
   their policy or deploy. Metadata binding is not a consumer GREEN result.
4. Release/install/adopt only through their separate gates. Live Fleet rollout
   stays paused until the owner changes that instruction.

No PR is opened at this initial boundary: its workflow starts the final release
validation automatically, while Cloud integration and old consumer version
ceilings remain known prerequisites. The isolated source branch is the durable
reviewable result. Next dependency action: observe the qualified 2.13 source
release identity, reconcile its actual diff and integrate into this branch,
then freeze a new candidate and run the remaining required qualification.
