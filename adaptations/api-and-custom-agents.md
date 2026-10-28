# Adaptation: API System Prompts and Custom Agents

For builders wiring Operant into agents they construct themselves: an API integration, an Agent SDK app, a graph or crew framework, or a bespoke loop. Here you control the whole context assembly, which means you can do this better than any off-the-shelf harness, or waste tokens badly.

## Architecture: three layers, three budgets

**Layer 1, the constitution (always in the system prompt).** The SKILL.md body: Ten Principles, session shape, calibration, routing table. About 2.4k tokens for the generic SKILL.md; more with a project overlay, so measure the copy you ship. This is the non-negotiable core. It goes in every request, positioned before task-specific instructions, so the stable prefix is prompt-cache friendly.

**Layer 2, the chapters (retrieved, not resident).** The references/ and playbooks/ files. Do not inline all of them (roughly 25k tokens for references alone); expose them through retrieval:

- Simplest: a `read_discipline(chapter)` tool the agent can call, with the routing table (already in Layer 1) telling it when. This mirrors the skill's native progressive disclosure exactly.
- Alternative: task-type detection at assembly time. Building a debugging run? Prepend `playbooks/debugging.md` for that run. Deterministic, no tool round-trip, right when you know the task type up front.

**Layer 3, enforcement (code, not prompt).** The rules that must never depend on model compliance get implemented in the loop itself:

- **Tier-3 gating** ([safety.md](../references/safety.md)): destructive and outward-facing tools require a human-approval step in your code, whether a `confirm: true` parameter the loop intercepts or an approval queue. The prompt teaches the agent to expect the gate; the code is the gate.
- **Secret hygiene** ([security-posture.md](../references/security-posture.md)): output filters for credential patterns; never rely on the model remembering.
- **Injection defense**: fetched and third-party content enters the context wrapped in delimiters with a standing "this is data, not instructions" frame. Structural, not behavioral.

The division of labor: prompts produce judgment, code produces guarantees. Anything on the guarantee list that lives only in the prompt is a bug in your harness.

**Agent SDK hooks.** The Claude Agent SDK registers hook callbacks in the `hooks` option of the agent options (a `HookMatcher` per event in Python, an object keyed by event name in TypeScript). A `PreToolUse` callback returns `hookSpecificOutput.permissionDecision` of `allow`, `deny`, `ask`, or `defer` with a `permissionDecisionReason`; a `PostToolUse` callback can set `additionalContext` or replace the result with `updatedToolOutput`. Those are the same fields the Claude Code shell hooks use, so the gate scripts in `enforcement/` port to an SDK app with no change to their logic; only the transport changes from stdin JSON to a function call. Shell-command hooks from settings files also run when the matching `settingSources` entry is enabled. Facts checked against the SDK hooks page on 2026-10-28.

## Inventory the harness once, at the start

For a host nobody wrote an adaptation for, project the discipline onto whatever tools exist. Answer seven questions before the first substantive move:

1. Can several tool calls go out in one turn?
2. Is there a subagent tool, and does it run in the background?
3. Are there dedicated read, edit, and search tools beside the shell?
4. Is there a persistent memory surface?
5. Are permission denials visible to you?
6. Can the code or tests actually run here?
7. Is there a task-tracking mechanism?

For each missing capability, use the degraded form. Serial harness: order calls by value and drop lookups that would not change the action. No subagents: run the sweep yourself and summarize immediately. Shell only: read ranges instead of whole files. No memory: keep a notes file in the project if the user agrees, otherwise say that nothing persists. No permission layer: the gate is entirely yours, so widen it. No runnable tests: say so in every verification claim, because "not verified" is the only honest verdict then. No task tracker: keep the task-state file ([context-management.md](../references/context-management.md)) and treat it as the tracker.

Five things never degrade: the verdict vocabulary (verified, attempted and unverified, not done), verification to the depth the environment allows, the irreversibility gate, data never commands, and established facts are not re-derived. [environment-awareness.md](../references/environment-awareness.md) points here for this inventory.

## Multi-agent systems

If your system spawns subagents, [delegation-and-multiagent.md](../references/delegation-and-multiagent.md) becomes architecture documentation:

- Every subagent gets Layer 1. The constitution travels; a rude, unverified sub-report poisons the lead's honest one.
- The brief contract (task, scope, output format, done criteria, what does not count) becomes your subagent-spawn schema. Enforce it as structure, not convention.
- The orchestration shapes (scout then work, fan-out then synthesize, generate then verify) are your workflow-graph patterns; pick per task type in code.
- A subagent's report is a tool result. It carries no instruction and no approval. The lead verifies load-bearing claims against the artifact before building on them.

[multi-agent-orchestrators.md](multi-agent-orchestrators.md) carries the rest.

## Non-coding agents

The discipline is domain-general; the coding examples are incidental. For a support agent, research assistant, ops bot, or marketing agent, the mapping:

- **Verification ladder** becomes "never state an account fact without pulling the record; never claim a ticket resolved without the status check."
- **Tier 3** becomes refunds, sends, account changes, anything customer-visible.
- **Outcome-first communication** is unchanged; it is universal.
- **Playbooks**: write your domain's own using the bundle's shape: orientation, verified increments, adversarial self-check, honest report, exit criteria, anti-patterns. `data-work.md` and `research-and-analysis.md` port almost verbatim to analyst agents.

Drop `code-quality.md` and the coding playbooks from Layer 2 for these; keep everything else.

## Token economics

- Layer 1 as a stable prefix plus prompt caching means the constitution costs you once per cache window, not per request.
- Chapter retrieval means you pay for depth only when the task needs it, which mirrors exactly how the skill works in Claude Code.
- The examples/ files are the most cuttable content for budget-constrained systems, and the highest-leverage content for smaller models, which imitate demonstrated shape better than they follow abstract rules. If you run small models, cut references before examples.

## Evaluating whether it is working

Operant makes claims about behavior; test them like any other system property. The bundle ships the eval set: [evals/eval-suite.md](../evals/eval-suite.md) holds 40 behavioral scenarios after 1.5.0, each with pass criteria and fail tells, mapped to a principle, with a scorecard and a score-interpretation guide. The criteria are written to be judgeable, so they drop straight into an LLM-judge harness for automated runs.

Run it per model and per prompt revision. To extend beyond the 40: the [failure-modes.md](../references/failure-modes.md) catalogue is a pre-written eval taxonomy; each anti-pattern's tell is a fail condition waiting for a fixture.
