# PREQUALIFICATION — conservative quota correction and admission bounds

Source anchor: `598cdb0976544c6143bb425818e40ae678351b50`.
Parent: `cdc-runtime-signal-admission-repair-20261019`.
Only this example directory changed. No local tests, models, provider requests,
CI, submit, installation, scheduler, Git metadata writes or native-store writes.
The fixed entrypoint owns diff checks, commit, independent SPEC then distinct
QUALITY. This packet does not claim any of those stages passed.

The reviewed maintenance implementation and its tests are unchanged. Its previous
README/result/freeze are preserved byte-for-byte in `admission/evidence/prior-kit/`.
Those records describe earlier work, not acceptance of this changed packet.

## Concrete source and apply contract

`admission/baseline/` holds exact installed code copies; `admission/candidate/`
holds replacement modules. `admission/quota.py.patch` and
`admission/immutable_history_cache.py.patch` are exact unified diffs.
`admission/apply-manifest.json` binds before/after hashes and byte lengths.
`admission/protected-inventory.json` pins the inspected integration boundaries;
`admission/sdk-source-pins.json` freezes the credential-free SDK scripts/tests
needed by the hosted runner. Never apply to a different before hash.
No application command in this packet writes the protected installation.
Patches use zero context to avoid staged trailing-context whitespace violations;
exact before/after hashes are mandatory, and application requires support for
zero-context unified patches. `admission/activation-contract.json` binds the
qualification overlay, installation prerequisites and real-exercise separation.

### A: bounded conservative local timestamp correction

This is an owner-authorized change in LOCAL continuity policy, not a provider
reset or a claim that two actual provider buckets are semantically identical.
`kimi_metadata.project_quota` copies the official reset_time string unchanged;
`runtime._epoch` parses absolute ISO8601 without rounding. The recorded one-second
change is real input. Conversion precision is not established as its cause.

For each account/window, the original stored deadline is the immutable anchor A.
Legacy snapshots without local metadata seed A from their existing deadline.
Every accepted within-bound Kimi observation must satisfy abs(raw_deadline-A)<=1
second; comparison is never against the previous observation. Account/provider,
mandatory window names and durations retain their exact bindings. Codex does not
receive a timestamp-correction allowance. Old-copy observations and usage rollback
are denied. Caller-supplied local continuity metadata is rejected.

The effective hold H becomes max(A, previous_H, fresh_raw_deadline). Consumed usage
U is a monotonic high-water within this local epoch; a lower raw value is denied,
never treated as new credit. After the effective hold expires, a within-bound observation is denied even
with unchanged usage: it cannot extend admission, reanchor or create reset credit. A genuinely later deadline outside the correction
bound can start a new epoch only after the old effective hold has expired and all
existing fresh/future-reset conditions pass. Duration changes remain denied even
at reset. Before expiry, any out-of-bound change remains denied.

Both the fresh official RAW normalized observation and the effective state are
assessed. An expired raw deadline is denied even if H is later. Returned severity
is the worse of raw/effective assessments, remaining allowance the minimum, and
runway the minimum available. Burn history is matched by the immutable anchor for
the effective assessment, so lengthening H cannot erase measured burn. The raw
assessment separately uses original raw observations with their actual deadlines.
Neither historical provider deadlines nor percentages are rewritten.

Proof within an epoch: U_new>=U_old and U_new>=raw_used, hence
100-U_new<=min(100-U_old,100-raw_used), independently in every mandatory window.
H_new>=max(A,H_old,raw_deadline), so no earlier reset/hold is introduced. Taking
the worst assessment preserves every raw reserve refusal and the effective burn
reserve. A changed timestamp introduces zero additional starts, requests, session
seconds or native credit. At a true reset only the pre-existing expiry conditions
can permit new allowance, with the additional within-bound no-reanchor rule.
This proves conservative usable percentage/credit, not provider bucket identity.
For example, repeated +1,+1 changes would otherwise drift: A+1 is accepted with
A unchanged, A+2 before H expires is rejected. A+1 observed just after A expires
with lower usage is also rejected rather than counted as a new reset.

The existing SQLite schema/file is reused. Stored account rowids are preserved by
UPDATE; history rows are append-only, including legacy seeding. No six-hour deletion
or silent eviction remains: the existing 1024-row limit denies transactionally when
full, requiring separately authorized retention work rather than discarded history.
Raw normalized observations and per-window anchors are stored with each new snapshot;
legacy rows are not rewritten. All failed validation rolls back the transaction.
No live database is opened by this packet. The five encrypted DB histories remain
untouched. Session/native budget and security modules are unchanged.

### B: refuse an oversized optional cache entry before serialization

SDK3.6.8 `_history` authenticates the fresh endpoint/head, nonshallow full parent
chain, cached prefix and final head readback before calling `_HistoryCache.put`.
The old `put` materializes all documents through `json.dumps(...).encode()` before
checking 128 MiB. The replacement retains `_history` and every authentication gate
byte-exact. It performs a bounded conservative size preflight, then incremental
JSON encoding/compression. Strings cost at most six bytes per codepoint; numbers,
containers and punctuation also count. A conservative estimate may refuse a valid
small optional entry. Depth >256, unsupported/cyclic data or an excessive estimate
also refuses caching. This never removes mandatory caller history or grants intake.

Passing preflight bounds the largest JSON encoder allocation; compressor input
uses 16,384-character slices. Decoded output is counted independently and compact
output cannot exceed the existing total-byte bound minus its key. No full decoded
snapshot string/bytes pair is constructed. The old lock, detached decoding,
monotonic-prefix/concurrent-old-reader handling, divergence refusal, LRU and byte/
entry/decoded bounds remain. An oversized update leaves any old cached snapshot
intact. Fresh authentication still runs on every read. This reduces the *optional
cache insertion* peak; it does not eliminate the mandatory history's memory cost,
all decode peaks, or arbitrary host memory failures.

Reported read-only measurements: failures at 512 MiB and 2 GiB during dumps;
ALLOW at 4 GiB with peak RSS 2,979,920 KiB. These are owner-supplied diagnostics,
not reproduced here and not proof of generic CDC_VPS_REQUEST_REJECTED causality.
The named deterministic collector export was absent during writing; its absence
is recorded, not substituted with fabricated native evidence.

## Changed-boundary matrix

| Boundary | Change | Frozen qualification | Remaining limit |
|---|---|---|---|
| Kimi reset/account ledger | Fixed original-anchor bound, monotonic hold/usage, dual assessment | Recorded case, drift, expiry, rollback/rowids, concurrency, old copies, all reserve negatives | Local policy authored; provider bucket equivalence not asserted |
| Session admission | Unchanged real SessionBudget module | Bound correction at start; invalid identity/out-of-bound and reserve denials, UNKNOWN, cap3/cap4, deadline and no restart | No actual protected service or Kimi exercise |
| SDK optional cache | Conservative preflight and streaming compression | Eager-encode RED, memory child, concurrency, detached copies, old snapshots, all bounds | Mandatory history/decode memory still exists |
| Fresh history/retirement | No code changes | Pinned native real-Git suites plus oversized-cache integration | No new disposition capability or task mutation |
| Existing maintenance kit | Implementation/tests preserved | Full prior kit tests in same hosted packet | Prior native integration/physical closure blockers remain |

## One combined hosted qualification, authored only

After fixed native checks and ordered independent SPEC → distinct QUALITY on one
frozen candidate, reserve exactly one hosted compute start for:

```
python3 -B examples/cdc-maintenance-20261019/admission/qualify.py --sdk-source <credential-free-pinned-SDK-export> --receipts <new-external-receipt-directory>
```

Linux, Python 3.11+, Git and SQLite; no network/provider access. The runner checks
packet freeze and all external SDK source pins, creates a hosted temporary overlay,
then runs **two expected old RED cases** (eager cache allocation and refusal of the
recorded conservative correction), all new candidate packet tests, the exact SDK history/UNKNOWN/budget
suites plus new oversized-history integration tests, and the preserved maintenance
suite. This is the full frozen candidate *packet*, not an SDK-wide FULL/bootstrap,
installed integration test, or a real provider exercise.
Old quota RED means the baseline rejects the recorded correction; candidate GREEN
must accept it conservatively while preserving all negative coverage.
The 140 MiB child test asserts incremental insertion RSS <32 MiB above allocated
input; only hosted execution can establish that claim. All tests are authored,
none executed. No test result, RSS improvement or RED/GREEN is claimed here.

Each subprocess receives separate stdout/stderr files, SHA-256 and its actual
exit before interpretation. A timeout retains logs, null unavailable exit and an
explicit timeout marker; it cannot pass. Aggregate subprocess wait allowance is
600 seconds. The hosted compute/controller must enforce its own outer budget and
physical closure; this runner is not a process-supervision replacement. New receipt
directory only; no receipt overwrite or automatic rerun. `qualification-manifest.json`
is the frozen intent, not a scheduling or admission capability. Native diff check,
SPEC and QUALITY remain separate from hosted evidence.

## Historical disposition and activation

The earlier `cdc-kimi-quota-continuity-repair-20261019` queued contract is immutable:
source919e883, operation=null, empty native budget events. Actual source advanced
to598cdb0 through prior native publication. SDK `_authenticate_intake` requires
an original operation/start_request and an exact prelaunch UNKNOWN/start state;
its existing retirement capability cannot retire this stale queued/null-operation
row. Do not manufacture a proof, relabel it UNKNOWN, alter its source, rearm it or
resubmit it. Supported stale-queued disposition remains a separate missing native
capability, not fixed by faster history caching.

`cdc-kimi-quota-continuity-598cdb0-20261019` returned CDC_VPS_REQUEST_REJECTED;
canonical866759c1ad1f540a916e83fab6bd2e35a9e4930c reportedly contains no task row.
The operator claim remains spent/UNKNOWN: row absence does not refund or permit
retry. All five encrypted DB histories and rowids, accounts, provider cap3, prompt
cap4, old UNKNOWNs, task budgets and claims remain authoritative and untouched.
The unrelated original supervisor cannot acquire authentic waitpid_ECHILD from
these files; RCA101 and RCA113 remain OPEN.

Final activation gates (not performed by this worker):

1. Fixed entrypoint binds the final tree, performs its native diff checks/commit,
   then genuine independent SPEC and distinct QUALITY; preserve actual receipts.
2. One prospectively admitted hosted packet run with exact freeze and SDK pins.
   Inspect every old failure and candidate result. No retry allowance is implied.
3. Independently register native integration/application work. Reinventory protected
   operator quota/runtime/session/metadata collector and SDK cache/unknown_recovery
   against `protected-inventory.json`, all SDK pins, and the current whole operator
   package/deployment policy. Obtain new reviewed whole-package pins and protected
   service/package bindings; old whole-package pins cannot authorize changed code.
   Apply only the manifest's exact before/after modules through the authorized
   deployment mechanism, never patch this live installation from this packet.
4. Validate native fresh endpoints/full parent chain/retirement refusals, five DB
   inventory/rowid preservation, original UNKNOWN gates, all quota/account/provider/
   freshness/required-window/duration/hard-reserve/paid-fallback/reset refusals,
   concurrency and old-copy behavior under the protected installation. No DB copy
   backward, reset, new DB or migration is part of this source change.
5. This changed local policy requires qualification and authorized protected
   application before use. Any genuinely new Kimi exercise needs fresh original
   authorization, unchanged native budgets/claims and actual ACP acknowledgement
   of **K2.8 Preview / Thinking Max** before sending the prompt. A requested model
   label alone is insufficient. Never retry either historical contract.
   Record application and actual Kimi exercise separately from source, review,
   hosted and native integration. Keep controller alive through start/observe/
   finish; require actual returns and birth-bound aggregate closure. Genuine
   managed expected-head finish alone may advance main. Schedulers stay PAUSED.

Budget ceiling: compute1 / agents3 / CI0 / tools40 / 900 seconds. Writer used no
subagents/model observers and performed no compute start. Fixed native stages own
SPEC/QUALITY. This packet confers no authority to spend historical allocations.

## Preserved failed writer and source-review status

The frozen WIP was copied first from
`/opt/cdc-tools/candidates/cdc-admission-quota-wip-4b5be4d2`.
`wip-evidence.json` retains the original actual staged diff-check exit2 and both
trailing-context failures. `admission/evidence/original-wip-bytes.json` preserves
changed original packet bytes with SHA-256/base64, including the whitespace-bearing
patch, without reintroducing those spaces into a newly added patch file. SDK candidate,
SDK boundary tests, maintenance implementation/tests and baseline pins are unchanged.
The quota diagnostic/tests were minimally superseded for the authorized policy;
the old diagnostic test source remains archived, not claimed as current behavior.

Original handle `4b5be4d2-c8a3-552c-a4be-146a986d75f3` is FAILED/quiescent;
lease release and all original budgets remain spent and preserved. Owner-recorded
writer runtime495.4039869s, usage876497 total /857503 input /809728 cached /
47775 uncached /18994 output,23 commands. Native diff-check0 preceded the staged
failure; no original SPEC/QUALITY or publication occurred. No task was restarted.

Current source has only writer text/hash inspection; fixed native final checks,
commit and genuine independent SPEC then distinct QUALITY are pending. Hosted
qualification is separately pending. Installation has not occurred. Real Kimi
exercise has not occurred. Those four statuses must never be conflated. The optional
current native receipt export is observational only and conveys no launch authority.
