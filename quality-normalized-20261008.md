# CDC 2.12.1 normalized candidate — independent QUALITY rebind

Result: GREEN for code-quality rebind only, reviewed 2026-10-08 after completed SPEC rebind.

Reviewer: parent Work /root, separate from Cloud SPEC reviewer and managed normalization writer; no product edits were made in this review.
Candidate: 9b38bd4d9f5fb113ec10bdbca9fbe33908619a54.
Sole parent/base: b72435542f40ec3f5b195f357c968c2346ab4f8f.
Prior reviewed candidate: 9516aa1fafd32fcf7fcb239e96fa1e6b4d141d3a.
Root tree: 49e3db723a8703c89f9e535fcab373b3ff128a06.
Package tree: 9c45d98c3254e9658d452c505d8c97698e3fc9a7.
Governing authority: immutable released CDC 2.12.0.

Prerequisite SPEC was fetched in full from bajoicheg/g-cdc commit c4a1c1a1dc42642df98adcf339726fdbd3467ef0, document.json. Its actual report UTF-8 SHA256 independently matches 7a069a4c470655626a24d1c8d1081dac812080b0fc9875f4cef1037b7d6e2f0b. It explicitly requires this independent QUALITY and new exact-head CI.

Independent observations made through GitHub Git Data and compare endpoints:
- Both old and new exact commit objects have the identical complete root tree 49e3db723a8703c89f9e535fcab373b3ff128a06. This cryptographically binds every tracked byte, pathname and Git mode, including compressed evidence, workflow, bootstrap, package, compatibility fixtures, specification and plan.
- New commit has exactly one parent, the unchanged main base b72435542f40ec3f5b195f357c968c2346ab4f8f. Compare reports ahead, one commit, the same merge base and exactly 35 changed files. Their complete paths match the previously reviewed aggregate final diff.
- Recursive root-tree read is complete (truncated=false, 609 entries), including exact package tree 9c45d98c3254e9658d452c505d8c97698e3fc9a7.
- Fresh isolated source ref refs/heads/cdc/parallel-maintenance-normalized-20261008 resolves to this exact new commit.
- With a single commit atop the base, historical touched paths equal its final 35-path diff. The five old transient uncompressed logs are absent from this new history. The actual Cloud released-runtime _result PASS is supplied evidence, distinct from these independently observed Git facts.

The prior full independent QUALITY report was read unchanged and its actual UTF-8 SHA256 independently matches d3c07a4ef208e30b9cb0b3de0d117a578ab80e69fd8dea971e6f2892cb8dfea7. Its assessments of argv preservation/type rejection, transport content/tree binding, tests, scoped operating guidance, all seven retained log hashes and failed/corrected clean-consumer history remain applicable to the identical tree. No new implementation or evidence content is introduced by normalization. The former publication failure arose from intermediate history outside the final diff; the new one-commit history removes that admission mismatch without weakening the released gate.

Findings: none introduced by this normalization. Accept prior content-quality findings for the exact new candidate, preserving original report and validation provenance. No local FULL suite was rerun for identical bytes. Old CI run 37734195216 remains bound to old candidate 9516aa1; it is not new exact-head CI evidence. New required CI, source publication, immutable release, personal installation and live adoption remain separate pending gates. This report grants no write, merge, release, takeover, scheduler or provider-start authority. GAD remains excluded; paused schedulers and historical charges remain preserved.
