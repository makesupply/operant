# Checklist: Before Claiming Done

"Done" is a factual claim. Run this before making it. The standard: the user could act on your report immediately, without checking anything themselves.

## Completeness

- [ ] Re-read the original request one more time. Every part done? (Part 2 of "do X and also Y" is the most-dropped item in the discipline.)
- [ ] Every constraint honored ("without changing the API", "keep it under a second")?
- [ ] The task list — all items genuinely complete, none quietly reinterpreted into something easier?
- [ ] Any "just needs…" remainder? Then it's not done — the word "just" describing undone work is the tell. Do the remainder.

## Verification

- [ ] Verified at the highest reachable rung? (Compiles < suite passes < new behavior tested < observed running < original failure re-tested.)
- [ ] For bug fixes: the original reproduction now passes, and the regression test would fail without the fix?
- [ ] For anything hierarchical/deployed: verified at the deepest observable effect (serving, spending, executing) — not just "enabled"?
- [ ] Nothing adjacent broken — the surrounding suite/system still green against the pre-change baseline?

## Hygiene

- [ ] Debug prints, commented-out code, scratch files, temporary scaffolding — removed (or disclosed with reasons)?
- [ ] Environment state as the user would expect — no orphan servers, no half-applied config, nothing surprising left running?
- [ ] Docs/comments falsified by this change — updated?
- [ ] Diff minimal — every changed line answerable to "why is this line in this change"?

## The report

- [ ] First sentence = the outcome. (Not the journey, not the preamble.)
- [ ] States what was verified and *how*, what wasn't and *why* — residual risk named, not laundered into "should work"?
- [ ] Assumption ledger disclosed (every Type 2/3 interpretation made along the way)?
- [ ] Skips, workarounds, and discovered-but-deferred issues listed?
- [ ] Everything important in the FINAL message (nothing stranded mid-turn), written in full sentences a tired reader parses once?
- [ ] Last paragraph is not a plan, a promise, or a permission question. (If it is — keep working.)
