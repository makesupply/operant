# Playbook: Data Reporting

**Goal:** deliver numbers a decision-maker can trust — profiled at the source, reconciled to a known control, precision matched to the data's actual reliability, and every metric traceable to the exact query that produced it. This complements analysis work ([data-work.md](data-work.md)); the shape here is a pipeline you *ship on a cadence* — pull, transform, report — where the same number goes out again next period, often unattended.

## Phase 0 — Orient and profile before computing

A number computed on unprofiled data is a guess with decimals. Before any aggregate:

- **Shape**: row counts, date range covered, and grain — does one row mean one order, one line-item, one session? Every downstream total inherits the grain; get it wrong and the whole report is wrong at scale.
- **Completeness**: null rates per column you'll report on, and whether the current period is *complete*. A month-to-date pull dressed up as a monthly total is the most common false number in reporting.
- **Units and encoding**: currency (and mixed currencies), units (cents vs. dollars, grams vs. kilograms), and timezone of every timestamp. A report that silently mixes UTC and local time is wrong on every daily boundary.
- **Semantics from the source, not the column name**: `revenue` — gross or net, refunds in or out? State your reading as an assumption when no data dictionary settles it ([data-work.md](data-work.md)).
- **Sensitivity screen**: if the data describes people, minimize — profile with aggregates and masked samples, keep individuals out of the report body unless the deliverable is explicitly about them ([communication.md](../references/communication.md)).

## Phase 1 — Transform in checkable steps

- **Keep one reconciliation total alive end-to-end.** The grand total at the raw layer must survive every join and filter, or every loss is accounted for ("dropped 340 rows: 290 test accounts, 50 null join keys"). Row counts before and after every join, as a habit — the silent fanout that triples a total is invisible at the aggregate.
- **Filters are decisions — log them.** Every exclusion goes in the methodology note with its reason. "Excluding internal orders" changes the answer; the reader must know it happened.
- **Prefer reproducible over manual.** Next period's report is a re-run, not a re-derivation — a script or query beats hand-edited spreadsheet steps. Any unavoidable manual touch-up gets listed.

## Phase 2 — Reconcile to a known control

A total that "looks about right" is unverified. Tie every headline number to something computed independently:

- **The source system's own total**: the platform dashboard, the ledger, the count the owning team already trusts. If your number and theirs disagree, one of you is wrong and the report can't ship until you know which.
- **Last period**: a metric that moved 10× or flatlined against a stable history is a reconciliation failure until explained.
- **A hand count**: for small or high-stakes figures, count it a second way.

Report the reconciliation, not just the number: "revenue $412K, ties to the billing dashboard within $80 (rounding on refunds)." A number with no control behind it is a number on faith.

## Phase 3 — The plausibility gauntlet

Before believing your own output, attack it. For every headline number, check three things:

- **Magnitude**: is it in a sane range against an external anchor — per-unit economics, prior periods, order of magnitude?
- **Direction**: did it move the way the business would predict, and if it moved the other way, do you know why?
- **Shape**: does the distribution make sense, or is one account, one day, or one outlier creating the whole result? A conclusion one row creates is a fact about that row.

Investigate the surprising number *before* shipping it. A 40% jump is a pipeline bug — a duplicated load, a backfill, a changed filter — until traced to a real cause. "Interesting result" and "data error" are identical at the aggregate level; the trace is the only thing that tells them apart.

## Phase 4 — Honest precision and traceability

- **Round to the meaningful digit.** Four decimals on noisy data is a lie told with precision. "Roughly $410K (±5%, unreconciled refunds)" beats "$412,847.23" when the pipeline doesn't support cents-level trust.
- **Separate measured from modelled.** A number you counted and a number you estimated or forecast are different kinds of thing — label the estimates, and never let a projection inherit the authority of a measurement.
- **Every metric traces to its query.** Never state a figure you can't reproduce on demand: the exact filter, date range, and definition that produced it, kept with the report. When someone challenges a number next week — and they will — the answer is the query, not your memory.

## Phase 5 — Recurring delivery

A report that ships on a schedule inherits the full unattended discipline ([recurring-automation.md](recurring-automation.md)). The reporting-specific hazards:

- **Idempotent.** Re-running for the same period produces the same report, not a duplicate send or a doubled total.
- **Fail loud on missing or partial data.** Validate at the top: did every source arrive, is the period complete, are the row counts in their normal band? A job that limps forward on a half-loaded table ships a confident, smaller, wrong number on schedule.
- **The report must testify to its own inputs.** If it ran on stale or partial data, the report says so in the body — "based on data through 14:00; the evening feed had not landed" — rather than silently shipping a smaller number that reads as a real decline. Silent partiality is the recurring-report nightmare, because it looks exactly like news.

## Phase 6 — Lead with the finding

Lead with the number and what it means, then the reconciliation, then the method ([communication.md](../references/communication.md)). The decision-maker needs the finding first; the methodology is the footnote that makes it auditable, not the opening act. State what would change the answer — "this assumes refunds land in the order month; if they land in refund month, Q2 drops ~3%."

## Anti-patterns

- **The dateless metric.** *Tell:* a number with no period, no as-of, no timezone attached. *Fix:* every figure carries its date range and the boundary convention; "up 12%" names both periods and the base size.
- **The silent mismatch.** *Tell:* currencies, units, or timezones combined without anyone deciding they were compatible. *Fix:* profile units and timezone in Phase 0; convert explicitly and note the conversion.
- **The average of averages.** *Tell:* a headline rate computed by averaging per-group rates, ignoring their sizes. *Fix:* aggregate from the raw numerator and denominator, weighted by volume.
- **The unreconciled total.** *Tell:* a grand total shipped because it "looks about right," tied to nothing. *Fix:* reconcile to a source control or last period before it leaves; report the tie-out.
- **The undisclosed partial.** *Tell:* a scheduled report that ran on stale or incomplete data and shipped the smaller number as if it were real. *Fix:* fail loud on incompleteness, or disclose the partiality in the report body.
- **The false-precision decimal.** *Tell:* six significant figures on a number built from ±20% assumptions. *Fix:* round to the digit the data actually supports; separate measured from modelled.
