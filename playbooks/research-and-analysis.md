# Playbook: Research and Analysis

**Goal:** an answer the user can act on — with its confidence level, its sources, and its dissent visible. Research fails two ways: the shallow sweep that miscounts as thoroughness, and the confident synthesis of sources that were never checked against each other.

## Phase 0 — Sharpen the question

- **Convert the topic into questions**: "look into vector databases" becomes "which vector DB fits our scale (~10M embeddings), our stack (Postgres shop), and our ops appetite (small team)?" A question has a completion state; a topic doesn't.
- **Identify the decision behind the question** — what will the user *do* with the answer? Research that informs a purchase needs pricing rigor; research for orientation needs breadth. Calibrate depth to consequence ([user-calibration.md](../references/user-calibration.md)).
- **Establish what's already known**: the user's context, prior notes, existing internal knowledge ([memory-and-persistence.md](../references/memory-and-persistence.md)). Re-researching the known is the field's most common waste.

## Phase 1 — Sweep wide before drilling deep

- **Multiple angles, not multiple repetitions**: vary the search modality — different phrasings, different source types (docs, issues, benchmarks, practitioner writeups, primary data), different vantage points (vendor's claim vs. user's complaint). Eight variations of the same query is one search with extra steps.
- **Fan out when the harness allows** ([delegation-and-multiagent.md](../references/delegation-and-multiagent.md)): parallel sweeps per sub-question or per source type; you keep the synthesis.
- **Track provenance from the first note**: every claim gets its source attached *as collected* — retrofitting citations after synthesis is where attribution errors are born.
- **Notice the shape of what's missing**: no independent benchmarks? all sources trace to one vendor post? nothing newer than 2023? The gaps are findings.

## Phase 2 — Grade the evidence

Not all sources weigh the same, and the weighting is the analyst's actual job:

- **Primary beats secondary**: the changelog beats the blog post about it; the pricing page beats the comparison article; the paper beats the tweet thread.
- **Independent beats interested**: a vendor's benchmark of their own product is a claim, not a measurement. Note the incentive of every load-bearing source.
- **Recent beats stale for anything moving**: version-sensitive claims (APIs, prices, limits, performance) carry dates or they carry nothing.
- **Convergence is evidence only when sources are independent** — five articles paraphrasing the same press release is one source with an echo.
- **Absence of evidence is reportable**: "I found no independent verification of X" is a finding that changes decisions.

## Phase 3 — Verify the load-bearing claims

The claims your conclusion stands on get adversarial treatment ([verification.md](../references/verification.md)):

- **Actively search for the refutation** — "X doesn't scale", "X problems", "migrating away from X". Confirmation-shaped searching finds confirmation-shaped results.
- **Check the concrete claims directly**: the price against the pricing page today, the API against the current docs, the quote against the original context.
- **Where hands-on is possible, prefer it**: an hour testing the actual library answers questions no amount of reading settles.
- Claims that survive refutation attempts are **verified**; claims you couldn't check are **reported-but-unverified** — the report distinguishes them.

## Phase 4 — Synthesize for the decision

- **Lead with the answer to the sharpened question** ([communication.md](../references/communication.md)) — then the evidence, then the dissent, then the method.
- **Show the disagreement, don't average it away.** "Sources conflict on self-hosting cost: the vendor claims X, two practitioner writeups report 3–4×; the practitioners' numbers include ops labor the vendor excludes" beats a mushy midpoint that no source actually said.
- **State confidence per conclusion, with the driver**: "high confidence (primary docs, hands-on verified)" vs. "low confidence (single dated source, vendor-authored)."
- **Name the open questions and their price**: what would settle each remaining unknown (a benchmark run, a sales call, a spike), so the user can buy more certainty if the decision warrants it.
- **Recommend** per [planning-and-decisions.md](../references/planning-and-decisions.md): the analyst who assembles all the evidence and then declines to weigh it has done half the job. Recommendation first, strongest alternative named, the one fact that would flip it.

## Anti-patterns

- **The first-page oracle.** Synthesizing from whatever ranked highest, weighting by rank rather than by evidence grade.
- **The echo count.** "Multiple sources confirm" — all quoting the same origin.
- **The dateless claim.** Prices, limits, and version behaviors reported without when-was-this-true.
- **The both-sides mush.** Averaging contradictory sources into a number nobody published instead of surfacing the conflict.
- **The verdict dodge.** Ten pages of findings, no recommendation, decision returned to sender.
- **The unbounded dig.** Research without a stop condition. Set the bar with the question; when the marginal search stops changing the answer, write it up.
