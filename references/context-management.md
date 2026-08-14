# Context Management — Working Well When the Window Is the Bottleneck

Context is working memory, and it is finite. Long sessions degrade not because the model gets dumber but because the signal (the task, the constraints, the decisions) gets diluted by noise (file dumps, dead ends, stale state). The discipline: protect the signal, shed the noise, and leave durable traces outside the window.

## The context budget mindset

Every token you pull into context competes with the task for attention. Spend deliberately:

- **High-value context**: the user's actual words, constraints and decisions made this session, the specific code/data under change, verification results.
- **Low-value context**: whole files read for one function, broad search dumps, repeated re-reads of unchanged files, verbose tool output nobody will reference again.

Before any large read, ask: *which lines of this will I actually use?* Read those. A 2,000-line file read for a 12-line function is a 99% waste with a compounding cost — it's still displacing signal ten turns later.

## Anchors: restate the load-bearing facts

In long sessions, periodically re-anchor — one short paragraph restating: the goal in the user's words, the key decisions so far, and the current state of the work. Do this:

- After finishing a major phase.
- After any long detour (a debugging rabbit hole, a big research sweep).
- When you notice yourself about to re-derive something you suspect was already established.

Re-anchoring costs three sentences and prevents the two expensive failures of long sessions: drifting from the original request (solving a nearby-but-different problem), and re-doing work already done.

## Surviving summarization and compaction

When a harness compacts or summarizes history, details die: exact values, file paths, error strings, half-made decisions. Defend against this proactively:

- **Write state to disk, not just to chat.** Task lists, decision logs, intermediate results, and long findings go in files (a scratchpad, a notes file, the project's docs). Files survive; conversation may not.
- **Make your final messages self-contained.** A message that says "applied the fix discussed above" is worthless after compaction; "changed the retry backoff in `client.py` from fixed 1s to exponential (cap 30s)" survives.
- **Keep a running task list for multi-step work** — in whatever task/todo mechanism the harness offers, or a plain file. The list is the thread you follow back after any interruption.

After a compaction, treat the summary as a briefing, not gospel: verify any detail you're about to act on (does the file still exist? did that test actually pass?) before building on it.

## Don't re-derive; do re-verify

Two categories of established facts, opposite treatments:

- **Static facts** (a config value, an architectural relationship, a user decision) — established once, trusted thereafter. Re-searching these is pure waste.
- **Perishable facts** (test results, service state, file contents *after you edited them*) — stale the moment anything relevant changes. Re-check before relying on them.

The failure modes are symmetric: re-deriving static facts burns budget; trusting perishable facts causes wrong actions. Classify before you decide.

## Dead ends: close them, don't carry them

When an approach fails, close it explicitly in one sentence — "the cache theory is dead: TTLs were correct all along" — and stop referencing it. Unclosed dead ends linger as ambient confusion; three turns later you (or the summarizer) can't tell which hypothesis won. State transitions out loud: what's dead, what's alive, what's next.

The same applies to **errors**: compact them, don't accumulate them. Three raw stack traces from the same failing loop teach nothing the first one didn't, and they crowd out signal for the rest of the session. Keep the distilled lesson ("attempt 2 failed identically — the flag isn't reaching the subprocess") and let the raw dumps go; re-fetch a full trace only when you need to re-examine it.

## The long-task pattern

For work spanning many steps or sessions:

1. **Externalize the plan** at the start — a numbered list in a file or task tracker, not just in prose.
2. **Update it as you go** — mark items done *when verified done*, add discovered items, never let it silently diverge from reality.
3. **Checkpoint at boundaries** — after each major item, one line of durable state: what's done, what's verified, what's next.
4. **On resume** (new session, post-compaction), read the checkpoint first, verify the last claimed state, then continue — don't trust, then act; verify, then act.

## Reading discipline quick reference

| Situation | Do | Don't |
|---|---|---|
| Need one function | Read that range (grep for it first) | Read the whole file |
| Need the shape of a module | Read exports/signatures/docs | Read every implementation |
| Broad "how does X work here" | Delegate the sweep, keep the summary | Stream 30 files through your own context |
| Same file, third time, unchanged | Use what you know | Re-read "to be safe" |
| Same file, after your edit | Re-read the changed region if acting on it | Assume the edit landed as intended without having checked the edit result |
