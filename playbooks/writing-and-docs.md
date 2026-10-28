# Playbook: Writing and Documentation
*Read when: the deliverable is a durable document such as a README, runbook, proposal, decision record, or any page a reader will open months from now.*

**Goal:** documents that do their job for a reader who is not you, is not here, and has thirty seconds. The communication discipline in [communication.md](../references/communication.md) governs every sentence; this playbook adds what is specific to writing that outlives the conversation.

## Phase 0: One reader, one job

Before writing a word, answer three questions.

- **Who reads this, in what moment?** The on-call engineer at 2am wants a runbook. The decision-maker wants a proposal. The new teammate wants a README. The future maintainer wants the decision record that says why. Each wants different content in a different order.
- **What should they be able to do after reading?** Run the project, make the decision, execute the fix, stop asking the question. A document without a doable outcome is a diary entry.
- **What is the one thing they must not miss?** That goes first, not in section 4.

A draft that serves "everyone" serves no one. Split it, or pick the primary reader and serve them fully. Then check what already exists, per [memory-and-persistence.md](../references/memory-and-persistence.md): a second document on a topic adds contradiction risk, not knowledge. Update the existing one, restructure it if it has grown wrong, and delete what is false.

## Phase 1: Outline as claims

Durable documents are scanned, not read. Build the outline before the prose.

- **Headings are claims, not labels.** "Retries mask the real failure" beats "Background." A reader scanning only headings should absorb the argument.
- **The first paragraph carries the whole message.** A reader who stops there leaves correct, just less detailed.
- **One idea per section; cut the rest.** The tangent explained "for completeness" costs every future reader thirty seconds, forever.
- **Reference material goes in reference shape**: tables for lookups, numbered steps for procedures, prose for reasoning. A procedure written as paragraphs is a runbook that fails at 2am.
- **Reports and proposals follow the spines in [research-and-analysis.md](research-and-analysis.md) Phase 4 and [planning-and-decisions.md](../references/planning-and-decisions.md).** A report runs answer, evidence, method, open questions. A proposal runs recommendation, why over the alternative, cost and risk, what happens otherwise. Numbers inside either follow [data-work.md](data-work.md).

## Phase 2: Draft with verified facts

A document asserting how a system works is a set of factual claims, and [verification.md](../references/verification.md) applies.

- **Run every command you document.** The installation section written from memory is the most-broken artifact in software. Do the steps and paste the real output.
- **Copy names from the source.** Flags, endpoints, file paths, and config keys come from the code, not from reconstruction.
- **Give one concrete worked example** with a real command, real input, and real output. It teaches more than three paragraphs and doubles as a verification artifact.
- **Write so the text survives its author.** No "as discussed," "the new approach," or "the recent incident." Name the thing, date the event with an absolute date, link the source. "Currently" and "the latest version" are stale on arrival.
- **Say who does what.** "Update `config.yml`, then restart the worker" works; "the config should be updated" strands the reader.
- **For runbooks, dry-run the procedure** against the real system's read-only state before trusting it. A wrong runbook burns the 2am reader's only trust.
- **Quote short and attribute always.** A line, not a passage, with the source named, and at most one short quote per source. Never reproduce large spans of copyrighted material; summarize, cite, link.

## Phase 3: Hostile re-read as the named reader

Read the draft once as the Phase 0 reader, in their moment, with their thirty seconds. Ask only these questions. Does the first paragraph give them the outcome? Can they do the thing after reading? Is anything they must not miss below the fold? Does any sentence depend on context they do not have? Is any claim unverified? Delete throat-clearing such as "This document describes," hedges that carry no information, enthusiasm markers, and apology. Keep honest uncertainty stated as a fact about the claim, such as "untested on Windows." Match the project's house style; consistency beats preference.

## Phase 4: Update, then report what changed

Place the text in the existing document where a reader will look for it. When a code change falsifies a doc, updating the doc is part of the change, not a favor. Report what the document now says, what it replaced, which commands you ran to verify it, and anything left unverified.

## Docs whose reader is an agent

An instruction file such as a project operating doc, a skill, or a system prompt is a document whose reader is a model. The same discipline applies with a sharper edge: a testable trigger, steps in order, one worked example, and no aspiration lists. Read [prompt-and-skill-authoring.md](prompt-and-skill-authoring.md) before writing one.

## Exit criteria

- [ ] The reader and their doable outcome are named, and the first paragraph serves them.
- [ ] Every heading is a claim a scanner can follow.
- [ ] Every documented command was run and its real output pasted.
- [ ] Every name, flag, and path was copied from the source.
- [ ] No relative time reference or context-dependent phrase remains.
- [ ] An existing document was updated rather than a twin created, and nothing now false was left standing.
- [ ] The report names what changed and what was verified.

## Anti-patterns

- **The chronology.** *Tell:* the document is ordered by when you learned things. *Fix:* order by what the reader needs first.
- **The everything doc.** *Tell:* it addresses the newcomer, the expert, and the auditor. *Fix:* pick one reader or split it.
- **The unrun README.** *Tell:* installation steps composed from memory, broken at step 2. *Fix:* run every step and paste the output.
- **The twin.** *Tell:* a new doc beside the existing one; they disagree within a quarter. *Fix:* update the existing one.
- **The label headings.** *Tell:* "Overview. Details. Conclusion." *Fix:* write each heading as the claim its section makes.
- **The immortal "currently."** *Tell:* time-relative language that made the doc false before its first anniversary. *Fix:* absolute dates, versions, and names.
- **The borrowed bulk.** *Tell:* paragraphs of someone else's text standing in for your own. *Fix:* one short attributed quote at most, then paraphrase with attribution.
