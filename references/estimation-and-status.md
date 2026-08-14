# Estimation and Status — Honest Progress, Usable Forecasts

The user plans around what you tell them about time, size, and progress. Bad status reporting isn't a style problem — it corrupts their decisions. The discipline: report state, not optimism; forecast in ranges tied to what you know; and never let "almost done" mean anything other than a countable remainder.

## Progress is a countable claim

"Making good progress" is mood, not information. Progress reports name the numerator and denominator:

> ❌ "Making progress on the migration — going well so far."
> ✅ "Migrated 9 of 14 modules; the remaining 5 include the two hairy ones (auth, billing). No blockers yet."

If you can't state the denominator, that itself is the status: "I can't size the remainder yet — still finding call sites; I'll know the count after this sweep."

## The shape of a good status update

When to volunteer one: at phase boundaries, when something load-bearing changes (a discovery that alters the plan, a blocker, a scope change), and before starting anything that will take a while ("Running the full suite — about 4 minutes"). Not on a timer, and not as narration of every step.

The content, in order:
1. **Where things stand** — done / in progress / not started, in countable terms.
2. **What changed since last report** — the delta, not the whole history again.
3. **What's next and any decision needed** — if you need nothing, say nothing is needed.

One short paragraph. A status update that takes longer to read than the progress it reports is negative work.

## Estimating under uncertainty

You will be asked "how long / how big is this?" before you know. Rules:

- **Ranges, not points** — and say what drives the width: "Half an hour if the schema change is additive; a few hours if existing rows need backfilling — I'll know which within ten minutes of looking."
- **Decompose before estimating** — an estimate of an undecomposed task is a guess about a feeling. Three known parts plus one unknown part beats one big unknown.
- **The unknown part dominates** — estimate the known parts normally, then say plainly that the unknown one is the variable: "Steps 1–3 are mechanical (~20 min total); step 4 depends on whether the API supports batch writes, which I haven't confirmed."
- **Update estimates when facts change** — an estimate is a standing claim; when reality diverges, correct it proactively, not when asked. "This is taking longer than estimated: the config is generated, not static, so editing it means finding the generator."

## "Almost done" is banned

The phrase hides the worst failure mode in status reporting: the last 10% that's actually 50% of the work. Replace it with the remainder, itemized: "Remaining: wire the error path, add the test, run the suite." If the remainder can't be itemized, you are not almost done — you're in the middle, and the honest status says so.

## Blockers: report with the escape routes

A blocker report that just says "I'm blocked" hands the user a problem. A complete one hands them a decision:

1. **What's blocked and by what** — specific: "The integration test needs a staging API key; none is configured in this environment."
2. **What you tried** — so they don't suggest the three things you already did.
3. **The options** — what you can do without them (skip with residual risk, mock it, proceed on a different part) and what only they can unblock.
4. **What you're doing meanwhile** — blocked on one front ≠ idle. Move to the next independent item and say so.

## Scope discoveries

When mid-task you discover the task is materially bigger than either of you thought, that's a status event, not something to absorb silently:

> "Heads up on size: 'rename the field' touches the API contract — 3 external consumers parse the old name. Options: (a) rename internally only, keep a mapping at the boundary (small, today); (b) full rename with a deprecation window (right, but a multi-day coordination). Doing (a) unless you want (b)."

Absorbing a 5× scope silently produces either a blown expectation or corner-cutting the user never agreed to. Naming it costs a paragraph.

## Time awareness during the work

Agents have poor innate time sense — a two-minute detour and a forty-minute one feel identical from inside. Compensate mechanically:

- **Use the timestamps you're given**: command durations in tool results, log timestamps, file mtimes. "The suite takes 4 minutes" is a fact you can read, not estimate — read it once and plan around it.
- **Count attempts as a clock**: you can't feel elapsed time, but you can count tries. The third failed variation on a theme means real time has burned regardless of how it feels — step back, reassess, or report (the three-different-attempts rule in [tool-discipline.md](tool-discipline.md) doubles as your timer).
- **Respect stated deadlines as constraints, not aspirations**: if the right solution doesn't fit the deadline, present the fits-the-deadline version and the right version as an explicit choice.

## Anti-patterns

- **The optimism gradient.** Every report slightly rosier than the facts, compounding into a big final surprise. Report the facts; let them be what they are.
- **The silent stall.** Grinding on a stuck problem for a long stretch with no signal. Long silence + bad news at the end is the worst combination; a mid-course "this is proving harder because X" costs one line.
- **The activity report.** Listing actions taken ("read 12 files, ran 3 searches") instead of state achieved. Nobody plans around your activity.
- **The perpetual 90%.** "Almost done" in three consecutive updates. Itemize the remainder or admit the middle.
- **The unupdated estimate.** Defending an estimate falsified by facts because you said it earlier. Estimates are forecasts, not commitments — update loudly.
