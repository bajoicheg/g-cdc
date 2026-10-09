# CDC 3.0.0 official predecessor integration and qualification

The official 2.13.0 release is 38971c582edfb5885b9281a316e02b2044b187bf,
package 5b95b33b4ed1f807ddbefbf4ca24e5ceb2896f2f. Canonical evidence is
663c56170f428b88e360030738859bf91f4277f6:release/evidence-2.13.0.json.
Exact-head CI run 37982529250 is successful. Merge 99c6296 records the official
release ancestry while preserving the already-integrated implementation and
compact 3.0.0 core. Development still uses the independently byte-verified
2.12.1 driver; no candidate is relabeled as installed authority.

Original managed writer generation 68 released normally at 20:19:56 UTC.
Its immutable execution-release-receipt/v1 is bound to coordination commit
71b81faa28ba684177e08810432606a83123518e and invocation
managed-terminal:3eb59d666b592ebf1d3c5e9361bb3da6dc5a13e66c77b787624a9b499e6266cb.
Fresh ownership readback has no owner, invocation, finalization or guard.
The original finish wrapper later failed awaiting supervisor quiescence;
the raw runtime UNKNOWN and incomplete pool acceptance remain history.
Independent physical process closure is recorded at coordination revision
738eca612a75962ac668d935eda2dd22f36b002e. Do not replay source publication,
release refs or CI to repair that wrapper receipt. The later read-only verifier
reservation remains charged: its advertised pool ref was absent on this
resume and no actual start or successful finish is inferred from admission.

Before the compatibility correction, the unchanged integrated 3.0.0 package
10e9f3fa8c7ff1175bd1725a9d4642955aacedb7 passed 51 independent bootstrap
tests, package parsing and a clean-consumer FULL: 1254 tests, 315.182 seconds,
exit 0. Preserve that source/package binding; the corrected package needs its
own affected and aggregate evidence.

The old workflow incorrectly required archived 2.x policies to install 3.0.0.
The reproduced adapter command failed with the expected exclusive-ceiling
rejection. The corrected gate preserves that rejection and validates only
in-memory migration copies; originals, ownership/external state, budget pointers
and history remain intact. A compatible copy is not live installation evidence.

Fleet rollout and schedulers remain paused. Source candidate, immutable source
release, personal installation and consumer adoption remain separate states.
