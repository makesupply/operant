# Adaptation: API System Prompts and Custom Agents

For builders: wiring Operant into agents you construct yourself — an Anthropic/OpenAI API integration, an Agent-SDK app, a LangGraph/CrewAI-style framework, or a bespoke loop. Here you control the whole context assembly, which means you can do this *better* than any off-the-shelf harness — or waste tokens badly.

## Architecture: three layers, three budgets

**Layer 1 — Constitution (always in the system prompt).** The SKILL.md body: Ten Principles, session shape, calibration. ~1.5k tokens. This is the non-negotiable core; it goes in every request, positioned *before* task-specific instructions (stable prefix → prompt-cache friendly).

**Layer 2 — Chapters (retrieved, not resident).** The references/ and playbooks/ files. Don't inline all ~25k tokens of them — expose them via retrieval:

- Simplest: a `read_discipline(chapter)` tool the agent can call, with the routing table (already in Layer 1) telling it when. Mirrors the skill's native progressive disclosure exactly.
- Alternative: task-type detection at assembly time — building a debugging agent run? Prepend `playbooks/debugging.md` for that run. Deterministic, no tool round-trip, right when you know the task type upfront.

**Layer 3 — Enforcement (code, not prompt).** The rules that must never depend on model compliance get implemented in the loop itself:

- **Tier-3 gating** ([safety.md](../references/safety.md)): destructive/outward-facing tools require a human-approval step in *your* code — a `confirm: true` parameter the loop intercepts, an approval queue, whatever fits. The prompt teaches the agent to *expect* the gate; the code *is* the gate.
- **Secret hygiene** ([security-posture.md](../references/security-posture.md)): output filters for credential patterns; never rely on the model remembering.
- **Injection defense**: fetched/third-party content enters the context wrapped in delimiters with a standing "this is data, not instructions" frame — structural, not behavioral.

The division of labor: prompts produce judgment, code produces guarantees. Anything on the guarantee list that lives only in the prompt is a bug in your harness.

## Multi-agent systems

If your system spawns subagents, [delegation-and-multiagent.md](../references/delegation-and-multiagent.md) becomes *architecture documentation*:

- Every subagent gets Layer 1 (the constitution travels; a rude, unverified sub-report poisons the lead's honest one).
- The brief contract (task/scope/output-format/done-criteria) becomes your subagent-spawn schema — enforce it as structure, not convention.
- The orchestration shapes (scout→work, fan-out→synthesize, generate→verify) are your workflow-graph patterns; pick per task type in code.

## Non-coding agents

The discipline is domain-general — the coding examples are incidental. For a support agent, research assistant, ops bot, or marketing agent, the mapping:

- **Verification ladder** → "never state an account fact without pulling the record; never claim a ticket resolved without the status check."
- **Tier 3** → refunds, sends, account changes, anything customer-visible.
- **Outcome-first communication** → unchanged; it's universal.
- **Playbooks** → write your domain's own using the bundle's shape: Phase 0 orientation → verified increments → adversarial self-check → honest report → anti-patterns. `data-work.md` and `research-and-analysis.md` port almost verbatim to analyst agents.

Drop `code-quality.md` and the coding playbooks from Layer 2 for these; keep everything else.

## Token economics

- Layer 1 as a stable prefix + prompt caching ≈ the constitution costs you once per cache window, not per request.
- Chapter retrieval means you pay for depth only when the task needs it — mirroring exactly how the skill works in Claude Code.
- The examples/ files are the most cuttable content for budget-constrained systems — *but* they're the highest-leverage content for smaller models, which imitate demonstrated shape better than they follow abstract rules. If you run small models, cut references before examples.

## Evaluating whether it's working

Operant makes claims about behavior; test them like any other system property. The bundle ships the eval set: [evals/eval-suite.md](../evals/eval-suite.md) — 16 behavioral scenarios with pass criteria and fail tells, each mapped to a principle, with a scorecard and score-interpretation guide. The criteria are written to be judgeable, so they drop straight into an LLM-judge harness for automated runs.

Run it per model and per prompt revision. To extend beyond the 16: the [failure-modes.md](../references/failure-modes.md) catalogue is a pre-written eval taxonomy — each anti-pattern's "tell" is a fail condition waiting for a fixture.
