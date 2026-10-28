# Context Management: Working Well When the Window Is the Bottleneck

Context is working memory, and it is finite. Long sessions degrade not because the model gets dumber but because the signal, meaning the task, the constraints, and the decisions, gets diluted by noise: file dumps, dead ends, stale state. The discipline: protect the signal, shed the noise, and leave durable traces outside the window.

## The context budget mindset

Every token you pull into context competes with the task for attention. Spend deliberately:

- **High-value context**: the user's actual words, constraints and decisions made this session, the specific code or data under change, verification results.
- **Low-value context**: whole files read for one function, broad search dumps, repeated re-reads of unchanged files, verbose tool output nobody will reference again.

Before any large read, ask which lines you will actually use, and read those. A 2,000-line file read for a 12-line function is a 99% waste with a compounding cost; it is still displacing signal ten turns later.

## Large results go to disk

When a search, a log, or an API response comes back large, save it to the scratchpad, keep one line in context stating the path and the finding that matters, and search the file for details later. Check a file's size before reading it whole; a single read can cost more context than the entire task. Before acting on a path remembered from an earlier turn, confirm it still exists. Files move, and a stale path acted on is a wrong action.

## Anchors: restate the load-bearing facts

Re-anchor when any of these fires: an item on the task list completes; fifteen tool calls have passed since the last anchor; or the harness has compacted the conversation. The anchor is three sentences: the goal in the user's words, the decisions made, the current state. Also re-anchor after a long detour and when you catch yourself about to re-derive something already established. Three sentences prevent the two expensive failures of long sessions: drifting into a nearby but different problem, and re-doing work already done.

## Surviving summarization and compaction

When a harness compacts or summarizes history, details die: exact values, file paths, error strings, half-made decisions. Defend against this proactively:

- **Write state to disk, not just to chat.** Decision logs, intermediate results, and long findings go in files. Files survive; conversation may not. The task-state file below is the primary one.
- **Make your final messages self-contained.** "Applied the fix discussed above" is worthless after compaction; "changed the retry backoff in `client.py` from fixed 1s to exponential (cap 30s)" survives.
- **Boundaries stated in chat do not survive compaction.** A rule meant to hold for the whole session lives in a file or in a permission rule, never only in a sentence you said earlier.

After a compaction, treat the summary as a briefing, not gospel: verify any detail you are about to act on before building on it.

## Don't re-derive; do re-verify

Two categories of established facts, opposite treatments:

- **Static facts**, such as a config value, an architectural relationship, or a user decision, are established once and trusted thereafter. Re-searching these is pure waste.
- **Perishable facts**, such as test results, service state, and file contents *after you edited them*, are stale the moment anything relevant changes. Re-check before relying on them.

Re-deriving static facts burns budget; trusting perishable facts causes wrong actions. Classify before you decide. This chapter is the canonical copy of that classification.

## Dead ends: close them, don't carry them

When an approach fails, close it in one sentence, such as "the cache theory is dead: TTLs were correct all along", and stop referencing it. Unclosed dead ends linger as ambient confusion; three turns later you, or the summarizer, cannot tell which hypothesis won. State transitions out loud: what is dead, what is alive, what is next.

The same applies to **errors**: compact them, do not accumulate them. Three raw stack traces from the same failing loop teach nothing the first one did not. Keep the distilled lesson and let the raw dumps go; re-fetch a full trace only when you need to re-examine it.

## The task-state file

Any task expected to outlive one context window, or to span more than one session, gets a state file before the first long stretch of work. Put it in the harness scratchpad or the project's designated working folder, never in the repository root. Keep five short sections and no others: Goal, in the user's words; Done, each item with the evidence that made it done; In progress, at most one item; Next, in order; Decisions and gotchas, each with the reason and an absolute date. A template and a filled example are in [../examples/task-state.md](../examples/task-state.md).

Update the file after every verified item and after every commit, not at the end. Re-read it at the start of every turn after a compaction, a resume, or a detour longer than a few tool calls, and before claiming done. After a compaction, trust the file and the artifact over the summary: re-run any check whose evidence you cannot point at in the file.

When the work continues in another session or another agent, write the handoff document described in [concurrency-and-handoffs.md](concurrency-and-handoffs.md) under "Handing off".

## One item in progress

Finish and verify the item you are on before opening the next, and let the task-state file show at most one item in progress. Three half-built items are not progress on any of them, and the next session cannot tell which half is trustworthy. Discoveries made while working an item go into Next, not into the work.

## Reading discipline quick reference

| Situation | Do | Don't |
|---|---|---|
| Need one function | Read that range (grep for it first) | Read the whole file |
| Need the shape of a module | Read exports/signatures/docs | Read every implementation |
| Broad "how does X work here" | Delegate the sweep, keep the summary | Stream 30 files through your own context |
| Same file, third time, unchanged | Use what you know | Re-read "to be safe" |
| Same file, after your edit | Trust the edit result the harness returned; re-read only shared files or when the harness tells you to | Re-read "to verify" what the edit contract already proved |
