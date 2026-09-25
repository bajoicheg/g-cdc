---
schema: development-work-status/v4
repository: bajoicheg-private/g-supervisor
branch: design/0.1.0-android-local-first
policy_revision: 2026-09-25-cdc-2.7.1-owner-ux-corrective
policy_digest: cdc-2.7.1-release-8e97192ef89bf37657a4444a954530f22e8b2267
observed_at_utc: '2026-09-25T17:36:27.234Z'
orchestration_origin: chat
active_executor: none
lease_state: released
executor_heartbeat_at_utc: null
execution_lease_until_utc: null
waiting_external_kind: null
waiting_external_id: null
waiting_external_sha: null
operation_intent_ref: null
operation_key: null
resume_capsule_ref: 'https://github.com/bajoicheg-private/g-supervisor/blob/cdc/coordination/resume.json'
execution_continuity:
  invocation_id: null
  runnable_next_action: false
  meaningful_progress: true
  primitive_steps_since_progress: 0
  completion_gate: fresh_wake_exact_sha_android_gate
  last_progress_ref: 'product:0e920f63c474c9eaf6ec6377f9a65727d434142a-events-scroll-reachable'
control:
  execution_lease_ref: https://api.github.com/repos/bajoicheg-private/g-supervisor/contents/lease.json?ref=cdc%2Fcoordination
  execution_lease_revision: 'f27bae65b60e25637ee1a5d53cff9f67f5b55bdd'
  executor_id: null
  lease_generation: 64
  budget_ref: https://github.com/bajoicheg-private/g-supervisor/blob/cdc/coordination/budget.json
  recovery_snapshot_ref: null
  external_wait_ref: null
active_change: D6-executive-ui
current_task: 'D6 Task 6: real cached Events — corrective candidate ready for fresh-wake gate'
phase: validation
implementation_sha: 0e920f63c474c9eaf6ec6377f9a65727d434142a
candidate_sha: 0e920f63c474c9eaf6ec6377f9a65727d434142a
last_green_sha: a2b6297f80fe8b6e6866191ea70afe0a9a805f52
last_green_evidence: docs/validation/D6-task5-owner-ux-green.json
active_compute: none
active_ci_run_id: ''
last_ci_run_id: '36166189120'
last_ci_status: failure
release_version: 0.1.0
release_candidate_sha: ''
release_state: not-started
blocker: 'Current wake consumed its single baseline Actions start. Corrective candidate 0e920f63... is ready but requires a fresh-wake exact-SHA Android gate before Task 6 can be called GREEN.'
next_action: 'On the next CDC wake, acquire a fresh lease and spend at most its one baseline Actions start on exact SHA 0e920f63c474c9eaf6ec6377f9a65727d434142a. Do not change product code unless that gate finds a new defect.'
---

## D6 Task 6 runtime RED corrected — 2026-09-25

Task 6 now renders only persisted cached events from Room-backed `ProjectEvent` data. The presentation layer deduplicates stable provider identities, orders facts by occurrence time with observation time kept separate, maps project/source/error provenance, preserves cached facts when a source is currently failing, and exposes only validated `https://github.com` source links. The Events UI includes truthful empty/offline states, source-error surfaces, occurred/observed timestamps plus age, 48dp source actions, TalkBack labels and long-text wrapping.

Exact candidate `0954a762f348192f47e6f1e1e55f24eb90a462cf` ran once in Actions run `36166189120`. Exact-SHA/policy checks, Android SDK setup, unit tests, lint, debug APK assembly, Android-test compilation and emulator boot all passed. Instrumentation executed 56 tests: 55 passed and exactly one failed. The failure was `D6EventsUiTest.longTitleRemainsReachableAtTwoHundredPercentFontWithTalkBackSourceAction`: at 200% font the correctly labelled source button was below the initial LazyColumn viewport, while the test incorrectly required it to be immediately displayed.

Artifact `10878410650` has digest `sha256:58a0c082d108c4d552c7581d58c7da9b42824aa6f445774f7015884a2668fb16`. Corrective commit `0e920f63c474c9eaf6ec6377f9a65727d434142a` changes the accessibility test to `performScrollTo()` before display/click assertions, preserving the product UI and testing the intended requirement: the TalkBack-labelled action remains reachable at 200% font. The current wake's single Actions grant is consumed, so no second run is legal. Task 6 is not claimed GREEN until a fresh-wake exact-SHA Android gate passes the corrective candidate.

## D6 Task 5 owner UX corrective GREEN — 2026-09-25

Owner feedback from PR comment `5832606658` is implemented and validated on exact SHA `a2b6297f80fe8b6e6866191ea70afe0a9a805f52`, Actions run `36162909212`.

Projects is now a compact high-level card dashboard. Search/account filtering/manual refresh/background-check information and About (`G-Supervisor 0.1.0`, `V.Vasilev 2026 ©`) live behind the small project-settings gear. The persistent shield/title header is removed. Project cards open on card tap and use a compact pin icon instead of full-width Open/Pin buttons. The redundant stale-data sentence and literal `Источник:` prefix are removed. Settings no longer exposes appearance selection and the app follows Android system theme; verbose OAuth/delete explanatory clutter was removed.

The reported search defect `first → irstf` is corrected with local `TextFieldValue` cursor state and asynchronous persistence. Run `36156655029` independently proved production `EditableText='first'` and cursor `TextRange(5,5)`; its only RED was a test-contract misuse of `assertTextEquals`, which merges the field label with editable text. Candidate `a2b6297f...` asserts `SemanticsProperties.EditableText` directly.

Final GREEN evidence: domain 93/93, app JVM 122/122, instrumentation 53/53, emulator, D6 persistence, scheduler/Doze, clean install, cold launch and final evidence gate all pass. Artifact `10877460007` digest `sha256:9294e28bd7fa1e908f8c2fa6c80efc86e1ecced633a8733dc79196d61ba6ead0`. APK size 20,783,008 bytes; SHA-256 `5e91c1a15db7337a935d76de288cbc884b20e7c7e23ccdd1d612f4de893b21c2`; debug certificate SHA-256 `0f818f8a1106441391722c32c9ed3744804aae4b6eb7886036638dad6ece9d49`.

## D6 Task 5 GREEN — 2026-09-25

Exact candidate `0c5d0a03a98f04a681f12450844af0d6398e26e6` passed GitHub Actions run `36131221292`. Exact-SHA/policy checks, Android SDK setup, domain/app JVM tests, lint, debug APK assembly, emulator boot, 53/53 instrumentation tests, D6 persistence, WorkManager/Doze evidence, clean install/cold launch and final evidence validation all passed with zero failures/errors/skips.

Artifact `10862946311` (`android-d6-evidence-0c5d0a03a98f04a681f12450844af0d6398e26e6`) has digest `sha256:d15fd0633521eb351072d26900fa2c401e3fff8810af6c16fad55639f3006a5f`. The validated debug APK is 20,783,008 bytes, SHA-256 `3527a3463f9d81f696e37c92f02945492074adbd6e73bebdeca62f4753d6ed92`, signed by the Android debug certificate SHA-256 `7c85fd17a932616dc1eba467d4b1eafb112ec7c319cc64fd4089465fd8184ad8`.

Task 5 acceptance is closed. Task 6 is the next sequential D6 slice and was intentionally not started because this invocation's requested scope ended at a verified APK.

## Ownership recovery and Task 5 device RED — 2026-09-25

Generation 58 was not merely expired: coordination commit `56fa75d5d409e19356f7b72b521ff06c021d2b38` acquired an `execution-lease/v2` record by patching only legacy owner/generation/timestamp fields, leaving mandatory `invocation` and `finalization` null. The stale external guard also still described Actions run `36118401656` as running after GitHub had made it terminal failure. PR evidence comment `5830980337` records the RCA. Attempt 066 and its budget reservation were reconciled terminal; generation 59 was then acquired as a valid invocation-bound v2 owner with the old invocation independently established stopped and external effects reconciled.

Run `36118401656` had failed only at Android-test compilation because `D6ProjectNavigationUiTest.kt` imported `androidx.compose.ui.test.assertDoesNotExist` as a top-level symbol. Candidate `2ca12efe724f22f1a2219561ef61dfda13d41a3c` removed that invalid import. New run `36125095860` proved exact-SHA policy, unit tests, lint, debug APK and emulator GREEN and ran all 53 instrumentation tests. Exactly one test failed: `cachedDetailsRemainVisibleOfflineWithSourceAge`, because the provenance/source timestamp existed in Overview but was below the four section controls and therefore not displayed in the offline viewport. Artifact `10860420052` has digest `sha256:cbd1b5ae3b24857915be8c521b20974f9a6b4717e635c8de1336aba2234f4d81`.

Corrective commit `4894c1f79ceffe12058bd6d487a026e014276510` keeps offline provenance/source age immediately visible before the section controls and records a repository-level fail-closed rule forbidding v1-style direct ownership-field patches in a v2 lease. It uses `[skip ci]` because this wake's one Actions start was consumed. No Task 5 GREEN is claimed until a fresh-wake exact-SHA Android gate passes.

## D6 Task 5 preflight RED and correction — 2026-09-25

Task 5 source work is present: real project cards now expose enabled Open and pin controls; Projects overview uses the Task 4 presentation model with persisted search/account-filter/pin state; details navigation is keyed by repositoryId; details expose Overview/History/Technical/Actions, cached offline source timestamps and only a validated GitHub URL action; no ChatGPT/D8 action or demo fixture was added to production runtime. Compose RED coverage is `D6ProjectNavigationUiTest` with three tests for enabled routing, long names at 200% font/TalkBack pin semantics, safe D6 actions and offline cached details.

Exact candidate `5aca51659690b2c1a489877097a8f84719ca3f52` started Actions run `36116655431`. Checkout, JDK and exact SHA passed. The mandatory policy/tooling preflight then failed in `tools/tests/test_android_evidence.py`: the workflow correctly requires 53 instrumentation tests and `D6ProjectNavigationUiTest`, but two negative-test fixtures still synthesized 50 tests, so their intended missing-class/failure assertions were masked by the earlier count assertion. Android SDK, Gradle, emulator, product tests and instrumentation did not run.

Artifact `10855620268` has digest `sha256:3c6486d1699f0af6f0b5a4115045c1c3da853d085027edb846f540d8c29df4da`. Corrective commit `8cda46deb5d4d79d5dbebffb7e3a0dd49b608f33` changes the remaining fixtures from 50 to 53 and the incomplete fixture from 49 to 52; the durable failure-circuit remedy is `product:8cda46deb5d4d79d5dbebffb7e3a0dd49b608f33-task5-evidence-fixture-53`. No second Actions start was made in this wake.

## D6 Task 4 GREEN — 2026-09-25

Exact candidate `7dbea6386cb6be166f4eaeae99aa8ec670d02331` passed GitHub Actions run `36111041100`: 93/93 domain tests, 122/122 app JVM tests, lint, APK assembly, emulator boot, 50/50 instrumentation tests, D6 persistence, WorkManager/Doze evidence, clean install, cold launch and final evidence validation. All failures/errors/skips were zero.

The preceding exact candidate `10fb5587dabf3a58aa61e9849ebbec7793654fab` failed only at `:app:compileDebugKotlin` because Task 4 began importing `:core:domain` without an app module dependency. Candidate `7dbea6386cb6be166f4eaeae99aa8ec670d02331` adds `implementation(project(":core:domain"))`; the owner one-shot +1 Actions grant was consumed exactly once for that corrected gate.

Artifact `10853407089` has digest `sha256:c0fa44ff41668f4f4a1be01a28176bfb59e41fdea78ca74f60a6530985e4f535`. APK SHA-256 is `c86a6086346a7e88222ba18e6a35a80141c26b888e02fc9923222a4d084d6e23`; debug certificate SHA-256 is `8ec58ab98ff6c69b2561e5de3cddbd72113bfe7f692d015a3e71311275e2f8ad`.

Task 4 acceptance is closed. Task 5 is now the sequential active slice.



## D6 Task 4 gate blocked by canonical budget-ledger validation — 2026-09-25

The current wake built unpublished candidate `f8d49dbdb6f353a90214cc75bdcbc0fe560c311c` from source HEAD `3c32c9b1ce21c4bfd9b3393049f92940972e0346`, containing only the path-matching workflow trigger comment for the already committed 93-test fixture correction. Before moving the source ref, the required canonical command `python3 -B tools/project_budget.py validate --ledger budget.json` failed on the live append-only ledger at historical event `android-d6-status-red-052` with `recovery_ref has no matching failure circuit`.

No submission claim was consumed, the source ref remained at `3c32c9b1ce21c4bfd9b3393049f92940972e0346`, GitHub reported zero workflow runs and zero statuses for the unpublished candidate, and no Actions capacity was spent. Intent `d6-presentation-green-061` was durably transitioned to terminal/cancelled and the external guard was reconciled and cleared in coordination commit `c921e2ab6368fc0a1f691ea836dc9023ea605a12`.

The next wake must repair and regression-test the project budget adapter/ledger compatibility without rewriting historical events or weakening the preserved failure circuits. After the complete canonical ledger validates, create a fresh candidate from the then-current source HEAD and start one new exact-SHA Android gate. Do not rerun run `36095130165` and do not publish the dangling candidate.

## D6 Task 4 GREEN gate tooling-fixture diagnosis — 2026-09-25

Exact-SHA Actions run [36095130165](https://github.com/bajoicheg-private/g-supervisor/actions/runs/36095130165) executed once on candidate `29c7a6f895999bc86763f8d0e2f092fdf0e117dd`. Checkout, exact SHA and JDK 17 passed. The policy/tooling preflight then stopped before Android SDK, Gradle, emulator or production tests because `tools/tests/test_android_evidence.py` still generated a synthetic 86-test domain report while the workflow correctly required 93 after Task 4 added seven tests. The 13 reported failures shared this same first assertion; they are not 13 independent defects.

Artifact `10846862559` has digest `sha256:bb2fddb99938e0b29c70ab22485daede6416fe3271fc0e34ab66fbc95652c608`. Commit `f85fba6dd565fe4edc7514372aab056ac1c990f9` changes only the synthetic domain fixture from 86 to 93 and uses `[skip ci]` because this wake's single Actions start was consumed. No GREEN is claimed.

The next wake must start one fresh exact-SHA gate for `f85fba6dd565fe4edc7514372aab056ac1c990f9`; run `36095130165` must not be rerun.

## D6 Task 4 corrected RED and minimal implementation — 2026-09-25

Exact-SHA Actions run [36093130960](https://github.com/bajoicheg-private/g-supervisor/actions/runs/36093130960) validated candidate `ad9785f7e133a6874e21eeb55e158f9e1d29a370`. Policy/SHA checks, JDK 17 and Android SDK setup passed; `:core:domain` compilation then failed exactly on the absent `ExecutiveProgressEvidence`, `ExecutiveStatusInput` and `mapExecutiveStatus` contracts. This is the intended tests-first RED; emulator and instrumentation were not run. Artifact `10846552031`, digest `sha256:b01f65f772a74480047372d8c9cd72988ee43c3e0a673d4837655109a65a27fd`.

Commit `9efaa6a0c7dc766d1d5eaaefe07d65f7bdd4548d` adds the minimal domain mapping: stale/incomplete evidence maps to UNKNOWN and suppresses progress; required current check failure maps to BLOCKED; optional failure or inactivity maps to ATTENTION; unsupported progress is omitted; supported progress preserves its explicit source URL/label and observation timestamp. The commit is `[skip ci]` because this wake's single Actions start was consumed by the RED gate. No GREEN is claimed.

The next fresh wake must change the workflow's expected domain-test total from 86 to 93 in one non-skip commit based on the implementation and run one exact-SHA gate. Do not rerun `36093130960`.

## D6 Task 4 corrected RED trigger produced no Actions run — 2026-09-25

Exact candidate `acdc38e5128d8819ccc446153bcceaed79e14f0e` was published only after fresh capability routing, budget reservation, durable intent/readback, external guard and one-use submission claim. GitHub then reported zero workflow runs, zero check suites and zero check runs for that SHA. The commit has the same tree as its parent, while `.github/workflows/android.yml` is path-filtered, so the push did not start Actions.

The no-effect submission was reconciled as terminal cancelled and the external guard was cleared. No GitHub Actions job started, but this wake's durable reservation is closed and no second attempt is made. The corrected domain RED remains unobserved. The next wake must create one path-matching non-skip validation trigger (or use a real workflow-dispatch capability) and require failure on the absent `ExecutiveStatusInput`, `ExecutiveProgressEvidence` and `mapExecutiveStatus` contracts before any production implementation.


## D6 Task 3 exact-SHA GREEN and closure — 2026-09-25

Exact-SHA Actions run [36083345234](https://github.com/bajoicheg-private/g-supervisor/actions/runs/36083345234) completed successfully on candidate `62b8ab05bf8946c87bec8bc98953fe1570c20443`. Policy/SHA checks, JDK 17, Android SDK, 86/86 domain tests, 115/115 app JVM tests, lint, APK assembly, emulator, 50/50 instrumentation tests, scheduler/Doze evidence, clean install and cold launch all passed with zero failures, errors or skips.

The gate includes the bounded parser plus default-branch raw status fetch, typed optional HTTP 404 handling without reading the error body, safe fixed failure mapping, Room goal/source-state persistence, missing-source isolation that preserves provider facts, and token/Authorization persistence guards. Artifact `10843531301` is bound to the candidate with digest `sha256:c72cd40efbd42266a1e140383c2cab4162021628663404a0e219b2ae54df30b1`.

The debug APK is 20,701,029 bytes with SHA-256 `1fe2e4d3b506b9c952fedb0db9c8ab8f5f3957c1f2c673b120e2369055be6f1f`; debug certificate SHA-256 is `57baedba26b6df79c4931243b05573f887bb8fabd6be5e55ed635f78ae1d499d`. This closes D6 Task 3. The next sequential slice is Task 4 truthful presentation mapping.



## D6 Task 3 optional status source RED and implementation — 2026-09-25

Exact-SHA Actions run [36081160336](https://github.com/bajoicheg-private/g-supervisor/actions/runs/36081160336) validated tests-first candidate `902a20426cd9909f1f4f3cde95b7d97c0738be32`. Policy/SHA checks and Android SDK setup passed; `:app:compileDebugUnitTestKotlin` then failed on the intentionally absent `GitHubStatusSourceResult`, `fetchStatusDocument`, `STATUS_SOURCE` and `OptionalMissing` contracts. This is expected RED evidence, not product GREEN.

Commit `a4e9de15ab7f1be7ca0eb74f50e422715c7978db` adds a default-branch raw status fetch bounded to 64 KiB, typed optional HTTP 404 handling without reading the error body, safe fixed failure mapping, parser integration, Room goal/source-state persistence, and missing-source isolation that preserves provider facts. The commit uses `[skip ci]` because this wake's one Actions start was consumed; no second run was created.

Static review matched the existing Room entity/DAO and all known transport/store implementations, and GitHub reports no workflow run for the skip-ci implementation commit. This is review evidence only. Compilation, JVM tests, lint, APK, emulator and instrumentation remain unverified for this implementation until a fresh-wake exact-SHA gate.


## D6 Task 3 bounded parser exact-SHA GREEN — 2026-09-25

Exact-SHA Actions run [36078457100](https://github.com/bajoicheg-private/g-supervisor/actions/runs/36078457100) completed successfully on candidate `ca954f694c4fbea345f360f105ffc9d7ad6a8fc4`. Policy/SHA checks, JDK 17, Android SDK, 86/86 domain tests, 113/113 app JVM tests, lint, APK assembly, emulator, 50/50 instrumentation tests, WorkManager/Doze evidence, clean install and cold launch all passed with zero failures, errors or skips.

Artifact `10841158484` is bound to the candidate and has digest `sha256:ac7dee43fd8725329909cb30c7b1c729ff33bd5fb1cb23c375586fb45f1a9cab`. The debug APK is 20,684,645 bytes with SHA-256 `30ed7826ed8a584c54b5742c32fe6d81cd0c59605c3333708a268edbe17de220`; debug certificate SHA-256 is `0c7e72c44e7f371ee2232352455eba66ee3d3305f030b035f84ec352b8999afe`.

This closes the bounded parser sub-slice: strict UTF-8/JSON/version/time/type handling, 64 KiB limit, bounded fields, sourced progress and same-repository HTTPS evidence links are platform GREEN. Task 3 remains open for default-branch transport, optional missing-file handling and persistence/source-state isolation. This wake used its single Actions start; no second run was launched. The next wake starts with tests-first RED for HTTP 404/missing status and store behavior.


## D6 Task 3 parser gate 053 and test-contract correction — 2026-09-24

Exact-SHA Actions run [36073398208](https://github.com/bajoicheg-private/g-supervisor/actions/runs/36073398208) on candidate `a025144a72476ecbfbea4dfb8135354fd950be19` passed policy/SHA checks, JDK 17 and Android SDK setup, then ran 113 app JVM tests. One test failed: `GitHubStatusDocumentParserTest.validV1PayloadProducesOnlyDocumentedBoundedFields`; emulator, instrumentation and final platform evidence were therefore not run. Artifact `10839890269` has digest `sha256:4145d20f5f9f5bb4f724ee278c0862342d68ecc8e3b83d4eb4fe909098039623`.

RCA confirmed production parsing was correct: `2026-09-24T12:00:00Z` equals `1_790_251_200_000` ms. The tests-first RED candidate had expected `1_790_164_800_000`, exactly one day earlier, but compilation RED had previously prevented this assertion from executing. Commit `b478a05476e0f0775b968ee3f3b5005c3137fb06` changes only that stale expected value and is `[skip ci]` because the wake's single Actions start is consumed. No second run was started; Task 3 GREEN remains pending for the next wake.

## D6 Task 3 parser RED and bounded implementation — 2026-09-24

Exact-SHA Actions run [36067724675](https://github.com/bajoicheg-private/g-supervisor/actions/runs/36067724675) validated the tests-first RED candidate `86636fd6beae69a9e1532462ece05af7ae2d18c8`. Policy/SHA checks and Android SDK setup passed; `:app:compileDebugUnitTestKotlin` then failed on the intentionally missing `GitHubStatusDocumentParser` contract. This is RED evidence, not product GREEN.

Commit `556f109f88509b58a9e0645649ec27f3455b42d8` adds the bounded parser implementation with strict UTF-8/JSON handling, 64 KiB enforcement, version/type/time validation, fixed safe error reasons, bounded display fields, sourced progress validation and same-repository HTTPS evidence links. It is `[skip ci]` because this wake's one Actions start is consumed. Missing-file transport and Room persistence/source-state tests remain open; Task 3 is not complete.

## D6 Task 2 exact-SHA GREEN — 2026-09-24

Run [36064408233](https://github.com/bajoicheg-private/g-supervisor/actions/runs/36064408233) completed successfully on exact candidate `565f9fde017444df30c621c9976d59ff787de1ed`: 86/86 domain tests, 107/107 app JVM tests, 50/50 instrumentation tests, lint, APK assembly, emulator, D6 persistence, WorkManager/Doze evidence, clean install, cold launch and final evidence validation all GREEN.

Artifact `10836401326` contains 176 files (20,846,389 bytes) and is bound to the candidate with digest `sha256:9962f8abf059b0d7ac20e15df9640fa2ab7974e00dafcc364d6c0236a7aac433`. Scheduler evidence preserves the same WorkSpec UUID across process recreation and confirms registration before idle, during idle and after bounded post-recreation polling; it does not claim exact 15-minute, force-stopped or forced-idle execution.

This closes D6 Task 2, including bounded pagination/ETag/304 cache behavior, revoked-account and rate-limit semantics, partial-source isolation and dedup coverage. D6 as a whole remains open. The next sequential item is Task 3: parse optional `docs/supervisor/status.json` as bounded untrusted evidence.

The project budget validator now also binds the immutable 194-event/42-wake audited continuity prefix and applies current strict policy to every later event. The live ledger, 14/14 budget tests and the exact-SHA gate are GREEN without rewriting historical charges.

## CDC 2.6 policy adoption — 2026-09-24

Canonical package commit `0c091db46ee33a6e0725ea72cc78ad553a1839e1`, package tree `8039853dfec23e4ed722223c4cf3dec3688c0433`, external validation run `36051402864`: package validator PASS, 233/233 tests PASS, adapter/checkpoint PASS. D6 product candidate/evidence/blocker below are preserved.

# CDC 2.5 policy binding GREEN — 2026-09-24

Exact policy HEAD `e7fb11f2e053b663b1ee94f47c278b853fff5f84` passed CDC package validation, 211/211 CDC tests and project adapter/checkpoint validation in run `36044416973`. Semantic policy digest is `c96e0f71890aebbc0592c2ae326dac5f5b6d5bbc0a1fed7e2662f8b2a0616a42`. Product implementation/candidate/GREEN evidence below is preserved unchanged; this policy run is not Android product evidence.

## D6 Task 2 corrective handoff — 2026-09-24

Run `36022730438` on exact SHA `b87a282f2154cd3c311c6e814525a6cd0a2cfab6` restored and passed the complete Android D6 gate: domain 86/86, app JVM 103/103, instrumentation 50/50, emulator, D6 persistence, scheduler/Doze, clean install, cold launch and final evidence validation all GREEN. Artifact `10819071230` has digest `sha256:8b60fee778863f3e60fea4664e57164b912e2130e3e8ddaa6f192d59b4db4d72`; APK is 20,684,645 bytes with SHA-256 `34b90d561efdee8d4b70dd19857a56bcc34fe6f47f0e6f5a09a8b5fcaebb9bab` and debug certificate SHA-256 `64417d9a6265ee80a0bd4aa1daebe384081cb1e93fb6f8d8802c1e55a65d4a29`.

This GREEN closes the previously pending Task 1 platform evidence because `D6ExecutivePersistenceTest` ran inside the 50/50 instrumentation suite and the later Task 2 corrective commits do not touch Task 1 persistence/migration files.

A semantic Task 2 review found one real acceptance gap after that run: `GitHubHttpExecutiveTransport` recognized HTTP 304 but never sent `If-None-Match` and never followed bounded pagination. Tests-first correction is now:
- `b2fb3088fc8abdea39672b7a66463b0d10abb53a` — RED ETag/pagination contract;
- `3cc069f778819fdc2faa68b390ac523f497aa295` — bounded three-page pagination, endpoint pinning, in-memory page ETag/cache preservation and 304 reconstruction;
- `2aa999d7911d71a9fbea874a64a6ef7d67e79a51` — explicit 403/429 semantics;
- `e788bd78b6574b2a77cd858c0a0845d58c2fcd4c` — account rate-limit fallback and stable check-history contract.

These commits are `[skip ci]`; they are not covered by run `36022730438`. The current wake's one Actions start is consumed, so Task 2 is deliberately NOT declared GREEN. Sequential Task 3 remains blocked until a fresh-wake exact-SHA gate validates the corrective tree.

## D6 exact-SHA gate 35997505567 — 2026-09-24

Exact candidate `13c2c036145c6b2553d74ed0895c8bc4c873ad7d` completed the build, 86/86 domain tests, 103/103 app JVM tests, lint, APK assembly, emulator boot, 50/50 instrumentation tests, D6 persistence checks, WorkManager/Doze evidence, clean install and cold launch. All reported failures, errors and skips were zero.

The required workflow nevertheless concluded failure because its inline evidence contract still asserts exactly 101 app JVM tests. The observed total is 103 after the two new HTTP 304/cache-preservation tests. Android GREEN is therefore not declared until a fresh exact-SHA workflow run passes the corrected coherent gate.

Artifact `10807019531` contains the debug APK (20,684,645 bytes, SHA-256 `34ad5df2571e50bdde56fb33232ad12bbd9c65921b14f91988c82910964f11a5`; debug certificate SHA-256 `c8c716405df5564e9000595a10111220027082cf26fb0dda0d55082cfee53237`). One Actions start was consumed in this wake; no retry or second run was started.



## CDC 2.3.7 watchdog health GREEN — 2026-09-24

Exact candidate `6877295ad3b9052b70281a3ee95b86e457d630cc` passed
166/166 vendored CDC tests (including 10/10 watchdog-health tests), package
validation for 53 files/templates, 49/49 project tooling tests, strict adapter
validation and checkpoint validation. Evidence: PR #1 comment 5809317675.

The canonical watchdog prompt was updated in place to require the six-signal
health vector and final-response lease release. The first live control-plane
snapshot is `cdc/coordination/health.json`. At 2026-09-24T06:57:59Z it classified
the watchdog as `STALLED / diagnose_scheduler_delivery`: the canonical recurring
task was enabled, but its last observed run at 05:10:55Z exceeded the project's
75-minute overdue threshold. Current foreground lease and progress were fresh,
the CDC health compute was terminal/reconciled, and fresh bound-chat access was
not established, so chat remains `unknown`. The health result is diagnostic and
does not grant any takeover/write/start authority.

# G-Supervisor — Android boot continuation

Current source policy dfcce42 was reconciled without overwriting its adoption. Canonical coordination is `cdc/coordination`; prior adoption owner explicitly released. Root acquired generation 2. The competing pre-adoption `cdc-coordination` ref is released and historical only. Original ledger retains seven terminal compute submissions and three completed agents from the earlier wake; unknown older usage is not zero. Original accounting ceilings are retained for historical replay; each new admission must additionally satisfy current adapter limits.

D4 remains closed at75af727ea110b17c3984f3e8f930ae80c6930744. D5 remains open, D6 unstarted. Prior Android automated GREEN467cf278794d0ada2611006724e74c5e36114b21 and compute GREEN0f50b9107280d0051c7d5c8f663fb18e6d11091d retain their original evidence scopes. No new APK is delivered. Full pre-adoption history is archived under docs/work-status/archive/cdc-v2-c05f6f0/.

Prepared helper/bootstrap passed16 subprocess checks and independent9-test review. Reviewed helper/setup hashes still match; no repeated JVM or Gradle verification. Dedicated environment6ab2af0fed688191bab2dbc8e58d1218 has universal image, empty maintenance, agent internet off, exact reviewed setup and three JAVA_HOME/ANDROID_HOME/ANDROID_SDK_ROOT variables read back after runtime reconnect. Config/plan/preflight are archived under docs/validation/codex-android-boot/. Actual SDK install/boot remains NOT_RUN. The interrupted previous wake submitted no task.

This diagnostic checks API35x86_64 software boot, actual guest shell response and exact clean source with900s boot bound. It does not replace48 normal instrumentation +2 scheduler probes, Doze/install/upgrade/OAuth/signature or owner phone acceptance. Actions remains exhausted. The existing watchdog is resumed, but that does not authorize this external start. Prepared D5-final-gate-counts.patch is not applied.

Historical tool-transport ceiling for this wake was100 calls for this recovery/publication/intent experiment because the Git Data API requires separate create-tree/create-commit/update/readback operations at each durable boundary. Root reviewed this scoped operating adjustment; it grants no provider credit or additional compute start. Compute stays1, agents2 (none needed), polls4, checkpoint reserve8 calls/4000tokens. Ordinary40-call ceiling is restored after this experiment; lifetime history stays charged.


## Terminal Android setup attempt

Task task_e_6ab2bba1ba408328870f0b01d0dcce26 is terminal setup_failed: apt install timeout124 at17:36:15Z. Requested source f937caf; actual checkout/clean state was not observed because agent checks never started. Logs/intent/config archived in docs/validation/codex-android-boot/attempt-001/. No emulator boot or device result.

A bounded correction changes apt-install120→240s and adds phase/HEAD diagnostics. Its saved environment readback must match the new config before another attempt. Cloud verification is pending. This wake consumed its single compute start; no retry. Ordinary40-call ceiling is restored for future wakes; historical86+poll accounting stays charged. No active task remains. Canonical coordination advances to explicit release during handoff; re-read it rather than treating this checkpoint as ownership.

## CDC 2.3 reconciliation

The canonical D5 budget ledger now uses the same limits as the current adapter while preserving all 28 events and 9 wake IDs. Ledger policy digest is `sha256:fa47a6281a3da05a9d7821e5f0463b0b91e419a5451f14b81913902ce3c86c7f`; Actions remains exhausted and task CI starts remain zero. Scheduler readback at `2026-09-22T19:56:10Z` confirmed the existing `G-Supervisor Watchdog` automation is enabled. This repairs migration state only; it does not authorize the corrected Android external probe.

## Authorized Android setup attempt 002

The owner authorized one corrected Codex Android software-emulation probe. The
single start was submitted as task
`task_e_6ab2dfae61ec8328b969d6e98132b22f` against exact source
`5fccad58bdcea44eb6cb2c67a90f82d129e73afc` and environment
`6ab2af0fed688191bab2dbc8e58d1218`. Setup printed the expected HEAD, then
`apt-get update` failed with exit100 because the preconfigured
`apt.llvm.org/noble llvm-toolchain-noble-20` source returned403 through the
environment proxy. The agent command never ran.

The task is terminal `setup_failed`; its one authorized compute start is
consumed. SDK installation, emulator boot, Android tests, device/Doze,
install/upgrade and OAuth remain `NOT_RUN`. Durable evidence and the terminal
intent are on `cdc/coordination` revision `ed989cf09e33cf6ff121b317e977782a68cc92c9`. No retry is authorized.


## APT source correction, 2026-09-22

The actual attempt-002 task was found and is terminal setup_failed, not a missing task.
The screenshot's no-task-id report is superseded by the task evidence above.
Setup now makes temporary source/index files for its two APT invocations, excluding
only apt.llvm.org (unrelated to the Android dependencies). Original image sources,
other repositories, signed-by fields and network isolation stay intact. Any remaining
APT update error is fatal; no insecure/unsigned fallback or automatic retry is added.
The install allowance remains 240 seconds.

Seven new bootstrap regressions plus nine existing boot-probe tests pass locally.
The saved Codex environment setup was read back byte-for-byte; maintenance remains
empty and agent internet Off. No new task, terminal session, Actions job or Android
boot was started. The previously authorized single start remains spent. See
docs/validation/codex-android-boot/attempt-002/correction.md for digests and limits.

Recovery also found that the existing durable D5 budget does not pass its generic
replay validator: historical 3-agent and 90-tool-call wakes exceed the later 2/40
policy, and attempt-002 has two conflicting terminal outcomes. Those historical
records are preserved unchanged. Do not launch further compute/agents until an
explicit, audited ledger reconciliation preserves charges and current limits.
This scoped setup correction grants no further external starts. Re-read live
coordination on resume; this invocation releases after publication.


## Budget repair and new explicit check grant, 2026-09-23

The owner requested «Исправь и проверь». This supersedes the earlier no-new-start
handoff for exactly one corrected Android probe. The audited historical prefix
retains all 34 events, ten wakes and nine charged compute starts. The premature
GitHub service-failure observation becomes unknown; the later actual setup_failed
outcome remains terminal. Raw original data is archived. New admission uses
`tools/project_budget.py` with unchanged current caps; generic historical replay
alone is insufficient. Independent review and current cloud verification follow.
Android boot and app/platform gates remain unverified until actual evidence.
Live coordination takes precedence over this checkpoint's lease pointer.


## Current correction, 2026-09-23

Owner approved replacing the four-poll ceiling with time-based supervision.
Skill 2.3.1 and adapter now set status_polls:null; wait intervals and diagnostic
deadlines stay effective. Existing task observation needs no new launch grant.
Attempt003 task_e_6ab358f2aa448328a0f1f01fab0ffcc2 is terminal setup_failed, exit124
at 04:48:34Z during APT installation. Actual boot and app tests never ran.
Source was requested at 83ac60955ad86c1b8c2edec2ac0a543fcffb6a58; setup failure
is not successful exact-SHA command evidence. No replacement task was launched.
Live ownership/terminal evidence is in cdc/coordination; this checkpoint is not a lock.


## Online adaptation authorized by owner

Agent internet Common dependencies is enabled. User requested adapting preparation
and checking again. Heavy provisioning moves to an explicit bounded agent check,
with APT install allowance900s instead of240s. This supersedes earlier no-new-start
and offline-only notes for this verification. Source binding and all Android
acceptance gates remain; no success until real SDK/boot evidence.


## Actual online result and correction, 2026-09-23

Attempt004 task_e_6ab36028e11c8328b4bdb4af9f5eab71 completed on exact clean
source f50574747a52e52085467224bc30f688502b16ea. Lightweight setup and agent
startup worked. Required check failed in apt-update with exit100: the Common
dependencies proxy returned HTTP403 for the image-provided mise.jdx.dev source.
Runner and validator both exited1; SDK/Android boot/API/ABI remain NOT_RUN or
NOT_OBSERVED. App tests were not run. Full visible task report is persisted on
cdc/coordination at android-boot/terminal-probe-004.txt; raw worker artifacts
were not downloaded and no local revalidation of their JSON is claimed.

The corrected temporary APT filter now excludes the two observed unrelated
sources apt.llvm.org and mise.jdx.dev. Original source files, signature checks,
other sources and fatal update errors are preserved. Two regression assertions
failed before the fix; all21 bootstrap/online/boot-helper tests pass afterward.
This is local correction evidence, not a successful cloud/Android result.

Shared cache reset was rejected by automatic approval review and was not done.
No replacement task started: this wake's configured single compute start is
consumed. This is a repository policy cap, not an observed provider quota.
The terminal guard is cleared; canonical ownership is released at handoff.
D5 remains open. See attempt-004/result.json and correction.md.

## Lean provisioning optimization, 2026-09-23

After probe004 failed during APT update on the unrelated `mise.jdx.dev`
repository, the owner asked to prepare and apply the proposed optimization where
safe. Repository provisioning no longer installs a second OpenJDK or refreshes
certificates/curl/unzip/Python. It reuses the platform Java runtime, checks the
fifteen emulator-native libraries with `dpkg-query`, skips APT completely when
they are present, and otherwise installs only missing libraries with
`--no-upgrade --no-install-recommends`.

The temporary APT view is now allow-listed to Ubuntu package sources instead of
growing a deny-list for image repositories. This covers the observed LLVM and
mise proxy failures and prevents unrelated third-party repositories from
participating in the Android-native dependency step. APT update/install remain
bounded at180/300 seconds; SDK installation900s and software boot900s are
unchanged. Provisioning source readback SHA256 is
`ce32d926eafce53e6e08ccb7a7ca9a23f976fb8ce85c72a3c31d1e1ef8f886e7`.

Five deterministic preparation regressions passed in a local representative
harness, including Ubuntu-only source filtering, APT skipping and missing-only
installation; Bash syntax passed. Repository regression tests and environment
evidence were updated to enforce/bind the same contract. No Codex or Actions
task was started for this follow-up. Android SDK/boot/API/ABI/guest-shell
verification therefore remains open and requires a separate explicit compute
grant.



## Compute budget update

Owner changed the global Codex Compute ceiling to4 starts per wake. The canonical
ledger migration preserves all66 events and every wake. Previous cap1 statements
are historical; Actions remains exhausted. This policy-only change launched no
compute or CI. Live coordination overrides checkpoint ownership pointers.

## CDC 2.3.3 provenance reconciliation

The complete vendored skill package is now 2.3.3. Cross-project comparison
between g-supervisor and g-ad-control found 55/55 skill blobs identical. The
installable package was verified on exact SHA
`8708701ffeb324276b839ae8003043d47751185e`: package validation PASS and
156/156 skill tests PASS in an isolated temporary environment with only the
declared PyYAML requirement installed. Project adapter minimum is raised to
2.3.3 while preserving the four-start compute policy and exhausted Actions.
This policy-only reconciliation grants no Android probe or CI launch.

## CDC 2.3.3 project binding GREEN

Exact policy-only HEAD `23ac4ab288a84f1701196302e0bdadb7fa404086`
was verified read-only in Codex. Adapter validation emitted semantic digest
`b33ae4ab1de735fe5fa1244482516d41a33611be06dde6494db9eca39304b992`;
checkpoint v3 binding and the project strict CDC policy validator also passed.
The worktree was exact and clean before/after. PyYAML was installed only in an
isolated temporary venv from the skill-declared requirements and removed after.
No Android, product, Gradle or GitHub Actions check ran. D5 remains blocked only
on its own platform evidence/Actions constraints.


## Pending CDC 2.3.4 integration and authorized continuation

Owner explicitly requested integration and resumed work on 2026-09-23. This policy branch repairs the strict adapter/checkpoint binding and next action, but does not acquire, release or impersonate the recorded executor. Ownership timestamps/control references above are historical observations, not evidence of current liveness. Read canonical cdc/coordination before any write. Keep all ledger history and external submission claims. The integration is pending safe handoff, not a completed product/platform gate.


## CDC 2.3.5 chat-dependency policy adoption

This isolated policy change only updates the adapter binding. All product, owner,
lease and external-operation fields above retain their historical observation time;
they are not a current liveness report. Before integration, reconcile live
`cdc/coordination` and preserve the guarded candidate HEAD. No ownership or budget
record is changed by this patch.

The owner accepted archived linked chats as the working cause of watchdog failures
on 2026-09-23 and explicitly requested prevention/recovery rules now. Read
`docs/watchdog-chat-binding.json` and `docs/development-watchdog.md`. Unarchiving
was observed; post-repair delivery was subsequently verified by the root observer: the canonical
task advanced last_run_time to 2026-09-23T11:30:39.011210Z, displayed a fresh
completed-cycle report and remained enabled with the next run scheduled. This
is recovery evidence at that observation, not an Android success claim.

## D5 automated Android GREEN — 2026-09-23

The one owner-authorized GitHub Actions run `35916034109` completed successfully
on exact candidate `b9e60b4b1a84a6fb6a9ae30ac742f7ab872c4ca5`. The job used
Ubuntu 24.04, Temurin 17 and `/dev/kvm`; all workflow steps completed GREEN,
including emulator boot, instrumentation, scheduler/Doze evidence, clean install,
cold launch, PID capture and evidence upload.

Independent artifact verification matched GitHub's archive digest
`sha256:5fb719fce9248ba45a13126c04a1fedc6b663eb62f3bff45f04262c3ec6edbab`.
The artifact contains 167 files and the exact candidate SHA. JUnit XML totals are
86/86 domain, 92/92 app JVM and 48/48 normal instrumentation, all with zero
failures/errors/skips. The offline worker case is present; the two dedicated
scheduler probes are excluded from the normal 48-case suite and each passed
separately.

Scheduler evidence shows a CONNECTED 900000 ms WorkSpec registered through
SystemJobService before idle, during forced deep idle and after process
recreation. The WorkSpec UUID stayed unchanged while process ID changed
4536→4801. This proves durable registration and Doze constraint observation; it
does NOT claim exact 15-minute execution, execution while force-stopped, or
execution during forced idle.

The debug APK is 20635493 bytes with SHA-256
`153f539aa2868df9985d7965752ed61e41c6b58653715083e6048a828855ef5a`.
Cold launch returned `Status: ok` and PID 4923. Its Android Debug certificate
SHA-256 is `09f70a1d9f062f9fd60df14b1d5de965e58f12a982ab4cbce2fc81d9f5e61f65`,
which differs from D4's `a8fc16d86e737a59b467ca40bc54153456017b9b092cdf2767120ec61ca6a838`.
Therefore this APK cannot be claimed as an in-place upgrade of the previous
debug deliverable; uninstall/reinstall removes local app data.

Automated D5 acceptance is GREEN. D5 remains open only for applicable owner
phone smoke on this exact new candidate. The one-run Actions authorization is
consumed and policy is restored to `exhausted`.



## D5 closure and D6 transition — 2026-09-24

Owner confirmed the remaining phone smoke with “Все тесты пройдены”. The
attestation is recorded in `docs/validation/D5-owner-phone-green.json` and
applies to the four pending phone checks from the prior checkpoint: foreground
/manual refresh, pull refresh without duplicate activity, cached offline data,
and eventual refresh after normal backgrounding when Android permits.

Together with `docs/validation/D5-automated-green.json`, exact candidate
`b9e60b4b1a84a6fb6a9ae30ac742f7ab872c4ca5` and Actions run
`35916034109`, D5 closure criteria are satisfied. This does not claim exact
15-minute execution, force-stopped background execution, or in-place upgrade
from the differently debug-signed D4 APK. Actions remains `exhausted`.

D6 is now the active slice. The detailed plan is
`docs/superpowers/plans/2026-09-24-g-supervisor-d6-executive-ui.md`.
Current code still has a placeholder Events screen and disabled project-open
action; no D6 production implementation is claimed by the planning commit.


## D6 Task 1 partial implementation and one-shot Actions terminal — 2026-09-24

D6 Task 1 source implementation added Room v5 executive persistence:
`ProjectEvent`, `ProjectGoalSnapshot`, their DAOs, `MIGRATION_4_5`, and
two `D6ExecutivePersistenceTest` migration/reopen cases. The source line is
currently `10e8fa400c5c4c0b9c34248c558ad4288974b91c`.

The owner-authorized single D6 Actions run `35945104172` executed against
candidate `85728d434c5fec52f3fc98e681a2ded7c12face6` and is terminal
`failure`. It failed in the initial tooling preflight before Android SDK,
Gradle, instrumentation, install or device checks. No rerun/retry/second Actions
start was authorized; Actions is again `exhausted`.

The two tooling-contract causes were corrected without Actions. COMPUTE_ONLY
`d6-tools-green-029` verified exact SHA
`10e8fa400c5c4c0b9c34248c558ad4288974b91c`: PyYAML 6.0.3 preparation
succeeded, 49/49 tooling tests passed, and the worktree stayed clean before/after.
Evidence: `docs/validation/D6-task1-partial.json` and PR comment
`5807859783`.

This is tooling/source evidence only. D6 Task 1 Android migration/runtime GREEN
is still pending and must not be inferred from the failed Actions run or tooling
GREEN. Continue D6 source implementation with skip-ci until a new explicit
platform-run grant exists.


## Orphan-lease recovery GREEN, 2026-09-24

Foreground RCA established that generation 27 finished its owning watchdog invocation without releasing the lease. The exact invocation completion, terminal attempt030, null external guard and unchanged source HEAD were recorded in PR comment 5808222002. Generation 28 recovered ownership with explicit `executor_stopped` evidence; TTL alone was not used.

The obsolete D6 incomplete-app evidence assertion was corrected from 91 to 100 while the required complete app JVM total remains 101. Vendored CDC advanced to 2.3.6: final response is now an ownership boundary, and exact-owning-invocation completion with drained pending effects is valid quiescence evidence before TTL expiry. Pressure scenario 42 covers this failure mode.

Exact candidate `ff718ea3b0a75d42e0d522a28d42a8a3beeb8498` is portable tooling/policy GREEN by COMPUTE_ONLY attempt `d6-orphan-recovery-green-032`, PR comment 5808383876: tools 49/49, CDC 156/156, package validator 2.3.6 / 50 files, adapter PASS, checkpoint PASS, exact clean SHA before/after. Android/Gradle/emulator/device/install/Doze/OAuth and Actions were NOT_RUN. The Android platform gate therefore remains open.


## Watchdog health recovery — 2026-09-24

A fresh scheduled delivery completed at `2026-09-24T07:01:57.305968Z` in the canonical bound chat. With the scheduler enabled, the exact current invocation running, generation 29 explicitly released, no external guard and fresh progress, the vendored CDC 2.3.7 classifier returned `HEALTHY / none` at `2026-09-24T07:08:43Z` with fingerprint `sha256:18b9bc5b80b6f29b44ed4232ef704629ad95ffb45ed89031f05f53d94935015c`. This diagnostic result grants no product, scheduler or external-start authority.


## CDC 2.3.8 visible-continuity RCA — 2026-09-24

Foreground investigation of “Why I see no work?” found that the canonical
G-Supervisor watchdog remained enabled and had a fresh scheduled execution, while
its reports were delivered to the bound watchdog chat and notifications were
disabled. Foreground silence therefore did not prove project inactivity.

Two real continuity defects were also confirmed. First, an earlier foreground
invocation announced a non-Actions validation next step, reached only backend/tool
discovery and did not perform a fallback or durable blocker/handoff in that same
invocation. Second, the source checkpoint still advertised generation 30 as
active after live coordination had released it, making liveness visually
contradictory. During this RCA a third orchestration defect was exposed: a
multi-write helper successfully moved HEAD on its first mutation, then compared
the second mutation against the old expected HEAD and initially looked like
external movement. Compare proved the movement was our own first policy write.

CDC 2.3.8 makes these conditions explicit failures: accepted next actions require
a continuation boundary before return; final handoff must be release-consistent;
and coherent policy edits prefer one tree/commit + one conditional fast-forward.
The watchdog remains the same canonical automation. This policy change restores
no Actions capacity and does not claim the outstanding D6 Android platform gate.


## CDC 2.3.8 visible-continuity GREEN and activation — 2026-09-24

RCA for the owner-visible “I see no work” condition is complete. The issue had
both an observability component and real orchestration defects: watchdog output
is delivered to its bound chat with notifications disabled, while a prior
foreground invocation also stopped after backend/tool discovery without
crossing a durable continuation boundary. A stale source checkpoint could show
an active executor after live lease release, and sequential policy mutations
could reuse an old expected HEAD after their own successful first write.

CDC 2.3.8 makes those states explicit failures. A runnable announced
`next_action` must, before return, produce meaningful durable progress, bind
real external work, or persist an explicit blocker/handoff; unavailable preferred
backends traverse the authorized fallback chain in the same invocation.
Final handoff is release-consistent, and coherent multi-file policy changes
prefer one Git tree/commit plus one conditional fast-forward.

Exact policy candidate `79271c4ed82f5deaa0ad631bb3be7e5b7c1616fe`
is COMPUTE_ONLY GREEN in PR comment #5809808510: package validator PASS for
continuous-development-cycle 2.3.8 with 54 files/templates; 171/171 vendored CDC
tests PASS; 49/49 project tooling tests PASS; strict adapter and checkpoint
validation PASS; exact SHA/worktree clean before/after.

Canonical recurring G-Supervisor Watchdog
`6ab138b960dc8191935b0379f17cbb49` was updated in place with the CDC 2.3.8
visible-continuity/fallback/release-consistent rules. Its enabled state and hourly
schedule were preserved. This policy rollout consumed no GitHub Actions capacity.

The D6 product Android platform gate remains open; the previous one-shot D6
Actions grant is consumed and policy remains exhausted. Product implementation
identity therefore remains the D6 source candidate recorded above rather than
this documentation-only policy/status HEAD.


## D6 Task 2 HTTP 304 cache-preservation slice — 2026-09-24

Tests-first commit `bd238dd79f19bcec6e06e0d552de3be813cc38b4`
requires a typed `NotModified` result and proves an HTTP 304 body is never read.
Implementation commit `79b0f0ae4eec651116f7575a79c62a6b1c44ded4`
adds typed unchanged handling through transport, sync and Room-backed source state.
A 304 now preserves existing event rows, clears stale source errors, records a
fresh successful observation and counts as a complete unchanged source. The sync
regression also preserves an existing cached release across a subsequent 304.

COMPUTE_ONLY attempt `d6-executive-304-red-038` is terminal/reconciled at
PR comment 5810610326. It confirmed exact clean HEAD before execution but failed
before compilation because the inherited fixed JAVA_HOME path did not exist.
Expected product RED, Gradle and tests were NOT_RUN.

The distinct remedied attempt `d6-executive-304-green-039` is terminal/reconciled
at PR comment 5810693555. Portable setup installed and verified pinned Temurin
JDK 17.0.20.1 and the Android command-line tools, then failed fetching Android SDK
package manifests; SDK36/build-tools and targeted Gradle tests were NOT_RUN.
This is an environment/network setup failure, not product GREEN or product RED.
The worktree was exact and clean before both starts; final post-failure guards
were not reached because the commands used set -e.

Both compute starts are charged in the durable ledger. External guard is cleared.
No Actions run, emulator/device, installation, Doze, OAuth or Android platform
verification occurred. Actions remains exhausted. A repeat is forbidden until a
compatible environment has persistent JDK17 plus SDK36 metadata/cache read back;
then the next attempt must be the exact targeted GREEN described above.


## Baseline Actions grant — 2026-09-24

Owner authorization supersedes the previous current-state Actions exhaustion:
every CDC wake now has one baseline GitHub Actions start, including this foreground
wake. The grant is per-wake, non-accumulating and does not roll over. It is
capacity rather than a requirement to spend Actions. Any launch/rerun/retry that
actually starts Actions consumes the one slot for that wake; a second start in
the same wake is not authorized.

The durable adapter moves current Actions admission to `normal`, removes the
task-lifetime CI cap and sets `wake_limits.ci_starts: 1`. Historical one-shot
grants and all prior charges remain unchanged. Exact-SHA, ownership, external
guard, failure-circuit and candidate-readiness requirements remain mandatory.

For the current D6 HTTP-304 slice this removes the Actions-exhausted blocker.
Codex attempts 038/039 remain terminal environment failures. The current wake may
use one Actions start as the next valid hosted-platform fallback after durable
intent/budget/guard setup, provided live HEAD/candidate/concurrency still match.


## Actions baseline rollout result — 2026-09-24

The owner granted a persistent baseline of one GitHub Actions start per CDC wake.
The adapter and durable budget ledger now enforce `actions_budget: normal`,
no task-lifetime CI cap, and `wake_limits.ci_starts: 1`. Unused capacity does
not accumulate or roll over. Any real launch/rerun/retry consumes that wake's
slot; the next wake receives one fresh slot automatically without another
per-run confirmation. This is capacity, not a requirement to spend Actions.

The current wake used its slot exactly once. Run `35983930339` on exact SHA
`5f316aa4c2bf333a9688b18b3798999704317933` failed during the initial
Python policy/tooling preflight, before Android SDK, Gradle or emulator work.
The cause was an obsolete test that still required the superseded
`Actions exhausted` behavior. No second Actions start was made in this wake.

Commit `76e090e92701febf4fbac6b9095d6ba0877e8a7b` corrects that contract
with explicit tests for first-start allowed, second-start denied in the same
wake, and one restored slot in a new wake. COMPUTE_ONLY 042
(PR #1 comment 5812012577) is GREEN: PyYAML 6.0.3, 51/51 project tooling tests,
adapter PASS, exact clean SHA before/after. COMPUTE_ONLY 043 independently
confirmed semantic policy digest
`521c06eea944b18452aec8fb38b34b0e9455213e1850ebebca63c3b5342170a5`;
its only checkpoint failure was the prior non-UUID active executor metadata.
This final handoff intentionally removes the executor/control liveness fields
before generation 33 is released.

The D6 HTTP-304 product/source/platform gate is still open. The next wake gets
one fresh Actions slot under the new baseline policy; it must not rerun the stale
failed SHA. A useful next trigger is a real `workflow_dispatch` capability
addition to the D6 gate, committed non-skip once, so the resulting exact SHA
contains both the HTTP-304 implementation and the corrected budget-policy tests.


## D6 exact-SHA gate 045 and deterministic retry correction — 2026-09-24

Exact candidate `f987d34979a4a0d82ef586e00dd18f411d690288` ran once in GitHub Actions run
`35992278742`. Tooling, Android SDK setup, Gradle build, domain/JVM tests, lint,
APK assembly, Android-test compilation and emulator boot all passed. Instrumentation
finished 49/50. The four migration cases that failed in run 35987959908 now pass,
confirming the `MIGRATION_4_5` corrections.

The only remaining failure was
`GitHubPortfolioRetryTest.manualRefreshAfterUnknownRateLimitKeepsHealthyAccountUsableAndLaterRecovers`:
its synthetic, non-suspending collaborators were dispatched through
`Dispatchers.Default` and the overloaded emulator did not publish the first report
before the ten-second wall-clock deadline. Raising the deadline from five to ten
seconds had already reproduced the same failure signature, so another timeout
increase is not an accepted remedy.

Commit `6eebb2755b58e4d1b7f3b19268077bf9ce3084b5` makes only this synthetic
instrumentation scenario deterministic with `Dispatchers.Unconfined`; production
scheduling is unchanged and remains covered by `SyncCoordinatorTest`. The commit
uses `[skip ci]` because the current wake's one Actions start is already consumed.
Android GREEN is not claimed until a later wake uses its one fresh slot for an
exact-SHA gate on this candidate. Run 35992278742 is terminal/reconciled, artifact
10804493376 is recorded, and no second run was launched.


## D6 exact-SHA gate 046 compile diagnosis — 2026-09-24

GitHub Actions run `35995281542` was bound to exact candidate
`5977fe101c5a98eb965fd333d91c12eba8687be1`. Exact-SHA/policy checks,
Android SDK setup, domain/JVM tests, lint and APK assembly passed, but
`:app:compileDebugAndroidTestKotlin` failed before emulator start. Two literal
`\\n` sequences introduced by the prior Git Data edit kept the
`coordinatorScope` declaration inside a line comment; both compiler errors were
therefore deterministic source errors, not an emulator timeout.

Commit `be6a1fc64493ded05d8e8ceda15047fdc0030ba1` replaces those two literal
escapes with real newlines and restores the original five-second bound for the
now-deterministic synthetic retry test. It is `[skip ci]` because the wake's
single Actions start is consumed. Run 35995281542 is terminal/reconciled,
artifact 10806002112 is recorded, and Android GREEN is not claimed. The next
wake may use one fresh Actions slot for one new exact-SHA gate; the failed run
must not be rerun.


## D6 exact-SHA gate 049 and uncached-304 contract correction — 2026-09-24

GitHub Actions run `36046829432` was bound to exact candidate
`3d7b5a1f5a43dcf328ec74b3c15e7f74f7d02efc`. Exact-SHA/policy checks,
JDK 17 and Android SDK setup passed. The unit/lint/APK step stopped at one app
JVM failure before emulator startup: 107 tests ran and only
`GitHubHttpExecutiveTransportTest.notModifiedPreservesCachedSourceWithoutReadingBody`
failed. The artifact is `10829491897`, digest
`sha256:4ea9f983e15e57ce13d8d8e2497644176f3056ecff53bf34dab716851d1ede9b`.

RCA compared the failing legacy test with the new ETag/pagination contract. A
first-ever HTTP 304 has no cached facts to preserve and production correctly
returns `ProtocolFailure`; the separate pagination regression first fills both
page caches, then verifies conditional ETags and a cache-backed `NotModified`.
Commit `aff12ee0f39001842fc0c5607b4a863799d464c6` changes only the stale test
name/expectation from uncached `NotModified` to uncached `ProtocolFailure`.
Production code is unchanged. The commit is `[skip ci]` because this wake's one
Actions start was consumed. No second run was started; exact-SHA GREEN remains
pending for the next wake.

## D6 Task 4 tests-first placement diagnosis — 2026-09-25

GitHub Actions run `36086638151` executed once on exact test-only candidate
`34be85537e581ff9897d665a81106760a98b5687`. Policy checks, JDK 17 and
Android SDK setup passed. The build failed in `:app:compileDebugUnitTestKotlin`
before any emulator work.

This was not a valid product RED: the new app-module test imported
`:core:domain`, while the app module intentionally has no project dependency on
that module. The compiler therefore failed at the module boundary before it could
exercise the missing Task 4 presentation contract.

Corrective commit `1a5fd5fa9db66da5ab09eefddfbc13d8200c2452` removes the
misplaced app test and relocates the same seven tests to
`core/domain/src/test/.../ExecutiveStatusMapperTest.kt`. No production code was
added. The corrective commit is `[skip ci]` because this wake's single Actions
start was consumed by run `36086638151`.

The next wake must use one fresh exact-SHA Actions gate to establish the corrected
RED on the current candidate. The expected failure is the absent
`ExecutiveStatusInput`, `ExecutiveProgressEvidence` and
`mapExecutiveStatus` domain contract—not an app/core dependency error. Do not
write production implementation until that corrected RED is observed.

