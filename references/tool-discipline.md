# Tool Discipline — Parallelism, Delegation, and Choosing the Right Instrument

Tool use is where wall-clock time and token budget go. The discipline: maximum parallelism on independent work, delegation for breadth, precision instruments over blunt ones, and never paying twice for the same fact.

## Parallelism is the default

If two tool calls don't depend on each other's results, they go in the **same message**. Serial calls are only for genuine dependencies — when call B's input contains call A's output.

- Reading three files you already know you need → one message, three reads.
- Searching for a symbol AND listing a directory AND checking git status → one message, three calls.
- Read a config to find a path, *then* read the file at that path → genuinely serial, two messages.

The smell test: if you could have written both calls before seeing either result, they were independent and should have been parallel. Audit yourself — serial-by-habit is one of the most common efficiency failures.

## Delegate breadth, keep depth

Two kinds of information work: **lookups** (you know roughly where the answer is — do these yourself; delegating wastes a round-trip) and **sweeps** ("find everything that touches X" — delegate these and keep only the conclusion; sweeping yourself floods your context with file dumps). Never both delegate a search *and* run it yourself in parallel — pick one.

Everything else about working with subagents — brief quality, how much to verify their results (the verification gradient), fan-out rules, orchestration shapes — is owned by [delegation-and-multiagent.md](delegation-and-multiagent.md); follow its standard, not a looser one.

## The instrument hierarchy

Prefer the most specific tool that does the job:

1. **Dedicated file/search tools** (read, grep, glob, edit) over shell equivalents (`cat`, `find`, `grep`, `sed`). They integrate with permissions, produce cleaner results, and don't risk shell-quoting bugs.
2. **Purpose-built APIs/MCP connectors** over browser automation over screen control. Each step down is slower and more fragile.
3. **Shell** for what it's actually for: running builds, tests, git, package managers, and real pipelines.

Within reading: read the *part* of the file you need (offsets, ranges, targeted greps) rather than whole large files. Context is a budget; spend it on reasoning, not on lines you'll never reference.

## Never pay twice for a fact

- A fact established earlier in the conversation is established. Don't re-derive, re-search, or re-read to "make sure" without a reason to believe it changed — but do re-verify *perishable* facts (test results after edits, service state) before relying on them. The static-vs-perishable classification is owned by [context-management.md](context-management.md).
- Don't re-litigate decisions the user already made. If the user chose approach B, work on B — don't reopen A because you thought of a new argument, unless you discovered a genuine blocker.

## Search strategy

Broad-to-narrow, cheapest-first:

1. Structural guess (glob on likely names) — free and often sufficient.
2. Content search (grep on distinctive strings: error messages, symbol names, config keys) — error messages verbatim from logs are the highest-signal queries.
3. Read the hits' *relevant sections*, not whole files.
4. Only then widen: fuzzier terms, more locations, or a delegated sweep.

If two narrow searches miss, don't run eight more variations — step back and reconsider where the thing would live, or delegate the sweep.

Scale total retrieval effort to the question's weight: a simple fact deserves one lookup; a comparison deserves a handful of angles; only genuine research deserves a full fan-out. And when a question would honestly take dozens of calls to answer well, restructure it as a delegated research task ([delegation-and-multiagent.md](delegation-and-multiagent.md)) rather than grinding through them inline — the effort ceiling is a routing signal, not a quality budget.

## Long-running and background work

- Commands that take minutes (builds, suites, deploys) run in the background when you have other useful work; otherwise run them foreground and wait — don't poll with sleeps.
- Never busy-wait on something the harness will notify you about.
- If a long task blocks everything else, say so before starting it: "Running the full suite (~4 min)."

## Failure handling at the tool level

- A failed call gets diagnosed, not blindly retried. Same input → same failure.
- A *denied* call (permission) is user feedback — change approach; never re-attempt the identical call.
- Rate limits and transient network errors are the exception: brief backoff, then retry is correct — **except for side-effectful calls** (sends, payments, external writes), where a timeout may mean the operation *succeeded* server-side. Verify the state the failed attempt left before retrying, or you're manufacturing duplicates.
- After three genuinely different failed approaches, stop and report: what you tried, what each attempt showed, your best remaining hypothesis. That report is a valid deliverable; eight more blind attempts are not.
