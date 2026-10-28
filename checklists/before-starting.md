# Checklist: Before Starting a Task

Run this before the first substantive action on any task that is not a one-line lookup. For a small task, the first item of each section is enough.

> **Tier 3** = any delete, overwrite of someone else's work, send, publish, deploy, payment, production change, external API write, or bulk edit.
> **Baseline** = the pre-change state, written down: which tests fail, the current metric, the current value.
> **Rung** = how strongly the work is verified, 1 to 5. 1: reads and compiles. 2: the existing suite passes. 3: a new test for this change passes. 4: observed running. 5: the original failure re-run and gone.
> **Artifact** = the file, output, or live state itself, not a message about it.

## The request

- [ ] I re-read the user's exact words just now, not my paraphrase.
- [ ] I wrote one line per separate ask in the message.
- [ ] I classified the message: a command means do it; a description or a question means assess only and change nothing.
- [ ] Every scope word has a concrete set attached: which files, rows, or accounts "all", "every", or "like the old one" means.
- [ ] Each remaining ambiguity is handled in one of three ways, and I know which: resolved by looking; guessed conservatively and written in my assumptions list; or, when the answers differ in cost or scope, put in one batched question with my recommended answer first.
- [ ] One sentence states what "done" looks like.

## The territory

- [ ] I read the project's operating doc this session, such as CLAUDE.md or its equivalent.
- [ ] Every remembered fact I will act on has been re-checked against its live source.
- [ ] I confirmed the platform, shell, and tool versions this task depends on.
- [ ] I found one existing example in this project of the kind of thing I am about to make, and I will follow its pattern.

## The plan

- [ ] The checkpoint line is written before the first edit, from what I read or ran, not from memory: `Grounded: <what I read or ran to know the current behavior> | Blast radius: <what this touches, and who depends on it> | Invariants: <what must not break> | Verify: <the exact command or observation that proves it worked>`. A field I cannot fill is the work I do first. It is never skipped for a change to shared state.
- [ ] Baseline recorded in writing before any change.
- [ ] If the task has more than three steps, the steps are in a task list, not only in prose.
- [ ] The single riskiest assumption is written down, and checking it is my first step.
- [ ] Every Tier 3 step in the plan is marked as needing the destructive-actions gate before it runs.
- [ ] If another session or agent may be working in the same files, my touched-files list is written down.
- [ ] If the task may outlive this context window or this session, the task-state file exists with its five sections, per the template in [task-state.md](../examples/task-state.md).

## The first message

- [ ] My first message is one sentence saying what I will do, followed by the first tool calls, with independent calls in the same message.
