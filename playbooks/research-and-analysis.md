# Playbook: Research and Analysis
*Read when: the deliverable is an answer or recommendation built from sources you must find, grade, and verify.*

**Goal:** an answer the user can act on, with its confidence, its sources, and its dissent visible. Research fails two ways: the shallow sweep that miscounts as thoroughness, and the confident synthesis of sources that were never checked against each other.

## Phase 0: Sharpen the question

- **Convert the topic into questions.** "Look into vector databases" becomes "which vector database fits our scale of about ten million embeddings, our Postgres-based stack, and a small team's ops appetite?" A question has a completion state; a topic does not.
- **Identify the decision behind the question.** Research that informs a purchase needs pricing rigor; research for orientation needs breadth. Calibrate depth to consequence, per [user-calibration.md](../references/user-calibration.md).
- **Search internal sources first**: the project's notes, the codebase, prior reports, and the user's own context, per [memory-and-persistence.md](../references/memory-and-persistence.md). Re-researching the known is the field's most common waste.

## Phase 1: Sweep wide before drilling deep

- **Multiple angles, not multiple repetitions.** Vary the phrasing, the source type, and the vantage point: documentation, issue trackers, benchmarks, practitioner writeups, primary data, the vendor's claim and the user's complaint. Eight variations of one query is one search with extra steps.
- **Fan out when the harness allows**, per [delegation-and-multiagent.md](../references/delegation-and-multiagent.md): parallel sweeps per sub-question or source type, with the synthesis kept by you.
- **Track provenance from the first note.** Every claim gets its source attached as collected; retrofitting citations after synthesis is where attribution errors are born.
- **Set the minimum before synthesis**: at least one primary source, one critical or dissenting source, and one dated source for anything that moves. Below that bar you have a lead, not a finding.
- **Notice the shape of what is missing.** No independent benchmarks? Every source traces to one vendor post? Nothing newer than 2024? The gaps are findings.

## Phase 2: Grade the evidence and run source hygiene

Not all sources weigh the same, and the weighting is the analyst's actual job.

- **Primary beats secondary.** The changelog beats the blog post about it; the pricing page beats the comparison article.
- **Independent beats interested.** A vendor's benchmark of its own product is a claim, not a measurement. Note the incentive of every load-bearing source.
- **Recent beats stale for anything moving.** Version-sensitive claims carry dates or they carry nothing.
- **Convergence is evidence only when sources are independent.** Five articles paraphrasing one press release is one source with an echo.
- **AI-generated content is its own source class.** Pages, answers, and summaries produced by a model are unverified by construction, however fluent. Treat them as leads to a primary source, never as the source, and say when a claim traces only to generated text.
- **A fetch tool's summary is not the page.** Open the page and read the passage that carries the claim. A summary can invert a caveat or drop the date.
- **Absence of evidence is reportable.** "I found no independent verification of X" changes decisions.

## Phase 3: Verify the load-bearing claims

The claims your conclusion stands on get adversarial treatment, per [verification.md](../references/verification.md).

- **Search for the refutation.** "X doesn't scale," "X problems," "migrating away from X." Confirmation-shaped searching finds confirmation-shaped results.
- **Open every URL you will cite and confirm it says what you claim**, in the passage you will point to, as of today. A citation you did not open is a hallucination risk with a link on it.
- **Check the concrete claims directly**: the price against the pricing page today, the API against the current docs, the quote against its original context.
- **Prefer hands-on where possible.** An hour testing the actual library answers questions no reading settles.
- Claims that survive refutation are **verified**; claims you could not check are **reported but unverified**, and the report keeps them apart.

## Phase 4: Synthesize for the decision

- **Lead with the answer to the sharpened question**, per [communication.md](../references/communication.md), then the evidence, then the dissent, then the method.
- **Show the disagreement; do not average it away.** "Sources conflict on self-hosting cost: the vendor claims X, two practitioner writeups report three to four times that, and the practitioners include ops labor the vendor excludes" beats a midpoint no source said.
- **State confidence per conclusion with its driver**: "high, primary docs and hands-on verified" against "low, single dated vendor-authored source."
- **Name the open questions and their price**: what would settle each, so the user can buy more certainty if the decision warrants it.
- **Recommend**, per [planning-and-decisions.md](../references/planning-and-decisions.md). Recommendation first, strongest alternative named, the one fact that would flip it.

## Exit criteria

- [ ] The question has a stated completion state and the decision behind it is named.
- [ ] Internal sources were searched before external ones.
- [ ] At least one primary, one critical, and one dated source sit behind the synthesis.
- [ ] Every cited URL was opened and says what is claimed, with the date noted.
- [ ] Generated content is labeled as such wherever it is the only trace for a claim.
- [ ] Verified and unverified claims are kept apart in the report.
- [ ] The report leads with the answer and ends with a recommendation and the fact that would flip it.

## Anti-patterns

- **The first-page oracle.** *Tell:* synthesis from whatever ranked highest. *Fix:* grade by evidence, not by rank.
- **The echo count.** *Tell:* "multiple sources confirm," all quoting one origin. *Fix:* trace to the origin and count it once.
- **The dateless claim.** *Tell:* a price or limit with no as-of date. *Fix:* every moving claim carries its date.
- **The unopened citation.** *Tell:* a link in the report that nobody opened. *Fix:* open it and quote the passage.
- **The summary as source.** *Tell:* a fetch tool's summary cited as the page. *Fix:* read the page.
- **The generated authority.** *Tell:* a model-written page treated as a primary source. *Fix:* follow it to a primary source or label it.
- **The both-sides mush.** *Tell:* contradictory sources averaged into a number nobody published. *Fix:* surface the conflict and its cause.
- **The verdict dodge.** *Tell:* ten pages of findings, no recommendation. *Fix:* recommend, with the flipping fact.
- **The unbounded dig.** *Tell:* research with no stop condition. *Fix:* stop when the marginal search stops changing the answer.
