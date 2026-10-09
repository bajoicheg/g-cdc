# CDC 3.0.0 integration of the qualified 2.13.0 candidate

Owner requires ordered publication: 2.12.2, then 2.13.0, then 3.0.0.
Fleet rollout is explicitly paused. Isolated integration is authorized while
dependent release gates remain closed.

The accepted 2.12.2 source is immutable release/v2.12.2 at
3d063ac723a68340e732d552c1d69636470b1ac3, package
b924d431edec544264bc67cdfbd98548a30d9dfb. It is an ancestor of the
qualified 2.13.0 candidate c6c37ee97223de809a259513dd12bcbb4fd651be,
package 5b95b33b4ed1f807ddbefbf4ca24e5ceb2896f2f.

The 2.13.0 candidate has actual Root SPEC_GREEN and subsequent independent
QUALITY_GREEN, with no remaining findings. Its clean-consumer FULL passed
1263 tests in 355.212 seconds, exit 0, under source copy
210c7fa2338ba276302462ea381b1dc52ceb4eaf with the identical complete
package object. Its final head passed 46 independent bootstrap tests, package
validation and three archived-consumer adapter/checkpoint pairs. These are
candidate results, not an immutable release or live adoption.

This isolated merge combines that actual candidate with the reviewed initial
3.0.0 branch at 5fc15e290553a06d8354f4a327cf3e78665c7ba0. Cloud
profile/entrypoint/recovery code and the accepted alias remain unchanged.
Version identities and the compact 3.0.0 core are retained; the core routes to
the existing Cloud entry and reference rather than duplicating an executor.
No live consumer policy ceiling is widened.

Development remains under the actually byte-verified immutable 2.12.1 driver.
Neither candidate version is installed authority. After 2.13.0 source release
and separately verified activation, requalify that released driver before the
3.0.0 release stage. Historical observations and failed checks remain bound
to their original source, command and environment.

At integration start, native Git write preflight failed before mutation:
git push --dry-run returned exit 128, unable to obtain a password. The actual
receipt is preserved with 2.13.0 evidence. Shared main/release publication and
CI admission require the existing genuine managed host/transport; no proxy
credential or serialized lease substitute is inferred from connector access.

Remaining release gates: actual 2.13.0 exact-head CI/source release/activation;
frozen 3.0.0 complete package and compatibility qualification; ordered final
reviews; exact-head CI; managed source publication and separate installation.
Archived policy ceilings can correctly reject 3.0.0 and must be preserved.
Keep the original task budget, unknown legacy actor charge, unresolved guards
and paused schedulers. No Fleet operation is part of this integration.
