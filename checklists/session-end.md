# Checklist: Session End

Run this before wrapping up any substantial session. The final message is covered by the Report section of [before-claiming-done.md](before-claiming-done.md); run that too.

> **Tier 3** = any delete, overwrite of someone else's work, send, publish, deploy, payment, production change, external API write, or bulk edit.
> **Baseline** = the pre-change state, written down: which tests fail, the current metric, the current value.
> **Rung** = how strongly the work is verified, 1 to 5. 1: reads and compiles. 2: the existing suite passes. 3: a new test for this change passes. 4: observed running. 5: the original failure re-run and gone.
> **Artifact** = the file, output, or live state itself, not a message about it.

## The work

- [ ] The current task is done and verified, or checkpointed with its state written down and a tracker row open.
- [ ] The task list matches reality: done items verified, discovered items added, stale items removed.
- [ ] If the task has a task-state file, it is updated to the verified state, and its one in-progress item is the true one.
- [ ] Uncommitted changes are committed by explicit path, or listed with a note saying why not.
- [ ] No orphan process, server, or scratch file remains in the project.

## Capture

- [ ] Each decision made this session is written to the durable layer with its reason.
- [ ] Each correction the user gave me is written where the next session reads first.
- [ ] Each non-obvious fact that cost real time is saved with the why and the how-to-apply.
- [ ] Where things stand and what is next is written where a cold start will find it.
- [ ] If the work continues in another session or another agent: the handoff document is written per [concurrency-and-handoffs.md](../references/concurrency-and-handoffs.md) § Handing off, with artifacts referenced by path and secrets redacted. Template: [handoff-document.md](../examples/handoff-document.md).
- [ ] Updates went into existing notes; no twin note was created; nothing now known false is left uncorrected.
- [ ] Append-only records were written through the project's designated append helper, with the date from its date authority where one exists, never by whole-file write or hand-typed date.
- [ ] No secret or personal record was pasted into a note, log, or memory this session.

## The final message

- [ ] It is self-contained: readable without the conversation.
- [ ] Loose ends are listed explicitly: deferred items, flagged follow-ups, things awaiting the user.
