# Adaptation: Multi-Agent Orchestrators

For systems where a lead agent spawns subagents — fan-out and synthesize, staged pipelines, judge panels. The lead's discipline is necessary but not sufficient: the quality of the final answer is bounded by the quality of the worst sub-report the lead trusts. Operant's job here is to make every actor in the system honest and to keep every irreversible action behind a single gate. The delegation reference ([delegation-and-multiagent.md](../references/delegation-and-multiagent.md)) covers what to delegate, brief quality, fan-out rules, the verification gradient, and orchestration shapes; this file is how those hold up when the lead is code, not judgment.

## The constitution travels

Every subagent gets Layer 1 in its system prompt — the Ten Principles, the session shape, the calibration. Discipline is not just the lead's job. A subagent that pads its output with filler, states a claim it never verified, or answers in a rude register hands the lead poisoned input, and the lead then synthesizes honestly *over* dishonest material. The corruption is invisible at the synthesis step because it looks like data. Ship the constitution to the leaves, or the leaves rot the root.

## The brief contract as spawn schema

The brief contract — task, scope, output-format, done-criteria — stops being a convention the lead is trusted to follow and becomes a structured `TaskBrief` the orchestrator constructs and validates before spawn (reference [../schemas/task-brief.schema.json](../schemas/task-brief.schema.json)). Enforce it as structure, not prose. A subagent handed a vague brief returns vague work — no amount of downstream synthesis recovers precision the brief never demanded. If the orchestrator cannot populate every required field, the task is not ready to spawn; that failure surfaces in code, before an agent burns tokens on a question it was never given cleanly.

## The verification gradient

The lead does not trust sub-findings by default; it re-verifies the load-bearing ones (see [verification.md](../references/verification.md)). Calibrate to consequence, exactly as a human lead would:

- **Cheap, low-stakes findings** — informs a search direction, one of many inputs — pass through. Re-verifying everything defeats the point of delegating.
- **Load-bearing findings** — the lead will build or act on it — get spot-checked against the cited evidence before entering the synthesis.
- **High-stakes claims** get adversarial verification: spawn an independent subagent, fresh context, prompted to *refute* the claim rather than confirm it. Agreement between a producer and an adversary is worth far more than a single confident report.

## Orchestration shapes as workflow graphs

Pick the shape per task type in code, before spawning — not by vibe mid-run:

- **Scout → work** — one cheap agent maps unknown territory; a second wave acts on the map.
- **Fan-out → synthesize** — N parallel workers over disjoint scopes, one synthesis pass the lead owns. The default for audits and multi-source research.
- **Generate → verify** — a producer emits, an adversarial checker refutes. Right when plausible-but-wrong is the dominant risk.
- **Loop-until-dry** — repeat a pass until it stops finding new results, then stop. Right for exhaustive sweeps with an unknown endpoint.

The shape is a property of the task, decidable up front. Retrofitting orchestration after agents are already running wastes every one of them.

## Enforcement stays centralized

Tier-3 gates and the external-send gate live in the orchestrator, never in the subagents (see [safety.md](../references/safety.md)). A subagent must not be able to delete, deploy, pay, or send outward on its own authority — every such action routes back through the lead's single gate. Delegate the gate to N subagents and you have not one gated actor but N ungated ones, any of which can take an irreversible action the lead never reviewed. The subagents produce proposals; the orchestrator holds the one lever that touches the outside world.

## Failure isolation

A subagent that dies, times out, or returns malformed output resolves to null and is filtered — one bad sub must not block the barrier or corrupt the synthesis. But filtering is not forgetting: log what was dropped and why, and carry that gap into the synthesis. Silent truncation reads as "covered everything" when it did not. A report built on six of ten subagents that presents itself as complete is a false claim about coverage — the honest synthesis names the four it lost.

## Context and token economy

Subagents keep their own context; the lead keeps conclusions, not raw dumps. A subagent burns *its* window reading the 5,000-line file and returns the ten lines that matter — that is the entire economic case for fan-out (Principle 8, use tools like a professional). A lead that hoards every sub's full transcript floods its own context and loses the thread it was spawned to hold.

## Anti-patterns

- **The ungated subagent.** A leaf agent wired directly to a send/delete/deploy tool, bypassing the lead's gate — N irreversible actors instead of one.
- **The trusting lead.** Relaying load-bearing sub-findings to the user without re-verifying them. "The subagent said so" is not a citation.
- **The silent drop.** A failed subagent filtered out and unreported, shrinking coverage while the synthesis still reads as complete.
- **The filler sub-report.** A subagent that pads, hedges, and preambles; the lead synthesizes over noise and inherits it.
- **The vague brief.** A `TaskBrief` missing scope or output-format, spawned anyway — vague brief, vague work, guaranteed.
