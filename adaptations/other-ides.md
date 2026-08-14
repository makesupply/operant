# Adaptation: Cursor, Windsurf, Copilot, and Other IDE Agents

These harnesses share the shape that matters: a rules file auto-loaded into context, an agent that edits and runs things, and no (or limited) skill registry. Two port strategies, pick by appetite:

- **Simple (default)**: put the self-contained [dist/single-file.md](../dist/single-file.md) in the rules location and stop — no repo docs, no routing, done in two minutes. This is what [QUICKSTART.md](../QUICKSTART.md) prescribes.
- **Full (power option, detailed below)**: **SKILL.md becomes the rules file; the bundle lands in `docs/operant/` and the routing table points at it** — the agent pulls chapter depth on demand, exactly as the skill works natively. Worth it when your agent reliably reads workspace files and you want the playbooks in play.

## Cursor

**Modern setup — Project Rules** (`.cursor/rules/`, versioned with the repo):

```
.cursor/rules/operant.mdc        ← SKILL.md content, with MDC frontmatter
docs/operant/                    ← the full bundle (references/, playbooks/, checklists/, examples/)
```

In `operant.mdc`, set the rule to always-apply:

```
---
description: Operant operating discipline
alwaysApply: true
---
<paste SKILL.md body here>
```

Then rewrite SKILL.md's routing table to point at `docs/operant/...` paths and add one line: *"When a situation matches a chapter in the routing table, read that file before proceeding."* Cursor's agent can read workspace files, so the progressive-disclosure design survives intact.

Bonus on Cursor: **glob-scoped rules** replicate playbook routing mechanically — split hot playbooks into their own `.mdc` files with `globs` frontmatter (e.g., `globs: ["**/*.test.*"]` for the testing rules, migration playbook on `**/migrations/**`) so they load only when matching files are touched, keeping the always-on budget at just the constitution.

For **global** application, paste the single-file edition into Cursor Settings → Rules — it applies to all projects, and since the bundle's files aren't guaranteed to exist in every project, a self-contained rule is the right shape there (a global rule *may* still tell the agent to read `docs/operant/` when present, as a bonus).

## Windsurf

Same pattern via `.windsurf/rules/` (or the legacy `.windsurfrules` single file): SKILL.md body as an always-on rule, bundle in `docs/operant/`, routing table pointed at those paths. Windsurf's Cascade agent reads workspace files on request, so chapter-consultation works. Mind the rules-size limits — if the file is truncated, keep the Ten Principles and the routing table, and drop the Session Shape/Calibration prose (the chapters cover them).

## GitHub Copilot (agent mode)

`/.github/copilot-instructions.md` is the auto-loaded location. Use the single-file edition there (or the SKILL.md body + `docs/operant/` for the full port). Treat the instructions file as size-constrained — long instruction files get diluted in practice even without a published hard limit; if you must cut, priority order: the Ten Principles (keep all ten, trimmed to their bold first sentences if needed), then the routing table, then everything else.

## Generic recipe for anything with a rules file

1. **Core → rules file**: SKILL.md body into whatever auto-loads (`AGENTS.md`, `.rules`, system-prompt field).
2. **Bundle → repo docs**: the full tree at a stable path (`docs/operant/` by convention).
3. **Rewire the routing table** to those paths, with the one-line consultation instruction.
4. **Verify the wiring**: fresh session, ask "what operating discipline are you under?" — then watch one real task for the two easiest tells: does it lead with the outcome, and does it stop asking permission for reversible work?

## What degrades without a real harness

Be honest about the port's limits so you can compensate:

- **No skill triggering**: everything rides the rules file; there's no on-demand invocation. Always-on is the only mode — which is what you wanted anyway.
- **No subagents** (in most): [delegation-and-multiagent.md](../references/delegation-and-multiagent.md) mostly doesn't apply. The compensating rule: the *context-management* chapter matters more — without delegation, sweeps flood the main context, so targeted reading discipline is the whole defense.
- **Weaker permission surfaces**: some IDE agents auto-approve more than Claude Code would. The [safety.md](../references/safety.md) tiers compensate *behaviorally* — the agent asks in chat before Tier 3 actions even when the harness wouldn't force it. Consider the IDE's own guardrail settings as backup.
- **Rules-size ceilings**: when truncation looms, the cut order is: examples → playbooks → references → routing table → **never the Ten Principles**.

## Team rollout note

Committing the rules file + `docs/operant/` to the repo applies the discipline to every teammate's agent automatically. That's a feature and a courtesy issue: mention it in the PR description — teammates should know their agent's behavior is about to change, and the bundle's README gives them the why.
