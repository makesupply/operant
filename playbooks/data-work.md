# Playbook: Data Work

**Goal:** numbers the user can act on without re-checking them. Data work has a property code doesn't: a wrong result usually *looks identical* to a right one. The whole discipline is building the cross-checks that make wrongness visible.

## Phase 0 — Meet the data before computing on it

Never run the real analysis as your first query. First, profile:

- **Shape and size**: row counts, column types, date ranges. Does the row count match expectations? (A "two-year dataset" with 3 months of rows is a finding before it's a bug.)
- **Nulls, duplicates, and denominators**: how many nulls per key column, are IDs actually unique, what does one row *mean* (one order? one line-item? one event?). Getting the grain wrong is the most expensive mistake in analysis — every downstream aggregate inherits it.
- **The weird tails**: min/max of every numeric you'll use. Negative quantities, 1970 timestamps, and 9999 placeholder values announce themselves in thirty seconds here and poison averages silently forever after.
- **The sensitivity screen**: does this data contain people — names, emails, addresses, purchase or health details? Then minimization applies to everything downstream ([security-posture.md](../references/security-posture.md)): profile with aggregates and masked samples (`c***@gmail.com`, `customer 4471`) rather than pasting real records into the transcript or report, and keep individuals out of examples, fixtures, and memory. The analysis needs distributions, not identities — except where the deliverable is explicitly about named individuals, which stays in the deliverable and nowhere else.
- **Semantics from the source, not the column name**: `revenue` — gross or net? refunds included? which currency? If a data dictionary or owner exists, check; if not, state your reading as an assumption ([ambiguity-and-requirements.md](../references/ambiguity-and-requirements.md)).

## Phase 1 — Build the analysis in checkable steps

- **Small verified steps, intermediate results inspected** — the analysis analogue of running tests between refactor steps. Compute the base table, *look at it* (a sample, a count, a spot-check row you can verify by hand), then aggregate.
- **Keep one reconciliation total alive end-to-end**: the grand total at the raw layer should survive every join and filter, or every loss should be accounted for ("dropped 340 rows: 290 test accounts, 50 nulls in the join key"). A join that silently duplicates or drops rows is the classic invisible error — row counts before and after every join, as a habit.
- **Filters are decisions — log them**: every WHERE clause and exclusion goes in the methodology note with its reason. "Excluding refunds" changes the answer; the reader must know.
- **Prefer reproducible over manual**: a script/query that regenerates the result beats hand-edited spreadsheet steps — next month's version of this request is a re-run, not a re-derivation. Manual touch-ups, if unavoidable, get listed.

## Phase 2 — The plausibility gauntlet

Before believing your own output, attack it:

- **Order-of-magnitude check against an independent anchor**: does the computed revenue roughly match what the finance dashboard says? Does per-unit anything fall in a sane range? A number with no external anchor is a number on faith.
- **Sum the parts against the whole**: segments should total ~100%; the breakdown should sum to the topline it decomposes.
- **Perturb it**: does the trend survive removing the single biggest account/day/outlier? A conclusion that one row creates is a fact about that row, not a trend.
- **Explain the surprises before shipping them**: a 40% week-over-week jump is a data bug until traced to a cause (a real event, a backfill, a duplicated load). "Interesting result" and "pipeline error" look identical at the aggregate level — the trace is what distinguishes them. If it survives the trace, *lead* with it; if unexplained, report it as unexplained, never silently smooth it.

## Phase 3 — Report numbers honestly

- **Answer first** ([communication.md](../references/communication.md)), with its precision matched to its reliability: "roughly $410K (±5%, unreconciled refunds)" beats "$412,847.23" when the pipeline doesn't support cents-level trust. False precision is a lie told with decimals.
- **Comparisons need denominators and baselines**: "up 12%" — versus what period, on what base size? Percentages on small denominators get flagged ("+50%, but n=4").
- **The methodology footnote, always**: source, date range, filters, grain, known exclusions. Three lines that make the number auditable and next quarter's re-run consistent.
- **Charts follow the same honesty**: axes from zero unless deviation is the story (then say so), no truncated-axis drama, labels a cold reader can parse.
- **State what would change the answer**: "this assumes refunds land in the order month; if they land in refund month, Q2 drops ~3%."

## Special cases

- **Someone else's spreadsheet**: expect merged cells, hand-typed totals that don't match the rows, hidden columns, and a second header row. Reconcile any pre-existing totals against your recomputation *first* — a mismatch means you've misread the structure, and it's their layout, not your math, until proven otherwise.
- **Joins across systems**: identity is never as shared as claimed. Sample the unmatched keys from both sides before trusting the match rate.
- **Time**: timezones, week-start conventions, and partial current periods corrupt more comparisons than all other causes combined. "This week vs. last week" with today at 2pm included is a lie by construction — truncate to complete periods or footnote it.

## Anti-patterns

- **The blind aggregate.** GROUP BY on data never profiled; the placeholder 9999s are in the average now.
- **The silent join fanout.** Row count tripled at step 3; every downstream number is 3× and nobody noticed.
- **The convenient exclusion.** Filters that were never disclosed, discovered when someone else's total disagrees.
- **The decimal costume.** Six significant figures on a number built from assumptions worth ±20%.
- **The unexplained jump, shipped.** The anomaly presented as insight without the trace that separates insight from bug.
- **The one-off artifact.** An answer no one can regenerate; next month's identical question starts from zero.
