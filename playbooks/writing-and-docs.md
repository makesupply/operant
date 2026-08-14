# Playbook: Writing and Documentation

**Goal:** documents that do their job for a reader who isn't you, isn't here, and has thirty seconds. All the communication discipline ([communication.md](../references/communication.md)) applies; this playbook adds what's specific to *durable* writing — docs, READMEs, reports, proposals, runbooks — where the reader arrives months later without the conversation.

## Phase 0 — Every document has one reader and one job

Before writing a word, answer:

- **Who reads this, in what moment?** The 2am on-call engineer (runbook), the evaluating decision-maker (proposal), the new teammate on day one (README), the future maintainer wondering *why* (ADR/decision record). Each wants different content in a different order.
- **What should they be able to DO after reading?** Run the project, make the decision, execute the fix, stop re-asking the question. A document without a doable outcome is a diary entry.
- **What's the one thing they must not miss?** That goes first, not in section 4.

If a draft serves "everyone," it serves no one — split it or pick the primary reader and serve them fully.

## Structure: front-load ruthlessly

Durable documents are *scanned*, not read:

- **The first paragraph carries the whole message** — the inverted pyramid. A reader who stops there should leave correct, just less detailed.
- **Headings are claims, not labels**: "Retries mask the real failure" beats "Background." A reader scanning only headings should absorb the argument.
- **One idea per section; cut the rest.** The discipline is what you leave out — the tangent explained "for completeness" costs every future reader thirty seconds, forever, compounding.
- **Put reference material in reference shape**: tables for lookups, numbered steps for procedures, prose for reasoning. A procedure written as paragraphs is a runbook that fails at 2am.

## Writing that survives its author

- **No context-dependent references**: "as discussed", "the new approach", "the recent incident" — meaningless in six months. Name the thing, date the event, link the source.
- **Absolute dates, versions, and names** — "currently" and "the latest version" are stale on arrival ([memory-and-persistence.md](../references/memory-and-persistence.md)).
- **Examples over abstractions**: one concrete worked example (real command, real input, real output) teaches more than three paragraphs of description — and doubles as a verification artifact.
- **Say who does what**: passive-voice procedures ("the config should be updated") strand the reader; "update `config.yml`, then restart the worker" doesn't.

## Accuracy: docs are claims — verify them

A document asserting how a system works is a set of factual claims, and [verification.md](../references/verification.md) applies:

- **Run every command you document.** The README installation section written from memory is the most-broken artifact in software. Do the steps; paste the real output.
- **Check names against the source**: flags, endpoints, file paths, config keys — copy them from the code, don't reconstruct them.
- **For runbooks especially**: the procedure gets a dry-run (or a walkthrough against the real system's read-only state) before it's trusted. A wrong runbook is worse than none — it burns the 2am reader's only trust.

## Updating beats creating

Before writing a new document, check what exists ([memory-and-persistence.md](../references/memory-and-persistence.md)): the second document on a topic doesn't add knowledge, it adds *contradiction risk* — two docs drift, and future readers can't tell which is current. Update the existing one; restructure it if it's grown wrong; delete what's false. And when your code change falsifies a doc — the flag renamed, the step removed — updating that doc is part of the change, not a favor.

## Reports and proposals specifically

- **A report's spine**: answer → evidence → method → open questions. Not chronological. The narrative of your investigation is scaffolding — remove it before shipping (the travelogue anti-pattern).
- **A proposal's spine**: recommendation → why this over the alternative → cost/risk → what happens if we don't. Decision-makers read to decide; give them the decision shape, per [planning-and-decisions.md](../references/planning-and-decisions.md).
- **Numbers in documents follow the data honesty rules** ([data-work.md](data-work.md)): sourced, dated, denominated.
- **Length is a cost you impose on the reader.** The two-page version that gets read beats the twelve-page version that gets skimmed. Appendices exist for the twelve-page material.

## Quoting and borrowed material

Other people's words are load you carry, not filler you get for free:

- **Quote short and attribute always** — a line, not a passage, with the source named. Needing more than a sentence of someone else's words is the signal to paraphrase with attribution instead.
- **One short quote per source is a sound ceiling** for any deliverable; past that you're reproducing, not citing.
- **Never reproduce large spans of copyrighted material** — articles, lyrics, book passages — into deliverables. Summarize, cite, link. This is an IP obligation and a quality bar at once: borrowed bulk is filler wearing quotation marks.
- The same discipline applies in research syntheses ([research-and-analysis.md](research-and-analysis.md)) and marketing copy ([marketing-content.md](marketing-content.md)), where an unattributed borrowed claim is also a truth problem.

## Voice and register

Durable docs default to plain, direct, unhedged prose. Delete: throat-clearing ("This document describes…" — the title did that), hedges that carry no information ("it could be argued"), enthusiasm markers, and apology ("this is just a rough attempt"). Keep: honest uncertainty where it's real, stated as a fact about the claim ("untested on Windows"). Match any house style the project has; consistency beats preference here as in code.

## Anti-patterns

- **The chronology.** The document ordered by when you learned things instead of what the reader needs first.
- **The everything doc.** Serves the newcomer, the expert, and the auditor — reaches none of them.
- **The unrun README.** Installation steps composed from memory; broken at step 2 for every user forever.
- **The twin.** A new doc created beside the existing one; they disagree within a quarter.
- **The label headings.** "Overview. Details. Conclusion." — a scanner learns nothing.
- **The immortal "currently".** Time-relative language that made the doc false before its first anniversary.
