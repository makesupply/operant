# Adaptation: Cursor, Windsurf, Copilot, and Other IDE Agents

These harnesses share the shape that matters: a rules file auto-loaded into context, an agent that edits and runs things, and no skill registry or a limited one. Two port strategies, pick by appetite:

- **Simple (default)**: put the self-contained [dist/single-file.md](../dist/single-file.md) in the rules location and stop. No repo docs, no routing, done in two minutes. This is what [QUICKSTART.md](../QUICKSTART.md) prescribes.
- **Full (power option, detailed below)**: SKILL.md becomes the rules file, the bundle lands in `docs/operant/`, and the routing table points at it. The agent pulls chapter depth on demand, exactly as the skill works natively. Worth it when your agent reliably reads workspace files and you want the playbooks in play.

A third path covers every tool at once: `npx skills add <owner>/<repo>` installs the bundle as an Agent Skills directory into the tools it detects on the machine (Claude Code, Codex, Cursor, Copilot, Windsurf, Cline, Roo, Kiro, Gemini, and the rest listed at skills.sh). Use it when a tool reads skills natively; use the rules-file port when it only reads rules.

## Rules-file locations by tool

Checked against each vendor's documentation on 2026-10-28. Where a tool reads `AGENTS.md`, that file is the cheapest cross-tool home for the constitution: one file, every agent.

| Tool | Always-on rules file | Scoped rules | Reads `AGENTS.md` |
|---|---|---|---|
| Cursor | `.cursor/rules/*.mdc` with `alwaysApply: true`; global "User Rules" under Customize, Rules | `.mdc` with `globs` or a `description` the agent matches | Yes, root and subdirectories |
| Windsurf | `.windsurf/rules/*.md` with `trigger: always_on` (`.devin/rules/` is now preferred, `.windsurf/rules/` the fallback); global `global_rules.md`; `.windsurfrules` is legacy and still read | `trigger: glob` with `globs`; `model_decision`; `manual` | Yes, root files always on |
| GitHub Copilot | `.github/copilot-instructions.md` | `.github/instructions/*.instructions.md` with an `applyTo` glob in frontmatter | Yes, nearest file wins |
| Gemini CLI | `GEMINI.md` (global `~/.gemini/GEMINI.md`, project, subdirectories); `context.fileName` in settings accepts other names | by directory, loaded when a tool touches the path | Yes, when `context.fileName` lists it |
| Cline and Roo | `.clinerules/` (or `.cline/rules/`) folder; global rules under the Cline Rules directory | per-file inside the folder | Yes, workspace root and `~/.agents/AGENTS.md` |
| Kiro | `.kiro/steering/*.md` with `inclusion: always` (default); global `~/.kiro/steering/` | `inclusion: fileMatch` with `fileMatchPattern`; `manual`; `auto` | Yes, always included |
| Any tool that reads it | `AGENTS.md` at the repository root | nested `AGENTS.md` in subdirectories | the convention itself |

Two cautions. Gemini CLI was replaced by Antigravity CLI on 2026-06-18 according to its own documentation, so check the migration note before relying on the `GEMINI.md` row. Windsurf caps each workspace rule file at 12,000 characters and the global file at 6,000, so the one-page edition fits and the single-file edition does not.

## Cursor

**Project Rules** (`.cursor/rules/`, versioned with the repo):

```
.cursor/rules/operant.mdc        SKILL.md content, with MDC frontmatter
docs/operant/                    the full bundle (references/, playbooks/, checklists/, examples/)
```

In `operant.mdc`, set the rule to always-apply:

```
---
description: Operant operating discipline
alwaysApply: true
---
<paste SKILL.md body here>
```

Then rewrite SKILL.md's routing table to point at `docs/operant/...` paths and add one line: "When a situation matches a chapter in the routing table, read that file before proceeding." Cursor's agent can read workspace files, so the progressive-disclosure design survives intact.

Glob-scoped rules replicate playbook routing mechanically. Split hot playbooks into their own `.mdc` files with `globs` frontmatter, for example `globs: ["**/*.test.*"]` for the testing rules and `**/migrations/**` for the migration playbook, so they load only when matching files are touched. The always-on budget then stays at the constitution.

For global application, paste the single-file edition into User Rules (Customize, Rules). It applies to all projects. The bundle's files are not guaranteed to exist in every project, so a self-contained rule is the right shape there; a global rule may still tell the agent to read `docs/operant/` when present.

## Windsurf

Same pattern via `.windsurf/rules/` (or the legacy `.windsurfrules` single file, still read): SKILL.md body as an always-on rule, bundle in `docs/operant/`, routing table pointed at those paths. Cascade reads workspace files on request, so chapter consultation works. Mind the rules-size limits. If the file would be truncated, keep the Ten Principles and the routing table and drop the session-shape and calibration prose, because the chapters cover them.

## GitHub Copilot (agent mode)

`.github/copilot-instructions.md` is the auto-loaded location. Use the single-file edition there, or the SKILL.md body plus `docs/operant/` for the full port. Path-specific files under `.github/instructions/` with an `applyTo` glob give Copilot the same scoped routing Cursor gets from `globs`. Treat the instructions file as size-constrained; long instruction files get diluted in practice even without a published hard limit. If you must cut, keep all ten principles (trimmed to their bold first sentences if needed), then the routing table, then everything else.

## Generic recipe for anything with a rules file

1. **Core into the rules file**: SKILL.md body into whatever auto-loads (`AGENTS.md`, `.rules`, a system-prompt field).
2. **Bundle into repo docs**: the full tree at a stable path (`docs/operant/` by convention).
3. **Rewire the routing table** to those paths, with the one-line consultation instruction.
4. **Verify the wiring**: fresh session, ask "what operating discipline are you under?", then watch one real task for the two easiest tells: does it lead with the outcome, and does it stop asking permission for reversible work?

## What degrades without a real harness

Be honest about the port's limits so you can compensate:

- **No skill triggering**: everything rides the rules file; there is no on-demand invocation. Always-on is the only mode, which is what you wanted anyway.
- **No subagents** (in most): [delegation-and-multiagent.md](../references/delegation-and-multiagent.md) mostly does not apply. The compensating rule: the context-management chapter matters more, because without delegation a sweep floods the main context, so targeted reading discipline is the whole defense.
- **Weaker permission surfaces**: some IDE agents auto-approve more than Claude Code would. The [safety.md](../references/safety.md) tiers compensate behaviorally: the agent asks in chat before Tier 3 actions even when the harness would not force it. Use the IDE's own guardrail settings as backup.
- **Rules-size ceilings**: when truncation looms, cut in this order: examples, then playbooks, then references, then the routing table, and never the Ten Principles.

## Team rollout note

Committing the rules file and `docs/operant/` to the repo applies the discipline to every teammate's agent automatically. That is a feature and a courtesy issue: mention it in the PR description. Teammates should know their agent's behavior is about to change, and the bundle's README gives them the why.
