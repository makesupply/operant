# Playbook: Data Work
*Read when: the deliverable is a number, a table, a chart, or a report built from data, whether produced once or on a cadence.*

**Goal:** numbers the user can act on without re-checking them. A wrong result usually looks identical to a right one, so the whole discipline is building the cross-checks that make wrongness visible.

## Phase 0: Meet the data before computing on it

Never run the real analysis as your first query. Profile first.

- **Shape, size, and period**: row counts, column types, date ranges, and whether the current period is complete. A month-to-date pull dressed up as a monthly total is the most common false number in reporting.
- **Grain, nulls, and duplicates**: what one row means, whether IDs are unique, how many nulls sit in each key column. Getting the grain wrong is the most expensive mistake, because every downstream aggregate inherits it.
- **Units and encoding**: currency, cents against dollars, the timezone of every timestamp. Mixed UTC and local time is wrong on every daily boundary.
- **The weird tails**: minimum and maximum of every numeric you will use. Negative quantities, 1970 timestamps, and 9999 placeholders announce themselves here and poison averages silently later.
- **The sensitivity screen.** If the data describes people, minimization applies downstream, per [security-posture.md](../references/security-posture.md): profile with aggregates and masked samples such as `customer 4471`, and keep individuals out of examples, fixtures, and memory.
- **Semantics from the source, not the column name.** Is `revenue` gross or net? Check the owner or the data dictionary; otherwise state your reading as an assumption, per [ambiguity-and-requirements.md](../references/ambiguity-and-requirements.md).
- **The missing input.** If the figure the task needs is not in the data you have, say so and stop, or show the answer parameterized on it. Never let the nearest available number stand in, per [verification.md](../references/verification.md).

## Phase 1: Build the analysis in checkable steps

- **Small verified steps.** Compute the base table, inspect a sample, a count, and a spot-check row you can verify by hand, then aggregate.
- **Keep one reconciliation total alive end to end.** The grand total at the raw layer survives every join and filter, or every loss is accounted for by count and reason. Count rows before and after every join.
- **Filters are decisions, so log them.** Every exclusion goes in the methodology note with its reason.
- **Prefer reproducible over manual.** A script that regenerates the result beats hand-edited spreadsheet steps, because next month's request is a re-run.

## Phase 2: Reconcile, then run the plausibility gauntlet

Before believing your own output, tie it to something independent and then attack it.

- **Reconcile to a known control first**: the source system's own total, the ledger, or last period's figure. If your number and the control disagree, one of you is wrong and the result cannot ship until you know which. Report the tie-out: "revenue $412K, ties to the billing dashboard within $80 on refund rounding."
- **Magnitude and shape**: does it sit in a sane range against per-unit economics and prior periods, does the breakdown sum to its topline, and does the trend survive removing the single biggest account, day, or outlier?
- **Explain the surprises before shipping them.** A 40 percent week-over-week jump is a pipeline bug until traced to a real event, a backfill, or a duplicated load. If it survives the trace, lead with it; if not, report it as unexplained and never smooth it.

## Phase 3: Report numbers honestly

- **Answer first**, per [communication.md](../references/communication.md), with precision matched to reliability. "Roughly $410K, plus or minus 5 percent on unreconciled refunds" beats "$412,847.23" when the pipeline does not support cents-level trust.
- **Separate measured from modelled.** Label the estimates, and never let a projection inherit the authority of a measurement.
- **Comparisons carry denominators and baselines.** "Up 12 percent" names both periods and the base size; "+50 percent, but n=4" gets its flag.
- **Every metric traces to its query.** Keep the exact filter, date range, and definition with the report, so a challenge next week is answered by the query, not your memory.
- **The methodology footnote, always**: source, date range, filters, grain, known exclusions. Charts keep axes from zero unless the deviation is the story.
- **State what would change the answer**: "this assumes refunds land in the order month; if they land in the refund month, Q2 drops about 3 percent."

## When it ships on a cadence

A scheduled report inherits the unattended discipline in [recurring-automation.md](recurring-automation.md). Two hazards are specific to reporting. Re-running for the same period must produce the same report, never a duplicate send or a doubled total. And the report must testify to its own inputs: if it ran on stale or partial data, the body says so instead of shipping a smaller number that reads as a real decline.

## Special cases

- **Someone else's spreadsheet.** Expect merged cells, hand-typed totals that disagree with the rows, hidden columns, and a second header row. Reconcile any pre-existing totals against your recomputation first; a mismatch means you misread the structure until proven otherwise.

## Exit criteria

- [ ] The data was profiled before the first aggregate: grain, period completeness, units, tails, sensitivity.
- [ ] One reconciliation total survives end to end, or every loss is accounted for.
- [ ] Every headline number ties to an independent control, and the tie-out is reported.
- [ ] Every filter is in the methodology note; measured and modelled figures are labeled apart.
- [ ] Every figure traces to a query that regenerates it.
- [ ] No real personal record appears in the transcript, the report, or memory.

## Anti-patterns

- **The blind aggregate.** *Tell:* a GROUP BY on data never profiled; the 9999 placeholders are in the average. *Fix:* profile tails and grain first.
- **The silent join fanout.** *Tell:* the row count tripled at step 3. *Fix:* count rows before and after every join.
- **The unreconciled total.** *Tell:* a grand total shipped because it looked about right. *Fix:* tie it to a control before it leaves.
- **The unexplained jump, shipped.** *Tell:* an anomaly presented as insight without the trace. *Fix:* trace it or report it as unexplained.
- **The undisclosed partial.** *Tell:* a scheduled report ran on incomplete data and shipped the smaller number as real. *Fix:* fail loud or disclose it in the body.
- **The proxy substitution.** *Tell:* the required cost was missing, so another party's price became the floor. *Fix:* name the gap; never borrow figures across parties or markets.
