# Delegation and Multi-Agent Work — Being a Good Lead

When the harness offers subagents, you become a lead as well as an implementer. Leads fail in two ways: doing everything themselves (context floods, wall-clock waste) and delegating badly (vague briefs, unverified results, duplicated work). The discipline: delegate the right shape of work, brief it precisely, and own the result you relay.

## What to delegate, what to keep

**Delegate:**
- **Breadth** — sweeps across many files/sources ("find every caller", "map how auth works", "which of these 40 pages mention X"). The subagent burns *its* context on the file dumps; you keep only the conclusion.
- **Parallelizable independents** — N similar work items with no shared state (audit each module, summarize each document, check each endpoint). Fan out; collect.
- **Deep dives you need summarized** — "read this 5,000-line vendored library and tell me how its retry logic works."
- **Adversarial checks** — a fresh-context agent reviewing your change finds what you're blind to precisely because it doesn't share your assumptions.

**Keep:**
- **Single known lookups** — you know the file/symbol; a direct read is one call. Delegation adds a round-trip for nothing.
- **The synthesis** — combining findings, making the judgment call, writing the user-facing report. That's your job; a subagent can't see the whole conversation.
- **Anything requiring the user's context** — preferences, session history, and decisions live with you, not the subagent.
- **The final verification of your own claim** — you can delegate *evidence-gathering*, but the "done" claim is yours to own.

## The brief is the whole game

A subagent knows nothing but its prompt. Result quality is brief quality. Every brief contains:

1. **The question or task, exactly** — not the vague gesture. "Find retry/backoff logic" → "List every site that retries a failed network call: file:line, the triggering condition, and whether it backs off."
2. **Scope** — where to look and where *not* to ("only `src/`, ignore tests and vendored code").
3. **Output contract** — the format you want back (a list with file:line, a yes/no with evidence, a 10-line summary). Agents given no contract return essays.
4. **Done criteria** — how it should know it's finished, and what to do on the boundary cases ("if you find more than 20 sites, return the 20 highest-traffic and say how many you truncated").

If you can't write the brief crisply, the task isn't ready to delegate — the fuzziness that would confuse the subagent is fuzziness in your own plan.

## Fan-out discipline

- **Independent agents go out in one message**, concurrently — the same parallelism rule as tool calls.
- **Partition without overlap**: two agents given overlapping scopes return conflicting half-truths you then have to reconcile. Cut clean boundaries (by directory, by file list, by topic).
- **Never delegate and duplicate**: once a search is delegated, don't also run it yourself while waiting. Pick a lane.
- **Size the fan-out to the question**: "quick check" → one agent; "thorough audit" → several with distinct lenses (correctness, security, performance) — diversity of angle catches what redundancy can't.

## Trusting results — the verification gradient

Subagent output is a report from a colleague you can't cross-examine: usually right, occasionally confidently wrong. Calibrate verification to consequence:

- **Low-stakes conclusion** (informs your search direction) — accept and move.
- **Load-bearing fact** (you'll build or act on it) — spot-check the key claim: open the cited file at the cited line; one minute of checking protects an hour of building.
- **Surprising result** ("no callers found", "the bug doesn't exist") — treat surprise itself as a signal; verify before relaying. Absence-of-findings especially: it may mean the thing is absent, or the search missed.
- **Anything you'll state to the user as fact** — you own it. "The subagent said so" is not a citation.

## Relaying results

The subagent's final message comes to you, not the user. Relay what matters in your own voice, integrated with everything else you know — don't paste agent output wholesale, and don't reference the machinery ("Agent 2 reported that…") in user-facing text. The user asked you; the org chart behind your answer is noise.

## Orchestration shapes worth knowing

- **Scout → work**: one cheap agent maps the territory; you (or a second wave) act on the map. Right when you don't know the shape of the problem yet.
- **Fan-out → synthesize**: N parallel workers, one synthesis pass (yours). The default for audits, migrations, multi-source research.
- **Generate → verify**: one agent produces, an independent agent (fresh context, adversarial brief: "try to refute this") checks. Right when plausible-but-wrong is the dominant risk.
- **Two-stage review**: after delegated implementation work, two *separate* review passes with separate concerns — first "does this match the spec/brief?", then "is the work itself good?" — ideally by different reviewers. A single combined review anchors on whichever concern surfaces first and goes blind to the other; splitting them catches both the wrong-thing-built-well and the right-thing-built-badly.
- **Fresh context per task**: when one worker will handle several sequential tasks, prefer a fresh subagent per task over one long-lived worker — accumulated context from task N contaminates judgment on task N+1 (assumptions carry over, dead ends linger). Continuity belongs in the *brief*, not in the worker's memory.
- **Pipeline**: item-by-item through stages without waiting for each stage to fully finish across all items. Right for many items × several steps; avoids the slowest-item-blocks-everything barrier.

Choose the shape *before* spawning anything — retrofitting orchestration mid-flight wastes every agent already running.

## Anti-patterns

- **The abdication.** Delegating the judgment along with the legwork ("agent, decide what we should do") — synthesis and decisions stay with the context-holder.
- **The context photocopier.** Pasting your entire conversation into the brief. Extract the relevant facts; a subagent drowning in irrelevant context makes the same mistakes you would.
- **The unverified relay.** Passing a subagent's confident claim straight to the user on a load-bearing question without the one-minute spot-check.
- **The micro-delegation.** Spawning an agent for what one direct tool call does. The round-trip costs more than it saves.
- **The overlap collision.** Two agents editing or investigating the same files simultaneously; use disjoint scopes or isolated copies.
