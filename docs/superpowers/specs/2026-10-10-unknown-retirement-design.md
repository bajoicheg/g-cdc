# CDC 3.3.1: bounded retirement of an unknown isolated Git submission

Owner authorization: 2026-10-10, "Исправляй этот бред. Мы сами себе создаём проблемы", accepting the immediately proposed administrative isolation of UNKNOWN without replay, followed by independent GPC CDC migration. Develop under immutable released CDC 3.3.0 (2be2088d8e6ad59f87cdd9d07dc9f7ab8d4c34ad; package 3f00c4927557aa94912c8bf21a881add47c2f412).

## Problem and decision

The old diagnostic caller returned but discarded the Git subprocess result before raising a wrapper exception. Existing reconciliation correctly cannot fabricate a terminal Git result. Its project-wide guard also blocks unrelated CDC maintenance indefinitely. Add an explicit owner-authorized administrative disposition, separate from provider terminal reconciliation. The operation outcome remains UNKNOWN permanently in its retirement entry; it must never become a success, rejection, refunded budget, or completed product validation by this path.

## Supported transition

Only a released v2 lease with the exact original consumed guard, no owner/invocation/finalization, and a matching last_release can be retired. The proof binds the exact current lease revision/digest, original guard, immutable owner decision, original authenticated caller/effect observation, candidate and isolated refs/heads/pilot/* target. The original operation must be a single create-only Git push with an empty expected destination; source, coordination, release and protected refs are unsupported. The released original runtime must have physically stopped without pending shared writes, and its dispatcher/subprocess must have returned. These are authenticated evidence obligations for the controller; structural parsing is not authentication. A boot mismatch, elapsed time, absent ref or zero Actions runs cannot satisfy them.

A late remote result may create only that preserved pilot branch. It cannot mutate the source ref used for independent migration. Never delete or recreate the pilot, never submit the original candidate again, never create a replacement grant, and never rerun or dry-run the original command.

Canonical CAS moves the original guard unchanged to one append-only `submission_retirements` entry, outcome UNKNOWN and replay_forbidden true. Only external_guard and submission_retirements change. Claims, last_terminal, submission_resolutions, generation, last_release, ownership and neighboring coordination files stay unchanged. Raw clears and history rewriting remain rejected. Stale CAS and a lost response require observation, never a second effect. No provider callback is called by retirement.

The optional field preserves old records exactly until used. Retired operation keys and original candidate/backend bindings cannot be rearmed under a new attempt, environment or grant. A distinct candidate operation remains eligible through normal fresh managed ownership, intent, budget and publication checks. Older runtimes fail closed on the added field; retirement and migration must run under released 3.3.1, not the installed GPC 2.12.1 parser.

## Validation and delivery

Behavioral RED/GREEN for exact retirement, UNKNOWN/history preservation, malformed scope/provenance/quiescence, replay under changed attempts/bindings, stale and lost CAS, unrelated mutations, multi-document Git preservation and race. FULL risk floor; bootstrap/package/layout and archived compatibility; ordered independent SPEC then distinct QUALITY; exact hosted candidate CI; normal managed source release; actual package verification before GPC CAS and independent migration. Preserve previous budgets, checks, scheduler pause and retired projects. Physical executor closure is a separate final gate.
