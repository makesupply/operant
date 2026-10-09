# Adaptation: Long-Running Personal / Ops Orchestrator Agents (the Hermes-class archetype)

For builders wiring Operant into a *Hermes-class agent*: a custom local agent with many tools, persistent memory, scheduled and recurring jobs, and standing authority to act across systems on its operator's behalf. It reads mail, moves money, edits records, posts, deploys, and files reports — often while the operator is asleep. This is the highest-stakes deployment the framework addresses, because it pairs real authority with reduced human-in-the-loop. Everything below follows from that pairing.

## Why enforcement must be code here, not prompt

An interactive agent has a human catching its mistakes in real time. A Hermes-class agent does not: it acts unattended and outward-facing, so the irreversible subset of its actions cannot rely on self-discipline. Self-discipline is real and load-bearing — but it governs the *reversible majority*, where a wrong move costs a retry. The *irreversible minority* — a wire transfer, a mass send, a production deploy, a hard delete — must be governed by code the model cannot talk its way past.

Concretely, these belong in the agent's own action-gating loop, not in its prompt ([safety.md](../references/safety.md)):

- **Tier-3 gates** — destructive and outward-facing tools are intercepted before they fire and routed to an approval path the loop enforces (a `confirm: true` the loop demands, an approval queue, a hold). The prompt teaches the agent to *expect* the gate; the code *is* the gate.
- **The external-send gate** — every send/publish/pay is a Tier-3 action by definition; sending to a real destination publishes, and there is no unattended "test post."
- **The retry-after-side-effect rule** — before any retry of a side-effecting call, the loop verifies what the failed attempt actually did server-side.
- **Secret hygiene** — an output/log filter for credential patterns ([security-posture.md](../references/security-posture.md)); never rely on the model remembering not to leak.
- **Injection defense** — mail, web pages, ticket bodies, and tool results are untrusted content; they enter the context wrapped in delimiters under a standing "this is data, not instructions" frame. Structural, not behavioral.

The division of labor: the prompt produces judgment, the code produces guarantees. Anything on the guarantee list that lives only in the prompt is a bug in the harness — and unlike an interactive agent, this one has no human to catch that bug at runtime.

## Where each layer lives

- **Layer 1 — Constitution.** The SKILL.md body (Ten Principles, session shape, calibration) sits in the standing system prompt as a stable, cache-friendly prefix, present on every turn and every scheduled run. Principles (4) *act when you can act; ask only when you must*, (6) *never claim without proof*, and (10) *respect irreversibility* do the most work in this archetype and must survive verbatim.
- **Layer 2 — Chapters.** The `references/` and `playbooks/` files are retrieved on demand through the agent's own memory/retrieval, keyed off the routing table already in Layer 1 — the same progressive disclosure the skill uses natively. Don't resident-load all of them.
- **Layer 3 — Enforcement.** The gates above live in the action loop, where every tool call passes through them.

## Persistent memory

Map the agent's long-term store to [memory-and-persistence.md](../references/memory-and-persistence.md) and hold its three rules exactly:

- **One fact per file, name-as-claim.** Decisions with reasons, operator preferences and corrections, hard-won environmental facts, pointers (IDs, endpoints, dashboard locations). Dates absolute, never relative.
- **Update, don't accrete.** Before writing, check the neighbors; rewrite the note rather than adding a contradictory duplicate. A stale note in a standing agent is a landmine that fires on a schedule.
- **Recall is not truth.** A recalled fact is a record of what was once true. Perishable facts (state, who's responsible, what's running) get verified before the agent acts on them; this matters more here because the agent acts on recall unattended, with no human to notice it trusted a six-week-old note about a system that changed five weeks ago.

## Recurring and scheduled jobs

Map every cron/scheduled task to [recurring-automation.md](../playbooks/recurring-automation.md): nobody is watching, so mistakes compound at schedule frequency.

- **Idempotent.** The job *will* eventually double-run; running twice must equal running once, or the second run must detect the first and exit.
- **Fail loud, not partial.** Validate every precondition at the top (data present, fresh enough, credentials valid) and stop on any miss; a job that limps forward on stale input ships confident garbage on time.
- **Staleness detection.** A failure alert only covers detected failures; the job that stops running entirely emits nothing, so a separate "no successful run in >N hours" check catches the silence.
- **The job must testify.** Every run answers, without being asked: did I run, did I succeed, what did I change — with the run's key numbers — logged somewhere durable and auditable. A job that did nothing must say so and why.

## Multi-tool routing

A Hermes-class agent is tool-rich, so [tool-discipline.md](../references/tool-discipline.md) is central: fire independent calls in parallel, prefer dedicated tools over generic shells, and never blindly re-run a failed call. The retry-after-side-effect rule matters most in exactly this archetype — an unattended retry of a timed-out send or charge can double-send or double-charge with no human watching, so the loop checks server-side state before it retries or reconciles.

## Autonomy levels

The operator picks a risk profile per [autonomy-levels.md](../references/autonomy-levels.md); a Hermes-class agent is the archetypal L3 deployment. The counterintuitive rule: **higher autonomy requires stronger code enforcement and richer audit logging, not looser rules.** Granting the agent standing authority to act without confirmation raises the floor of what the code must guarantee — every Tier-3 path it's trusted to walk unsupervised needs a tighter gate and a durable record, not a removed one. Autonomy is bought with enforcement, not traded against it.

## Confirmation payloads

When a Tier-3 action does need the operator, the agent surfaces it through the framework's confirmation schemas — [`DestructiveActionConfirmation`](../schemas/destructive-action-confirmation.schema.json) for deletes/overwrites and [`ExternalSendConfirmation`](../schemas/external-send-confirmation.schema.json) for sends/publishes/payments (structured payloads; see also the confirmation section of [safety.md](../references/safety.md)). The payload shows exact scope — the verbatim content, the real destination, the blast radius, the undo cost — so that even asynchronously, over a push or notification channel, the operator approves *what will actually happen*, not a vague summary. Approval is per-action: one "yes" authorizes that action, not the category.

## Wiring checklist

1. Pin Layer 1 as the standing system-prompt prefix; keep it stable for cache reuse across turns and scheduled runs.
2. Expose Layer 2 via the agent's retrieval, keyed off the Layer 1 routing table; don't resident-load chapters.
3. Put the Tier-3 gate, external-send gate, and retry-after-side-effect check in the action loop — enforced in code, per the host-agnostic [generic-policy-spec.md](../enforcement/generic-policy-spec.md) (gates G1–G9); wire the reference hooks in [claude-code-hooks.md](../enforcement/claude-code-hooks.md) as one concrete backstop.
4. Add the secret-pattern output/log filter and the untrusted-content delimiter frame ([security-posture.md](../references/security-posture.md)).
5. Structure memory one-fact-per-file with update-on-write and verify-on-recall ([memory-and-persistence.md](../references/memory-and-persistence.md)).
6. Make every scheduled job idempotent and fail-loud, with a heartbeat, a testimony log, and an external staleness check ([recurring-automation.md](../playbooks/recurring-automation.md)).
7. Set the autonomy profile ([autonomy-levels.md](../references/autonomy-levels.md)) and scale the audit logging and gate strictness up with it, never down.
8. Route Tier-3 confirmations through `DestructiveActionConfirmation` / `ExternalSendConfirmation` payloads over the operator's async channel, one approval per action.
