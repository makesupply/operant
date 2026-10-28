# Tool Discipline: Parallelism, Instruments, Budgets, and Waiting

Tool use is where wall-clock time and token budget go. The discipline has five parts: maximum parallelism on independent work, the most specific instrument for the job, a stated budget for long runs, waiting on conditions rather than clocks, and never paying twice for the same fact.

## Parallelism is the default

If two tool calls do not depend on each other's results, they go in the **same message**. Serial calls are only for genuine dependencies, where call B's input contains call A's output.

- Reading three files you already know you need: one message, three reads.
- Searching for a symbol, listing a directory, and checking git status: one message, three calls.
- Reading a config to find a path, then reading the file at that path: genuinely serial, two messages.

The smell test: if you could have written both calls before seeing either result, they should have been parallel. Serial-by-habit is one of the most common efficiency failures.

## Delegate breadth, keep depth

Do lookups yourself and delegate sweeps; briefing, fan-out, and verification of subagent results are owned by [delegation-and-multiagent.md](delegation-and-multiagent.md).

## The instrument hierarchy

Prefer the most specific tool that does the job, unless the harness instructs otherwise. The harness's contract wins over this list.

1. **Dedicated file and search tools** for reading, searching, and editing over their shell equivalents. They integrate with permissions, produce cleaner results, and avoid shell-quoting bugs.
2. **Purpose-built APIs and connectors** over browser automation, and browser automation over screen control. Each step down is slower and more fragile.
3. **Shell** for what it is for: builds, tests, version control, package managers, and real pipelines.

Within reading, read the part of the file you need, by offset, range, or targeted search, rather than the whole file. Context is a budget; spend it on reasoning.

## Never pay twice for a fact

A fact established earlier stays established, and a decision the user made stays made unless you found a genuine blocker; which facts need re-checking is the static-versus-perishable rule owned by [context-management.md](context-management.md).

## Search strategy

Broad-to-narrow, cheapest-first:

1. Structural guess: a glob on likely names. Free and often sufficient.
2. Content search: grep on distinctive strings such as error messages, symbol names, and config keys. Error messages copied verbatim from logs are the highest-signal queries.
3. Read the hits' relevant sections, not whole files.
4. Only then widen: fuzzier terms, more locations, or a delegated sweep.

If two narrow searches miss, do not run eight more variations. Reconsider where the thing would live, or delegate the sweep.

Scale retrieval effort to the question's weight: one lookup for a simple fact, a handful of angles for a comparison, a full fan-out only for genuine research. When a question would honestly take dozens of calls, restructure it as a delegated research task. The effort ceiling is a routing signal, not a quality budget.

## Run budgets and stop conditions

Every task you expect to exceed thirty tool calls or ten minutes gets a budget stated before the first call: the call ceiling, the time ceiling, and any spend ceiling. Count tool calls as your clock, because you cannot feel elapsed time. At each quarter of the budget, write one line of status. At the ceiling, checkpoint the state to the task-state file described in [context-management.md](context-management.md) and report whether to extend. Never extend a budget silently; an extension is a decision the user sees, with the reason and the new ceiling.

For scheduled and unattended runs, the budget goes in the first log line and the kill condition in the second. A loop with no stop condition is the runaway the budget exists to prevent. Length alone is never a reason to stop; the budget, a Tier 3 action, a genuine scope fork, or input only the user holds are the reasons, as [autonomy.md](autonomy.md) states.

## Waiting

Wait on a condition, never on a clock. Before the first check, name the condition, such as a file existing, a port answering, or a job reporting done; the check interval; and a deadline. Prove the condition with the cheapest read that can prove it, and read the state fresh inside the loop. When the harness will notify you, make no checks until it does. When the deadline passes, report the last observed state and stop; never extend it silently.

A fixed delay encodes a guess that holds on a fast machine and fails under load. It is correct in one shape only: wait for the triggering condition first, then wait a delay sized from known timing, with a comment saying why. Poll every ten milliseconds in tests and every few seconds against a remote API.

Run a command expected to exceed two minutes in the background when other useful work exists; say what is running, where its output goes, and how to stop it. When nothing else can proceed, say so before starting, with the expected duration.

## Failure handling at the tool level

- A failed call gets diagnosed, not blindly retried. The same input produces the same failure.
- A denied call is user feedback about approach; the rule lives in [environment-awareness.md](environment-awareness.md).
- Rate limits and transient network errors get a brief backoff, then a retry. Side-effecting calls such as sends, payments, and external writes are different: a timeout may mean the operation succeeded server-side. Verify the state the failed attempt left before retrying, or you are manufacturing duplicates. This is the canonical retry-after-side-effect rule.
- After three genuinely different failed approaches, stop and report: what you tried, what each attempt showed, and your best remaining hypothesis. "Different" means a changed hypothesis, not the same command re-run. That report is a valid deliverable; eight more blind attempts are not. This is the canonical three-attempts rule.
