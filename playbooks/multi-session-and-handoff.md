# Playbook: Multi-Session Projects and Handoff
*Read when: you resume work from a previous session or hand work to the next session or agent.*

**Goal:** work that spans sessions or agents resumes from verified state, never from memory or from a note alone.

## Phase 0: Orient

Read the handoff document, then open the artifact it describes. Where they disagree, the artifact wins; correct the note before any other step. Verify the note's last claim before building on it. Record the resuming step and the observed state in the task-state file. Load what the note says to load first.

## Phase 1: Verified increments

Work in steps that each leave a checkpoint: a commit, a saved file, a tracker row. Update the task-state file after every verified item, because a session can end at any tool call. Never redo a step the note marks done without stating why you doubt it. On a shared checkout, follow [shared-checkout.md](shared-checkout.md).

## Phase 2: Adversarial self-check

Before handing off, read your own document as a stranger. Can they find the files, the next step, the open questions, and what is unverified? Does every "done" line say how it was verified? Redact secrets and personal identifiers; the document becomes a prompt. The test: a new agent resumes from the document plus the disk alone.

## Phase 3: Honest report

Write the handoff in the shape defined in [concurrency-and-handoffs.md](../references/concurrency-and-handoffs.md) under "Handing off", from the template in [handoff-document.md](../examples/handoff-document.md). Keep these on separate lines: done and verified, with evidence; done and unverified; in progress, with its exact state; the next three steps; questions only the user can answer; what the reader must not redo. Save it where the harness or the project keeps session files, and tell the user the path.

## Exit criteria

- [ ] The artifact was opened and checked against the note before work resumed.
- [ ] The task-state file was updated after the last verified item.
- [ ] The handoff separates verified from unverified and names the next three steps.
- [ ] Secrets and personal identifiers are absent, and the user knows the path.

## Anti-patterns

**The memory resume.** *Tell:* work continued from recollection of the last session. *Fix:* read the handoff, then the artifact.
**The trusted handoff.** *Tell:* the note said "deployed" and the agent built on it unread. *Fix:* verify the claim at the live source first.
**The silent abandonment.** *Tell:* a session ended at eighty percent with no record of the rest. *Fix:* update the task-state file after every item.
**The duplicated step.** *Tell:* a step marked done was redone on a hunch. *Fix:* state the doubt, read the artifact, then decide.
**The restated artifact.** *Tell:* the handoff pastes the plan, the diff, or the ledger. *Fix:* reference by path; a copy drifts from its source.
